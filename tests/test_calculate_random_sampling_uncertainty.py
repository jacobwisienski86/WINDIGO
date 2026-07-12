import numpy as np
from unittest.mock import patch

from src.WINDIGO.post_processing_main_functions import (
    calculate_random_sampling_uncertainty,
)


def test_random_sampling_uncertainty_basic():
    """Basic standard deviation calculation."""
    outputs = np.array([10.0, 12.0, 14.0])

    # mean = 12, squared distances = [4, 0, 4]
    # variance = 8 / (3 - 1) = 4, uncertainty = sqrt(4) = 2
    expected = 2.0

    result = calculate_random_sampling_uncertainty(outputs)

    assert np.allclose(result, expected)


def test_random_sampling_uncertainty_no_error_propagation():
    """Ensure only propagated uncertainty is returned when flag is False."""
    outputs = np.array([1.0, 2.0, 3.0])

    result = calculate_random_sampling_uncertainty(
        outputs,
        error_propagation_flag=False,
    )

    assert isinstance(result, float)


def test_random_sampling_uncertainty_with_error_propagation():
    """Full error-propagation path with patched internal calls."""
    outputs = np.array([10.0, 12.0, 14.0])
    errs = np.array([0.3, 0.4, 0.5])

    with patch(
        "src.WINDIGO.post_processing_main_functions.calculate_mean_error",
        return_value=0.2,
    ) as mock_mean_err, patch(
        "src.WINDIGO.post_processing_main_functions.calculate_random_sampling_variance_error",
        return_value=5.0,
    ) as mock_var_err, patch(
        "src.WINDIGO.post_processing_main_functions.calculate_uncertainty_error",
        return_value=1.5,
    ) as mock_uncert_err:

        propagated, error = calculate_random_sampling_uncertainty(
            outputs,
            error_propagation_flag=True,
            perturbed_output_errors=errs,
        )

    # All three internal functions MUST be called
    mock_mean_err.assert_called_once()
    mock_var_err.assert_called_once()
    mock_uncert_err.assert_called_once()

    assert isinstance(propagated, float)
    assert isinstance(error, float)


def test_random_sampling_uncertainty_negative_errors():
    """Negative errors behave identically because they are squared."""
    outputs = np.array([10.0, 12.0])
    errs = np.array([-0.3, -0.4])

    with patch(
        "src.WINDIGO.post_processing_main_functions.calculate_mean_error",
        return_value=0.2,
    ), patch(
        "src.WINDIGO.post_processing_main_functions.calculate_random_sampling_variance_error",
        return_value=4.0,
    ), patch(
        "src.WINDIGO.post_processing_main_functions.calculate_uncertainty_error",
        return_value=1.0,
    ):
        propagated, error = calculate_random_sampling_uncertainty(
            outputs,
            error_propagation_flag=True,
            perturbed_output_errors=errs,
        )

    assert isinstance(propagated, float)
    assert isinstance(error, float)


def test_random_sampling_uncertainty_scalar_output():
    """Ensure the function returns a scalar float."""
    outputs = np.array([10.0, 11.0, 12.0])

    result = calculate_random_sampling_uncertainty(outputs)

    assert isinstance(result, float)


def test_random_sampling_uncertainty_zero_denominator_suppressed():
    """
    If len(outputs) = 1 → denominator (n−1) = 0.
    Suppress warnings and ensure a float is returned.
    """
    outputs = np.array([10.0])

    with np.errstate(divide="ignore", invalid="ignore"):
        result = calculate_random_sampling_uncertainty(
            outputs,
            error_propagation_flag=False,
        )

    assert isinstance(result, float)
