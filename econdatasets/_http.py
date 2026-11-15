"""Internal helpers for talking to the Hugging Face Hub API."""

import json
import sys
import urllib.error
import urllib.request
from typing import Any

HF_ORG = "econdataverse"
HF_BASE_URL = "https://huggingface.co"
USER_AGENT = "econdatasets Python library (https://github.com/econdataverse/py-econdatasets)"


def resolve_url(dataset: str, path: str) -> str:
    """Return the direct download URL of a file in an EconDataverse dataset repo."""
    return f"{HF_BASE_URL}/datasets/{HF_ORG}/{dataset}/resolve/main/{path}"


def get_json(url: str, timeout: float = 30.0) -> Any:
    """Perform a GET request and parse the JSON response body.

    Raises
    ------
    RuntimeError
        If the request fails or the response is not valid JSON.
    """
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(
            f"Request to {url} failed with HTTP status {e.code}: {e.reason}"
        ) from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Request to {url} failed: {e.reason}") from e

    try:
        return json.loads(body)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse JSON response from {url}") from e


def inform(message: str, quiet: bool) -> None:
    """Print an informational message to stderr unless `quiet` is set."""
    if not quiet:
        print(message, file=sys.stderr)
