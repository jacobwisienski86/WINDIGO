"""
Unit tests for write_upgrade_lines.
"""

import pytest


def test_write_upgrade_lines_low_energy(monkeypatch):
    'Test behavior for energies < 99.99'

    from src.WINDIGO.frendy_internal_functions import write_upgrade_lines

    energy_grid = [1.0, 2.0, 3.0]

    result = write_upgrade_lines(energy_grid)

    # Expected upgrade bounds:
    # index 0: +1e-6
    # index 1: -1e-6, +1e-6
    # index 2: -1e-6
    expected_bounds = [
        1.0 + 1e-6,
        2.0 - 1e-6,
        2.0 + 1e-6,
        3.0 - 1e-6,
    ]

    # Check formatting of lines
    assert result[0] == f"    add_grid_data    ({expected_bounds[0]}\n"
    assert result[1] == f"        {expected_bounds[1]}\n"
    assert result[2] == f"        {expected_bounds[2]}\n"
    assert result[3] == f"        {expected_bounds[3]})\n"


def test_write_upgrade_lines_mid_energy(monkeypatch):
    'Test behavior for energies between 99.99 and 99990'

    from src.WINDIGO.frendy_internal_functions import write_upgrade_lines

    energy_grid = [100.0, 200.0, 300.0]

    result = write_upgrade_lines(energy_grid)

    expected_bounds = [
        100.0 + 0.1,
        200.0 - 0.1,
        200.0 + 0.1,
        300.0 - 0.1,
    ]

    assert result[0] == f"    add_grid_data    ({expected_bounds[0]}\n"
    assert result[1] == f"        {expected_bounds[1]}\n"
    assert result[2] == f"        {expected_bounds[2]}\n"
    assert result[3] == f"        {expected_bounds[3]})\n"


def test_write_upgrade_lines_high_energy(monkeypatch):
    'Test behavior for energies >= 99990'

    from src.WINDIGO.frendy_internal_functions import write_upgrade_lines

    energy_grid = [100000.0, 200000.0, 300000.0]

    result = write_upgrade_lines(energy_grid)

    expected_bounds = [
        100000.0 + 1000,
        200000.0 - 1000,
        200000.0 + 1000,
        300000.0 - 1000,
    ]

    assert result[0] == f"    add_grid_data    ({expected_bounds[0]}\n"
    assert result[1] == f"        {expected_bounds[1]}\n"
    assert result[2] == f"        {expected_bounds[2]}\n"
    assert result[3] == f"        {expected_bounds[3]})\n"