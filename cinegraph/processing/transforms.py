"""
Domain-specific transforms that flatten complex nested TMDB responses
into tabular columns.
"""

from __future__ import annotations

from cinegraph.processing.parsers import join_names


def watch_providers_flat(
    raw:       dict | None,
    countries: list[str],
) -> dict:
    """
    Flatten the ``watch/providers`` response into per-country columns.

    For each country code the function emits five columns:
        watch_{cc}_flatrate  — subscription services
        watch_{cc}_rent      — paid rental services
        watch_{cc}_buy       — purchase services
        watch_{cc}_free      — ad-supported or free services
        watch_{cc}_link      — canonical TMDB watch page

    TMDB returns provider entries under the ``provider_name`` key.
    """
    output: dict = {}
    results = (raw or {}).get("results") or {}

    for country in countries:
        entry = results.get(country, {})
        slug = country.lower()
        output[f"watch_{slug}_flatrate"] = join_names(entry.get("flatrate"), "provider_name")
        output[f"watch_{slug}_rent"]     = join_names(entry.get("rent"),     "provider_name")
        output[f"watch_{slug}_buy"]      = join_names(entry.get("buy"),      "provider_name")
        output[f"watch_{slug}_free"]     = join_names(entry.get("free"),     "provider_name")
        output[f"watch_{slug}_link"]     = entry.get("link")

    return output


def content_ratings_flat(
    raw:       dict | None,
    countries: list[str],
) -> dict:
    """
    Flatten the television ``content_ratings`` response into per-country
    certification columns (for example ``cert_us = 'TV-MA'``).
    """
    output: dict = {}
    results = (raw or {}).get("results") or []

    rating_map = {
        entry["iso_3166_1"]: entry.get("rating")
        for entry in results
        if entry.get("iso_3166_1")
    }

    for country in countries:
        slug = country.lower()
        output[f"cert_{slug}"] = rating_map.get(country) or None

    return output


def theatrical_certification(raw: dict | None, country: str = "US") -> str | None:
    """
    Extract the theatrical certification (type 3) for a single country
    from a movie's ``release_dates`` payload.
    """
    for release in (raw or {}).get("results", []):
        if release.get("iso_3166_1") != country:
            continue
        for entry in release.get("release_dates", []):
            if entry.get("type") == 3:
                return entry.get("certification") or None
    return None
