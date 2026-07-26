import numpy as np

from src.WINDIGO.post_processing_internal_functions import (
    calculate_relative_backward_coefficient_errors,
)


def test_relative_backward_errors_basic():
    """Test basic backward-differencing relative coefficient error calculation."""
    original_inputs = np.array([1.0, 2.0, 3.0])
    negative_perturbed_inputs = np.array([0.9, 1.8, 2.7])

    unperturbed_output = 10.0
    negative_perturbed_outputs = np.array([9.0, 18.0, 27.0])

    unperturbed_output_error = 0.5
    negative_perturbed_output_errors = np.array([0.1, 0.2, 0.3])

    # Manual expected calculation
    input_factor = original_inputs / (negative_perturbed_inputs - original_inputs)

    term1 = input_factor * (negative_perturbed_outputs / unperturbed_output**2)
    term2 = input_factor * (-1 / unperturbed_output)

    expected = np.sqrt(
        term1**2 * unperturbed_output_error**2
        + term2**2 * negative_perturbed_output_errors**2
    )

    result = calculate_relative_backward_coefficient_errors(
        original_inputs,
        negative_perturbed_inputs,
        unperturbed_output,
        negative_perturbed_outputs,
        unperturbed_output_error,
        negative_perturbed_output_errors,
    )

    np.testing.assert_allclose(result, expected)


def test_relative_backward_errors_shape():
    """Ensure output shape matches input array shape."""
    original_inputs = np.array([1.0, 2.0])
    negative_perturbed_inputs = np.array([0.8, 1.6])

    unperturbed_output = 5.0
    negative_perturbed_outputs = np.array([4.0, 8.0])

    unperturbed_output_error = 0.1
    negative_perturbed_output_errors = np.array([0.01, 0.02])

    result = calculate_relative_backward_coefficient_errors(
        original_inputs,
        negative_perturbed_inputs,
        unperturbed_output,
        negative_perturbed_outputs,
        unperturbed_output_error,
        negative_perturbed_output_errors,
    )

    assert result.shape == original_inputs.shape


def test_relative_backward_errors_nonuniform_inputs():
    """Test correctness with non-uniform spacing in perturbed inputs."""
    original_inputs = np.array([2.0, 10.0])
    negative_perturbed_inputs = np.array([1.0, 5.0])

    unperturbed_output = 4.0
    negative_perturbed_outputs = np.array([3.0, 20.0])

    unperturbed_output_error = 0.25
    negative_perturbed_output_errors = np.array([0.5, 1.0])

    input_factor = original_inputs / (negative_perturbed_inputs - original_inputs)
    term1 = input_factor * (negative_perturbed_outputs / unperturbed_output**2)
    term2 = input_factor * (-1 / unperturbed_output)

    expected = np.sqrt(
        term1**2 * unperturbed_output_error**2
        + term2**2 * negative_perturbed_output_errors**2
    )

    result = calculate_relative_backward_coefficient_errors(
        original_inputs,
        negative_perturbed_inputs,
        unperturbed_output,
        negative_perturbed_outputs,
        unperturbed_output_error,
        negative_perturbed_output_errors,
    )

    np.testing.assert_allclose(result, expected)


def test_relative_backward_errors_zero_output_error():
    """If unperturbed_output_error is zero, only the second term contributes."""
    original_inputs = np.array([1.0])
    negative_perturbed_inputs = np.array([0.5])

    unperturbed_output = 10.0
    negative_perturbed_outputs = np.array([8.0])

    unperturbed_output_error = 0.0
    negative_perturbed_output_errors = np.array([0.4])

    input_factor = original_inputs / (negative_perturbed_inputs - original_inputs)
    term2 = input_factor * (-1 / unperturbed_output)

    expected = np.sqrt(term2**2 * negative_perturbed_output_errors**2)

    result = calculate_relative_backward_coefficient_errors(
        original_inputs,
        negative_perturbed_inputs,
        unperturbed_output,
        negative_perturbed_outputs,
        unperturbed_output_error,
        negative_perturbed_output_errors,
    )

    np.testing.assert_allclose(result, expected)
