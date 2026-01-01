import re
import os
import sys

# ==========================================
# 1. REPLICATION OF BACKEND LOGIC
# ==========================================

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
    
    for p in [METADATA_PATTERNS["resolution"], METADATA_PATTERNS["source"], METADATA_PATTERNS["audio"], METADATA_PATTERNS["hdr"], METADATA_PATTERNS["codec"]]:
        cleaned = p.sub("", cleaned).strip()

    cleaned = NON_WORD_START_CLEANER.sub("", cleaned)
    return cleaned.strip()

def _contains_non_ascii(text: str) -> bool:
    for char in text:
        code = ord(char)
        if code > 127:
            if 0x0400 <= code <= 0x04FF: return True # Cyrillic
            if 0x4E00 <= code <= 0x9FFF: return True # CJK
            if 0x3040 <= code <= 0x309F: return True # Hiragana
            if 0x30A0 <= code <= 0x30FF: return True # Katakana
            if 0xAC00 <= code <= 0xD7AF: return True # Hangul
            if 0x0900 <= code <= 0x097F: return True # Devanagari
    return False

def parse_filename(filename: str, force_type: str = None):
    if _contains_non_ascii(filename):
        return None
    
    clean_name = filename.replace("__all__", "").strip("/\\")
    
    for p in PATTERNS:
        match = p["regex"].search(clean_name)
        if match:
            data = match.groupdict()
            raw_title = data.get("title", "")
            final_title = clean_title(raw_title)
            
            has_markers = data.get("season") or data.get("episode")
            if (not final_title or len(final_title) < 2) and not has_markers:
                continue
            
            # Simulated match data
            return {
                "original": filename,
                "title": final_title,
                "pattern": p["name"]
            }
    
    # GENERIC FALLBACK (The Fix)
    if force_type:
        final_title = clean_title(clean_name)
        if len(final_title) > 0:
             return {
                "original": filename,
                "title": final_title,
                "media_type": force_type,
                "pattern": "Generic Folder Fallback"
            }

    return None

# ==========================================
# 2. EXPORT PARSER
# ==========================================

def extract_folders_from_export(filepath):
    """
    Parses 'tree' output to find direct children of 'movies' and 'shows'.
    Refined specifically for the user's export.txt structure.
    """
    targets = {"movies": [], "shows": []}
    
    current_context = None # 'movies' or 'shows'
    
    # Indentation analysis based on user snippet:
    # 1: /mnt/zurg
    # ...
    # 107576:├── movies
    # 107577:│   ├── 10 Cloverfield Lane...
    
    # '├── ' is the marker for an item at current level
    # '│   ' is the indentation for subsequent levels.
    
    # We are looking for lines that start with:
    # "├── movies" or "└── movies" -> Set context to movies
    # "├── shows" or "└── shows" -> Set context to shows
    
    # Children of movies/shows will look like:
    # "│   ├── Movie Name"
    # or
    # "    ├── Movie Name" (if last child)
    
    # Actually, simpler:
    # We find the line with "movies".
    # Then we assume subsequent lines with +1 indentation are the movies.
    # Until indentation drops back or changes.
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        line_clean = line.strip()
        
        # Detect Context Switch
        # Note: tree output uses special chars. We'll search by substring.
        if line_clean.endswith(" movies"):
            current_context = "movies"
            continue
        elif line_clean.endswith(" shows"):
            current_context = "shows"
            continue
        elif " __all__" in line_clean:
            current_context = None # Reset if we see other value
            
        if current_context:
            # Check if this line is a direct child (folder) of the context
            # We assume the export is well structured.
            # Tree output:
            # ├── movies
            # │   ├── Movie A    <-- We want this
            # │   │   ├── file.mkv
            # │   ├── Movie B    <-- We want this
            
            # The pattern for a direct child of 'movies' (which is at depth X)
            # is typically "│   ├── Name" or "│   └── Name"
            # Files inside Movie A would be "│   │   ├── file"
            
            # Heuristic:
            # We want headers that are folders.
            # In the snippet provided:
            # 3: │   ├── 1000 Men...
            # 4: │   │   └── ...mkv
            
            # Line 3 is a folder (top level in __all__).
            # Line 4 is a file (deeper).
            
            # Wait, the snippet showed:
            # 1: /mnt/zurg
            # 2: ├── __all__
            # 3: │   ├── 1000 Men and Me...
            # This means '1000 Men...' is a child of '__all__'.
            
            # The 'movies' and 'shows' are likely siblings of '__all__' or children of it?
            # User grep output for `├── movies` suggests it is at the same level as `__all__`?
            # Or inside it?
            # Line 2: `├── __all__`
            # Line 107576: `├── movies`
            # They have same indentation pattern prefix structure?
            # If `├── ` starts line 2 and line 107576, they are siblings.
            
            # So children of `movies` should have pattern `│   ├── ` or `    ├── ` (if movies was last).
            # But children of children (files) will have `│   │   ├── `.
            
            # We can count the number of `│` or spaces to determine depth.
            
            # Let's count depth by special chars.
            # `├── ` counts as depth indicator too?
            # "│   " is one level (4 chars/bytes sequence).
            
            # Simple approach: substring check.
            # Valid item: `│   ├── NAME` or `    ├── NAME` or `│   └── NAME` or `    └── NAME`
            
            # Sub-item (file inside): `│   │   ├── NAME` (double indent)
            
            # In the user snippet for `__all__`:
            # 3: │   ├── 1000 ... (Folder)
            # 4: │   │   └── ... (File)
            
            # So if we are in 'movies' block:
            # We only want items with exactly ONE level of indentation deeper than 'movies'.
            
            # If 'movies' line was `├── movies`, then `movies` is at Depth 1.
            # Children are at Depth 2.
            # Grandchildren at Depth 3.
            
            # We only want Depth 2.
            
            # Let's just blindly grab lines that look like a folder name and filter out the clearly deep ones.
            # Or rely on the fact that the user wants to test "all folders".
            
            # Refined Heuristic:
            # Extract the name.
            # If the next line is indented FURTHER, this line was a folder.
            # If the next line is SAME or LESS indent, this line was a leaf (file or empty folder).
            # We basically want "Top Level Folders in Movies/Shows".
            
            # Let's clean the line to just the name.
            # Remove `│`, ` `, `├`, `─`, `└`.
            
            parts = line.split("── ", 1)
            if len(parts) < 2: continue # Not a tree item line
            
            name = parts[1].strip()
            
            # Determine depth by length of prefix
            prefix = parts[0]
            # In typical tree:
            # Root: 0
            # L1: ├── (4 chars visible, bytes vary)
            # L2: │   ├── (8 chars)
            
            # We want items that are exactly one step deeper than the `movies` line.
            # Since we don't know the exact `movies` line prefix without reading it again or storing state...
            # We can assume `movies` is a root category here.
            
            # Let's just collect ALL names found in the block, and then filter/deduplicate?
            # No, that's 200k lines.
            
            # Let's try to identify the standard "Movie Folder" depth.
            # Ideally, `└── movies` or `├── movies`.
            # Children have `│   ├── ` or `    ├── `. (One padding block + marker).
            # Grandchildren have `│   │   ├── ` (Two padding blocks + marker).
            
            # We count `│` and space blocks?
            # Let's just use a regex for the line prefix.
            # Child of L1: `(│   |    )(├── |└── )`
            # Child of L2: `(│   |    ){2}(├── |└── )`
            
            match = re.search(r"^([│\s]+)(├── |└── )(.+)", line)
            if match:
                folder_depth = len(match.group(1)) // 4 # Rough guess, usually 4 chars per level
                name = match.group(3).strip()
                
                # We assume correct depth is... 1 level deep?
                # Actually, `├── movies` has 0 padding (just marker).
                # So children have 1 padding block.
                # Grandchildren have 2 padding blocks.
                
                # So we want items with len(group 1) == 4 (bytes/chars depending on decoding).
                # Let's just check if it contains exactly ONE `│   ` or `    ` block.
                
                if current_context == "movies" or current_context == "shows":
                    # We store it.
                    # To verify it's a folder (and not a file sitting at root of 'movies'), 
                    # usually structure is movies/Folder/File.
                    # But if we have movies/File.mkv, we might get a false positive.
                    # But the user says "folders".
                    
                    # Key differentiation: Valid folders usually force a new indent level for their content.
                    # But 'tree' handles this visually.
                    
                    # Let's just add items that appear to be depth 1 relative to context.
                     # "│   " is `\u2502\u00a0\u00a0\u0020` or similar.
                     
                     # Check if prefix length is "Short" (Level 1) vs "Long" (Level 2).
                     # Level 1 prefix usually ~4 chars.
                     # Level 2 prefix usually ~8 chars.
                     
                     raw_prefix = match.group(1)
                     # print(f"DEBUG: {len(raw_prefix)} - {name}")
                     
                     if len(raw_prefix) <= 4: # Is Level 1
                         targets[current_context].append(name)

    return targets

# ==========================================
# 3. ANALYSIS
# ==========================================

def analyze():
    print("Reading export.txt...")
    path = "export.txt"
    if not os.path.exists(path):
        # Fallback to absolute path from previous context if running in dev folder
        path = "../export.txt"
    
    if not os.path.exists(path):
        print(f"Error: {path} not found.")
        return

    data = extract_folders_from_export(path)
    
    print(f"\nFound {len(data['movies'])} Movie folders and {len(data['shows'])} Show folders.")
    
    # Analyze Movies
    print("\n--- MOVIES ANALYSIS ---")
    failures = []
    
    for folder in data["movies"]:
        result = parse_filename(folder, force_type="movie")
        if not result:
            failures.append(folder)
            
    success_count = len(data["movies"]) - len(failures)
    print(f"Total: {len(data['movies'])}")
    print(f"Matched: {success_count}")
    print(f"Failed: {len(failures)}")
    
    if failures:
        print("\n--- FAILED MOVIE SAMPLES (First 20) ---")
        for f in failures[:20]:
            print(f"[FAIL] {f}")
            
    # Analyze Shows
    print("\n--- SHOWS ANALYSIS ---")
    s_failures = []
    for folder in data["shows"]:
        result = parse_filename(folder, force_type="tv")
        if not result:
            s_failures.append(folder)
            
    s_success_count = len(data["shows"]) - len(s_failures)
    print(f"Total: {len(data['shows'])}")
    print(f"Matched: {s_success_count}")
    print(f"Failed: {len(s_failures)}")
    
    if s_failures:
        print("\n--- FAILED SHOW SAMPLES (First 20) ---")
        for f in s_failures[:20]:
            print(f"[FAIL] {f}")

if __name__ == "__main__":
    analyze()
