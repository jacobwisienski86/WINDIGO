# tests/test_save_covariance_file.py

import builtins
import pytest

from src.WINDIGO.sandy_internal_functions import save_covariance_file


def test_save_covariance_file(monkeypatch):
    """Test that covariance data is saved, reloaded, saved again, and cleaned up."""

    calls = {
        "cov_to_csv": [],
        "pd_read_csv": [],
        "df_to_csv": [],
        "remove": [],
        "print": [],
    }

    class FakeCovariance:
        def to_csv(self, filename, index):
            calls["cov_to_csv"].append((filename, index))

    covariance_data = FakeCovariance()

    class FakeDF:
        def to_csv(self, filename, index, header):
            calls["df_to_csv"].append((filename, index, header))

    monkeypatch.setattr(
        "src.WINDIGO.sandy_internal_functions.pd.read_csv",
        lambda filename, skiprows: calls["pd_read_csv"].append((filename, skiprows)) or FakeDF(),
    )

    monkeypatch.setattr(
        "src.WINDIGO.sandy_internal_functions.os.remove",
        lambda filename: calls["remove"].append(filename),
    )

    monkeypatch.setattr(
        builtins, "print",
        lambda msg: calls["print"].append(msg),
    )

    energy_grid = [1, 2, 3, 4]   # 4 points → 3 groups
    nuclide = "U235"
    mt = 102
    flag = "Relative"

    result = save_covariance_file(
        covariance_data=covariance_data,
        energy_grid=energy_grid,
        nuclide=nuclide,
        mt_Number=mt,
        flag_String=flag,
    )

    expected_filename = "covarianceMatrix_3Groups_U235_MT_102_Relative.csv"

    assert result == expected_filename

    assert calls["cov_to_csv"] == [
        ("intermediate_dataframe.csv", False)
    ]

    assert calls["pd_read_csv"] == [
        ("intermediate_dataframe.csv", 2)
    ]

    assert calls["df_to_csv"] == [
        (expected_filename, False, False)
    ]

    assert calls["remove"] == ["intermediate_dataframe.csv"]

    assert any(expected_filename in msg for msg in calls["print"])
