"""
Unit tests for generate_direct_perturbation_ace_files.
"""

import pytest
from io import StringIO
import sys


def test_generate_direct_perturbation_ace_files_basic(monkeypatch):
    'Test normal successful generation with cleanup'

    calls = {
        "makedirs": [],
        "chdir": [],
        "system": [],
        "remove": [],
        "rmtree": [],
        "create_inputs": [],
        "create_list": [],
        "create_cmd": [],
        "folder_check": [],
    }

    # Mock OS functions
    monkeypatch.setattr("os.getcwd", lambda: "/start")
    monkeypatch.setattr("os.chdir", lambda p: calls["chdir"].append(p))
    monkeypatch.setattr("os.makedirs", lambda p: calls["makedirs"].append(p))
    monkeypatch.setattr("os.system", lambda cmd: calls["system"].append(cmd))
    monkeypatch.setattr("os.remove", lambda p: calls["remove"].append(p))

    monkeypatch.setattr("shutil.rmtree", lambda p: calls["rmtree"].append(p))

    # Mock internal FRENDY functions
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_direct_perturbation_inputs",
        lambda **kwargs: (["line1", "line2"], "input_folder"),
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_direct_perturbation_list",
        lambda **kwargs: "pert_list.inp",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_direct_perturbation_command_file",
        lambda **kwargs: "run_create_perturbed_ace_file.csh",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.direct_perturbation_folder_check",
        lambda **kwargs: False,
    )

    captured = StringIO()
    monkeypatch.setattr(sys, "stdout", captured)

    from src.WENDIGO.frendy_main_functions import (
        generate_direct_perturbation_ace_files
    )

    result = generate_direct_perturbation_ace_files(
        frendy_Path="/F",
        unperturbed_ACE_file_path="/F/U235.ace",
        energy_grid=[1, 2, 3],
        mt_Number=102,
        nuclide="U235",
        perturbation_coefficient=1.05,
        cleanup_Flag=True,
    )

    expected_dir = "/F/U235_DirectPerturbationACEFiles_ReactionMT_102"
    assert result == expected_dir

    # Directory creation
    assert calls["makedirs"] == [expected_dir]

    # Directory switching
    assert calls["chdir"][0] == "/F"
    assert calls["chdir"][1] == expected_dir
    assert calls["chdir"][-1] == "/start"

    # System command executed
    assert calls["system"] == ["csh ./run_create_perturbed_ace_file.csh"]

    # Cleanup performed
    assert "pert_list.inp" in calls["remove"]
    assert expected_dir + "/results.log" in calls["remove"]
    assert "input_folder" in calls["rmtree"]

    # Success message printed
    assert "All ACE files have successfully generated" in captured.getvalue()


def test_generate_direct_perturbation_ace_files_failure(monkeypatch):
    'Test failure message when folder check fails'

    monkeypatch.setattr("os.getcwd", lambda: "/start")
    monkeypatch.setattr("os.chdir", lambda p: None)
    monkeypatch.setattr("os.makedirs", lambda p: None)
    monkeypatch.setattr("os.system", lambda cmd: None)
    monkeypatch.setattr("os.remove", lambda p: None)
    monkeypatch.setattr("shutil.rmtree", lambda p: None)

    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_direct_perturbation_inputs",
        lambda **kwargs: (["x"], "folder"),
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_direct_perturbation_list",
        lambda **kwargs: "list.inp",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_direct_perturbation_command_file",
        lambda **kwargs: "cmd.csh",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.direct_perturbation_folder_check",
        lambda **kwargs: True,
    )

    captured = StringIO()
    monkeypatch.setattr(sys, "stdout", captured)

    from src.WENDIGO.frendy_main_functions import (
        generate_direct_perturbation_ace_files
    )

    result = generate_direct_perturbation_ace_files(
        frendy_Path="/F",
        unperturbed_ACE_file_path="/F/Xe135.ace",
        energy_grid=[1],
        mt_Number=51,
        nuclide="Xe135",
        perturbation_coefficient=1.1,
        cleanup_Flag=False,
    )

    assert result is None
    assert "failed to generate" in captured.getvalue()


def test_generate_direct_perturbation_ace_files_no_cleanup(monkeypatch):
    'Test cleanup_Flag=False results in no cleanup actions'

    calls = {"remove": [], "rmtree": []}

    monkeypatch.setattr("os.getcwd", lambda: "/start")
    monkeypatch.setattr("os.chdir", lambda p: None)
    monkeypatch.setattr("os.makedirs", lambda p: None)
    monkeypatch.setattr("os.system", lambda cmd: None)
    monkeypatch.setattr("os.remove", lambda p: calls["remove"].append(p))
    monkeypatch.setattr("shutil.rmtree", lambda p: calls["rmtree"].append(p))

    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_direct_perturbation_inputs",
        lambda **kwargs: (["a"], "folderA"),
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_direct_perturbation_list",
        lambda **kwargs: "list.inp",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_direct_perturbation_command_file",
        lambda **kwargs: "cmd.csh",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.direct_perturbation_folder_check",
        lambda **kwargs: False,
    )

    captured = StringIO()
    monkeypatch.setattr(sys, "stdout", captured)

    from src.WENDIGO.frendy_main_functions import (
        generate_direct_perturbation_ace_files
    )

    result = generate_direct_perturbation_ace_files(
        frendy_Path="/F",
        unperturbed_ACE_file_path="/F/Mo95.ace",
        energy_grid=[1, 2],
        mt_Number=18,
        nuclide="Mo95",
        perturbation_coefficient=0.9,
        cleanup_Flag=False,
    )

    assert calls["remove"] == []
    assert calls["rmtree"] == []
    assert "Intermediate Files Removed" not in captured.getvalue()


def test_generate_direct_perturbation_ace_files_varied_inputs(monkeypatch):
    'Test arbitrary paths and nuclide names'

    created_dirs = []

    monkeypatch.setattr("os.getcwd", lambda: "/start")
    monkeypatch.setattr("os.chdir", lambda p: None)
    monkeypatch.setattr("os.makedirs", lambda p: created_dirs.append(p))
    monkeypatch.setattr("os.system", lambda cmd: None)
    monkeypatch.setattr("os.remove", lambda p: None)
    monkeypatch.setattr("shutil.rmtree", lambda p: None)

    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_direct_perturbation_inputs",
        lambda **kwargs: (["x"], "folder"),
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_direct_perturbation_list",
        lambda **kwargs: "list.inp",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_direct_perturbation_command_file",
        lambda **kwargs: "cmd.csh",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.direct_perturbation_folder_check",
        lambda **kwargs: False,
    )

    from src.WENDIGO.frendy_main_functions import (
        generate_direct_perturbation_ace_files
    )

    result = generate_direct_perturbation_ace_files(
        frendy_Path="/ROOT",
        unperturbed_ACE_file_path="/ROOT/Th232.ace",
        energy_grid=[0.1],
        mt_Number=4,
        nuclide="Th232",
        perturbation_coefficient=1.2,
        cleanup_Flag=False,
    )

    expected_dir = "/ROOT/Th232_DirectPerturbationACEFiles_ReactionMT_4"
    assert created_dirs == [expected_dir]
    assert result == expected_dir


def test_generate_direct_perturbation_ace_files_calls_internal_functions(monkeypatch):
    'Test that all internal FRENDY helper functions are called with correct arguments'

    captured = {
        "inputs": None,
        "list": None,
        "cmd": None,
        "check": None,
    }

    monkeypatch.setattr("os.getcwd", lambda: "/start")
    monkeypatch.setattr("os.chdir", lambda p: None)
    monkeypatch.setattr("os.makedirs", lambda p: None)
    monkeypatch.setattr("os.system", lambda cmd: None)
    monkeypatch.setattr("os.remove", lambda p: None)
    monkeypatch.setattr("shutil.rmtree", lambda p: None)

    def fake_inputs(**kwargs):
        captured["inputs"] = kwargs
        return (["a"], "folderA")

    def fake_list(**kwargs):
        captured["list"] = kwargs
        return "list.inp"

    def fake_cmd(**kwargs):
        captured["cmd"] = kwargs
        return "cmd.csh"

    def fake_check(**kwargs):
        captured["check"] = kwargs
        return False

    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_direct_perturbation_inputs",
        fake_inputs,
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_direct_perturbation_list",
        fake_list,
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_direct_perturbation_command_file",
        fake_cmd,
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.direct_perturbation_folder_check",
        fake_check,
    )

    from src.WENDIGO.frendy_main_functions import (
        generate_direct_perturbation_ace_files
    )

    generate_direct_perturbation_ace_files(
        frendy_Path="/F",
        unperturbed_ACE_file_path="/F/U.ace",
        energy_grid=[1, 2],
        mt_Number=102,
        nuclide="U",
        perturbation_coefficient=1.1,
        cleanup_Flag=False,
    )

    assert captured["inputs"]["nuclide"] == "U"
    assert captured["inputs"]["mt_Number"] == 102
    assert captured["inputs"]["energy_grid"] == [1, 2]
    assert captured["inputs"]["perturbation_coefficient"] == 1.1

    assert captured["list"]["nuclide"] == "U"
    assert captured["list"]["mt_Number"] == 102

    assert captured["cmd"]["frendy_Path"] == "/F"
    assert captured["cmd"]["perturbation_list_filename"] == "list.inp"
    assert captured["cmd"]["unperturbed_ACE_file_path"] == "/F/U.ace"

    assert captured["check"]["perturbed_ace_folder_path"] == (
        "/F/U_DirectPerturbationACEFiles_ReactionMT_102"
    )
    assert captured["check"]["energy_grid"] == [1, 2]


def test_generate_direct_perturbation_ace_files_directory_switching(monkeypatch):
    'Test correct directory switching order'

    calls = {"chdir": []}

    monkeypatch.setattr("os.getcwd", lambda: "/start")
    monkeypatch.setattr("os.chdir", lambda p: calls["chdir"].append(p))
    monkeypatch.setattr("os.makedirs", lambda p: None)
    monkeypatch.setattr("os.system", lambda cmd: None)
    monkeypatch.setattr("os.remove", lambda p: None)
    monkeypatch.setattr("shutil.rmtree", lambda p: None)

    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_direct_perturbation_inputs",
        lambda **kwargs: (["x"], "folder"),
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_direct_perturbation_list",
        lambda **kwargs: "list.inp",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_direct_perturbation_command_file",
        lambda **kwargs: "cmd.csh",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.direct_perturbation_folder_check",
        lambda **kwargs: False,
    )

    from src.WENDIGO.frendy_main_functions import (
        generate_direct_perturbation_ace_files
    )

    generate_direct_perturbation_ace_files(
        frendy_Path="/F",
        unperturbed_ACE_file_path="/F/U.ace",
        energy_grid=[1],
        mt_Number=1,
        nuclide="U",
        perturbation_coefficient=1.0,
        cleanup_Flag=False,
    )

    expected_dir = "/F/U_DirectPerturbationACEFiles_ReactionMT_1"

    assert calls["chdir"] == [
        "/F",          # enter FRENDY root
        expected_dir,  # enter perturbed ACE directory
        "/start",      # return to original directory
    ]