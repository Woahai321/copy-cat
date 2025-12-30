
import sqlite3
import os
import sys
import logging
from media_scanner import MediaScanner
from unittest.mock import MagicMock

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("GapAnalyzer")

def get_db_connection(db_path):
    if not os.path.exists(db_path):
        logger.error(f"Database not found: {db_path}")
        return None
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to {db_path}: {e}")
        return None

def analyze_db(db_path, label, scanner):
    conn = get_db_connection(db_path)
    if not conn:
        return

    logger.info(f"\n--- Analyzing {label} ({db_path}) ---")
    
    try:
        cursor = conn.cursor()
        # Fetch all items that look like TV shows based on path
        cursor.execute("SELECT full_path FROM media_items WHERE full_path LIKE '%/shows/%' OR full_path LIKE '%/tv/%'")
        rows = cursor.fetchall()
        
        logger.info(f"Found {len(rows)} potential TV items.")
        
        failed_count = 0
        passed_count = 0
        
        for row in rows:
            full_path = row['full_path']
            filename = os.path.basename(full_path)
            
            # Skip if it's a directory? The scanner handles both, but let's assume we want leaf nodes usually.
            # But wait, original code scans files.
            
            # Run scanner logic
            parsed = scanner.parse_filename(filename, force_type="tv")
            
            if not parsed:
                logger.warning(f"❌ FAILED: {filename}")
                failed_count += 1
                with open("gap_report.txt", "a", encoding="utf-8") as f:
                    f.write(f"FAILED: {filename}\n")
            elif not parsed.get('season') and not parsed.get('is_season_pack') and not parsed.get('is_multi_season'):
                 # It parsed, but maybe missed the season info?
                 logger.warning(f"⚠️  PARTIAL: {filename} -> {parsed}")
                 failed_count += 1
                 with open("gap_report.txt", "a", encoding="utf-8") as f:
                    f.write(f"PARTIAL: {filename} -> {parsed}\n")
            else:
                passed_count += 1
                
        logger.info(f"Results for {label}: {passed_count} Passed, {failed_count} Failed/Partial")

    except Exception as e:
        logger.error(f"Error analyzing {label}: {e}")
    finally:
        conn.close()

def main():
    # Initialize scanner (mocking DB session as we only need regex logic)
    scanner = MediaScanner(MagicMock(), "")
    
    # Define DB paths
    old_db = "data/oldcopypaste.db"
    new_db = "data/copypaste.db"
    
    # Check if files exist relative to CWD
    if not os.path.exists(old_db) and os.path.exists("oldcopypaste.db"):
        old_db = "oldcopypaste.db"
        
    if not os.path.exists(new_db) and os.path.exists("copypaste.db"):
         new_db = "copypaste.db"

    analyze_db(old_db, "OLD DB", scanner)
    analyze_db(new_db, "NEW DB", scanner)

if __name__ == "__main__":
    main()
