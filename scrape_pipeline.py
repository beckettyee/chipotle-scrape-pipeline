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


def save_results(results, output_dir):
    """Save Firecrawl results as frontmatter-annotated markdown files."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for i, r in enumerate(results, start=1):
        slug = slugify(r["title"])
        filename = f"{i:02d}-{slug}.md"
        scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        frontmatter = (
            f'---\n'
            f'title: "{r["title"]}"\n'
            f'url: "{r["url"]}"\n'
            f'scraped_at: "{scraped_at}"\n'
            f'---\n'
        )
        body = r.get("markdown") or ""
        path = output_dir / filename
        path.write_text(frontmatter + "\n" + body)
        print(f"  saved: {path}")


if __name__ == "__main__":
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

    data = response.json()  # parse the response as JSON
    results = data["data"]["web"]  # extract the results from the response
    print(f"Firecrawl returned {len(results)} results")  # print the number of results

    for r in results:
        print(f"  - {r['title']}")
        print(f"    {r['url']}")
        print(f"    markdown length: {len(r.get('markdown') or '')} chars")

    # --- Step 02: Save raw markdown files ---

    output_dir = Path("knowledge/raw")
    save_results(results, output_dir)
    print(f"\nSaved {len(results)} files to {output_dir}/")
