import requests
from bs4 import BeautifulSoup
import os
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class ZurgClient:
    def __init__(self, base_url=None):
        # Default to localhost if not specified, but allow override via Env
        if not base_url:
            base_url = os.getenv("ZURG_API_URL", "http://localhost:9999")
        self.base_url = base_url.rstrip('/')

    def get_stats(self):
        """
        Scrape and parse the Zurg dashboard for stats.
        Returns a dict with structured data or None if failed.
        """
        try:
            url = f"{self.base_url}/"
            logger.info(f"Fetching Zurg stats from: {url}")
            
            # Short timeout to avoid blocking if Zurg is down
            response = requests.get(url, timeout=3)
            if response.status_code != 200:
                logger.error(f"Zurg returned status {response.status_code}")
                return None

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Initialize data structure
            data = {
                "version": "Unknown",
                "status": "online",
                "memory": {
                    "usage": "0 MB",
                    "total_allocated": "0 MB",
                    "system": "0 MB"
                },
                "account": {
                    "username": "Unknown",
                    "type": "free",
                    "premium_days": 0,
                    "expiration": None
                }
            }

            # Parse Strategy:
            # Zurg's UI seems to use tables or list-like structures. 
            # Based on the user provided text, it's label-value pairs. 
            # We will look for text patterns since we don't know exact classes.
            
            text_content = soup.get_text(" ", strip=True)
            
            # 1. Version - Removed per user request
            data["version"] = None
            
            # 2. Memory
            # "Memory Allocation 33 MB" (Option 1) or "Memory 145 MB" (Option 2)
            mem_match = re.search(r"(?:Memory Allocation|Memory)\s+(\d+\s*MB)", text_content)
            if mem_match:
                data["memory"]["usage"] = mem_match.group(1)

            # "Total Memory Allocated 426481 MB" or "Total Allocated 99464 MB"
            total_mem_match = re.search(r"Total(?: Memory)? Allocated\s+(\d+\s*MB)", text_content)
            if total_mem_match:
                data["memory"]["total_allocated"] = total_mem_match.group(1)
                
            # 3. User Info
            # "User Info Username user-a" or just "Username user-a" (implied)
            # Option 1: "User Info Username user-a"
            # Option 2: "User Information user-b"
            
            # Try to find Username pattern
            # "Username X"
            # Or just look for the block. In Option 2 it's "User Information user-b"
            
            username = "Unknown"
            user_match = re.search(r"Username\s+(\S+)", text_content)
            if user_match:
                 username = user_match.group(1)
            else:
                # Option 2 Fallback: "User Information [Name]"
                user_match_2 = re.search(r"User Information\s+(\S+)", text_content)
                if user_match_2:
                    username = user_match_2.group(1)
            
            data["account"]["username"] = username
            
            # Premium Days
            # "Premium 87 days" or "Premium 148 days"
            prem_match = re.search(r"Premium\s+(\d+)\s+days", text_content)
            if prem_match:
                 data["account"]["premium_days"] = int(prem_match.group(1))
                 data["account"]["type"] = "premium" if int(prem_match.group(1)) > 0 else "free"
            
            # Expiration
            # "Expiration 2026-03-30T..." or "Expires 2026-06-01T..."
            exp_match = re.search(r"(?:Expiration|Expires)\s+(\d{4}-\d{2}-\d{2}T[\d:\.]+[\+\-]\d{2}:\d{2})", text_content)
            if exp_match:
                data["account"]["expiration"] = exp_match.group(1)

            return data

        except requests.exceptions.RequestException:
            logger.warning("Could not connect to Zurg")
            return {
                "version": "Unknown",
                "status": "offline",
                "memory": None,
                "account": None
            }
        except Exception as e:
            logger.error(f"Error parsing Zurg stats: {e}")
            return None
