import os
import pytest
from WINDIGO.frendy_main_functions import generate_random_sampling_ace_files

MODULE_PATH = "WINDIGO.frendy_main_functions"


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #

@pytest.fixture
def mock_os(monkeypatch):
    """Mock os functions used in the function."""
    monkeypatch.setattr(os, "getcwd", lambda: "/start")
    monkeypatch.setattr(os, "chdir", lambda path: None)
    monkeypatch.setattr(os, "system", lambda cmd: 0)
    monkeypatch.setattr(os, "remove", lambda path: None)
    return os


@pytest.fixture
def mock_shutil(monkeypatch):
    """Mock shutil functions."""
    import shutil
    monkeypatch.setattr(shutil, "move", lambda src, dst: None)
    monkeypatch.setattr(shutil, "rmtree", lambda path: None)
    return shutil


@pytest.fixture
def mock_helpers(monkeypatch):
    """Mock all helper functions imported inside frendy_main_functions."""
    monkeypatch.setattr(
        f"{MODULE_PATH}.create_random_sampling_tool_execution_file",
        lambda **kwargs: "exec_tool.sh"
    )
    monkeypatch.setattr(
        f"{MODULE_PATH}.create_random_sampling_tool_inputs",
        lambda **kwargs: "inputs.txt"
    )
    monkeypatch.setattr(
        f"{MODULE_PATH}.generate_random_sampling_factors",
        lambda **kwargs: None
    )
    monkeypatch.setattr(
        f"{MODULE_PATH}.move_random_sampling_files",
        lambda **kwargs: "inputs_dir"
    )
    monkeypatch.setattr(
        f"{MODULE_PATH}.create_random_sampling_pert_list",
        lambda **kwargs: "pert_list.txt"
    )
    monkeypatch.setattr(
        f"{MODULE_PATH}.create_random_sampling_ace_directory",
        lambda **kwargs: "/ace_dir"
    )
    monkeypatch.setattr(
        f"{MODULE_PATH}.create_random_sampling_ace_execution_file",
        lambda **kwargs: "ace_exec.sh"
    )
    return monkeypatch

def test_successful_workflow(
    monkeypatch, mock_os, mock_shutil, mock_helpers
):
    """Test the full successful workflow and returned ACE directory."""
    monkeypatch.setattr(
        f"{MODULE_PATH}.random_sampling_folder_check",
        lambda **kwargs: False
    )

    result = generate_random_sampling_ace_files(
        frendy_Path="/frendy",
        relative_covariance_matrix_path="cov.csv",
        unperturbed_ACE_file_path="unperturbed.ace",
        energy_grid=[1e-5, 20.0],
        mt_Number=102,
        nuclide="H1",
        seed=42,
        sample_size=5,
        cleanup_Flag=True
    )

    assert result == "/ace_dir"


def test_no_cleanup_flag(
    monkeypatch, mock_os, mock_shutil, mock_helpers
):
    """Ensure cleanup does not occur when cleanup_Flag=False."""
    removed = []
    removed_dirs = []

    monkeypatch.setattr(os, "remove", lambda path: removed.append(path))
    monkeypatch.setattr(
        f"{MODULE_PATH}.shutil.rmtree",
        lambda path: removed_dirs.append(path)
    )
    monkeypatch.setattr(
        f"{MODULE_PATH}.random_sampling_folder_check",
        lambda **kwargs: False
    )

    generate_random_sampling_ace_files(
        frendy_Path="/frendy",
        relative_covariance_matrix_path="cov.csv",
        unperturbed_ACE_file_path="unperturbed.ace",
        energy_grid=[1, 2],
        mt_Number=102,
        nuclide="H1",
        cleanup_Flag=False
    )

    assert removed == []
    assert removed_dirs == []


def test_failure_branch(
    monkeypatch, mock_os, mock_shutil, mock_helpers, capsys
):
    """Test the failure path where ACE files are not generated."""
    monkeypatch.setattr(
        f"{MODULE_PATH}.random_sampling_folder_check",
        lambda **kwargs: True
    )

    result = generate_random_sampling_ace_files(
        frendy_Path="/frendy",
        relative_covariance_matrix_path="cov.csv",
        unperturbed_ACE_file_path="unperturbed.ace",
        energy_grid=[1, 2],
        mt_Number=102,
        nuclide="H1"
    )

    captured = capsys.readouterr()
    assert "ACE files not generated successfully" in captured.out
    assert result is None


def test_directory_switching(
    monkeypatch, mock_os, mock_shutil, mock_helpers
):
    """Ensure os.chdir is called with expected directories."""
    calls = []

    monkeypatch.setattr(os, "chdir", lambda path: calls.append(path))
    monkeypatch.setattr(
        f"{MODULE_PATH}.random_sampling_folder_check",
        lambda **kwargs: False
    )

    generate_random_sampling_ace_files(
        frendy_Path="/frendy",
        relative_covariance_matrix_path="cov.csv",
        unperturbed_ACE_file_path="ace.ace",
        energy_grid=[1, 2],
        mt_Number=102,
        nuclide="H1"
    )

    assert "/frendy/tools/make_perturbation_factor" in calls[0]
    assert "/ace_dir" in calls[-2]


def test_argument_propagation(
    monkeypatch, mock_os, mock_shutil, mock_helpers
):
    """Ensure helper functions receive correct propagated arguments."""
    captured = {}

    def fake_inputs(**kwargs):
        captured.update(kwargs)
        return "inputs.txt"

    monkeypatch.setattr(
        f"{MODULE_PATH}.create_random_sampling_tool_inputs",
        fake_inputs
    )
    monkeypatch.setattr(
        f"{MODULE_PATH}.random_sampling_folder_check",
        lambda **kwargs: False
    )

    generate_random_sampling_ace_files(
        frendy_Path="/frendy",
        relative_covariance_matrix_path="cov.csv",
        unperturbed_ACE_file_path="ace.ace",
        energy_grid=[1e-5, 20.0],
        mt_Number=102,
        nuclide="U235",
        seed=999,
        sample_size=77,
        cleanup_Flag=False
    )

    assert captured["sample_size"] == 77
    assert captured["seed"] == 999
    assert captured["nuclide"] == "U235"
    assert captured["mt_Number"] == 102


def test_system_command_format(
    monkeypatch, mock_os, mock_shutil, mock_helpers
):
    """Ensure the ACE generation system command is formatted correctly."""
    commands = []

    monkeypatch.setattr(os, "system", lambda cmd: commands.append(cmd))
    monkeypatch.setattr(
        f"{MODULE_PATH}.random_sampling_folder_check",
        lambda **kwargs: False
    )

    generate_random_sampling_ace_files(
        frendy_Path="/frendy",
        relative_covariance_matrix_path="cov.csv",
        unperturbed_ACE_file_path="ace.ace",
        energy_grid=[1, 2],
        mt_Number=102,
        nuclide="H1"
    )

    assert commands[0] == "csh ./ace_exec.sh"
