import numpy as np
import pytest
from unittest.mock import patch, MagicMock

from src.WINDIGO.post_processing_internal_functions import (
    plot_relative_sens,
)


@patch("src.WINDIGO.post_processing_internal_functions.plt")
def test_plot_relative_sens_basic(mock_plt):
    """Test that the basic step plot is created without error bars."""
    # Mock figure and axes
    mock_fig = MagicMock()
    mock_ax = MagicMock()
    mock_plt.subplots.return_value = (mock_fig, mock_ax)

    relative_sens_per_lethargy = np.array([0.0, 1.0, 2.0, 3.0])
    energy_grid_MeV = np.array([1.0, 2.0, 4.0, 8.0])

    plot_relative_sens(relative_sens_per_lethargy, energy_grid_MeV)

    # Verify step plot call
    mock_ax.step.assert_called_once_with(
        energy_grid_MeV, relative_sens_per_lethargy, color="black"
    )

    # No error bars should be plotted
    mock_ax.errorbar.assert_not_called()

    # Ensure savefig and show were called
    mock_plt.savefig.assert_called_once()
    mock_plt.show.assert_called_once()


@patch("src.WINDIGO.post_processing_internal_functions.plt")
def test_plot_relative_sens_with_errors(mock_plt):
    """Test that error bars are plotted when error_propagation_flag=True."""
    mock_fig = MagicMock()
    mock_ax = MagicMock()
    mock_plt.subplots.return_value = (mock_fig, mock_ax)

    relative_sens_per_lethargy = np.array([0.0, 10.0, 20.0])
    relative_sens_error_per_lethargy = np.array([0.0, 1.0, 2.0])
    energy_grid_MeV = np.array([1.0, 2.0, 10.0])

    # Expected midpoints
    expected_midpoints = np.array([
        0.0,            # inserted zero
        (1.0 + 2.0) / 2,
        (2.0 + 10.0) / 2,
    ])

    plot_relative_sens(
        relative_sens_per_lethargy,
        energy_grid_MeV,
        error_propagation_flag=True,
        relative_sens_error_per_lethargy=relative_sens_error_per_lethargy,
    )

    # Verify step plot call
    mock_ax.step.assert_called_once_with(
        energy_grid_MeV, relative_sens_per_lethargy, color="black"
    )

    # Verify errorbar call
    mock_ax.errorbar.assert_called_once()
    args, kwargs = mock_ax.errorbar.call_args

    # Check x-values (midpoints)
    np.testing.assert_allclose(args[0], expected_midpoints)

    # Check y-values
    np.testing.assert_allclose(args[1], relative_sens_per_lethargy)

    # Check yerr
    np.testing.assert_allclose(kwargs["yerr"], relative_sens_error_per_lethargy)

    # Check formatting options
    assert kwargs["fmt"] == "none"
    assert kwargs["color"] == "black"
    assert kwargs["capsize"] == 3

    mock_plt.savefig.assert_called_once()
    mock_plt.show.assert_called_once()


@patch("src.WINDIGO.post_processing_internal_functions.plt")
def test_plot_relative_sens_no_errors_when_flag_false(mock_plt):
    """Ensure error bars are NOT plotted when flag=False even if errors are provided."""
    mock_fig = MagicMock()
    mock_ax = MagicMock()
    mock_plt.subplots.return_value = (mock_fig, mock_ax)

    relative_sens_per_lethargy = np.array([0.0, 5.0])
    relative_sens_error_per_lethargy = np.array([0.0, 0.5])
    energy_grid_MeV = np.array([1.0, 2.0])

    plot_relative_sens(
        relative_sens_per_lethargy,
        energy_grid_MeV,
        error_propagation_flag=False,
        relative_sens_error_per_lethargy=relative_sens_error_per_lethargy,
    )

    mock_ax.errorbar.assert_not_called()
    mock_plt.savefig.assert_called_once()
    mock_plt.show.assert_called_once()
