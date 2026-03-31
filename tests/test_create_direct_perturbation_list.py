"""
Unit tests for create_direct_perturbation_list.
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


def test_create_direct_perturbation_list_basic(monkeypatch):
    'Test that the list file is created with correct name and contents'

    written = {}

    def fake_open(path, mode):
        return FakeFile(written, path)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WINDIGO.frendy_internal_functions import (
        create_direct_perturbation_list
    )

    lines = ["file1\n", "file2\n", "file3\n"]

    result = create_direct_perturbation_list(
        nuclide="U235",
        mt_Number=102,
        perturbation_list_lines=lines,
    )

    expected_filename = "perturbation_list_U235_MT_102Direct.inp"
    assert result == expected_filename

    assert expected_filename in written
    assert written[expected_filename] == lines


def test_create_direct_perturbation_list_empty(monkeypatch):
    'Test that an empty list still creates a valid file'

    written = {}

    def fake_open(path, mode):
        return FakeFile(written, path)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WINDIGO.frendy_internal_functions import (
        create_direct_perturbation_list
    )

    result = create_direct_perturbation_list(
        nuclide="Xe135",
        mt_Number=51,
        perturbation_list_lines=[],
    )

    expected_filename = "perturbation_list_Xe135_MT_51Direct.inp"
    assert result == expected_filename

    assert written[expected_filename] == []


def test_create_direct_perturbation_list_varied_lines(monkeypatch):
    'Test that arbitrary strings are written exactly as provided'

    written = {}

    def fake_open(path, mode):
        return FakeFile(written, path)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WINDIGO.frendy_internal_functions import (
        create_direct_perturbation_list
    )

    lines = [
        "alpha\n",
        "beta gamma\n",
        "12345\n",
        "U235_0001\n",
    ]

    result = create_direct_perturbation_list(
        nuclide="Mo95",
        mt_Number=18,
        perturbation_list_lines=lines,
    )

    expected_filename = "perturbation_list_Mo95_MT_18Direct.inp"
    assert result == expected_filename

    assert written[expected_filename] == lines