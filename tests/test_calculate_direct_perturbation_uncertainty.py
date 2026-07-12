import numpy as np
import pytest
from unittest.mock import patch, MagicMock

from src.WINDIGO.post_processing_main_functions import (
    calculate_direct_perturbation_uncertainty,
)


# ---------------------------------------------------------------------------
# Forward method
# ---------------------------------------------------------------------------

@patch("src.WINDIGO.post_processing_main_functions.calculate_uncertainty_error")
@patch("src.WINDIGO.post_processing_main_functions.calculate_direct_perturbation_variance_error")
@patch("src.WINDIGO.post_processing_main_functions.calculate_absolute_forward_coefficient_errors")
@patch("src.WINDIGO.post_processing_main_functions.calculate_forward_coefficients")
@patch("src.WINDIGO.post_processing_main_functions.check_input_types")
def test_direct_uncertainty_forward(
    mock_check,
    mock_forward,
    mock_abs_err,
    mock_var_err,
    mock_uncert_err,
):
    """Forward method: dispatch, shape checks, and return values."""

    # Mock input conversion
    mock_check.return_value = [
        np.array([11.0, 22.0]),   # positive outputs
        np.array([]),             # negative outputs
        np.array([[2.0, 0.5],     # covariance matrix
                  [0.5, 3.0]]),
        np.array([1.1, 2.2]),     # positive inputs
        np.array([]),             # negative inputs
        np.array([0.3, 0.4]),     # positive output errors
        np.array([]),             # negative output errors
    ]

    mock_forward.return_value = np.array([1.0, 2.0])
    mock_abs_err.return_value = np.array([0.2, 0.3])
    mock_var_err.return_value = 5.0
    mock_uncert_err.return_value = 1.5

    propagated, error = calculate_direct_perturbation_uncertainty(
        sens_calculation_method="Forward",
        covariance_matrix=[[2.0, 0.5], [0.5, 3.0]],
        unperturbed_output=10.0,
        original_inputs=[1.0, 2.0],
        positive_perturbed_outputs=[11.0, 22.0],
        positive_perturbed_inputs=[1.1, 2.2],
        error_propagation_flag=True,
        unperturbed_output_error=0.5,
        positive_perturbed_output_errors=[0.3, 0.4],
    )

    mock_forward.assert_called_once()
    mock_abs_err.assert_called_once()
    mock_var_err.assert_called_once()
    mock_uncert_err.assert_called_once()

    assert isinstance(propagated, float)
    assert isinstance(error, float)


# ---------------------------------------------------------------------------
# Backward method
# ---------------------------------------------------------------------------

@patch("src.WINDIGO.post_processing_main_functions.calculate_uncertainty_error")
@patch("src.WINDIGO.post_processing_main_functions.calculate_direct_perturbation_variance_error")
@patch("src.WINDIGO.post_processing_main_functions.calculate_absolute_backward_coefficient_errors")
@patch("src.WINDIGO.post_processing_main_functions.calculate_backward_coefficients")
@patch("src.WINDIGO.post_processing_main_functions.check_input_types")
def test_direct_uncertainty_backward(
    mock_check,
    mock_backward,
    mock_abs_err,
    mock_var_err,
    mock_uncert_err,
):
    """Backward method: dispatch and downstream calls."""

    mock_check.return_value = [
        np.array([]),             # positive outputs
        np.array([9.0, 18.0]),    # negative outputs
        np.array([[1.0, 0.2],
                  [0.2, 2.0]]),   # covariance
        np.array([]),             # positive inputs
        np.array([0.9, 1.8]),     # negative inputs
        np.array([]),             # positive output errors
        np.array([0.3, 0.4]),     # negative output errors
    ]

    mock_backward.return_value = np.array([3.0, 4.0])
    mock_abs_err.return_value = np.array([0.2, 0.3])
    mock_var_err.return_value = 4.0
    mock_uncert_err.return_value = 1.0

    propagated, error = calculate_direct_perturbation_uncertainty(
        sens_calculation_method="Backward",
        covariance_matrix=[[1.0, 0.2], [0.2, 2.0]],
        unperturbed_output=10.0,
        original_inputs=[1.0, 2.0],
        negative_perturbed_outputs=[9.0, 18.0],
        negative_perturbed_inputs=[0.9, 1.8],
        error_propagation_flag=True,
        unperturbed_output_error=0.5,
        negative_perturbed_output_errors=[0.3, 0.4],
    )

    mock_backward.assert_called_once()
    mock_abs_err.assert_called_once()
    mock_var_err.assert_called_once()
    mock_uncert_err.assert_called_once()

    assert isinstance(propagated, float)
    assert isinstance(error, float)


# ---------------------------------------------------------------------------
# Central method
# ---------------------------------------------------------------------------

@patch("src.WINDIGO.post_processing_main_functions.calculate_uncertainty_error")
@patch("src.WINDIGO.post_processing_main_functions.calculate_direct_perturbation_variance_error")
@patch("src.WINDIGO.post_processing_main_functions.calculate_absolute_central_coefficient_errors")
@patch("src.WINDIGO.post_processing_main_functions.calculate_central_coefficients")
@patch("src.WINDIGO.post_processing_main_functions.check_input_types")
def test_direct_uncertainty_central(
    mock_check,
    mock_central,
    mock_abs_err,
    mock_var_err,
    mock_uncert_err,
):
    """Central method: dispatch and downstream calls."""

    mock_check.return_value = [
        np.array([11.0, 22.0]),   # positive outputs
        np.array([9.0, 18.0]),    # negative outputs
        np.array([[2.0, 0.5],
                  [0.5, 3.0]]),   # covariance
        np.array([1.1, 2.2]),     # positive inputs
        np.array([0.9, 1.8]),     # negative inputs
        np.array([0.3, 0.4]),     # positive output errors
        np.array([0.2, 0.3]),     # negative output errors
    ]

    mock_central.return_value = np.array([5.0, 6.0])
    mock_abs_err.return_value = np.array([0.2, 0.3])
    mock_var_err.return_value = 10.0
    mock_uncert_err.return_value = 2.0

    propagated, error = calculate_direct_perturbation_uncertainty(
        sens_calculation_method="Central",
        covariance_matrix=[[2.0, 0.5], [0.5, 3.0]],
        unperturbed_output=10.0,
        original_inputs=[1.0, 2.0],
        positive_perturbed_outputs=[11.0, 22.0],
        negative_perturbed_outputs=[9.0, 18.0],
        positive_perturbed_inputs=[1.1, 2.2],
        negative_perturbed_inputs=[0.9, 1.8],
        error_propagation_flag=True,
        positive_perturbed_output_errors=[0.3, 0.4],
        negative_perturbed_output_errors=[0.2, 0.3],
    )

    mock_central.assert_called_once()
    mock_abs_err.assert_called_once()
    mock_var_err.assert_called_once()
    mock_uncert_err.assert_called_once()

    assert isinstance(propagated, float)
    assert isinstance(error, float)


# ---------------------------------------------------------------------------
# Invalid method
# ---------------------------------------------------------------------------

def test_direct_uncertainty_invalid_method():
    """Invalid sensitivity method should raise an exception."""
    with pytest.raises(Exception):
        calculate_direct_perturbation_uncertainty(
            sens_calculation_method="NotARealMethod",
            covariance_matrix=[[1.0]],
            original_inputs=[1.0],
        )


# ---------------------------------------------------------------------------
# Covariance matrix shape validation
# ---------------------------------------------------------------------------

def test_direct_uncertainty_non_square_covariance():
    """Non-square covariance matrix should raise."""
    with pytest.raises(Exception):
        calculate_direct_perturbation_uncertainty(
            sens_calculation_method="Forward",
            covariance_matrix=[[1.0, 2.0]],
            original_inputs=[1.0],
            positive_perturbed_outputs=[10.0],
            positive_perturbed_inputs=[1.1],
            unperturbed_output=10.0,
        )


def test_direct_uncertainty_covariance_size_mismatch():
    """Covariance matrix size must match original_inputs length."""
    with pytest.raises(Exception):
        calculate_direct_perturbation_uncertainty(
            sens_calculation_method="Forward",
            covariance_matrix=[[1.0, 0.2], [0.2, 1.0]],
            original_inputs=[1.0],  # mismatch
            positive_perturbed_outputs=[10.0],
            positive_perturbed_inputs=[1.1],
            unperturbed_output=10.0,
        )
