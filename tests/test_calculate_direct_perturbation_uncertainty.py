import numpy as np
import pytest
from unittest.mock import patch

from src.WINDIGO.post_processing_main_functions import (
    calculate_direct_perturbation_uncertainty,
)


# ---------------------------------------------------------------------------
# Forward method
# ---------------------------------------------------------------------------

@patch("src.WINDIGO.post_processing_main_functions.calculate_forward_coefficients")
def test_direct_uncertainty_forward(mock_forward):
    """Forward method: correct dispatch and uncertainty calculation."""

    mock_forward.return_value = np.array([1.0, 2.0])

    covariance = np.array([[2.0, 0.0],
                           [0.0, 8.0]])

    result = calculate_direct_perturbation_uncertainty(
        sens_calculation_method="Forward",
        covariance_matrix=covariance,
        unperturbed_output=10.0,
        original_inputs=[1.0, 2.0],
        positive_perturbed_outputs=[11.0, 22.0],
        positive_perturbed_inputs=[1.1, 2.2],
    )

    # [1,2] @ cov = [2,16]
    # dot([2,16],[1,2]) = 2 + 32 = 34
    assert np.isclose(result, np.sqrt(34.0))

    mock_forward.assert_called_once()


# ---------------------------------------------------------------------------
# Backward method
# ---------------------------------------------------------------------------

@patch("src.WINDIGO.post_processing_main_functions.calculate_backward_coefficients")
def test_direct_uncertainty_backward(mock_backward):
    """Backward method: correct dispatch and uncertainty calculation."""

    mock_backward.return_value = np.array([3.0, 4.0])

    covariance = np.array([[1.0, 0.0],
                           [0.0, 9.0]])

    result = calculate_direct_perturbation_uncertainty(
        sens_calculation_method="Backward",
        covariance_matrix=covariance,
        unperturbed_output=10.0,
        original_inputs=[1.0, 2.0],
        negative_perturbed_outputs=[9.0, 18.0],
        negative_perturbed_inputs=[0.9, 1.8],
    )

    # [3,4] @ cov = [3,36]
    # dot([3,36],[3,4]) = 9 + 144 = 153
    assert np.isclose(result, np.sqrt(153.0))

    mock_backward.assert_called_once()


# ---------------------------------------------------------------------------
# Central method (corrected)
# ---------------------------------------------------------------------------

@patch("src.WINDIGO.post_processing_main_functions.calculate_central_coefficients")
def test_direct_uncertainty_central(mock_central):
    """Central method: uses only perturbed outputs."""

    mock_central.return_value = np.array([5.0, 6.0])

    covariance = np.array([[4.0, 0.0],
                           [0.0, 1.0]])

    result = calculate_direct_perturbation_uncertainty(
        sens_calculation_method="Central",
        covariance_matrix=covariance,
        unperturbed_output=10.0,
        original_inputs=[1.0, 2.0],
        positive_perturbed_outputs=[11.0, 22.0],
        negative_perturbed_outputs=[9.0, 18.0],
        perturbation_coefficient=0.1,
    )

    # [5,6] @ cov = [20,6]
    # dot([20,6],[5,6]) = 100 + 36 = 136
    assert np.isclose(result, np.sqrt(136.0))

    mock_central.assert_called_once()


# ---------------------------------------------------------------------------
# Error: covariance matrix must be square
# ---------------------------------------------------------------------------

def test_direct_uncertainty_non_square_covariance():
    covariance = np.array([[1.0, 2.0, 3.0],
                           [4.0, 5.0, 6.0]])

    with pytest.raises(Exception):
        calculate_direct_perturbation_uncertainty(
            sens_calculation_method="Forward",
            covariance_matrix=covariance,
            unperturbed_output=10.0,
            original_inputs=[1.0, 2.0],
            positive_perturbed_outputs=[11.0, 22.0],
            positive_perturbed_inputs=[1.1, 2.2],
        )


# ---------------------------------------------------------------------------
# Error: covariance size must match input length
# ---------------------------------------------------------------------------

def test_direct_uncertainty_covariance_length_mismatch():
    covariance = np.eye(3)  # 3x3 but inputs length = 2

    with pytest.raises(Exception):
        calculate_direct_perturbation_uncertainty(
            sens_calculation_method="Backward",
            covariance_matrix=covariance,
            unperturbed_output=10.0,
            original_inputs=[1.0, 2.0],
            negative_perturbed_outputs=[9.0, 18.0],
            negative_perturbed_inputs=[0.9, 1.8],
        )


# ---------------------------------------------------------------------------
# Error: invalid method
# ---------------------------------------------------------------------------

def test_direct_uncertainty_invalid_method():
    covariance = np.eye(2)

    with pytest.raises(Exception):
        calculate_direct_perturbation_uncertainty(
            sens_calculation_method="NotARealMethod",
            covariance_matrix=covariance,
            unperturbed_output=10.0,
            original_inputs=[1.0, 2.0],
        )


# ---------------------------------------------------------------------------
# Error: shape mismatch for Forward
# ---------------------------------------------------------------------------

def test_direct_uncertainty_forward_shape_error():
    covariance = np.eye(2)

    with pytest.raises(Exception):
        calculate_direct_perturbation_uncertainty(
            sens_calculation_method="Forward",
            covariance_matrix=covariance,
            unperturbed_output=10.0,
            original_inputs=[1.0, 2.0],
            positive_perturbed_outputs=[11.0],   # wrong length
            positive_perturbed_inputs=[1.1, 2.2],
        )


# ---------------------------------------------------------------------------
# Error: shape mismatch for Backward
# ---------------------------------------------------------------------------

def test_direct_uncertainty_backward_shape_error():
    covariance = np.eye(2)

    with pytest.raises(Exception):
        calculate_direct_perturbation_uncertainty(
            sens_calculation_method="Backward",
            covariance_matrix=covariance,
            unperturbed_output=10.0,
            original_inputs=[1.0, 2.0],
            negative_perturbed_outputs=[9.0, 18.0],
            negative_perturbed_inputs=[0.9],  # wrong length
        )


# ---------------------------------------------------------------------------
# Error: shape mismatch for Central
# ---------------------------------------------------------------------------

def test_direct_uncertainty_central_shape_error():
    covariance = np.eye(2)

    with pytest.raises(Exception):
        calculate_direct_perturbation_uncertainty(
            sens_calculation_method="Central",
            covariance_matrix=covariance,
            unperturbed_output=10.0,
            original_inputs=[1.0, 2.0],
            positive_perturbed_outputs=[11.0],     # wrong length
            negative_perturbed_outputs=[9.0, 18.0],
            perturbation_coefficient=0.1,
        )
