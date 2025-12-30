import threading
import shutil
import os
import asyncio
from datetime import datetime
from typing import Set, Optional
from sqlalchemy.orm import Session
from database import SessionLocal
from models import CopyJob, SystemSettings
import time
from discord_notifier import discord_notifier
from security_utils import decrypt_value


class CopyWorker:
    def __init__(self):
        self.is_running = False
        self.thread = None
        self.current_job_id = None
        self.websocket_manager = None
        self.scanner = None # For triggering stats updates
        self.stop_flag = False
        self.cancelled_jobs: Set[int] = set()  # Track cancelled job IDs
        
    def set_websocket_manager(self, manager):
        """Set the WebSocket manager for broadcasting progress."""
        self.websocket_manager = manager

    def set_scanner(self, scanner):
        """Set the scanner instance for triggering stats updates."""
        self.scanner = scanner
    
    def cancel_job(self, job_id: int):
        """
        Cancel a specific job. 
        If it's the current job, marks it for cancellation.
        If it's queued, marks it as cancelled immediately.
        """
        self.cancelled_jobs.add(job_id)
        print(f"Job {job_id} marked for cancellation")
        
        # If this isn't the current job, update it in DB immediately
        if self.current_job_id != job_id:
            db = SessionLocal()
            try:
                job = db.query(CopyJob).filter(CopyJob.id == job_id).first()
                if job and job.status in ['queued', 'processing']:
                    job.status = 'cancelled'
                    job.error_message = 'Cancelled by user'
                    db.commit()
                    print(f"Job {job_id} cancelled (was {job.status})")
            finally:
                db.close()
    
    def start(self):
        """Start the background worker thread."""
        if not self.is_running:
            self.is_running = True
            self.stop_flag = False
            self.thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.thread.start()
            print("Copy worker started")
    
    def stop(self):
        """Stop the background worker thread."""
        self.stop_flag = True
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def _worker_loop(self):
        """Main worker loop that processes queued jobs."""
        while self.is_running and not self.stop_flag:
            db = SessionLocal()
            try:
                # Get the next queued job (highest priority first, then oldest)
                job = db.query(CopyJob).filter(
                    CopyJob.status == "queued"
                ).order_by(CopyJob.priority.desc(), CopyJob.created_at).first()
                
                if job:
                    self.current_job_id = job.id
                    self._process_job(db, job)
                    self.current_job_id = None
                else:
                    # No jobs in queue, wait a bit
                    time.sleep(2)
            except Exception as e:
                print(f"Error in worker loop: {e}")
                time.sleep(5)
            finally:
                db.close()
    
    def _process_job(self, db: Session, job: CopyJob):
        """Process a single copy job."""
        print(f"Processing job {job.id}: {job.source_path} -> {job.destination_path}")
        
        # Check if job was cancelled before starting
        if job.id in self.cancelled_jobs:
            job.status = "cancelled"
            job.error_message = "Cancelled by user before processing"
            db.commit()
            self.cancelled_jobs.remove(job.id)
            return
        
        try:
            # Update status to processing
            job.status = "processing"
            job.progress_percent = 0
            db.commit()
            self._broadcast_progress(job)
            
            # Check if source exists
            if not os.path.exists(job.source_path):
                raise Exception(f"Source path does not exist: {job.source_path}")
            
            # Calculate total size
            total_size = self._get_total_size(job.source_path)
            job.total_size_bytes = total_size
            db.commit()
            
            # Prepare destination
            dest_parent = os.path.dirname(job.destination_path)
            if not os.path.exists(dest_parent):
                os.makedirs(dest_parent, exist_ok=True)
            
            # Perform the copy with progress tracking
            copied_bytes = [0]  # Use list to allow modification in nested function
            last_update = [0]  # Track last update to avoid too frequent updates
            file_bytes_tracked = {}  # Track bytes per file to avoid double-counting
            
            def copy_progress(src, dst, bytes_copied_in_file=None, file_size=None):
                """Enhanced callback for chunk-level progress tracking."""
                # Check for cancellation during copy
                if job.id in self.cancelled_jobs:
                    raise InterruptedError(f"Job {job.id} cancelled by user")
                
                # Handle chunk-level progress (new signature)
                if bytes_copied_in_file is not None and file_size is not None:
                    # Track the highest bytes_copied for this file to avoid double counting
                    if src not in file_bytes_tracked:
                        file_bytes_tracked[src] = 0
                    
                    # Calculate the delta (new bytes since last update for this file)
                    delta = bytes_copied_in_file - file_bytes_tracked[src]
                    file_bytes_tracked[src] = bytes_copied_in_file
                    copied_bytes[0] += delta
                # Handle old-style file completion callback
                elif os.path.isfile(src):
                    # Only count if we haven't tracked this file yet
                    if src not in file_bytes_tracked:
                        size = os.path.getsize(src)
                        copied_bytes[0] += size
                        file_bytes_tracked[src] = size
                
                # Update progress more frequently - every 1MB or 1%
                update_threshold = max(total_size * 0.01, 1 * 1024 * 1024)
                if copied_bytes[0] - last_update[0] >= update_threshold:
                    progress = int((copied_bytes[0] / total_size) * 100) if total_size > 0 else 0
                    job.copied_size_bytes = copied_bytes[0]
                    job.progress_percent = min(progress, 99)  # Never show 100% until complete
                    db.commit()
                    self._broadcast_progress(job)
                    last_update[0] = copied_bytes[0]
                    print(f"Progress update: Job {job.id} - {progress}% ({self._format_size(copied_bytes[0])} / {self._format_size(total_size)})")
            
            # Copy the directory or file
            if os.path.isdir(job.source_path):
                # Remove destination if it exists (to avoid conflicts)
                if os.path.exists(job.destination_path):
                    if os.path.isdir(job.destination_path):
                        shutil.rmtree(job.destination_path)
                    else:
                        os.remove(job.destination_path)
                
                shutil.copytree(
                    job.source_path,
                    job.destination_path,
                    copy_function=lambda src, dst, **kwargs: self._copy_with_callback(src, dst, copy_progress, **kwargs),
                    dirs_exist_ok=False
                )
            else:
                # Single file copy with chunked progress
                dest_path = job.destination_path
                if os.path.exists(dest_path) and os.path.isdir(dest_path):
                    dest_path = os.path.join(dest_path, os.path.basename(job.source_path))
                
                self._copy_file_with_progress(job.source_path, dest_path, copy_progress)
            
            # Mark as completed
            job.status = "completed"
            job.progress_percent = 100
            job.copied_size_bytes = total_size
            job.completed_at = datetime.utcnow()
            db.commit()
            self._broadcast_progress(job)
            
            # Send Discord notification
            duration = (job.completed_at - job.created_at).total_seconds()
            self._send_discord_notification(db, job, duration)
            
            # Trigger stats update to keep dashboard live
            if self.scanner:
                print(f"Job {job.id}: Triggering post-copy stats update...")
                try:
                    self.scanner.update_storage_stats(db)
                except Exception as e:
                    print(f"Post-copy stats update failed: {e}")

            print(f"Job {job.id} completed successfully")
            
        except InterruptedError as e:
            # Job was cancelled - clean up partial file
            print(f"Job {job.id} cancelled: {e}")
            
            # Delete the partially copied file/directory
            try:
                if os.path.exists(job.destination_path):
                    if os.path.isdir(job.destination_path):
                        shutil.rmtree(job.destination_path)
                        print(f"Removed partial directory: {job.destination_path}")
                    else:
                        os.remove(job.destination_path)
                        print(f"Removed partial file: {job.destination_path}")
            except Exception as cleanup_error:
                print(f"Error cleaning up partial file: {cleanup_error}")
            
            job.status = "cancelled"
            job.error_message = "Cancelled by user"
            job.completed_at = datetime.utcnow()
            db.commit()
            self._broadcast_progress(job)
            
            # Send Discord notification
            duration = (job.completed_at - job.created_at).total_seconds()
            self._send_discord_notification(db, job, duration)
            
            # Remove from cancelled set
            if job.id in self.cancelled_jobs:
                self.cancelled_jobs.remove(job.id)
            
        except Exception as e:
            print(f"Job {job.id} failed: {e}")
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()
            self._broadcast_progress(job)
            
            # Send Discord notification
            duration = (job.completed_at - job.created_at).total_seconds()
            self._send_discord_notification(db, job, duration)
    
    def _copy_with_callback(self, src, dst, callback, **kwargs):
        """Copy file with chunk-level progress callback."""
        if os.path.isfile(src):
            self._copy_file_with_progress(src, dst, callback)
        return dst
    
    def _copy_file_with_progress(self, src: str, dst: str, callback) -> None:
        """Copy a file in chunks with progress reporting."""
        chunk_size = 1024 * 1024  # 1MB chunks
        
        # Get file size
        file_size = os.path.getsize(src)
        
        # Copy file content in chunks
        with open(src, 'rb') as fsrc:
            with open(dst, 'wb') as fdst:
                copied = 0
                while True:
                    chunk = fsrc.read(chunk_size)
                    if not chunk:
                        break
                    fdst.write(chunk)
                    copied += len(chunk)
                    
                    # Report progress for this chunk
                    callback(src, dst, copied, file_size)
        
        # Copy file metadata after content
        shutil.copystat(src, dst)
    
    def _get_total_size(self, path: str) -> int:
        """Calculate total size of files to be copied."""
        total_size = 0
        if os.path.isfile(path):
            return os.path.getsize(path)
        
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except (OSError, FileNotFoundError):
                    pass
        return total_size
    
    def _send_discord_notification(self, db: Session, job: CopyJob, duration: float):
        """Send Discord notification for job status change."""
        try:
            # Check if Discord notifications are enabled
            webhook_setting = db.query(SystemSettings).filter(
                SystemSettings.key == "discord_webhook_url"
            ).first()
            
            if not webhook_setting or not webhook_setting.value:
                return
            
            webhook_url = decrypt_value(webhook_setting.value)
            if not webhook_url:
                return
            
            # Check notification preferences
            notify_success_setting = db.query(SystemSettings).filter(
                SystemSettings.key == "discord_notify_success"
            ).first()
            notify_failure_setting = db.query(SystemSettings).filter(
                SystemSettings.key == "discord_notify_failure"
            ).first()
            
            notify_success = notify_success_setting and notify_success_setting.value == "true"
            notify_failure = notify_failure_setting and notify_failure_setting.value == "true"
            
            # Default to true if not set
            if not notify_success_setting:
                notify_success = True
            if not notify_failure_setting:
                notify_failure = True
            
            # Check if we should send for this status
            if job.status == "completed" and not notify_success:
                return
            if job.status in ["failed", "cancelled"] and not notify_failure:
                return
            
            # Retrieve enrichment info (title, poster)
            media_title = None
            poster_url = None
            
            # Try to get from CopyJob fields if they exist, or join with MediaItem
            try:
                # Check for enriched title in MediaItem (by matching path)
                from models import MediaItem
                media_item = db.query(MediaItem).filter(
                    MediaItem.full_path == job.source_path
                ).first()
                if media_item:
                    media_title = media_item.title
                    poster_url = media_item.poster_url

                # Fallback to job title if set (some jobs might have title directly)
                if not media_title and hasattr(job, 'title') and job.title:
                    media_title = job.title
            except Exception as e:
                print(f"Error fetching metadata for notification: {e}")

            # Update notifier URL and send
            discord_notifier.set_webhook_url(webhook_url)
            
            # Run async notification in thread-safe way
            import asyncio
            loop = getattr(self.websocket_manager, '_loop', None)
            if loop and loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    discord_notifier.send_job_notification(
                        job_id=job.id,
                        source_path=job.source_path,
                        destination_path=job.destination_path,
                        status=job.status,
                        total_size_bytes=job.total_size_bytes or 0,
                        duration_seconds=duration,
                        error_message=job.error_message,
                        media_title=media_title,
                        poster_url=poster_url
                    ),
                    loop
                )
            else:
                # Fallback: create new event loop
                try:
                    asyncio.run(discord_notifier.send_job_notification(
                        job_id=job.id,
                        source_path=job.source_path,
                        destination_path=job.destination_path,
                        status=job.status,
                        total_size_bytes=job.total_size_bytes or 0,
                        duration_seconds=duration,
                        error_message=job.error_message,
                        media_title=media_title,
                        poster_url=poster_url
                    ))
                except:
                    pass
                    
        except Exception as e:
            print(f"Error sending Discord notification: {e}")

    def _broadcast_progress(self, job: CopyJob):
        """Broadcast job progress to all connected WebSocket clients."""
        if self.websocket_manager:
            try:
                progress_data = {
                    "job_id": job.id,
                    "status": job.status,
                    "progress_percent": job.progress_percent,
                    "copied_size_bytes": job.copied_size_bytes,
                    "total_size_bytes": job.total_size_bytes
                }
                
                # Use asyncio.run_coroutine_threadsafe to call async function from thread
                import asyncio
                loop = getattr(self.websocket_manager, '_loop', None)
                if loop and loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        self.websocket_manager.broadcast_progress(progress_data),
                        loop
                    )
                    print(f"WebSocket broadcast: Job {job.id} - {job.progress_percent}% ({self._format_size(job.copied_size_bytes)} / {self._format_size(job.total_size_bytes)})")
                else:
                    # Fallback if no event loop available
                    print(f"Warning: No active event loop for WebSocket. Progress: Job {job.id} - {job.progress_percent}%")
            except Exception as e:
                print(f"Error broadcasting progress for job {job.id}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"Warning: No WebSocket manager available. Progress: Job {job.id} - {job.progress_percent}%")
    
    def _format_size(self, bytes_size: int) -> str:
        """Format bytes to human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} PB"


# Global worker instance
copy_worker = CopyWorker()

