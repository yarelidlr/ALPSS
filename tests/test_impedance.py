"""
test_impedance.py  --  unit tests for alpss.analysis.impedance

"""
import numpy as np
import pytest


#   from alpss.analysis.impedance import Material, particle_velocity, check_case1, _P_forward, _P_backward
from impedance import Material, particle_velocity, check_case1, _P_forward, _P_backward

# SI Hugoniot params (rho0 kg/m^3, C0 m/s, s) -- replace with project-fitted values.
AL = Material("Al6061", 2700.0, 5350.0, 1.34)
CU = Material("Cu",     8930.0, 3940.0, 1.489)


def test_case1_direction():
    """Shock into a higher-impedance target slows the interface: u_p < u_g."""
    u_g = 1000.0  # m/s
    u_p = particle_velocity(u_g, AL, CU)
    assert 0.0 < u_p < u_g
    assert u_p == pytest.approx(618.7, abs=2.0)


def test_pressure_continuity():
    """Transmitted pressure must match on both Hugoniots at the solution."""
    u_g = 1000.0
    u_p = particle_velocity(u_g, AL, CU)
    assert _P_forward(CU, u_p) == pytest.approx(_P_backward(AL, u_p, u_g), rel=1e-9)


def test_near_symmetric_limit():
    """Identical materials -> shock crosses unchanged -> u_p -> u_g."""
    cu_star = Material("Cu*", CU.rho0, CU.C0, CU.s * (1 + 1e-9))
    assert particle_velocity(1000.0, CU, cu_star) == pytest.approx(1000.0, abs=1.0)


def test_vectorized():
    """Accepts an array (an ALPSS velocity trace) and preserves shape."""
    trace = np.linspace(200.0, 2000.0, 7)
    out = particle_velocity(trace, AL, CU)
    assert out.shape == trace.shape
    assert np.all(out < trace)


def test_case_classifier():
    assert check_case1(AL, CU) is True      # Cu is stiffer
    assert check_case1(CU, AL) is False
