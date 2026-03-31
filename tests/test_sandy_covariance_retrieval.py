"""
Unit tests for sandy_covariance_retrieval.
"""

import pytest
import numpy as np


@pytest.fixture
def mock_internal_functions(monkeypatch):
    """
    Mock all internal Sandy-related functions used by sandy_covariance_retrieval.
    """

    # Mock retrieve_nuclide_information
    def fake_retrieve_nuclide_information(nuclide):
        return 999999  # fake ZZZAAA number

    # Mock retrieve_covariance_data
    def fake_retrieve_covariance_data(
        energy_grid,
        nuclide,
        mt_Number,
        data_library,
        nuclide_number,
        temperature,
        relative_Flag=False
    ):
        fake_cov = np.array([[1, 2], [3, 4]])
        fake_flag = "Absolute"
        return fake_cov, fake_flag

    # Mock plot_covariance
    def fake_plot_covariance(
        covariance_data,
        energy_grid,
        nuclide,
        mt_Number,
        flag_String
    ):
        return "fake_plot.png"

    # Mock save_covariance_file
    def fake_save_covariance_file(
        covariance_data,
        energy_grid,
        nuclide,
        mt_Number,
        flag_String
    ):
        return "fake_output.csv"

    # IMPORTANT: patch the functions *as imported inside sandy_main_functions.py*
    monkeypatch.setattr(
        "src.WINDIGO.sandy_internal_functions.retrieve_nuclide_information",
        fake_retrieve_nuclide_information
    )
    monkeypatch.setattr(
        "src.WINDIGO.sandy_internal_functions.retrieve_covariance_data",
        fake_retrieve_covariance_data
    )
    monkeypatch.setattr(
        "src.WINDIGO.sandy_internal_functions.plot_covariance",
        fake_plot_covariance
    )
    monkeypatch.setattr(
        "src.WINDIGO.sandy_internal_functions.save_covariance_file",
        fake_save_covariance_file
    )


def test_sandy_covariance_retrieval_no_plot(mock_internal_functions):
    """
    Test sandy_covariance_retrieval when plotting is disabled.
    """

    from src.WINDIGO.sandy_main_functions import sandy_covariance_retrieval

    csv_filename = sandy_covariance_retrieval(
        energy_grid=[1e-5, 1e-3],
        nuclide="U235",
        mt_Number=102,
        data_library="endfb_80",
        temperature=300,
        relative_Flag=False,
        plotting_Flag=False
    )

    assert csv_filename == "fake_output.csv"


def test_sandy_covariance_retrieval_with_plot(mock_internal_functions):
    """
    Test sandy_covariance_retrieval when plotting is enabled.
    """

    from src.WINDIGO.sandy_main_functions import sandy_covariance_retrieval

    csv_filename, plot_filename = sandy_covariance_retrieval(
        energy_grid=[1e-5, 1e-3],
        nuclide="U235",
        mt_Number=102,
        data_library="endfb_80",
        temperature=300,
        relative_Flag=True,
        plotting_Flag=True
    )

    assert csv_filename == "fake_output.csv"
    assert plot_filename == "fake_plot.png"