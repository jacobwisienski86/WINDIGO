"""
Unit tests for random_sampling_folder_check.
"""

import pytest


def test_random_sampling_folder_check_all_present(monkeypatch):
    'Test when all expected folders exist'

    calls = []

    def fake_exists(path):
        calls.append(path)
        return True

    monkeypatch.setattr("os.path.exists", fake_exists)

    from src.WINDIGO.frendy_internal_functions import (
        random_sampling_folder_check
    )

    result = random_sampling_folder_check(
        sample_size=4,
        ace_files_directory="/data/ACE/",
    )

    assert result is False

    # Expected folders: 0001, 0002, 0003, 0004
    assert calls == [
        "/data/ACE/0001",
        "/data/ACE/0002",
        "/data/ACE/0003",
        "/data/ACE/0004",
    ]


def test_random_sampling_folder_check_first_missing(monkeypatch):
    'Test when the first folder is missing'

    def fake_exists(path):
        return False

    monkeypatch.setattr("os.path.exists", fake_exists)

    from src.WINDIGO.frendy_internal_functions import (
        random_sampling_folder_check
    )

    result = random_sampling_folder_check(
        sample_size=3,
        ace_files_directory="/ACE/",
    )

    assert result is True


def test_random_sampling_folder_check_middle_missing(monkeypatch):
    'Test when a middle folder is missing'

    def fake_exists(path):
        return not path.endswith("0002")

    monkeypatch.setattr("os.path.exists", fake_exists)

    from src.WINDIGO.frendy_internal_functions import (
        random_sampling_folder_check
    )

    result = random_sampling_folder_check(
        sample_size=3,
        ace_files_directory="/ACE/",
    )

    assert result is True


def test_random_sampling_folder_check_three_digit_format(monkeypatch):
    'Test folder naming for indices 9–98 (00XX formatting)'

    calls = []

    def fake_exists(path):
        calls.append(path)
        return True

    monkeypatch.setattr("os.path.exists", fake_exists)

    from src.WINDIGO.frendy_internal_functions import (
        random_sampling_folder_check
    )

    # 11 samples → indices 0–10 → triggers 000X and 00XX formatting
    random_sampling_folder_check(
        sample_size=11,
        ace_files_directory="/pert/",
    )

    assert calls[0].endswith("0001")
    assert calls[8].endswith("0009")
    assert calls[9].endswith("0010")
    assert calls[10].endswith("0011")


def test_random_sampling_folder_check_large_index(monkeypatch):
    'Test folder naming for ii > 98 (0XXX formatting)'

    calls = []

    def fake_exists(path):
        calls.append(path)
        return True

    monkeypatch.setattr("os.path.exists", fake_exists)

    from src.WINDIGO.frendy_internal_functions import (
        random_sampling_folder_check
    )

    # 105 samples → index 99 triggers the final formatting branch
    random_sampling_folder_check(
        sample_size=105,
        ace_files_directory="/big/",
    )

    assert calls[98].endswith("0099")
    assert calls[99].endswith("0100")
    assert calls[104].endswith("0105")