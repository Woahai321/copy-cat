import re
import os

# Original "Old" logic (simulated)
def old_clean_title(title):
    return title.replace('.', ' ').replace('_', ' ').strip()

# New Logic
GARBAGE_PREFIXES = [
    r"www\.[a-z0-9\.-]+\.[a-z]{2,4}\s*-\s*",
    r"\[.*?\]",
    r"^\s*-\s*",
    r"^(movies|shows|series|tv)[\/\\]",
]
def new_clean_title(title):
    cleaned = title
    for p in GARBAGE_PREFIXES:
        cleaned = re.sub(p, "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = cleaned.replace('.', ' ').replace('_', ' ').strip()
    cleaned = re.sub(r"^[^a-zA-Z0-9]+", "", cleaned)
    return cleaned.strip()

def main():
    input_file = r"c:\Users\aidan\Downloads\newcopypaste\copypaste\zurg_folders.txt"
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    dropped_examples = []
    
    for line in lines:
        line = line.strip()
        if not line: continue
        line = line.replace("__all__", "").strip("/\\")

        # Simulate a match where title was just "movies/" or "shows/"
        # Ideally we'd run full regex, but let's test the hypothesis:
        # If title matches "movies/..." and cleaning makes it empty.
        
        # Checking if it starts with garbage
        is_garbage = False
        for p in GARBAGE_PREFIXES:
            if re.match(p, line, re.IGNORECASE):
                # If the line IS just the prefix + maybe extension?
                # or if removing prefix leaves nothing.
                cleaned = re.sub(p, "", line, flags=re.IGNORECASE).strip()
                if len(cleaned) < 2:
                    is_garbage = True
                    dropped_examples.append(line)
                    if len(dropped_examples) > 10:
                        break
        
        if len(dropped_examples) > 10: break

    print("Dropped Items Examples:")
    for d in dropped_examples:
        print(f" - {d}")

if __name__ == "__main__":
    main()
