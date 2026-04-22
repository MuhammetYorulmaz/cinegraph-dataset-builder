"""
Parallel execution helpers.

Wraps :class:`concurrent.futures.ThreadPoolExecutor` with uniform
progress logging so that every long-running fetch step reports to the
same log stream in the same format.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from typing import Callable

from cinegraph.config import settings
from cinegraph.utils.logging import log


_lock = Lock()


def bulk_fetch(
    ids:      set[int] | list[int],
    fetch_fn: Callable[[int], dict | None],
    label:    str,
) -> list[dict]:
    """
    Execute ``fetch_fn`` concurrently for each ID and collect the results.

    Parameters
    ----------
    ids:
        Identifiers to process. Order is not preserved.
    fetch_fn:
        Callable receiving one ID and returning a dict row or ``None``.
    label:
        Human-readable name used in progress log lines.

    Returns
    -------
    list[dict]
        The non-null rows returned by ``fetch_fn`` in completion order.
    """
    id_list = list(ids)
    total = len(id_list)
    results: list[dict] = []
    success = failure = 0

    log.info("─" * 60)
    log.info(f"Fetching {total:,} {label} records ({settings.threads} threads)")
    log.info("─" * 60)

    with ThreadPoolExecutor(max_workers=settings.threads) as executor:
        futures = {executor.submit(fetch_fn, identifier): identifier for identifier in id_list}
        done = 0

        for future in as_completed(futures):
            done += 1
            try:
                row = future.result()
                if row:
                    with _lock:
                        results.append(row)
                    success += 1
                else:
                    failure += 1
            except Exception as exc:
                failure += 1
                log.debug(f"Future error: {exc}")

            if done % 200 == 0 or done == total:
                log.info(
                    f"  {label}: {done:>7,}/{total:,}  "
                    f"({done / total * 100:5.1f}%)  "
                    f"✓{success:,}  ✗{failure}"
                )

    log.info(f"{label} done — {success:,} succeeded, {failure} dropped/failed")
    return results


def bulk_fetch_reviews(
    ids:        set[int] | list[int],
    media_type: str,
    fetch_fn:   Callable[[int, str], list[dict]],
) -> list[dict]:
    """Execute the review fetcher concurrently across many IDs."""
    label = f"{media_type} reviews"
    id_list = list(ids)
    total = len(id_list)
    results: list[dict] = []
    done = 0

    log.info("─" * 60)
    log.info(f"Fetching reviews for {total:,} {media_type} titles")
    log.info("─" * 60)

    with ThreadPoolExecutor(max_workers=settings.threads) as executor:
        futures = {
            executor.submit(fetch_fn, identifier, media_type): identifier
            for identifier in id_list
        }

        for future in as_completed(futures):
            done += 1
            try:
                rows = future.result()
                if rows:
                    with _lock:
                        results.extend(rows)
            except Exception as exc:
                log.debug(f"Review future error: {exc}")

            if done % 500 == 0 or done == total:
                log.info(
                    f"  {label}: {done:>7,}/{total:,}  "
                    f"({done / total * 100:5.1f}%)  "
                    f"reviews={len(results):,}"
                )

    log.info(f"{label} done — {len(results):,} reviews")
    return results
