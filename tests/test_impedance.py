
import numpy as np
import pytest
 
from alpss.analysis.impedance import Material, particle_velocity, check_case1
 
 
# --- Reference materials (rho0 [kg/m^3], C0 [m/s], S [-]) -------------------
# Standard linear-Hugoniot values; good enough to exercise the algebra.
CU = Material(8930.0, 3940.0, 1.489, name="OFHC Cu")
AL = Material(2785.0, 5328.0, 1.338, name="Al 6061")
TA = Material(16690.0, 3414.0, 1.201, name="Tantalum")
PMMA = Material(1186.0, 2598.0, 1.516, name="PMMA")
LIF = Material(2638.0, 5150.0, 1.350, name="LiF")
 
 
def _P_target(mat, u):
    """Forward-shock Hugoniot: material initially at rest."""
    return mat.density * (mat.C0 + mat.S * u) * u
 
 
def _P_flyer(mat, u, V):
    """Reflected Hugoniot: flyer initially moving at V."""
    return mat.density * (mat.C0 + mat.S * (V - u)) * (V - u)
 
 
# --------------------------------------------------------------------------
# Material container
# --------------------------------------------------------------------------
class TestMaterial:
    def test_shock_impedance(self):
        assert CU.shock_impedance == pytest.approx(8930.0 * 3940.0)
 
    def test_shock_velocity(self):
        assert CU.shock_velocity(500.0) == pytest.approx(3940.0 + 1.489 * 500.0)
 
    @pytest.mark.parametrize("bad", [dict(density=0.0), dict(C0=-1.0)])
    def test_invalid_properties_raise(self, bad):
        kwargs = dict(density=8930.0, C0=3940.0, S=1.489)
        kwargs.update(bad)
        with pytest.raises(ValueError):
            Material(**kwargs)
 
    def test_from_config(self):
        cfg = {"density": 1730.0, "C0": 4540.0, "S": 1.5}
        m = Material.from_config(cfg)
        assert (m.density, m.C0, m.S) == (1730.0, 4540.0, 1.5)
 
 
# --------------------------------------------------------------------------
# check_case1
# --------------------------------------------------------------------------
class TestCheckCase1:
    def test_none_target_is_symmetric(self):
        assert check_case1(CU) is True
 
    def test_same_material_is_symmetric(self):
        assert check_case1(CU, CU) is True
 
    def test_different_material_is_not(self):
        assert check_case1(CU, PMMA) is False
 
 
# --------------------------------------------------------------------------
# particle_velocity -- symmetric case
# --------------------------------------------------------------------------
class TestSymmetric:
    @pytest.mark.parametrize("V", [10.0, 100.0, 1000.0, 3000.0])
    def test_half_velocity_rule(self, V):
        # target=None and explicit same-material must both give exactly V/2.
        assert particle_velocity(V, CU) == pytest.approx(V / 2.0)
        assert particle_velocity(V, CU, CU) == pytest.approx(V / 2.0)
 
 
# --------------------------------------------------------------------------
# particle_velocity -- asymmetric case
# --------------------------------------------------------------------------
class TestAsymmetric:
    PAIRS = [(CU, PMMA), (PMMA, CU), (AL, TA), (TA, AL), (CU, LIF)]
 
    @pytest.mark.parametrize("flyer,target", PAIRS)
    def test_pressure_continuity(self, flyer, target):
        """The returned u_p must equate the flyer and target Hugoniot stresses."""
        V = 1500.0
        up = particle_velocity(V, flyer, target)
        assert _P_flyer(flyer, up, V) == pytest.approx(_P_target(target, up), rel=1e-7)
 
    @pytest.mark.parametrize("flyer,target", PAIRS)
    def test_root_in_physical_range(self, flyer, target):
        V = 1500.0
        up = particle_velocity(V, flyer, target)
        assert 0.0 < up < V
 
    def test_stiff_flyer_soft_target_above_half(self):
        assert particle_velocity(1000.0, CU, PMMA) > 500.0
 
    def test_soft_flyer_stiff_target_below_half(self):
        assert particle_velocity(1000.0, PMMA, CU) < 500.0
 
    def test_matches_manual_quadratic(self):
        V, f, t = 2000.0, AL, TA
        a = t.density * t.S - f.density * f.S
        b = t.density * t.C0 + f.density * f.C0 + 2 * f.density * f.S * V
        c = -f.density * V * (f.C0 + f.S * V)
        root = (-b + np.sqrt(b * b - 4 * a * c)) / (2 * a)
        assert particle_velocity(V, f, t) == pytest.approx(root)
 
 
# --------------------------------------------------------------------------
# pressure output + vectorization + edge cases
# --------------------------------------------------------------------------
class TestPressureAndVectorization:
    def test_return_pressure_positive_and_consistent(self):
        up, P = particle_velocity(1000.0, CU, PMMA, return_pressure=True)
        assert P > 0
        assert P == pytest.approx(_P_target(PMMA, up))
 
    def test_vectorized_matches_scalar_loop(self):
        Vs = np.linspace(0.0, 3000.0, 11)
        ups = particle_velocity(Vs, CU, PMMA)
        assert ups.shape == Vs.shape
        loop = np.array([particle_velocity(v, CU, PMMA) for v in Vs])
        assert np.allclose(ups, loop)
 
    def test_vectorized_is_monotonic(self):
        Vs = np.linspace(0.0, 3000.0, 50)
        ups = particle_velocity(Vs, CU, PMMA)
        assert np.all(np.diff(ups) > 0)
 
    def test_zero_velocity(self):
        assert particle_velocity(0.0, CU, PMMA) == 0.0
 
    def test_negative_velocity_raises(self):
        with pytest.raises(ValueError):
            particle_velocity(-1.0, CU, PMMA)
