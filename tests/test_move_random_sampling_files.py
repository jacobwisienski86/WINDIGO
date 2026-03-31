"""
Unit tests for move_random_sampling_files.
"""

import pytest


def test_move_random_sampling_files_basic(monkeypatch):
    'Test that both moves occur with correct paths'

    moves = []

    def fake_move(src, dst):
        moves.append((src, dst))

    monkeypatch.setattr("shutil.move", fake_move)

    from src.WENDIGO.frendy_internal_functions import (
        move_random_sampling_files
    )

    result = move_random_sampling_files(
        random_sampling_tool_directory="/tmp/random",
        nuclide="U235",
        frendy_Path="/opt/frendy",
        mt_Number=102,
    )

    # Expected new directory name
    expected_name = "U235_RandomSamplingInputs_ReactionMT_102_Inputs"
    assert result == expected_name

    # First move: move /tmp/random/U235 → /opt/frendy
    assert moves[0] == ("/tmp/random/U235", "/opt/frendy")

    # Second move: rename /opt/frendy/U235 → /opt/frendy/<new_name>
    assert moves[1] == (
        "/opt/frendy/U235",
        f"/opt/frendy/{expected_name}"
    )


def test_move_random_sampling_files_varied_inputs(monkeypatch):
    'Test that arbitrary paths and nuclides are handled correctly'

    moves = []

    def fake_move(src, dst):
        moves.append((src, dst))

    monkeypatch.setattr("shutil.move", fake_move)

    from src.WENDIGO.frendy_internal_functions import (
        move_random_sampling_files
    )

    result = move_random_sampling_files(
        random_sampling_tool_directory="/data/tools",
        nuclide="Xe135",
        frendy_Path="/FRENDY",
        mt_Number=51,
    )

    expected_name = "Xe135_RandomSamplingInputs_ReactionMT_51_Inputs"
    assert result == expected_name

    assert moves[0] == ("/data/tools/Xe135", "/FRENDY")
    assert moves[1] == ("/FRENDY/Xe135", f"/FRENDY/{expected_name}")


def test_move_random_sampling_files_move_order(monkeypatch):
    'Test that the two moves occur in the correct order'

    moves = []

    def fake_move(src, dst):
        moves.append((src, dst))

    monkeypatch.setattr("shutil.move", fake_move)

    from src.WENDIGO.frendy_internal_functions import (
        move_random_sampling_files
    )

    move_random_sampling_files(
        random_sampling_tool_directory="/root/tools",
        nuclide="Mo95",
        frendy_Path="/F",
        mt_Number=18,
    )

    # Ensure exactly two moves
    assert len(moves) == 2

    # Order matters
    assert moves[0][0] == "/root/tools/Mo95"   # first move
    assert moves[1][0] == "/F/Mo95"            # second move