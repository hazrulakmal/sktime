"""Forecasting benchmarks tests."""

import pandas as pd
import pytest

from sktime.benchmarking.benchmarks import coerce_estimator_and_id
from sktime.benchmarking.forecasting import ForecastingBenchmark
from sktime.forecasting.model_selection import ExpandingWindowSplitter
from sktime.forecasting.naive import NaiveForecaster
from sktime.forecasting.trend import TrendForecaster
from sktime.performance_metrics.forecasting import (
    MeanAbsoluteError,
    MeanAbsolutePercentageError,
    MeanSquaredPercentageError,
)
from sktime.utils.validation._dependencies import _check_soft_dependencies

# TODO:
# Manual test is labor intensive, need to refactor the tests for fast iteration
EXPECTED_RESULTS_1 = pd.DataFrame(
    data={
        "validation_id": [
            "[dataset=data_loader_simple]_[cv_splitter=ExpandingWindowSplitter]-v1"
        ],
        "model_id": ["NaiveForecaster-v1"],
        "MeanSquaredPercentageError_fold_0_test": [0.0],
        "y_train_fold_0": [pd.DataFrame([2])],
        "y_test_fold_0": [pd.DataFrame([2], index=[1])],
        "y_pred_fold_0": [pd.DataFrame([2.0], index=[1])],
        "MeanSquaredPercentageError_fold_1_test": [0.111],
        "y_train_fold_1": [pd.DataFrame([2, 2])],
        "y_test_fold_1": [pd.DataFrame([3], index=[2])],
        "y_pred_fold_1": [pd.DataFrame([2.0], index=[2])],
        "MeanSquaredPercentageError_mean": [0.0555],
        "MeanSquaredPercentageError_std": [0.0785],
    },
    index=[0],
)

EXPECTED_RESULTS_2 = pd.DataFrame(
    data={
        "validation_id": [
            "[dataset=data_loader_simple]_[cv_splitter=ExpandingWindowSplitter]-v1"
        ],
        "model_id": ["NaiveForecaster-v1"],
        "MeanAbsolutePercentageError_fold_0_test": [0.0],
        "y_train_fold_0": [pd.DataFrame([2])],
        "y_test_fold_0": [pd.DataFrame([2], index=[1])],
        "y_pred_fold_0": [pd.DataFrame([2.0], index=[1])],
        "MeanAbsolutePercentageError_fold_1_test": [0.333],
        "y_train_fold_1": [pd.DataFrame([2, 2])],
        "y_test_fold_1": [pd.DataFrame([3], index=[2])],
        "y_pred_fold_1": [pd.DataFrame([2.0], index=[2])],
        "MeanAbsolutePercentageError_mean": [0.1666],
        "MeanAbsolutePercentageError_std": [0.2357],
        "MeanAbsoluteError_fold_0_test": [0.0],
        "MeanAbsoluteError_fold_1_test": [1.0],
        "MeanAbsoluteError_mean": [0.5],
        "MeanAbsoluteError_std": [0.7071],
    },
    index=[0],
)

COER_CASES = [
    (
        NaiveForecaster(),
        "NaiveForecaster-v1",
        {"NaiveForecaster-v1": NaiveForecaster()},
    ),
    (NaiveForecaster(), None, {"NaiveForecaster-v1": NaiveForecaster()}),
    (
        [NaiveForecaster(), TrendForecaster()],
        None,
        {
            "NaiveForecaster-v1": NaiveForecaster(),
            "TrendForecaster-v1": TrendForecaster(),
        },
    ),
    (
        {"estimator_1-v1": NaiveForecaster()},
        None,
        {"estimator_1-v1": NaiveForecaster()},
    ),
]


def data_loader_simple() -> pd.DataFrame:
    """Return simple data for use in testing."""
    return pd.DataFrame([2, 2, 3])


@pytest.mark.skipif(
    not _check_soft_dependencies("kotsu", severity="none"),
    reason="skip test if required soft dependencies not available",
)
@pytest.mark.parametrize(
    "expected_results_df, scorers",
    [
        (EXPECTED_RESULTS_1, [MeanSquaredPercentageError()]),
        (EXPECTED_RESULTS_2, [MeanAbsolutePercentageError(), MeanAbsoluteError()]),
    ],
)
def test_forecastingbenchmark(tmp_path, expected_results_df, scorers):
    """Test benchmarking a forecaster estimator."""
    benchmark = ForecastingBenchmark()

    benchmark.add_estimator(NaiveForecaster(strategy="last"))

    cv_splitter = ExpandingWindowSplitter(
        initial_window=1,
        step_length=1,
        fh=1,
    )
    benchmark.add_task(data_loader_simple, cv_splitter, scorers)

    results_file = tmp_path / "results.csv"
    results_df = benchmark.run(results_file)

    results_df = results_df.drop(columns=["runtime_secs"])

    pd.testing.assert_frame_equal(
        expected_results_df, results_df, check_exact=False, atol=0, rtol=0.001
    )


@pytest.mark.parametrize("estimator, estimator_id, expected_output", COER_CASES)
def test_coerce_estimator_and_id(estimator, estimator_id, expected_output):
    """Test coerce_estimator_and_id return expected output."""
    assert (
        coerce_estimator_and_id(estimator, estimator_id) == expected_output
    ), "coerce_estimator_and_id does not return the expected output."


@pytest.mark.skipif(
    not _check_soft_dependencies("kotsu", severity="none"),
    reason="skip test if required soft dependencies not available",
)
@pytest.mark.parametrize(
    "estimators",
    [
        ({"N-v1": NaiveForecaster(), "T-v1": TrendForecaster()}),
        ([NaiveForecaster(), TrendForecaster()]),
    ],
)
def test_multiple_estimators(estimators):
    """Test add_estimator with multiple estimators."""
    # single estimator test is checked in test_forecastingbenchmark
    benchmark = ForecastingBenchmark()
    benchmark.add_estimator(estimators)
    registered_estimators = benchmark.estimators.entity_specs.keys()
    assert len(registered_estimators) == len(
        estimators
    ), "add_estimator does not register all estimators."
