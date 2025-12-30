import json
import sys

def find_items():
    with open(r"c:\Users\aidan\Downloads\newcopypaste\copypaste\zurg_parsed.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    queries = ["Red Queen"]
    
    print(f"Searching {len(data)} items...")
    
    for item in data:
        title = item.get('title', '').lower()
        original = item.get('original', '').lower()
        
        for q in queries:
            if q.lower() in title or q.lower() in original:
                print(f"MATCH [{q}]:")
                print(json.dumps(item, indent=2))
                print("-" * 50)

if __name__ == "__main__":
    find_items()
