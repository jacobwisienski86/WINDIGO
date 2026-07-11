import numpy as np
import pytest

from src.WINDIGO.post_processing_internal_functions import check_input_types


def test_check_input_types_converts_lists_to_ndarrays():
    """Ensure lists are converted to numpy ndarrays."""
    inputs = [[1, 2, 3], [4, 5]]
    result = check_input_types(inputs)

    assert all(isinstance(item, np.ndarray) for item in result)
    assert np.array_equal(result[0], np.array([1, 2, 3]))
    assert np.array_equal(result[1], np.array([4, 5]))


def test_check_input_types_preserves_ndarrays():
    """Ensure ndarray inputs are returned unchanged."""
    arr1 = np.array([1, 2, 3])
    arr2 = np.array([4, 5, 6])

    result = check_input_types([arr1, arr2])

    # They should be the same objects, not copies
    assert result[0] is arr1
    assert result[1] is arr2


def test_check_input_types_mixed_inputs():
    """Ensure mixed list/ndarray inputs are handled correctly."""
    arr = np.array([10, 20])
    lst = [1, 2, 3]

    result = check_input_types([arr, lst])

    assert result[0] is arr
    assert isinstance(result[1], np.ndarray)
    assert np.array_equal(result[1], np.array([1, 2, 3]))


def test_check_input_types_nested_lists():
    """Ensure nested lists are converted to ndarrays with correct shape."""
    nested = [[1, 2], [3, 4]]
    result = check_input_types([nested])

    assert isinstance(result[0], np.ndarray)
    assert result[0].shape == (2, 2)
    assert np.array_equal(result[0], np.array([[1, 2], [3, 4]]))


def test_check_input_types_preserves_length():
    """Ensure the output list has the same length as the input list."""
    inputs = [1, [2, 3], np.array([4])]
    result = check_input_types(inputs)

    assert len(result) == len(inputs)
