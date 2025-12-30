import re
import os

# Define the path to the sample file
SAMPLE_FILE = "../zurg_folders.txt"

# Regex Patterns to Test
# 1. Standard Movie: Title Year ...
# 2. Dot-Separated Movie: Title.Year...
# 3. Standard TV: Title SxxExx ...
# 4. Dot-Separated TV: Title.SxxExx...
# 5. Year in Parentheses: Title (Year)...

PATTERNS = [
    # TV Show Patterns (Prioritize these as they are more specific)
    {
        "name": "TV Standard SxxExx",
        "regex": r"(?P<title>.*?)[\.\s]S(?P<season>\d{1,2})E(?P<episode>\d{1,2})",
        "type": "tv"
    },
    {
        "name": "TV Season Only Sxx",
        "regex": r"(?P<title>.*?)[\.\s]S(?P<season>\d{1,2})[\.\s](?!E\d)", # Negative lookahead to ensure it's not SxxExx
        "type": "tv"
    },
    
    # Movie Patterns
    {
        "name": "Movie Year (Standard/Dot)",
        "regex": r"(?P<title>.*?)[\.\s\(](?P<year>19\d{2}|20\d{2})[\.\s\)]",
        "type": "movie"
    }
]

def load_samples():
    if not os.path.exists(SAMPLE_FILE):
        print(f"Error: {SAMPLE_FILE} not found.")
        return []
    with open(SAMPLE_FILE, "r", encoding="utf-8") as f:
        # distinct lines, ignore __all__ parents if possible, but the file seems to be full paths or names
        return [line.strip() for line in f if line.strip() and not line.startswith("total")]

def clean_title(title):
    return title.replace('.', ' ').replace('_', ' ').strip()

def run_test():
    samples = load_samples()
    print(f"Loaded {len(samples)} samples.")
    
    matched_count = 0
    unmatched = []
    
    results = []

    for sample in samples:
        # Skip the root folder lines if any
        if sample == "/mnt/zurg" or sample == "__all__":
            continue
            
        # Remove prefix if present (e.g. __all__/)
        filename = sample.replace("__all__/", "")
        
        is_matched = False
        
        for p in PATTERNS:
            match = re.search(p["regex"], filename, re.IGNORECASE)
            if match:
                data = match.groupdict()
                title = clean_title(data.get("title", ""))
                
                # Refinement: invalid title check
                if not title or len(title) < 2:
                    continue

                res = {
                    "original": filename,
                    "type": p["type"],
                    "pattern": p["name"],
                    "title": title,
                    "year": data.get("year"),
                    "season": data.get("season"),
                    "episode": data.get("episode")
                }
                results.append(res)
                matched_count += 1
                is_matched = True
                break
        
        if not is_matched:
            unmatched.append(filename)

    # Report
    print("="*50)
    print(f"Total Processed: {len(results) + len(unmatched)}")
    print(f"Matched: {matched_count}")
    print(f"Unmatched: {len(unmatched)}")
    print(f"Success Rate: {matched_count / (len(results) + len(unmatched)) * 100:.2f}%")
    print("="*50)
    
    print("\n--- First 20 Matches ---")
    for r in results[:20]:
        meta = f"Year: {r.get('year')}" if r['type'] == 'movie' else f"S{r.get('season')}E{r.get('episode')}"
        print(f"[{r['type'].upper()}] {r['title']} ({meta}) matched by {r['pattern']}")

    print("\n--- First 20 Unmatched ---")
    for u in unmatched[:20]:
        print(u)

if __name__ == "__main__":
    run_test()
