"""Unit tests for reference extraction."""

from cinegraph.discovery.references import extract_orphan_ids, extract_person_ids


def test_extract_person_ids_threshold_two():
    movies = [
        {"tmdb_id": 1, "cast_ids": "100, 200, 300", "director_ids": "500"},
        {"tmdb_id": 2, "cast_ids": "100, 400",       "director_ids": "500"},
        {"tmdb_id": 3, "cast_ids": "600",            "director_ids": "700"},
    ]
    tv = [
        {"tmdb_id": 10, "cast_ids": "100, 800",  "creator_ids": "500"},
        {"tmdb_id": 11, "cast_ids": "200, 900",  "creator_ids": "950"},
    ]
    # Person 100: 3× (movies 1, 2 and tv 10)
    # Person 200: 2× (movie 1 and tv 11)
    # Person 500: 3× (movies 1, 2 as director, tv 10 as creator)
    assert extract_person_ids(movies, tv, min_refs=2) == {100, 200, 500}


def test_extract_person_ids_threshold_three():
    movies = [
        {"tmdb_id": 1, "cast_ids": "100, 200", "director_ids": "500"},
        {"tmdb_id": 2, "cast_ids": "100",      "director_ids": "500"},
    ]
    tv = [{"tmdb_id": 10, "cast_ids": "100", "creator_ids": "500"}]
    assert extract_person_ids(movies, tv, min_refs=3) == {100, 500}


def test_extract_person_ids_threshold_one_returns_all():
    movies = [{"tmdb_id": 1, "cast_ids": "1, 2, 3", "director_ids": ""}]
    tv = [{"tmdb_id": 10, "cast_ids": "4", "creator_ids": "5"}]
    assert extract_person_ids(movies, tv, min_refs=1) == {1, 2, 3, 4, 5}


def test_extract_orphan_ids_basic():
    rows = [
        {"tmdb_id": 1, "similar_ids": "2, 3, 999",  "recommended_ids": "4, 888"},
        {"tmdb_id": 2, "similar_ids": "1, 3",        "recommended_ids": "777"},
    ]
    universe = {1, 2, 3, 4}
    assert extract_orphan_ids(rows, universe) == {999, 888, 777}


def test_extract_orphan_ids_all_in_universe():
    rows = [{"tmdb_id": 1, "similar_ids": "2, 3", "recommended_ids": "4"}]
    universe = {1, 2, 3, 4}
    assert extract_orphan_ids(rows, universe) == set()


def test_extract_orphan_ids_empty_refs():
    rows = [{"tmdb_id": 1, "similar_ids": None, "recommended_ids": None}]
    universe = {1}
    assert extract_orphan_ids(rows, universe) == set()
