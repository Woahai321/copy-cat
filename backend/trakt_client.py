import aiohttp
import requests
import logging
import urllib.parse
import asyncio
import time
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

TRAKT_API_URL = "https://api.trakt.tv"

class TraktClient:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.headers = {
            "Content-Type": "application/json",
            "trakt-api-version": "2",
            "trakt-api-key": self.client_id
        }

# Global Rate Limit State (Module Level)
# This ensures that ALL instances of TraktClient share the same rate limit status.
_GLOBAL_RATE_LIMIT_UNTIL = None
_GLOBAL_CONSECUTIVE_LIMITS = 0

class TraktClient:
    def __init__(self, client_id=None):
        self.client_id = client_id or os.getenv("TRAKT_CLIENT_ID")
        self.base_url = "https://api.trakt.tv"
        self.headers = {
            "Content-Type": "application/json",
            "trakt-api-version": "2",
            "trakt-api-key": self.client_id
        }
        self.last_request_time = 0
        self.min_delay = 0.5 # 2 requests per second max
        
    @property
    def rate_limit_until(self):
        return _GLOBAL_RATE_LIMIT_UNTIL
        
    @rate_limit_until.setter
    def rate_limit_until(self, value):
        global _GLOBAL_RATE_LIMIT_UNTIL
        _GLOBAL_RATE_LIMIT_UNTIL = value
    
    async def _handle_rate_limit(self, response: aiohttp.ClientResponse):
        """
        Handle rate limit responses (429) and log limit headers.
        Updates GLOBAL rate limit state.
        """
        global _GLOBAL_RATE_LIMIT_UNTIL, _GLOBAL_CONSECUTIVE_LIMITS
        
        # Log X-Ratelimit headers if present
        remaining = response.headers.get('X-Ratelimit-Remaining')
        limit = response.headers.get('X-Ratelimit-Limit')
        reset = response.headers.get('X-Ratelimit-Reset')
        
        if remaining is not None:
            logger.debug(f"📊 Trakt Rate Limit: {remaining}/{limit} remaining (Resets in {reset}s)")

        if response.status == 429:
            _GLOBAL_CONSECUTIVE_LIMITS += 1
            
            # Check for Retry-After header
            retry_after = response.headers.get('Retry-After')
            if retry_after:
                try:
                    wait_seconds = int(retry_after)
                except:
                    wait_seconds = 60
            else:
                wait_seconds = min(10 * (3 ** (_GLOBAL_CONSECUTIVE_LIMITS - 1)), 300)
            
            _GLOBAL_RATE_LIMIT_UNTIL = datetime.utcnow() + timedelta(seconds=wait_seconds + 2) # Buffer
            logger.warning(f"⚠️ Trakt rate limit hit! Waiting {wait_seconds}s (Retry-After: {retry_after})")
            return True
        elif response.status == 200:
            # Only reset consecutive count on success if we were previously limited? 
            # Actually, standard logic is to reset on success.
            _GLOBAL_CONSECUTIVE_LIMITS = 0
            # Do NOT reset _GLOBAL_RATE_LIMIT_UNTIL here, wait for time to pass naturally?
            # No, if we get a 200, we are good.
            _GLOBAL_RATE_LIMIT_UNTIL = None
        return False
    
    async def _wait_for_throttle(self):
        """Proactively throttle requests to stay under limit using GLOBAL state"""
        global _GLOBAL_RATE_LIMIT_UNTIL
        
        # 1. Standard per-instance throttle (leaky bucket-ish)
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.min_delay:
            await asyncio.sleep(self.min_delay - elapsed)
        
        # 2. Check GLOBAL backoff
        if _GLOBAL_RATE_LIMIT_UNTIL and datetime.utcnow() < _GLOBAL_RATE_LIMIT_UNTIL:
            wait_time = (_GLOBAL_RATE_LIMIT_UNTIL - datetime.utcnow()).total_seconds()
            if wait_time > 0:
                logger.info(f"⏳ Global Trakt Backoff: Waiting {wait_time:.1f}s...")
                await asyncio.sleep(wait_time)
            
        self.last_request_time = time.time()
    
    async def _check_rate_limit(self):
        """Proactive throttle helper"""
        await self._wait_for_throttle()

    async def validate_api(self) -> bool:
        """
        Validates the API key by making a lightweight request.
        """
        async with aiohttp.ClientSession() as session:
            try:
                # 'countries' is a public lightweight endpoint, but we want to test auth if possible.
                # Actually, client ID is public. The best test is if we can fetch something.
                # Let's try to get trending movies (limit 1)
                url = f"{TRAKT_API_URL}/movies/trending?limit=1"
                async with session.get(url, headers=self.headers) as resp:
                    return resp.status == 200
            except Exception as e:
                logger.error(f"Trakt Validation Error: {e}")
                return False

    def _clean_query_title(self, title: str) -> str:
        """
        Cleans a filename/folder title by removing common releaser tags,
        websites, and brackets to improve Trakt search results.
        Example: 'www.DDHDTV.com】联结 Connection' -> '联结 Connection'
        """
        import re

        # 1. Remove anything inside brackets or after a right bracket 】
        title = re.sub(r'^[\[【].*?[\]】]', '', title)
        title = re.sub(r'^.*?[\】\]]', '', title)

        # 2. Remove common website prefixes
        title = re.sub(r'www\.[a-zA-Z0-9-]+\.[a-com]{2,4}', '', title, flags=re.IGNORECASE)
        title = re.sub(r'[a-zA-Z0-9-]+\.(com|net|org|tv|me)', '', title, flags=re.IGNORECASE)

        # 3. Clean up leading/trailing junk
        title = title.strip(' ._-【】[]()')

        # 4. If nothing left, return original (fallback)
        return title if title else title
    
    async def get_summary(self, media_type: str, trakt_id: int) -> Optional[Dict]:
        """
        Get full summary including images.
        """
        # Check if we're in a rate limit backoff period
        await self._check_rate_limit()
        
        async with aiohttp.ClientSession() as session:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Use the 'summary' endpoint with extended=full,images
                    endpoint = f"movies/{trakt_id}" if media_type == 'movie' else f"shows/{trakt_id}"
                    url = f"{TRAKT_API_URL}/{endpoint}"
                    params = {"extended": "full,images"}
                    
                    async with session.get(url, headers=self.headers, params=params, ssl=False) as resp:
                        # Handle rate limits
                        if await self._handle_rate_limit(resp):
                            continue  # Retry after waiting
                        
                        if resp.status == 200:
                            return await resp.json()
                except Exception as e:
                    logger.error(f"Trakt Summary Error (attempt {attempt+1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2)
        return None

    async def _search_first_match(self, endpoint: str, query_title: str, params: Dict, strict_match: bool = False) -> Optional[Dict]:
        """
        Searches Trakt.
        If strict_match is True, the result title must match query_title exactly (case-insensitive).
        This is used when we don't have a year to narrow it down.
        """
        # Check if we're in a rate limit backoff period
        await self._check_rate_limit()
        
        async with aiohttp.ClientSession() as session:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    url = f"{TRAKT_API_URL}/{endpoint}"
                    async with session.get(url, headers=self.headers, params=params) as resp:
                        # Handle rate limits
                        if await self._handle_rate_limit(resp):
                            continue  # Retry after waiting
                        
                        if resp.status == 200:
                            data = await resp.json()
                            if data and isinstance(data, list) and len(data) > 0:
                                
                                # Logic: If strict_match is required, iterate through results to find exact match
                                for candidate in data:
                                    media_key = "movie" if "movie" in candidate else "show"
                                    item = candidate.get(media_key)
                                    if not item: continue
                                    
                                    result_title = item.get("title")
                                    
                                    if strict_match:
                                        # Normalize both titles by removing all non-alphanumeric characters AND accents
                                        import re
                                        import unicodedata
                                        import difflib
                                        
                                        def normalize(t):
                                            t = unicodedata.normalize('NFKD', t).encode('ASCII', 'ignore').decode('utf-8')
                                            t = t.replace('&', 'and')
                                            return re.sub(r'[\W_]+', '', t).lower()
                                        
                                        norm_result = normalize(result_title)
                                        norm_query = normalize(query_title)
                                        
                                        # 1. Exact Match (Fastest)
                                        if norm_result == norm_query:
                                            pass # Match!
                                        
                                        # 2. Fuzzy Match (Difflib)
                                        # We allow a match if similarity is > 85%
                                        elif difflib.SequenceMatcher(None, norm_result, norm_query).ratio() > 0.85:
                                            logger.info(f"Fuzzy match accepted: '{query_title}' ~= '{result_title}'")
                                            pass # Match!
                                            
                                        # 3. Substring match (risky, but useful for "Title: Subtitle" cases)
                                        # Only if one title is significantly long to avoid "The" matching "The Movie"
                                        elif len(norm_query) > 10 and (norm_result in norm_query or norm_query in norm_result):
                                             logger.info(f"Substring match accepted: '{query_title}' contains/is contained by '{result_title}'")
                                             pass # Match!
                                             
                                        else:
                                            continue # Skip this result
                                    
                                    # Found a match
                                    return {
                                        "title": result_title,
                                        "year": item.get("year"),
                                        "tmdb_id": item.get("ids", {}).get("tmdb"),
                                        "imdb_id": item.get("ids", {}).get("imdb"),
                                        "trakt_id": item.get("ids", {}).get("trakt"),
                                        "media_type": media_key
                                    }
                                
                                logger.info(f"No match found for '{query_title}' (Strict: {strict_match})")
                                    
                except Exception as e:
                    logger.error(f"Trakt Search Error: {e}")
        return None

    async def search_movie(self, title: str, year: Optional[int] = None) -> Optional[Dict]:
        """Keep this for initial identification from folder name."""
        clean_title = self._clean_query_title(title)
        params = {"query": clean_title, "type": "movie", "extended": "full"}
        if year:
            params["years"] = str(year)
        
        # Enforce strict match if year is missing
        strict = (year is None)
        return await self._search_first_match("search/movie", clean_title, params, strict_match=strict)

    async def search_show(self, title: str) -> Optional[Dict]:
        """Keep this for initial identification."""
        clean_title = self._clean_query_title(title)
        params = {"query": clean_title, "type": "show", "extended": "full"}
        # Shows often don't have year in filename, but stricter matching is still good
        # However, for shows, often the folder title is 'Show Name', which is exact.
        # We'll enforce strict matching for safety.
        return await self._search_first_match("search/show", clean_title, params, strict_match=True)

    async def get_trakt_metadata(self, tmdb_id: Optional[int] = None, imdb_id: Optional[str] = None, media_type: str = "movie") -> Optional[Dict[str, Any]]:
        """
        Async method to fetch full metadata + images.
        """
        trakt_type = 'shows' if media_type == 'tv' or media_type == 'show' else 'movies'
        
        url = None
        async with aiohttp.ClientSession() as session:
            if imdb_id:
                url = f"{TRAKT_API_URL}/{trakt_type}/{imdb_id}"
            elif tmdb_id:
                try:
                    await self._wait_for_throttle()
                    search_url = f"{TRAKT_API_URL}/search/tmdb/{tmdb_id}?type={trakt_type[:-1]}"
                    async with session.get(search_url, headers=self.headers) as r:
                        if await self._handle_rate_limit(r):
                             return await self.get_trakt_metadata(tmdb_id, imdb_id, media_type)
                        
                        if r.status == 200:
                            res = await r.json()
                            if res:
                                 item = res[0].get(trakt_type[:-1])
                                 slug = item.get("ids", {}).get("slug")
                                 if slug:
                                     url = f"{TRAKT_API_URL}/{trakt_type}/{slug}"
                except:
                    pass
            
            if not url:
                return None
            
            try:
                await self._wait_for_throttle()
                params = {"extended": "full,images"}
                async with session.get(url, headers=self.headers, params=params) as resp:
                    if await self._handle_rate_limit(resp):
                         return await self.get_trakt_metadata(tmdb_id, imdb_id, media_type)
                    
                    if resp.status == 200:
                        data = await resp.json()
                        
                        # Image Proxy Logic
                        poster_url = None
                        images = data.get("images", {})
                        if images:
                            posters = images.get("poster", [])
                            if posters:
                                raw_url = posters[0]
                                if not raw_url.startswith("http"):
                                    raw_url = "https://" + raw_url
                                
                                encoded_url = urllib.parse.quote(raw_url)
                                poster_url = f"/api/images/proxy?url={encoded_url}"
                        
                        # Phase 1 & 2 Findings
                        genres = data.get("genres", [])
                        genre_string = None
                        if genres:
                            # Format as "Action, Adventure, Sci-Fi"
                            genre_string = ", ".join([g.title() for g in genres])
                            
                        # Extract TV Specifics
                        network = data.get("network")
                        aired_episodes = data.get("aired_episodes")
                        
                        return {
                            "title": data.get("title"),
                            "year": data.get("year"),
                            "overview": data.get("overview"),
                            "rating": data.get("rating"),
                            "genres": genre_string, # Now a formatted string!
                            "poster_url": poster_url,
                            "tmdb_id": data.get("ids", {}).get("tmdb"),
                            "imdb_id": data.get("ids", {}).get("imdb"),
                            # Validating unused fields
                            "certification": data.get("certification"),
                            "runtime": data.get("runtime"),
                            "tagline": data.get("tagline"),
                            "trailer_url": data.get("trailer"),
                            "homepage": data.get("homepage"),
                            "status": data.get("status"),
                            "network": network,
                            "aired_episodes": aired_episodes
                        }
            except Exception as e:
                logger.error(f"Trakt Metadata Fetch Error: {e}")
        
        return None
