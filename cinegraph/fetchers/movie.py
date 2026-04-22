"""
Movie metadata fetcher.

A single ``movie/{id}`` request with ``append_to_response`` retrieves
credits, keywords, videos, release dates, related titles, alternative
titles, and watch providers — collapsing seven separate HTTP calls into
one round trip.
"""

from __future__ import annotations

from cinegraph.api.client import api_get
from cinegraph.config import settings
from cinegraph.processing.parsers import (
    alternative_titles,
    clean_html,
    image_url,
    join_ids,
    join_names,
    safe_year,
)
from cinegraph.processing.transforms import (
    theatrical_certification,
    watch_providers_flat,
)


_APPEND = (
    "credits,keywords,videos,release_dates,similar,"
    "recommendations,alternative_titles,watch/providers"
)


def fetch_movie(movie_id: int) -> dict | None:
    """Fetch a single movie and flatten its response into one row."""
    data = api_get(
        f"movie/{movie_id}",
        {"append_to_response": _APPEND, "language": "en-US"},
    )
    if not data or not data.get("id"):
        return None

    # Credits — top 15 cast members and filtered crew roles.
    credits = data.get("credits") or {}
    cast = (credits.get("cast") or [])[:15]
    crew = credits.get("crew") or []

    directors = [c for c in crew if c.get("job") == "Director"]
    writers   = [c for c in crew if c.get("job") in ("Screenplay", "Writer", "Story")][:5]
    producers = [c for c in crew if c.get("job") == "Producer"][:3]
    composers = [
        c for c in crew
        if c.get("department") == "Sound" and "Composer" in (c.get("job") or "")
    ][:2]

    keywords = (data.get("keywords") or {}).get("keywords") or []

    trailers = [
        video for video in (data.get("videos") or {}).get("results", [])
        if video.get("type") == "Trailer" and video.get("site") == "YouTube"
    ]

    similar = (data.get("similar")         or {}).get("results", [])[:settings.similar_count]
    recs    = (data.get("recommendations") or {}).get("results", [])[:settings.recommended_count]

    # Financial aggregates — null when source values are absent.
    budget  = data.get("budget")  or 0
    revenue = data.get("revenue") or 0

    collection = data.get("belongs_to_collection") or {}
    alt_items  = (data.get("alternative_titles") or {}).get("titles") or []

    row = {
        # Identifiers
        "tmdb_id":              data["id"],
        "imdb_id":              data.get("imdb_id") or None,

        # Titles and text
        "title":                clean_html(data.get("title")),
        "original_title":       clean_html(data.get("original_title")),
        "original_language":    data.get("original_language"),
        "alternative_titles":   alternative_titles(alt_items),
        "tagline":              clean_html(data.get("tagline")),
        "overview":             clean_html(data.get("overview")),

        # Timing
        "release_date":         data.get("release_date") or None,
        "release_year":         safe_year(data.get("release_date")),
        "runtime_min":          data.get("runtime") or None,
        "status":               data.get("status") or None,

        # Ratings
        "vote_average":         data.get("vote_average") or None,
        "vote_count":           data.get("vote_count")   or None,
        "popularity":           data.get("popularity")   or None,

        # Financials
        "budget_usd":           budget  if budget  > 0 else None,
        "revenue_usd":          revenue if revenue > 0 else None,
        "profit_usd":           (revenue - budget) if budget > 0 and revenue > 0 else None,
        "roi_pct":              round((revenue - budget) / budget * 100, 1) if budget > 0 else None,

        # Categorization
        "genres":               join_names(data.get("genres")),
        "keywords":             join_names(keywords),
        "us_certification":     theatrical_certification(data.get("release_dates"), "US"),

        # Production
        "production_companies": join_names(data.get("production_companies")),
        "production_countries": join_names(data.get("production_countries"), "iso_3166_1"),
        "spoken_languages":     join_names(data.get("spoken_languages"), "english_name"),

        # Collection
        "collection_id":        collection.get("id") or None,
        "collection_name":      clean_html(collection.get("name")),

        # Credits
        "cast_names":           join_names(cast),
        "cast_ids":             join_ids([c.get("id") for c in cast]),
        "cast_characters":      join_ids([c.get("character") for c in cast]),
        "directors":            join_names(directors),
        "director_ids":         join_ids([c.get("id") for c in directors]),
        "writers":              join_names(writers),
        "producers":            join_names(producers),
        "composers":            join_names(composers),

        # Videos
        "has_trailer":          bool(trailers),
        "trailer_url":          f"https://youtube.com/watch?v={trailers[0]['key']}" if trailers else None,

        # Related content
        "similar_ids":          join_ids([s.get("id") for s in similar]),
        "similar_titles":       join_names(similar, "title"),
        "recommended_ids":      join_ids([r.get("id") for r in recs]),
        "recommended_titles":   join_names(recs, "title"),

        # Imagery
        "poster_url":           image_url(data.get("poster_path"), "w500"),
        "poster_url_hd":        image_url(data.get("poster_path"), "original"),
        "backdrop_url":         image_url(data.get("backdrop_path"), "w780"),
        "homepage":             data.get("homepage") or None,
    }

    # Watch providers — per-country columns appended in place.
    row.update(watch_providers_flat(data.get("watch/providers"), settings.watch_countries))

    return row
