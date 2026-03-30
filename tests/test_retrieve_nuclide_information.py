"""
Unit tests for retrieve_nuclide_information.
"""

import pytest


def test_retrieve_nuclide_information(monkeypatch):
    """
    Test that retrieve_nuclide_information correctly parses nuclide strings
    and computes the expected ZZZAAA-style identifier.
    """

    # Mock the nuclide_ZZZs lookup table
    mock_z_numbers = {
        "H": 1,
        "U": 92,
        "Mo": 42
    }

    monkeypatch.setattr(
        "src.WENDIGO.z_number_library.nuclide_ZZZs",
        mock_z_numbers
    )

    from src.WENDIGO.sandy_internal_functions import retrieve_nuclide_information

    # H1 → Z=1, A=1 → 10000*1 + 10*1 = 10010
    assert retrieve_nuclide_information("H1") == 10010

    # U235 → Z=92, A=235 → 10000*92 + 10*235 = 922350
    assert retrieve_nuclide_information("U235") == 922350

    # Mo98 → Z=42, A=98 → 10000*42 + 10*98 = 420000 + 980 = 420980
    assert retrieve_nuclide_information("Mo98") == 420980


def test_retrieve_nuclide_information_invalid_number(monkeypatch):
    """
    Test that the function raises a ValueError when the mass number
    cannot be parsed into an integer.
    """

    mock_z_numbers = {"X": 99}

    monkeypatch.setattr(
        "src.WENDIGO.z_number_library.nuclide_ZZZs",
        mock_z_numbers
    )

    from src.WENDIGO.sandy_internal_functions import retrieve_nuclide_information

    with pytest.raises(ValueError):
        retrieve_nuclide_information("Xabc")
