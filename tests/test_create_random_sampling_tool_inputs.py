"""
Unit tests for create_random_sampling_tool_inputs.
"""

import pytest


class FakeFile:
    'Simple context-manager file mock that records written lines'

    def __init__(self, written_dict, path):
        self.written_dict = written_dict
        self.path = path
        self.buffer = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.written_dict[self.path] = self.buffer
        return False

    def writelines(self, lines):
        self.buffer.extend(lines)

    def close(self):
        pass


def test_create_random_sampling_tool_inputs_basic(monkeypatch):
    'Test basic file creation and formatting'

    written = {}

    def fake_open(path, mode):
        return FakeFile(written, path)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WENDIGO.frendy_internal_functions import (
        create_random_sampling_tool_inputs
    )

    sample_file = create_random_sampling_tool_inputs(
        sample_size=50,
        seed=12345,
        relative_covariance_matrix_path="/data/cov.csv",
        energy_grid=[1.0, 2.0, 3.0],
        nuclide="U235",
        mt_Number=102,
    )

    assert sample_file == "sample_copy.inp"
    assert "sample_copy.inp" in written

    lines = written["sample_copy.inp"]

    # Header block
    assert lines[0] == "<sample_size>         50\n"
    assert lines[1] == "\n"
    assert lines[2] == "<seed>                12345\n"
    assert lines[3] == "\n"
    assert lines[4] == "<relative_covariance> /data/cov.csv\n"
    assert lines[5] == "\n"

    # Energy grid block
    assert lines[6] == "<energy_grid>          (1.0\n"
    assert lines[7] == "                       2.0\n"
    assert lines[8] == "                       3.0)\n"

    # After energy grid
    assert lines[9] == "\n"

    # Nuclide and reaction
    assert lines[10] == "<nuclide>             (U235)\n"
    assert lines[11] == "\n"
    assert lines[12] == "<reaction>            (102)\n"
    assert lines[13] == "\n"


def test_create_random_sampling_tool_inputs_varied_paths(monkeypatch):
    'Test that arbitrary paths and values are inserted correctly'

    written = {}

    def fake_open(path, mode):
        return FakeFile(written, path)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WENDIGO.frendy_internal_functions import (
        create_random_sampling_tool_inputs
    )

    create_random_sampling_tool_inputs(
        sample_size=10,
        seed=777,
        relative_covariance_matrix_path="/tmp/rel_cov.csv",
        energy_grid=[0.01, 0.02],
        nuclide="Xe135",
        mt_Number=18,
    )

    lines = written["sample_copy.inp"]

    assert "<sample_size>         10\n" == lines[0]
    assert "<seed>                777\n" == lines[2]
    assert "<relative_covariance> /tmp/rel_cov.csv\n" == lines[4]
    assert "<nuclide>             (Xe135)\n" == lines[9]
    assert "<reaction>            (18)\n" == lines[11]


def test_create_random_sampling_tool_inputs_energy_grid_formatting(monkeypatch):
    'Test correct formatting for first, middle, and last energy grid entries'

    written = {}

    def fake_open(path, mode):
        return FakeFile(written, path)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WENDIGO.frendy_internal_functions import (
        create_random_sampling_tool_inputs
    )

    grid = [0.1, 0.2, 0.3, 0.4]

    create_random_sampling_tool_inputs(
        sample_size=5,
        seed=42,
        relative_covariance_matrix_path="cov.csv",
        energy_grid=grid,
        nuclide="Mo95",
        mt_Number=51,
    )

    lines = written["sample_copy.inp"]

    # Energy grid starts at index 6
    assert lines[6] == "<energy_grid>          (0.1\n"
    assert lines[7] == "                       0.2\n"
    assert lines[8] == "                       0.3\n"
    assert lines[9] == "                       0.4)\n"


def test_create_random_sampling_tool_inputs_line_count(monkeypatch):
    'Test that line count matches expected structure'

    written = {}

    def fake_open(path, mode):
        return FakeFile(written, path)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WENDIGO.frendy_internal_functions import (
        create_random_sampling_tool_inputs
    )

    grid = [1.0, 2.0, 3.0, 4.0]

    create_random_sampling_tool_inputs(
        sample_size=100,
        seed=999,
        relative_covariance_matrix_path="cov.csv",
        energy_grid=grid,
        nuclide="Th232",
        mt_Number=4,
    )

    lines = written["sample_copy.inp"]

    # Structure:
    # 0 sample_size
    # 1 blank
    # 2 seed
    # 3 blank
    # 4 covariance
    # 5 blank
    # 6–9 energy grid (4 entries)
    # 10 blank
    # 11 nuclide
    # 12 blank
    # 13 reaction
    # 14 blank
    assert len(lines) == 15