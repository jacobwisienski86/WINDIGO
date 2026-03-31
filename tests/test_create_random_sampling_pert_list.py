"""
Unit tests for create_random_sampling_pert_list.
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


def test_create_random_sampling_pert_list_basic(monkeypatch):
    'Test basic list creation and filename correctness'

    written = {}

    def fake_open(path, mode):
        return FakeFile(written, path)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WINDIGO.frendy_internal_functions import (
        create_random_sampling_pert_list
    )

    result = create_random_sampling_pert_list(
        nuclide="U235",
        mt_Number=102,
        new_inputs_directory_name="/opt/frendy/U235_inputs",
        sample_size=3,
    )

    expected_filename = "perturbation_list_U235_MT_102.inp"
    assert result == expected_filename
    assert expected_filename in written

    lines = written[expected_filename]

    assert lines == [
        "/opt/frendy/U235_inputs/U235_0001\n",
        "/opt/frendy/U235_inputs/U235_0002\n",
        "/opt/frendy/U235_inputs/U235_0003\n",
    ]


def test_create_random_sampling_pert_list_three_digit_format(monkeypatch):
    'Test correct formatting for ii >= 9 (00XX formatting)'

    written = {}

    def fake_open(path, mode):
        return FakeFile(written, path)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WINDIGO.frendy_internal_functions import (
        create_random_sampling_pert_list
    )

    # 11 entries → indices 0–10 → triggers 000X and 00XX formatting
    result = create_random_sampling_pert_list(
        nuclide="Xe135",
        mt_Number=51,
        new_inputs_directory_name="/data/x",
        sample_size=11,
    )

    lines = written[result]

    assert lines[0].endswith("Xe135_0001\n")
    assert lines[8].endswith("Xe135_0009\n")
    assert lines[9].endswith("Xe135_0010\n")
    assert lines[10].endswith("Xe135_0011\n")


def test_create_random_sampling_pert_list_large_index(monkeypatch):
    'Test correct formatting for ii > 98 (0XXX formatting)'

    written = {}

    def fake_open(path, mode):
        return FakeFile(written, path)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WINDIGO.frendy_internal_functions import (
        create_random_sampling_pert_list
    )

    # 105 entries → index 99 triggers the final formatting branch
    result = create_random_sampling_pert_list(
        nuclide="Mo95",
        mt_Number=18,
        new_inputs_directory_name="/inputs",
        sample_size=105,
    )

    lines = written[result]

    assert lines[98].endswith("Mo95_0099\n")
    assert lines[99].endswith("Mo95_0100\n")
    assert lines[104].endswith("Mo95_0105\n")


def test_create_random_sampling_pert_list_varied_inputs(monkeypatch):
    'Test arbitrary directory and nuclide names'

    written = {}

    def fake_open(path, mode):
        return FakeFile(written, path)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WINDIGO.frendy_internal_functions import (
        create_random_sampling_pert_list
    )

    result = create_random_sampling_pert_list(
        nuclide="Th232",
        mt_Number=4,
        new_inputs_directory_name="/tmp/random_inputs",
        sample_size=2,
    )

    lines = written[result]

    assert lines[0] == "/tmp/random_inputs/Th232_0001\n"
    assert lines[1] == "/tmp/random_inputs/Th232_0002\n"