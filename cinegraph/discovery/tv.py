"""
Television identifier discovery.

Mirrors the movie discovery strategy but uses the TMDB TV endpoints and
a lower vote-count threshold, reflecting the naturally sparser voting
patterns of television content.
"""

from __future__ import annotations

from cinegraph.config import settings
from cinegraph.discovery.movies import _collect
from cinegraph.utils.logging import log


TV_GENRES: dict[int, str] = {
    10759: "Action & Adventure",
    16:    "Animation",
    35:    "Comedy",
    80:    "Crime",
    99:    "Documentary",
    18:    "Drama",
    10751: "Family",
    10762: "Kids",
    9648:  "Mystery",
    10763: "News",
    10764: "Reality",
    10765: "Sci-Fi & Fantasy",
    10766: "Soap",
    10767: "Talk",
    10768: "War & Politics",
    37:    "Western",
}


def gather_tv_ids() -> set[int]:
    """
    Collect television IDs from curated lists and genre-based discovery.

    Sources:
        • tv/popular      — daily activity leaders
        • tv/top_rated    — highest user-rated series
        • tv/on_the_air   — airing within the last/next seven days
        • tv/airing_today — releasing an episode today
        • discover/tv     — per-genre sweep ordered by vote_count desc,
                            filtered by ``tv_min_votes``
    """
    log.info("Starting TV ID discovery")
    identifiers: set[int] = set()

    for endpoint in ("tv/popular", "tv/top_rated",
                     "tv/on_the_air", "tv/airing_today"):
        identifiers |= _collect(endpoint, settings.tv_pages)

    log.info(
        f"  ├─ Genre discovery ({len(TV_GENRES)} genres, "
        f"min. {settings.tv_min_votes} votes)"
    )
    for genre_id, genre_name in TV_GENRES.items():
        new_ids = _collect(
            "discover/tv",
            settings.tv_genre_pages,
            {
                "with_genres":    genre_id,
                "sort_by":        "vote_count.desc",
                "vote_count.gte": settings.tv_min_votes,
            },
        )
        identifiers |= new_ids
        log.info(f"  │   {genre_name:<22} +{len(new_ids):,}")

    log.info(f"  └─ Unique TV IDs: {len(identifiers):,}")
    return identifiers
