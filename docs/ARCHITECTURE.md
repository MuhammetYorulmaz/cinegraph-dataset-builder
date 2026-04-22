# Architecture

This document explains *why* the pipeline is structured the way it is.
The focus is on the design decisions that shape output quality and on
the guarantees each component provides.

---

## Goals and constraints

The pipeline has three explicit goals.

1. **Produce a self-consistent dataset.** Every foreign-key reference
   (cast, director, similar title) should resolve to an actual row in
   another table when possible.
2. **Capture the right people, not the popular ones.** A person who
   appears in titles we collected is more useful to downstream tasks
   than a person who happens to be trending globally.
3. **Stay inside TMDB rate limits without a throttling framework.** Ten
   concurrent threads with a 40-millisecond delay between requests keep
   the pipeline comfortably below the 50-requests-per-second CDN limit.

Two constraints drive the implementation.

* **TMDB caps list endpoints at 500 pages** (roughly 10,000 results per
  endpoint). Broad coverage therefore requires multiple endpoints.
* **TMDB's `person/popular` endpoint is unrelated to the films you
  happen to be collecting.** Fetching the 10,000 "most popular" people
  in the world produces a low-quality join: roughly 94% of cast IDs in
  the movie corpus will not resolve.

---

## Six-phase execution model

### Phase 0 — ID discovery

Collected from two source types:

* **Curated lists.** `popular`, `top_rated`, `now_playing`,
  `upcoming` for movies; `popular`, `top_rated`, `on_the_air`,
  `airing_today` for TV.
* **Genre-based discovery.** One sweep per genre with
  `sort=vote_count.desc`, filtered by a minimum vote count
  (`movie_min_votes = 200`, `tv_min_votes = 20`).

Identifiers are kept in a `set`, so duplicates across endpoints are
removed automatically. Pagination stops early once three consecutive
empty or duplicate pages are encountered, which saves a large number
of requests at the tail of each endpoint.

### Phase 1 — Core fetch

Each ID is expanded with one request using `append_to_response` so that
credits, keywords, videos, release dates, related titles, alternative
titles, and watch providers arrive together. The rate of one API call
per title (versus seven) is what keeps the full run under two hours.

The response is flattened into a wide row. Lists (cast, genres, IDs)
are serialized as comma-separated strings so that the output remains a
plain CSV without relational splits.

### Phase 2 — Reference extraction

Once movies and TV rows are materialized, two derived sets are built
from them.

* **Person references.** The fetcher already records `cast_ids`,
  `director_ids`, and `creator_ids` for every title. These are
  aggregated into a frequency counter. People who appear at least
  `person_min_refs = 2` times across the whole corpus move on to
  Phase 3; singletons are skipped as likely background extras.
* **Orphan references.** Every title stores the top 5 similar and
  recommended IDs. Any such ID missing from the primary universe is
  a candidate for lightweight capture in Phase 4.

### Phase 3 — People

Each selected person is fetched individually through `person/{id}`
with `movie_credits`, `tv_credits`, and `external_ids` appended. The
resulting `people.csv` is therefore guaranteed to contain every
frequently-referenced contributor, which produces high practical
coverage for downstream joins.

### Phase 4 — Orphan lite-fetch

Orphan IDs are fetched with no `append_to_response`, then filtered by
vote count:

* Movies: `orphan_movie_min_votes = 20`.
* TV: `orphan_tv_min_votes = 1`.

The two thresholds are not arbitrary — they come from a distribution
study of 500 random orphan titles from each media type. Movie orphans
cluster between 20 and 200 votes (peak at 50-99); TV orphans are
concentrated between 0 and 20 with a natural break at 1, where 0-vote
entries are almost always placeholder records.

Only ten columns are stored per orphan movie and nine per orphan TV —
enough to resolve a recommendation without paying the full-fetch cost.

### Phase 5 — Reviews

Only primary titles receive reviews. Orphans are intentionally skipped
because review density at that end of the tail is under 2%, so the
additional traffic would add hours for marginal benefit.

TMDB review responses are paginated per title. The fetcher walks every
page, drops empty bodies, strips HTML, and caps content at 3000
characters so that a single verbose review cannot dominate storage.

---

## Design decisions worth calling out

### Reference-driven people collection

The `person/popular` endpoint is popular-contributor-driven, not
corpus-driven. Using it to populate `people.csv` produces a dataset
where the *world's* most popular actors are present but the ones who
appear in *your* films are not. The pipeline inverts the direction:
films come first, and the person set is computed from what those films
reference.

The frequency threshold (`person_min_refs = 2`) is a deliberate
trade-off. A minimum of 1 would pull in every single-title extra and
double the person table; a minimum of 3 would drop genuine supporting
actors. Two appearances is the empirical sweet spot: it keeps name
actors while excluding the long tail of background credits.

### Two-tier media model

The `orphan_*` tables exist because a recommendation-heavy use case
(for example, "titles similar to `X`") needs every referenced ID to
resolve, even if the target title was not interesting enough to fetch
in full. Without orphan records, roughly half of `similar_ids`
references would point nowhere.

Orphans use a reduced schema because the absence of full metadata is
the point: they are "this title exists, here's its gist" placeholders
that keep the recommendation graph closed.

### Data-driven vote thresholds

Thresholds for `movie_min_votes`, `tv_min_votes`,
`orphan_movie_min_votes`, and `orphan_tv_min_votes` were chosen after
measuring the actual vote distribution of sample IDs — not guessed.
The distribution shapes for movies and TV differ substantially, which
is why the two media types are configured independently.

### Schema preservation over compactness

The CSV writer never drops a column for being entirely null. A missing
field is valuable information — it signals that the upstream fetcher
did not populate it — and silently omitting the column would hide
genuine regressions. Instead, an empty column produces a warning in
the log and stays in the file.

---

## Concurrency model

All network-bound work runs under `ThreadPoolExecutor` with ten
workers. Each task is a single HTTP call (for detail fetches) or a
short paginated walk (for list endpoints and reviews). Threads share
the `requests.Session` instance in `api/client.py`, which reuses TCP
connections for throughput.

The one global lock is a `threading.Lock` used only to append finished
rows to the shared result list — a trivial section of code that
executes in microseconds.

Failures are absorbed per task: a returning `None` from the fetcher
increments the "failure" counter but does not stop the phase. Retry
logic (four attempts with increasing backoff, explicit handling of HTTP
429 and 5xx) lives in `api_get` itself.

---

## Output directory contract

After a successful run, the `data/` directory contains exactly seven
files:

```
data/
├── movies.csv          # 55 columns
├── tv_shows.csv        # 55 columns
├── people.csv          # 24 columns
├── orphan_movies.csv   # 10 columns
├── orphan_tv.csv       #  9 columns
├── movie_reviews.csv   #  8 columns
└── tv_reviews.csv      #  8 columns
```

The number of rows varies with TMDB's state at fetch time, but the
column set for each file is fixed and documented in
[`SCHEMA.md`](SCHEMA.md). Downstream code can rely on that contract.
