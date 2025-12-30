import json
import re
import sys
import os

# Copy PATTERNS exactly from media_scanner.py as viewed
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
        "regex": r"(?P<title>.*?)[\\.\\s\\(](?P<year>19\d{2}|20\d{2})([\\.\\s\\)]|$)",
        "type": "movie"
    }
]

def parse_check(filename):
    clean_name = filename.replace("__all__", "").strip("/\\")
    
    for p in PATTERNS:
        match = re.search(p["regex"], clean_name, re.IGNORECASE)
        if match:
             return p["name"], match.groupdict()
    return None, None

def main():
    json_path = r"c:\Users\aidan\Downloads\newcopypaste\copypaste\zurg_parsed.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    failures = [d for d in data if d.get("media_type") == "movie" and d.get("year") is None]
    print(f"Found {len(failures)} mysterious 'Movie No Year' items in JSON.")
    
    print("\nAttempting to re-parse sample with CURRENT patterns:\n")
    
    for item in failures[:10]:
        original = item['original']
        print(f"Original: {original}")
        print(f"JSON Result: Title='{item['title']}', Year={item['year']}")
        
        name, groups = parse_check(original)
        if name:
            print(f"CURRENT PARSE: Matched '{name}'")
            print(f"Groups: {groups}")
        else:
            print(f"CURRENT PARSE: NO MATCH (Item would be dropped)")
        print("-" * 50)

if __name__ == "__main__":
    main()
