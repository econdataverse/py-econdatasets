# econdatasets

Easily download EconDataverse datasets with Polars.

The [EconDataverse](https://www.econdataverse.org) is a universe of open-source packages to work seamlessly with economic data. This package makes it easy to download selected datasets that are preprocessed by EconDataverse packages and publicly hosted on [Hugging Face](https://huggingface.co/econdataverse). It is the Python counterpart of the R package [econdatasets](https://github.com/econdataverse/r-econdatasets).

`econdatasets` returns [Polars](https://pola.rs) DataFrames and has no dependencies besides Polars.

## Installation

Install the development version from GitHub:

```bash
pip install "git+https://github.com/econdataverse/py-econdatasets"
```

## Usage

```python
from econdatasets import ed_get, ed_get_datasets, ed_get_tables
```

List all datasets available in the EconDataverse organization on Hugging Face:

```python
ed_get_datasets()
```

List the tables of a dataset, e.g., the World Bank International Debt Statistics (`wbids`):

```python
ed_get_tables("wbids")
```

Download a table as a Polars DataFrame:

```python
ed_get("wbids", "counterparts")
```

Read only the columns you need:

```python
ed_get("wbids", "counterparts", columns=["counterpart_id", "counterpart_name"])
```

All functions print short status messages to stderr. Pass `quiet=True` to suppress them. If a download fails, the functions raise a `RuntimeError` with the URL that failed.

If you prefer pandas, convert the result with `.to_pandas()` (requires `pandas` and `pyarrow`).

## Contributing

Contributions are welcome! Please open an [issue](https://github.com/econdataverse/py-econdatasets/issues) or a pull request.
