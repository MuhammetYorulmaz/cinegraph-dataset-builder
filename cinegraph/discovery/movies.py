"""
Movie identifier discovery.

Combines four curated list endpoints with genre-based discovery filtered
by vote count to produce a deduplicated set of TMDB movie identifiers.
"""

from __future__ import annotations

import time

from cinegraph.api.client import api_get
from cinegraph.config import settings
from cinegraph.utils.logging import log


# TMDB movie genre taxonomy — the discovery endpoint accepts the numeric IDs.
MOVIE_GENRES: dict[int, str] = {
    28:    "Action",
    12:    "Adventure",
    16:    "Animation",
    35:    "Comedy",
    80:    "Crime",
    99:    "Documentary",
    18:    "Drama",
    10751: "Family",
    14:    "Fantasy",
    36:    "History",
    27:    "Horror",
    10402: "Music",
    9648:  "Mystery",
    10749: "Romance",
    878:   "Science Fiction",
    10770: "TV Movie",
    53:    "Thriller",
    10752: "War",
    37:    "Western",
}


def _collect(endpoint: str, max_pages: int, params: dict | None = None) -> set[int]:
    """Walk a paginated TMDB list endpoint and return all unique IDs."""
    base_params = {"page": 1, "language": "en-US"}
    base_params.update(params or {})

    first = api_get(endpoint, {**base_params, "page": 1})
    if not first or not first.get("results"):
        return set()

    api_total = first.get("total_pages", 1)
    page_limit = min(api_total, max_pages, 500)

    log.info(f"  ├─ {endpoint}: API={api_total:,} pages │ fetching={page_limit}")

    def _extract(data: dict) -> set[int]:
        return {item["id"] for item in data.get("results", []) if item.get("id")}

    collected = _extract(first)
    empty_streak = 0

    for page in range(2, page_limit + 1):
        data = api_get(endpoint, {**base_params, "page": page})

        if not data or not data.get("results"):
            empty_streak += 1
        else:
            new_ids = _extract(data) - collected
            if not new_ids:
                empty_streak += 1
            else:
                empty_streak = 0
                collected |= new_ids

        if empty_streak >= settings.empty_page_tolerance:
            log.info(f"  ├─ {endpoint}: exhausted at page {page}, stopping.")
            break

        time.sleep(settings.request_delay)

    return collected


def gather_movie_ids() -> set[int]:
    """
    Collect movie IDs from curated lists and genre-based discovery.

    Sources:
        • movie/popular     — daily activity leaders
        • movie/top_rated   — highest user-rated titles
        • movie/now_playing — current theatrical releases
        • movie/upcoming    — scheduled releases
        • discover/movie    — per-genre sweep ordered by vote_count desc,
                              filtered by ``movie_min_votes``
    """
    log.info("Starting movie ID discovery")
    identifiers: set[int] = set()

    for endpoint in ("movie/popular", "movie/top_rated",
                     "movie/now_playing", "movie/upcoming"):
        identifiers |= _collect(endpoint, settings.movie_pages)

    log.info(
        f"  ├─ Genre discovery ({len(MOVIE_GENRES)} genres, "
        f"min. {settings.movie_min_votes} votes)"
    )
    for genre_id, genre_name in MOVIE_GENRES.items():
        new_ids = _collect(
            "discover/movie",
            settings.movie_genre_pages,
            {
                "with_genres":    genre_id,
                "sort_by":        "vote_count.desc",
                "vote_count.gte": settings.movie_min_votes,
            },
        )
        identifiers |= new_ids
        log.info(f"  │   {genre_name:<20} +{len(new_ids):,}")

    log.info(f"  └─ Unique movie IDs: {len(identifiers):,}")
    return identifiers
