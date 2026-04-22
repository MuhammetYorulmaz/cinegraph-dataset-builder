"""
Disk I/O for pipeline outputs.

CSV files are written with a UTF-8 BOM so that Turkish and other
non-ASCII characters display correctly in spreadsheet applications.
Columns that are entirely null are preserved (rather than silently
dropped) so that the schema remains consistent across runs.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from cinegraph.config import settings
from cinegraph.utils.logging import log


def save_csv(rows: list[dict], filename: str) -> None:
    """Persist a list of records as a UTF-8 BOM encoded CSV."""
    if not rows:
        log.warning(f"No rows for '{filename}' — file not written.")
        return

    os.makedirs(settings.output_dir, exist_ok=True)

    frame = pd.DataFrame(rows)

    # Report entirely-null columns but keep them in place so that the
    # schema contract is never weakened by a single incomplete run.
    all_null = [column for column in frame.columns if frame[column].isna().all()]
    if all_null:
        log.warning(
            f"Columns with no data in '{filename}': {all_null} "
            f"(kept for schema consistency)"
        )

    path = Path(settings.output_dir) / filename
    frame.to_csv(path, index=False, encoding="utf-8-sig")
    log.info(f"Wrote {filename:<22} {len(frame):>7,} rows │ {len(frame.columns)} columns")
