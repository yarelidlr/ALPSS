
from __future__ import annotations
 
from dataclasses import dataclass
import logging
 
import numpy as np
 
logger = logging.getLogger("alpss")
 
__all__ = ["Material", "particle_velocity", "check_case1"]
 
 
@dataclass(frozen=True)
class Material:

 
    density: float
    C0: float
    S: float
    name: str = ""
    C_L: float | None = None
 
    def __post_init__(self) -> None:
        if self.density <= 0:
            raise ValueError(f"density must be > 0, got {self.density}")
        if self.C0 <= 0:
            raise ValueError(f"C0 must be > 0, got {self.C0}")
        if self.S < 0:
            # Physically S is almost always >= 0; warn rather than hard-fail.
            logger.warning("Material %r has negative Hugoniot slope S=%s",
                           self.name or "<unnamed>", self.S)
 
    @property
    def shock_impedance(self) -> float:
        """Acoustic (weak-shock) impedance ``Z0 = rho0 * C0`` [kg m^-2 s^-1]."""
        return self.density * self.C0
 
    def shock_velocity(self, u_p):
        """Shock velocity ``U_s = C0 + S*u_p`` for particle velocity ``u_p``."""
        return self.C0 + self.S * np.asarray(u_p, dtype=float)
 
    def impedance_at(self, u_p):
        """Finite-amplitude impedance ``rho0 * U_s(u_p)`` at particle velocity ``u_p``."""
        return self.density * self.shock_velocity(u_p)
 
    @classmethod
    def from_config(cls, inputs: dict, *, prefix: str = "") -> "Material":
  
        return cls(
            density=float(inputs[f"{prefix}density"]),
            C0=float(inputs[f"{prefix}C0"]),
            S=float(inputs.get(f"{prefix}S", 0.0)),
            name=str(inputs.get(f"{prefix}material_name", "")),
            C_L=inputs.get(f"{prefix}C_L"),
        )
 
 
def check_case1(flyer: Material, target: Material | None = None,
                *, rtol: float = 1e-9) -> bool:
 
    if target is None:
        return True
    return bool(
        np.isclose(flyer.density, target.density, rtol=rtol)
        and np.isclose(flyer.C0, target.C0, rtol=rtol)
        and np.isclose(flyer.S, target.S, rtol=rtol)
    )
 
 
def _select_physical_root(a, b, c, V):

    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    c = np.asarray(c, dtype=float)
    V = np.asarray(V, dtype=float)
 
    # --- linear branch (a ~ 0): symmetric / matched impedance ---------------
    # Use a relative threshold so units don't matter.
    scale = np.maximum(np.abs(b), 1.0)
    linear = np.abs(a) <= 1e-12 * scale
 
    with np.errstate(divide="ignore", invalid="ignore"):
        u_linear = np.where(b != 0.0, -c / b, 0.0)
 
        # --- quadratic branch ---------------------------------------------
        disc = b * b - 4.0 * a * c
        disc = np.where(disc < 0.0, np.nan, disc)
        sqrt_disc = np.sqrt(disc)
        a_safe = np.where(linear, np.nan, a)  # avoid 0-division warnings
        root_plus = (-b + sqrt_disc) / (2.0 * a_safe)
        root_minus = (-b - sqrt_disc) / (2.0 * a_safe)
 
    # Tolerance band for "inside [0, V]".
    tol = 1e-9 * np.maximum(np.abs(V), 1.0)
 
    def _in_range(r):
        return (r >= -tol) & (r <= V + tol)
 
    plus_ok = _in_range(root_plus)
    # Prefer root_plus when valid, else root_minus, else NaN.
    u_quad = np.where(plus_ok, root_plus, root_minus)
    quad_valid = plus_ok | _in_range(root_minus)
    u_quad = np.where(quad_valid, u_quad, np.nan)
 
    u_p = np.where(linear, u_linear, u_quad)
 
    # Clip tiny numerical excursions back into the physical band.
    u_p = np.clip(u_p, 0.0, V)
    return u_p
 
 
def particle_velocity(flyer_velocity, flyer: Material,
                      target: Material | None = None,
                      *, return_pressure: bool = False):

    V = np.asarray(flyer_velocity, dtype=float)
    scalar_input = V.ndim == 0
 
    if np.any(V < 0):
        raise ValueError("flyer_velocity must be >= 0 (impact speed).")
 
    # --- symmetric / Case-1 shortcut ---------------------------------------
    if check_case1(flyer, target):
        u_p = 0.5 * V
        mat = flyer
    else:
        a = target.density * target.S - flyer.density * flyer.S
        b = (target.density * target.C0
             + flyer.density * flyer.C0
             + 2.0 * flyer.density * flyer.S * V)
        c = -flyer.density * V * (flyer.C0 + flyer.S * V)
        u_p = _select_physical_root(a, b, c, V)
        mat = target
 
        if np.any(np.isnan(u_p)):
            raise ValueError(
                "No physical impedance-matching root in [0, V]; check the "
                "material properties and impact velocity."
            )
 
    if return_pressure:
        # Stress on the *target* (or flyer, in the symmetric case) Hugoniot.
        pressure = mat.density * mat.shock_velocity(u_p) * u_p
        if scalar_input:
            return float(u_p), float(pressure)
        return u_p, pressure
 
    return float(u_p) if scalar_input else u_p
 
