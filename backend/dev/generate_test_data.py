import os
import random
import shutil

# Configuration
SOURCE_FILE = "../zurg_folders.txt"
TARGET_DIR = "../mock_zurg"
SAMPLE_SIZE = 50

def generate_folders():
    # 1. Setup Target
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
        print(f"Created target directory: {TARGET_DIR}")
    
    # 2. Read Source
    if not os.path.exists(SOURCE_FILE):
        print(f"Error: {SOURCE_FILE} not found.")
        return

    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    # 3. Filter and Sample (Strict Mode)
    # The user states the file has "movies/" and "shows/" explicitly.
    movies = [l for l in lines if l.startswith("movies/")]
    shows = [l for l in lines if l.startswith("shows/")]
    
    print(f"Found {len(movies)} movies and {len(shows)} shows in source file.")
    
    # Take samples
    movies_sample = random.sample(movies, min(len(movies), 25))
    shows_sample = random.sample(shows, min(len(shows), 25))
    
    samples = movies_sample + shows_sample

    print(f"Generating {len(samples)} folders in {TARGET_DIR}...")

    # 4. Create Folders
    created_count = 0
    for s in samples:
        # s is like "movies/Some Movie 2024..." or "shows/Some Show..."
        # We want to maintain that structure inside mock_zurg
        # e.g. mock_zurg/movies/Some Movie 2024...
        
        full_path = os.path.join(TARGET_DIR, s)
        
        # Normalize path separators for Windows
        full_path = str(full_path).replace("/", os.sep).replace("\\", os.sep)
        
        try:
            os.makedirs(full_path, exist_ok=True)
            created_count += 1
        except Exception as e:
            print(f"Failed to create {s}: {e}")

    print(f"Successfully created {created_count} test items.")
    print(f"Location: {os.path.abspath(TARGET_DIR)}")
    print("\nTo test the scanner, you can update ZURG_BASE in .env or main.py to point to this directory.")

if __name__ == "__main__":
    generate_folders()
