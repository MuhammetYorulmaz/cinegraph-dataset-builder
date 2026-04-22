"""
TMDB HTTP client.

All outbound API traffic flows through :func:`api_get`. The function
handles authentication, retry on transient failures, and rate-limit
backoff using the ``Retry-After`` header supplied by TMDB.
"""

from __future__ import annotations

import time
from typing import Any

import requests

from cinegraph.config import settings
from cinegraph.utils.logging import log


BASE_URL = "https://api.themoviedb.org/3"

# Shared session — reuses connections for throughput and sets common headers.
_session = requests.Session()
_session.headers.update({
    "Authorization": f"Bearer {settings.access_token}",
    "accept":        "application/json",
})


def api_get(
    endpoint: str,
    params:   dict[str, Any] | None = None,
    retries:  int = 4,
) -> dict | None:
    """
    Perform a GET request against the TMDB API.

    Response handling:
        200 → JSON is returned.
        404 → ``None`` is returned silently (resource missing is normal).
        429 → sleep for ``Retry-After`` seconds and retry.
        5xx → retry with increasing backoff.
        Network exception → retry with increasing backoff.

    Returns ``None`` if every retry is exhausted.
    """
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"

    for attempt in range(retries):
        try:
            response = _session.get(url, params=params or {}, timeout=15)

            if response.status_code == 200:
                return response.json()

            if response.status_code == 429:
                wait = int(response.headers.get("Retry-After", 12))
                log.warning(f"Rate limited → sleeping {wait}s ({endpoint})")
                time.sleep(wait)
                continue

            if response.status_code == 404:
                return None

            if response.status_code in (500, 502, 503, 504):
                wait = 3 * (attempt + 1)
                log.debug(
                    f"HTTP {response.status_code} on {endpoint} — "
                    f"retry {attempt + 1} after {wait}s"
                )
                time.sleep(wait)
                continue

            log.debug(f"Unexpected HTTP {response.status_code} on {endpoint}")
            return None

        except requests.exceptions.ConnectionError:
            time.sleep(4 * (attempt + 1))
        except requests.exceptions.Timeout:
            time.sleep(6)
        except Exception as exc:
            log.debug(f"Request error on {endpoint} [{attempt + 1}/{retries}]: {exc}")
            time.sleep(2)

    return None


def validate_token() -> bool:
    """Verify that the configured access token is accepted by TMDB."""
    result = api_get("authentication")
    return bool(result and result.get("success"))
