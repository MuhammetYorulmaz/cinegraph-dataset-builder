"""
User review fetcher.

Reviews are paginated on TMDB's side. The fetcher walks every page until
the server reports the last one, skipping empty bodies and trimming
extremely long reviews so that a single record never dominates storage.
"""

from __future__ import annotations

import time

from cinegraph.api.client import api_get
from cinegraph.config import settings
from cinegraph.processing.parsers import clean_html


_MAX_CONTENT_LENGTH = 3000


def fetch_reviews(item_id: int, media_type: str) -> list[dict]:
    """
    Fetch every review page for a movie or TV show.

    Parameters
    ----------
    item_id:
        TMDB movie or TV identifier.
    media_type:
        Either ``"movie"`` or ``"tv"``.

    Returns
    -------
    list[dict]
        Flat review records. May be empty if the title has no reviews.
    """
    reviews: list[dict] = []
    page = 1

    while True:
        data = api_get(f"{media_type}/{item_id}/reviews", {"page": page})

        if not data or not data.get("results"):
            break

        for item in data["results"]:
            content = clean_html(item.get("content"))
            if not content:
                continue

            reviews.append({
                "review_id":  item.get("id"),
                "tmdb_id":    item_id,
                "media_type": media_type,
                "author":     item.get("author"),
                "rating":     (item.get("author_details") or {}).get("rating"),
                "content":    content[:_MAX_CONTENT_LENGTH],
                "created_at": item.get("created_at"),
                "url":        item.get("url"),
            })

        if page >= data.get("total_pages", 1):
            break

        page += 1
        time.sleep(settings.request_delay)

    return reviews
