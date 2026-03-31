"""
Unit tests for create_model_folders.
"""

import pytest


@pytest.fixture
def mock_fs(monkeypatch):
    """
    Mock filesystem operations: os.path.exists, os.mkdir, shutil.rmtree.
    """

    created_dirs = []
    removed_dirs = []

    # Mock os.path.exists
    def fake_exists(path):
        # Treat any path in removed_dirs as "existing" for test purposes
        return path in removed_dirs

    # Mock os.mkdir
    def fake_mkdir(path):
        created_dirs.append(path)

    # Mock shutil.rmtree
    def fake_rmtree(path):
        removed_dirs.append(path)

    monkeypatch.setattr("os.path.exists", fake_exists)
    monkeypatch.setattr("os.mkdir", fake_mkdir)
    monkeypatch.setattr("shutil.rmtree", fake_rmtree)

    return created_dirs, removed_dirs


def test_create_model_folders_basic(mock_fs):
    """
    Basic test: ensure correct folder creation and naming.
    """

    from src.WENDIGO.openmc_internal_functions import create_model_folders

    created_dirs, removed_dirs = mock_fs

    top, folders = create_model_folders(
        directory_number=3,
        perturbed_nuclide="U235",
        model_name="TestModel",
        perturbation_type="Random"
    )

    expected_top = "TestModel_U235_RandomPerturbedModels"

    # Top-level directory created first
    assert created_dirs[0] == expected_top

    # Three subfolders created
    assert created_dirs[1:] == [
        f"{expected_top}/Model_1_Folder",
        f"{expected_top}/Model_2_Folder",
        f"{expected_top}/Model_3_Folder",
    ]

    # Function returns correct values
    assert top == expected_top
    assert folders == created_dirs[1:]


def test_create_model_folders_removes_existing(mock_fs):
    """
    If the top directory already exists, it should be removed before recreation.
    """

    from src.WENDIGO.openmc_internal_functions import create_model_folders

    created_dirs, removed_dirs = mock_fs

    # Pretend the directory already exists
    removed_dirs.append("ExistingModel_U235_DirectPerturbedModels")

    top, _ = create_model_folders(
        directory_number=1,
        perturbed_nuclide="U235",
        model_name="ExistingModel",
        perturbation_type="Direct"
    )

    expected_top = "ExistingModel_U235_DirectPerturbedModels"

    # Directory should have been removed
    assert expected_top in removed_dirs

    # Directory should then be recreated
    assert created_dirs[0] == expected_top


def test_create_model_folders_zero(mock_fs):
    """
    If directory_number = 0, only the top directory should be created.
    """

    from src.WENDIGO.openmc_internal_functions import create_model_folders

    created_dirs, removed_dirs = mock_fs

    top, folders = create_model_folders(
        directory_number=0,
        perturbed_nuclide="H1",
        model_name="ZeroCase",
        perturbation_type="None"
    )

    expected_top = "ZeroCase_H1_NonePerturbedModels"

    # Only top directory created
    assert created_dirs == [expected_top]

    # No subfolders
    assert folders == []