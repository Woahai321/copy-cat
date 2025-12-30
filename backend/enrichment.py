import logging
import asyncio
import time
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import MediaItem, SystemSettings, CachedImage
from media_scanner import get_media_type_from_path
from trakt_client import TraktClient
from security_utils import decrypt_value
from image_cache import save_cached_image
import requests
import imghdr
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def enrich_single_item(db: Session, item: MediaItem, client: TraktClient) -> bool:
    """
    Enrich a single media item with Trakt metadata.
    Returns True if successful, False otherwise.
    
    CRITICAL RULE: media_type is determined by filepath (/shows = tv, /movies = movie)
    and must NEVER be changed by enrichment. Only enrich metadata, never change type.
    """
    try:
        # Skip if already marked failed or exceeded retry limit
        if item.enrichment_status == 'failed' or (item.enrichment_retry_count or 0) >= 3:
            return False

        # CRITICAL: Always derive media_type from path for enrichment logic
        media_type = get_media_type_from_path(item.full_path)
        
        # --- OPTIMIZATION START ---
        # 1. Local Database Lookup
        # Check if we already have a SUCCESSFUL enrichment for this title/type
        existing_match = db.query(MediaItem).filter(
            MediaItem.title == item.title,
            MediaItem.media_type == media_type,
            MediaItem.enrichment_status == 'success',
            MediaItem.tmdb_id != None  # Ensure it has valuable data
        ).first()

        if existing_match:
            # We found a match! Reuse the metadata.
            logger.info(f"✨ Enrichment Optimization: Found existing metadata for '{item.title}' (from ID {existing_match.id})")
            
            # Copy Metadata
            item.tmdb_id = existing_match.tmdb_id
            item.imdb_id = existing_match.imdb_id
            item.overview = existing_match.overview
            item.rating = existing_match.rating
            item.genres = existing_match.genres
            item.certification = existing_match.certification
            item.runtime = existing_match.runtime
            item.tagline = existing_match.tagline
            item.year = existing_match.year # Trust the enriched year
            
            # Reuse Poster URL directly (it's already a proxied path or URL)
            item.poster_url = existing_match.poster_url
            item.poster_cached_at = existing_match.poster_cached_at
            
            item.enrichment_status = 'success'
            return True
        # --- OPTIMIZATION END ---
        
        result = None
        if media_type == 'movie':
            result = await client.search_movie(item.title, item.year)
        elif media_type == 'tv':
            result = await client.search_show(item.title)
            
        # No fallback type swapping - media_type is determined by filepath and must not be changed
        
        if result:
            # Update IDs
            item.tmdb_id = result.get('tmdb_id')
            item.imdb_id = result.get('imdb_id')
            
            logger.info(f"Matched '{item.title}' -> TraktID:{result.get('trakt_id')}")
            
            # B. Fetch Full Summary (Images & Metadata)
            trakt_id = result.get('trakt_id')
            if trakt_id:
                # Use path-derived media_type
                media_type = get_media_type_from_path(item.full_path)
                summary = await client.get_summary(media_type, trakt_id)
                if summary:
                    # IDs
                    ids = summary.get('ids', {})
                    item.tmdb_id = ids.get('tmdb')
                    item.imdb_id = ids.get('imdb')
                    
                    # Metadata Persistence
                    item.overview = summary.get('overview')
                    item.rating = summary.get('rating')
                    item.certification = summary.get('certification')
                    item.tagline = summary.get('tagline')
                    item.runtime = summary.get('runtime')
                    
                    # Persist Year if missing or updated
                    if summary.get('year'):
                        item.year = summary.get('year')
                    
                    # Genres
                    genres = summary.get('genres', [])
                    if genres:
                        item.genres = ",".join([g['name'] for g in genres if isinstance(g, dict)] if isinstance(genres, list) else [])
                    
                    # Images & Caching
                    images = summary.get('images', {})
                    poster = images.get('poster', {})
                    
                    poster_url = None
                    if isinstance(poster, dict):
                        poster_url = poster.get('full') or poster.get('medium')
                    elif isinstance(poster, list) and len(poster) > 0:
                        first = poster[0]
                        if isinstance(first, str): poster_url = first
                        elif isinstance(first, dict): poster_url = first.get('full') or first.get('medium')
                            
                    if poster_url:
                        item.poster_url = poster_url
                        
                        # Download & Cache Image (Async)
                        try:
                            if not poster_url.startswith('http'):
                                poster_url = f"https://{poster_url}"
                                item.poster_url = poster_url
                            
                            import aiohttp
                            async with aiohttp.ClientSession() as session:
                                logger.info(f"Downloading poster: {poster_url}")
                                async with session.get(poster_url, timeout=15) as img_resp:
                                    if img_resp.status == 200:
                                        img_data = await img_resp.read()
                                        mime = imghdr.what(None, img_data) or 'image/jpeg'
                                        if not mime.startswith('image/'): mime = f'image/{mime}'
                                        
                                        save_cached_image(
                                            db, 
                                            poster_url, 
                                            img_data, 
                                            mime_type=mime, 
                                            source='trakt'
                                        )
                                        item.poster_cached_at = datetime.utcnow()
                                        logger.info(f"Cached poster for {item.title}")
                                    else:
                                        logger.warning(f"Failed to download poster: {img_resp.status}")
                                        # Use pending_retry for transient image failures
                                        item.enrichment_status = 'pending_retry'
                                        return False
                        except Exception as e:
                            logger.error(f"Image download failed: {e}")
                            item.enrichment_status = 'pending_retry'
                            return False
                    
                    logger.info(f"Enriched '{item.title}' (Rating: {item.rating})")
            
            item.enrichment_status = 'success'
            return True
        else:
            logger.debug(f"Could not find match for '{item.title}'")
            item.enrichment_retry_count = (item.enrichment_retry_count or 0) + 1
            if item.enrichment_retry_count >= 3:
                item.enrichment_status = 'failed'
            else:
                item.enrichment_status = 'pending_retry'
            return False
            
    except Exception as e:
        logger.error(f"Error enriching {item.title}: {e}")
        item.enrichment_retry_count = (item.enrichment_retry_count or 0) + 1
        if item.enrichment_retry_count >= 3:
            item.enrichment_status = 'failed'
        else:
            item.enrichment_status = 'pending_retry'
        return False

async def enrich_media_items(db: Session, batch_size: int = 20):
    """
    Background task to find items without metadata and enrich them via Trakt.
    Processes a FIXED number of items per call to avoid blocking the scanner for too long.
    """
    logger.info("Starting enrichment cycle (Limited batch)...")
    
    # 1. Get Trakt Client
    setting = db.query(SystemSettings).filter(SystemSettings.key == "trakt_client_id").first()
    if not setting:
        logger.warning("No Trakt Client ID configured. Skipping enrichment.")
        return
        
    trakt_key = decrypt_value(setting.value)
    client = TraktClient(trakt_key)
    
    # 2. Find items needing enrichment
    items = db.query(MediaItem).filter(
        or_(MediaItem.tmdb_id == None, MediaItem.poster_url == None),
        or_(MediaItem.enrichment_status == None, MediaItem.enrichment_status.in_(['pending', 'pending_retry']))
    ).order_by(MediaItem.created_at.desc()).limit(batch_size).all()
    
    if not items:
        logger.info("No items requiring enrichment found.")
        return
        
    logger.info(f"Enriching batch of {len(items)} items...")
    
    total_updated = 0
    for item in items:
        # Check if we should stop (if global backoff is too long we might want to return early)
        if client.rate_limit_until and datetime.utcnow() < client.rate_limit_until:
             logger.warning("Stoping enrichment batch: Trakt Global Backoff active.")
             break

        success = await enrich_single_item(db, item, client)
        if success:
            total_updated += 1
            
        # Commit every item for immediate feedback in UI
        db.commit()
            
        # Conservative rate limit - 2 per second max
        await asyncio.sleep(0.5)
    
    logger.info(f"Enrichment cycle complete. Updated: {total_updated} items.")
