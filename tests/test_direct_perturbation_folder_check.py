"""
Unit tests for direct_perturbation_folder_check.
"""

import pytest


def test_direct_perturbation_folder_check_all_present(monkeypatch):
    'Test when all expected folders exist'

    calls = []

    def fake_exists(path):
        calls.append(path)
        return True

    monkeypatch.setattr("os.path.exists", fake_exists)

    from src.WENDIGO.frendy_internal_functions import (
        direct_perturbation_folder_check
    )

    result = direct_perturbation_folder_check(
        perturbed_ace_folder_path="/data/perturbed",
        energy_grid=[1.0, 2.0, 3.0, 4.0],
    )

    assert result is False

    # Expected folders: 0001, 0002, 0003
    assert calls == [
        "/data/perturbed/0001",
        "/data/perturbed/0002",
        "/data/perturbed/0003",
    ]


def test_direct_perturbation_folder_check_first_missing(monkeypatch):
    'Test when the first folder is missing'

    def fake_exists(path):
        return False  # first check fails immediately

    monkeypatch.setattr("os.path.exists", fake_exists)

    from src.WENDIGO.frendy_internal_functions import (
        direct_perturbation_folder_check
    )

    result = direct_perturbation_folder_check(
        perturbed_ace_folder_path="/out",
        energy_grid=[1.0, 2.0],
    )

    assert result is True


def test_direct_perturbation_folder_check_middle_missing(monkeypatch):
    'Test when a middle folder is missing'

    def fake_exists(path):
        # Missing the second folder only
        return not path.endswith("0002")

    monkeypatch.setattr("os.path.exists", fake_exists)

    from src.WENDIGO.frendy_internal_functions import (
        direct_perturbation_folder_check
    )

    result = direct_perturbation_folder_check(
        perturbed_ace_folder_path="/out",
        energy_grid=[1.0, 2.0, 3.0],
    )

    assert result is True


def test_direct_perturbation_folder_check_three_digit_format(monkeypatch):
    'Test folder naming for indices 9–98 (00XX formatting)'

    calls = []

    def fake_exists(path):
        calls.append(path)
        return True

    monkeypatch.setattr("os.path.exists", fake_exists)

    from src.WENDIGO.frendy_internal_functions import (
        direct_perturbation_folder_check
    )

    # 11 intervals → indices 0–10 → triggers 000X and 00XX formatting
    energy_grid = list(range(12))

    result = direct_perturbation_folder_check(
        perturbed_ace_folder_path="/pert",
        energy_grid=energy_grid,
    )

    assert result is False

    # Check boundary formatting
    assert calls[0].endswith("/0001")
    assert calls[8].endswith("/0009")
    assert calls[9].endswith("/0010")
    assert calls[10].endswith("/0011")


def test_direct_perturbation_folder_check_large_index(monkeypatch):
    'Test folder naming for ii > 98 (0XXX formatting)'

    calls = []

    def fake_exists(path):
        calls.append(path)
        return True

    monkeypatch.setattr("os.path.exists", fake_exists)

    from src.WENDIGO.frendy_internal_functions import (
        direct_perturbation_folder_check
    )

    # 105 intervals → index 99 triggers the final formatting branch
    energy_grid = list(range(106))

    result = direct_perturbation_folder_check(
        perturbed_ace_folder_path="/big",
        energy_grid=energy_grid,
    )

    assert result is False

    # Check formatting around the transition
    assert calls[98].endswith("/0099")
    assert calls[99].endswith("/0100")
    assert calls[104].endswith("/0105")