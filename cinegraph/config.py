"""
Central configuration for the cinegraph pipeline.

All tunable parameters live here. The TMDB access token is loaded from an
environment variable (or a local .env file) to keep secrets out of source
control.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _load_env_file(env_path: Path) -> None:
    """Minimal .env loader — parses KEY=VALUE lines, ignores comments."""
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        # Do not override already-set environment variables.
        os.environ.setdefault(key, value)


# Look for .env at the project root (two levels above this file).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
# print(f"DEBUG: .env aranan dizin: {_PROJECT_ROOT}")
_load_env_file(_PROJECT_ROOT / ".env")


@dataclass
class Settings:
    # ──────────────────────────────────────────────────────────────
    # AUTHENTICATION
    # ──────────────────────────────────────────────────────────────
    # Bearer token obtained from https://www.themoviedb.org/settings/api
    # Set via environment variable TMDB_ACCESS_TOKEN or the .env file.
    access_token: str = field(
        default_factory=lambda: os.environ.get("TMDB_ACCESS_TOKEN", "")
    )

    # ──────────────────────────────────────────────────────────────
    # DISCOVERY — PAGE LIMITS
    # TMDB caps list endpoints at 500 pages. The pipeline stops earlier
    # if it exhausts results or encounters repeated empty pages.
    # ──────────────────────────────────────────────────────────────
    movie_pages: int = 500
    tv_pages: int = 500
    movie_genre_pages: int = 500
    tv_genre_pages: int = 500

    # ──────────────────────────────────────────────────────────────
    # QUALITY FILTERS
    # Vote count thresholds separate well-documented content from
    # sparsely-cataloged or placeholder records.
    # ──────────────────────────────────────────────────────────────
    # Minimum vote_count for inclusion via genre discovery.
    movie_min_votes: int = 200
    tv_min_votes: int = 20

    # ──────────────────────────────────────────────────────────────
    # PEOPLE COLLECTION STRATEGY
    # People are collected by reference: a person is fetched only if they
    # appear in the cast, director, or creator list of at least N titles.
    # This favors actual contributors over single-appearance extras.
    # ──────────────────────────────────────────────────────────────
    person_min_refs: int = 2

    # ──────────────────────────────────────────────────────────────
    # RECOMMENDATION GRAPH
    # Each title stores the top N similar and recommended titles.
    # IDs appearing in these lists but outside the primary universe are
    # captured in a lightweight "orphan" table to preserve graph coverage.
    # ──────────────────────────────────────────────────────────────
    similar_count: int = 5
    recommended_count: int = 5

    # Vote thresholds for orphan inclusion. Derived empirically:
    # movies show a peak around 50-99 votes, so 20 captures meaningful
    # content while filtering noise; television votes are naturally much
    # lower, so the threshold is set at 1 to exclude placeholder records.
    orphan_movie_min_votes: int = 20
    orphan_tv_min_votes: int = 1

    # ──────────────────────────────────────────────────────────────
    # WATCH PROVIDERS
    # ISO 3166-1 country codes for which streaming availability is
    # recorded. Provider data is sourced via JustWatch through TMDB.
    # ──────────────────────────────────────────────────────────────
    watch_countries: list = field(default_factory=lambda: ["TR", "US"])

    # ──────────────────────────────────────────────────────────────
    # CONCURRENCY
    # TMDB's CDN allows up to 50 requests/second and 20 simultaneous
    # connections per IP. Ten threads with a 40 ms delay between
    # requests stays well inside these limits.
    # ──────────────────────────────────────────────────────────────
    threads: int = 10
    request_delay: float = 0.04

    # Stop paginating an endpoint after this many consecutive empty or
    # duplicate pages.
    empty_page_tolerance: int = 3

    # ──────────────────────────────────────────────────────────────
    # OUTPUT
    # ──────────────────────────────────────────────────────────────
    output_dir: str = "data"
    log_dir: str = "logs"


# Single shared instance used throughout the package.
settings = Settings()
