import numpy as np

from src.WINDIGO.post_processing_internal_functions import (
    calculate_central_coefficients,
)


def test_central_coefficients_absolute_basic():
    """Test absolute central-difference sensitivity calculation."""
    positive_outputs = np.array([12.0, 22.0, 42.0])
    negative_outputs = np.array([8.0, 18.0, 38.0])
    unperturbed_output = 10.0
    original_inputs = np.array([1.0, 2.0, 4.0])
    perturbation_coefficient = 0.1  # ensure denominator is non-zero

    expected = (positive_outputs - negative_outputs) / (
        2 * perturbation_coefficient * original_inputs
    )

    result = calculate_central_coefficients(
        positive_outputs,
        negative_outputs,
        unperturbed_output,
        original_inputs,
        perturbation_coefficient,
        relative_flag=False,
    )

    assert np.allclose(result, expected)


def test_central_coefficients_relative_basic():
    """Test relative sensitivity calculation."""
    positive_outputs = np.array([12.0, 22.0, 42.0])
    negative_outputs = np.array([8.0, 18.0, 38.0])
    unperturbed_output = 10.0
    original_inputs = np.array([1.0, 2.0, 4.0])
    perturbation_coefficient = 0.1

    absolute = (positive_outputs - negative_outputs) / (
        2 * perturbation_coefficient * original_inputs
    )
    expected = absolute * (original_inputs / unperturbed_output)

    result = calculate_central_coefficients(
        positive_outputs,
        negative_outputs,
        unperturbed_output,
        original_inputs,
        perturbation_coefficient,
        relative_flag=True,
    )

    assert np.allclose(result, expected)


def test_central_coefficients_shape_preserved():
    """Ensure output shape matches input shape."""
    positive_outputs = np.array([11.0, 21.0, 31.0, 41.0])
    negative_outputs = np.array([9.0, 19.0, 29.0, 39.0])
    unperturbed_output = 10.0
    original_inputs = np.array([1.0, 2.0, 3.0, 4.0])
    perturbation_coefficient = 0.1

    result = calculate_central_coefficients(
        positive_outputs,
        negative_outputs,
        unperturbed_output,
        original_inputs,
        perturbation_coefficient,
        relative_flag=False,
    )

    assert result.shape == positive_outputs.shape


def test_central_coefficients_symmetric_behavior():
    """Ensure symmetric perturbations produce expected scaling."""
    # Symmetric outputs around unperturbed_output
    positive_outputs = np.array([11.0])
    negative_outputs = np.array([9.0])
    unperturbed_output = 10.0
    original_inputs = np.array([2.0])
    perturbation_coefficient = 0.05

    expected = (11.0 - 9.0) / (2 * 0.05 * 2.0)

    result = calculate_central_coefficients(
        positive_outputs,
        negative_outputs,
        unperturbed_output,
        original_inputs,
        perturbation_coefficient,
        relative_flag=False,
    )

    assert np.allclose(result, expected)
