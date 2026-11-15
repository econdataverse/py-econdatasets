import urllib.error

import polars as pl
import pytest

from econdatasets import ed_get_tables

TREE = [
    {"type": "file", "size": 2461, "path": ".gitattributes"},
    {"type": "file", "size": 655, "path": "README.md"},
    {"type": "file", "size": 10445, "path": "counterparts.parquet"},
    {"type": "directory", "size": 0, "path": "sub"},
    {"type": "file", "size": 108609789, "path": "sub/debt_statistics.PARQUET"},
]


def test_ed_get_tables_parses_tree(mock_json):
    calls = mock_json(TREE)

    df = ed_get_tables("wbids", quiet=True)

    assert calls == [
        "https://huggingface.co/api/datasets/econdataverse/wbids/tree/main?recursive=1"
    ]
    assert df.columns == ["table", "filename", "path", "size", "url"]
    assert df["table"].to_list() == ["counterparts", "debt_statistics"]
    assert df["filename"].to_list() == [
        "counterparts.parquet",
        "debt_statistics.PARQUET",
    ]
    assert df["size"].to_list() == [10445, 108609789]
    assert df["url"][1] == (
        "https://huggingface.co/datasets/econdataverse/wbids/resolve/main/"
        "sub/debt_statistics.PARQUET"
    )


def test_ed_get_tables_handles_tree_key(mock_json):
    mock_json({"tree": TREE})
    assert ed_get_tables("wbids", quiet=True).height == 2


def test_ed_get_tables_empty(mock_json, capsys):
    mock_json([{"type": "file", "size": 1, "path": "README.md"}])

    df = ed_get_tables("wbids")

    assert df.height == 0
    assert df.schema == pl.Schema(
        {
            "table": pl.String,
            "filename": pl.String,
            "path": pl.String,
            "size": pl.Int64,
            "url": pl.String,
        }
    )
    assert "No Parquet files found" in capsys.readouterr().err


def test_ed_get_tables_unexpected_structure(mock_json):
    mock_json({"error": "nope"})
    with pytest.raises(RuntimeError, match="Unexpected API response structure"):
        ed_get_tables("wbids", quiet=True)


def test_ed_get_tables_http_error(monkeypatch):
    def fake_urlopen(request, timeout=None):
        raise urllib.error.HTTPError(request.full_url, 404, "Not Found", {}, None)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    with pytest.raises(RuntimeError, match="HTTP status 404"):
        ed_get_tables("does-not-exist", quiet=True)


@pytest.mark.online
def test_ed_get_tables_online():
    df = ed_get_tables("wbids", quiet=True)
    assert "counterparts" in df["table"].to_list()
