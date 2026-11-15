"""Easily download EconDataverse datasets with Polars."""

from ._ed_get import ed_get
from ._ed_get_datasets import ed_get_datasets
from ._ed_get_tables import ed_get_tables

__all__ = [
    "ed_get",
    "ed_get_datasets",
    "ed_get_tables",
]
