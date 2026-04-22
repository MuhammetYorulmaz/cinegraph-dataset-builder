"""Unit tests for domain transforms."""

from cinegraph.processing.transforms import (
    content_ratings_flat,
    theatrical_certification,
    watch_providers_flat,
)


def test_watch_providers_uses_provider_name_key():
    raw = {
        "results": {
            "TR": {
                "link": "https://www.themoviedb.org/movie/603/watch?locale=TR",
                "flatrate": [
                    {"provider_id": 8,   "provider_name": "Netflix"},
                    {"provider_id": 337, "provider_name": "Disney Plus"},
                ],
                "rent": [{"provider_id": 10, "provider_name": "Amazon Video"}],
            },
            "US": {
                "link": "https://www.themoviedb.org/movie/603/watch?locale=US",
                "flatrate": [{"provider_id": 8, "provider_name": "Netflix"}],
            },
        }
    }

    result = watch_providers_flat(raw, ["TR", "US"])

    assert result["watch_tr_flatrate"] == "Netflix, Disney Plus"
    assert result["watch_tr_rent"] == "Amazon Video"
    assert result["watch_tr_buy"] is None
    assert result["watch_tr_free"] is None
    assert result["watch_tr_link"].endswith("locale=TR")
    assert result["watch_us_flatrate"] == "Netflix"
    assert result["watch_us_rent"] is None


def test_watch_providers_empty_input():
    result = watch_providers_flat(None, ["TR"])
    assert result["watch_tr_flatrate"] is None
    assert result["watch_tr_link"] is None


def test_content_ratings_flat():
    raw = {
        "results": [
            {"iso_3166_1": "US", "rating": "TV-MA"},
            {"iso_3166_1": "TR", "rating": "18+"},
        ]
    }
    result = content_ratings_flat(raw, ["TR", "US"])
    assert result["cert_tr"] == "18+"
    assert result["cert_us"] == "TV-MA"


def test_content_ratings_missing_country():
    raw = {"results": [{"iso_3166_1": "US", "rating": "TV-14"}]}
    result = content_ratings_flat(raw, ["TR", "US"])
    assert result["cert_tr"] is None
    assert result["cert_us"] == "TV-14"


def test_theatrical_certification_type_3():
    raw = {
        "results": [
            {
                "iso_3166_1": "US",
                "release_dates": [
                    {"type": 1, "certification": ""},
                    {"type": 3, "certification": "R"},
                ],
            }
        ]
    }
    assert theatrical_certification(raw, "US") == "R"


def test_theatrical_certification_missing():
    raw = {"results": []}
    assert theatrical_certification(raw, "US") is None
