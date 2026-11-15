import polars as pl
import pytest

from econdatasets import ed_get


@pytest.fixture
def local_read(monkeypatch, parquet_file):
    """Redirect `pl.read_parquet` to a local file and record the requested URL."""
    calls = []
    original = pl.read_parquet

    def fake_read_parquet(source, columns=None):
        calls.append({"source": source, "columns": columns})
        return original(parquet_file, columns=columns)

    monkeypatch.setattr("polars.read_parquet", fake_read_parquet)
    return calls


def test_ed_get_reads_table(local_read):
    df = ed_get("wbids", "counterparts", quiet=True)

    assert isinstance(df, pl.DataFrame)
    assert df.shape == (3, 3)
    assert local_read[0]["source"] == (
        "https://huggingface.co/datasets/econdataverse/wbids/resolve/main/"
        "counterparts.parquet"
    )


def test_ed_get_selects_columns(local_read):
    df = ed_get(
        "wbids",
        "counterparts",
        columns=["counterpart_id", "counterpart_name"],
        quiet=True,
    )

    assert df.columns == ["counterpart_id", "counterpart_name"]
    assert local_read[0]["columns"] == ["counterpart_id", "counterpart_name"]


def test_ed_get_raises_on_failure(monkeypatch):
    def failing(*args, **kwargs):
        raise OSError("404 Not Found")

    monkeypatch.setattr("polars.read_parquet", failing)

    with pytest.raises(RuntimeError, match="Failed to read table 'missing'"):
        ed_get("wbids", "missing", quiet=True)


def test_ed_get_messages(local_read, capsys):
    ed_get("wbids", "counterparts")
    err = capsys.readouterr().err
    assert "Reading dataset from" in err
    assert "Successfully loaded counterparts from wbids" in err


def test_ed_get_quiet(local_read, capsys):
    ed_get("wbids", "counterparts", quiet=True)
    assert capsys.readouterr().err == ""


@pytest.mark.online
def test_ed_get_online():
    df = ed_get("wbids", "counterparts", quiet=True)
    assert df.height > 0
    assert "counterpart_id" in df.columns
