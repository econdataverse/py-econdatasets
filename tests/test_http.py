import pytest

from econdatasets._http import get_json


def test_get_json_invalid_json(mock_body):
    mock_body(b"<html>Not JSON</html>")

    with pytest.raises(RuntimeError, match="Failed to parse JSON response from"):
        get_json("https://huggingface.co/api/datasets?author=econdataverse")
