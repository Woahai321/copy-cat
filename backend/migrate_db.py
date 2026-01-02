import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    # Use /data directory for database (or DATABASE_DIR env var)
    DATABASE_DIR = os.getenv("DATABASE_DIR", "/data")
    db_path = os.path.join(DATABASE_DIR, "copypaste.db")
    if not os.path.exists(db_path):
        # Fallback for local development
        db_path = os.path.join(os.path.dirname(__file__), "..", "data", "copypaste.db")
        db_path = os.path.abspath(db_path)

    if not os.path.exists(db_path):
        logger.warning(f"Database not found at {db_path}. Skipping migration.")
        return

    logger.info(f"Running migration on {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Migration 1: Check if size_bytes exists in media_items
        cursor.execute("PRAGMA table_info(media_items)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "size_bytes" not in columns:
            logger.info("Adding 'size_bytes' column to 'media_items' table...")
            cursor.execute("ALTER TABLE media_items ADD COLUMN size_bytes BIGINTEGER DEFAULT 0")
            conn.commit()
            logger.info("Successfully added 'size_bytes' column.")
        else:
            logger.info("'size_bytes' column already exists.")

        # Migration 2: Check if enrichment_retry_count exists in media_items
        if "enrichment_retry_count" not in columns:
            logger.info("Adding 'enrichment_retry_count' column to 'media_items' table...")
            cursor.execute("ALTER TABLE media_items ADD COLUMN enrichment_retry_count INTEGER DEFAULT 0")
            conn.commit()
            logger.info("Successfully added 'enrichment_retry_count' column.")
        else:
            logger.info("'enrichment_retry_count' column already exists.")

        # Migration 3: Check if priority exists in media_items (New for prioritization)
        if "priority" not in columns:
            logger.info("Adding 'priority' column to 'media_items' table...")
            cursor.execute("ALTER TABLE media_items ADD COLUMN priority INTEGER DEFAULT 0")
            conn.commit()
            logger.info("Successfully added 'priority' column to media_items.")
        else:
             logger.info("'priority' column already exists in media_items.")

        # Migration 3: Check if priority exists in copy_jobs
        cursor.execute("PRAGMA table_info(copy_jobs)")
        copy_jobs_columns = [row[1] for row in cursor.fetchall()]
        
        if "priority" not in copy_jobs_columns:
            logger.info("Adding 'priority' column to 'copy_jobs' table...")
            cursor.execute("ALTER TABLE copy_jobs ADD COLUMN priority INTEGER DEFAULT 1")
            conn.commit()
            logger.info("Successfully added 'priority' column.")
        else:
            logger.info("'priority' column already exists.")

        # Migration 4: Check if is_admin exists in users
        cursor.execute("PRAGMA table_info(users)")
        users_columns = [row[1] for row in cursor.fetchall()]
        
        if "is_admin" not in users_columns:
            logger.info("Adding 'is_admin' column to 'users' table...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL")
            # Set the first user (admin) as admin
            cursor.execute("UPDATE users SET is_admin = 1 WHERE username = 'admin'")
            conn.commit()
            logger.info("Successfully added 'is_admin' column.")
        else:
            logger.info("'is_admin' column already exists.")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
