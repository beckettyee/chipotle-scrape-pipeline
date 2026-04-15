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
