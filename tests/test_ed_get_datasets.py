import urllib.error

import polars as pl
import pytest

from econdatasets import ed_get_datasets

DATASETS = [
    {
        "_id": "6900ba28e9f617a5ce795cb4",
        "id": "econdataverse/wbids",
        "gated": False,
        "lastModified": "2025-12-11T11:56:55.000Z",
        "private": False,
        "downloads": 109,
    },
    {
        "_id": "69117e9d115742b9bc0e3748",
        "id": "econdataverse/imfweo",
        "gated": "auto",
        "lastModified": "2026-10-19T12:32:20.000Z",
        "private": False,
        "downloads": 42,
    },
]


def test_ed_get_datasets_parses_response(mock_json):
    calls = mock_json(DATASETS)

    df = ed_get_datasets(quiet=True)

    assert calls == ["https://huggingface.co/api/datasets?author=econdataverse"]
    assert df.schema == pl.Schema(
        {
            "dataset": pl.String,
            "total_downloads": pl.Int64,
            "last_modified": pl.Datetime("ms", "UTC"),
            "is_private": pl.Boolean,
            "is_gated": pl.Boolean,
        }
    )
    assert df["dataset"].to_list() == ["econdataverse/wbids", "econdataverse/imfweo"]
    assert df["total_downloads"].to_list() == [109, 42]
    assert df["is_gated"].to_list() == [False, True]
    # Compare as strings: converting a tz-aware value to a Python datetime needs
    # the `tzdata` package on Windows.
    assert df["last_modified"].dt.strftime("%Y-%m-%dT%H:%M:%S%z").to_list() == [
        "2025-12-11T11:56:55+0000",
        "2026-10-19T12:32:20+0000",
    ]


def test_ed_get_datasets_empty(mock_json):
    mock_json([])
    df = ed_get_datasets(quiet=True)
    assert df.height == 0
    assert df.columns == [
        "dataset",
        "total_downloads",
        "last_modified",
        "is_private",
        "is_gated",
    ]


def test_ed_get_datasets_messages(mock_json, capsys):
    mock_json(DATASETS)
    ed_get_datasets()
    err = capsys.readouterr().err
    assert "Fetching dataset list from" in err
    assert "Found 2 datasets." in err


def test_ed_get_datasets_unexpected_structure(mock_json):
    mock_json({"error": "nope"})
    with pytest.raises(RuntimeError, match="Unexpected API response structure"):
        ed_get_datasets(quiet=True)


def test_ed_get_datasets_network_error(monkeypatch):
    def fake_urlopen(request, timeout=None):
        raise urllib.error.URLError("no network")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    with pytest.raises(RuntimeError, match="no network"):
        ed_get_datasets(quiet=True)


@pytest.mark.online
def test_ed_get_datasets_online():
    df = ed_get_datasets(quiet=True)
    assert "econdataverse/wbids" in df["dataset"].to_list()
