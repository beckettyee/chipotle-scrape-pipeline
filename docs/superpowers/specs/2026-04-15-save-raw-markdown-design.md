# Save Firecrawl Results as Raw Markdown

## Overview

Extend `scrape_pipeline.py` to save each Firecrawl search result as a markdown file in `knowledge/raw/`, with YAML frontmatter for metadata.

## Data Flow

```
Firecrawl API → response JSON → loop over results → write .md files to knowledge/raw/
```

## File Format

Each file has YAML frontmatter followed by the raw markdown body:

```markdown
---
title: "News Releases - Chipotle Mexican Grill"
url: "https://ir.chipotle.com/news-releases"
scraped_at: "2026-04-15T11:03:00Z"
---

(raw markdown content from Firecrawl)
```

## Filename Slugification

- Lowercase the title
- Replace non-alphanumeric characters with hyphens
- Collapse multiple hyphens into one
- Strip leading/trailing hyphens
- Truncate to 80 characters to avoid filesystem issues
- Append `.md`

Example: `"News Releases - Chipotle Mexican Grill"` → `news-releases-chipotle-mexican-grill.md`

## Script Changes

All changes are inline in `scrape_pipeline.py` (Approach 1 — no new files or modules).

1. **Add `slugify(text)` helper** — uses `re.sub` to produce a filesystem-safe slug.
2. **Add save block after the existing print loop:**
   - Create `knowledge/raw/` via `Path.mkdir(parents=True, exist_ok=True)`
   - Loop over results: build frontmatter string, write `slug.md`
   - Overwrite existing files on re-runs (no skip/version logic)
   - Print each file path written for visibility

## Dependencies

No new dependencies. Uses `re`, `pathlib.Path`, and `datetime` from stdlib. `re` and `Path` are already imported.

## Decisions

- **Frontmatter + raw body** (not cleaned) — preserves original content for downstream processing
- **Slugified title filenames** — human-browsable; no hash suffix needed unless collisions arise
- **Overwrite on re-run** — `knowledge/raw/` is a disposable cache, Firecrawl is source of truth
- **Inline implementation** — the save logic is ~15 lines; extraction is premature for a single-file project
