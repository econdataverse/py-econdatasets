import posixpath

import polars as pl

from ._http import HF_BASE_URL, HF_ORG, get_json, inform, resolve_url

SCHEMA = {
    "table": pl.String,
    "filename": pl.String,
    "path": pl.String,
    "size": pl.Int64,
    "url": pl.String,
}


def ed_get_tables(dataset: str, quiet: bool = False) -> pl.DataFrame:
    """
    List the Parquet tables of an EconDataverse dataset.

    Queries the Hugging Face Hub and returns all `.parquet` files in a dataset
    repository of the [EconDataverse](https://huggingface.co/econdataverse)
    organization, including their file sizes.

    Parameters
    ----------
    dataset
        Name of the dataset repository on Hugging Face (e.g., `"wbids"`).
    quiet
        Suppress informational messages? Defaults to `False`.

    Returns
    -------
    pl.DataFrame
        A Polars DataFrame with the following columns:

        - `table`: file name without the `.parquet` extension.
        - `filename`: file name with extension.
        - `path`: path of the file within the repository.
        - `size`: file size in bytes.
        - `url`: direct download URL of the Parquet file.

    Raises
    ------
    RuntimeError
        If the request to the Hugging Face API fails or the response has an
        unexpected structure.

    Examples
    --------
    ```python
    from econdatasets import ed_get_tables

    ed_get_tables("wbids")
    ```
    """
    api_url = f"{HF_BASE_URL}/api/datasets/{HF_ORG}/{dataset}/tree/main?recursive=1"
    inform(f"> Fetching file tree from {api_url}", quiet)

    items = get_json(api_url)
    if isinstance(items, dict) and isinstance(items.get("tree"), list):
        items = items["tree"]
    if not isinstance(items, list):
        raise RuntimeError(
            "Unexpected API response structure; could not find file list."
        )

    rows = []
    for item in items:
        path = item.get("path", "")
        if item.get("type") != "file" or not path.lower().endswith(".parquet"):
            continue
        filename = posixpath.basename(path)
        rows.append(
            {
                "table": filename[: -len(".parquet")],
                "filename": filename,
                "path": path,
                "size": item.get("size"),
                "url": resolve_url(dataset, path),
            }
        )

    out = pl.DataFrame(rows, schema=SCHEMA)

    if out.height == 0:
        inform("i No Parquet files found in this dataset.", quiet)
    else:
        inform(f"✔ Found {out.height} Parquet table(s).", quiet)

    return out
