import numpy as np

from src.WINDIGO.post_processing_internal_functions import (
    calculate_relative_central_coefficient_errors,
)


def test_relative_central_errors_basic():
    """Test basic central-differencing relative coefficient error calculation."""
    original_inputs = np.array([1.0, 2.0, 3.0])
    positive_perturbed_inputs = np.array([1.1, 2.2, 3.3])
    negative_perturbed_inputs = np.array([0.9, 1.8, 2.7])

    unperturbed_output = 10.0
    positive_perturbed_outputs = np.array([11.0, 22.0, 33.0])
    negative_perturbed_outputs = np.array([9.0, 18.0, 27.0])

    unperturbed_output_error = 0.5
    positive_perturbed_output_errors = np.array([0.1, 0.2, 0.3])
    negative_perturbed_output_errors = np.array([0.05, 0.1, 0.15])

    # Manual expected calculation
    input_factor = original_inputs / (positive_perturbed_inputs - negative_perturbed_inputs)

    term1 = (input_factor / unperturbed_output**2) * (
        negative_perturbed_outputs - positive_perturbed_outputs
    )
    term2 = input_factor * (1 / unperturbed_output)
    term3 = input_factor * (-1 / unperturbed_output)

    expected = np.sqrt(
        term1**2 * unperturbed_output_error**2
        + term2**2 * positive_perturbed_output_errors**2
        + term3**2 * negative_perturbed_output_errors**2
    )

    result = calculate_relative_central_coefficient_errors(
        original_inputs,
        positive_perturbed_inputs,
        negative_perturbed_inputs,
        unperturbed_output,
        positive_perturbed_outputs,
        negative_perturbed_outputs,
        unperturbed_output_error,
        positive_perturbed_output_errors,
        negative_perturbed_output_errors,
    )

    np.testing.assert_allclose(result, expected)


def test_relative_central_errors_shape():
    """Ensure output shape matches input array shape."""
    original_inputs = np.array([1.0, 2.0])
    positive_perturbed_inputs = np.array([1.2, 2.4])
    negative_perturbed_inputs = np.array([0.8, 1.6])

    unperturbed_output = 5.0
    positive_perturbed_outputs = np.array([6.0, 12.0])
    negative_perturbed_outputs = np.array([4.0, 8.0])

    unperturbed_output_error = 0.1
    positive_perturbed_output_errors = np.array([0.01, 0.02])
    negative_perturbed_output_errors = np.array([0.02, 0.04])

    result = calculate_relative_central_coefficient_errors(
        original_inputs,
        positive_perturbed_inputs,
        negative_perturbed_inputs,
        unperturbed_output,
        positive_perturbed_outputs,
        negative_perturbed_outputs,
        unperturbed_output_error,
        positive_perturbed_output_errors,
        negative_perturbed_output_errors,
    )

    assert result.shape == original_inputs.shape


def test_relative_central_errors_nonuniform_inputs():
    """Test correctness with non-uniform spacing in perturbed inputs."""
    original_inputs = np.array([2.0, 10.0])
    positive_perturbed_inputs = np.array([3.0, 20.0])
    negative_perturbed_inputs = np.array([1.0, 5.0])

    unperturbed_output = 4.0
    positive_perturbed_outputs = np.array([8.0, 40.0])
    negative_perturbed_outputs = np.array([3.0, 20.0])

    unperturbed_output_error = 0.25
    positive_perturbed_output_errors = np.array([0.5, 1.0])
    negative_perturbed_output_errors = np.array([0.4, 0.8])

    input_factor = original_inputs / (positive_perturbed_inputs - negative_perturbed_inputs)
    term1 = (input_factor / unperturbed_output**2) * (
        negative_perturbed_outputs - positive_perturbed_outputs
    )
    term2 = input_factor * (1 / unperturbed_output)
    term3 = input_factor * (-1 / unperturbed_output)

    expected = np.sqrt(
        term1**2 * unperturbed_output_error**2
        + term2**2 * positive_perturbed_output_errors**2
        + term3**2 * negative_perturbed_output_errors**2
    )

    result = calculate_relative_central_coefficient_errors(
        original_inputs,
        positive_perturbed_inputs,
        negative_perturbed_inputs,
        unperturbed_output,
        positive_perturbed_outputs,
        negative_perturbed_outputs,
        unperturbed_output_error,
        positive_perturbed_output_errors,
        negative_perturbed_output_errors,
    )

    np.testing.assert_allclose(result, expected)


def test_relative_central_errors_zero_unperturbed_output_error():
    """If unperturbed_output_error is zero, term1 vanishes entirely."""
    original_inputs = np.array([1.0])
    positive_perturbed_inputs = np.array([1.5])
    negative_perturbed_inputs = np.array([0.5])

    unperturbed_output = 10.0
    positive_perturbed_outputs = np.array([12.0])
    negative_perturbed_outputs = np.array([8.0])

    unperturbed_output_error = 0.0
    positive_perturbed_output_errors = np.array([0.4])
    negative_perturbed_output_errors = np.array([0.3])

    input_factor = original_inputs / (positive_perturbed_inputs - negative_perturbed_inputs)

    # term1 disappears entirely
    term2 = input_factor * (1 / unperturbed_output)
    term3 = input_factor * (-1 / unperturbed_output)

    expected = np.sqrt(
        term2**2 * positive_perturbed_output_errors**2
        + term3**2 * negative_perturbed_output_errors**2
    )

    result = calculate_relative_central_coefficient_errors(
        original_inputs,
        positive_perturbed_inputs,
        negative_perturbed_inputs,
        unperturbed_output,
        positive_perturbed_outputs,
        negative_perturbed_outputs,
        unperturbed_output_error,
        positive_perturbed_output_errors,
        negative_perturbed_output_errors,
    )

    np.testing.assert_allclose(result, expected)
