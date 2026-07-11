# tests/test_create_unperturbed_ace_generation_input.py

import builtins
import pytest

from src.WINDIGO.frendy_internal_functions import (
    create_unperturbed_ace_generation_input,
)


def test_create_unperturbed_ace_generation_input_normal(monkeypatch):
    """Test normal (non-upgrade) ACE input file creation."""

    written_path = None
    written_lines = []

    class FakeFile:
        def __init__(self, path, mode):
            nonlocal written_path
            written_path = path

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def writelines(self, lines):
            written_lines.extend(lines)

        def close(self):
            pass

    monkeypatch.setattr(builtins, "open", lambda p, m: FakeFile(p, m))

    printed = []
    monkeypatch.setattr(builtins, "print", lambda msg: printed.append(msg))

    result = create_unperturbed_ace_generation_input(
        frendy_Path="/opt/frendy",
        nuclide="U235",
        endf_file_dat="/data/U235.dat",
        temperature=300,
        upgrade_Flag=False,
        energy_grid=[1.0, 2.0],
    )

    expected_path = "/opt/frendy/frendy/main/U235_acegenerator_normal.dat"
    assert result == expected_path
    assert written_path == expected_path

    assert written_lines[0] == "ace_file_generation_fast_mode\n"
    assert written_lines[1] == "    nucl_file_name    /data/U235.dat\n"
    assert written_lines[2] == "    temp    300\n"
    assert written_lines[3] == "    ace_file_name    U235.ace\n"

    assert len(written_lines) == 4
    assert expected_path in printed[0]


def test_create_unperturbed_ace_generation_input_upgrade(monkeypatch):
    """Test upgrade mode, ensuring write_upgrade_lines is called and lines appended."""

    written_lines = []
    written_path = None

    class FakeFile:
        def __init__(self, path, mode):
            nonlocal written_path
            written_path = path

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def writelines(self, lines):
            written_lines.extend(lines)

        def close(self):
            pass

    monkeypatch.setattr(builtins, "open", lambda p, m: FakeFile(p, m))

    fake_upgrade_lines = ["    add_grid_data    (1.0\n", "        2.0)\n"]
    monkeypatch.setattr(
        "src.WINDIGO.frendy_internal_functions.write_upgrade_lines",
        lambda energy_grid: fake_upgrade_lines,
    )

    printed = []
    monkeypatch.setattr(builtins, "print", lambda msg: printed.append(msg))

    result = create_unperturbed_ace_generation_input(
        frendy_Path="/opt/frendy",
        nuclide="U238",
        endf_file_dat="/data/U238.dat",
        temperature=600,
        upgrade_Flag=True,
        energy_grid=[1.0, 2.0],
    )

    expected_path = "/opt/frendy/frendy/main/U238_acegenerator_upgrade.dat"
    assert result == expected_path
    assert written_path == expected_path

    assert written_lines[0] == "ace_file_generation_fast_mode\n"
    assert written_lines[1] == "    nucl_file_name    /data/U238.dat\n"
    assert written_lines[2] == "    temp    600\n"
    assert written_lines[3] == "    ace_file_name    U238_upgrade.ace\n"

    assert written_lines[4:] == fake_upgrade_lines
    assert expected_path in printed[0]


def test_create_unperturbed_ace_generation_input_energy_grid_none(monkeypatch):
    """Ensure energy_grid=None is treated as an empty list."""

    written_lines = []
    written_path = None

    class FakeFile:
        def __init__(self, path, mode):
            nonlocal written_path
            written_path = path

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def writelines(self, lines):
            written_lines.extend(lines)

        def close(self):
            pass

    monkeypatch.setattr(builtins, "open", lambda p, m: FakeFile(p, m))

    printed = []
    monkeypatch.setattr(builtins, "print", lambda msg: printed.append(msg))

    result = create_unperturbed_ace_generation_input(
        frendy_Path="/opt/frendy",
        nuclide="Pu239",
        endf_file_dat="/data/Pu239.dat",
        temperature=900,
        upgrade_Flag=False,
        energy_grid=None,
    )

    expected_path = "/opt/frendy/frendy/main/Pu239_acegenerator_normal.dat"
    assert result == expected_path
    assert written_path == expected_path

    assert len(written_lines) == 4
