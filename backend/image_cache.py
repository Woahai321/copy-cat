import os
import hashlib
import tempfile
import logging
import imghdr
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import select
from models import CachedImage

# Configuration
DATA_DIR = os.getenv("DATABASE_DIR", "/data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")

logger = logging.getLogger(__name__)

def ensure_images_directory():
    """Ensure data/images exists."""
    os.makedirs(IMAGES_DIR, exist_ok=True)
    return IMAGES_DIR

def generate_image_filename(image_url: str, mime_type: str = None) -> str:
    """Generate SHA256 has filename."""
    url_hash = hashlib.sha256(image_url.encode('utf-8')).hexdigest()[:32]
    
    extension = 'webp'
    if mime_type:
        mime_to_ext = {
            'image/webp': 'webp',
            'image/jpeg': 'jpg',
            'image/jpg': 'jpg',
            'image/png': 'png',
            'image/gif': 'gif',
            'image/svg+xml': 'svg'
        }
        extension = mime_to_ext.get(mime_type.lower(), 'webp')
    else:
         # Fallback
        url_lower = image_url.lower()
        if '.jpg' in url_lower or '.jpeg' in url_lower:
            extension = 'jpg'
        elif '.png' in url_lower:
            extension = 'png'
        elif '.gif' in url_lower:
            extension = 'gif'
    
    return f"{url_hash}.{extension}"

def save_cached_image(
    db: Session,
    image_url: str,
    image_data: bytes,
    mime_type: str = None,
    source: str = 'trakt',
    width: int = None,
    height: int = None
) -> int:
    """Save image to filesystem and DB atomically."""
    try:
        images_dir = ensure_images_directory()
        filename = generate_image_filename(image_url, mime_type)
        local_path = os.path.join(images_dir, filename)
        
        # Atomic Write
        if not os.path.exists(local_path):
            temp_fd, temp_path = tempfile.mkstemp(dir=images_dir)
            try:
                with os.fdopen(temp_fd, 'wb') as tmp:
                    tmp.write(image_data)
                
                os.replace(temp_path, local_path)
                logger.info(f"Saved image to {local_path}")
            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise e
        
        file_size = len(image_data)
        
        # DB Update (Upsert logic)
        existing = db.query(CachedImage).filter(CachedImage.image_url == image_url).first()
        
        if existing:
            existing.local_path = local_path
            existing.mime_type = mime_type
            existing.file_size = file_size
            existing.last_accessed = datetime.utcnow()
            existing.source = source
            existing.width = width
            existing.height = height
            db.commit()
            return existing.id
        else:
            new_img = CachedImage(
                image_url=image_url,
                local_path=local_path,
                mime_type=mime_type,
                file_size=file_size,
                source=source,
                width=width,
                height=height,
                cached_at=datetime.utcnow(),
                last_accessed=datetime.utcnow()
            )
            db.add(new_img)
            db.commit()
            db.refresh(new_img)
            return new_img.id

    except Exception as e:
        logger.error(f"Error saving cached image {image_url}: {e}")
        raise

def get_cached_image_rec(db: Session, image_url: str):
    """Get metadata from DB and verify file exists."""
    cached = db.query(CachedImage).filter(CachedImage.image_url == image_url).first()
    
    if cached:
        if cached.local_path and os.path.exists(cached.local_path):
            # Update access time
            cached.last_accessed = datetime.utcnow()
            db.commit()
            return cached
        else:
             logger.warning(f"Cached file missing for {image_url}")
             return None
    return None
