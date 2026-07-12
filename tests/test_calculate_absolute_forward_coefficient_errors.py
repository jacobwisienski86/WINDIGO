import numpy as np

from src.WINDIGO.post_processing_internal_functions import (
    calculate_absolute_forward_coefficient_errors,
)


def test_forward_abs_errors_basic():
    """Basic absolute forward-difference error calculation."""
    original_inputs = np.array([1.0, 2.0])
    positive_inputs = np.array([1.1, 2.2])
    unperturbed_err = 0.5
    positive_errs = np.array([0.3, 0.4])

    expected = (1.0 / (positive_inputs - original_inputs)) * np.sqrt(
        positive_errs**2 + unperturbed_err**2
    )

    result = calculate_absolute_forward_coefficient_errors(
        original_inputs,
        positive_inputs,
        unperturbed_err,
        positive_errs,
    )

    assert np.allclose(result, expected)


def test_forward_abs_errors_shape_preserved():
    """Ensure output shape matches input shape."""
    original_inputs = np.array([1.0, 2.0, 3.0])
    positive_inputs = np.array([1.1, 2.1, 3.1])
    unperturbed_err = 0.2
    positive_errs = np.array([0.1, 0.2, 0.3])

    result = calculate_absolute_forward_coefficient_errors(
        original_inputs,
        positive_inputs,
        unperturbed_err,
        positive_errs,
    )

    assert result.shape == original_inputs.shape


def test_forward_abs_errors_negative_denominator():
    """Negative denominator should produce correct sign behavior."""
    original_inputs = np.array([1.2])
    positive_inputs = np.array([1.0])  # denominator negative
    unperturbed_err = 0.5
    positive_errs = np.array([0.4])

    expected = (1.0 / (1.0 - 1.2)) * np.sqrt(0.4**2 + 0.5**2)

    result = calculate_absolute_forward_coefficient_errors(
        original_inputs,
        positive_inputs,
        unperturbed_err,
        positive_errs,
    )

    assert np.allclose(result, expected)


def test_forward_abs_errors_zero_denominator():
    """Zero denominator should produce inf or nan without emitting warnings."""
    original_inputs = np.array([1.0])
    positive_inputs = np.array([1.0])  # zero denominator
    unperturbed_err = 0.5
    positive_errs = np.array([0.4])

    # Suppress NumPy divide-by-zero warnings for this test
    with np.errstate(divide="ignore", invalid="ignore"):
        result = calculate_absolute_forward_coefficient_errors(
            original_inputs,
            positive_inputs,
            unperturbed_err,
            positive_errs,
        )

    assert np.isinf(result) or np.isnan(result)
