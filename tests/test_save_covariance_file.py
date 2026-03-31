"""
Unit tests for save_covariance_file.
"""

import pytest
import numpy as np


@pytest.fixture
def mock_file_ops(monkeypatch):
    """
    Mock pandas and os operations so no real files are created.
    """

    class MockDataFrame:
        def __init__(self):
            self.saved_files = []

        def to_csv(self, filename, index=False, header=True):
            # Record filenames written
            self.saved_files.append((filename, index, header))

    mock_df = MockDataFrame()

    # Mock covariance_data.to_csv(...)
    monkeypatch.setattr(
        "pandas.DataFrame.to_csv",
        lambda self, filename, index=False, header=True:
            mock_df.to_csv(filename, index=index, header=header)
    )

    # Mock pandas.read_csv to return a DataFrame-like object
    monkeypatch.setattr(
        "pandas.read_csv",
        lambda filename, skiprows=0: mock_df
    )

    # Mock os.remove
    removed_files = []

    def fake_remove(filename):
        removed_files.append(filename)

    monkeypatch.setattr("os.remove", fake_remove)

    return mock_df, removed_files


def test_save_covariance_file_basic(mock_file_ops):
    """
    Test that save_covariance_file writes the correct filenames and removes
    the intermediate CSV.
    """

    from src.WINDIGO.sandy_internal_functions import save_covariance_file

    mock_df, removed_files = mock_file_ops

    # Fake covariance data with a to_csv method
    class FakeCovariance:
        def to_csv(self, filename, index=False):
            mock_df.to_csv(filename, index=index, header=True)

    covariance_data = FakeCovariance()
    energy_grid = [1e-5, 1e-3, 1e-1]
    nuclide = "U235"
    mt_number = 102
    flag_string = "Absolute"

    filename = save_covariance_file(
        covariance_data,
        energy_grid,
        nuclide,
        mt_number,
        flag_string
    )

    expected = "covarianceMatrix_3Groups_U235_MT_102_Absolute.csv"

    # Check returned filename
    assert filename == expected

    # Check intermediate and final CSV writes
    assert mock_df.saved_files[0][0] == "intermediate_dataframe.csv"
    assert mock_df.saved_files[-1][0] == expected

    # Check intermediate file removal
    assert "intermediate_dataframe.csv" in removed_files


def test_save_covariance_file_empty_energy_grid(mock_file_ops):
    """
    Test filename logic when the energy grid is empty.
    """

    from src.WINDIGO.sandy_internal_functions import save_covariance_file

    mock_df, removed_files = mock_file_ops

    class FakeCovariance:
        def to_csv(self, filename, index=False):
            mock_df.to_csv(filename, index=index, header=True)

    covariance_data = FakeCovariance()
    energy_grid = []  # edge case
    nuclide = "H1"
    mt_number = 1
    flag_string = "Relative"

    filename = save_covariance_file(
        covariance_data,
        energy_grid,
        nuclide,
        mt_number,
        flag_string
    )

    expected = "covarianceMatrix_0Groups_H1_MT_1_Relative.csv"

    assert filename == expected
    assert mock_df.saved_files[-1][0] == expected
    assert "intermediate_dataframe.csv" in removed_files