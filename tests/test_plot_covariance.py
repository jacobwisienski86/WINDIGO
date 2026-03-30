"""
Unit tests for plot_covariance.
"""

import pytest
import numpy as np


@pytest.fixture
def mock_plotting(monkeypatch):
    """
    Mock matplotlib and seaborn so no real files or windows are created.
    """

    class MockFig:
        def tight_layout(self):
            pass

    class MockAx:
        def set_aspect(self, aspect):
            pass

    def fake_subplots(figsize=None, dpi=None):
        return MockFig(), MockAx()

    def fake_heatmap(data, cmap=None):
        return None

    def fake_savefig(filename, bbox_inches=None):
        fake_savefig.saved_filename = filename

    monkeypatch.setattr("matplotlib.pyplot.subplots", fake_subplots)
    monkeypatch.setattr("matplotlib.pyplot.savefig", fake_savefig)
    monkeypatch.setattr("seaborn.heatmap", fake_heatmap)

    return fake_savefig


def test_plot_covariance_filename(mock_plotting):
    """
    Test that plot_covariance generates the correct filename and calls savefig.
    """

    from src.WENDIGO.sandy_internal_functions import plot_covariance

    covariance_data = np.array([[1, 2], [3, 4]])
    energy_grid = [1e-5, 1e-3, 1e-1]
    nuclide = "U235"
    mt_number = 102
    flag_string = "Absolute"

    filename = plot_covariance(
        covariance_data,
        energy_grid,
        nuclide,
        mt_number,
        flag_string
    )

    expected = "covariancePlot_3Groups_U235MT102_Absolute.png"

    assert filename == expected
    assert mock_plotting.saved_filename == expected


def test_plot_covariance_non_square_matrix(mock_plotting):
    """
    Test that the function still attempts to plot and save a file even when
    the covariance matrix is non-square.
    """

    from src.WENDIGO.sandy_internal_functions import plot_covariance

    covariance_data = np.array([[1, 2, 3], [4, 5, 6]])  # 2x3 matrix
    energy_grid = [1e-5, 1e-3]
    nuclide = "Mo98"
    mt_number = 51
    flag_string = "Relative"

    filename = plot_covariance(
        covariance_data,
        energy_grid,
        nuclide,
        mt_number,
        flag_string
    )

    expected = "covariancePlot_2Groups_Mo98MT51_Relative.png"

    assert filename == expected
    assert mock_plotting.saved_filename == expected


def test_plot_covariance_empty_energy_grid(mock_plotting):
    """
    Test that the filename logic works even when the energy grid is empty.
    """

    from src.WENDIGO.sandy_internal_functions import plot_covariance

    covariance_data = np.array([[1]])
    energy_grid = []  # edge case
    nuclide = "H1"
    mt_number = 1
    flag_string = "Absolute"

    filename = plot_covariance(
        covariance_data,
        energy_grid,
        nuclide,
        mt_number,
        flag_string
    )

    expected = "covariancePlot_0Groups_H1MT1_Absolute.png"

    assert filename == expected
    assert mock_plotting.saved_filename == expected