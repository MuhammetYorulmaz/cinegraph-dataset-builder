"""
Person metadata fetcher.

Fetches biographical details together with filmography (movie and TV
credits) and external social IDs in a single request.
"""

from __future__ import annotations

from cinegraph.api.client import api_get
from cinegraph.processing.parsers import clean_html, image_url, join_ids, join_names


_APPEND = "movie_credits,tv_credits,external_ids"

_GENDER_MAP = {
    0: "Unspecified",
    1: "Female",
    2: "Male",
    3: "Non-binary",
}


def fetch_person(person_id: int) -> dict | None:
    """Fetch a single person record and flatten the response."""
    data = api_get(
        f"person/{person_id}",
        {"append_to_response": _APPEND, "language": "en-US"},
    )
    if not data or not data.get("id"):
        return None

    external = data.get("external_ids") or {}

    # Movie credits — both as cast and as director.
    movie_credits = data.get("movie_credits") or {}
    movie_cast = sorted(
        movie_credits.get("cast") or [],
        key=lambda c: (c.get("popularity") or 0),
        reverse=True,
    )[:15]
    directed = [
        c for c in (movie_credits.get("crew") or [])
        if c.get("job") == "Director"
    ][:8]

    # TV credits.
    tv_credits = data.get("tv_credits") or {}
    tv_cast = sorted(
        tv_credits.get("cast") or [],
        key=lambda c: (c.get("popularity") or 0),
        reverse=True,
    )[:10]

    gender = _GENDER_MAP.get(data.get("gender") or 0, "Unspecified")

    return {
        # Identifiers
        "tmdb_id":             data["id"],
        "imdb_id":             external.get("imdb_id") or None,
        "instagram_id":        external.get("instagram_id") or None,
        "twitter_id":          external.get("twitter_id") or None,

        # Basic info
        "name":                clean_html(data.get("name")),
        "also_known_as":       ", ".join(data.get("also_known_as") or []) or None,
        "gender":              gender,
        "birthday":            data.get("birthday") or None,
        "deathday":            data.get("deathday") or None,
        "place_of_birth":      clean_html(data.get("place_of_birth")),
        "known_for_dept":      data.get("known_for_department") or None,

        # Biography and ranking
        "biography":           clean_html(data.get("biography")),
        "popularity":          data.get("popularity") or 0,

        # Filmography — movies
        "known_movies":        join_names(movie_cast, "title"),
        "known_movie_ids":     join_ids([c.get("id") for c in movie_cast]),
        "total_movie_credits": len(movie_credits.get("cast") or []),
        "directed_movies":     join_names(directed, "title"),
        "directed_movie_ids":  join_ids([c.get("id") for c in directed]),
        "total_directed":      len([
            c for c in (movie_credits.get("crew") or [])
            if c.get("job") == "Director"
        ]),

        # Filmography — television
        "known_tv_shows":      join_names(tv_cast, "name"),
        "known_tv_ids":        join_ids([c.get("id") for c in tv_cast]),
        "total_tv_credits":    len(tv_credits.get("cast") or []),

        # Imagery
        "profile_url":         image_url(data.get("profile_path"), "h632"),
        "homepage":            data.get("homepage") or None,
    }
