# tests/test_impedance.py
#
# Automated tests for the Week 1 impedance-matching code. These follow the
# same style as the existing tests in the repo (e.g. test_shock.py): import
# the function, build simple inputs, and compare against a value we computed
# by hand using pytest.approx for floating-point safety.

import pytest

from alpss.analysis.impedance import Material, particle_velocity, check_case1


def test_symmetric_impact_is_half_velocity():
    """Same material on both sides -> u_p = v_flyer / 2 (the classic result)."""
    cu = Material(name="Copper", density=8960.0, wave_speed=3940.0)
    up = particle_velocity(1000.0, cu, cu)
    assert up == pytest.approx(500.0, rel=1e-12)


def test_mismatched_impact_matches_hand_calc():
    """Copper flyer onto aluminum target, checked against a hand calculation."""
    cu = Material(name="Copper", density=8960.0, wave_speed=3940.0)
    al = Material(name="Aluminum", density=2700.0, wave_speed=5350.0)

    z_cu = 8960.0 * 3940.0
    z_al = 2700.0 * 5350.0
    expected = (z_cu / (z_cu + z_al)) * 1000.0

    assert particle_velocity(1000.0, cu, al) == pytest.approx(expected, rel=1e-12)


def test_soft_flyer_into_hard_target_gives_less_than_half():
    """If the target is 'harder' (higher impedance), u_p < v_flyer / 2."""
    al = Material(name="Aluminum", density=2700.0, wave_speed=5350.0)
    cu = Material(name="Copper", density=8960.0, wave_speed=3940.0)
    up = particle_velocity(1000.0, al, cu)  # soft flyer, hard target
    assert up < 500.0


def test_zero_velocity_gives_zero():
    cu = Material(name="Copper", density=8960.0, wave_speed=3940.0)
    assert particle_velocity(0.0, cu, cu) == 0.0


def test_zero_total_impedance_raises():
    dead = Material(name="Nothing", density=0.0, wave_speed=0.0)
    with pytest.raises(ValueError):
        particle_velocity(1000.0, dead, dead)


def test_check_case1():
    cu = Material(name="Copper", density=8960.0, wave_speed=3940.0)
    al = Material(name="Aluminum", density=2700.0, wave_speed=5350.0)
    assert check_case1(cu, al) is True   # copper is harder than aluminum
    assert check_case1(al, cu) is False
