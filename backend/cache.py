"""
Backend caching for directory listings to improve performance with slow FUSE mounts.
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
import threading

class DirectoryCache:
    def __init__(self, ttl_seconds: int = 300):  # 5 minutes default
        self._cache: Dict[str, tuple[Dict, datetime]] = {}
        self._lock = threading.Lock()
        self.ttl = timedelta(seconds=ttl_seconds)
    
    def get(self, key: str) -> Optional[Dict]:
        """Get cached directory listing if not expired."""
        with self._lock:
            if key in self._cache:
                data, timestamp = self._cache[key]
                if datetime.now() - timestamp < self.ttl:
                    return data
                else:
                    # Expired, remove it
                    del self._cache[key]
        return None
    
    def set(self, key: str, data: Dict):
        """Cache directory listing with timestamp."""
        with self._lock:
            self._cache[key] = (data, datetime.now())
    
    def clear(self):
        """Clear all cached data."""
        with self._lock:
            self._cache.clear()
    
    def remove(self, key: str):
        """Remove specific cache entry."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]

# Global cache instance
_dir_cache = DirectoryCache(ttl_seconds=300)  # 5 minutes

def get_cache():
    return _dir_cache

