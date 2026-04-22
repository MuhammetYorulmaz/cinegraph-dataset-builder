"""
Dataset validation utility.

Loads every CSV produced by the pipeline and prints a concise integrity
report:

    * Row counts and column counts per table
    * Primary-key uniqueness
    * Null rates for critical columns
    * Join coverage across cast/people and recommendation graphs

Usage
-----
    python scripts/validate_dataset.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from cinegraph.config import settings
from cinegraph.processing.parsers import parse_id_list


CRITICAL_COLUMNS = {
    "movies":   ["title", "overview", "genres", "cast_names", "directors"],
    "tv_shows": ["title", "overview", "genres", "cast_names", "creators"],
    "people":   ["name", "biography", "known_for_dept"],
}


def _load(name: str) -> pd.DataFrame:
    path = Path(settings.output_dir) / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8-sig", low_memory=False)


def _pct(count: int, total: int) -> str:
    return f"{count / total * 100:5.1f}%" if total else "    —"


def main() -> None:
    print("\n" + "=" * 70)
    print(" DATASET VALIDATION")
    print("=" * 70)

    tables = {
        "movies":         _load("movies.csv"),
        "tv_shows":       _load("tv_shows.csv"),
        "people":         _load("people.csv"),
        "orphan_movies":  _load("orphan_movies.csv"),
        "orphan_tv":      _load("orphan_tv.csv"),
        "movie_reviews":  _load("movie_reviews.csv"),
        "tv_reviews":     _load("tv_reviews.csv"),
    }

    # Size summary
    print("\n[1] Table sizes")
    print(f"    {'Table':<18} {'Rows':>10} {'Cols':>6}")
    print(f"    {'-' * 18} {'-' * 10} {'-' * 6}")
    for name, frame in tables.items():
        rows = len(frame)
        cols = frame.shape[1] if not frame.empty else 0
        print(f"    {name:<18} {rows:>10,} {cols:>6}")

    # Primary key uniqueness
    print("\n[2] Primary key uniqueness")
    pk_map = {
        "movies":        "tmdb_id",
        "tv_shows":      "tmdb_id",
        "people":        "tmdb_id",
        "orphan_movies": "tmdb_id",
        "orphan_tv":     "tmdb_id",
        "movie_reviews": "review_id",
        "tv_reviews":    "review_id",
    }
    for name, pk in pk_map.items():
        frame = tables[name]
        if frame.empty or pk not in frame.columns:
            continue
        duplicates = len(frame) - frame[pk].nunique()
        status = "✓" if duplicates == 0 else "✗"
        print(f"    {status} {name:<18} {pk}: {duplicates} duplicates")

    # Critical nulls
    print("\n[3] Null rates in critical columns")
    for table, columns in CRITICAL_COLUMNS.items():
        frame = tables.get(table, pd.DataFrame())
        if frame.empty:
            continue
        print(f"    {table}")
        for column in columns:
            if column not in frame.columns:
                print(f"      ! {column}: column missing")
                continue
            null_pct = frame[column].isna().mean() * 100
            print(f"      · {column:<18} {null_pct:5.1f}%")

    # Join coverage
    movies = tables["movies"]
    tv = tables["tv_shows"]
    people = tables["people"]

    if not people.empty:
        people_ids = set(people["tmdb_id"].dropna().astype(int))

        def _coverage(frame: pd.DataFrame, column: str) -> str:
            if frame.empty or column not in frame.columns:
                return "—"
            all_ids: set[int] = set()
            for value in frame[column]:
                all_ids.update(parse_id_list(value))
            if not all_ids:
                return "—"
            return _pct(len(all_ids & people_ids), len(all_ids))

        print("\n[4] Join coverage (references → people.csv)")
        print(f"    movies.cast_ids       → people : {_coverage(movies, 'cast_ids')}")
        print(f"    movies.director_ids   → people : {_coverage(movies, 'director_ids')}")
        print(f"    tv_shows.cast_ids     → people : {_coverage(tv,     'cast_ids')}")
        print(f"    tv_shows.creator_ids  → people : {_coverage(tv,     'creator_ids')}")

    # Recommendation graph coverage
    if not movies.empty:
        main_u = set(movies["tmdb_id"].dropna().astype(int))
        orphan_u = (
            set(tables["orphan_movies"]["tmdb_id"].dropna().astype(int))
            if not tables["orphan_movies"].empty else set()
        )
        combined = main_u | orphan_u

        for column in ("similar_ids", "recommended_ids"):
            total_refs = 0
            hits_main = 0
            hits_all = 0
            for value in movies.get(column, []):
                ids = parse_id_list(value)
                total_refs += len(ids)
                hits_main += sum(1 for i in ids if i in main_u)
                hits_all  += sum(1 for i in ids if i in combined)
            if total_refs:
                print(
                    f"[5] movies.{column}: main={_pct(hits_main, total_refs)}, "
                    f"main+orphan={_pct(hits_all, total_refs)}"
                )

    print("\n" + "=" * 70)
    print(" Validation complete")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
