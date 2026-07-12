import numpy as np

from src.WINDIGO.post_processing_internal_functions import (
    calculate_random_sampling_variance_error,
)


def test_random_sampling_variance_error_basic():
    """Basic random sampling variance error calculation."""
    outputs = np.array([10.0, 12.0, 14.0])
    mean_output = 12.0
    errs = np.array([0.3, 0.4, 0.5])
    mean_err = 0.2

    # Manual tau calculation
    taus = (outputs - mean_output)**2  # [4, 0, 4]

    # tau_errors = sqrt( (2*sqrt(tau))^2 * err_i^2 + (2*-1*sqrt(tau))^2 * mean_err^2 )
    tau_errors = np.sqrt(
        (2*np.sqrt(taus))**2 * errs**2 +
        (2*(-1)*np.sqrt(taus))**2 * mean_err**2
    )

    expected = (1 / (len(outputs) - 1)) * np.sqrt(np.sum(tau_errors**2))

    result = calculate_random_sampling_variance_error(
        outputs,
        mean_output,
        errs,
        mean_err,
    )

    assert np.allclose(result, expected)


def test_random_sampling_variance_error_zero_errors():
    """Zero perturbed and mean errors should produce zero variance error."""
    outputs = np.array([10.0, 11.0, 12.0])
    mean_output = 11.0
    errs = np.array([0.0, 0.0, 0.0])
    mean_err = 0.0

    result = calculate_random_sampling_variance_error(
        outputs,
        mean_output,
        errs,
        mean_err,
    )

    assert np.allclose(result, 0.0)


def test_random_sampling_variance_error_negative_errors():
    """
    Negative error values (nonphysical but allowed numerically)
    should behave identically to positive ones because errors are squared.
    """
    outputs = np.array([10.0, 12.0])
    mean_output = 11.0
    errs = np.array([-0.3, -0.4])
    mean_err = -0.2

    taus = (outputs - mean_output)**2
    tau_errors = np.sqrt(
        (2*np.sqrt(taus))**2 * errs**2 +
        (2*(-1)*np.sqrt(taus))**2 * mean_err**2
    )
    expected = (1 / (len(outputs) - 1)) * np.sqrt(np.sum(tau_errors**2))

    result = calculate_random_sampling_variance_error(
        outputs,
        mean_output,
        errs,
        mean_err,
    )

    assert np.allclose(result, expected)


def test_random_sampling_variance_error_scalar_output():
    """Ensure the function returns a scalar float."""
    outputs = np.array([10.0, 11.0, 12.0])
    mean_output = 11.0
    errs = np.array([0.1, 0.2, 0.3])
    mean_err = 0.1

    result = calculate_random_sampling_variance_error(
        outputs,
        mean_output,
        errs,
        mean_err,
    )

    assert isinstance(result, float)
