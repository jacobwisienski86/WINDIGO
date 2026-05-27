import numpy as np
import pytest
from unittest.mock import patch, Mock

from src.WINDIGO.post_processing_internal_functions import (
    plot_relative_sens,
)


@patch("src.WINDIGO.post_processing_internal_functions.plt.show")
@patch("src.WINDIGO.post_processing_internal_functions.plt.savefig")
@patch("src.WINDIGO.post_processing_internal_functions.plt.subplots")
def test_plot_relative_sens_basic(mock_subplots, mock_savefig, mock_show):
    """Ensure the plotting function calls Matplotlib correctly."""

    # Mock figure and axis objects
    mock_fig = object()
    mock_ax = Mock()

    # Configure subplots() to return our mock fig/ax
    mock_subplots.return_value = (mock_fig, mock_ax)

    # Sample inputs
    relative_sens = np.array([0.0, 1.0, 2.0])
    energy_grid = np.array([1.0, 2.0, 4.0])

    # Run the function
    plot_relative_sens(relative_sens, energy_grid)

    # subplots() should be called once with figsize
    mock_subplots.assert_called_once_with(figsize=(8, 6))

    # step() should be called with correct data
    mock_ax.step.assert_called_once_with(energy_grid, relative_sens, color="black")

    # savefig should be called with the expected filename
    mock_savefig.assert_called_once()
    args, kwargs = mock_savefig.call_args
    assert args[0] == "RelativeSensitivityPlot.png"

    # show() should be called exactly once
    mock_show.assert_called_once()


@patch("src.WINDIGO.post_processing_internal_functions.plt.show")
@patch("src.WINDIGO.post_processing_internal_functions.plt.savefig")
@patch("src.WINDIGO.post_processing_internal_functions.plt.subplots")
def test_plot_relative_sens_grid_called(mock_subplots, mock_savefig, mock_show):
    """Ensure ax.grid() is called to enable gridlines."""

    mock_fig = object()
    mock_ax = Mock()
    mock_subplots.return_value = (mock_fig, mock_ax)

    relative_sens = np.array([0.0, 1.0])
    energy_grid = np.array([1.0, 2.0])

    plot_relative_sens(relative_sens, energy_grid)

    mock_ax.grid.assert_called_once()


@patch("src.WINDIGO.post_processing_internal_functions.plt.show")
@patch("src.WINDIGO.post_processing_internal_functions.plt.savefig")
@patch("src.WINDIGO.post_processing_internal_functions.plt.subplots")
def test_plot_relative_sens_tick_params(mock_subplots, mock_savefig, mock_show):
    """Ensure tick_params() is called for both x and y axes."""

    mock_fig = object()
    mock_ax = Mock()
    mock_subplots.return_value = (mock_fig, mock_ax)

    relative_sens = np.array([0.0, 1.0])
    energy_grid = np.array([1.0, 2.0])

    plot_relative_sens(relative_sens, energy_grid)

    # tick_params should be called twice: once for x, once for y
    calls = mock_ax.tick_params.call_args_list
    assert len(calls) == 2

    # Validate axis arguments
    assert calls[0].kwargs["axis"] == "x"
    assert calls[1].kwargs["axis"] == "y"
