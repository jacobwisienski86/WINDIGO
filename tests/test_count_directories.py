"""
Unit tests for count_directories.
"""

import pytest


class MockDirEntry:
    """
    Simple mock for os.DirEntry objects.
    """

    def __init__(self, path, is_dir):
        self.path = path
        self._is_dir = is_dir

    def is_dir(self):
        return self._is_dir


@pytest.fixture
def mock_scandir(monkeypatch):
    """
    Fixture to mock os.scandir with a custom list of entries.
    """

    def _mock(entries):
        def fake_scandir(path):
            for entry in entries:
                yield entry

        monkeypatch.setattr("os.scandir", fake_scandir)

    return _mock


def test_count_directories_basic(mock_scandir):
    """
    Count only directories and skip files.
    """

    from src.WINDIGO.openmc_internal_functions import count_directories

    entries = [
        MockDirEntry("folderA", True),
        MockDirEntry("file.txt", False),
        MockDirEntry("folderB", True),
    ]

    mock_scandir(entries)

    result = count_directories("/fake/path")
    assert result == 2


def test_count_directories_skips_input_dirs(mock_scandir):
    """
    Directories containing 'Input' or 'input' should be skipped.
    """

    from src.WINDIGO.openmc_internal_functions import count_directories

    entries = [
        MockDirEntry("Input_Files", True),
        MockDirEntry("folder1", True),
        MockDirEntry("myinputdata", True),
        MockDirEntry("folder2", True),
    ]

    mock_scandir(entries)

    result = count_directories("/fake/path")
    assert result == 2  # only folder1 and folder2 count


def test_count_directories_empty(mock_scandir):
    """
    No directories should return 0.
    """

    from src.WINDIGO.openmc_internal_functions import count_directories

    entries = []
    mock_scandir(entries)

    result = count_directories("/fake/path")
    assert result == 0


def test_count_directories_mixed_case_input(mock_scandir):
    """
    Ensure case-insensitive matching for 'Input' directories.
    """

    from src.WINDIGO.openmc_internal_functions import count_directories

    entries = [
        MockDirEntry("InPuT_folder", True),
        MockDirEntry("folderX", True),
        MockDirEntry("INPUT_data", True),
        MockDirEntry("folderY", True),
    ]

    mock_scandir(entries)

    result = count_directories("/fake/path")
    assert result == 2