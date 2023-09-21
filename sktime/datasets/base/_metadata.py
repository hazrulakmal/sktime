"""Metadata for sktime datasets."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class BaseDatasetMetadata:
    """Base class for dataset metadata."""

    name: str
    task_type: str  # classification, regression, forecasting
    download_file_format: str  # zip, .ts, .arff, .csv
    # is_univariate: bool
    # dimensions: tuple


@dataclass
class ExternalDatasetMetadata(BaseDatasetMetadata):
    """Metadata for external datasets."""

    url: str
    citation: str
    backup_urls: Optional[list[str]]


@dataclass
class ForecastingDatasetMetadata(ExternalDatasetMetadata):
    """Metadata for forecasting datasets."""

    record_number: int
