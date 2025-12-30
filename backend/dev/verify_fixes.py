import json
import asyncio
import sys
import logging
from trakt_client import TraktClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def verify_fixes():
    if len(sys.argv) < 2:
        print("Usage: python verify_specific_items.py <CLIENT_ID>")
        return
        
    client_id = sys.argv[1]
    client = TraktClient(client_id=client_id)
    
    # Load Parsed Data
    with open(r"c:\Users\aidan\Downloads\newcopypaste\copypaste\zurg_parsed.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Validating these specific tricky items
    targets = [
        "Red Queen",           # Was failing due to (2024)
        "McDonald and Dodds",  # Was failing due to & vs and
        "The Bay",             # Was failing due to 2019 suffix
        "Wednesday",           # Was failing due to (2022) Season 1 suffix
        "90 Day Fiance",       # Was failing due to accents
        "Jurassic World"       # Was failing due to punctuation
    ]
    
    print(f"\nVerifying {len(targets)} specific edge cases...\n")
    print(f"{'ORIGINAL INPUT (Partial)':<40} | {'PARSED TITLE':<25} | {'RESULT':<10} | {'DETAILS'}")
    print("-" * 100)

    for target in targets:
        # Find item in JSON
        # We look for one that matches the target "roughly" in original filename to ensure we test the specific file
        # or just match the Parsed Title if that's what we expect
        
        candidates = [i for i in data if target.lower() in i['original'].lower()]
        if not candidates:
            print(f"Could not find test candidate for '{target}' in JSON.")
            continue
            
        # Pick the most complex one (longest original string usually implies more garbage to clean)
        item = max(candidates, key=lambda x: len(x['original']))
        
        title = item['title']
        media_type = item['media_type']
        year = item['year']
        
        # Search Trakt
        if media_type == 'movie':
            result = await client.search_movie(title, year)
        else:
            result = await client.search_show(title)
            
        # Fallback
        if not result:
            if media_type == 'movie':
                result = await client.search_show(title)
            else:
                result = await client.search_movie(title, year)
        
        status = "FOUND" if result else "MISSING"
        details = result['title'] if result else "N/A"
        if result and result.get('year'): details += f" ({result['year']})"
        
        print(f"{item['original'][:40]:<40} | {title[:25]:<25} | {status:<10} | {details}")
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(verify_fixes())
