from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query, Body, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
from pydantic import BaseModel
from datetime import timedelta, datetime

from database import get_db, engine, SessionLocal
from models import Base, User, CopyJob, SystemSettings, MediaItem, StorageStats, CachedImage
from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from file_operations import list_directory, get_folder_info, format_size
from copy_worker import copy_worker
from websocket_manager import websocket_manager
from security_utils import encrypt_value, decrypt_value
from media_scanner import MediaScanner, get_media_type_from_path
from trakt_client import TraktClient
from image_cache import get_cached_image_rec, save_cached_image, ensure_images_directory
import logging
import asyncio
import time
import os
import imghdr
import requests
import aiohttp
from fastapi.responses import FileResponse, Response

from fastapi.middleware.gzip import GZipMiddleware

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Run migrations for existing databases
from migrate_db import migrate
migrate()

app = FastAPI(title="CopyCat API")

# Gzip Middleware (Enable compression for static files/responses)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Base paths for source and destination (Configurable via Env Vars for Cross-Platform Support)
# In Docker, we map to /mnt/source and /mnt/destination by default
SOURCE_BASE = os.getenv("SOURCE_MOUNT", "/mnt/source") 
DESTINATION_BASE = os.getenv("DESTINATION_MOUNT", "/mnt/destination")

# Deprecation Fallbacks (Maintain temporary compatibility if old env vars are set)
if os.getenv("ZURG_BASE"):
    SOURCE_BASE = os.getenv("ZURG_BASE")
if os.getenv("HARDDRIVE_BASE"):
    DESTINATION_BASE = os.getenv("HARDDRIVE_BASE")

# Import workers
from enrichment_worker import enrichment_worker
from periodic_scanner import init_periodic_scanner

# Global periodic scanner instance
periodic_scanner = None


@app.on_event("startup")
async def startup_event():
    """
    Run startup tasks:
    1. Initialize workers
    2. Start enrichment worker if Trakt configured
    3. Run background library scan
    """
    logger.info("🚀 Application startup...")

    # Security Check
    jwt_secret = os.getenv("JWT_SECRET_KEY", "unsafe_default_change_me")
    if jwt_secret == "unsafe_default_change_me" or jwt_secret == "change_this_to_a_secure_random_string":
        logger.warning("⚠️  SECURITY WARNING: You are using the default JWT_SECRET_KEY!")
        logger.warning("   Please set a strong JWT_SECRET_KEY in your environment variables.")
    
    # 1. Initialize copy worker
    websocket_manager.set_event_loop(asyncio.get_event_loop())
    copy_worker.set_websocket_manager(websocket_manager)
    copy_worker.start()

    # Initialize periodic scanner
    global periodic_scanner
    periodic_scanner = init_periodic_scanner(SOURCE_BASE)
    
    # Inject scanner into copy worker for stats updates
    copy_worker.set_scanner(periodic_scanner)
    
    # Check mounts logic (moved from the redundant startup event)
    logger.info(f"Checking mounts: SOURCE={SOURCE_BASE}, DEST={DESTINATION_BASE}")
    
    db = SessionLocal()
    try:
        # 2. Check for Trakt key and start enrichment
        trakt_setting = db.query(SystemSettings).filter(
            SystemSettings.key == "trakt_client_id"
        ).first()
        
        if trakt_setting:
            logger.info("✅ Trakt client ID found - starting enrichment worker")
            asyncio.create_task(enrichment_worker.start())
        else:
            logger.info("⏩ No Trakt client ID configured - skipping enrichment worker")

        # Start periodic scanner
        logger.info("🔄 Starting periodic scanner")
        asyncio.create_task(periodic_scanner.start())
        
        # 3. Trigger Library Scan in background
        async def _startup_scan():
            logger.info("Running background startup library scan...")
            scan_db = SessionLocal()
            try:
                # Use the periodic_scanner instance to respect the global scan lock
                count = await periodic_scanner.scan_once(scan_db)
                logger.info(f"✅ Startup scan complete: {count} items processed")
            except Exception as e:
                logger.error(f"Startup scan failed: {e}")
            finally:
                scan_db.close()
        
        asyncio.create_task(_startup_scan())
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
    finally:
        db.close()


@app.on_event("shutdown")
async def shutdown_event():
    """Stop workers on shutdown"""
    logger.info("🛑 Application shutdown...")
    copy_worker.stop()
    await enrichment_worker.stop()
    if periodic_scanner:
        await periodic_scanner.stop()



# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


class FileItem(BaseModel):
    name: str
    path: str
    is_directory: bool
    size: int
    size_formatted: str
    modified: float


class BrowseResponse(BaseModel):
    items: List[FileItem]
    total: int
    has_more: bool


class CopyJobCreate(BaseModel):
    source_path: str
    destination_path: str


class CopyJobResponse(BaseModel):
    id: int
    source_path: str
    destination_path: str
    status: str
    priority: int = 1
    progress_percent: int
    total_size_bytes: int
    copied_size_bytes: int
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    # Enriched Fields
    media_title: Optional[str] = None
    media_year: Optional[int] = None
    media_rating: Optional[float] = None
    media_poster: Optional[str] = None
    media_type: Optional[str] = None

    class Config:
        from_attributes = True







# Auth endpoints
@app.post("/api/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


# File browsing endpoints
@app.get("/api/browse", response_model=BrowseResponse)
async def browse_directory(
    source: str = Query(..., description="Source location: source (zurg) or destination (16tb)"),
    path: str = Query("", description="Relative path within the source"),
    limit: Optional[int] = Query(None, description="Maximum items to return (pagination)"),
    offset: int = Query(0, description="Number of items to skip (pagination)"),
    sort_by: str = Query("modified", description="Field to sort by: name, size, modified"),
    order: str = Query("desc", description="Sort order: asc, desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List contents of a directory with optional pagination."""
    # Allow legacy 'zurg'/'16tb' for compatibility, but prefer 'source'/'destination'
    valid_sources = ["source", "destination", "zurg", "16tb"]
    if source not in valid_sources:
        raise HTTPException(status_code=400, detail="Source must be 'source' or 'destination'")
    
    # Map to filesystem path
    if source in ["source", "zurg"]:
        base_path = SOURCE_BASE
    else:
        base_path = DESTINATION_BASE
    
    # Handle absolute paths (strip base if present)
    if path.startswith(base_path):
        path = path[len(base_path):]
    
    # Validate path to prevent directory traversal
    from file_operations import validate_path
    if path and not validate_path(path, base_path):
        raise HTTPException(status_code=400, detail="Invalid path")
    
    try:
        result = list_directory(base_path, path, limit=limit, offset=offset, sort_by=sort_by, order=order)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/folder-info")
async def folder_info(
    source: str = Query(..., description="Source location: source or destination"),
    path: str = Query(..., description="Relative path within the source"),
    calculate_size: bool = Query(False, description="Calculate full recursive size (slow)"),
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a folder."""
    # Allow legacy 'zurg'/'16tb' for compatibility, but prefer 'source'/'destination'
    valid_sources = ["source", "destination", "zurg", "16tb"]
    if source not in valid_sources:
        raise HTTPException(status_code=400, detail="Source must be 'source' or 'destination'")
    
    if source in ["source", "zurg"]:
        base_path = SOURCE_BASE
    else:
        base_path = DESTINATION_BASE
    
    # Handle absolute paths (strip base if present)
    if path.startswith(base_path):
        path = path[len(base_path):]

    # Validate path to prevent directory traversal
    from file_operations import validate_path
    if path and not validate_path(path, base_path):
        raise HTTPException(status_code=400, detail="Invalid path")
    
    info = get_folder_info(base_path, path, calculate_size=calculate_size)
    if not info:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    return info


@app.post("/api/create-folder")
async def create_folder(
    source: str = Query(..., description="Source location: source or destination"),
    path: str = Query(..., description="Relative path within the source"),
    folder_name: str = Query(..., description="Name of the folder to create"),
    current_user: User = Depends(get_current_user)
):
    """Create a new folder in the specified location."""
    # STRICT SECURITY: Only allow folder creation on DESTINATION (writeable)
    if source not in ["destination", "16tb"]:
        print(f"SECURITY ALERT: Attempt to create folder on {source} blocked.")
        raise HTTPException(status_code=400, detail="Folders can only be created on Destination (Writeable)")
    
    base_path = DESTINATION_BASE
    
    # Validate path to prevent directory traversal
    from file_operations import validate_path
    import os
    import re
    
    if path and not validate_path(path, base_path):
        raise HTTPException(status_code=400, detail="Invalid path")
    
    # Validate folder name (no special characters, no path separators)
    if not re.match(r'^[a-zA-Z0-9._\-\s]+$', folder_name):
        raise HTTPException(status_code=400, detail="Invalid folder name. Use only letters, numbers, spaces, dots, hyphens, and underscores")
    
    if '/' in folder_name or '\\' in folder_name or '..' in folder_name:
        raise HTTPException(status_code=400, detail="Folder name cannot contain path separators")
    
    # Build full path
    relative_path = path.lstrip('/').replace('\\', '/')
    full_path = os.path.normpath(os.path.join(base_path, relative_path))
    new_folder_path = os.path.join(full_path, folder_name)
    
    # Security check
    if not new_folder_path.startswith(os.path.abspath(base_path)):
        raise HTTPException(status_code=400, detail="Invalid path")
    
    # Check if folder already exists
    if os.path.exists(new_folder_path):
        raise HTTPException(status_code=409, detail="Folder already exists")
    
    try:
        os.makedirs(new_folder_path, exist_ok=False)
        return {
            "success": True,
            "message": f"Folder '{folder_name}' created successfully",
            "path": os.path.join(relative_path, folder_name).replace('\\', '/')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create folder: {str(e)}")


@app.delete("/api/files/delete")
async def delete_item(
    source: str = Query(..., description="Source location: source or destination"),
    path: str = Query(..., description="Relative path within the source"),
    current_user: User = Depends(get_current_user)
):
    """Delete a file or folder (Recursive)."""
    # STRICT SECURITY: Only allow deletion on DESTINATION
    if source not in ["destination", "16tb"]:
         raise HTTPException(status_code=400, detail="Deletion is only allowed on Destination (Writeable)")
    
    base_path = DESTINATION_BASE
    
    from file_operations import delete_path
    
    try:
        delete_path(base_path, path)
        return {"success": True, "message": f"Deleted {path}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Item not found")
    except OSError as e:
        raise HTTPException(status_code=500, detail=str(e))



# Copy job endpoints
@app.get("/api/jobs/{job_id}", response_model=CopyJobResponse)
async def get_job_details(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific job."""
    job = db.query(CopyJob).filter(CopyJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.post("/api/copy/start", response_model=CopyJobResponse)
async def start_copy(
    copy_data: CopyJobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new copy job and add it to the queue."""
    # Convert relative paths to absolute paths
    from file_operations import validate_path
    import os
    
    source_full = copy_data.source_path
    if not source_full.startswith('/'):
        source_full = os.path.join(SOURCE_BASE, copy_data.source_path.lstrip('/'))
    else:
        # Ensure it's within SOURCE_BASE (or ZURG override)
        if not source_full.startswith(SOURCE_BASE):
            raise HTTPException(status_code=400, detail="Source path must be within Source drive")
    
    # Normalize and validate source path
    source_full = os.path.normpath(source_full)
    if not source_full.startswith(os.path.abspath(SOURCE_BASE)):
        raise HTTPException(status_code=400, detail="Source path must be within Source drive")
    
    # Check source exists
    if not os.path.exists(source_full):
        raise HTTPException(status_code=404, detail="Source path does not exist")
    
    dest_full = copy_data.destination_path
    if not dest_full.startswith('/'):
        dest_full = os.path.join(DESTINATION_BASE, copy_data.destination_path.lstrip('/'))
    else:
        # Ensure it's within DESTINATION_BASE
        if not dest_full.startswith(DESTINATION_BASE):
            raise HTTPException(status_code=400, detail="Destination path must be within Destination drive")
    
    # Normalize and validate destination path
    # Normalize and validate destination path
    dest_full = os.path.normpath(dest_full)
    if not dest_full.startswith(os.path.abspath(DESTINATION_BASE)):
        raise HTTPException(status_code=400, detail="Destination path must be within Destination drive")
        
    # LOGIC FIX: Handle "Copy Into" behavior
    # If source is a file and dest is a dir, append filename
    if os.path.isfile(source_full) and os.path.isdir(dest_full):
        dest_full = os.path.join(dest_full, os.path.basename(source_full))
    # If source is a dir and dest is a dir (e.g. copying 'Avatar' to 'Movies'), append dirname
    elif os.path.isdir(source_full) and os.path.isdir(dest_full):
        # Check if we are already copying to a full path (heuristic: dest ends with source name)
        # But explicitly, if the user picked a folder 'Movies', they want 'Movies/Avatar'
        dest_full = os.path.join(dest_full, os.path.basename(source_full))
    
    # Create the copy job
    job = CopyJob(
        source_path=source_full.replace('\\', '/'),
        destination_path=dest_full.replace('\\', '/'),
        status="queued",
        progress_percent=0
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    return job


@app.get("/api/copy/queue", response_model=List[CopyJobResponse])
async def get_queue(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all jobs in the queue (queued and processing)."""
    jobs = db.query(
        CopyJob, 
        MediaItem.title.label("media_title"),
        MediaItem.year.label("media_year"),
        MediaItem.rating.label("media_rating"),
        MediaItem.poster_url.label("media_poster"),
        MediaItem.media_type.label("media_type")
    ).outerjoin(
        MediaItem, func.replace(CopyJob.source_path, '\\', '/') == func.replace(MediaItem.full_path, '\\', '/')
    ).filter(
        CopyJob.status.in_(["queued", "processing"])
    ).order_by(CopyJob.created_at).all()
    
    # Convert to list of dicts that match CopyJobResponse
    enriched_jobs = []
    for job, title, year, rating, poster, mtype in jobs:
        # Proxy poster URL if needed
        if poster and poster.startswith("http"):
             from urllib.parse import quote
             poster = f"/api/images/proxy?url={quote(poster)}"

        job_data = {
            "id": job.id,
            "source_path": job.source_path,
            "destination_path": job.destination_path,
            "status": job.status,
            "priority": job.priority,
            "progress_percent": job.progress_percent,
            "total_size_bytes": job.total_size_bytes,
            "copied_size_bytes": job.copied_size_bytes,
            "error_message": job.error_message,
            "created_at": job.created_at,
            "completed_at": job.completed_at,
            "media_title": title,
            "media_year": year,
            "media_rating": rating,
            "media_poster": poster,
            "media_type": mtype
        }
        enriched_jobs.append(job_data)
        
    return enriched_jobs


@app.get("/api/copy/history", response_model=List[CopyJobResponse])
async def get_history(
    limit: int = Query(50, description="Number of jobs to return"),
    offset: int = Query(0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get copy job history."""
    jobs = db.query(
        CopyJob,
        MediaItem.title.label("media_title"),
        MediaItem.year.label("media_year"),
        MediaItem.rating.label("media_rating"),
        MediaItem.poster_url.label("media_poster"),
        MediaItem.media_type.label("media_type")
    ).outerjoin(
        MediaItem, func.replace(CopyJob.source_path, '\\', '/') == func.replace(MediaItem.full_path, '\\', '/')
    ).order_by(
        CopyJob.created_at.desc()
    ).limit(limit).offset(offset).all()
    
    enriched_jobs = []
    for job, title, year, rating, poster, mtype in jobs:
        if poster and poster.startswith("http"):
             from urllib.parse import quote
             poster = f"/api/images/proxy?url={quote(poster)}"

        job_data = {
            "id": job.id,
            "source_path": job.source_path,
            "destination_path": job.destination_path,
            "status": job.status,
            "priority": job.priority,
            "progress_percent": job.progress_percent,
            "total_size_bytes": job.total_size_bytes,
            "copied_size_bytes": job.copied_size_bytes,
            "error_message": job.error_message,
            "created_at": job.created_at,
            "completed_at": job.completed_at,
            "media_title": title,
            "media_year": year,
            "media_rating": rating,
            "media_poster": poster,
            "media_type": mtype
        }
        enriched_jobs.append(job_data)
        
    return enriched_jobs


@app.delete("/api/copy/{job_id}")
async def cancel_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a queued or processing job."""
    job = db.query(CopyJob).filter(CopyJob.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status not in ["queued", "processing"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel {job.status} job. Only queued and processing jobs can be cancelled."
        )
    
    # Use the copy worker's cancel method which handles cleanup
    copy_worker.cancel_job(job_id)
    
    return {"message": "Job cancellation requested. Partial files will be cleaned up."}


@app.delete("/api/copy/queue")
async def clear_queue(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel all active jobs (queued and processing)."""
    jobs = db.query(CopyJob).filter(
        CopyJob.status.in_(["queued", "processing"])
    ).all()
    
    count = 0
    for job in jobs:
        job.status = "cancelled"
        job.completed_at = datetime.utcnow()
        count += 1
    
    db.commit()
    
    # Optional: Broadcast clear event to websocket if needed
    
    return {"message": f"Cancelled {count} jobs"}


@app.post("/api/copy/{job_id}/retry", response_model=CopyJobResponse)
async def retry_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retry a failed job."""
    job = db.query(CopyJob).filter(CopyJob.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "failed":
        raise HTTPException(
            status_code=400,
            detail="Can only retry failed jobs"
        )
    
    # Create a new job with the same paths
    new_job = CopyJob(
        source_path=job.source_path,
        destination_path=job.destination_path,
        status="queued",
        progress_percent=0
    )
    
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    return new_job


class PriorityUpdate(BaseModel):
    priority: int  # 0=low, 1=normal, 2=high


class ReorderRequest(BaseModel):
    job_ids: List[int]


@app.post("/api/copy/{job_id}/priority", response_model=CopyJobResponse)
async def set_job_priority(
    job_id: int,
    priority_data: PriorityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set the priority of a queued job."""
    job = db.query(CopyJob).filter(CopyJob.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "queued":
        raise HTTPException(
            status_code=400,
            detail="Can only change priority of queued jobs"
        )
    
    # Validate priority value (0=low, 1=normal, 2=high)
    if priority_data.priority not in [0, 1, 2]:
        raise HTTPException(status_code=400, detail="Priority must be 0 (low), 1 (normal), or 2 (high)")
    
    job.priority = priority_data.priority
    db.commit()
    db.refresh(job)
    
    return job


@app.post("/api/copy/reorder")
async def reorder_queue(
    reorder_data: ReorderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reorder queued jobs by setting their priorities based on position."""
    if not reorder_data.job_ids:
        raise HTTPException(status_code=400, detail="No job IDs provided")
    
    # Get all queued jobs
    jobs = db.query(CopyJob).filter(
        CopyJob.id.in_(reorder_data.job_ids),
        CopyJob.status == "queued"
    ).all()
    
    if not jobs:
        raise HTTPException(status_code=404, detail="No queued jobs found with provided IDs")
    
    job_dict = {job.id: job for job in jobs}
    
    # Set priority based on position in the list (first = highest priority)
    # We'll use higher priority values for items at the top
    total = len(reorder_data.job_ids)
    for index, job_id in enumerate(reorder_data.job_ids):
        if job_id in job_dict:
            # First item gets priority 2 (high), rest get calculated values
            # We'll use 100+ as custom priority to support any order
            job_dict[job_id].priority = 100 + (total - index)
    
    db.commit()
    
    return {"success": True, "reordered": len(jobs)}


# WebSocket endpoint
@app.websocket("/ws/progress")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time progress updates."""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and receive any client messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Copy Management API", "status": "running"}


@app.get("/api/system/status")
async def system_status(
    current_user: User = Depends(get_current_user)
):
    """Check system status including mount points."""
    # Map to frontend friendly names (source/destination)
    # Check Source
    source_exists = os.path.exists(SOURCE_BASE) and os.path.isdir(SOURCE_BASE)
    dest_exists = os.path.exists(DESTINATION_BASE) and os.path.isdir(DESTINATION_BASE)
    
    source_empty = True
    if source_exists:
        try:
            source_empty = len(os.listdir(SOURCE_BASE)) == 0
        except:
            pass
            
    dest_empty = True
    if dest_exists:
        try:
            dest_empty = len(os.listdir(DESTINATION_BASE)) == 0
        except:
            pass
            
    return {
        "zurg": { # Keeping legacy key 'zurg' for frontend compatibility or alias to 'source'
            "path": SOURCE_BASE,
            "exists": source_exists,
            "empty": source_empty,
            "contents_preview": os.listdir(SOURCE_BASE)[:5] if source_exists and not source_empty else []
        },
        "harddrive": { # Keeping legacy key 'harddrive' for frontend compatibility or alias to 'destination'
            "path": DESTINATION_BASE,
            "exists": dest_exists,
            "empty": dest_empty,
            "contents_preview": os.listdir(DESTINATION_BASE)[:5] if dest_exists and not dest_empty else []
        }
    }


@app.get("/api/stats")
async def get_transfer_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transfer statistics for various time periods."""
    from sqlalchemy import func
    
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    month_start = today_start - timedelta(days=30)
    
    def get_period_stats(start_date=None):
        """Get stats for a specific time period."""
        query = db.query(CopyJob)
        if start_date:
            query = query.filter(CopyJob.created_at >= start_date)
        
        jobs = query.all()
        
        total_count = len(jobs)
        completed = sum(1 for j in jobs if j.status == 'completed')
        failed = sum(1 for j in jobs if j.status == 'failed')
        cancelled = sum(1 for j in jobs if j.status == 'cancelled')
        total_bytes = sum(j.total_size_bytes or 0 for j in jobs if j.status == 'completed')
        
        # Calculate average duration for completed jobs
        durations = []
        for j in jobs:
            if j.status == 'completed' and j.completed_at and j.created_at:
                duration = (j.completed_at - j.created_at).total_seconds()
                if duration > 0:
                    durations.append(duration)
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Calculate average speed (bytes per second)
        speeds = []
        for j in jobs:
            if j.status == 'completed' and j.completed_at and j.created_at and j.total_size_bytes:
                duration = (j.completed_at - j.created_at).total_seconds()
                if duration > 0:
                    speeds.append(j.total_size_bytes / duration)
        
        avg_speed = sum(speeds) / len(speeds) if speeds else 0
        
        success_rate = (completed / total_count * 100) if total_count > 0 else 0
        
        return {
            "count": total_count,
            "completed": completed,
            "failed": failed,
            "cancelled": cancelled,
            "bytes": total_bytes,
            "bytes_formatted": format_size(total_bytes),
            "avg_duration": round(avg_duration, 1),
            "avg_speed": round(avg_speed, 1),
            "avg_speed_formatted": format_size(int(avg_speed)) + "/s" if avg_speed > 0 else "N/A",
            "success_rate": round(success_rate, 1)
        }
    
    # Get daily breakdown for last 7 days
    daily_breakdown = []
    for i in range(7):
        day_start = today_start - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        
        day_jobs = db.query(CopyJob).filter(
            CopyJob.created_at >= day_start,
            CopyJob.created_at < day_end
        ).all()
        
        completed = sum(1 for j in day_jobs if j.status == 'completed')
        failed = sum(1 for j in day_jobs if j.status == 'failed')
        bytes_copied = sum(j.total_size_bytes or 0 for j in day_jobs if j.status == 'completed')
        
        daily_breakdown.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "day": day_start.strftime("%a"),
            "completed": completed,
            "failed": failed,
            "bytes": bytes_copied,
            "bytes_formatted": format_size(bytes_copied)
        })
    
    return {
        "today": get_period_stats(today_start),
        "week": get_period_stats(week_start),
        "month": get_period_stats(month_start),
        "all_time": get_period_stats(None),
        "daily_breakdown": list(reversed(daily_breakdown))  # Oldest first
    }


@app.get("/api/system/disk")
async def get_disk_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get disk usage statistics from cached background worker."""
    from file_operations import format_size
    
    def get_cached_info(source: str) -> dict:
        stats = db.query(StorageStats).filter(StorageStats.source == source).first()
        if not stats:
            return {
                "total": 0,
                "used": 0,
                "free": 0,
                "percent": 0,
                "total_formatted": "N/A",
                "used_formatted": "N/A",
                "free_formatted": "N/A",
                "available": False,
                "file_count": 0,
                "folder_count": 0
            }
        
        return {
            "total": stats.total_size,
            "used": stats.used_size,
            "free": stats.free_size,
            "percent": stats.percent,
            "total_formatted": format_size(stats.total_size),
            "used_formatted": format_size(stats.used_size),
            "free_formatted": format_size(stats.free_size),
            "available": True,
            "file_count": stats.file_count,
            "folder_count": stats.folder_count,
            "updated_at": stats.updated_at.isoformat() if stats.updated_at else None
        }
    
    return {
        "zurg": get_cached_info("zurg"),
        "harddrive": get_cached_info("harddrive")
    }


# User Management Endpoints

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class UserCreateRequest(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class UserResponse(BaseModel):
    id: int
    username: str
    is_admin: bool
    require_password_change: bool
    trakt_configured: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


@app.post("/api/users/change-password")
async def change_password(
    data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change current user password"""
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    current_user.password_hash = get_password_hash(data.new_password)
    current_user.require_password_change = False
    db.commit()
    
    return {"message": "Password changed successfully"}


@app.get("/api/users/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    # Check if Trakt is configured
    trakt_setting = db.query(SystemSettings).filter(SystemSettings.key == "trakt_client_id").first()
    trakt_configured = bool(trakt_setting and trakt_setting.value)
    
    # We can't modify the ORM object directly for a computed field that doesn't exist on the model
    # So we construct the response dict
    return {
        "id": current_user.id,
        "username": current_user.username,
        "is_admin": current_user.is_admin,
        "require_password_change": current_user.require_password_change,
        "trakt_configured": trakt_configured,
        "created_at": current_user.created_at
    }


@app.post("/api/users/create", response_model=UserResponse)
async def create_user(
    data: UserCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new user (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    new_user = User(
        username=data.username,
        password_hash=get_password_hash(data.password),
        is_admin=data.is_admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@app.get("/api/users/list", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all users (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    users = db.query(User).all()
    return users




# =================================================================================
# LIBRARY & SETTINGS API 
# =================================================================================

class SettingsUpdate(BaseModel):
    trakt_client_id: Optional[str] = None
    default_movies_path: Optional[str] = None
    default_series_path: Optional[str] = None
    scan_interval_seconds: Optional[int] = None
    discord_webhook_url: Optional[str] = None
    discord_notify_success: Optional[bool] = None
    discord_notify_failure: Optional[bool] = None


class StatsFullResponse(BaseModel):
    library_stats: dict
    job_stats: dict
    storage_stats: dict
    charts: dict
    top_lists: dict
    discord_notify_success: Optional[bool] = None
    discord_notify_failure: Optional[bool] = None

# =================================================================================
# IMAGE PROXY & METADATA CACHE
# =================================================================================

# In-memory cache for metadata (Overview, Rating, Genres)
# Key: "{media_type}_{id}", Value: (data_dict, timestamp)
_metadata_cache = {}
CACHE_TTL = 3600  # 1 hour

@app.get("/api/images/proxy")
async def proxy_image(
    url: str = Query(..., description="Image URL to proxy/cache"),
    db: Session = Depends(get_db)
):
    try:
        # 1. Check DB Cache
        cached = get_cached_image_rec(db, url)
        if cached:
             # Serve from file
             headers = {
                'Cache-Control': 'public, max-age=31536000, immutable',
                'X-Image-Source': cached.source or 'unknown',
                'X-Image-Cached': 'true'
             }
             return FileResponse(
                 cached.local_path,
                 media_type=cached.mime_type or 'image/webp',
                 headers=headers
             )
        
        # 2. Download (Non-blocking)
        logger.info(f"Downloading image: {url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30, headers={'User-Agent': 'CopyCat/1.0'}) as resp:
                if resp.status != 200:
                     raise HTTPException(status_code=resp.status, detail="Failed to fetch image")
                
                image_data = await resp.read()
        
        if len(image_data) > 10 * 1024 * 1024: # 10MB limit
             return Response(content=image_data, media_type="image/jpeg") # Skip cache
             
        # Detect Type
        image_type = imghdr.what(None, image_data)
        if not image_type: image_type = 'webp' # Fallback
        mime_type = f"image/{image_type}"
        
        source = 'trakt' if 'trakt' in url else 'tmdb'
        
        # 3. Save Cache
        from image_cache import save_cached_image
        save_cached_image(db, url, image_data, mime_type, source)
        
        # Get location again
        cached = get_cached_image_rec(db, url)
        if cached:
            return FileResponse(cached.local_path, media_type=mime_type)
        else:
             return Response(content=image_data, media_type=mime_type)

    except Exception as e:
        logger.error(f"Proxy error: {e}")
        raise HTTPException(status_code=500, detail="Image proxy failed")


class BatchCopyRequest(BaseModel):
    item_ids: List[int]
    destination_path: str


@app.post("/api/library/batch-copy")
async def batch_copy_items(
    request: BatchCopyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Batch copy multiple media items from the library to a destination."""
    if not request.item_ids:
        raise HTTPException(status_code=400, detail="No item IDs provided")
    
    if not request.destination_path:
        raise HTTPException(status_code=400, detail="No destination path provided")
    
    # Get all media items by ID
    items = db.query(MediaItem).filter(MediaItem.id.in_(request.item_ids)).all()
    
    if not items:
        raise HTTPException(status_code=404, detail="No items found with provided IDs")
    
    # Validate destination path
    from file_operations import validate_path
    try:
        validate_path(DESTINATION_BASE, request.destination_path.lstrip('/'))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    dest_base = os.path.normpath(os.path.join(DESTINATION_BASE, request.destination_path.lstrip('/')))
    
    # Create copy jobs for each item
    created_jobs = []
    for item in items:
        source_path = item.full_path
        
        # Determine destination based on media type
        if item.media_type == 'tv':
            # For TV shows, keep the folder structure
            dest = os.path.join(dest_base, os.path.basename(source_path))
        else:
            # For movies, just copy the file/folder
            dest = os.path.join(dest_base, os.path.basename(source_path))
        
        job = CopyJob(
            source_path=source_path.replace('\\', '/'),
            destination_path=dest.replace('\\', '/'),
            status="queued",
            priority=1,
            progress_percent=0
        )
        db.add(job)
        created_jobs.append(job)
    
    db.commit()
    
    # Refresh to get IDs
    for job in created_jobs:
        db.refresh(job)
    
    return {
        "success": True,
        "message": f"Created {len(created_jobs)} copy jobs",
        "job_ids": [job.id for job in created_jobs]
    }



@app.get("/api/library/items")
async def get_library_items(
    background_tasks: BackgroundTasks,
    limit: int = 50,
    offset: int = 0,
    type: str = Query(None, description="movie or tv"),
    sort_by: str = Query("created_at", description="created_at, title, year, rating"),
    order: str = Query("desc", description="asc or desc"),
    search: str = Query(None, description="Search title"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get enriched media items.
    Fetches basic info from DB, then enriches with metadata from Cache/Trakt on-demand.
    """
    logger.info(f"GET /api/library/items request: type={type}, limit={limit}")
    # 1. Get Base Items
    query = db.query(MediaItem)
    if type == 'movie':
        # Lock down to movie folders
        query = query.filter(or_(
            MediaItem.full_path.ilike('%/movies/%'), 
            MediaItem.full_path.ilike('%/movie/%'),
            MediaItem.full_path.ilike('%\\movies\\%'),
            MediaItem.full_path.ilike('%\\movie\\%')
        ))
    elif type == 'tv':
        # Lock down to show folders
        query = query.filter(or_(
            MediaItem.full_path.ilike('%/shows/%'),
            MediaItem.full_path.ilike('%/show/%'),
            MediaItem.full_path.ilike('%/series/%'),
            MediaItem.full_path.ilike('%/tv/%'),
            MediaItem.full_path.ilike('%/tv shows/%'),
            MediaItem.full_path.ilike('%\\shows\\%'),
            MediaItem.full_path.ilike('%\\show\\%'),
            MediaItem.full_path.ilike('%\\series\\%'),
            MediaItem.full_path.ilike('%\\tv\\%'),
            MediaItem.full_path.ilike('%\\tv shows\\%')
        ))
    
    # 1.1 Search Filter
    if search:
        query = query.filter(MediaItem.title.ilike(f"%{search}%"))
    
    # Sort Logic
    if sort_by == 'title':
        if order == 'asc':
            query = query.order_by(MediaItem.title.asc(), MediaItem.id.asc())
        else:
            query = query.order_by(MediaItem.title.desc(), MediaItem.id.desc())
    elif sort_by == 'year':
        if order == 'asc':
            query = query.order_by(MediaItem.year.asc(), MediaItem.id.asc())
        else:
            query = query.order_by(MediaItem.year.desc().nulls_last(), MediaItem.id.desc())
    elif sort_by == 'rating':
        if order == 'asc':
            query = query.order_by(MediaItem.rating.asc(), MediaItem.id.asc())
        else:
            query = query.order_by(MediaItem.rating.desc().nulls_last(), MediaItem.id.desc())
    else:
        # Default: created_at
        if order == 'asc':
            query = query.order_by(MediaItem.created_at.asc(), MediaItem.id.asc())
        else:
            query = query.order_by(MediaItem.created_at.desc(), MediaItem.id.desc())

    # Get total count before pagination
    total_count = query.count()

    db_items = query.limit(limit).offset(offset).all()
    logger.info(f"Found {len(db_items)} base items in DB. Starting enrichment.")
    
    # 2. Enrich
    enriched_items = []
    
    # Get Trakt Key for API calls
    setting = db.query(SystemSettings).filter(SystemSettings.key == "trakt_client_id").first()
    trakt_key = decrypt_value(setting.value) if setting else None
    
    client = TraktClient(trakt_key) if trakt_key else None
    
    current_time = time.time()
    
    for item in db_items:
        # Helper to wrap proxy
        poster_src = item.poster_url
        if poster_src and poster_src.startswith("http"):
             from urllib.parse import quote
             encoded = quote(poster_src)
             poster_src = f"/api/images/proxy?url={encoded}"
        
        # Base object
        from file_operations import format_size # Ensure import available or move to top
        data = {
            "id": item.id,
            "full_path": item.full_path,
            "title": item.title,
            "year": item.year,
            "media_type": get_media_type_from_path(item.full_path),
            "tmdb_id": item.tmdb_id,
            "imdb_id": item.imdb_id,
            "poster_url": poster_src,
            "enrichment_status": item.enrichment_status,
            "size_bytes": item.size_bytes or 0,
            "size_formatted": format_size(item.size_bytes or 0),
            
            # Persisted Metadata (No longer cache based)
            "overview": item.overview,
            "rating": item.rating,
            "genres": item.genres.split(",") if item.genres else [],
            "certification": item.certification,
            "runtime": item.runtime,
            "tagline": item.tagline,
            "source_metadata": item.source_metadata # JSON String
        }
        
        # If we lack IDs, we can't enrich effectively (maybe add search fallback later)
        # But we still return them so user sees them
        enriched_items.append(data)
            
        cache_key = f"{item.media_type}_{item.tmdb_id or item.imdb_id}"
        
        # Check Cache
        if cache_key in _metadata_cache:
            cached_meta, timestamp = _metadata_cache[cache_key]
            if current_time - timestamp < CACHE_TTL:
                data.update(cached_meta)
                # Ensure poster_url from cache if DB is empty
                if not data["poster_url"] and cached_meta.get("poster_url"):
                    data["poster_url"] = cached_meta["poster_url"]
        
    # Trigger Background Enrichment if we have missing metadata
    # We check if *any* returned item is missing a poster or TMDB ID AND hasn't failed enrichment yet
    missing_meta = any(
        (not i["poster_url"] or not i["tmdb_id"]) and 
        (not i["enrichment_status"] or i["enrichment_status"] == 'pending')
        for i in enriched_items
    )
    
    
    # Global/Module level lock for enrichment to avoid concurrency explosion
    if not hasattr(app, "enrichment_lock"):
        app.enrichment_lock = False

    if missing_meta and trakt_key and not app.enrichment_lock:
        from enrichment import enrich_media_items
        
        def _enrich_task():
            if app.enrichment_lock: return 
            app.enrichment_lock = True
            
            # Fresh session for background
            from database import SessionLocal
            db_bg = SessionLocal()
            try:
                # We need an async loop for enrich_media_items since it awaits Trakt
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(enrich_media_items(db_bg))
                loop.close()
            except Exception as e:
                logger.error(f"Background enrichment failed: {e}")
            finally:
                db_bg.close()
                app.enrichment_lock = False

        background_tasks.add_task(_enrich_task)
        
    return {
        "items": enriched_items,
        "total": total_count,
        "has_more": len(enriched_items) >= limit
    }

# Background Task now only focuses on resolving IDs if missing



@app.post("/api/library/prioritize")
async def prioritize_item(
    item_id: int = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Prioritize a media item for enrichment.
    Bump priority to 10 (Highest)
    """
    item = db.query(MediaItem).filter(MediaItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    # Bump priority
    item.priority = 10
    
    # Reset status if it was failed so it gets picked up again
    if item.enrichment_status == 'failed':
         item.enrichment_status = 'pending_retry'
         item.enrichment_retry_count = 0
         
    db.commit()
    
    # Optional: trigger immediate worker check?
    # For now, the worker polls frequently enough (every 1s if busy, 30s if idle)
    # But if we want instant reaction from an idle worker, we could trigger it.
    # However, since the worker loop sleeps 30s when idle, we might wait up to 30s.
    # Ideally we'd have an event or condition variable, but for MVP just let it be picked up.
    # Optimization: If we really want it fast, we can wake up the worker
    if enrichment_worker.running:
         # This is a bit hacky but if we expose a 'wake' method or just rely on the loop
         pass

    return {"success": True}



@app.post("/api/settings")
async def update_settings(
    settings: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update system settings (Admin only)."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")
    
    # Update Trakt ID if provided
    if settings.trakt_client_id:
        # Validate first
        client = TraktClient(settings.trakt_client_id)
        is_valid = await client.validate_api()
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid Trakt Client ID")

        encrypted_key = encrypt_value(settings.trakt_client_id)
        existing = db.query(SystemSettings).filter(SystemSettings.key == "trakt_client_id").first()
        if existing:
            existing.value = encrypted_key
            existing.is_encrypted = True
            existing.updated_at = datetime.utcnow()
        else:
            new_setting = SystemSettings(key="trakt_client_id", value=encrypted_key, is_encrypted=True)
            db.add(new_setting)

    # Update Default Movies Path if provided
    if settings.default_movies_path is not None:
        existing = db.query(SystemSettings).filter(SystemSettings.key == "default_movies_path").first()
        if existing:
            existing.value = settings.default_movies_path
            existing.updated_at = datetime.utcnow()
        else:
            new_setting = SystemSettings(key="default_movies_path", value=settings.default_movies_path, is_encrypted=False)
            db.add(new_setting)

    # Update Default Series Path if provided
    if settings.default_series_path is not None:
        existing = db.query(SystemSettings).filter(SystemSettings.key == "default_series_path").first()
        if existing:
            existing.value = settings.default_series_path
            existing.updated_at = datetime.utcnow()
        else:
            new_setting = SystemSettings(key="default_series_path", value=settings.default_series_path, is_encrypted=False)
            db.add(new_setting)

    # Update Scan Interval if provided
    if settings.scan_interval_seconds is not None:
        # Validate interval (minimum 30 seconds, maximum 24 hours)
        if settings.scan_interval_seconds < 30:
            raise HTTPException(status_code=400, detail="Scan interval must be at least 30 seconds")
        if settings.scan_interval_seconds > 86400:  # 24 hours
            raise HTTPException(status_code=400, detail="Scan interval cannot exceed 24 hours (86400 seconds)")

        existing = db.query(SystemSettings).filter(SystemSettings.key == "scan_interval_seconds").first()
        if existing:
            existing.value = str(settings.scan_interval_seconds)
            existing.updated_at = datetime.utcnow()
        else:
            new_setting = SystemSettings(key="scan_interval_seconds", value=str(settings.scan_interval_seconds), is_encrypted=False)
            db.add(new_setting)
    
    # Update Discord Webhook URL if provided
    if settings.discord_webhook_url is not None:
        encrypted_url = encrypt_value(settings.discord_webhook_url) if settings.discord_webhook_url else ""
        existing = db.query(SystemSettings).filter(SystemSettings.key == "discord_webhook_url").first()
        if existing:
            existing.value = encrypted_url
            existing.is_encrypted = True
            existing.updated_at = datetime.utcnow()
        else:
            new_setting = SystemSettings(key="discord_webhook_url", value=encrypted_url, is_encrypted=True)
            db.add(new_setting)
    
    # Update Discord Notify Success if provided
    if settings.discord_notify_success is not None:
        existing = db.query(SystemSettings).filter(SystemSettings.key == "discord_notify_success").first()
        val = "true" if settings.discord_notify_success else "false"
        if existing:
            existing.value = val
            existing.updated_at = datetime.utcnow()
        else:
            new_setting = SystemSettings(key="discord_notify_success", value=val, is_encrypted=False)
            db.add(new_setting)
    
    # Update Discord Notify Failure if provided
    if settings.discord_notify_failure is not None:
        existing = db.query(SystemSettings).filter(SystemSettings.key == "discord_notify_failure").first()
        val = "true" if settings.discord_notify_failure else "false"
        if existing:
            existing.value = val
            existing.updated_at = datetime.utcnow()
        else:
            new_setting = SystemSettings(key="discord_notify_failure", value=val, is_encrypted=False)
            db.add(new_setting)
    
    db.commit()
    
    # Start enrichment worker if Trakt ID was just added and it's not running
    if settings.trakt_client_id:
        from enrichment_worker import enrichment_worker
        if not enrichment_worker.running:
            logger.info("Starting enrichment worker after settings update")
            asyncio.create_task(enrichment_worker.start())

    return {"success": True}

@app.get("/api/settings")
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all settings (masked)."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")

    def get_val(key):
        s = db.query(SystemSettings).filter(SystemSettings.key == key).first()
        return s.value if s else None

    trakt_val = get_val("trakt_client_id")
    scan_interval_val = get_val("scan_interval_seconds")
    discord_webhook_val = get_val("discord_webhook_url")
    discord_notify_success = get_val("discord_notify_success")
    discord_notify_failure = get_val("discord_notify_failure")

    return {
        "trakt_client_id": "********" if trakt_val else None,
        "trakt_configured": bool(trakt_val),
        "default_movies_path": get_val("default_movies_path"),
        "default_series_path": get_val("default_series_path"),
        "discord_webhook_configured": bool(discord_webhook_val),
        "discord_notify_success": discord_notify_success == "true" if discord_notify_success else True,
        "discord_notify_failure": discord_notify_failure == "true" if discord_notify_failure else True,
        "scan_interval_seconds": int(scan_interval_val) if scan_interval_val else 300
    }

@app.post("/api/settings/validate")
async def validate_settings(
    settings: SettingsUpdate,
    current_user: User = Depends(get_current_user)
):
    """Validate Trakt Client ID."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")

    client = TraktClient(settings.trakt_client_id)
    is_valid = await client.validate_api()
    
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid Trakt Client ID")
        
    return {"valid": True}

@app.get("/api/settings/status")
async def get_settings_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if critical settings (Trakt Key) are configured."""
    setting = db.query(SystemSettings).filter(SystemSettings.key == "trakt_client_id").first()
    has_key = setting is not None and len(setting.value) > 0
    
    movies_path = db.query(SystemSettings).filter(SystemSettings.key == "default_movies_path").first()
    series_path = db.query(SystemSettings).filter(SystemSettings.key == "default_series_path").first()
    
    return {
        "has_trakt_key": has_key,
        "movies_configured": bool(movies_path and movies_path.value),
        "series_configured": bool(series_path and series_path.value),
        "require_password_change": current_user.require_password_change
    }


@app.post("/api/settings/test-discord")
async def test_discord_webhook(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test the configured Discord webhook."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")
    
    # Get webhook URL
    webhook_setting = db.query(SystemSettings).filter(
        SystemSettings.key == "discord_webhook_url"
    ).first()
    
    if not webhook_setting or not webhook_setting.value:
        raise HTTPException(status_code=400, detail="No Discord webhook configured")
    
    webhook_url = decrypt_value(webhook_setting.value)
    if not webhook_url:
        raise HTTPException(status_code=400, detail="Invalid webhook URL")
    
    from discord_notifier import discord_notifier
    discord_notifier.set_webhook_url(webhook_url)
    
    success = await discord_notifier.test_webhook()
    
    if success:
        return {"success": True, "message": "Test notification sent successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send test notification")


@app.post("/api/library/scan")
async def scan_library(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger a Library Scan using the periodic scanner."""
    logger.info("Received Library Scan Request - triggering immediate scan")

@app.get("/api/stats/full", response_model=StatsFullResponse)
def get_full_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Aggregate all statistics for the dashboard.
    """
    # 1. Library Stats
    total_items = db.query(MediaItem).count()
    movies_count = db.query(MediaItem).filter(MediaItem.media_type == 'movie').count()
    tv_count = db.query(MediaItem).filter(MediaItem.media_type == 'tv').count()
    total_size = db.query(func.sum(MediaItem.size_bytes)).scalar() or 0
    
    # Genres Breakdown
    # This is rough as genres are CSV strings, ideally we'd normalize but for now we fetch all and parse in py
    # For performance on large DBs, this should be cached or normalized. 
    # For <10k items, python processing is fine.
    all_genres = db.query(MediaItem.genres).filter(MediaItem.genres != None).all()
    genre_counts = {}
    for g_row in all_genres:
        if not g_row[0]: continue
        genres = [x.strip() for x in g_row[0].split(',')]
        for g in genres:
            genre_counts[g] = genre_counts.get(g, 0) + 1
            
    top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:8]

    # Resolution Breakdown (from source_metadata)
    # Again, parsing JSON text in SQL is hard in SQLite/Generic, so we do Python scan
    # Limit to last 1000 items for performance if needed, but doing all for accuracy
    resolutions = {}
    audio_codecs = {}
    total_duration_mins = 0
    
    # We fetch relevant columns for python-side processing
    # Optimization: On very large libraries, this should be done via SQL GroupBy or specialized queries
    all_metadata = db.query(MediaItem.source_metadata, MediaItem.runtime, MediaItem.year).all()
    
    decade_counts = {}
    
    for row in all_metadata:
        m_json, r_runtime, r_year = row
        
        # 1. Runtime
        if r_runtime:
            total_duration_mins += r_runtime
            
        # 2. Decades
        if r_year:
            try:
                decade = (int(r_year) // 10) * 10
                decade_str = f"{decade}s"
                decade_counts[decade_str] = decade_counts.get(decade_str, 0) + 1
            except:
                pass

        # 3. Tech Metadata (Res/Audio)
        if m_json:
            try:
                meta = json.loads(m_json) if isinstance(m_json, str) else m_json
                if not isinstance(meta, dict): continue
                
                # Resolution
                if meta.get('resolution'):
                    res = meta['resolution'][0] if isinstance(meta['resolution'], list) else meta['resolution']
                    resolutions[res] = resolutions.get(res, 0) + 1
                
                # Audio
                if meta.get('audio_channels'):
                    # Simplify audio (e.g. "5.1", "7.1", "2.0")
                    # Sometimes it's a list, sometimes value
                    aud = meta['audio_channels']
                    if isinstance(aud, list): aud = aud[0]
                    audio_codecs[aud] = audio_codecs.get(aud, 0) + 1
            except:
                pass
                
    # Sort decades
    decade_counts = dict(sorted(decade_counts.items()))
            
    # 2. Job Stats
    completed_jobs = db.query(CopyJob).filter(CopyJob.status == 'completed')
    failed_jobs = db.query(CopyJob).filter(CopyJob.status == 'failed')
    
    total_transferred = db.query(func.sum(CopyJob.copied_size_bytes)).filter(CopyJob.status == 'completed').scalar() or 0
    success_rate = 0
    total_finished = completed_jobs.count() + failed_jobs.count()
    if total_finished > 0:
        success_rate = (completed_jobs.count() / total_finished) * 100

    # Activity (Last 14 days)
    import datetime
    today = datetime.datetime.utcnow().date()
    activity_data = {}
    for i in range(14):
        d = today - datetime.timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")
        activity_data[d_str] = 0
        
    recent_jobs = db.query(CopyJob).filter(
        CopyJob.created_at >= (datetime.datetime.utcnow() - datetime.timedelta(days=14)),
        CopyJob.status == 'completed'
    ).all()
    
    for job in recent_jobs:
        d_str = job.created_at.date().strftime("%Y-%m-%d")
        if d_str in activity_data:
            activity_data[d_str] += (job.copied_size_bytes or 0)

    # 3. Top Lists
    largest_files = db.query(MediaItem).order_by(MediaItem.size_bytes.desc()).limit(5).all()
    # Removed highest_rated as requested

    # 4. Storage
    storage = {
        s.source: {"percent": s.percent, "free": s.free_size, "total": s.total_size} 
        for s in db.query(StorageStats).all()
    }

    return {
        "library_stats": {
            "total_items": total_items,
            "movies_count": movies_count,
            "tv_count": tv_count,
            "total_size_bytes": total_size,
            "total_runtime_minutes": total_duration_mins,
            "avg_file_size": (total_size / total_items) if total_items > 0 else 0
        },
        "job_stats": {
            "total_transferred_bytes": total_transferred,
            "success_rate": round(success_rate, 1),
            "completed_count": completed_jobs.count(),
            "failed_count": failed_jobs.count()
        },
        "storage_stats": storage,
        "charts": {
            "genres": dict(top_genres),
            "resolutions": resolutions,
            "audio_codecs": audio_codecs,
            "decades": decade_counts,
            "activity": activity_data # Date -> Bytes
        },
        "top_lists": {
            "largest_files": [
                {"title": i.title, "size": format_size(i.size_bytes), "path": i.full_path} 
                for i in largest_files
            ]
        }
    }



async def background_enrichment_wrapper():
    """
    Wrapper to ensure enrichment runs with a fresh DB session in the background.
    """
    db = SessionLocal()
    try:
        from enrichment import enrich_media_items
        # Run full enrichment (IDs + Metadata + Images)
        # This now loops internally until no more items need enrichment
        await enrich_media_items(db, batch_size=100) 
    except Exception as e:
        logger.error(f"Background enrichment failed: {e}")
    finally:
        db.close()

# SPA Static Files (Must be last)
# Mount assets folder
app.mount("/_nuxt", StaticFiles(directory="static/_nuxt", check_dir=False), name="static")

# Catch-all for SPA
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # If it's an API route that 404'd, return 404 JSON, not HTML
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API Endpoint not found")
    
    # Otherwise serve index.html
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"message": "CopyCat Backend Running (Frontend not built)"}




