"""
Unit tests for generate_random_sampling_ace_files.
"""

import pytest
from io import StringIO
import sys


def test_generate_random_sampling_ace_files_success(monkeypatch):
    'Test full successful workflow with cleanup'

    calls = {
        "chdir": [],
        "system": [],
        "remove": [],
        "rmtree": [],
        "create_exec": [],
        "create_inputs": [],
        "gen_factors": [],
        "move": [],
        "create_list": [],
        "create_dir": [],
        "create_ace_exec": [],
        "folder_check": [],
    }

    monkeypatch.setattr("os.getcwd", lambda: "/start")
    monkeypatch.setattr("os.chdir", lambda p: calls["chdir"].append(p))
    monkeypatch.setattr("os.system", lambda cmd: calls["system"].append(cmd))
    monkeypatch.setattr("os.remove", lambda p: calls["remove"].append(p))
    monkeypatch.setattr("shutil.rmtree", lambda p: calls["rmtree"].append(p))

    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_tool_execution_file",
        lambda **kwargs: calls["create_exec"].append(kwargs) or "exec.csh",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_tool_inputs",
        lambda **kwargs: calls["create_inputs"].append(kwargs) or "sample.inp",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.generate_random_sampling_factors",
        lambda **kwargs: calls["gen_factors"].append(kwargs),
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.move_random_sampling_files",
        lambda **kwargs: calls["move"].append(kwargs) or "U235_inputs",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_pert_list",
        lambda **kwargs: calls["create_list"].append(kwargs) or "pert_list.inp",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_ace_directory",
        lambda **kwargs: calls["create_dir"].append(kwargs) or "/F/U235_RSACE",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_ace_execution_file",
        lambda **kwargs: calls["create_ace_exec"].append(kwargs) or "run_ace.csh",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.random_sampling_folder_check",
        lambda **kwargs: calls["folder_check"].append(kwargs) or True,
    )

    captured = StringIO()
    monkeypatch.setattr(sys, "stdout", captured)

    from src.WENDIGO.frendy_main_functions import (
        generate_random_sampling_ace_files
    )

    result = generate_random_sampling_ace_files(
        frendy_Path="/F",
        relative_covariance_matrix_path="/cov.csv",
        unperturbed_ACE_file_path="/F/U235.ace",
        energy_grid=[1, 2],
        mt_Number=102,
        nuclide="U235",
        seed=42,
        sample_size=5,
        cleanup_Flag=True,
    )

    assert result == "/F/U235_RSACE"
    assert "All ACE files generated successfully" in captured.getvalue()

    assert calls["system"] == ["csh ./run_ace.csh"]
    assert "/start" in calls["chdir"][-1]


def test_generate_random_sampling_ace_files_failure(monkeypatch):
    'Test failure message when folder check fails'

    monkeypatch.setattr("os.getcwd", lambda: "/start")
    monkeypatch.setattr("os.chdir", lambda p: None)
    monkeypatch.setattr("os.system", lambda cmd: None)
    monkeypatch.setattr("os.remove", lambda p: None)
    monkeypatch.setattr("shutil.rmtree", lambda p: None)

    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_tool_execution_file",
        lambda **kwargs: "exec.csh",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_tool_inputs",
        lambda **kwargs: "sample.inp",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.generate_random_sampling_factors",
        lambda **kwargs: None,
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.move_random_sampling_files",
        lambda **kwargs: "inputs",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_pert_list",
        lambda **kwargs: "list.inp",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_ace_directory",
        lambda **kwargs: "/F/RSACE",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_ace_execution_file",
        lambda **kwargs: "run.csh",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.random_sampling_folder_check",
        lambda **kwargs: False,
    )

    captured = StringIO()
    monkeypatch.setattr(sys, "stdout", captured)

    from src.WENDIGO.frendy_main_functions import (
        generate_random_sampling_ace_files
    )

    result = generate_random_sampling_ace_files(
        frendy_Path="/F",
        relative_covariance_matrix_path="/cov.csv",
        unperturbed_ACE_file_path="/F/Xe135.ace",
        energy_grid=[1],
        mt_Number=51,
        nuclide="Xe135",
        sample_size=3,
        cleanup_Flag=False,
    )

    assert result is None
    assert "ACE files not generated successfully" in captured.getvalue()


def test_generate_random_sampling_ace_files_no_cleanup(monkeypatch):
    'Test cleanup_Flag=False results in no cleanup actions'

    calls = {"remove": [], "rmtree": []}

    monkeypatch.setattr("os.getcwd", lambda: "/start")
    monkeypatch.setattr("os.chdir", lambda p: None)
    monkeypatch.setattr("os.system", lambda cmd: None)
    monkeypatch.setattr("os.remove", lambda p: calls["remove"].append(p))
    monkeypatch.setattr("shutil.rmtree", lambda p: calls["rmtree"].append(p))

    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_tool_execution_file",
        lambda **kwargs: "exec.csh",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_tool_inputs",
        lambda **kwargs: "sample.inp",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.generate_random_sampling_factors",
        lambda **kwargs: None,
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.move_random_sampling_files",
        lambda **kwargs: "inputs",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_pert_list",
        lambda **kwargs: "list.inp",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_ace_directory",
        lambda **kwargs: "/F/RSACE",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_ace_execution_file",
        lambda **kwargs: "run.csh",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.random_sampling_folder_check",
        lambda **kwargs: True,
    )

    captured = StringIO()
    monkeypatch.setattr(sys, "stdout", captured)

    from src.WENDIGO.frendy_main_functions import (
        generate_random_sampling_ace_files
    )

    result = generate_random_sampling_ace_files(
        frendy_Path="/F",
        relative_covariance_matrix_path="/cov.csv",
        unperturbed_ACE_file_path="/F/Mo95.ace",
        energy_grid=[1, 2],
        mt_Number=18,
        nuclide="Mo95",
        sample_size=2,
        cleanup_Flag=False,
    )

    assert calls["remove"] == []
    assert calls["rmtree"] == []
    assert "Intermediate Files Removed" not in captured.getvalue()
    assert result == "/F/RSACE"


def test_generate_random_sampling_ace_files_directory_switching(monkeypatch):
    'Test correct directory switching order'

    calls = {"chdir": []}

    monkeypatch.setattr("os.getcwd", lambda: "/start")
    monkeypatch.setattr("os.chdir", lambda p: calls["chdir"].append(p))
    monkeypatch.setattr("os.system", lambda cmd: None)
    monkeypatch.setattr("os.remove", lambda p: None)
    monkeypatch.setattr("shutil.rmtree", lambda p: None)

    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_tool_execution_file",
        lambda **kwargs: "exec.csh",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_tool_inputs",
        lambda **kwargs: "sample.inp",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.generate_random_sampling_factors",
        lambda **kwargs: None,
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.move_random_sampling_files",
        lambda **kwargs: "inputs",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_pert_list",
        lambda **kwargs: "list.inp",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_ace_directory",
        lambda **kwargs: "/F/RSACE",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_ace_execution_file",
        lambda **kwargs: "run.csh",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.random_sampling_folder_check",
        lambda **kwargs: True,
    )

    from src.WENDIGO.frendy_main_functions import (
        generate_random_sampling_ace_files
    )

    generate_random_sampling_ace_files(
        frendy_Path="/F",
        relative_covariance_matrix_path="/cov.csv",
        unperturbed_ACE_file_path="/F/U.ace",
        energy_grid=[1],
        mt_Number=1,
        nuclide="U",
        sample_size=1,
        cleanup_Flag=False,
    )

    assert calls["chdir"] == [
        "/F/tools/make_perturbation_factor",
        "/F",
        "/F/RSACE",
        "/start",
    ]


def test_generate_random_sampling_ace_files_internal_calls(monkeypatch):
    'Test that all internal helper functions receive correct arguments'

    captured = {
        "exec": None,
        "inputs": None,
        "factors": None,
        "move": None,
        "list": None,
        "dir": None,
        "ace_exec": None,
        "check": None,
    }

    monkeypatch.setattr("os.getcwd", lambda: "/start")
    monkeypatch.setattr("os.chdir", lambda p: None)
    monkeypatch.setattr("os.system", lambda cmd: None)
    monkeypatch.setattr("os.remove", lambda p: None)
    monkeypatch.setattr("shutil.rmtree", lambda p: None)

    def fake_exec(**kwargs):
        captured["exec"] = kwargs
        return "exec.csh"

    def fake_inputs(**kwargs):
        captured["inputs"] = kwargs
        return "sample.inp"

    def fake_factors(**kwargs):
        captured["factors"] = kwargs

    def fake_move(**kwargs):
        captured["move"] = kwargs
        return "inputs"

    def fake_list(**kwargs):
        captured["list"] = kwargs
        return "list.inp"

    def fake_dir(**kwargs):
        captured["dir"] = kwargs
        return "/F/RSACE"

    def fake_ace_exec(**kwargs):
        captured["ace_exec"] = kwargs
        return "run.csh"

    def fake_check(**kwargs):
        captured["check"] = kwargs
        return True

    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_tool_execution_file",
        fake_exec,
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_tool_inputs",
        fake_inputs,
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.generate_random_sampling_factors",
        fake_factors,
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.move_random_sampling_files",
        fake_move,
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_pert_list",
        fake_list,
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_ace_directory",
        fake_dir,
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_ace_execution_file",
        fake_ace_exec,
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.random_sampling_folder_check",
        fake_check,
    )

    from src.WENDIGO.frendy_main_functions import (
        generate_random_sampling_ace_files
    )

    generate_random_sampling_ace_files(
        frendy_Path="/F",
        relative_covariance_matrix_path="/cov.csv",
        unperturbed_ACE_file_path="/F/U.ace",
        energy_grid=[1, 2],
        mt_Number=102,
        nuclide="U",
        seed=99,
        sample_size=7,
        cleanup_Flag=False,
    )

    assert captured["exec"]["executable_directory"] == "/F/tools/make_perturbation_factor/make_perturbation_factor.exe"
    assert captured["inputs"]["sample_size"] == 7
    assert captured["inputs"]["seed"] == 99
    assert captured["inputs"]["relative_covariance_matrix_path"] == "/cov.csv"
    assert captured["inputs"]["energy_grid"] == [1, 2]
    assert captured["inputs"]["nuclide"] == "U"
    assert captured["inputs"]["mt_Number"] == 102

    assert captured["factors"]["execution_filename"] == "exec.csh"
    assert captured["move"]["nuclide"] == "U"
    assert captured["list"]["sample_size"] == 7
    assert captured["dir"]["nuclide"] == "U"
    assert captured["ace_exec"]["unperturbed_ACE_file_path"] == "/F/U.ace"
    assert captured["check"]["sample_size"] == 7


def test_generate_random_sampling_ace_files_varied_inputs(monkeypatch):
    'Test arbitrary paths, nuclides, and MT numbers'

    monkeypatch.setattr("os.getcwd", lambda: "/start")
    monkeypatch.setattr("os.chdir", lambda p: None)
    monkeypatch.setattr("os.system", lambda cmd: None)
    monkeypatch.setattr("os.remove", lambda p: None)
    monkeypatch.setattr("shutil.rmtree", lambda p: None)

    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_tool_execution_file",
        lambda **kwargs: "exec.csh",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_tool_inputs",
        lambda **kwargs: "sample.inp",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.generate_random_sampling_factors",
        lambda **kwargs: None,
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.move_random_sampling_files",
        lambda **kwargs: "inputs",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_pert_list",
        lambda **kwargs: "list.inp",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_ace_directory",
        lambda **kwargs: "/ROOT/Th232_RSACE",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.create_random_sampling_ace_execution_file",
        lambda **kwargs: "run.csh",
    )
    monkeypatch.setattr(
        "src.WENDIGO.frendy_internal_functions.random_sampling_folder_check",
        lambda **kwargs: True,
    )

    from src.WENDIGO.frendy_main_functions import (
        generate_random_sampling_ace_files
    )

    result = generate_random_sampling_ace_files(
        frendy_Path="/ROOT",
        relative_covariance_matrix_path="/cov.csv",
        unperturbed_ACE_file_path="/ROOT/Th232.ace",
        energy_grid=[0.1],
        mt_Number=4,
        nuclide="Th232",
        seed=1,
        sample_size=2,
        cleanup_Flag=False,
    )

    assert result == "/ROOT/Th232_RSACE"