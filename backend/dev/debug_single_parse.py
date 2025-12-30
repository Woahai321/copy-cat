import re

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

def parse(filename):
    clean_name = filename.replace("__all__", "").strip("/\\")
    print(f"Cleaning: '{filename}' -> '{clean_name}'")
    
    for p in PATTERNS:
        match = re.search(p["regex"], clean_name, re.IGNORECASE)
        if match:
            print(f"Matched Pattern: {p['name']}")
            print(f"Groups: {match.groupdict()}")
            return
            
    print("NO MATCH FOUND")

if __name__ == "__main__":
    parse("__all__/I Am Andrew Tate 2024 1080p WEB-DL x264 BONE")
    parse("mnt/zurg")
    parse("__all__/The Match 2025 1080p NF WEB-DL Multi-Audio DDP5.1 H.264-TBMovies")
