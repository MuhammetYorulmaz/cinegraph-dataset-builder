"""
Reference extraction.

After movies and TV shows have been fetched in detail, this module walks
the fetched rows to derive two downstream input sets:

    1. Person IDs worth fetching (those referenced at least N times as
       cast, director, or creator across the corpus).
    2. Orphan movie/TV IDs — identifiers appearing in ``similar_ids`` or
       ``recommended_ids`` but missing from the primary universe.

This reference-driven approach is what distinguishes the pipeline from a
naive "fetch the most popular N people" strategy: it guarantees that
downstream people data is relevant to the titles actually collected.
"""

from __future__ import annotations

from collections import Counter

from cinegraph.config import settings
from cinegraph.processing.parsers import parse_id_list
from cinegraph.utils.logging import log


def extract_person_ids(
    movie_rows: list[dict],
    tv_rows:    list[dict],
    min_refs:   int | None = None,
) -> set[int]:
    """
    Return person IDs appearing at least ``min_refs`` times across the
    cast and crew columns of both movies and TV shows.
    """
    if min_refs is None:
        min_refs = settings.person_min_refs

    counter: Counter = Counter()

    for row in movie_rows:
        for column in ("cast_ids", "director_ids"):
            for person_id in parse_id_list(row.get(column)):
                counter[person_id] += 1

    for row in tv_rows:
        for column in ("cast_ids", "creator_ids"):
            for person_id in parse_id_list(row.get(column)):
                counter[person_id] += 1

    total_unique = len(counter)
    selected = {pid for pid, count in counter.items() if count >= min_refs}
    excluded = total_unique - len(selected)

    log.info("─" * 60)
    log.info("Person reference extraction")
    log.info("─" * 60)
    log.info(f"  Unique people referenced : {total_unique:,}")
    log.info(f"  Frequency distribution:")
    distribution = Counter(counter.values())
    for threshold in sorted(distribution.keys())[:6]:
        log.info(f"    seen {threshold:>2}×   : {distribution[threshold]:>6,} people")
    log.info(f"  Threshold applied        : seen ≥ {min_refs} times")
    log.info(f"    Will fetch             : {len(selected):,}")
    log.info(f"    Excluded               : {excluded:,}")

    return selected


def extract_orphan_ids(
    rows:     list[dict],
    universe: set[int],
    columns:  tuple[str, ...] = ("similar_ids", "recommended_ids"),
) -> set[int]:
    """
    Return identifiers that appear in the recommendation columns of
    ``rows`` but are absent from ``universe``.
    """
    references: set[int] = set()
    for row in rows:
        for column in columns:
            for reference_id in parse_id_list(row.get(column)):
                references.add(reference_id)

    orphans = references - universe

    log.info("─" * 60)
    log.info("Orphan reference extraction")
    log.info("─" * 60)
    log.info(f"  Total unique references   : {len(references):,}")
    log.info(f"  Already in universe       : {len(references & universe):,}")
    log.info(f"  Orphans (needs lite-fetch): {len(orphans):,}")

    return orphans
