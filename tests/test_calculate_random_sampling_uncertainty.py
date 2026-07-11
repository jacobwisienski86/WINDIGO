import numpy as np
import pytest

from src.WINDIGO.post_processing_main_functions import (
    calculate_random_sampling_uncertainty,
)


def test_random_sampling_uncertainty_basic():
    """Correct sample standard deviation for a simple dataset."""

    data = np.array([10.0, 12.0, 14.0, 16.0])  # mean = 13

    # squared distances = [9, 1, 1, 9]
    # sum = 20
    # sample variance = 20 / (4 - 1) = 20/3
    expected = np.sqrt(20.0 / 3.0)

    result = calculate_random_sampling_uncertainty(data)

    assert np.isclose(result, expected)


def test_random_sampling_uncertainty_list_input():
    """List input should be converted to ndarray automatically."""

    data = [1.0, 2.0, 3.0]

    # mean = 2
    # squared distances = [1, 0, 1]
    # sum = 2
    # variance = 2 / (3 - 1) = 1
    expected = 1.0

    result = calculate_random_sampling_uncertainty(data)

    assert np.isclose(result, expected)


def test_random_sampling_uncertainty_two_points():
    """Two-point sample standard deviation is well-defined."""

    data = np.array([5.0, 9.0])

    # mean = 7
    # squared distances = [4, 4]
    # variance = 8 / (2 - 1) = 8
    expected = np.sqrt(8.0)

    result = calculate_random_sampling_uncertainty(data)

    assert np.isclose(result, expected)

def test_random_sampling_uncertainty_shape_independent():
    """Function should work for any 1D shape."""

    data = np.array([3.0, 7.0, 11.0, 15.0])

    result_flat = calculate_random_sampling_uncertainty(data)
    result_list = calculate_random_sampling_uncertainty(list(data))

    assert np.isclose(result_flat, result_list)
