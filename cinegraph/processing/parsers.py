"""
Pure-function parsers used across fetchers.

These utilities normalize raw API payloads into the flat string/numeric
values stored in the final CSV files.
"""

from __future__ import annotations

import re
from typing import Any


_HTML_TAG = re.compile(r"<[^>]+>")
_WHITESPACE = re.compile(r"\s+")


def clean_html(text: Any) -> str | None:
    """Strip HTML tags and collapse internal whitespace."""
    if not text or not isinstance(text, str):
        return None
    cleaned = _HTML_TAG.sub(" ", text)
    cleaned = _WHITESPACE.sub(" ", cleaned).strip()
    return cleaned or None


def join_names(items: list | None, key: str = "name") -> str | None:
    """Concatenate dict values under ``key`` with commas."""
    if not items:
        return None
    joined = ", ".join(str(item[key]) for item in items if item.get(key))
    return joined or None


def join_ids(items: list | None) -> str | None:
    """Concatenate a list of primitive values with commas."""
    if not items:
        return None
    joined = ", ".join(str(item) for item in items if item is not None)
    return joined or None


def parse_id_list(value: Any) -> list[int]:
    """Parse a comma-separated ID string back into a list of integers."""
    if value is None:
        return []
    if isinstance(value, (int, float)):
        try:
            return [int(value)]
        except (ValueError, OverflowError):
            return []
    if not isinstance(value, str):
        return []

    parsed: list[int] = []
    for token in value.split(","):
        token = token.strip()
        if not token:
            continue
        try:
            parsed.append(int(float(token)))
        except (ValueError, TypeError, OverflowError):
            pass
    return parsed


def image_url(path: str | None, size: str = "w500") -> str | None:
    """Convert a TMDB relative image path into a fully-qualified URL."""
    if not path or not isinstance(path, str):
        return None
    path = path.strip()
    if not path.startswith("/"):
        return None
    return f"https://image.tmdb.org/t/p/{size}{path}"


def safe_year(date_str: str | None) -> int | None:
    """Extract a four-digit year from an ISO date string."""
    if not date_str or len(date_str) < 4:
        return None
    prefix = date_str[:4]
    return int(prefix) if prefix.isdigit() else None


def alternative_titles(items: list | None) -> str | None:
    """
    Format alternative title entries as ``CC:Title`` pairs joined by ``|``.

    Example output: ``TR:Matriks | DE:Matrix``
    """
    if not items:
        return None
    parts = [
        f"{item.get('iso_3166_1', '?')}:{item.get('title', '')}"
        for item in items
        if item.get("title")
    ]
    return " | ".join(parts) or None
