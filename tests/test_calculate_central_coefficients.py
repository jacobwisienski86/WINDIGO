import numpy as np

from src.WINDIGO.post_processing_internal_functions import (
    calculate_central_coefficients,
)


def test_central_coefficients_absolute_basic():
    """Test absolute central-difference sensitivity calculation."""
    positive_outputs = np.array([12.0, 22.0, 42.0])
    negative_outputs = np.array([8.0, 18.0, 38.0])
    positive_inputs = np.array([1.2, 2.2, 4.2])
    negative_inputs = np.array([0.8, 1.8, 3.8])   # ensure no zero denominators
    original_inputs = np.array([1.0, 2.0, 4.0])
    unperturbed_output = 10.0

    expected = (positive_outputs - negative_outputs) / (
        positive_inputs - negative_inputs
    )

    result = calculate_central_coefficients(
        positive_outputs,
        negative_outputs,
        unperturbed_output,
        original_inputs,
        positive_inputs,
        negative_inputs,
        relative_flag=False,
    )

    assert np.allclose(result, expected)


def test_central_coefficients_relative_basic():
    """Test relative sensitivity calculation."""
    positive_outputs = np.array([12.0, 22.0, 42.0])
    negative_outputs = np.array([8.0, 18.0, 38.0])
    positive_inputs = np.array([1.2, 2.2, 4.2])
    negative_inputs = np.array([0.8, 1.8, 3.8])
    original_inputs = np.array([1.0, 2.0, 4.0])
    unperturbed_output = 10.0

    absolute = (positive_outputs - negative_outputs) / (
        positive_inputs - negative_inputs
    )
    expected = absolute * (original_inputs / unperturbed_output)

    result = calculate_central_coefficients(
        positive_outputs,
        negative_outputs,
        unperturbed_output,
        original_inputs,
        positive_inputs,
        negative_inputs,
        relative_flag=True,
    )

    assert np.allclose(result, expected)


def test_central_coefficients_shape_preserved():
    """Ensure output shape matches input shape."""
    positive_outputs = np.array([11.0, 21.0, 31.0, 41.0])
    negative_outputs = np.array([9.0, 19.0, 29.0, 39.0])
    positive_inputs = np.array([1.1, 2.1, 3.1, 4.1])
    negative_inputs = np.array([0.9, 1.9, 2.9, 3.9])
    original_inputs = np.array([1.0, 2.0, 3.0, 4.0])
    unperturbed_output = 10.0

    result = calculate_central_coefficients(
        positive_outputs,
        negative_outputs,
        unperturbed_output,
        original_inputs,
        positive_inputs,
        negative_inputs,
        relative_flag=False,
    )

    assert result.shape == positive_outputs.shape


def test_central_coefficients_negative_perturbation():
    """Ensure negative perturbations behave correctly."""
    positive_outputs = np.array([12.0])
    negative_outputs = np.array([14.0])  # negative slope
    positive_inputs = np.array([1.2])
    negative_inputs = np.array([1.0])
    original_inputs = np.array([1.0])
    unperturbed_output = 10.0

    expected = (12.0 - 14.0) / (1.2 - 1.0)

    result = calculate_central_coefficients(
        positive_outputs,
        negative_outputs,
        unperturbed_output,
        original_inputs,
        positive_inputs,
        negative_inputs,
        relative_flag=False,
    )

    assert np.allclose(result, expected)
