"""
Unit tests for format_endf_evaluation.
"""

import pytest


def test_format_endf_evaluation_basic(monkeypatch):
    'Test that .dat filename is created correctly and copy2 is called'

    copied = []

    def fake_copy2(src, dst):
        copied.append((src, dst))

    monkeypatch.setattr("shutil.copy2", fake_copy2)

    from src.WENDIGO.frendy_internal_functions import format_endf_evaluation

    result = format_endf_evaluation("/path/to/U235.endf")

    assert result == "/path/to/U235.dat"
    assert copied == [
        ("/path/to/U235.endf", "/path/to/U235.dat")
    ]


def test_format_endf_evaluation_relative_path(monkeypatch):
    'Test that relative .endf paths are handled correctly'

    copied = []

    monkeypatch.setattr(
        "shutil.copy2",
        lambda src, dst: copied.append((src, dst))
    )

    from src.WENDIGO.frendy_internal_functions import format_endf_evaluation

    result = format_endf_evaluation("Th232.endf")

    assert result == "Th232.dat"
    assert copied == [
        ("Th232.endf", "Th232.dat")
    ]


def test_format_endf_evaluation_filename_with_dots(monkeypatch):
    'Test .endf filenames containing multiple dots'

    copied = []

    monkeypatch.setattr(
        "shutil.copy2",
        lambda src, dst: copied.append((src, dst))
    )

    from src.WENDIGO.frendy_internal_functions import format_endf_evaluation

    result = format_endf_evaluation("/lib/n-092.U235.v1.endf")

    # Remove last 5 chars: ".endf" → ".dat"
    assert result == "/lib/n-092.U235.v1.dat"
    assert copied == [
        ("/lib/n-092.U235.v1.endf", "/lib/n-092.U235.v1.dat")
    ]