import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
import requests

load_dotenv()


def slugify(text, max_length=80):
    """Convert text to a filesystem-safe slug."""
    slug = text.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug[:max_length].rstrip("-")


api_key = os.getenv("FIRECRAWL_API_KEY")

# --- Step 01: Search + scrape with Firecrawl ---

api_url = "https://api.firecrawl.dev/v2/search"

headers = {
    "Authorization": f"Bearer {api_key}"
}

payload = {
    "query": "Chipotle investor relations press releases",
    "limit": 5,
    "scrapeOptions": {"formats": ["markdown"]}
}

response = requests.post(api_url, headers=headers, json=payload)

data = response.json() # parse the response as JSON
results = data["data"]["web"] # extract the results from the response
print(f"Firecrawl returned {len(results)} results") # print the number of results

for r in results:
    print(f"  - {r['title']}")
    print(f"    {r['url']}")
    print(f"    markdown length: {len(r.get('markdown') or '')} chars")