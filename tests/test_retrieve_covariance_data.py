# tests/test_retrieve_covariance_data.py
# Tests for retrieve_covariance_data in sandy_internal_functions.py

import builtins
import numpy as np
import pytest

from src.WINDIGO.sandy_internal_functions import retrieve_covariance_data


class FakeCov:
    """Simple container for covariance data."""
    def __init__(self, data):
        self.data = data


def make_fake_errorr(cov31=None, cov33=None, cov35=None):
    """Construct a fake errorr object with the required structure."""
    return {
        "errorr31": cov31,
        "errorr33": cov33,
        "errorr35": cov35,
    }


def test_retrieve_covariance_data_general_xs(monkeypatch):
    """MT not in special lists → use errorr33."""

    printed = []

    fake_matrix = np.array([[1, 2], [3, 4]])
    fake_cov_obj = FakeCov(fake_matrix)

    fake_errorr = make_fake_errorr(
        cov31=None,
        cov33=type("CovBlock", (), {"get_cov": lambda self, mts: fake_cov_obj})(),
        cov35=None,
    )

    # Mock sandy.get_endf6_file(...).get_errorr(...)
    def fake_get_endf6_file(lib, xs, nuc):
        class FakeEndf:
            def get_errorr(self, err, temperature, errorr_kws, groupr_kws):
                return fake_errorr
        return FakeEndf()

    monkeypatch.setattr(
        "src.WINDIGO.sandy_internal_functions.sandy.get_endf6_file",
        fake_get_endf6_file,
    )

    monkeypatch.setattr(builtins, "print", lambda msg: printed.append(msg))

    cov, flag = retrieve_covariance_data(
        energy_grid=[1, 2, 3],
        mt_Number=102,
        data_library="endfb_80",
        nuclide_number=922350,
        temperature=300,
        err_tolerance=0.1,
        relative_Flag=False,
    )

    assert flag == "Absolute"
    assert np.array_equal(cov, fake_matrix)
    assert any("2 by 2" in msg for msg in printed)


def test_retrieve_covariance_data_nu_related(monkeypatch):
    """MT in {452, 455, 456} → use errorr31."""

    printed = []

    fake_matrix = np.array([[10]])
    fake_cov_obj = FakeCov(fake_matrix)

    fake_errorr = make_fake_errorr(
        cov31=type("CovBlock", (), {"get_cov": lambda self, mts: fake_cov_obj})(),
        cov33=None,
        cov35=None,
    )

    def fake_get_endf6_file(lib, xs, nuc):
        class FakeEndf:
            def get_errorr(self, err, temperature, errorr_kws, groupr_kws):
                return fake_errorr
        return FakeEndf()

    monkeypatch.setattr(
        "src.WINDIGO.sandy_internal_functions.sandy.get_endf6_file",
        fake_get_endf6_file,
    )
    monkeypatch.setattr(builtins, "print", lambda msg: printed.append(msg))

    cov, flag = retrieve_covariance_data(
        energy_grid=[1],
        mt_Number=452,
        data_library="endfb_80",
        nuclide_number=922350,
        temperature=300,
        err_tolerance=0.05,
        relative_Flag=True,
    )

    assert flag == "Relative"
    assert np.array_equal(cov, fake_matrix)
    assert any("1 by 1" in msg for msg in printed)


def test_retrieve_covariance_data_fission_spectrum(monkeypatch):
    """MT = 1018 → use errorr35 (no mts argument)."""

    printed = []

    fake_matrix = np.array([[5, 6]])
    fake_cov_obj = FakeCov(fake_matrix)

    fake_errorr = make_fake_errorr(
        cov31=None,
        cov33=None,
        cov35=type("CovBlock", (), {"get_cov": lambda self: fake_cov_obj})(),
    )

    def fake_get_endf6_file(lib, xs, nuc):
        class FakeEndf:
            def get_errorr(self, err, temperature, errorr_kws, groupr_kws):
                return fake_errorr
        return FakeEndf()

    monkeypatch.setattr(
        "src.WINDIGO.sandy_internal_functions.sandy.get_endf6_file",
        fake_get_endf6_file,
    )
    monkeypatch.setattr(builtins, "print", lambda msg: printed.append(msg))

    cov, flag = retrieve_covariance_data(
        energy_grid=[1, 2],
        mt_Number=1018,
        data_library="endfb_80",
        nuclide_number=922350,
        temperature=300,
        err_tolerance=0.2,
        relative_Flag=False,
    )

    assert flag == "Absolute"
    assert np.array_equal(cov, fake_matrix)
    assert any("1 by 2" in msg for msg in printed)
