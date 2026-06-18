
import math
 
 
class Material:
    """Holds the three shock properties of one material.
 
    density : starting density, in kg/m^3
    C0      : bulk sound speed, in m/s
    S       : Hugoniot slope (just a plain number, no units)
    name    : an optional label like "Copper", only used for printing
    """
 
    def __init__(self, density, C0, S, name=""):
        if density <= 0:
            raise ValueError("density must be a positive number")
        if C0 <= 0:
            raise ValueError("C0 must be a positive number")
        self.density = density
        self.C0 = C0
        self.S = S
        self.name = name
 
 
def check_case1(flyer, target):
    """Return True if the flyer and the sample are the same material.
 
    "Case 1" is the simple case: same material on both sides, so the flyer
    velocity splits exactly in half (u_p = V / 2) and we don't need the
    quadratic formula.
 
    If target is None treat it as "same material as the flyer", which is
    also Case 1.
    """
    if target is None:
        return True
 
    # two numbers are "the same" if their difference is tiny
    tiny = 0.000001  # 1e-6
    same_density = abs(flyer.density - target.density) < tiny
    same_C0 = abs(flyer.C0 - target.C0) < tiny
    same_S = abs(flyer.S - target.S) < tiny
 
    return same_density and same_C0 and same_S
 
 
def particle_velocity(flyer_velocity, flyer, target=None):
    """Return the particle velocity u_p at the flyer/sample interface.
 
    Inputs
    ------
    flyer_velocity : the impact speed V of the flyer, in m/s (a single number,
                     must be 0 or positive)
    flyer          : a Material describing the flyer
    target         : a Material describing the sample. If you leave this out
                     (or pass None), the sample is assumed to be the SAME
                     material as the flyer.
 
    Output
    ------
    u_p : the particle velocity in m/s (a single number).
 
    Example
    -------
    >>> copper = Material(8930, 3940, 1.489, name="Copper")
    >>> particle_velocity(1000, copper)          # same material -> half
    500.0
    """
    V = flyer_velocity
 
    if V < 0:
        raise ValueError("flyer_velocity must be 0 or positive")
 
    # ---- Case 1: same material on both sides -> exactly half ----
    if check_case1(flyer, target):
        return V / 2
 
    # ---- Different materials: solve a*u_p^2 + b*u_p + c = 0 ----
    # These three lines ARE the impedance-matching equation. They come from
    # setting the flyer's pressure equal to the sample's pressure at the
    # interface and gathering the u_p terms together.
    a = target.density * target.S - flyer.density * flyer.S
    b = (target.density * target.C0
         + flyer.density * flyer.C0
         + 2 * flyer.density * flyer.S * V)
    c = -flyer.density * V * (flyer.C0 + flyer.S * V)
 
    # If a is essentially zero, the u_p^2 term disappears and the equation is
    # just a straight line:  b*u_p + c = 0  ->  u_p = -c / b
    if abs(a) < 1e-12:
        return -c / b
 
    # Otherwise use the quadratic formula. A quadratic has two answers
    # (root1 and root2), and keep the one that makes sense
    discriminant = b * b - 4 * a * c
    root1 = (-b + math.sqrt(discriminant)) / (2 * a)
    root2 = (-b - math.sqrt(discriminant)) / (2 * a)
 
    # The particle velocity must be between 0 and the impact speed V. Pick the
    # root that lands in that range.
    if 0 <= root1 <= V:
        return root1
    else:
        return root2
