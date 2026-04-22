# 🎬 CineGraph — TMDB Movies, TV & People Dataset (2026 Edition)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TMDB](https://img.shields.io/badge/Source-TMDB%20API-01B4E4)](https://www.themoviedb.org/)
[![Format](https://img.shields.io/badge/Format-CSV%20UTF--8%20BOM-green)](.)

A structured TMDB dataset builder for film, television, and biographical
content — designed as the input layer for analytics, recommendation,
and retrieval-augmented generation workloads.

The pipeline produces seven normalized CSV files covering **22k+
movies, 15k+ TV shows, 58k+ people, and 25k+ user reviews**, with full
foreign-key integrity between cast, creators, and recommendation
graphs.

---

## Why this project exists

Most public film datasets are either thin (title, year, rating), stale
(snapshots from years ago), or structurally disconnected (IDs don't
resolve across tables). cinegraph addresses all three:

- **Breadth** — curated lists plus genre-based discovery across 19
  movie genres and 16 TV genres.
- **Currency** — every run pulls live data from the TMDB API.
- **Integrity** — people are fetched by reference, not by global
  popularity, so the cast and director IDs embedded in `movies.csv`
  actually resolve in `people.csv` the vast majority of the time.
  Similarly, titles referenced by the recommendation graph but absent
  from the primary corpus are captured as lightweight "orphan" records
  so that recommendation edges don't dangle.

---

## Output

Seven CSV files, roughly 160 MB in total when the full corpus is
collected:

| File | Typical rows | Columns | Purpose |
|---|---|---|---|
| `movies.csv` | ~22,000 | 55 | Primary movie corpus, full metadata |
| `tv_shows.csv` | ~16,000 | 55 | Primary TV corpus, full metadata |
| `people.csv` | ~58,000 | 24 | Reference-driven person profiles |
| `orphan_movies.csv` | ~8,500 | 10 | Lightweight records from the recommendation graph |
| `orphan_tv.csv` | ~3,000 | 9 | Same idea for television |
| `movie_reviews.csv` | ~22,000 | 8 | User reviews for movies |
| `tv_reviews.csv` | ~3,000 | 8 | User reviews for TV shows |

Full column-by-column reference in [`docs/SCHEMA.md`](docs/SCHEMA.md).

---

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your TMDB API token
Create a new file named `.env` in the root directory of the project and paste your token inside:

TMDB_API_KEY=your_token_here

# 3. Run the pipeline
python scripts/run_pipeline.py

# 4. Validate the output
python scripts/validate_dataset.py
```

A TMDB API Read Access Token is available for free at
[themoviedb.org/settings/api](https://www.themoviedb.org/settings/api).

### Runtime

Expect the full pipeline to take approximately **1.5-2 hours** on a
consumer internet connection. The run is deliberately rate-limited
(10 concurrent threads, 40 ms delay between requests) to stay well
inside TMDB's CDN quotas of 50 requests/second and 20 simultaneous
connections per IP.

---

## Project layout

```
cinegraph/
├── cinegraph/                       # Python package
│   ├── api/client.py                # HTTP client with retry and rate handling
│   ├── discovery/                   # ID discovery (movies, tv, references)
│   ├── fetchers/                    # Per-record detail fetchers
│   ├── processing/                  # Parsers, transforms, CSV writer
│   ├── orchestration/               # Threaded executor + pipeline driver
│   ├── utils/logging.py             # Console + file logging
│   └── config.py                    # Dataclass settings, .env loader
├── scripts/
│   ├── run_pipeline.py              # Entry point
│   └── validate_dataset.py          # Integrity report over the CSVs
├── tests/                           # pytest unit tests
├── notebooks/
│   └── cinegraph_dataset_overview.ipynb       # Visual walk-through of the dataset
├── docs/
│   ├── SCHEMA.md                    # Column-by-column reference
│   └── ARCHITECTURE.md              # Design rationale
├── data/                            # Pipeline output (git-ignored)
├── logs/                            # Run logs (git-ignored)
├── requirements.txt
├── requirements-dev.txt
├── .env
└── .gitignore
```

---

## How the pipeline works

```
Phase 0 — ID discovery
  movies  : popular, top_rated, now_playing, upcoming + 19 genre sweeps
  tv      : popular, top_rated, on_the_air, airing_today + 16 genre sweeps
  Genre discovery uses vote_count thresholds to drop placeholder entries.

Phase 1 — Core fetch (parallel, 10 threads)
  Each ID is expanded with append_to_response so one HTTP call returns
  credits, keywords, videos, release dates, related titles, alternative
  titles, and watch providers together.

Phase 2 — Reference extraction
  The fetched rows are scanned for person IDs (cast, director, creator)
  and for similar/recommended IDs that fall outside the primary universe.
  A frequency filter (≥ 2 appearances) keeps the person set focused on
  genuine contributors rather than one-off extras.

Phase 3 — People fetch
  Every selected person is fetched individually through person/{id} with
  movie_credits, tv_credits, and external_ids appended.

Phase 4 — Orphan lite-fetch
  IDs surfaced by similar/recommended lists that weren't already
  collected are fetched with a minimal schema, subject to a vote-count
  threshold tuned separately for movies and TV (the underlying vote
  distributions differ by roughly an order of magnitude).

Phase 5 — Reviews
  Paginated review fetch for every primary movie and TV title.
  Orphans are intentionally skipped — review density there is under 2%.
```

Detailed design rationale in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## Analysis notebook

A ready-to-run walk-through of the dataset lives at
[`notebooks/dataset_overview.ipynb`](notebooks/dataset_overview.ipynb).
It covers:

1. Loading and schema summary
2. Release-year, language, and genre distributions
3. Watch-provider coverage by country
4. Recommendation-graph integrity with and without orphans
5. Cast / people join integrity
6. Review statistics (per-title density, length, rating)
7. People demographics and practical coverage test
8. Data-quality audit of critical columns

```bash
pip install -r requirements-dev.txt
jupyter notebook notebooks/dataset_overview.ipynb
```

---

## Configuration

All tunable parameters live in [`cinegraph/config.py`](cinegraph/config.py).
The values shipped are production defaults.

| Parameter | Default | Notes |
|---|---|---|
| `movie_pages` / `tv_pages` | 500 | TMDB hard limit per list endpoint |
| `movie_min_votes` | 200 | Genre-discovery vote threshold for movies |
| `tv_min_votes` | 20 | Genre-discovery vote threshold for TV |
| `person_min_refs` | 2 | Minimum appearances for a person to be fetched |
| `similar_count` / `recommended_count` | 5 | Top-N kept per title |
| `orphan_movie_min_votes` | 20 | Quality threshold for orphan movies |
| `orphan_tv_min_votes` | 1 | Quality threshold for orphan TV (votes are naturally lower) |
| `watch_countries` | `["TR", "US"]` | Regions for streaming availability |
| `threads` | 10 | Concurrent fetch workers |

---

## Running the tests

```bash
pip install -r requirements-dev.txt
pytest tests/
```

The suite covers parsing, reference extraction, and the watch-provider
flattening logic.

---

## Attribution

This product uses the TMDB API but is not endorsed or certified by
TMDB. All rights to film, television, and biographical metadata belong
to their respective owners.

---
