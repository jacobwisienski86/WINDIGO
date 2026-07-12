import numpy as np

from src.WINDIGO.post_processing_internal_functions import (
    calculate_direct_perturbation_variance_error,
)


def test_direct_variance_error_basic():
    """Basic variance error calculation using the non-vectorized Sandwich Rule."""
    abs_sens = np.array([1.0, 2.0])
    abs_errs = np.array([0.3, 0.4])
    cov = np.array([
        [2.0, 0.5],
        [0.5, 3.0],
    ])

    # Manual calculation of intermediate terms
    # Term for index 0:
    #   2*a0*cov00 + 2*a1*cov01
    t0 = 2*1.0*2.0 + 2*2.0*0.5

    # Term for index 1:
    #   2*a1*cov11 + 2*a0*cov10
    t1 = 2*2.0*3.0 + 2*1.0*0.5

    expected = np.sqrt(t0**2 * abs_errs[0]**2 + t1**2 * abs_errs[1]**2)

    result = calculate_direct_perturbation_variance_error(
        abs_sens,
        abs_errs,
        cov,
    )

    assert np.allclose(result, expected)


def test_direct_variance_error_negative_covariance():
    """Negative covariance values should be handled correctly."""
    abs_sens = np.array([1.0, -1.0])
    abs_errs = np.array([0.2, 0.3])
    cov = np.array([
        [1.0, -0.5],
        [-0.5, 2.0],
    ])

    # Manual intermediate terms
    t0 = 2*1.0*1.0 + 2*(-1.0)*(-0.5)
    t1 = 2*(-1.0)*2.0 + 2*1.0*(-0.5)

    expected = np.sqrt(t0**2 * abs_errs[0]**2 + t1**2 * abs_errs[1]**2)

    result = calculate_direct_perturbation_variance_error(
        abs_sens,
        abs_errs,
        cov,
    )

    assert np.allclose(result, expected)


def test_direct_variance_error_shape_consistency():
    """Ensure intermediate term count matches sensitivity coefficient count."""
    abs_sens = np.array([1.0, 2.0, 3.0])
    abs_errs = np.array([0.1, 0.2, 0.3])
    cov = np.array([
        [1.0, 0.2, 0.3],
        [0.2, 2.0, 0.4],
        [0.3, 0.4, 3.0],
    ])

    # We only check that the function runs and returns a scalar
    result = calculate_direct_perturbation_variance_error(
        abs_sens,
        abs_errs,
        cov,
    )

    assert isinstance(result, float)


def test_direct_variance_error_zero_sensitivity():
    """Zero sensitivity coefficients should produce zero intermediate terms."""
    abs_sens = np.array([0.0, 0.0])
    abs_errs = np.array([0.5, 0.5])
    cov = np.array([
        [2.0, 1.0],
        [1.0, 3.0],
    ])

    # All intermediate terms = 0 → variance error = 0
    expected = 0.0

    result = calculate_direct_perturbation_variance_error(
        abs_sens,
        abs_errs,
        cov,
    )

    assert np.allclose(result, expected)


def test_direct_variance_error_zero_denominator_suppressed():
    """
    If covariance matrix contains zeros such that intermediate terms become zero,
    ensure no warnings are emitted and NumPy behavior is preserved.
    """
    abs_sens = np.array([1.0])
    abs_errs = np.array([0.5])
    cov = np.array([[0.0]])  # zero covariance → intermediate term = 0

    with np.errstate(divide="ignore", invalid="ignore"):
        result = calculate_direct_perturbation_variance_error(
            abs_sens,
            abs_errs,
            cov,
        )

    # sqrt(0 * err^2) = 0
    assert np.allclose(result, 0.0)
