import io
import json

import polars as pl
import pytest


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


@pytest.fixture
def mock_json(monkeypatch):
    """Patch urllib so `get_json` returns `payload` and records requested URLs."""
    calls = []

    def _install(payload):
        def fake_urlopen(request, timeout=None):
            calls.append(request.full_url)
            return FakeResponse(json.dumps(payload).encode())

        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
        return calls

    return _install


@pytest.fixture
def parquet_file(tmp_path):
    path = tmp_path / "counterparts.parquet"
    pl.DataFrame(
        {
            "counterpart_id": [1, 2, 3],
            "counterpart_name": ["A", "B", "C"],
            "value": [10.0, 20.0, 30.0],
        }
    ).write_parquet(path)
    return path
