"""Unit tests for parsing utilities."""

from cinegraph.processing.parsers import (
    alternative_titles,
    clean_html,
    image_url,
    join_ids,
    join_names,
    parse_id_list,
    safe_year,
)


def test_clean_html_strips_tags():
    assert clean_html("<p>Hello <b>world</b></p>") == "Hello world"


def test_clean_html_collapses_whitespace():
    assert clean_html("foo    bar\n\nbaz") == "foo bar baz"


def test_clean_html_returns_none_for_falsy():
    assert clean_html(None) is None
    assert clean_html("") is None
    assert clean_html("   ") is None


def test_join_names_with_provider_name_key():
    items = [
        {"provider_name": "Netflix", "provider_id": 8},
        {"provider_name": "Disney Plus", "provider_id": 337},
    ]
    assert join_names(items, "provider_name") == "Netflix, Disney Plus"


def test_join_names_default_key():
    assert join_names([{"name": "Action"}, {"name": "Drama"}]) == "Action, Drama"


def test_join_names_skips_empty_values():
    assert join_names([{"name": "A"}, {"name": None}, {"name": "B"}]) == "A, B"


def test_join_ids_basic():
    assert join_ids([1, 2, 3]) == "1, 2, 3"


def test_join_ids_skips_none():
    assert join_ids([1, None, 3]) == "1, 3"


def test_parse_id_list_roundtrip():
    assert parse_id_list(join_ids([10, 20, 30])) == [10, 20, 30]


def test_parse_id_list_handles_whitespace():
    assert parse_id_list("  17419  ,  84497  ") == [17419, 84497]


def test_parse_id_list_ignores_non_numeric():
    assert parse_id_list("bad, 12, also bad") == [12]


def test_parse_id_list_accepts_numeric_input():
    assert parse_id_list(42) == [42]
    assert parse_id_list(42.0) == [42]


def test_parse_id_list_empty_inputs():
    assert parse_id_list(None) == []
    assert parse_id_list("") == []
    assert parse_id_list("   ") == []


def test_image_url_builds_full_path():
    expected = "https://image.tmdb.org/t/p/w500/abc.jpg"
    assert image_url("/abc.jpg", "w500") == expected


def test_image_url_rejects_invalid():
    assert image_url(None) is None
    assert image_url("abc.jpg") is None  # missing leading slash


def test_safe_year_extracts_year():
    assert safe_year("1999-03-31") == 1999
    assert safe_year("2024-01-01") == 2024


def test_safe_year_rejects_invalid():
    assert safe_year(None) is None
    assert safe_year("abc") is None
    assert safe_year("19") is None


def test_alternative_titles_format():
    items = [
        {"iso_3166_1": "TR", "title": "Matriks"},
        {"iso_3166_1": "DE", "title": "Matrix"},
    ]
    assert alternative_titles(items) == "TR:Matriks | DE:Matrix"


def test_alternative_titles_empty():
    assert alternative_titles(None) is None
    assert alternative_titles([]) is None
