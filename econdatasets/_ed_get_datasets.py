import polars as pl

from ._http import HF_BASE_URL, HF_ORG, get_json, inform

SCHEMA = {
    "dataset": pl.String,
    "total_downloads": pl.Int64,
    "last_modified": pl.Datetime("ms", "UTC"),
    "is_private": pl.Boolean,
    "is_gated": pl.Boolean,
}


def ed_get_datasets(quiet: bool = False) -> pl.DataFrame:
    """
    List the datasets available in the EconDataverse organization.

    Retrieves all datasets published under the
    [EconDataverse](https://huggingface.co/econdataverse) organization on
    Hugging Face.

    Parameters
    ----------
    quiet
        Suppress informational messages? Defaults to `False`.

    Returns
    -------
    pl.DataFrame
        A Polars DataFrame with the following columns:

        - `dataset`: dataset identifier on Hugging Face (e.g., `"econdataverse/wbids"`).
        - `total_downloads`: approximate download count.
        - `last_modified`: last update timestamp (UTC).
        - `is_private`: whether the dataset is private.
        - `is_gated`: whether access to the dataset is gated.

    Raises
    ------
    RuntimeError
        If the request to the Hugging Face API fails or the response has an
        unexpected structure.

    Examples
    --------
    ```python
    from econdatasets import ed_get_datasets

    ed_get_datasets()
    ```
    """
    url = f"{HF_BASE_URL}/api/datasets?author={HF_ORG}"
    inform(f"> Fetching dataset list from {url}", quiet)

    items = get_json(url)
    if not isinstance(items, list):
        raise RuntimeError(
            "Unexpected API response structure; could not find dataset list."
        )

    rows = [
        {
            "dataset": item.get("id"),
            "total_downloads": item.get("downloads"),
            "last_modified": item.get("lastModified"),
            "is_private": bool(item.get("private", False)),
            # `gated` is either `false` or a string such as "auto" or "manual"
            "is_gated": item.get("gated", False) not in (False, None),
        }
        for item in items
    ]

    df = pl.DataFrame(
        rows, schema={**SCHEMA, "last_modified": pl.String}
    ).with_columns(
        pl.col("last_modified").str.to_datetime(
            "%Y-%m-%dT%H:%M:%S%.fZ", time_unit="ms", time_zone="UTC"
        )
    )

    inform(f"✔ Found {df.height} datasets.", quiet)
    return df
