# Schema reference

This document describes every column in the seven CSV files produced by
the pipeline. All files are encoded as UTF-8 with BOM for Excel
compatibility. Lists (cast, genres, IDs) are stored as comma-separated
strings within a single cell.

---

## `movies.csv` — 55 columns

One row per movie.

| Column | Type | Description | Example |
|---|---|---|---|
| `tmdb_id` | int | Unique TMDB movie identifier | `603` |
| `imdb_id` | str | IMDb identifier | `tt0133093` |
| `title` | str | English display title | `The Matrix` |
| `original_title` | str | Native-language title | `The Matrix` |
| `original_language` | str | ISO 639-1 code | `en` |
| `alternative_titles` | str | Alternative titles `CC:Title` separated by ` \| ` | `TR:Matriks \| DE:Matrix` |
| `tagline` | str | Promotional tagline | `Welcome to the Real World` |
| `overview` | str | English synopsis | `A computer hacker learns...` |
| `release_date` | str | First release date (YYYY-MM-DD) | `1999-03-31` |
| `release_year` | int | Release year | `1999` |
| `runtime_min` | int | Runtime in minutes | `136` |
| `status` | str | Release status | `Released` |
| `vote_average` | float | TMDB user rating (0-10) | `8.2` |
| `vote_count` | int | Total number of votes | `24000` |
| `popularity` | float | TMDB popularity score | `47.3` |
| `budget_usd` | float | Production budget (USD, null if unknown) | `63000000` |
| `revenue_usd` | float | Box-office revenue (USD, null if unknown) | `467000000` |
| `profit_usd` | float | `revenue_usd - budget_usd` | `404000000` |
| `roi_pct` | float | Return on investment percentage | `641.3` |
| `genres` | str | Genre names, comma-separated | `Action, Science Fiction` |
| `keywords` | str | TMDB keywords, comma-separated | `dystopia, artificial intelligence` |
| `us_certification` | str | US theatrical certification (type 3) | `R` |
| `production_companies` | str | Production companies | `Warner Bros., Village Roadshow` |
| `production_countries` | str | ISO 3166-1 country codes | `US, AU` |
| `spoken_languages` | str | Languages spoken in the film | `English, Japanese` |
| `collection_id` | int | TMDB collection/franchise ID | `2344` |
| `collection_name` | str | Franchise name | `The Matrix Collection` |
| `cast_names` | str | Top 15 cast member names | `Keanu Reeves, Laurence Fishburne` |
| `cast_ids` | str | Top 15 cast TMDB IDs (joins to `people.tmdb_id`) | `6384, 2975` |
| `cast_characters` | str | Characters played | `Neo, Morpheus` |
| `directors` | str | Director names | `Lana Wachowski, Lilly Wachowski` |
| `director_ids` | str | Director TMDB IDs | `9340, 9341` |
| `writers` | str | Writing credits (up to 5) | `Lana Wachowski` |
| `producers` | str | Top 3 producers | `Joel Silver` |
| `composers` | str | Top 2 composers | `Don Davis` |
| `has_trailer` | bool | Whether a YouTube trailer exists | `True` |
| `trailer_url` | str | First trailer URL | `https://youtube.com/watch?v=vKQi3bBA1y8` |
| `similar_ids` | str | Top 5 similar-movie TMDB IDs | `604, 605` |
| `similar_titles` | str | Top 5 similar-movie titles | `The Matrix Reloaded, ...` |
| `recommended_ids` | str | Top 5 recommended TMDB IDs | `78, 680` |
| `recommended_titles` | str | Top 5 recommended titles | `Pulp Fiction, ...` |
| `poster_url` | str | Poster URL (w500 size) | `https://image.tmdb.org/t/p/w500/...` |
| `poster_url_hd` | str | Poster URL (original size) | `https://image.tmdb.org/t/p/original/...` |
| `backdrop_url` | str | Backdrop URL (w780 size) | `https://image.tmdb.org/t/p/w780/...` |
| `homepage` | str | Official website | `https://www.whatisthematrix.com` |
| `watch_tr_flatrate` | str | Turkish subscription services | `Netflix, Amazon Prime` |
| `watch_tr_rent` | str | Turkish rental services | `Apple TV` |
| `watch_tr_buy` | str | Turkish purchase services | `Google Play Movies` |
| `watch_tr_free` | str | Turkish ad-supported services | `null` |
| `watch_tr_link` | str | TMDB Turkish watch page | `https://www.themoviedb.org/movie/603/watch?locale=TR` |
| `watch_us_flatrate` | str | US subscription services | `Netflix` |
| `watch_us_rent` | str | US rental services | `Amazon Video` |
| `watch_us_buy` | str | US purchase services | `Vudu` |
| `watch_us_free` | str | US ad-supported services | `null` |
| `watch_us_link` | str | TMDB US watch page | `https://www.themoviedb.org/movie/603/watch?locale=US` |

---

## `tv_shows.csv` — 55 columns

One row per series.

| Column | Type | Description |
|---|---|---|
| `tmdb_id` | int | Unique TMDB series identifier |
| `imdb_id` | str | IMDb identifier |
| `tvdb_id` | int | TheTVDB identifier |
| `title` | str | English series name |
| `original_title` | str | Native-language series name |
| `original_language` | str | ISO 639-1 code |
| `alternative_titles` | str | Alternative titles |
| `tagline` | str | Promotional tagline |
| `overview` | str | English synopsis |
| `first_air_date` | str | Date of first episode |
| `last_air_date` | str | Date of last aired episode |
| `release_year` | int | Year of first air date |
| `status` | str | `Ended`, `Returning Series`, `Canceled`, etc. |
| `in_production` | bool | Actively producing new episodes |
| `show_type` | str | `Scripted`, `Reality`, `Documentary`, `Talk Show`, etc. |
| `number_of_seasons` | int | Total season count |
| `number_of_episodes` | int | Total episode count |
| `avg_episode_runtime` | int | Mean episode runtime (minutes) |
| `season_count` | int | Season count excluding specials (season 0) |
| `vote_average` | float | User rating (0-10) |
| `vote_count` | int | Total votes |
| `popularity` | float | TMDB popularity score |
| `genres` | str | Genre names |
| `keywords` | str | TMDB keywords |
| `networks` | str | Broadcasting networks |
| `network_ids` | str | Network TMDB IDs |
| `origin_countries` | str | Country of origin codes |
| `spoken_languages` | str | Languages spoken on air |
| `production_companies` | str | Production companies |
| `creators` | str | Creator names |
| `creator_ids` | str | Creator TMDB IDs |
| `cast_names` | str | Top 15 cast member names |
| `cast_ids` | str | Top 15 cast TMDB IDs |
| `cast_characters` | str | Characters played |
| `writers` | str | Writing department credits |
| `similar_ids` | str | Top 5 similar-series IDs |
| `similar_titles` | str | Top 5 similar-series names |
| `recommended_ids` | str | Top 5 recommended series IDs |
| `recommended_titles` | str | Top 5 recommended series names |
| `poster_url` | str | Poster URL (w500) |
| `poster_url_hd` | str | Poster URL (original) |
| `backdrop_url` | str | Backdrop URL (w780) |
| `homepage` | str | Official website |
| `watch_tr_flatrate` / `_rent` / `_buy` / `_free` / `_link` | str | Turkish watch availability |
| `watch_us_flatrate` / `_rent` / `_buy` / `_free` / `_link` | str | US watch availability |
| `cert_tr` | str | Turkish content rating (for example `18+`) |
| `cert_us` | str | US content rating (for example `TV-MA`) |

---

## `people.csv` — 24 columns

One row per person (actor, director, producer, etc.).

| Column | Type | Description |
|---|---|---|
| `tmdb_id` | int | Unique TMDB person identifier |
| `imdb_id` | str | IMDb person identifier |
| `instagram_id` | str | Instagram handle |
| `twitter_id` | str | Twitter/X handle |
| `name` | str | Full name |
| `also_known_as` | str | Aliases / transliterations, comma-separated |
| `gender` | str | `Male`, `Female`, `Non-binary`, `Unspecified` |
| `birthday` | str | Date of birth (YYYY-MM-DD) |
| `deathday` | str | Date of death, null if living |
| `place_of_birth` | str | Birthplace |
| `known_for_dept` | str | Primary department (`Acting`, `Directing`, ...) |
| `biography` | str | Biographical text, HTML-cleaned |
| `popularity` | float | TMDB popularity score |
| `known_movies` | str | Top 15 movie roles by popularity |
| `known_movie_ids` | str | Corresponding TMDB movie IDs |
| `total_movie_credits` | int | Count of all movie cast credits |
| `directed_movies` | str | Top 8 directed movies |
| `directed_movie_ids` | str | Corresponding TMDB movie IDs |
| `total_directed` | int | Count of all director credits |
| `known_tv_shows` | str | Top 10 TV roles by popularity |
| `known_tv_ids` | str | Corresponding TMDB TV IDs |
| `total_tv_credits` | int | Count of all TV cast credits |
| `profile_url` | str | Profile photo URL (h632 size) |
| `homepage` | str | Personal website |

---

## `orphan_movies.csv` — 10 columns (lightweight)

Movies that appear in the recommendation graph of the primary corpus but
are not themselves primary records. Only essential fields are captured.

| Column | Type |
|---|---|
| `tmdb_id` | int |
| `imdb_id` | str |
| `title` | str |
| `original_language` | str |
| `release_year` | int |
| `overview` | str |
| `genres` | str |
| `vote_average` | float |
| `vote_count` | int |
| `poster_url` | str |

---

## `orphan_tv.csv` — 9 columns (lightweight)

Same shape as `orphan_movies.csv` without the `imdb_id` column.

---

## `movie_reviews.csv` and `tv_reviews.csv` — 8 columns

One row per user review.

| Column | Type | Description |
|---|---|---|
| `review_id` | str | TMDB review identifier |
| `tmdb_id` | int | Parent movie or TV show ID (foreign key) |
| `media_type` | str | `movie` or `tv` |
| `author` | str | Author username |
| `rating` | float | Author's 0-10 rating, null if absent |
| `content` | str | Review body, HTML-cleaned, capped at 3000 characters |
| `created_at` | str | ISO 8601 timestamp |
| `url` | str | Review permalink on TMDB |

---

## Relationships

```text
movies.cast_ids          → people.tmdb_id                 (N:N)
movies.director_ids      → people.tmdb_id                 (N:N)
movies.similar_ids       → movies.tmdb_id ∪ orphan_movies (N:N)
movies.recommended_ids   → movies.tmdb_id ∪ orphan_movies (N:N)

tv_shows.cast_ids        → people.tmdb_id                 (N:N)
tv_shows.creator_ids     → people.tmdb_id                 (N:N)
tv_shows.similar_ids     → tv_shows.tmdb_id ∪ orphan_tv   (N:N)
tv_shows.recommended_ids → tv_shows.tmdb_id ∪ orphan_tv   (N:N)

movie_reviews.tmdb_id    → movies.tmdb_id                 (N:1)
tv_reviews.tmdb_id       → tv_shows.tmdb_id               (N:1)

people.known_movie_ids   → movies.tmdb_id ∪ orphan_movies (N:N)
people.known_tv_ids      → tv_shows.tmdb_id ∪ orphan_tv   (N:N)
people.directed_movie_ids → movies.tmdb_id ∪ orphan_movies (N:N)
```

All relationships are expressed as comma-separated IDs inside a single
string cell. Use a helper such as `cinegraph.processing.parsers.parse_id_list`
to turn them back into integers.
