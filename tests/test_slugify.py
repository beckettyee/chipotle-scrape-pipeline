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
