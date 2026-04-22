"""
Pipeline entry point.

Usage
-----
    python scripts/run_pipeline.py

Prerequisites
-------------
    * Python 3.10+
    * ``pip install -r requirements.txt``
    * A TMDB API Read Access Token provided via:
        - the ``TMDB_ACCESS_TOKEN`` environment variable, or
        - a local ``.env`` file at the project root.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make the ``cinegraph`` package importable when running as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cinegraph.api.client import validate_token
from cinegraph.config import settings
from cinegraph.orchestration.pipeline import run
from cinegraph.utils.logging import log


def main() -> None:
    if not settings.access_token or len(settings.access_token) < 100:
        log.error(
            "TMDB access token is missing or appears invalid.\n"
            "  → Copy .env.example to .env and fill in TMDB_ACCESS_TOKEN, or\n"
            "  → Export TMDB_ACCESS_TOKEN in your shell."
        )
        sys.exit(1)

    log.info("cinegraph pipeline starting")
    log.info("Validating TMDB credentials...")

    if not validate_token():
        log.error("Token validation failed. Check your credentials and network.")
        sys.exit(1)

    log.info("  Credentials OK")
    log.info(f"  Output directory: {settings.output_dir}/")
    log.info(f"  Log directory:    {settings.log_dir}/")

    run()


if __name__ == "__main__":
    main()
