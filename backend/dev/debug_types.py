from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database URL
DATABASE_URL = "sqlite:///./data/copypaste.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def debug_types():
    db = SessionLocal()
    try:
        # Get count of items by media_type
        result = db.execute(text("SELECT media_type, count(*) as count FROM media_items GROUP BY media_type"))
        print("\n--- Media Type Distribution ---")
        for row in result:
             print(f"Type: '{row[0]}' - Count: {row[1]}")
             
        # Sample items
        print("\n--- Sample Items ---")
        result = db.execute(text("SELECT id, title, media_type, full_path FROM media_items LIMIT 10"))
        for row in result:
            print(f"[{row[2]}] {row[1]} ({row[3]})")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_types()
