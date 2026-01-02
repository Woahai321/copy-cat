"""
Background worker for continuous metadata enrichment.
Processes media items in batches, prioritizing most recently added items.
"""
import asyncio
import logging
from sqlalchemy.orm import Session
from database import SessionLocal
from enrichment import enrich_media_items
from models import SystemSettings, MediaItem
from sqlalchemy import or_

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnrichmentWorker:
    """Continuous background worker for metadata enrichment"""
    
    def __init__(self):
        self.running = False
        self.task = None
        
    async def enrich_batch_by_type(self, db: Session, media_type: str, limit: int = 50) -> int:
        """
        Enrich a batch of items for a specific media type using concurrent processing.
        Returns count of items processed.
        """
        from enrichment import enrich_single_item
        from trakt_client import TraktClient
        from security_utils import decrypt_value
        
        # Get Trakt Client ID
        setting = db.query(SystemSettings).filter(SystemSettings.key == "trakt_client_id").first()
        if not setting:
            return 0
            
        trakt_key = decrypt_value(setting.value)
        client = TraktClient(trakt_key)
        
        # Find items needing enrichment for this specific type
        items = db.query(MediaItem).filter(
            MediaItem.media_type == media_type,
            or_(MediaItem.tmdb_id == None, MediaItem.poster_url == None),
            or_(MediaItem.enrichment_status == None, MediaItem.enrichment_status.in_(['pending', 'pending_retry'])),
            or_(MediaItem.enrichment_retry_count == None, MediaItem.enrichment_retry_count < 3)
        ).order_by(MediaItem.priority.desc(), MediaItem.created_at.desc()).limit(limit).all()
        
        if not items:
            return 0
        
        logger.info(f"Enriching {len(items)} {media_type} items concurrently...")
        
        # Concurrent processing with semaphore to limit parallel requests
        concurrency = 5  # Process 5 items in parallel to reduce DB load
        semaphore = asyncio.Semaphore(concurrency)
        success_count = 0
        
        async def process_with_limit(item):
            """Process single item with concurrency control"""
            nonlocal success_count
            async with semaphore:
                try:
                    success = await enrich_single_item(db, item, client)
                    if success:
                        success_count += 1
                    
                    # Rate limit per item - spread out requests
                    await asyncio.sleep(0.5) 
                    return success
                except Exception as e:
                    logger.error(f"Error enriching {item.title}: {e}")
                    item.enrichment_status = 'pending_retry'
                    return False
        
        # Process all items concurrently
        tasks = [process_with_limit(item) for item in items]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Commit all changes
        db.commit()
        
        return success_count
    
    async def start(self):
        """Start the continuous enrichment loop"""
        self.running = True
        logger.info("🚀 Enrichment worker started")
        
        while self.running:
            db = SessionLocal()
            try:
                # Process 50 movies
                movie_count = await self.enrich_batch_by_type(db, 'movie', limit=50)
                
                # Process 50 shows
                show_count = await self.enrich_batch_by_type(db, 'tv', limit=50)
                
                # Reporting
                total_done = db.query(MediaItem).filter(MediaItem.enrichment_status == 'success').count()
                total_pending = db.query(MediaItem).filter(
                    or_(MediaItem.enrichment_status == None, MediaItem.enrichment_status.in_(['pending', 'pending_retry']))
                ).count()
                total_failed = db.query(MediaItem).filter(MediaItem.enrichment_status == 'failed').count()
                
                logger.info(f"📊 ENRICHMENT REPORT: Success: {total_done} | Pending: {total_pending} | Failed: {total_failed}")
                
                if movie_count > 0 or show_count > 0:
                    # Continue immediately when there's more work
                    await asyncio.sleep(1) 
                else:
                    # Only delay when queue is empty
                    await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Enrichment worker error: {e}")
                await asyncio.sleep(30)  # Wait longer on error
            finally:
                db.close()
    
    async def stop(self):
        """Stop the enrichment worker"""
        logger.info("🛑 Stopping enrichment worker...")
        self.running = False


# Global worker instance
enrichment_worker = EnrichmentWorker()
