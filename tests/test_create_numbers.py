"""
Unit tests for create_numbers.
"""

import pytest


def test_create_numbers_basic():
    """
    Basic test: ensure correct zero-padded numbering.
    """

    from src.WINDIGO.openmc_internal_functions import create_numbers

    result = create_numbers(5)

    assert result == ["0001", "0002", "0003", "0004", "0005"]


def test_create_numbers_zero():
    """
    If directory_number = 0, the function should return an empty list.
    """

    from src.WINDIGO.openmc_internal_functions import create_numbers

    result = create_numbers(0)

    assert result == []


def test_create_numbers_large():
    """
    Ensure correct formatting for larger numbers (e.g., 100+).
    """

    from src.WINDIGO.openmc_internal_functions import create_numbers

    result = create_numbers(123)

    # First and last entries should be correct
    assert result[0] == "0001"
    assert result[-1] == "0123"

    # Length should match directory_number
    assert len(result) == 123


def test_create_numbers_type_and_format():
    """
    Ensure all outputs are strings and always 4 characters long.
    """

    from src.WINDIGO.openmc_internal_functions import create_numbers

    result = create_numbers(10)

    assert all(isinstance(x, str) for x in result)
    assert all(len(x) == 4 for x in result)