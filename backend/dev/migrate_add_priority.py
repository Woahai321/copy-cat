#!/usr/bin/env python3
"""Migration to add priority column to copy_jobs table."""
import sqlite3
import os

def migrate():
    DATABASE_DIR = os.getenv("DATABASE_DIR", "/data")
    DB_PATH = f"{DATABASE_DIR}/copypaste.db"
    
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Skipping migration.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(copy_jobs)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'priority' not in columns:
        print("Adding priority column to copy_jobs table...")
        cursor.execute("ALTER TABLE copy_jobs ADD COLUMN priority INTEGER DEFAULT 1")
        conn.commit()
        print("Migration completed successfully.")
    else:
        print("Priority column already exists. Skipping.")
    
    conn.close()

if __name__ == "__main__":
    migrate()

