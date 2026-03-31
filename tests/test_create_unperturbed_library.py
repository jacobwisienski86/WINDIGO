"""
Unit tests for create_unperturbed_library.
"""

import pytest


class MockDataLibrary:
    """Mock replacement for openmc.data.DataLibrary."""

    def __init__(self):
        self.registered = []

    def register_file(self, filename):
        self.registered.append(filename)


@pytest.fixture
def mock_openmc(monkeypatch):
    """Mock openmc.data.DataLibrary so no real OpenMC is used."""

    mock_lib = MockDataLibrary()

    class MockOpenMCData:
        DataLibrary = lambda self=None: mock_lib

    monkeypatch.setattr("openmc.data", MockOpenMCData())

    return mock_lib


@pytest.fixture
def mock_listdir(monkeypatch):
    """Mock os.listdir with custom directory contents."""

    def _mock(path_to_contents):
        def fake_listdir(path):
            return path_to_contents[path]
        monkeypatch.setattr("os.listdir", fake_listdir)

    return _mock


def test_create_unperturbed_library_basic(mock_openmc, mock_listdir):
    """
    Ensure neutron and TSL files are correctly registered.
    """

    from src.WINDIGO.openmc_internal_functions import create_unperturbed_library

    mock_listdir({
        "/neutrons": ["H1.h5", "U235.h5", "junk.txt"],
        "/tsl": ["c_H_in_H2O.h5", "c_O_in_H2O.h5"]
    })

    lib = create_unperturbed_library(
        neutron_sublibrary_path="/neutrons",
        unperturbed_nuclide_list=["H1", "U235"],
        thermal_scatter_sublibrary_path="/tsl",
        unperturbed_TSL_list=["c_H_in_H2O", "c_O_in_H2O"]
    )

    assert set(lib.registered) == {
        "/neutrons/H1.h5",
        "/neutrons/U235.h5",
        "/tsl/c_H_in_H2O.h5",
        "/tsl/c_O_in_H2O.h5"
    }


def test_create_unperturbed_library_no_matches(mock_openmc, mock_listdir):
    """
    If no files match, nothing should be registered.
    """

    from src.WINDIGO.openmc_internal_functions import create_unperturbed_library

    mock_listdir({
        "/neutrons": ["A.h5", "B.h5"],
        "/tsl": ["X.h5"]
    })

    lib = create_unperturbed_library(
        neutron_sublibrary_path="/neutrons",
        unperturbed_nuclide_list=["H1"],
        thermal_scatter_sublibrary_path="/tsl",
        unperturbed_TSL_list=["c_H_in_H2O"]
    )

    assert lib.registered == []


def test_create_unperturbed_library_multiple_matches(mock_openmc, mock_listdir):
    """
    Ensure all matching files are registered, not just the last one.
    """

    from src.WINDIGO.openmc_internal_functions import create_unperturbed_library

    mock_listdir({
        "/neutrons": ["H1_1.h5", "H1_2.h5", "H1_extra.txt"],
        "/tsl": ["c_H_in_H2O_1.h5", "c_H_in_H2O_2.h5"]
    })

    lib = create_unperturbed_library(
        neutron_sublibrary_path="/neutrons",
        unperturbed_nuclide_list=["H1"],
        thermal_scatter_sublibrary_path="/tsl",
        unperturbed_TSL_list=["c_H_in_H2O"]
    )

    assert set(lib.registered) == {
        "/neutrons/H1_1.h5",
        "/neutrons/H1_2.h5",
        "/tsl/c_H_in_H2O_1.h5",
        "/tsl/c_H_in_H2O_2.h5"
    }