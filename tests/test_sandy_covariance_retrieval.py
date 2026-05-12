# tests/test_sandy_covariance_retrieval.py
# Tests for sandy_covariance_retrieval in sandy_main_functions.py

import builtins
import pytest

from src.WINDIGO.sandy_main_functions import sandy_covariance_retrieval


def test_sandy_covariance_retrieval_no_plot(monkeypatch):
    """Test workflow when plotting_Flag=False."""

    calls = {
        "retrieve_nuclide_information": [],
        "retrieve_covariance_data": [],
        "save_covariance_file": [],
        "print": [],
    }

    # -----------------------------
    # Mock helper functions
    # -----------------------------
    monkeypatch.setattr(
        "src.WINDIGO.sandy_main_functions.retrieve_nuclide_information",
        lambda nuclide: calls["retrieve_nuclide_information"].append(nuclide) or 922350,
    )

    monkeypatch.setattr(
        "src.WINDIGO.sandy_main_functions.retrieve_covariance_data",
        lambda **kwargs: (
            calls["retrieve_covariance_data"].append(kwargs) or
            ([[1, 2], [3, 4]], "Absolute")
        ),
    )

    monkeypatch.setattr(
        "src.WINDIGO.sandy_main_functions.save_covariance_file",
        lambda **kwargs: calls["save_covariance_file"].append(kwargs) or "cov.csv",
    )

    monkeypatch.setattr(
        builtins, "print",
        lambda msg: calls["print"].append(msg),
    )

    # -----------------------------
    # Run function
    # -----------------------------
    result = sandy_covariance_retrieval(
        energy_grid=[1, 2, 3],
        nuclide="U235",
        mt_Number=102,
        data_library="endfb_80",
        temperature=300,
        err_tolerance=0.1,
        relative_Flag=False,
        plotting_Flag=False,
    )

    # -----------------------------
    # Validate return value
    # -----------------------------
    assert result == "cov.csv"

    # -----------------------------
    # Validate helper calls
    # -----------------------------
    assert calls["retrieve_nuclide_information"] == ["U235"]

    rc = calls["retrieve_covariance_data"][0]
    assert rc["nuclide_number"] == 922350
    assert rc["mt_Number"] == 102
    assert rc["data_library"] == "endfb_80"
    assert rc["temperature"] == 300
    assert rc["err_tolerance"] == 0.1
    assert rc["relative_Flag"] is False

    sc = calls["save_covariance_file"][0]
    assert sc["nuclide"] == "U235"
    assert sc["mt_Number"] == 102
    assert sc["flag_String"] == "Absolute"

    # -----------------------------
    # Validate printed output
    # -----------------------------
    assert any("Covariance Retrieval Process Complete" in msg for msg in calls["print"])


def test_sandy_covariance_retrieval_with_plot(monkeypatch):
    """Test workflow when plotting_Flag=True."""

    calls = {
        "retrieve_nuclide_information": [],
        "retrieve_covariance_data": [],
        "plot_covariance": [],
        "save_covariance_file": [],
        "print": [],
    }

    # -----------------------------
    # Mock helper functions
    # -----------------------------
    monkeypatch.setattr(
        "src.WINDIGO.sandy_main_functions.retrieve_nuclide_information",
        lambda nuclide: calls["retrieve_nuclide_information"].append(nuclide) or 922350,
    )

    monkeypatch.setattr(
        "src.WINDIGO.sandy_main_functions.retrieve_covariance_data",
        lambda **kwargs: (
            calls["retrieve_covariance_data"].append(kwargs) or
            ([[1, 2], [3, 4]], "Relative")
        ),
    )

    monkeypatch.setattr(
        "src.WINDIGO.sandy_main_functions.plot_covariance",
        lambda **kwargs: calls["plot_covariance"].append(kwargs) or "plot.png",
    )

    monkeypatch.setattr(
        "src.WINDIGO.sandy_main_functions.save_covariance_file",
        lambda **kwargs: calls["save_covariance_file"].append(kwargs) or "cov.csv",
    )

    monkeypatch.setattr(
        builtins, "print",
        lambda msg: calls["print"].append(msg),
    )

    # -----------------------------
    # Run function
    # -----------------------------
    result_csv, result_plot = sandy_covariance_retrieval(
        energy_grid=[1, 2, 3],
        nuclide="U235",
        mt_Number=18,
        data_library="endfb_80",
        temperature=600,
        err_tolerance=0.2,
        relative_Flag=True,
        plotting_Flag=True,
    )

    # -----------------------------
    # Validate return values
    # -----------------------------
    assert result_csv == "cov.csv"
    assert result_plot == "plot.png"

    # -----------------------------
    # Validate helper calls
    # -----------------------------
    assert calls["retrieve_nuclide_information"] == ["U235"]

    rc = calls["retrieve_covariance_data"][0]
    assert rc["nuclide_number"] == 922350
    assert rc["relative_Flag"] is True
    assert rc["err_tolerance"] == 0.2

    pc = calls["plot_covariance"][0]
    assert pc["flag_String"] == "Relative"
    assert pc["nuclide"] == "U235"

    sc = calls["save_covariance_file"][0]
    assert sc["flag_String"] == "Relative"

    # -----------------------------
    # Validate printed output
    # -----------------------------
    assert any("Covariance Retrieval Process Complete" in msg for msg in calls["print"])
