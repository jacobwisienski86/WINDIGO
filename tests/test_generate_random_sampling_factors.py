"""
Unit tests for generate_random_sampling_factors.
"""

import pytest
from io import StringIO
import sys


def test_generate_random_sampling_factors_success(monkeypatch):
    'Test successful creation prints correct message and no cleanup'

    calls = {
        "system": [],
        "exists": [],
        "remove": []
    }

    def fake_system(cmd):
        calls["system"].append(cmd)
        return 0

    def fake_exists(path):
        calls["exists"].append(path)
        return True

    def fake_remove(path):
        calls["remove"].append(path)

    monkeypatch.setattr("os.system", fake_system)
    monkeypatch.setattr("os.path.exists", fake_exists)
    monkeypatch.setattr("os.remove", fake_remove)

    captured = StringIO()
    monkeypatch.setattr(sys, "stdout", captured)

    from src.WINDIGO.frendy_internal_functions import (
        generate_random_sampling_factors
    )

    generate_random_sampling_factors(
        execution_filename="run_tool.csh",
        random_sampling_tool_directory="/tmp/random",
        nuclide="U235",
        sample_filename="sample_copy.inp",
        cleanup_Flag=False,
    )

    # Correct command executed
    assert calls["system"] == ["csh ./run_tool.csh"]

    # Correct folder checked
    assert calls["exists"] == ["/tmp/random/U235"]

    # No cleanup
    assert calls["remove"] == []

    # Correct print
    assert "Perturbation factors created successfully" in captured.getvalue()


def test_generate_random_sampling_factors_failure(monkeypatch):
    'Test failure message when folder does not exist'

    calls = {"exists": []}

    def fake_exists(path):
        calls["exists"].append(path)
        return False

    monkeypatch.setattr("os.path.exists", fake_exists)
    monkeypatch.setattr("os.system", lambda cmd: None)
    monkeypatch.setattr("os.remove", lambda path: None)

    captured = StringIO()
    monkeypatch.setattr(sys, "stdout", captured)

    from src.WINDIGO.frendy_internal_functions import (
        generate_random_sampling_factors
    )

    generate_random_sampling_factors(
        execution_filename="run_tool.csh",
        random_sampling_tool_directory="/tmp/random",
        nuclide="Xe135",
        sample_filename="sample_copy.inp",
        cleanup_Flag=False,
    )

    assert calls["exists"] == ["/tmp/random/Xe135"]
    assert "not created successfully" in captured.getvalue()


def test_generate_random_sampling_factors_cleanup(monkeypatch):
    'Test cleanup removes both files when cleanup_Flag=True'

    removed = []

    monkeypatch.setattr("os.system", lambda cmd: None)
    monkeypatch.setattr("os.path.exists", lambda path: True)
    monkeypatch.setattr("os.remove", lambda path: removed.append(path))

    captured = StringIO()
    monkeypatch.setattr(sys, "stdout", captured)

    from src.WINDIGO.frendy_internal_functions import (
        generate_random_sampling_factors
    )

    generate_random_sampling_factors(
        execution_filename="run_tool.csh",
        random_sampling_tool_directory="/tmp/random",
        nuclide="Mo95",
        sample_filename="sample_copy.inp",
        cleanup_Flag=True,
    )

    # Both files removed
    assert removed == ["sample_copy.inp", "run_tool.csh"]

    # Success message printed
    assert "created successfully" in captured.getvalue()