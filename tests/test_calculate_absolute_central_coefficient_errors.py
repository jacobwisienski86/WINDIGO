import numpy as np

from src.WINDIGO.post_processing_internal_functions import (
    calculate_absolute_central_coefficient_errors,
)


def test_central_abs_errors_basic():
    """Basic absolute central-difference error calculation."""
    positive_inputs = np.array([1.1, 2.1])
    negative_inputs = np.array([0.9, 1.9])
    positive_errs = np.array([0.3, 0.4])
    negative_errs = np.array([0.2, 0.3])

    expected = (1.0 / (positive_inputs - negative_inputs)) * np.sqrt(
        positive_errs**2 + negative_errs**2
    )

    result = calculate_absolute_central_coefficient_errors(
        positive_inputs,
        negative_inputs,
        positive_errs,
        negative_errs,
    )

    assert np.allclose(result, expected)


def test_central_abs_errors_shape_preserved():
    """Ensure output shape matches input shape."""
    positive_inputs = np.array([1.1, 2.1, 3.1])
    negative_inputs = np.array([0.9, 1.9, 2.9])
    positive_errs = np.array([0.1, 0.2, 0.3])
    negative_errs = np.array([0.2, 0.3, 0.4])

    result = calculate_absolute_central_coefficient_errors(
        positive_inputs,
        negative_inputs,
        positive_errs,
        negative_errs,
    )

    assert result.shape == positive_inputs.shape


def test_central_abs_errors_negative_denominator():
    """Negative denominator should produce correct sign behavior."""
    positive_inputs = np.array([1.0])
    negative_inputs = np.array([1.2])  # denominator negative
    positive_errs = np.array([0.4])
    negative_errs = np.array([0.5])

    expected = (1.0 / (1.0 - 1.2)) * np.sqrt(0.4**2 + 0.5**2)

    result = calculate_absolute_central_coefficient_errors(
        positive_inputs,
        negative_inputs,
        positive_errs,
        negative_errs,
    )

    assert np.allclose(result, expected)


def test_central_abs_errors_zero_denominator():
    """Zero denominator should produce inf or nan without emitting warnings."""
    positive_inputs = np.array([1.0])
    negative_inputs = np.array([1.0])  # zero denominator
    positive_errs = np.array([0.4])
    negative_errs = np.array([0.5])

    # Suppress NumPy divide-by-zero warnings for this test
    with np.errstate(divide="ignore", invalid="ignore"):
        result = calculate_absolute_central_coefficient_errors(
            positive_inputs,
            negative_inputs,
            positive_errs,
            negative_errs,
        )

    assert np.isinf(result) or np.isnan(result)
