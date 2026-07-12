import numpy as np

from src.WINDIGO.post_processing_internal_functions import (
    calculate_mean_error,
)


def test_mean_error_basic():
    """Basic first-order mean error propagation."""
    errs = np.array([0.3, 0.4, 0.5])

    # Manual calculation:
    # mean_error = (1/n) * sqrt(sum(err_i^2))
    n = 3
    expected = (1 / n) * np.sqrt(0.3**2 + 0.4**2 + 0.5**2)

    result = calculate_mean_error(errs)

    assert np.allclose(result, expected)


def test_mean_error_zero_errors():
    """Zero errors should produce zero mean error."""
    errs = np.array([0.0, 0.0, 0.0])

    result = calculate_mean_error(errs)

    assert np.allclose(result, 0.0)


def test_mean_error_negative_errors():
    """
    Negative error values (nonphysical but allowed numerically)
    should behave identically to positive ones because errors are squared.
    """
    errs = np.array([-0.3, -0.4])

    expected = (1 / 2) * np.sqrt(0.3**2 + 0.4**2)

    result = calculate_mean_error(errs)

    assert np.allclose(result, expected)


def test_mean_error_scalar_output():
    """Ensure the function returns a scalar float."""
    errs = np.array([0.1, 0.2, 0.3])

    result = calculate_mean_error(errs)

    assert isinstance(result, float)
