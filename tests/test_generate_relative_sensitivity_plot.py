import numpy as np
import pytest
from unittest.mock import patch

from src.WINDIGO.post_processing_main_functions import (
    generate_relative_sensitivity_plot,
)


# ---------------------------------------------------------------------------
# Forward method
# ---------------------------------------------------------------------------

@patch("src.WINDIGO.post_processing_main_functions.plot_relative_sens")
@patch("src.WINDIGO.post_processing_main_functions.convert_per_lethargy")
@patch("src.WINDIGO.post_processing_main_functions.calculate_forward_coefficients")
@patch("src.WINDIGO.post_processing_main_functions.check_input_types")
def test_generate_plot_forward(
    mock_check, mock_forward, mock_convert, mock_plot
):
    """Forward method: dispatch and downstream calls."""

    mock_check.return_value = [
        np.array([1.0, 2.0, 4.0]),   # energy grid
        np.array([1.0, 2.0]),        # original inputs
        np.array([11.0, 22.0]),      # positive outputs
        np.array([]),                # negative outputs
        np.array([1.1, 2.2]),        # positive inputs
        np.array([]),                # negative inputs
    ]

    mock_forward.return_value = np.array([1.0, 2.0])
    mock_convert.return_value = np.array([0.0, 1.0, 2.0])

    generate_relative_sensitivity_plot(
        energy_grid_MeV=[1.0, 2.0, 4.0],
        sens_calculation_method="Forward",
        unperturbed_output=10.0,
        original_inputs=[1.0, 2.0],
        positive_perturbed_outputs=[11.0, 22.0],
        positive_perturbed_inputs=[1.1, 2.2],
    )

    mock_check.assert_called_once()
    mock_forward.assert_called_once()
    mock_convert.assert_called_once()
    mock_plot.assert_called_once()


# ---------------------------------------------------------------------------
# Backward method
# ---------------------------------------------------------------------------

@patch("src.WINDIGO.post_processing_main_functions.plot_relative_sens")
@patch("src.WINDIGO.post_processing_main_functions.convert_per_lethargy")
@patch("src.WINDIGO.post_processing_main_functions.calculate_backward_coefficients")
@patch("src.WINDIGO.post_processing_main_functions.check_input_types")
def test_generate_plot_backward(
    mock_check, mock_backward, mock_convert, mock_plot
):
    """Backward method: dispatch and downstream calls."""

    mock_check.return_value = [
        np.array([1.0, 2.0, 4.0]),   # energy grid
        np.array([1.0, 2.0]),        # original inputs
        np.array([]),                # positive outputs
        np.array([9.0, 18.0]),       # negative outputs
        np.array([]),                # positive inputs
        np.array([0.9, 1.8]),        # negative inputs
    ]

    mock_backward.return_value = np.array([3.0, 4.0])
    mock_convert.return_value = np.array([0.0, 3.0, 4.0])

    generate_relative_sensitivity_plot(
        energy_grid_MeV=[1.0, 2.0, 4.0],
        sens_calculation_method="Backward",
        unperturbed_output=10.0,
        original_inputs=[1.0, 2.0],
        negative_perturbed_outputs=[9.0, 18.0],
        negative_perturbed_inputs=[0.9, 1.8],
    )

    mock_check.assert_called_once()
    mock_backward.assert_called_once()
    mock_convert.assert_called_once()
    mock_plot.assert_called_once()


# ---------------------------------------------------------------------------
# Central method
# ---------------------------------------------------------------------------

@patch("src.WINDIGO.post_processing_main_functions.plot_relative_sens")
@patch("src.WINDIGO.post_processing_main_functions.convert_per_lethargy")
@patch("src.WINDIGO.post_processing_main_functions.calculate_central_coefficients")
@patch("src.WINDIGO.post_processing_main_functions.check_input_types")
def test_generate_plot_central(
    mock_check, mock_central, mock_convert, mock_plot
):
    """Central method: uses only perturbed outputs, not perturbed inputs."""

    mock_check.return_value = [
        np.array([1.0, 2.0, 4.0]),   # energy grid
        np.array([1.0, 2.0]),        # original inputs
        np.array([11.0, 22.0]),      # positive outputs
        np.array([9.0, 18.0]),       # negative outputs
        np.array([]),                # positive inputs (unused)
        np.array([]),                # negative inputs (unused)
    ]

    mock_central.return_value = np.array([5.0, 6.0])
    mock_convert.return_value = np.array([0.0, 5.0, 6.0])

    generate_relative_sensitivity_plot(
        energy_grid_MeV=[1.0, 2.0, 4.0],
        sens_calculation_method="Central",
        unperturbed_output=10.0,
        original_inputs=[1.0, 2.0],
        positive_perturbed_outputs=[11.0, 22.0],
        negative_perturbed_outputs=[9.0, 18.0],
        perturbation_coefficient=0.1,
    )

    mock_check.assert_called_once()
    mock_central.assert_called_once()
    mock_convert.assert_called_once()
    mock_plot.assert_called_once()


# ---------------------------------------------------------------------------
# Invalid method
# ---------------------------------------------------------------------------

def test_generate_plot_invalid_method():
    """Invalid sensitivity method should raise an exception."""

    with pytest.raises(Exception):
        generate_relative_sensitivity_plot(
            energy_grid_MeV=[1.0, 2.0],
            sens_calculation_method="NotARealMethod",
            unperturbed_output=10.0,
            original_inputs=[1.0],
        )
