import numpy as np

from src.WINDIGO.post_processing_internal_functions import (
    calculate_absolute_backward_coefficient_errors,
)


def test_backward_abs_errors_basic():
    """Basic absolute backward-difference error calculation."""
    original_inputs = np.array([1.0, 2.0])
    negative_inputs = np.array([0.9, 1.9])
    unperturbed_err = 0.5
    negative_errs = np.array([0.3, 0.4])

    expected = (1.0 / (original_inputs - negative_inputs)) * np.sqrt(
        unperturbed_err**2 + negative_errs**2
    )

    result = calculate_absolute_backward_coefficient_errors(
        original_inputs,
        negative_inputs,
        unperturbed_err,
        negative_errs,
    )

    assert np.allclose(result, expected)


def test_backward_abs_errors_shape_preserved():
    """Ensure output shape matches input shape."""
    original_inputs = np.array([1.0, 2.0, 3.0])
    negative_inputs = np.array([0.8, 1.8, 2.8])
    unperturbed_err = 0.2
    negative_errs = np.array([0.1, 0.2, 0.3])

    result = calculate_absolute_backward_coefficient_errors(
        original_inputs,
        negative_inputs,
        unperturbed_err,
        negative_errs,
    )

    assert result.shape == original_inputs.shape


def test_backward_abs_errors_negative_denominator():
    """Negative denominator should produce correct sign behavior."""
    original_inputs = np.array([1.0])
    negative_inputs = np.array([1.2])  # denominator negative
    unperturbed_err = 0.5
    negative_errs = np.array([0.4])

    expected = (1.0 / (1.0 - 1.2)) * np.sqrt(0.4**2 + 0.5**2)

    result = calculate_absolute_backward_coefficient_errors(
        original_inputs,
        negative_inputs,
        unperturbed_err,
        negative_errs,
    )

    assert np.allclose(result, expected)


def test_backward_abs_errors_zero_denominator():
    """Zero denominator should produce inf or nan without emitting warnings."""
    original_inputs = np.array([1.0])
    negative_inputs = np.array([1.0])  # zero denominator
    unperturbed_err = 0.5
    negative_errs = np.array([0.4])

    # Suppress NumPy divide-by-zero warnings for this test
    with np.errstate(divide="ignore", invalid="ignore"):
        result = calculate_absolute_backward_coefficient_errors(
            original_inputs,
            negative_inputs,
            unperturbed_err,
            negative_errs,
        )

    assert np.isinf(result) or np.isnan(result)
