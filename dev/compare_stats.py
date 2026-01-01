import re
import os
import sys

# ==========================================
# CONSTANTS & PATTERNS
# ==========================================

PATTERNS = [
    {"name": "TV Multi-Season Sxx-Sxx", "regex": re.compile(r"(?P<title>.*?)\s*S(?P<season_start>\d{1,2})\s*-\s*S(?P<season_end>\d{1,2})", re.IGNORECASE), "type": "tv"},
    {"name": "TV Multi-Season Sxx-xx", "regex": re.compile(r"(?P<title>.*?)\s*S(?P<season_start>\d{1,2})\s*-\s*(?P<season_end>\d{1,2})(?!\d|E)", re.IGNORECASE), "type": "tv"},
    {"name": "TV Start SxxExx", "regex": re.compile(r"^(?P<title>)\s*S(?P<season>\d{1,2})E(?P<episode>\d{1,2})", re.IGNORECASE), "type": "tv"},
    {"name": "TV Episode Only", "regex": re.compile(r"(?P<title>.*?)[\.\s]+E(?P<episode>\d{1,2})(?!\d)", re.IGNORECASE), "type": "tv"},
    {"name": "TV Part X", "regex": re.compile(r"(?P<title>.*?)[\.\s]+Part\s+(?P<episode>\d{1,2})", re.IGNORECASE), "type": "tv"},
    {"name": "TV Standard SxxExx", "regex": re.compile(r"(?P<title>.*?)\s*-\s*S(?P<season>\d{1,2})E(?P<episode>\d{1,2})", re.IGNORECASE), "type": "tv"},
    {"name": "TV Alternative SxxExx", "regex": re.compile(r"(?P<title>.*?)[\.\s]+S(?P<season>\d{1,2})E(?P<episode>\d{1,2})", re.IGNORECASE), "type": "tv"},
    {"name": "TV Season Only Sxx", "regex": re.compile(r"(?P<title>.*?)[\.\s]+S(?P<season>\d{1,2})[\.\s]*(?!E\d)", re.IGNORECASE), "type": "tv"},
    {"name": "TV Season Words Range", "regex": re.compile(r"(?P<title>.*?)\s+Seasons?\s+(?P<season_start>\d{1,2})\s+(?:to|thru|through|-)\s+(?P<season_end>\d{1,2})", re.IGNORECASE), "type": "tv"},
    {"name": "TV Season Words Single", "regex": re.compile(r"(?P<title>.*?)\s+Seasons?\s+(?P<season>\d{1,2})(?!\d)", re.IGNORECASE), "type": "tv"},
    {"name": "Movie Year", "regex": re.compile(r"(?P<title>.*?)[\.\s\(](?P<year>19\d{2}|20\d{2})([\.\s\)]|$)", re.IGNORECASE), "type": "movie"}
]

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
}

EDITION_CLEANER_END = re.compile(r"\s+\b(Extended|Remastered|Unrated|Director'?s\s?Cut|Final\s?Cut|Theatrical(?:\s?Cut)?)\b\s*$", re.IGNORECASE)
SEASON_CLEANER_END = re.compile(r"\s+Season\s?\d+\s*$", re.IGNORECASE)
YEAR_CLEANER_END = re.compile(r"\s+(?:\(|\[)?(19|20)\d{2}(?:\)|\])?\s*$", re.IGNORECASE)
NON_WORD_START_CLEANER = re.compile(r"^[^a-zA-Z0-9]+")

def clean_title(title: str) -> str:
    cleaned = title
    for p in GARBAGE_PREFIXES:
        cleaned = p.sub("", cleaned).strip()
    cleaned = cleaned.replace('.', ' ').replace('_', ' ').strip()
    cleaned = EDITION_CLEANER_END.sub("", cleaned).strip()
    cleaned = SEASON_CLEANER_END.sub("", cleaned).strip()
    cleaned = YEAR_CLEANER_END.sub("", cleaned).strip()
    for p in METADATA_PATTERNS.values():
        cleaned = p.sub("", cleaned).strip()
    cleaned = NON_WORD_START_CLEANER.sub("", cleaned)
    return cleaned.strip()

def _contains_non_ascii(text: str) -> bool:
    for char in text:
        if ord(char) > 127: return True
    return False

# ==========================================
# PARSING LOGIC
# ==========================================

def parse_strict(filename):
    if _contains_non_ascii(filename): return None
    clean_name = filename.replace("__all__", "").strip("/\\")
    for p in PATTERNS:
        match = p["regex"].search(clean_name)
        if match:
            data = match.groupdict()
            final_title = clean_title(data.get("title", ""))
            has_markers = data.get("season") or data.get("episode")
            if (not final_title or len(final_title) < 2) and not has_markers:
                continue
            return True
    return False

def parse_fallback(filename, force_type):
    if _contains_non_ascii(filename): return None
    clean_name = filename.replace("__all__", "").strip("/\\")
    
    # Check Patterns First
    for p in PATTERNS:
        match = p["regex"].search(clean_name)
        if match:
            data = match.groupdict()
            final_title = clean_title(data.get("title", ""))
            has_markers = data.get("season") or data.get("episode")
            if (not final_title or len(final_title) < 2) and not has_markers:
                continue
            return True
            
    # Generic Fallback
    final_title = clean_title(clean_name)
    if final_title and len(final_title) > 0:
        return True
    return False

# ==========================================
# EXTRACTION
# ==========================================

def extract_folders(filepath):
    targets = {"movies": [], "shows": []}
    current_context = None
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line_clean = line.strip()
            if line_clean.endswith(" movies"):
                current_context = "movies"
                continue
            elif line_clean.endswith(" shows"):
                current_context = "shows"
                continue
            elif " __all__" in line_clean:
                current_context = None
                
            if current_context:
                match = re.search(r"^([│\s]+)(├── |└── )(.+)", line)
                if match:
                    prefix_len = len(match.group(1))
                    # Basic Heuristic: Approx 4 chars per level. 
                    # "├── movies" has 0 padding. Children have 1 padding block.
                    # We check if prefix length is reasonably small (Depth 1) 
                    if prefix_len <= 8: 
                        targets[current_context].append(match.group(3).strip())
    return targets

def main():
    if not os.path.exists("../export.txt"):
        print("export.txt not found")
        return
        
    data = extract_folders("../export.txt")
    
    m_total = len(data["movies"])
    s_total = len(data["shows"])
    
    # Strict Analysis
    m_strict = sum(1 for m in data["movies"] if parse_strict(m))
    s_strict = sum(1 for s in data["shows"] if parse_strict(s))
    
    # Fallback Analysis
    m_new = sum(1 for m in data["movies"] if parse_fallback(m, "movie"))
    s_new = sum(1 for s in data["shows"] if parse_fallback(s, "tv"))
    
    print(f"Movies: Total {m_total}")
    print(f"  Strict: {m_strict} matches ({m_strict/m_total*100:.1f}%)")
    print(f"  New:    {m_new} matches ({m_new/m_total*100:.1f}%)")
    print(f"  -->     +{m_new - m_strict} recovered")
    
    print(f"\nShows:  Total {s_total}")
    print(f"  Strict: {s_strict} matches ({s_strict/s_total*100:.1f}%)")
    print(f"  New:    {s_new} matches ({s_new/s_total*100:.1f}%)")
    print(f"  -->     +{s_new - s_strict} recovered")

if __name__ == "__main__":
    main()
