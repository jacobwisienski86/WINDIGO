"""
Unit tests for create_direct_perturbation_inputs.
"""

import pytest


class FakeFile:
    'Simple context-manager file mock that records written content'

    def __init__(self, path, written_dict):
        self.path = path
        self.written_dict = written_dict
        self.buffer = ""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.written_dict[self.path] = self.buffer
        return False

    def write(self, text):
        self.buffer += text

    def close(self):
        pass


def test_create_direct_perturbation_inputs_basic(monkeypatch):
    'Test basic file creation and naming for small energy grid'

    created_dirs = []
    written_files = {}

    monkeypatch.setattr(
        "os.mkdir",
        lambda folder: created_dirs.append(folder)
    )

    def fake_open(path, mode):
        return FakeFile(path, written_files)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WENDIGO.frendy_internal_functions import (
        create_direct_perturbation_inputs
    )

    energy_grid = [1.0, 2.0, 3.0]
    mt = 102
    nuclide = "U235"

    perturb_list, folder_name = create_direct_perturbation_inputs(
        nuclide=nuclide,
        mt_Number=mt,
        energy_grid=energy_grid,
        perturbation_coefficient=1.05,
    )

    # Folder name
    assert folder_name == "U235_DirectPerturbationInputs_ReactionMT_102"
    assert created_dirs == [folder_name]

    # Two intervals → two files
    assert len(perturb_list) == 2

    # Check filenames
    assert perturb_list[0] == f"{folder_name}/U235_0001\n"
    assert perturb_list[1] == f"{folder_name}/U235_0002\n"

    # Check file contents
    assert written_files[f"{folder_name}/U235_0001"] == "102     1.0     2.0     1.05"
    assert written_files[f"{folder_name}/U235_0002"] == "102     2.0     3.0     1.05"


def test_create_direct_perturbation_inputs_three_digit_index(monkeypatch):
    'Test filename formatting for ii >= 9 (00XX formatting)'

    created_dirs = []
    written_files = {}

    monkeypatch.setattr("os.mkdir", lambda folder: created_dirs.append(folder))

    def fake_open(path, mode):
        return FakeFile(path, written_files)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WENDIGO.frendy_internal_functions import (
        create_direct_perturbation_inputs
    )

    # 11 intervals → indices 0–10 → triggers 000X and 00XX formatting
    energy_grid = list(range(12))

    perturb_list, folder_name = create_direct_perturbation_inputs(
        nuclide="Xe135",
        mt_Number=18,
        energy_grid=energy_grid,
        perturbation_coefficient=0.9,
    )

    # Check formatting around the boundary
    assert perturb_list[0].endswith("Xe135_0001\n")
    assert perturb_list[8].endswith("Xe135_0009\n")
    assert perturb_list[9].endswith("Xe135_0010\n")
    assert perturb_list[10].endswith("Xe135_0011\n")


def test_create_direct_perturbation_inputs_large_index(monkeypatch):
    'Test filename formatting for ii > 98 (0XXX formatting)'

    created_dirs = []
    written_files = {}

    monkeypatch.setattr("os.mkdir", lambda folder: created_dirs.append(folder))

    def fake_open(path, mode):
        return FakeFile(path, written_files)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WENDIGO.frendy_internal_functions import (
        create_direct_perturbation_inputs
    )

    # 105 intervals → index 99 triggers the final formatting branch
    energy_grid = list(range(106))

    perturb_list, folder_name = create_direct_perturbation_inputs(
        nuclide="Mo95",
        mt_Number=51,
        energy_grid=energy_grid,
        perturbation_coefficient=1.2,
    )

    # Check the last few filenames
    assert perturb_list[98].endswith("Mo95_0099\n")
    assert perturb_list[99].endswith("Mo95_0100\n")
    assert perturb_list[104].endswith("Mo95_0105\n")