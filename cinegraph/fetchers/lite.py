"""
Lightweight metadata fetchers for orphan titles.

"Orphan" titles are IDs referenced by the recommendation graph of the
main corpus but not present as first-class entries. They are captured
with a minimal schema so that downstream recommendation queries resolve
to complete records, without paying the cost of a full detail fetch.

A per-media vote-count threshold filters low-signal placeholder entries.
"""

from __future__ import annotations

from cinegraph.api.client import api_get
from cinegraph.config import settings
from cinegraph.processing.parsers import clean_html, image_url, join_names, safe_year


def fetch_movie_lite(movie_id: int) -> dict | None:
    """Fetch a minimal movie record if it meets the orphan quality threshold."""
    data = api_get(f"movie/{movie_id}", {"language": "en-US"})
    if not data or not data.get("id"):
        return None

    vote_count = data.get("vote_count") or 0
    if vote_count < settings.orphan_movie_min_votes:
        return None

    return {
        "tmdb_id":           data["id"],
        "imdb_id":           data.get("imdb_id") or None,
        "title":             clean_html(data.get("title")),
        "original_language": data.get("original_language"),
        "release_year":      safe_year(data.get("release_date")),
        "overview":          clean_html(data.get("overview")),
        "genres":            join_names(data.get("genres"), "name"),
        "vote_average":      data.get("vote_average") or None,
        "vote_count":        vote_count,
        "poster_url":        image_url(data.get("poster_path"), "w500"),
    }


def fetch_tv_lite(tv_id: int) -> dict | None:
    """Fetch a minimal TV record if it meets the orphan quality threshold."""
    data = api_get(f"tv/{tv_id}", {"language": "en-US"})
    if not data or not data.get("id"):
        return None

    vote_count = data.get("vote_count") or 0
    if vote_count < settings.orphan_tv_min_votes:
        return None

    return {
        "tmdb_id":           data["id"],
        "title":             clean_html(data.get("name")),
        "original_language": data.get("original_language"),
        "release_year":      safe_year(data.get("first_air_date")),
        "overview":          clean_html(data.get("overview")),
        "genres":            join_names(data.get("genres"), "name"),
        "vote_average":      data.get("vote_average") or None,
        "vote_count":        vote_count,
        "poster_url":        image_url(data.get("poster_path"), "w500"),
    }
