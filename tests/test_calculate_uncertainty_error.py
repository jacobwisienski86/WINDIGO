import numpy as np

from src.WINDIGO.post_processing_internal_functions import (
    calculate_uncertainty_error,
)


def test_uncertainty_error_basic():
    """Basic uncertainty error calculation."""
    propagated_uncertainty = 4.0
    variance_error = 2.0

    expected = variance_error / (2 * propagated_uncertainty)

    result = calculate_uncertainty_error(
        propagated_uncertainty,
        variance_error,
    )

    assert np.allclose(result, expected)


def test_uncertainty_error_negative_inputs():
    """
    Negative inputs (nonphysical but allowed numerically)
    should behave consistently because the formula is algebraic.
    """
    propagated_uncertainty = -3.0
    variance_error = -6.0

    expected = variance_error / (2 * propagated_uncertainty)

    result = calculate_uncertainty_error(
        propagated_uncertainty,
        variance_error,
    )

    assert np.allclose(result, expected)


def test_uncertainty_error_scalar_output():
    """Ensure the function returns a scalar float."""
    result = calculate_uncertainty_error(5.0, 1.0)
    assert isinstance(result, float)

