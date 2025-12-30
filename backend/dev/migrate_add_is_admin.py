"""
Migration script to add is_admin column to users table
Run this once to update the existing database schema
"""
import sqlite3
import os

# Use /data directory in project root for persistent database
DATABASE_DIR = os.getenv("DATABASE_DIR", "/data")
os.makedirs(DATABASE_DIR, exist_ok=True)
DB_PATH = os.path.join(DATABASE_DIR, "copypaste.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'is_admin' not in columns:
            print("Adding is_admin column...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL")
            
            # Set the first user (admin) as admin
            cursor.execute("UPDATE users SET is_admin = 1 WHERE username = 'admin'")
            
            conn.commit()
            print("Migration completed successfully!")
            print("Admin user has been granted admin privileges.")
        else:
            print("Column is_admin already exists. No migration needed.")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()

