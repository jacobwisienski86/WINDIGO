"""
Unit tests for retrieve_covariance_data.
"""

import numpy as np
import pytest


class MockCovariance:
    """
    Simple mock object to emulate Sandy covariance objects.
    """

    def __init__(self, data):
        self.data = data

    def get_cov(self, mts):
        return self


class MockErrorr:
    """
    Mock object representing the structure returned by Sandy's get_errorr.
    """

    def __init__(self, cov_data):
        self.errorr31 = MockCovariance(cov_data)
        self.errorr35 = MockCovariance(cov_data)
        self.errorr33 = MockCovariance(cov_data)

    def __getitem__(self, key):
        # Allow errorr["errorr31"] syntax
        return getattr(self, key)


class MockEndf6File:
    """
    Mock object for sandy.get_endf6_file(...).
    """

    def __init__(self, cov_data):
        self.cov_data = cov_data

    def get_errorr(self, err, temperature, errorr_kws, groupr_kws):
        return MockErrorr(self.cov_data)


@pytest.fixture
def mock_sandy(monkeypatch):
    """
    Fixture to mock sandy.get_endf6_file while still using the real Sandy
    module import path.
    """

    def _mock(cov_data):
        def fake_get_endf6_file(data_library, xs, nuclide_number):
            return MockEndf6File(cov_data)

        monkeypatch.setattr(
            "sandy.get_endf6_file",
            fake_get_endf6_file
        )

    return _mock


def test_retrieve_covariance_data_absolute(mock_sandy):
    """
    Test absolute covariance retrieval and MF/MT routing for general XS data.
    """

    from src.WENDIGO.sandy_internal_functions import (
        retrieve_covariance_data
    )

    cov_matrix = np.array([[1.0, 0.5], [0.5, 2.0]])
    mock_sandy(cov_matrix)

    covariance, flag = retrieve_covariance_data(
        energy_grid=[1e-5, 1e-3, 1e-1],
        nuclide="U235",
        mt_Number=102,
        data_library="endfb_80",
        nuclide_number=922350,
        temperature=300,
        relative_Flag=False
    )

    assert flag == "Absolute"
    assert np.array_equal(covariance, cov_matrix)


def test_retrieve_covariance_data_relative(mock_sandy):
    """
    Test relative covariance retrieval and MF/MT routing for nu-related data.
    """

    from src.WENDIGO.sandy_internal_functions import (
        retrieve_covariance_data
    )

    cov_matrix = np.eye(3)
    mock_sandy(cov_matrix)

    covariance, flag = retrieve_covariance_data(
        energy_grid=[1e-5, 1e-3, 1e-1],
        nuclide="U235",
        mt_Number=452,
        data_library="endfb_80",
        nuclide_number=922350,
        temperature=600,
        relative_Flag=True
    )

    assert flag == "Relative"
    assert np.array_equal(covariance, cov_matrix)


def test_retrieve_covariance_data_fission_spectrum(mock_sandy):
    """
    Test MF/MT routing for fission spectrum covariance (MT=1018 → MF=35).
    """

    from src.WENDIGO.sandy_internal_functions import (
        retrieve_covariance_data
    )

    cov_matrix = np.array([[2.0]])
    mock_sandy(cov_matrix)

    covariance, flag = retrieve_covariance_data(
        energy_grid=[1e-5, 1e-3],
        nuclide="U235",
        mt_Number=1018,
        data_library="endfb_80",
        nuclide_number=922350,
        temperature=900,
        relative_Flag=False
    )

    assert flag == "Absolute"
    assert np.array_equal(covariance, cov_matrix)