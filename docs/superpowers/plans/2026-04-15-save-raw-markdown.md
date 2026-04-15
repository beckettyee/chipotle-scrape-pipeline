# Save Raw Markdown Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Save each Firecrawl search result as a frontmatter-annotated markdown file in `knowledge/raw/`.

**Architecture:** Add a `slugify()` helper and a save loop to the existing `scrape_pipeline.py`. No new files or modules.

**Tech Stack:** Python stdlib (`re`, `pathlib`, `datetime`) — all already available.

---

### Task 1: Add `slugify` helper with tests

**Files:**
- Modify: `scrape_pipeline.py:1-6` (add `datetime` import)
- Modify: `scrape_pipeline.py` (add `slugify` function after imports)
- Create: `tests/test_slugify.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_slugify.py`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scrape_pipeline import slugify


def test_basic_slugify():
    assert slugify("News Releases - Chipotle Mexican Grill") == "news-releases-chipotle-mexican-grill"


def test_collapses_multiple_hyphens():
    assert slugify("hello---world") == "hello-world"


def test_strips_leading_trailing_hyphens():
    assert slugify("--hello--") == "hello"


def test_truncates_to_80_chars():
    long_title = "a" * 100
    result = slugify(long_title)
    assert len(result) <= 80


def test_handles_special_characters():
    assert slugify("Q1 2026: Revenue & Earnings!") == "q1-2026-revenue-earnings"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `source venv/bin/activate && python -m pytest tests/test_slugify.py -v`
Expected: FAIL with `ImportError` — `slugify` doesn't exist yet.

- [ ] **Step 3: Add `datetime` import and `slugify` function to `scrape_pipeline.py`**

Add `from datetime import datetime, timezone` to the imports block (after `from pathlib import Path`).

Add after the `load_dotenv()` call:

```python
def slugify(text, max_length=80):
    """Convert text to a filesystem-safe slug."""
    slug = text.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug[:max_length].rstrip("-")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `source venv/bin/activate && python -m pytest tests/test_slugify.py -v`
Expected: All 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add scrape_pipeline.py tests/test_slugify.py
git commit -m "feat: add slugify helper with tests"
```

---

### Task 2: Add save loop that writes markdown files with frontmatter

**Files:**
- Modify: `scrape_pipeline.py` (add save block after existing print loop)
- Create: `tests/test_save_results.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_save_results.py`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scrape_pipeline import slugify, save_results


def test_save_results_writes_files(tmp_path):
    results = [
        {
            "title": "Test Release",
            "url": "https://example.com/test",
            "markdown": "# Hello\n\nSome content here.",
        },
        {
            "title": "Another Release",
            "url": "https://example.com/another",
            "markdown": "# Another\n\nMore content.",
        },
    ]

    save_results(results, tmp_path)

    files = sorted(tmp_path.glob("*.md"))
    assert len(files) == 2
    assert files[0].name == "another-release.md"
    assert files[1].name == "test-release.md"


def test_save_results_includes_frontmatter(tmp_path):
    results = [
        {
            "title": "Test Release",
            "url": "https://example.com/test",
            "markdown": "# Hello",
        },
    ]

    save_results(results, tmp_path)

    content = (tmp_path / "test-release.md").read_text()
    assert content.startswith("---\n")
    assert 'title: "Test Release"' in content
    assert 'url: "https://example.com/test"' in content
    assert "scraped_at:" in content
    assert "# Hello" in content


def test_save_results_handles_missing_markdown(tmp_path):
    results = [
        {
            "title": "No Content",
            "url": "https://example.com/empty",
            "markdown": None,
        },
    ]

    save_results(results, tmp_path)

    content = (tmp_path / "no-content.md").read_text()
    assert content.startswith("---\n")
    assert "---\n\n" in content  # frontmatter ends, body is empty


def test_save_results_overwrites_existing(tmp_path):
    (tmp_path / "test-release.md").write_text("old content")

    results = [
        {
            "title": "Test Release",
            "url": "https://example.com/test",
            "markdown": "# New",
        },
    ]

    save_results(results, tmp_path)

    content = (tmp_path / "test-release.md").read_text()
    assert "# New" in content
    assert "old content" not in content
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `source venv/bin/activate && python -m pytest tests/test_save_results.py -v`
Expected: FAIL with `ImportError` — `save_results` doesn't exist yet.

- [ ] **Step 3: Add `save_results` function to `scrape_pipeline.py`**

Add after the `slugify` function:

```python
def save_results(results, output_dir):
    """Save Firecrawl results as frontmatter-annotated markdown files."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for r in results:
        slug = slugify(r["title"])
        filename = f"{slug}.md"
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `source venv/bin/activate && python -m pytest tests/test_save_results.py -v`
Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add scrape_pipeline.py tests/test_save_results.py
git commit -m "feat: add save_results function with tests"
```

---

### Task 3: Wire save loop into the pipeline

**Files:**
- Modify: `scrape_pipeline.py` (add call to `save_results` after print loop)

- [ ] **Step 1: Add the save call at the end of `scrape_pipeline.py`**

Append after the existing `for r in results` print loop:

```python
# --- Step 02: Save raw markdown files ---

output_dir = Path("knowledge/raw")
save_results(results, output_dir)
print(f"\nSaved {len(results)} files to {output_dir}/")
```

- [ ] **Step 2: Run the full pipeline**

Run: `source venv/bin/activate && python scrape_pipeline.py`
Expected: The usual Firecrawl output plus new lines showing each file saved to `knowledge/raw/`.

- [ ] **Step 3: Verify the saved files**

Run: `ls knowledge/raw/` and inspect one file with `head -20 knowledge/raw/<any-file>.md`.
Expected: Files exist with YAML frontmatter and markdown body.

- [ ] **Step 4: Run all tests**

Run: `source venv/bin/activate && python -m pytest tests/ -v`
Expected: All tests PASS.

- [ ] **Step 5: Add `knowledge/` to `.gitignore` and commit**

```bash
echo "knowledge/" >> .gitignore
git add scrape_pipeline.py .gitignore
git commit -m "feat: wire save_results into pipeline, ignore knowledge dir"
```
