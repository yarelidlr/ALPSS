
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Material:
    """Linear-Hugoniot material description (Us = C0 + s*up), SI units."""
    name: str
    rho0: float   # initial density   [kg/m^3]
    C0: float     # Hugoniot intercept [m/s]
    s: float      # Hugoniot slope     [-]

    def impedance(self, up: float = 0.0) -> float:
        """Shock impedance Z = rho0 * Us(up) = rho0 * (C0 + s*up)  [kg/m^2/s]."""
        return self.rho0 * (self.C0 + self.s * up)


def particle_velocity(flyer_velocity, material_I: Material, material_II: Material):

    u_g = np.asarray(flyer_velocity, dtype=float)

    rI, CI, bI = material_I.rho0, material_I.C0, material_I.s
    rII, CII, bII = material_II.rho0, material_II.C0, material_II.s

    # Quadratic in u:  (rII*bII - rI*bI) u^2 + (...) u - (...) = 0  ->  u^2 + B u - C = 0
    denom = rII * bII - rI * bI
    num_B = rII * CII + rI * CI + 4.0 * rI * bI * u_g          # -> B numerator
    num_C = 2.0 * rI * (CI * u_g + 2.0 * bI * u_g**2)          # -> C numerator

    if np.isclose(denom, 0.0):
        # Matched Hugoniot slopes: u^2 term vanishes, equation is linear.
        u_p = num_C / num_B
    else:
        B = num_B / denom
        C = num_C / denom
        u_p = -B / 2.0 + np.sqrt((B / 2.0) ** 2 + C)

    return float(u_p) if u_p.ndim == 0 else u_p


def check_case1(material_I: Material, material_II: Material, up: float = 0.0) -> bool:
    """True if material_II is higher impedance (the rho_I*Us_I < rho_II*Us_II
    condition under which Eq. 3.11 / Case 1 is valid)."""
    return material_I.impedance(up) < material_II.impedance(up)


# Internal helpers used only by the tests to verify pressure continuity.
def _P_forward(mat: Material, up):
    return mat.rho0 * mat.C0 * up + mat.rho0 * mat.s * up**2


def _P_backward(mat: Material, up, u_g):
    r = 2.0 * u_g - up
    return mat.rho0 * mat.C0 * r + mat.rho0 * mat.s * r**2
