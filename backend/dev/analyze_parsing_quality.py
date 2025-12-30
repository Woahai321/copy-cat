import json
import re
import os
from collections import defaultdict

SUSPICIOUS_KEYWORDS = [
    "1080p", "720p", "2160p", "480p", "WEBDL", "WEB-DL", "Bluray", "Blu-ray",
    "x264", "x265", "HEVC", "AVC", "AAC", "DTS", "TrueHD", "REMUX",
    "H.264", "H.265", "AMZN", "NF", "DSNP", "HULU"
]

def is_suspicious(item):
    reasons = []
    title = item.get("title", "")
    
    # Check 1: Metadata keywords in title
    for kw in SUSPICIOUS_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", title, re.IGNORECASE):
            reasons.append(f"Contains '{kw}'")
            
    # Check 2: Very long title
    if len(title) > 60:
        reasons.append("Title > 60 chars")
        
    # Check 3: Uncleaned separator characters
    if re.search(r"[\._]", title):
         # Allow dots if it looks like an acronym e.g. S.H.I.E.L.D but risky
         # A simple heuristic: if it has dots/underscores it might be uncleaned
         pass # Actually clean_title typically handles this, but let's flag if obvious
    
    # Check 4: Movie without year (should not happen with current regex but let's check)
    if item.get("media_type") == "movie" and item.get("year") is None:
        reasons.append("Movie with No Year")
        
    return reasons

def analyze():
    json_path = r"c:\Users\aidan\Downloads\newcopypaste\copypaste\zurg_parsed.json"
    if not os.path.exists(json_path):
        print("Json not found")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    suspicious = []
    
    print(f"Analyzing {len(data)} parsed items...")
    
    for item in data:
        reasons = is_suspicious(item)
        if reasons:
            item["suspicious_reasons"] = reasons
            suspicious.append(item)
            
    # Report
    print(f"Found {len(suspicious)} suspicious items.")
    print("-" * 60)
    
    # Write details to file for user review
    out_path = r"c:\Users\aidan\Downloads\newcopypaste\copypaste\suspicious_items.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(suspicious, f, indent=2)
        
    # Print sample
    for i in suspicious[:10]:
        print(f"Title: {i['title']}")
        print(f"Reasons: {i['suspicious_reasons']}")
        print(f"Original: {i['original']}")
        print("-" * 40)
        
    print(f"\nFull list written to {out_path}")

if __name__ == "__main__":
    analyze()
