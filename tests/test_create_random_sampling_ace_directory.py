"""
Unit tests for create_random_sampling_ace_directory.
"""

import pytest


def test_create_random_sampling_ace_directory_basic(monkeypatch):
    'Test directory creation and both move operations'

    mkdir_calls = []
    move_calls = []

    def fake_mkdir(path):
        mkdir_calls.append(path)

    def fake_move(src, dst):
        move_calls.append((src, dst))

    monkeypatch.setattr("os.mkdir", fake_mkdir)
    monkeypatch.setattr("shutil.move", fake_move)

    from src.WINDIGO.frendy_internal_functions import (
        create_random_sampling_ace_directory
    )

    result = create_random_sampling_ace_directory(
        frendy_Path="/opt/frendy",
        nuclide="U235",
        mt_Number=102,
        perturbation_list_filename="pert_list.inp",
        new_inputs_directory_name="U235_inputs",
    )

    expected_dir = "/opt/frendy/U235_RandomSamplingACEFiles_ReactionMT_102"
    assert result == expected_dir

    # mkdir called correctly
    assert mkdir_calls == [expected_dir]

    # First move: list file
    assert move_calls[0] == (
        "/opt/frendy/pert_list.inp",
        f"{expected_dir}/pert_list.inp"
    )

    # Second move: inputs directory
    assert move_calls[1] == (
        "/opt/frendy/U235_inputs",
        f"{expected_dir}/U235_inputs"
    )


def test_create_random_sampling_ace_directory_varied_inputs(monkeypatch):
    'Test arbitrary paths and nuclide names'

    mkdir_calls = []
    move_calls = []

    monkeypatch.setattr("os.mkdir", lambda p: mkdir_calls.append(p))
    monkeypatch.setattr("shutil.move", lambda s, d: move_calls.append((s, d)))

    from src.WINDIGO.frendy_internal_functions import (
        create_random_sampling_ace_directory
    )

    result = create_random_sampling_ace_directory(
        frendy_Path="/FRENDY",
        nuclide="Xe135",
        mt_Number=51,
        perturbation_list_filename="list.inp",
        new_inputs_directory_name="Xe135_inputs",
    )

    expected_dir = "/FRENDY/Xe135_RandomSamplingACEFiles_ReactionMT_51"
    assert result == expected_dir

    assert mkdir_calls == [expected_dir]

    assert move_calls[0] == ("/FRENDY/list.inp", f"{expected_dir}/list.inp")
    assert move_calls[1] == ("/FRENDY/Xe135_inputs", f"{expected_dir}/Xe135_inputs")


def test_create_random_sampling_ace_directory_move_order(monkeypatch):
    'Test that moves occur in the correct order'

    move_calls = []

    monkeypatch.setattr("os.mkdir", lambda p: None)
    monkeypatch.setattr("shutil.move", lambda s, d: move_calls.append((s, d)))

    from src.WINDIGO.frendy_internal_functions import (
        create_random_sampling_ace_directory
    )

    create_random_sampling_ace_directory(
        frendy_Path="/root",
        nuclide="Mo95",
        mt_Number=18,
        perturbation_list_filename="plist.inp",
        new_inputs_directory_name="Mo95_inputs",
    )

    # Ensure exactly two moves
    assert len(move_calls) == 2

    # First move: list file
    assert move_calls[0][0] == "/root/plist.inp"

    # Second move: inputs directory
    assert move_calls[1][0] == "/root/Mo95_inputs"