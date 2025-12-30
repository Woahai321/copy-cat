"""
Background worker for periodic media directory scanning.
Scans for new media items at configured intervals.
"""
import asyncio
import logging
from sqlalchemy.orm import Session
from database import SessionLocal
from media_scanner import MediaScanner
from models import SystemSettings, StorageStats
from datetime import datetime
import os
import shutil
from file_operations import format_size

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PeriodicScanner:
    """Background worker for periodic media directory scanning"""

    def __init__(self, base_path: str):
        self.running = False
        self.task = None
        self.base_path = base_path
        self._scan_lock = asyncio.Lock()
        self._enrichment_running = False

    def get_scan_interval(self, db: Session) -> int:
        """Get the scan interval from settings, default to 300 seconds (5 minutes)"""
        setting = db.query(SystemSettings).filter(SystemSettings.key == "scan_interval_seconds").first()
        if setting and setting.value:
            try:
                return int(setting.value)
            except ValueError:
                pass
        return 300  # Default 5 minutes

    def _get_folder_stats(self, path: str) -> dict:
        """Calculate size, file count, and folder count for a directory."""
        total_size = 0
        file_count = 0
        folder_count = 0
        
        try:
            if not os.path.exists(path):
                return {"size": 0, "files": 0, "folders": 0}
                
            for root, dirs, files in os.walk(path):
                folder_count += len(dirs)
                file_count += len(files)
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        # Skip if it's a broken symlink
                        if os.path.exists(fp):
                            total_size += os.path.getsize(fp)
                    except:
                        pass
            return {"size": total_size, "files": file_count, "folders": folder_count}
        except Exception as e:
            logger.error(f"Error calculating folder stats for {path}: {e}")
            return {"size": 0, "files": 0, "folders": 0}

    def update_storage_stats(self, db: Session):
        """Update cached storage stats for Zurg and Harddrive."""
        try:
            logger.info("📊 Updating background storage statistics...")
            
            # 1. Source (Zurg/Cloud) - specifically /movies and /shows
            source_total_size = 0
            source_file_count = 0
            source_folder_count = 0
            
            # Get Source base path
            source_base = self.base_path
            target_subdirs = ["movies", "movie", "shows", "show", "tv", "series", "tv shows"]
            
            for subdir in target_subdirs:
                path = os.path.join(source_base, subdir)
                if os.path.exists(path):
                    stats = self._get_folder_stats(path)
                    source_total_size += stats["size"]
                    source_file_count += stats["files"]
                    source_folder_count += stats["folders"]
            
            # Save Source Stats (1PB total for cloud display)
            # Legacy key 'zurg' used for stats table to avoid migration complexity for now, or assume 'zurg' matches 'source'
            # Let's check if we should migrate the key? 
            # Ideally we keep 'zurg' in DB for now to not break historical stats or frontend charts if any.
            # But the detailed plan implied genericizing.
            # Let's map 'source' -> 'zurg' record in DB for backward compat in this file only.
            
            zurg_stats = db.query(StorageStats).filter(StorageStats.source == 'zurg').first()
            if not zurg_stats:
                zurg_stats = StorageStats(source='zurg')
                db.add(zurg_stats)
            
            zurg_stats.used_size = source_total_size
            zurg_stats.total_size = 1024 * 1024 * 1024 * 1024 * 1024  # 1 PB
            zurg_stats.free_size = zurg_stats.total_size - zurg_stats.used_size
            zurg_stats.percent = round((zurg_stats.used_size / zurg_stats.total_size * 100), 2)
            zurg_stats.file_count = source_file_count
            zurg_stats.folder_count = source_folder_count
            zurg_stats.updated_at = datetime.utcnow()
            
            # 2. Destination (Local/Harddrive)
            # Use os.getenv as fallback if settings not set
            dest_base = os.getenv("DESTINATION_MOUNT", "/mnt/destination")
            
            # ALWAYS scan the full base directory to get accurate drive stats
            # This ensures dashboard shows total files on the drive, not just in configured folders
            dest_paths = [dest_base]
            
            dest_total_size = 0
            dest_file_count = 0
            dest_folder_count = 0
            
            for path in dest_paths:
                if os.path.exists(path):
                    stats = self._get_folder_stats(path)
                    dest_total_size += stats["size"]
                    dest_file_count += stats["files"]
                    dest_folder_count += stats["folders"]
            
            # Use shutil for REAL disk capacity on the destination
            dest_stats = db.query(StorageStats).filter(StorageStats.source == 'harddrive').first()
            if not dest_stats:
                dest_stats = StorageStats(source='harddrive')
                db.add(dest_stats)
            
            # SAFETY CHECK: If we found 0 bytes but previously had significant data (>1GB), 
            # and the drive technically "exists", we might be seeing a temporary mount glitch (empty folder).
            # Don't zero it out immediately unless we are sure.
            if dest_total_size == 0 and dest_stats.used_size and dest_stats.used_size > 1024*1024*1024:
                 logger.warning(f"⚠️ Destination scan returned 0 bytes but previous contained {format_size(dest_stats.used_size)}. Assuming temporary mount issue and keeping old stats.")
                 # Keep old values for used_size, file_count, folder_count
                 dest_total_size = dest_stats.used_size
                 dest_file_count = dest_stats.file_count
                 dest_folder_count = dest_stats.folder_count
            
            try:
                real_usage = shutil.disk_usage(dest_base)
                dest_stats.total_size = real_usage.total
                dest_stats.free_size = real_usage.free
                # Use REAL disk usage
                dest_stats.used_size = real_usage.used
                dest_stats.percent = round((real_usage.used / real_usage.total * 100), 2)
            except:
                # Fallback if shutil fails
                dest_stats.total_size = 1024 * 1024 * 1024 * 1024 * 1024 # 1 PB fallback
                dest_stats.used_size = dest_total_size
                dest_stats.free_size = dest_stats.total_size - dest_stats.used_size
                dest_stats.percent = round((dest_stats.used_size / dest_stats.total_size * 100), 2)
                
            dest_stats.file_count = dest_file_count
            dest_stats.folder_count = dest_folder_count
            dest_stats.updated_at = datetime.utcnow()
            
            db.commit()
            logger.info("✅ Storage statistics updated")
        except Exception as e:
            logger.error(f"Failed to update storage stats: {e}")
            db.rollback()

    async def scan_once(self, db: Session) -> int:
        """
        Perform a single scan of the media directory.
        Returns the number of items processed.
        """
        async with self._scan_lock:
            try:
                # 1. High Priority: Source Discovery (Non-blocking thread)
                logger.info("🔍 [PRIORITY] Starting media source discovery (new/missing files)...")
                scanner = MediaScanner(db, self.base_path)
                count = await asyncio.to_thread(scanner.scan_directory)

                # 2. Trigger Enrichment (Low Priority, Background)
                if count > 0:
                    logger.info(f"📊 Source scan complete: {count} new/updated items found.")
                else:
                    logger.info("📊 Source scan complete: No new items found.")

                # Always try to trigger enrichment if new items exist OR if we have pending items
                # This is non-blocking to ensure storage stats and next scan run on time
                asyncio.create_task(self._safe_enrich())

                return count
            except Exception as e:
                logger.error(f"Source discovery failed: {e}")
                return 0

    async def _safe_enrich(self):
        """Helper to run enrichment in background without blocking or overlapping"""
        if getattr(self, '_enrichment_running', False):
            logger.debug("⏭️ Enrichment already in progress, skipping trigger.")
            return

        db = SessionLocal()
        try:
            self._enrichment_running = True
            from enrichment import enrich_media_items
            await enrich_media_items(db, batch_size=20)
        except Exception as e:
            logger.error(f"Background enrichment error: {e}")
        finally:
            self._enrichment_running = False
            db.close()

    async def start(self):
        """Start the periodic scanning loop"""
        self.running = True
        logger.info("🚀 Periodic scanner started")

        while self.running:
            db = SessionLocal()
            try:
                # Perform the scan
                await self.scan_once(db)
                
                # 2. Update storage stats (Heavy I/O/CPU)
                # We use a dedicated DB session for this thread-safe operation
                stats_db = SessionLocal()
                try:
                    await asyncio.to_thread(self.update_storage_stats, stats_db)
                finally:
                    stats_db.close()

                # Get the next scan interval
                scan_interval = self.get_scan_interval(db)

                logger.info(f"⏰ Next scan in {scan_interval} seconds")
                await asyncio.sleep(scan_interval)

            except Exception as e:
                logger.error(f"Periodic scanner error: {e}")
                # On error, wait a bit before retrying
                await asyncio.sleep(60)
            finally:
                db.close()

    async def stop(self):
        """Stop the periodic scanner"""
        logger.info("🛑 Stopping periodic scanner...")
        self.running = False

    async def trigger_scan_now(self) -> int:
        """Manually trigger a scan immediately, returns item count"""
        db = SessionLocal()
        try:
            return await self.scan_once(db)
        finally:
            db.close()


# Global scanner instance
periodic_scanner = None


def init_periodic_scanner(base_path: str):
    """Initialize the global periodic scanner"""
    global periodic_scanner
    periodic_scanner = PeriodicScanner(base_path)
    return periodic_scanner
