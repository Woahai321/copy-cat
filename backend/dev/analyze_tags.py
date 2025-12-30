import sqlite3
import json
import os
import re
from collections import Counter

DB_PATH = r"c:\Users\aidan\Downloads\SENDBACK\SENDBACK\data\oldcopypaste.db"

PATTERNS = {
    "Streaming": re.compile(r"\b(NF|AMZN|HULU|DSNP|ATVP|HMAX|PCOK|RED|TUBI)\b", re.IGNORECASE),
    "Quality Modifier": re.compile(r"\b(PROPER|REPACK|REAL|RERIP)\b", re.IGNORECASE),
    "Audio": re.compile(r"\b(DUAL|MULTI|DUBBED)\b", re.IGNORECASE),
    "Release Group": re.compile(r"-([A-Za-z0-9]+)(?:\[.*?\])?(?:\.[a-z]{3})?$", re.IGNORECASE)
}

def analyze_tags():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    counts = {k: Counter() for k in PATTERNS.keys()}

    try:
        cursor.execute("SELECT source_metadata FROM media_items WHERE source_metadata IS NOT NULL")
        
        row_count = 0
        while True:
            rows = cursor.fetchmany(1000)
            if not rows: break
            
            for row in rows:
                try:
                    if not row[0]: continue
                    meta = json.loads(row[0])
                    filename = meta.get('original', '')
                    if not filename: continue
                    
                    for cat, regex in PATTERNS.items():
                        matches = regex.findall(filename)
                        for m in matches:
                            if cat == "Release Group":
                                # Filter out common false positives for groups
                                if len(m) < 3 or m.lower() in ['mkv', 'mp4', 'avi', 'h264', 'x264']: continue
                            counts[cat][m.upper()] += 1
                            
                    row_count += 1
                except:
                    pass

        print(f"\n--- Analyzed {row_count} items ---\n")
        
        for cat, counter in counts.items():
            print(f"Top {cat}:")
            for tag, count in counter.most_common(10):
                print(f"  {tag}: {count}")
            print("")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    analyze_tags()
