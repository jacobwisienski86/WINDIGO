import numpy as np

from src.WINDIGO.post_processing_internal_functions import (
    calculate_backward_coefficients,
)


def test_backward_coefficients_absolute_basic():
    """Test absolute backward-difference sensitivity calculation."""
    negative_outputs = np.array([8.0, 18.0, 38.0])
    unperturbed_output = 10.0
    negative_inputs = np.array([0.8, 1.8, 3.8])   # ensure no zero denominators
    original_inputs = np.array([1.0, 2.0, 4.0])

    expected = (unperturbed_output - negative_outputs) / (
        original_inputs - negative_inputs
    )

    result = calculate_backward_coefficients(
        negative_outputs,
        unperturbed_output,
        negative_inputs,
        original_inputs,
        relative_flag=False,
    )

    assert np.allclose(result, expected)


def test_backward_coefficients_relative_basic():
    """Test relative sensitivity calculation."""
    negative_outputs = np.array([8.0, 18.0, 38.0])
    unperturbed_output = 10.0
    negative_inputs = np.array([0.8, 1.8, 3.8])
    original_inputs = np.array([1.0, 2.0, 4.0])

    absolute = (unperturbed_output - negative_outputs) / (
        original_inputs - negative_inputs
    )
    expected = absolute * (original_inputs / unperturbed_output)

    result = calculate_backward_coefficients(
        negative_outputs,
        unperturbed_output,
        negative_inputs,
        original_inputs,
        relative_flag=True,
    )

    assert np.allclose(result, expected)


def test_backward_coefficients_shape_preserved():
    """Ensure output shape matches input shape."""
    negative_outputs = np.array([9.0, 19.0, 29.0, 39.0])
    unperturbed_output = 10.0
    negative_inputs = np.array([0.9, 1.9, 2.9, 3.9])
    original_inputs = np.array([1.0, 2.0, 3.0, 4.0])

    result = calculate_backward_coefficients(
        negative_outputs,
        unperturbed_output,
        negative_inputs,
        original_inputs,
        relative_flag=False,
    )

    assert result.shape == negative_outputs.shape


def test_backward_coefficients_negative_perturbation():
    """Ensure negative perturbations behave correctly."""
    negative_outputs = np.array([12.0])  # output higher than unperturbed
    unperturbed_output = 10.0
    negative_inputs = np.array([1.2])
    original_inputs = np.array([1.0])

    expected = (10.0 - 12.0) / (1.0 - 1.2)

    result = calculate_backward_coefficients(
        negative_outputs,
        unperturbed_output,
        negative_inputs,
        original_inputs,
        relative_flag=False,
    )

    assert np.allclose(result, expected)
