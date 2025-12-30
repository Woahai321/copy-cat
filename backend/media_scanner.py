import os
import re
import logging
import time
from sqlalchemy.orm import Session
from datetime import datetime
from models import MediaItem
from typing import List, Dict, Optional, Set

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pre-compile Regex Patterns for maximum performance
PATTERNS = [
    {
        "name": "TV Multi-Season Sxx-Sxx",
        "regex": re.compile(r"(?P<title>.*?)\s*S(?P<season_start>\d{1,2})\s*-\s*S(?P<season_end>\d{1,2})", re.IGNORECASE),
        "type": "tv"
    },
    {
        "name": "TV Multi-Season Sxx-xx",
        "regex": re.compile(r"(?P<title>.*?)\s*S(?P<season_start>\d{1,2})\s*-\s*(?P<season_end>\d{1,2})(?!\d|E)", re.IGNORECASE),
        "type": "tv"
    },
    {
        "name": "TV Start SxxExx",
        "regex": re.compile(r"^(?P<title>)\s*S(?P<season>\d{1,2})E(?P<episode>\d{1,2})", re.IGNORECASE),
        "type": "tv"
    },
    {
        "name": "TV Episode Only",
        "regex": re.compile(r"(?P<title>.*?)[\.\s]+E(?P<episode>\d{1,2})(?!\d)", re.IGNORECASE),
        "type": "tv"
    },
    {
        "name": "TV Part X",
        "regex": re.compile(r"(?P<title>.*?)[\.\s]+Part\s+(?P<episode>\d{1,2})", re.IGNORECASE),
        "type": "tv"
    },
    {
        "name": "TV Standard SxxExx",
        "regex": re.compile(r"(?P<title>.*?)\s*-\s*S(?P<season>\d{1,2})E(?P<episode>\d{1,2})", re.IGNORECASE),
        "type": "tv"
    },
    {
        "name": "TV Alternative SxxExx",
        "regex": re.compile(r"(?P<title>.*?)[\.\s]+S(?P<season>\d{1,2})E(?P<episode>\d{1,2})", re.IGNORECASE),
        "type": "tv"
    },
    {
        "name": "TV Season Only Sxx",
        "regex": re.compile(r"(?P<title>.*?)[\.\s]+S(?P<season>\d{1,2})[\.\s]*(?!E\d)", re.IGNORECASE),
        "type": "tv"
    },
    {
        "name": "TV Season Words Range",
        "regex": re.compile(r"(?P<title>.*?)\s+Seasons?\s+(?P<season_start>\d{1,2})\s+(?:to|thru|through|-)\s+(?P<season_end>\d{1,2})", re.IGNORECASE),
        "type": "tv"
    },
    {
        "name": "TV Season Words Single",
        "regex": re.compile(r"(?P<title>.*?)\s+Seasons?\s+(?P<season>\d{1,2})(?!\d)", re.IGNORECASE),
        "type": "tv"
    },
    {
        "name": "Movie Year",
        "regex": re.compile(r"(?P<title>.*?)[\.\s\(](?P<year>19\d{2}|20\d{2})([\.\s\)]|$)", re.IGNORECASE),
        "type": "movie"
    }
]

# Common "Garbage" Prefixes to strip
GARBAGE_PREFIXES = [
    re.compile(r"www\.[a-z0-9\.-]+\.[a-z]{2,4}\s*-\s*", re.IGNORECASE),
    re.compile(r"\[.*?\]", re.IGNORECASE),
    re.compile(r"^\s*-\s*", re.IGNORECASE),
    re.compile(r"^(movies|movie|shows|show|series|tv|tv shows)[\/\\]", re.IGNORECASE),
]

METADATA_PATTERNS = {
    "resolution": re.compile(r"\b(2160p|1080p|720p|480p|576p|4K|UHD)\b", re.IGNORECASE),
    "source": re.compile(r"\b(BluRay|WEB-?DL|WEBRip|HDTV|DVD|BD|Remux)\b", re.IGNORECASE),
    "audio": re.compile(r"\b(TrueHD|Atmos|DTS-?HD|DTS|DD\+?|AAC|AC3|FLAC)\b", re.IGNORECASE),
    "hdr": re.compile(r"\b(HDR|DV|DoVi|10bit)\b", re.IGNORECASE),
    "codec": re.compile(r"\b(x265|x264|H\.?265|H\.?264|HEVC|AVC)\b", re.IGNORECASE),
    "edition": re.compile(r"\b(Director'?s\s?Cut|Extended(?:\s?Cut)?|Unrated|Remastered|Theatrical(?:\s?Cut)?|Final\s?Cut)\b", re.IGNORECASE),
    "streaming_service": re.compile(r"\b(NF|AMZN|HULU|DSNP|ATVP|HMAX|PCOK|RED|TUBI)\b", re.IGNORECASE),
    "audio_modifier": re.compile(r"\b(DUAL|MULTI|DUBBED)\b", re.IGNORECASE),
    "quality_modifier": re.compile(r"\b(PROPER|REPACK|REAL|RERIP)\b", re.IGNORECASE),
    "region": re.compile(r"\b(R[0-9]|PAL|NTSC)\b", re.IGNORECASE)
}

# Pre-compile combined edition cleaners
EDITION_CLEANER_END = re.compile(r"\s+\b(Extended|Remastered|Unrated|Director'?s\s?Cut|Final\s?Cut|Theatrical(?:\s?Cut)?)\b\s*$", re.IGNORECASE)
SEASON_CLEANER_END = re.compile(r"\s+Season\s?\d+\s*$", re.IGNORECASE)
YEAR_CLEANER_END = re.compile(r"\s+(?:\(|\[)?(19|20)\d{2}(?:\)|\])?\s*$", re.IGNORECASE)
NON_WORD_START_CLEANER = re.compile(r"^[^a-zA-Z0-9]+")

# Release Group Regex (End of string)
RELEASE_GROUP_REGEX = re.compile(r"-([A-Za-z0-9]+)(?:\[.*?\])?$", re.IGNORECASE)

def get_media_type_from_path(full_path: str) -> str:
    """
    Strictly determine media type from filepath.
    '/shows/' = tv, '/movies/' = movie
    """
    path_norm = full_path.lower().replace('\\', '/')
    if any(token in path_norm for token in ['/shows/', '/show/', '/series/', '/tv/', '/tv shows/']):
        return 'tv'
    if any(token in path_norm for token in ['/movies/', '/movie/']):
        return 'movie'
    return 'unknown'

def clean_title(title: str) -> str:
    """High-speed title cleaning."""
    cleaned = title
    for p in GARBAGE_PREFIXES:
        cleaned = p.sub("", cleaned).strip()
    
    cleaned = cleaned.replace('.', ' ').replace('_', ' ').strip()
    
    # Strip known suffixes
    cleaned = EDITION_CLEANER_END.sub("", cleaned).strip()
    cleaned = SEASON_CLEANER_END.sub("", cleaned).strip()
    cleaned = YEAR_CLEANER_END.sub("", cleaned).strip()
    
    # Strip common metadata tokens
    for p in [METADATA_PATTERNS["resolution"], METADATA_PATTERNS["source"], METADATA_PATTERNS["audio"], METADATA_PATTERNS["hdr"], METADATA_PATTERNS["codec"]]:
        cleaned = p.sub("", cleaned).strip()

    cleaned = NON_WORD_START_CLEANER.sub("", cleaned)
    return cleaned.strip()

def extract_metadata(filename: str) -> dict:
    meta = {}
    for key, pattern in METADATA_PATTERNS.items():
        matches = pattern.findall(filename)
        if matches:
            clean_matches = list(set([m.replace(".", "").replace("-", "").upper() for m in matches]))
            meta[key] = clean_matches
    return meta

def get_path_size(path: str) -> int:
    """Calculate size of file or directory recursively."""
    try:
        if os.path.isfile(path):
            return os.path.getsize(path)
        total = 0
        for root, _, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    if os.path.exists(fp):
                        total += os.path.getsize(fp)
                except: pass
        return total
    except:
        return 0

class MediaScanner:
    def __init__(self, db: Session, base_path: str):
        self.db = db
        self.base_path = base_path
        self.existing_items: Dict[str, str] = {} # full_path -> media_type

    def _load_existing_paths(self):
        """Loads all existing full_paths into memory for O(1) lookups."""
        logger.info("Loading existing media items into memory cache...")
        start = time.time()
        # Only fetch path and media_type to save memory
        results = self.db.query(MediaItem.full_path, MediaItem.media_type).all()
        self.existing_items = {r[0]: r[1] for r in results}
        logger.info(f"Loaded {len(self.existing_items)} items into memory in {time.time() - start:.2f}s")

    def scan_directory(self) -> int:
        # Retry logic for base path (e.g. valid rclone mount check)
        max_retries = 10
        retry_delay = 30 # seconds
        
        for attempt in range(max_retries + 1):
            if os.path.exists(self.base_path):
                break
            
            if attempt < max_retries:
                logger.warning(f"Base path {self.base_path} not found. Retrying in {retry_delay}s (Attempt {attempt+1}/{max_retries})...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Base path does not exist after {max_retries} retries: {self.base_path}")
                return 0

        # Load existing paths for blazing fast checks
        self._load_existing_paths()

        logger.info(f"Starting scoped recursive scan of directory: {self.base_path}")
        total_processed = 0
        added_count = 0
        skipped_non_ascii = 0
        BATCH_SIZE = 500
        
        # 1. Identify Target Media Folders at the ROOT
        target_folders = []
        try:
            with os.scandir(self.base_path) as entries:
                for entry in entries:
                    if not entry.is_dir(): continue
                    name_lower = entry.name.lower()
                    if name_lower in ["movies", "movie", "shows", "show", "tv", "series", "tv shows"]:
                        target_folders.append((entry.path, "movie" if "movie" in name_lower else "tv"))
        except Exception as e:
            logger.error(f"Failed to list root directory: {e}")
            return 0

        if not target_folders:
            logger.warning(f"No 'movies' or 'shows' folders found in {self.base_path}. Scanning nothing.")
            return 0

        logger.info(f"Identified target folders: {[os.path.basename(f[0]) for f in target_folders]}")

        # 2. Run Recursive Walk only on Target Folders
        for target_path, force_type in target_folders:
            logger.info(f"Recursively scanning {force_type} directory: {target_path}")
            
            for root, dirs, files in os.walk(target_path):
                # Optimization: Skip dot-directories and directories with non-ASCII characters
                dirs[:] = [d for d in dirs if not d.startswith('.') and not self._contains_non_ascii(d)]
                
                # Process files in current root
                for filename in files:
                    if filename.startswith('.'): continue
                    
                    # Skip files with non-ASCII characters (Russian, Chinese, Japanese, Korean, Indian)
                    if self._contains_non_ascii(filename):
                        skipped_non_ascii += 1
                        if skipped_non_ascii <= 5:  # Log first 5, then just count
                            logger.debug(f"Skipping file with non-ASCII characters: {filename}")
                        continue
                    
                    # Check extension to avoid scanning non-media
                    if not any(filename.lower().endswith(ext) for ext in ['.mkv', '.mp4', '.avi', '.ts', '.mov']):
                        continue
                    
                    full_path = os.path.join(root, filename)
                    
                    # 1. Faster Check: Is it already in our memory cache?
                    if full_path in self.existing_items:
                        # Check if media_type needs update
                        if self.existing_items[full_path] != force_type:
                            logger.info(f"Updating media_type for {filename}: {self.existing_items[full_path]} -> {force_type}")
                            item = self.db.query(MediaItem).filter(MediaItem.full_path == full_path).first()
                            if item:
                                item.media_type = force_type
                                item.updated_at = datetime.utcnow()
                        total_processed += 1
                        continue

                    try:
                        # CRITICAL: Always pass force_type to ensure path-based type is used
                        parsed = self.parse_filename(filename, force_type)
                        if parsed:
                            # Fallback: If title is empty/short, use parent folder name
                            if not parsed.get("title") or len(parsed["title"]) < 2:
                                parent_name = os.path.basename(root)
                                # Sanity check: if parent is "Season X", go up one more?
                                # Ideally yes, but let's stick to direct parent for now or cleaner approach.
                                # Actually, if parent is "Season 1", we want grandparent.
                                if "season" in parent_name.lower() and len(parent_name) < 15:
                                    parent_name = os.path.basename(os.path.dirname(root))
                                parsed["title"] = clean_title(parent_name) # Ensure title is clean

                            # Ensure media_type matches force_type (path-based)
                            parsed["media_type"] = force_type
                            
                            # 2. Get mtime
                            try:
                                mtime = datetime.fromtimestamp(os.path.getmtime(full_path))
                            except:
                                mtime = datetime.utcnow()
                            
                            self.create_media_item(full_path, parsed, mtime, get_path_size(full_path))
                            added_count += 1
                            total_processed += 1
                            
                            if added_count % BATCH_SIZE == 0:
                                self._safe_commit()
                                logger.info(f"Progress: {total_processed} items checked, {added_count} new items added.")
                    except Exception as item_err:
                        logger.warning(f"Error processing item '{filename}': {item_err}")
                        self.db.rollback()
                        continue
                
                # Also process the FOLDERS themselves (for folders named as titles)
                for dirname in dirs:
                    # Skip directories with non-ASCII characters (Russian, Chinese, Japanese, Korean, Indian)
                    if self._contains_non_ascii(dirname):
                        skipped_non_ascii += 1
                        if skipped_non_ascii <= 5:  # Log first 5, then just count
                            logger.debug(f"Skipping directory with non-ASCII characters: {dirname}")
                        continue
                        
                    full_path = os.path.join(root, dirname)
                    if full_path in self.existing_items:
                        # Check if media_type needs update
                        if self.existing_items[full_path] != force_type:
                            logger.info(f"Updating media_type for directory {dirname}: {self.existing_items[full_path]} -> {force_type}")
                            item = self.db.query(MediaItem).filter(MediaItem.full_path == full_path).first()
                            if item:
                                item.media_type = force_type
                                item.updated_at = datetime.utcnow()
                        continue
                    
                    # Since we are already inside a media folder, we are more lenient
                    try:
                        # CRITICAL: Always pass force_type to ensure path-based type is used
                        parsed = self.parse_filename(dirname, force_type)
                        if parsed:
                            # Fallback: If title is empty/short, use parent folder name
                            if not parsed.get("title") or len(parsed["title"]) < 2:
                                parsed["title"] = os.path.basename(root)
                                
                            # Ensure media_type matches force_type (path-based)
                            parsed["media_type"] = force_type
                            
                            try:
                                mtime = datetime.fromtimestamp(os.path.getmtime(full_path))
                            except:
                                mtime = datetime.utcnow()
                                
                            self.create_media_item(full_path, parsed, mtime, get_path_size(full_path))
                            added_count += 1
                            total_processed += 1
                    except:
                        pass

        self._safe_commit()
        logger.info(f"Scan complete. Total processed items: {total_processed}, New: {added_count}, Skipped (non-ASCII): {skipped_non_ascii}")
        if skipped_non_ascii > 0:
            logger.info(f"Skipped {skipped_non_ascii} files/directories with non-ASCII characters (Russian, Chinese, Japanese, Korean, Indian)")
        return total_processed

    def _safe_commit(self):
        """Helper to commit with retries."""
        from database import SessionLocal
        for attempt in range(3):
            try:
                self.db.commit()
                return
            except Exception as e:
                logger.error(f"Database commit attempt {attempt+1} failed: {e}")
                self.db.rollback()
                if "disk I/O error" in str(e).lower() and attempt < 2:
                    time.sleep(1)
                    self.db = SessionLocal() 
                else:
                    raise

    def _contains_non_ascii(self, text: str) -> bool:
        """
        Check if text contains non-ASCII characters that we want to skip.
        Specifically: Russian, Chinese, Japanese, Korean, Indian (Devanagari) characters.
        """
        # Unicode ranges for characters we want to skip:
        # Russian (Cyrillic): U+0400-U+04FF
        # Chinese (CJK Unified Ideographs): U+4E00-U+9FFF
        # Japanese (Hiragana): U+3040-U+309F, (Katakana): U+30A0-U+30FF
        # Korean (Hangul): U+AC00-U+D7AF
        # Indian (Devanagari): U+0900-U+097F
        
        for char in text:
            code = ord(char)
            # Skip if outside ASCII and in problematic ranges
            if code > 127:
                # Cyrillic (Russian)
                if 0x0400 <= code <= 0x04FF:
                    return True
                # CJK Unified Ideographs (Chinese)
                if 0x4E00 <= code <= 0x9FFF:
                    return True
                # Hiragana (Japanese)
                if 0x3040 <= code <= 0x309F:
                    return True
                # Katakana (Japanese)
                if 0x30A0 <= code <= 0x30FF:
                    return True
                # Hangul (Korean)
                if 0xAC00 <= code <= 0xD7AF:
                    return True
                # Devanagari (Indian)
                if 0x0900 <= code <= 0x097F:
                    return True
        return False

    def parse_filename(self, filename: str, force_type: str = None) -> Optional[Dict]:
        """High-speed filename parsing."""
        # Skip files with non-ASCII characters (Russian, Chinese, Japanese, Korean, Indian)
        if self._contains_non_ascii(filename):
            logger.debug(f"Skipping file with non-ASCII characters: {filename}")
            return None
        
        # Strip common trash
        clean_name = filename.replace("__all__", "").strip("/\\")
        
        for p in PATTERNS:
            match = p["regex"].search(clean_name)
            if match:
                data = match.groupdict()
                raw_title = data.get("title", "")
                final_title = clean_title(raw_title)
                
                # Allow short/empty titles if we have season/episode info (will fallback to parent folder)
                has_markers = data.get("season") or data.get("episode")
                if (not final_title or len(final_title) < 2) and not has_markers:
                    continue
                
                # CRITICAL: force_type (from filepath) ALWAYS takes precedence
                # If force_type is provided (from path like /shows or /movies), use it
                # Otherwise fall back to pattern type
                media_type = force_type if force_type else p["type"]
                    
                parsed = {
                    "original": filename,
                    "title": final_title,
                    "year": int(data.get("year")) if data.get("year") else None,
                    "media_type": media_type,
                    "season": int(data.get("season")) if data.get("season") else None,
                    "episode": int(data.get("episode")) if data.get("episode") else None
                }

                # Handle Multi-Season Ranges
                if data.get("season_start") and data.get("season_end"):
                    parsed["season"] = int(data.get("season_start"))
                    parsed["season_end"] = int(data.get("season_end"))
                    parsed["is_multi_season"] = True
                    parsed["season_range"] = f"{parsed['season']}-{parsed['season_end']}"
                
                # Handle Season Packs (S01 but no info on episodes)
                if parsed.get("season") and parsed.get("episode") is None and not parsed.get("is_multi_season"):
                    parsed["is_season_pack"] = True
                
                # Extract tags sparingly
                tags = extract_metadata(clean_name)
                parsed.update(tags)
                parsed["is_remux"] = "REMUX" in tags.get("source", []) or "REMUX" in clean_name.upper()
                
                # Extract Release Group (from original filename end)
                # Remove extension first
                # Extract Release Group (from original filename end)
                # Remove extension first
                stem = os.path.splitext(filename)[0]
                rg_match = RELEASE_GROUP_REGEX.search(stem)
                if rg_match:
                    group = rg_match.group(1)
                    # Simple filter to avoid false positives like 'H264' or '1080p' if regex matched them
                    if len(group) > 2 and group.upper() not in ["H264", "X264", "HEVC", "1080P", "720P"]:
                         parsed["release_group"] = group

                return parsed
        
        return None

    def create_media_item(self, full_path: str, meta: Dict, mtime: datetime, size_bytes: int = 0):
        """
        Creates a new record (Update is handled by logic elsewhere or later).
        CRITICAL: media_type is determined by filepath and must never be changed.
        """
        import json
        
        # CRITICAL: Always derive media_type from path for database storage
        meta["media_type"] = get_media_type_from_path(full_path)
        
        source_meta_json = json.dumps(meta)
        
        new_item = MediaItem(
            full_path=full_path,
            title=meta["title"],
            year=meta["year"],
            media_type=meta["media_type"],  # Path-based type, never changed by enrichment
            source_metadata=source_meta_json,
            created_at=mtime,
            updated_at=datetime.utcnow(),
            size_bytes=size_bytes
        )
        self.db.add(new_item)

