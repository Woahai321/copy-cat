#!/usr/bin/env python3
"""
Migration to add enrichment_retry_count column to media_items table.
"""
import sqlite3
import os

def migrate():
    # Use /data directory for database
    DATABASE_DIR = os.getenv("DATABASE_DIR", "/data")
    DB_PATH = f"{DATABASE_DIR}/copypaste.db"

    if not os.path.exists(DB_PATH):
        print("Database not found, skipping migration")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(media_items)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'enrichment_retry_count' not in columns:
            print("Adding enrichment_retry_count column...")
            cursor.execute("ALTER TABLE media_items ADD COLUMN enrichment_retry_count INTEGER DEFAULT 0")
            conn.commit()
            print("Migration completed successfully")
        else:
            print("Column already exists, skipping migration")

    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
