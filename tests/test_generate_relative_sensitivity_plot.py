import numpy as np
import pytest
from unittest.mock import patch, MagicMock

from src.WINDIGO.post_processing_main_functions import (
    generate_relative_sensitivity_plot,
)

MAIN = "src.WINDIGO.post_processing_main_functions"


# ---------------------------------------------------------------------------
# Forward (no error propagation)
# ---------------------------------------------------------------------------

@patch(f"{MAIN}.plot_relative_sens")
@patch(f"{MAIN}.convert_per_lethargy")
@patch(f"{MAIN}.calculate_forward_coefficients")
@patch(f"{MAIN}.check_input_types")
def test_generate_relative_sensitivity_plot_forward_no_errors(
    mock_check_types,
    mock_forward_coeffs,
    mock_convert,
    mock_plot,
):
    """Forward method without error propagation."""
    mock_check_types.return_value = [
        np.array([1.0, 2.0, 4.0]),
        np.array([10.0]),
        np.array([11.0]),
        np.array([]),
        np.array([1.1]),
        np.array([]),
        np.array([]),
        np.array([]),
    ]

    mock_forward_coeffs.return_value = np.array([0.1])
    mock_convert.return_value = np.array([0.0, 0.1])

    generate_relative_sensitivity_plot(
        energy_grid_MeV=[1.0, 2.0, 4.0],
        sens_calculation_method="Forward",
        unperturbed_output=10.0,
        original_inputs=[10.0],
        positive_perturbed_outputs=[11.0],
        positive_perturbed_inputs=[1.1],
        error_propagation_flag=False,
    )

    mock_forward_coeffs.assert_called_once()
    mock_convert.assert_called_once()
    mock_plot.assert_called_once()

    _, kwargs = mock_plot.call_args
    assert kwargs["error_propagation_flag"] is False
    assert kwargs["relative_sens_error_per_lethargy"] is None


# ---------------------------------------------------------------------------
# Backward (no error propagation)
# ---------------------------------------------------------------------------

@patch(f"{MAIN}.plot_relative_sens")
@patch(f"{MAIN}.convert_per_lethargy")
@patch(f"{MAIN}.calculate_backward_coefficients")
@patch(f"{MAIN}.check_input_types")
def test_generate_relative_sensitivity_plot_backward_no_errors(
    mock_check_types,
    mock_backward_coeffs,
    mock_convert,
    mock_plot,
):
    """Backward method without error propagation."""
    mock_check_types.return_value = [
        np.array([1.0, 2.0]),
        np.array([10.0]),
        np.array([]),
        np.array([9.0]),
        np.array([]),
        np.array([0.9]),
        np.array([]),
        np.array([]),
    ]

    mock_backward_coeffs.return_value = np.array([0.2])
    mock_convert.return_value = np.array([0.0, 0.2])

    generate_relative_sensitivity_plot(
        energy_grid_MeV=[1.0, 2.0],
        sens_calculation_method="Backward",
        unperturbed_output=10.0,
        original_inputs=[10.0],
        negative_perturbed_outputs=[9.0],
        negative_perturbed_inputs=[0.9],
        error_propagation_flag=False,
    )

    mock_backward_coeffs.assert_called_once()
    mock_convert.assert_called_once()
    mock_plot.assert_called_once()

    _, kwargs = mock_plot.call_args
    assert kwargs["error_propagation_flag"] is False
    assert kwargs["relative_sens_error_per_lethargy"] is None


# ---------------------------------------------------------------------------
# Central (no error propagation)
# ---------------------------------------------------------------------------

@patch(f"{MAIN}.plot_relative_sens")
@patch(f"{MAIN}.convert_per_lethargy")
@patch(f"{MAIN}.calculate_central_coefficients")
@patch(f"{MAIN}.check_input_types")
def test_generate_relative_sensitivity_plot_central_no_errors(
    mock_check_types,
    mock_central_coeffs,
    mock_convert,
    mock_plot,
):
    """Central method without error propagation."""
    mock_check_types.return_value = [
        np.array([1.0, 2.0]),
        np.array([10.0]),
        np.array([11.0]),
        np.array([9.0]),
        np.array([1.1]),
        np.array([0.9]),
        np.array([]),
        np.array([]),
    ]

    mock_central_coeffs.return_value = np.array([0.3])
    mock_convert.return_value = np.array([0.0, 0.3])

    generate_relative_sensitivity_plot(
        energy_grid_MeV=[1.0, 2.0],
        sens_calculation_method="Central",
        unperturbed_output=10.0,
        original_inputs=[10.0],
        positive_perturbed_outputs=[11.0],
        negative_perturbed_outputs=[9.0],
        positive_perturbed_inputs=[1.1],
        negative_perturbed_inputs=[0.9],
        error_propagation_flag=False,
    )

    mock_central_coeffs.assert_called_once()
    mock_convert.assert_called_once()
    mock_plot.assert_called_once()

    _, kwargs = mock_plot.call_args
    assert kwargs["error_propagation_flag"] is False
    assert kwargs["relative_sens_error_per_lethargy"] is None


# ---------------------------------------------------------------------------
# Forward (with error propagation)
# ---------------------------------------------------------------------------

@patch(f"{MAIN}.plot_relative_sens")
@patch(f"{MAIN}.convert_per_lethargy")
@patch(f"{MAIN}.calculate_relative_forward_coefficient_errors")
@patch(f"{MAIN}.calculate_forward_coefficients")
@patch(f"{MAIN}.check_input_types")
def test_generate_relative_sensitivity_plot_forward_with_errors(
    mock_check_types,
    mock_forward_coeffs,
    mock_forward_errors,
    mock_convert,
    mock_plot,
):
    """Forward method with error propagation."""
    mock_check_types.return_value = [
        np.array([1.0, 2.0]),
        np.array([10.0]),
        np.array([11.0]),
        np.array([]),
        np.array([1.1]),
        np.array([]),
        np.array([0.1]),
        np.array([]),
    ]

    mock_forward_coeffs.return_value = np.array([0.1])
    mock_forward_errors.return_value = np.array([0.01])

    mock_convert.side_effect = [
        np.array([0.0, 0.1]),   # sensitivities
        np.array([0.0, 0.01]),  # errors
    ]

    generate_relative_sensitivity_plot(
        energy_grid_MeV=[1.0, 2.0],
        sens_calculation_method="Forward",
        unperturbed_output=10.0,
        original_inputs=[10.0],
        positive_perturbed_outputs=[11.0],
        positive_perturbed_inputs=[1.1],
        error_propagation_flag=True,
        unperturbed_output_error=0.5,
        positive_perturbed_output_errors=[0.1],
    )

    mock_forward_errors.assert_called_once()
    assert mock_convert.call_count == 2
    mock_plot.assert_called_once()

    _, kwargs = mock_plot.call_args
    assert kwargs["error_propagation_flag"] is True
    np.testing.assert_allclose(kwargs["relative_sens_error_per_lethargy"],
                               np.array([0.0, 0.01]))


# ---------------------------------------------------------------------------
# Invalid method
# ---------------------------------------------------------------------------

def test_generate_relative_sensitivity_plot_invalid_method():
    """Invalid sensitivity method should raise an exception."""
    with pytest.raises(Exception):
        generate_relative_sensitivity_plot(
            energy_grid_MeV=[1.0, 2.0],
            sens_calculation_method="NotARealMethod",
            unperturbed_output=10.0,
            original_inputs=[10.0],
        )
