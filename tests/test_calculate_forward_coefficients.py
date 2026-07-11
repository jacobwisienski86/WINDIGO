import numpy as np

from src.WINDIGO.post_processing_internal_functions import (
    calculate_forward_coefficients,
)


def test_forward_coefficients_absolute_basic():
    """Test absolute forward-difference sensitivity calculation."""
    positive_outputs = np.array([12.0, 22.0, 42.0])
    unperturbed_output = 10.0
    positive_inputs = np.array([1.2, 2.3, 4.5])   # ensure no zero denominators
    original_inputs = np.array([1.0, 2.0, 4.0])

    expected = (positive_outputs - unperturbed_output) / (
        positive_inputs - original_inputs
    )

    result = calculate_forward_coefficients(
        positive_outputs,
        unperturbed_output,
        positive_inputs,
        original_inputs,
        relative_flag=False,
    )

    assert np.allclose(result, expected)


def test_forward_coefficients_relative_basic():
    """Test relative sensitivity calculation."""
    positive_outputs = np.array([12.0, 22.0, 42.0])
    unperturbed_output = 10.0
    positive_inputs = np.array([1.2, 2.3, 4.5])
    original_inputs = np.array([1.0, 2.0, 4.0])

    absolute = (positive_outputs - unperturbed_output) / (
        positive_inputs - original_inputs
    )
    expected = absolute * (original_inputs / unperturbed_output)

    result = calculate_forward_coefficients(
        positive_outputs,
        unperturbed_output,
        positive_inputs,
        original_inputs,
        relative_flag=True,
    )

    assert np.allclose(result, expected)


def test_forward_coefficients_shape_preserved():
    """Ensure output shape matches input shape."""
    positive_outputs = np.array([11.0, 21.0, 31.0, 41.0])
    unperturbed_output = 10.0
    positive_inputs = np.array([1.2, 2.2, 3.2, 4.2])
    original_inputs = np.array([1.0, 2.0, 3.0, 4.0])

    result = calculate_forward_coefficients(
        positive_outputs,
        unperturbed_output,
        positive_inputs,
        original_inputs,
        relative_flag=False,
    )

    assert result.shape == positive_outputs.shape


def test_forward_coefficients_negative_perturbation():
    """Ensure negative perturbations behave correctly."""
    positive_outputs = np.array([8.0])
    unperturbed_output = 10.0
    positive_inputs = np.array([0.8])
    original_inputs = np.array([1.0])

    expected = (8.0 - 10.0) / (0.8 - 1.0)

    result = calculate_forward_coefficients(
        positive_outputs,
        unperturbed_output,
        positive_inputs,
        original_inputs,
        relative_flag=False,
    )

    assert np.allclose(result, expected)
