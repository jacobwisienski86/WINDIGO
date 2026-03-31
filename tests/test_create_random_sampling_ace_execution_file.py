"""
Unit tests for create_random_sampling_ace_execution_file.
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


def test_create_random_sampling_ace_execution_file_basic(monkeypatch):
    'Test that the .csh file is created with correct name and contents'

    written = {}

    def fake_open(path, mode):
        return FakeFile(written, path)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WINDIGO.frendy_internal_functions import (
        create_random_sampling_ace_execution_file
    )

    frendy_path = "/opt/frendy"
    ace_dir = "/opt/frendy/U235_RSACE"
    nuclide = "U235"
    mt = 102
    unperturbed = "/data/U235.ace"

    result = create_random_sampling_ace_execution_file(
        frendy_Path=frendy_path,
        ace_files_directory=ace_dir,
        nuclide=nuclide,
        mt_Number=mt,
        unperturbed_ACE_file_path=unperturbed,
    )

    assert result == "run_create_perturbed_ace_file.csh"
    assert result in written

    lines = written[result]

    # Shebang + blank line
    assert lines[0] == "#!/bin/csh\n"
    assert lines[1] == "\n"

    # EXE line
    exe_expected = (
        f"set EXE     = {frendy_path}/tools/perturbation_ace_file/perturbation_ace_file.exe"
    )
    assert lines[2] == exe_expected
    assert lines[3] == "\n"

    # INP line
    inp_expected = (
        f"set INP     = {ace_dir}/perturbation_list_{nuclide}_MT_{mt}.inp"
    )
    assert lines[4] == inp_expected
    assert lines[5] == "\n"

    # ACE line
    assert lines[6] == f"set ACE     = {unperturbed}"
    assert lines[7] == "\n"

    # Log + echo + run lines
    assert lines[8] == "set LOG = results.log\n"
    assert lines[9] == 'echo "${EXE}  ${ACE}  ${INP}"      > ${LOG}\n'
    assert lines[10] == 'echo ""                           >> ${LOG}\n'
    assert lines[11] == '${EXE}  ${ACE}  ${INP} >> ${LOG}\n'


def test_create_random_sampling_ace_execution_file_varied_inputs(monkeypatch):
    'Test that arbitrary paths and nuclide names are inserted correctly'

    written = {}

    def fake_open(path, mode):
        return FakeFile(written, path)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WINDIGO.frendy_internal_functions import (
        create_random_sampling_ace_execution_file
    )

    frendy_path = "/FRENDY"
    ace_dir = "/FRENDY/Xe135_RSACE"
    nuclide = "Xe135"
    mt = 51
    unperturbed = "/tmp/Xe135.ace"

    result = create_random_sampling_ace_execution_file(
        frendy_Path=frendy_path,
        ace_files_directory=ace_dir,
        nuclide=nuclide,
        mt_Number=mt,
        unperturbed_ACE_file_path=unperturbed,
    )

    lines = written[result]

    assert f"set EXE     = {frendy_path}/tools/perturbation_ace_file/perturbation_ace_file.exe" == lines[2]
    assert f"set INP     = {ace_dir}/perturbation_list_{nuclide}_MT_{mt}.inp" == lines[4]
    assert f"set ACE     = {unperturbed}" == lines[6]


def test_create_random_sampling_ace_execution_file_line_count(monkeypatch):
    'Test that the script always contains exactly 12 lines'

    written = {}

    def fake_open(path, mode):
        return FakeFile(written, path)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WINDIGO.frendy_internal_functions import (
        create_random_sampling_ace_execution_file
    )

    create_random_sampling_ace_execution_file(
        frendy_Path="/x",
        ace_files_directory="/y",
        nuclide="Mo95",
        mt_Number=18,
        unperturbed_ACE_file_path="/z",
    )

    lines = written["run_create_perturbed_ace_file.csh"]

    assert len(lines) == 12