"""
Unit tests for create_direct_perturbation_command_file.
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


def test_create_direct_perturbation_command_file_basic(monkeypatch):
    'Test that the .csh file is created with correct name and contents'

    written = {}

    def fake_open(path, mode):
        return FakeFile(written, path)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WENDIGO.frendy_internal_functions import (
        create_direct_perturbation_command_file
    )

    frendy_path = "/opt/frendy"
    list_file = "perturbation_list_U235_MT_102Direct.inp"
    unperturbed_ace = "/data/U235.ace"

    result = create_direct_perturbation_command_file(
        frendy_Path=frendy_path,
        perturbation_list_filename=list_file,
        unperturbed_ACE_file_path=unperturbed_ace,
    )

    # Filename correctness
    assert result == "run_create_perturbed_ace_file.csh"
    assert result in written

    lines = written[result]

    # Expected lines
    assert lines[0] == "#!/bin/csh\n"
    assert lines[1] == "\n"

    exe_expected = (
        f"set EXE     = {frendy_path}/tools/perturbation_ace_file/perturbation_ace_file.exe"
    )
    assert lines[2] == exe_expected
    assert lines[3] == "\n"

    assert lines[4] == f"set INP     = {list_file}"
    assert lines[5] == "\n"

    assert lines[6] == f"set ACE     = {unperturbed_ace}"
    assert lines[7] == "\n"

    assert lines[8] == "set LOG = results.log\n"
    assert lines[9] == 'echo "${EXE}  ${ACE}  ${INP}"      > ${LOG}\n'
    assert lines[10] == 'echo ""                           >> ${LOG}\n'
    assert lines[11] == '${EXE}  ${ACE}  ${INP} >> ${LOG}\n'


def test_create_direct_perturbation_command_file_varied_inputs(monkeypatch):
    'Test that arbitrary paths are inserted correctly into the script'

    written = {}

    def fake_open(path, mode):
        return FakeFile(written, path)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WENDIGO.frendy_internal_functions import (
        create_direct_perturbation_command_file
    )

    frendy_path = "/usr/local/FRENDY-3.0"
    list_file = "pert_list.inp"
    unperturbed_ace = "/tmp/ACE_FILES/Th232.ace"

    result = create_direct_perturbation_command_file(
        frendy_Path=frendy_path,
        perturbation_list_filename=list_file,
        unperturbed_ACE_file_path=unperturbed_ace,
    )

    assert result == "run_create_perturbed_ace_file.csh"

    lines = written[result]

    assert f"set EXE     = {frendy_path}/tools/perturbation_ace_file/perturbation_ace_file.exe" in lines[2]
    assert f"set INP     = {list_file}" in lines[4]
    assert f"set ACE     = {unperturbed_ace}" in lines[6]


def test_create_direct_perturbation_command_file_line_count(monkeypatch):
    'Test that the script always contains exactly 12 lines'

    written = {}

    def fake_open(path, mode):
        return FakeFile(written, path)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WENDIGO.frendy_internal_functions import (
        create_direct_perturbation_command_file
    )

    create_direct_perturbation_command_file(
        frendy_Path="/opt/frendy",
        perturbation_list_filename="list.inp",
        unperturbed_ACE_file_path="U235.ace",
    )

    lines = written["run_create_perturbed_ace_file.csh"]

    assert len(lines) == 12