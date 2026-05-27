import numpy as np

from src.WINDIGO.post_processing_internal_functions import (
    convert_per_lethargy,
)


def test_convert_per_lethargy_basic():
    """Test basic conversion of sensitivity coefficients to per-lethargy form."""
    relative_sens = np.array([1.0, 2.0, 3.0])
    energy_grid = np.array([1.0, 2.0, 4.0, 8.0])  # strictly increasing

    # Compute expected lethargy widths
    lethargy_widths = np.log(energy_grid[1:] / energy_grid[:-1])

    expected = relative_sens / lethargy_widths
    expected = np.insert(expected, 0, 0)

    result = convert_per_lethargy(relative_sens, energy_grid)

    assert np.allclose(result, expected)


def test_convert_per_lethargy_shape():
    """Ensure output has one more element than the input coefficients."""
    relative_sens = np.array([0.5, 1.5, 2.5, 3.5])
    energy_grid = np.array([1.0, 1.5, 2.0, 3.0, 6.0])

    result = convert_per_lethargy(relative_sens, energy_grid)

    # Should be len(relative_sens) + 1
    assert result.shape == (len(relative_sens) + 1,)


def test_convert_per_lethargy_nonuniform_grid():
    """Test behavior with a non-uniform energy grid."""
    relative_sens = np.array([10.0, 20.0])
    energy_grid = np.array([0.5, 1.0, 10.0])  # non-uniform spacing

    lethargy_widths = np.log(energy_grid[1:] / energy_grid[:-1])
    expected = relative_sens / lethargy_widths
    expected = np.insert(expected, 0, 0)

    result = convert_per_lethargy(relative_sens, energy_grid)

    assert np.allclose(result, expected)


def test_convert_per_lethargy_zero_inserted():
    """Ensure the first element of the output is always zero."""
    relative_sens = np.array([5.0])
    energy_grid = np.array([1.0, 2.0])

    result = convert_per_lethargy(relative_sens, energy_grid)

    assert result[0] == 0.0
