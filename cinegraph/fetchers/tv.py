"""
Television metadata fetcher.

Differences from the movie fetcher:
    • Directors are replaced by "creators" (show runners / creators).
    • Season and episode counts are added.
    • Content ratings use a different endpoint shape than movie release
      dates — parsed via :func:`content_ratings_flat`.
    • External IDs include ``tvdb_id`` in addition to ``imdb_id``.
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
    content_ratings_flat,
    watch_providers_flat,
)


_APPEND = (
    "credits,keywords,external_ids,similar,"
    "recommendations,alternative_titles,watch/providers,content_ratings"
)


def fetch_tv(tv_id: int) -> dict | None:
    """Fetch a single TV series and flatten its response into one row."""
    data = api_get(
        f"tv/{tv_id}",
        {"append_to_response": _APPEND, "language": "en-US"},
    )
    if not data or not data.get("id"):
        return None

    credits = data.get("credits") or {}
    cast = (credits.get("cast") or [])[:15]
    crew = credits.get("crew") or []

    keywords  = (data.get("keywords")           or {}).get("results") or []
    similar   = (data.get("similar")            or {}).get("results", [])[:settings.similar_count]
    recs      = (data.get("recommendations")    or {}).get("results", [])[:settings.recommended_count]
    external  =  data.get("external_ids")       or {}
    alt_items = (data.get("alternative_titles") or {}).get("results") or []

    # Exclude season 0 (specials/bonus content) from the canonical count.
    seasons = [s for s in (data.get("seasons") or [])
               if (s.get("season_number") or 0) > 0]
    runtimes = data.get("episode_run_time") or []

    creators = data.get("created_by") or []
    networks = data.get("networks")   or []

    row = {
        # Identifiers
        "tmdb_id":              data["id"],
        "imdb_id":              external.get("imdb_id") or None,
        "tvdb_id":              external.get("tvdb_id") or None,

        # Titles and text
        "title":                clean_html(data.get("name")),
        "original_title":       clean_html(data.get("original_name")),
        "original_language":    data.get("original_language"),
        "alternative_titles":   alternative_titles(alt_items),
        "tagline":              clean_html(data.get("tagline")),
        "overview":             clean_html(data.get("overview")),

        # Air dates
        "first_air_date":       data.get("first_air_date") or None,
        "last_air_date":        data.get("last_air_date")  or None,
        "release_year":         safe_year(data.get("first_air_date")),
        "status":               data.get("status") or None,
        "in_production":        data.get("in_production"),
        "show_type":            data.get("type") or None,

        # Episode structure
        "number_of_seasons":    data.get("number_of_seasons")  or None,
        "number_of_episodes":   data.get("number_of_episodes") or None,
        "avg_episode_runtime":  round(sum(runtimes) / len(runtimes)) if runtimes else None,
        "season_count":         len(seasons) or None,

        # Ratings
        "vote_average":         data.get("vote_average") or None,
        "vote_count":           data.get("vote_count")   or None,
        "popularity":           data.get("popularity")   or None,

        # Categorization
        "genres":               join_names(data.get("genres")),
        "keywords":             join_names(keywords),

        # Broadcast and production
        "networks":             join_names(networks),
        "network_ids":          join_ids([n.get("id") for n in networks]),
        "origin_countries":     join_ids(data.get("origin_country")),
        "spoken_languages":     join_names(data.get("spoken_languages"), "english_name"),
        "production_companies": join_names(data.get("production_companies")),

        # Credits
        "creators":             join_names(creators),
        "creator_ids":          join_ids([c.get("id") for c in creators]),
        "cast_names":           join_names(cast),
        "cast_ids":             join_ids([c.get("id") for c in cast]),
        "cast_characters":      join_ids([c.get("character") for c in cast]),
        "writers":              join_names([c for c in crew if c.get("department") == "Writing"][:5]),

        # Related content
        "similar_ids":          join_ids([s.get("id") for s in similar]),
        "similar_titles":       join_names(similar, "name"),
        "recommended_ids":      join_ids([r.get("id") for r in recs]),
        "recommended_titles":   join_names(recs, "name"),

        # Imagery
        "poster_url":           image_url(data.get("poster_path"), "w500"),
        "poster_url_hd":        image_url(data.get("poster_path"), "original"),
        "backdrop_url":         image_url(data.get("backdrop_path"), "w780"),
        "homepage":             data.get("homepage") or None,
    }

    # Watch providers and content ratings are appended in place.
    row.update(watch_providers_flat(data.get("watch/providers"), settings.watch_countries))
    row.update(content_ratings_flat(data.get("content_ratings"), settings.watch_countries))

    return row
