"""
Logging configuration.

Log messages are written to both the console and a dated file inside the
logs directory. The file handler is configured lazily on first use so that
the directory is created only when the pipeline actually runs.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path

from cinegraph.config import settings


_LOG_FORMAT = "%(asctime)s │ %(levelname)-7s │ %(message)s"
_DATE_FORMAT = "%H:%M:%S"


def _build_logger() -> logging.Logger:
    logger = logging.getLogger("cinegraph")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(console)

    # File handler
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    file_handler = logging.FileHandler(
        log_dir / f"pipeline_{stamp}.log",
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


log = _build_logger()
