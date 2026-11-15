from typing import List, Optional

import polars as pl

from ._http import inform, resolve_url


def ed_get(
    dataset: str,
    table: str,
    columns: Optional[List[str]] = None,
    quiet: bool = False,
) -> pl.DataFrame:
    """
    Get a table from an EconDataverse dataset on Hugging Face.

    Downloads and reads a Parquet file directly from the
    [EconDataverse](https://huggingface.co/econdataverse) datasets on
    Hugging Face using Polars.

    Parameters
    ----------
    dataset
        Name of the dataset repository on Hugging Face (e.g., `"wbids"` for the
        World Bank International Debt Statistics).
    table
        Name of the table, i.e., the Parquet file name without the `.parquet`
        extension. Use `ed_get_tables()` to list the available tables.
    columns
        Names of the columns to read. Defaults to `None`, which reads all
        columns.
    quiet
        Suppress informational messages? Defaults to `False`.

    Returns
    -------
    pl.DataFrame
        A Polars DataFrame containing the requested table.

    Raises
    ------
    RuntimeError
        If the table cannot be downloaded or read.

    Examples
    --------
    ```python
    from econdatasets import ed_get

    ed_get("wbids", "counterparts")

    ed_get("wbids", "counterparts", columns=["counterpart_id", "counterpart_name"])
    ```
    """
    file_url = resolve_url(dataset, f"{table}.parquet")
    inform(f"> Reading dataset from {file_url}", quiet)

    try:
        df = pl.read_parquet(file_url, columns=columns)
    except Exception as e:
        raise RuntimeError(
            f"Failed to read table '{table}' from dataset '{dataset}' at {file_url}: {e}"
        ) from e

    inform(f"✔ Successfully loaded {table} from {dataset}", quiet)
    return df
