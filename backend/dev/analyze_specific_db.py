import sqlite3
import re
import json
import os

DB_PATH = r"c:\Users\aidan\Downloads\SENDBACK\SENDBACK\data\oldcopypaste.db"

def analyze_db():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if media_items table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='media_items'")
        if not cursor.fetchone():
            print("Table 'media_items' not found.")
            return

        print("Analyzing 'media_items' table...")
        
        # We want to see 'original' filenames that look like multi-season or full season packs
        # Patterns to look for: S01-S02, S01 Complete, Season 1, etc.
        
        cursor.execute("SELECT source_metadata FROM media_items")
        rows = cursor.fetchall()
        
        season_patterns = []
        range_patterns = []
        
        for row in rows:
            try:
                if not row[0]: continue
                meta = json.loads(row[0])
                original = meta.get('original', '')
                
                # Check for Range (S01-S05)
                if re.search(r'S\d+\s*-\s*S\d+', original, re.IGNORECASE):
                    range_patterns.append(original)
                
                # Check for "Season X" or "S01" without episode
                # Simple heuristic: matches S01 but not E01, or "Season 1"
                elif re.search(r'\bS\d+\b', original, re.IGNORECASE) and not re.search(r'\bE\d+\b', original, re.IGNORECASE):
                     season_patterns.append(original)
                     
            except json.JSONDecodeError:
                pass

        print(f"\n--- Found {len(range_patterns)} potential Multi-Season Ranges ---")
        for p in range_patterns[:20]:
            print(p)
            
        print(f"\n--- Found {len(season_patterns)} potential Full Season Packs ---")
        for p in season_patterns[:20]:
            print(p)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    analyze_db()
