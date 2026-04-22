# Data directory

This directory is the default destination for pipeline output. Seven CSV
files are written here by `scripts/run_pipeline.py`:

| File | Description |
|---|---|
| `movies.csv` | Full movie metadata |
| `tv_shows.csv` | Full television metadata |
| `people.csv` | Reference-driven person profiles |
| `orphan_movies.csv` | Lightweight movie records from the recommendation graph |
| `orphan_tv.csv` | Lightweight TV records from the recommendation graph |
| `movie_reviews.csv` | User reviews for movies |
| `tv_reviews.csv` | User reviews for TV shows |

Schema details: see [`docs/SCHEMA.md`](../docs/SCHEMA.md).

CSV files are excluded from version control via `.gitignore`. Publish
releases by uploading the built dataset to a release asset or to a
dataset platform (for example, Hugging Face Datasets or Kaggle).
