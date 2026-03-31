"""
Unit tests for create_random_sampling_tool_execution_file.
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


def test_create_random_sampling_tool_execution_file_basic(monkeypatch):
    'Test that the .csh file is created with correct name and contents'

    written = {}

    def fake_open(path, mode):
        return FakeFile(written, path)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WENDIGO.frendy_internal_functions import (
        create_random_sampling_tool_execution_file
    )

    exe_dir = "/opt/frendy/random_tool"
    tool_dir = "/opt/frendy/random_tool/config"

    result = create_random_sampling_tool_execution_file(
        executable_directory=exe_dir,
        random_sampling_tool_directory=tool_dir,
    )

    assert result == "run_make_perturbation_factor.csh"
    assert result in written

    lines = written[result]

    assert lines[0] == "#!/bin/csh\n"
    assert lines[1] == "\n"

    assert lines[2] == f"set EXE     = {exe_dir}\n"
    assert lines[3] == "\n"

    assert lines[4] == f"set INP        = {tool_dir}/sample_copy.inp"
    assert lines[5] == "\n"
    assert lines[6] == "\n"

    assert lines[7] == "set LOG = result.log\n"
    assert lines[8] == 'echo "${EXE}  ${INP}"      > ${LOG}\n'
    assert lines[9] == 'echo ""                   >> ${LOG}\n'
    assert lines[10] == '${EXE}  ${INP} >> ${LOG}\n'


def test_create_random_sampling_tool_execution_file_varied_inputs(monkeypatch):
    'Test that arbitrary paths are inserted correctly'

    written = {}

    def fake_open(path, mode):
        return FakeFile(written, path)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WENDIGO.frendy_internal_functions import (
        create_random_sampling_tool_execution_file
    )

    exe_dir = "/usr/local/bin/run_tool"
    tool_dir = "/tmp/random_sampling"

    result = create_random_sampling_tool_execution_file(
        executable_directory=exe_dir,
        random_sampling_tool_directory=tool_dir,
    )

    lines = written[result]

    assert f"set EXE     = {exe_dir}\n" == lines[2]
    assert f"set INP        = {tool_dir}/sample_copy.inp" == lines[4]


def test_create_random_sampling_tool_execution_file_line_count(monkeypatch):
    'Test that the script always contains exactly 11 lines'

    written = {}

    def fake_open(path, mode):
        return FakeFile(written, path)

    monkeypatch.setattr("builtins.open", fake_open)

    from src.WENDIGO.frendy_internal_functions import (
        create_random_sampling_tool_execution_file
    )

    create_random_sampling_tool_execution_file(
        executable_directory="/x",
        random_sampling_tool_directory="/y",
    )

    lines = written["run_make_perturbation_factor.csh"]

    assert len(lines) == 11