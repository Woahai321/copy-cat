import os
import re

# Regex Patterns (Proven 95% Success Rate) -> copied from media_scanner.py
PATTERNS = [
    {
        "name": "TV Standard SxxExx",
        "regex": r"(?P<title>.*?)[\.\s]S(?P<season>\d{1,2})E(?P<episode>\d{1,2})",
        "type": "tv"
    },
    {
        "name": "TV Season Only Sxx",
        "regex": r"(?P<title>.*?)[\.\s]S(?P<season>\d{1,2})[\.\s](?!E\d)",
        "type": "tv"
    },
    {
        "name": "Movie Year",
        "regex": r"(?P<title>.*?)[\.\s\(](?P<year>19\d{2}|20\d{2})([\.\s\)]|$)",
        "type": "movie"
    }
]

# Common "Garbage" Prefixes to strip
GARBAGE_PREFIXES = [
    r"www\.[a-z0-9\.-]+\.[a-z]{2,4}\s*-\s*",  # www.UIndex.org - 
    r"\[.*?\]",                                # [Source] or [Group] at start
    r"^\s*-\s*",                               # Leading hyphens
    r"^(movies|shows|series|tv)[\/\\]",        # Folder prefixes like movies/ or shows/
]

METADATA_PATTERNS = {
    "resolution": r"\b(2160p|1080p|720p|480p|576p|4K|UHD)\b",
    "source": r"\b(BluRay|WEB-?DL|WEBRip|HDTV|DVD|BD|Remux)\b",
    "audio": r"\b(TrueHD|Atmos|DTS-?HD|DTS|DD\+?|AAC|AC3|FLAC)\b",
    "hdr": r"\b(HDR|DV|DoVi|10bit)\b",
    "codec": r"\b(x265|x264|H\.?265|H\.?264|HEVC|AVC)\b",
    "edition": r"\b(Director'?s\s?Cut|Extended(?:\s?Cut)?|Unrated|Remastered|Theatrical(?:\s?Cut)?|Final\s?Cut)\b"
}

def clean_title(title: str) -> str:
    """Cleans title by removing garbage prefixes, dots/underscores, editions and stripping whitespace."""
    # 1. Strip known garbage regexes from the START of the string
    cleaned = title
    for p in GARBAGE_PREFIXES:
        cleaned = re.sub(p, "", cleaned, flags=re.IGNORECASE).strip()
    
    # 2. Standard cleanup
    cleaned = cleaned.replace('.', ' ').replace('_', ' ').strip()
    
    # 3. Strip Edition from END of title (if cleaner regex left it there)
    # Using the defined metadata pattern for edition
    edition_pattern = METADATA_PATTERNS["edition"]
    # Remove edition if it appears at the end of the string
    cleaned = re.sub(f"{edition_pattern}$", "", cleaned, flags=re.IGNORECASE).strip()
    
    # 3b. Also strip just "EXTENDED" or "REMASTERED" if they are lingering at the end
    # (The pattern above covers matching words, but let's be safe for spaces)
    cleaned = re.sub(r"\s+\b(Extended|Remastered|Unrated)\b\s*$", "", cleaned, flags=re.IGNORECASE).strip()

    # 3c. Strip "Season N" suffix if present (common in folders)
    cleaned = re.sub(r"\s+Season\s?\d+\s*$", "", cleaned, flags=re.IGNORECASE).strip()
    
    # 3d. Strip Year at end if present (e.g. "Title 2019" or "Title (2019)")
    cleaned = re.sub(r"\s+(?:\(|\[)?(19|20)\d{2}(?:\)|\])?\s*$", "", cleaned).strip()

    # NEW: Strip common metadata tokens if they accidentally made it into the title
    for key in ["resolution", "source", "audio", "hdr", "codec"]:
        p = METADATA_PATTERNS.get(key)
        if p:
             cleaned = re.sub(p, "", cleaned, flags=re.IGNORECASE).strip()

    # 4. Final sanity check: if it starts with hyphen or non-word char (after removing garbage)
    cleaned = re.sub(r"^[^a-zA-Z0-9]+", "", cleaned)
    
    return cleaned.strip()

def extract_metadata(filename: str) -> dict:
    meta = {}
    for key, pattern in METADATA_PATTERNS.items():
        matches = re.findall(pattern, filename, re.IGNORECASE)
        if matches:
            # unique checks + clean up (e.g. WEB-DL vs WEBDL)
            clean_matches = list(set([m.replace(".", "").replace("-", "").upper() for m in matches]))
            meta[key] = clean_matches
    return meta

def parse_filename(filename: str):
    """Applies regex patterns to extract metadata."""
    # Pre-clean known prefixes like '__all__' if they appear in filenames
    clean_name = filename.replace("__all__", "").strip("/\\")
    
    parsed = None
    
    for p in PATTERNS:
        match = re.search(p["regex"], clean_name, re.IGNORECASE)
        if match:
            data = match.groupdict()
            raw_title = data.get("title", "")
            final_title = clean_title(raw_title)
            
            # Minimum title length check
            if not final_title or len(final_title) < 2:
                continue
                
            parsed = {
                "original": filename.strip(),
                "title": final_title,
                "year": int(data.get("year")) if data.get("year") else None,
                "media_type": p["type"],
                "season": int(data.get("season")) if data.get("season") else None,
                "episode": int(data.get("episode")) if data.get("episode") else None
            }
            break
    
    if parsed:
        # Extract rich metadata from the ORIGINAL filename (keeps context like year/resolution)
        # We search the whole string for these tags
        tags = extract_metadata(clean_name)
        parsed.update(tags)
        # Add "REMUX" boolean/tag explicitly if present (common request)
        parsed["is_remux"] = "REMUX" in tags.get("source", []) or "REMUX" in clean_name.upper()
        
    return parsed

def main():
    input_file = r"c:\Users\aidan\Downloads\newcopypaste\copypaste\zurg_folders.txt"
    output_file = r"c:\Users\aidan\Downloads\newcopypaste\copypaste\zurg_parsed.json"
    
    print(f"Reading from {input_file}")
    
    parsed_count = 0
    total_count = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        total_count = len(lines)
        results = []
        
        for line in lines:
            line = line.strip()
            if not line: continue
            
            parsed = parse_filename(line)
            if parsed:
                parsed_count += 1
                results.append(parsed)
        
        # Write results to JSON
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
                
        print(f"Done! Processed {total_count} lines. Parsed {parsed_count} items.")
        print(f"Results written to {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
