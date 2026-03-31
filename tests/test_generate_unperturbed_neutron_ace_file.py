"""
Unit tests for generate_unperturbed_neutron_ace_file.
"""

import pytest
from io import StringIO
import sys


def test_generate_unperturbed_neutron_ace_file_basic(monkeypatch):
    'Test normal (non-upgrade) ACE generation with cleanup'

    calls = {
        "format": [],
        "create_input": [],
        "system": [],
        "chdir": [],
        "remove": [],
        "exists": [],
    }

    # Mock internal FRENDY functions
    def fake_format(endf_Path):
        calls["format"].append(endf_Path)
        return "formatted.dat"

    def fake_create_input(**kwargs):
        calls["create_input"].append(kwargs)
        return "input_file.inp"

    # Mock OS functions
    monkeypatch.setattr("os.getcwd", lambda: "/start")
    monkeypatch.setattr("os.chdir", lambda p: calls["chdir"].append(p))
    monkeypatch.setattr("os.system", lambda cmd: calls["system"].append(cmd))
    monkeypatch.setattr("os.remove", lambda p: calls["remove"].append(p))

    def fake_exists(path):
        calls["exists"].append(path)
        return True

    monkeypatch.setattr("os.path.exists", fake_exists)

    # Capture print output
    captured = StringIO()
    monkeypatch.setattr(sys, "stdout", captured)

    # Patch internal FRENDY imports in frendy_main_functions
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.format_endf_evaluation",
        fake_format,
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_unperturbed_ace_generation_input",
        fake_create_input,
    )

    from src.WENDIGO.frendy_main_functions import (
        generate_unperturbed_neutron_ace_file
    )

    result = generate_unperturbed_neutron_ace_file(
        frendy_Path="/FRENDY",
        endf_Path="/data/U235.endf",
        temperature=900,
        nuclide="U235",
        upgrade_Flag=False,
        energy_grid=[1, 2, 3],
        cleanup_Flag=True,
    )

    expected_output = "/FRENDY/frendy/main/U235.ace"
    assert result == expected_output

    # format_endf_evaluation called correctly
    assert calls["format"] == ["/data/U235.endf"]

    # create_unperturbed_ace_generation_input called with correct args
    args = calls["create_input"][0]
    assert args["frendy_Path"] == "/FRENDY"
    assert args["nuclide"] == "U235"
    assert args["endf_file_dat"] == "formatted.dat"
    assert args["temperature"] == 900
    assert args["upgrade_Flag"] is False
    assert args["energy_grid"] == [1, 2, 3]

    # Directory switching
    assert calls["chdir"] == [
        "/FRENDY/frendy/main",  # enter FRENDY executable directory
        "/start",               # return to original directory
    ]

    # System command executed
    assert calls["system"] == ["./frendy.exe input_file.inp"]

    # Cleanup removes .dat, .inp, and .ace.ace.dir
    assert "formatted.dat" in calls["remove"]
    assert "input_file.inp" in calls["remove"]
    assert "/FRENDY/frendy/main/U235.ace.ace.dir" in calls["remove"]

    # Success message printed
    assert "ACE file successfully generated" in captured.getvalue()


def test_generate_unperturbed_neutron_ace_file_upgrade(monkeypatch):
    'Test upgrade=True uses _upgrade.ace and removes correct files'

    calls = {"exists": [], "remove": []}

    monkeypatch.setattr("os.getcwd", lambda: "/start")
    monkeypatch.setattr("os.chdir", lambda p: None)
    monkeypatch.setattr("os.system", lambda cmd: None)
    monkeypatch.setattr("os.remove", lambda p: calls["remove"].append(p))

    def fake_exists(path):
        calls["exists"].append(path)
        return True

    monkeypatch.setattr("os.path.exists", fake_exists)

    # Patch internal FRENDY functions
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.format_endf_evaluation",
        lambda endf_Path: "formatted.dat",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_unperturbed_ace_generation_input",
        lambda **kwargs: "input_file.inp",
    )

    captured = StringIO()
    monkeypatch.setattr(sys, "stdout", captured)

    from src.WENDIGO.frendy_main_functions import (
        generate_unperturbed_neutron_ace_file
    )

    result = generate_unperturbed_neutron_ace_file(
        frendy_Path="/F",
        endf_Path="/e",
        temperature=300,
        nuclide="Xe135",
        upgrade_Flag=True,
        energy_grid=[],
        cleanup_Flag=True,
    )

    expected_output = "/F/frendy/main/Xe135_upgrade.ace"
    assert result == expected_output

    # Upgrade cleanup removes .upgrade.ace.ace.dir
    assert "/F/frendy/main/Xe135_upgrade.ace.ace.dir" in calls["remove"]

    # Success message printed
    assert "ACE file successfully generated" in captured.getvalue()


def test_generate_unperturbed_neutron_ace_file_failure(monkeypatch):
    'Test failure message when ACE file does not exist'

    monkeypatch.setattr("os.getcwd", lambda: "/start")
    monkeypatch.setattr("os.chdir", lambda p: None)
    monkeypatch.setattr("os.system", lambda cmd: None)
    monkeypatch.setattr("os.remove", lambda p: None)

    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.format_endf_evaluation",
        lambda endf_Path: "formatted.dat",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_unperturbed_ace_generation_input",
        lambda **kwargs: "input_file.inp",
    )

    monkeypatch.setattr("os.path.exists", lambda p: False)

    captured = StringIO()
    monkeypatch.setattr(sys, "stdout", captured)

    from src.WENDIGO.frendy_main_functions import (
        generate_unperturbed_neutron_ace_file
    )

    result = generate_unperturbed_neutron_ace_file(
        frendy_Path="/F",
        endf_Path="/e",
        temperature=600,
        nuclide="Mo95",
        upgrade_Flag=False,
        energy_grid=[],
        cleanup_Flag=False,
    )

    assert "couldn't generate" in captured.getvalue()

def test_generate_unperturbed_neutron_ace_file_no_cleanup(monkeypatch):
    'Test that no cleanup occurs when cleanup_Flag=False'

    calls = {"remove": [], "exists": []}

    monkeypatch.setattr("os.getcwd", lambda: "/start")
    monkeypatch.setattr("os.chdir", lambda p: None)
    monkeypatch.setattr("os.system", lambda cmd: None)
    monkeypatch.setattr("os.remove", lambda p: calls["remove"].append(p))

    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.format_endf_evaluation",
        lambda endf_Path: "formatted.dat",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_unperturbed_ace_generation_input",
        lambda **kwargs: "input_file.inp",
    )

    monkeypatch.setattr("os.path.exists", lambda p: True)

    from src.WENDIGO.frendy_main_functions import (
        generate_unperturbed_neutron_ace_file
    )

    result = generate_unperturbed_neutron_ace_file(
        frendy_Path="/F",
        endf_Path="/e",
        temperature=600,
        nuclide="U238",
        upgrade_Flag=False,
        energy_grid=[1],
        cleanup_Flag=False,
    )

    assert result == "/F/frendy/main/U238.ace"

    # No cleanup should occur
    assert calls["remove"] == []


def test_generate_unperturbed_neutron_ace_file_energy_grid_none(monkeypatch):
    'Test that energy_grid=None is replaced with an empty list'

    captured_args = {}

    def fake_create_input(**kwargs):
        captured_args.update(kwargs)
        return "input_file.inp"

    monkeypatch.setattr("os.getcwd", lambda: "/start")
    monkeypatch.setattr("os.chdir", lambda p: None)
    monkeypatch.setattr("os.system", lambda cmd: None)
    monkeypatch.setattr("os.remove", lambda p: None)
    monkeypatch.setattr("os.path.exists", lambda p: True)

    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.format_endf_evaluation",
        lambda endf_Path: "formatted.dat",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_unperturbed_ace_generation_input",
        fake_create_input,
    )

    from src.WENDIGO.frendy_main_functions import (
        generate_unperturbed_neutron_ace_file
    )

    generate_unperturbed_neutron_ace_file(
        frendy_Path="/F",
        endf_Path="/e",
        temperature=300,
        nuclide="Xe135",
        upgrade_Flag=False,
        energy_grid=None,
        cleanup_Flag=False,
    )

    # energy_grid=None must be converted to []
    assert captured_args["energy_grid"] == []


def test_generate_unperturbed_neutron_ace_file_upgrade_no_cleanup(monkeypatch):
    'Test upgrade=True but cleanup_Flag=False (no files removed)'

    calls = {"remove": [], "exists": []}

    monkeypatch.setattr("os.getcwd", lambda: "/start")
    monkeypatch.setattr("os.chdir", lambda p: None)
    monkeypatch.setattr("os.system", lambda cmd: None)
    monkeypatch.setattr("os.remove", lambda p: calls["remove"].append(p))

    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.format_endf_evaluation",
        lambda endf_Path: "formatted.dat",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_unperturbed_ace_generation_input",
        lambda **kwargs: "input_file.inp",
    )

    monkeypatch.setattr("os.path.exists", lambda p: True)

    from src.WENDIGO.frendy_main_functions import (
        generate_unperturbed_neutron_ace_file
    )

    result = generate_unperturbed_neutron_ace_file(
        frendy_Path="/F",
        endf_Path="/e",
        temperature=500,
        nuclide="Mo95",
        upgrade_Flag=True,
        energy_grid=[1, 2],
        cleanup_Flag=False,
    )

    expected_output = "/F/frendy/main/Mo95_upgrade.ace"
    assert result == expected_output

    # No cleanup should occur
    assert calls["remove"] == []