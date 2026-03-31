"""
Unit tests for create_unperturbed_ace_generation_input.
"""

import pytest
from io import StringIO
import sys


class FakeFile:
    'Simple context-manager file mock that records written lines'

    def __init__(self, written):
        self.written = written

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def writelines(self, lines):
        self.written.extend(lines)

    def close(self):
        pass


def test_create_unperturbed_ace_generation_input_normal(monkeypatch):
    'Test normal (non-upgrade) ACE input file creation'

    written = []

    def fake_open(path, mode):
        return FakeFile(written)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WINDIGO.frendy_internal_functions import (
        create_unperturbed_ace_generation_input
    )

    result = create_unperturbed_ace_generation_input(
        frendy_Path="/opt/frendy",
        nuclide="U235",
        endf_file_dat="/data/U235.dat",
        temperature=900.0,
        upgrade_Flag=False,
        energy_grid=[1.0, 2.0, 3.0],
    )

    assert result == "/opt/frendy/frendy/main/U235_acegenerator_normal.dat"

    assert written[0] == "ace_file_generation_fast_mode\n"
    assert written[1] == "    nucl_file_name    /data/U235.dat\n"
    assert written[2] == "    temp    900.0\n"
    assert written[3] == "    ace_file_name    U235.ace\n"
    assert len(written) == 4


def test_create_unperturbed_ace_generation_input_upgrade(monkeypatch):
    'Test upgrade ACE input file creation including upgrade lines'

    written = []

    def fake_open(path, mode):
        return FakeFile(written)

    monkeypatch.setattr("builtins.open", fake_open)

    fake_upgrade = [
        "    add_grid_data    (1.000001\n",
        "        0.999999\n",
        "        1.000001)\n",
    ]

    monkeypatch.setattr(
        "src.WINDIGO.frendy_internal_functions.write_upgrade_lines",
        lambda energy_grid: fake_upgrade
    )

    from src.WINDIGO.frendy_internal_functions import (
        create_unperturbed_ace_generation_input
    )

    result = create_unperturbed_ace_generation_input(
        frendy_Path="/opt/frendy",
        nuclide="U238",
        endf_file_dat="/data/U238.dat",
        temperature=600.0,
        upgrade_Flag=True,
        energy_grid=[1.0, 2.0],
    )

    assert result == "/opt/frendy/frendy/main/U238_acegenerator_upgrade.dat"

    assert written[0] == "ace_file_generation_fast_mode\n"
    assert written[1] == "    nucl_file_name    /data/U238.dat\n"
    assert written[2] == "    temp    600.0\n"
    assert written[3] == "    ace_file_name    U238_upgrade.ace\n"
    assert written[4] == fake_upgrade


def test_create_unperturbed_ace_generation_input_empty_energy_grid(monkeypatch):
    'Test that an empty energy grid still works when upgrade_Flag=True'

    written = []

    def fake_open(path, mode):
        return FakeFile(written)

    monkeypatch.setattr("builtins.open", fake_open)

    monkeypatch.setattr(
        "src.WINDIGO.frendy_internal_functions.write_upgrade_lines",
        lambda energy_grid: []
    )

    from src.WINDIGO.frendy_internal_functions import (
        create_unperturbed_ace_generation_input
    )

    result = create_unperturbed_ace_generation_input(
        frendy_Path="/opt/frendy",
        nuclide="Xe135",
        endf_file_dat="/data/Xe135.dat",
        temperature=300.0,
        upgrade_Flag=True,
        energy_grid=None,
    )

    assert result == "/opt/frendy/frendy/main/Xe135_acegenerator_upgrade.dat"
    assert written[-1] == []


def test_create_unperturbed_ace_generation_input_print(monkeypatch):
    'Test that the correct message is printed to stdout'

    written = []

    def fake_open(path, mode):
        return FakeFile(written)

    monkeypatch.setattr("builtins.open", fake_open)

    captured = StringIO()
    monkeypatch.setattr(sys, "stdout", captured)

    from src.WINDIGO.frendy_internal_functions import (
        create_unperturbed_ace_generation_input
    )

    result = create_unperturbed_ace_generation_input(
        frendy_Path="/opt/frendy",
        nuclide="Kr85",
        endf_file_dat="/data/Kr85.dat",
        temperature=500.0,
        upgrade_Flag=False,
        energy_grid=[],
    )

    expected_path = "/opt/frendy/frendy/main/Kr85_acegenerator_normal.dat"
    assert result == expected_path

    output = captured.getvalue()
    assert expected_path in output
    assert "The path to the ace file generation input is:" in output


def test_create_unperturbed_ace_generation_input_no_upgrade_empty_grid(monkeypatch):
    'Test that empty energy grid does nothing when upgrade_Flag=False'

    written = []

    def fake_open(path, mode):
        return FakeFile(written)

    monkeypatch.setattr("builtins.open", fake_open)

    # Ensure write_upgrade_lines is NOT called
    monkeypatch.setattr(
        "src.WINDIGO.frendy_internal_functions.write_upgrade_lines",
        lambda energy_grid: (_ for _ in ()).throw(Exception("Should not be called"))
    )

    from src.WINDIGO.frendy_internal_functions import (
        create_unperturbed_ace_generation_input
    )

    result = create_unperturbed_ace_generation_input(
        frendy_Path="/opt/frendy",
        nuclide="Mo95",
        endf_file_dat="/data/Mo95.dat",
        temperature=400.0,
        upgrade_Flag=False,
        energy_grid=[],
    )

    assert result == "/opt/frendy/frendy/main/Mo95_acegenerator_normal.dat"

    # Only the four base lines should be written
    assert len(written) == 4
