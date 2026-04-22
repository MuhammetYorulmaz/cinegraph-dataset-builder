"""
End-to-end pipeline orchestration.

The :func:`run` function drives the full six-phase data collection
sequence:

    0. Discover movie and TV IDs from curated lists and genre endpoints.
    1. Fetch full metadata for every discovered title.
    2. Extract person and orphan IDs from the fetched rows.
    3. Fetch full person records for references that meet the threshold.
    4. Fetch lightweight records for orphan titles surfaced by the
       recommendation graph.
    5. Fetch reviews for the primary movie and TV corpora.
"""

from __future__ import annotations

from datetime import datetime

from cinegraph.config import settings
from cinegraph.discovery.movies import gather_movie_ids
from cinegraph.discovery.references import extract_orphan_ids, extract_person_ids
from cinegraph.discovery.tv import gather_tv_ids
from cinegraph.fetchers.lite import fetch_movie_lite, fetch_tv_lite
from cinegraph.fetchers.movie import fetch_movie
from cinegraph.fetchers.person import fetch_person
from cinegraph.fetchers.review import fetch_reviews
from cinegraph.fetchers.tv import fetch_tv
from cinegraph.orchestration.executor import bulk_fetch, bulk_fetch_reviews
from cinegraph.processing.storage import save_csv
from cinegraph.utils.logging import log


def _banner(step: str, title: str) -> None:
    log.info("")
    log.info("═" * 60)
    log.info(f"  [{step}]  {title}")
    log.info("═" * 60)


def run() -> None:
    """Execute the complete pipeline. CSV files are written as each phase
    completes, so partial progress survives an interrupted run."""
    started_at = datetime.now()

    log.info(
        f"Configuration: person_min_refs={settings.person_min_refs}, "
        f"tv_min_votes={settings.tv_min_votes}, "
        f"orphan_movie_min_votes={settings.orphan_movie_min_votes}, "
        f"orphan_tv_min_votes={settings.orphan_tv_min_votes}"
    )

    # ── Phase 0: ID discovery ───────────────────────────────────────
    _banner("0/5", "ID DISCOVERY")
    movie_ids = gather_movie_ids()
    tv_ids = gather_tv_ids()

    # ── Phase 1: core fetch ────────────────────────────────────────
    _banner("1/5", "CORE FETCH — MOVIES & TV")
    movie_rows = bulk_fetch(movie_ids, fetch_movie, "Movies")
    save_csv(movie_rows, "movies.csv")

    tv_rows = bulk_fetch(tv_ids, fetch_tv, "TV shows")
    save_csv(tv_rows, "tv_shows.csv")

    # ── Phase 2: reference extraction ──────────────────────────────
    _banner("2/5", "REFERENCE EXTRACTION")
    person_ids = extract_person_ids(movie_rows, tv_rows)

    log.info("\nMovie orphan detection")
    movie_universe = {row["tmdb_id"] for row in movie_rows if row.get("tmdb_id")}
    orphan_movie_ids = extract_orphan_ids(movie_rows, movie_universe)

    log.info("\nTV orphan detection")
    tv_universe = {row["tmdb_id"] for row in tv_rows if row.get("tmdb_id")}
    orphan_tv_ids = extract_orphan_ids(tv_rows, tv_universe)

    # ── Phase 3: people ────────────────────────────────────────────
    _banner("3/5", "PEOPLE FETCH")
    log.info(f"Reference-driven selection: {len(person_ids):,} people to fetch")
    person_rows = bulk_fetch(person_ids, fetch_person, "People")
    save_csv(person_rows, "people.csv")

    # ── Phase 4: orphan lite-fetch ─────────────────────────────────
    _banner("4/5", "ORPHAN LITE-FETCH")
    log.info(
        f"Movie orphans: {len(orphan_movie_ids):,} IDs "
        f"(vote_count ≥ {settings.orphan_movie_min_votes})"
    )
    log.info(
        "Note: 'dropped' rows are IDs that failed the vote threshold — "
        "not API failures."
    )
    orphan_movie_rows = bulk_fetch(orphan_movie_ids, fetch_movie_lite, "Orphan movies")
    orphan_movie_rows = [row for row in orphan_movie_rows if row]
    save_csv(orphan_movie_rows, "orphan_movies.csv")

    log.info(
        f"\nTV orphans: {len(orphan_tv_ids):,} IDs "
        f"(vote_count ≥ {settings.orphan_tv_min_votes})"
    )
    orphan_tv_rows = bulk_fetch(orphan_tv_ids, fetch_tv_lite, "Orphan TV")
    orphan_tv_rows = [row for row in orphan_tv_rows if row]
    save_csv(orphan_tv_rows, "orphan_tv.csv")

    # ── Phase 5: reviews ───────────────────────────────────────────
    _banner("5/5", "REVIEWS")
    movie_reviews = bulk_fetch_reviews(movie_ids, "movie", fetch_reviews)
    save_csv(movie_reviews, "movie_reviews.csv")

    tv_reviews = bulk_fetch_reviews(tv_ids, "tv", fetch_reviews)
    save_csv(tv_reviews, "tv_reviews.csv")

    # ── Summary ────────────────────────────────────────────────────
    elapsed = datetime.now() - started_at
    hours = int(elapsed.total_seconds() // 3600)
    minutes = int((elapsed.total_seconds() % 3600) // 60)
    seconds = int(elapsed.total_seconds() % 60)

    log.info("")
    log.info("╔" + "═" * 58 + "╗")
    log.info("║" + "  DATA COLLECTION COMPLETE".center(58) + "║")
    log.info("╠" + "═" * 58 + "╣")
    log.info(f"║  {'movies.csv':<22} {len(movie_rows):>8,} rows".ljust(59) + "║")
    log.info(f"║  {'tv_shows.csv':<22} {len(tv_rows):>8,} rows".ljust(59) + "║")
    log.info(f"║  {'people.csv':<22} {len(person_rows):>8,} rows".ljust(59) + "║")
    log.info(f"║  {'orphan_movies.csv':<22} {len(orphan_movie_rows):>8,} rows".ljust(59) + "║")
    log.info(f"║  {'orphan_tv.csv':<22} {len(orphan_tv_rows):>8,} rows".ljust(59) + "║")
    log.info(f"║  {'movie_reviews.csv':<22} {len(movie_reviews):>8,} rows".ljust(59) + "║")
    log.info(f"║  {'tv_reviews.csv':<22} {len(tv_reviews):>8,} rows".ljust(59) + "║")
    log.info("╠" + "═" * 58 + "╣")
    log.info(f"║  {'Elapsed':<22} {hours}h {minutes}m {seconds}s".ljust(59) + "║")
    log.info(f"║  {'Output directory':<22} {settings.output_dir}/".ljust(59) + "║")
    log.info("╚" + "═" * 58 + "╝")
