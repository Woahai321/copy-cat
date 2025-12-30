import json
import asyncio
import random
import logging
import os
from trakt_client import TraktClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import sys

async def test_trakt_integration():
    # 1. Ask for Client ID
    if len(sys.argv) > 1:
        client_id = sys.argv[1]
    else:
        client_id = input("Enter Trakt Client ID: ").strip()
        
    if not client_id:
        print("Client ID is required.")
        return

    client = TraktClient(client_id=client_id)
    
    # 2. Load Parsed JSON
    json_path = r"c:\Users\aidan\Downloads\newcopypaste\copypaste\zurg_parsed.json"
    if not os.path.exists(json_path):
        print("zurg_parsed.json not found. Run regex parser first.")
        return
        
    with open(json_path, "r", encoding="utf-8") as f:
        all_items = json.load(f)
        
    # 3. Select Samples
    # User requested 25 Movies and 25 TV Shows
    movies = [i for i in all_items if i['media_type'] == 'movie']
    shows = [i for i in all_items if i['media_type'] == 'tv']
    
    samples = []
    
    # Sample Movies
    if len(movies) < 25:
        print(f"Sampling ALL {len(movies)} movies.")
        samples.extend(movies)
    else:
        print(f"Sampling 25 random movies (out of {len(movies)}).")
        samples.extend(random.sample(movies, 25))
        
    # Sample Shows
    if len(shows) < 25:
        print(f"Sampling ALL {len(shows)} shows.")
        samples.extend(shows)
    else:
        print(f"Sampling 25 random shows (out of {len(shows)}).")
        samples.extend(random.sample(shows, 25))
        
    random.shuffle(samples) # Mix them up for the output
    
    print(f"\n{'-'*140}")
    print(f"{'TYPE':<8} | {'TMDB_ID':<8} | {'TITLE (Cleaned)':<35} | {'RESULT':<10} | {'DETAILS'}")
    print(f"{'-'*140}")
    
    import re
    import unicodedata
    def normalize(t):
        t = unicodedata.normalize('NFKD', t).encode('ASCII', 'ignore').decode('utf-8')
        return re.sub(r'[\W_]+', '', t).lower()

    for item in samples:
        title = item['title']
        year = item['year']
        media_type = item['media_type']
        
        try:
            # Primary Search
            if media_type == 'movie':
                result = await client.search_movie(title, year)
            else:
                result = await client.search_show(title)
            
            # Fallback Search: If missing, try the other type
            fallback_type = None
            if not result:
                if media_type == 'movie':
                    fallback_type = 'show'
                    result = await client.search_show(title)
                else:
                    fallback_type = 'movie'
                    result = await client.search_movie(title, year)
                
                if result:
                    status = f"FOUND ({fallback_type.upper()}?)"
                else:
                    status = "MISSING"
            else:
                 status = "FOUND"

            details = ""
            tmdb_id = "N/A"
            
            if result:
                matched_title = result['title']
                if result.get('year'): matched_title += f" ({result['year']})"
                details = f"Matched: {matched_title}"
                tmdb_id = str(result.get('tmdb_id', 'N/A'))
            else:
                # DIAGNOSTIC: Why did it fail?
                # Perform a manual looser search to see what candidates existed
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    params = {"query": title, "type": "movie" if media_type == "movie" else "show"}
                    url = f"https://api.trakt.tv/search/{'movie' if media_type == 'movie' else 'show'}"
                    headers = client.headers
                    async with session.get(url, headers=headers, params=params) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if not data:
                                details = "Reason: No results returned from Trakt API"
                            else:
                                # Look at top candidate
                                first = data[0]
                                cand_key = "movie" if "movie" in first else "show"
                                cand_item = first.get(cand_key)
                                cand_title = cand_item.get('title')
                                cand_norm = normalize(cand_title)
                                query_norm = normalize(title)
                                
                                if cand_norm != query_norm:
                                    details = f"Reason: Rejected strict match. Top cand: '{cand_title}'"
                                else:
                                    details = f"Reason: Unknown (Top cand: '{cand_title}')"
                        else:
                            details = f"Reason: API Error {resp.status}"

            print(f"{media_type.upper():<8} | {tmdb_id:<8} | {title[:35]:<35} | {status:<10} | {details}")
            
        except Exception as e:
            print(f"{media_type.upper():<8} | {'ERR':<8} | {title[:35]:<35} | ERROR      | {str(e)}")

        # Sleep briefly to avoid rate limits
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(test_trakt_integration())
