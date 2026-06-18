# Impedance Matching

```{note}
**Status (Week 1).** This page documents the first piece of the impedance-matching
work: converting a measured/known **flyer velocity** into the **interface particle
velocity** `u_p`. Later weeks add a material database, free-surface/window
calibration curves, and wiring into the shock-stress phase.
```

## Why this exists

In a laser-driven flyer experiment a thin flyer plate is launched at velocity
$V$ and strikes a sample. The quantity we ultimately want — stress in the
sample — depends on the **particle velocity** $u_p$ generated *at the
flyer/sample interface*. When the flyer and sample are the **same** material the
answer is trivially $u_p = V/2$. When they are **different** materials
(*mismatched impedance*) the split is no longer 50/50, and we have to solve an
impedance-matching problem. This module does exactly that.

## The physics in one paragraph

When the flyer hits the sample, a shock runs **forward** into the sample
(accelerating it from rest up to $u_p$) and a shock runs **backward** into the
flyer (decelerating it from $V$ down to $u_p$). Two things must be continuous at
the interface: the **particle velocity** and the **stress (pressure)**. Each
material's stress–particle-velocity behaviour is given by its **Hugoniot**.
Matching the two Hugoniots at a common $(u_p, P)$ point gives the interface
state.

### Building blocks

**Rankine–Hugoniot momentum jump** (material initially at rest, ambient pressure
taken as zero):

```{math}
P = \rho_0\, U_s\, u_p
```

**Linear shock Hugoniot** (the standard empirical fit):

```{math}
U_s = C_0 + S\,u_p
```

so a material at rest follows

```{math}
P_\text{target}(u) = \rho_0\,(C_0 + S\,u)\,u .
```

The flyer is *moving* at $V$, so its Hugoniot is reflected about $V$:

```{math}
P_\text{flyer}(u) = \rho_{0,f}\,\big(C_{0,f} + S_f\,(V-u)\big)\,(V-u).
```

### Matching the two

Setting $P_\text{target}(u_p) = P_\text{flyer}(u_p)$ and collecting powers of
$u_p$ gives a quadratic:

```{math}
:label: impedance-quadratic
a\,u_p^2 + b\,u_p + c = 0
```

with

```{math}
\begin{aligned}
a &= \rho_{0,t} S_t - \rho_{0,f} S_f \\
b &= \rho_{0,t} C_{0,t} + \rho_{0,f} C_{0,f} + 2\,\rho_{0,f} S_f V \\
c &= -\rho_{0,f}\, V\,(C_{0,f} + S_f V).
\end{aligned}
```

The physical solution is the root with $0 \le u_p \le V$. For a **symmetric
impact** ($\rho_{0,f}=\rho_{0,t}$, $C_{0,f}=C_{0,t}$, $S_f=S_t$) the leading
coefficient $a \to 0$, the quadratic degenerates to a linear equation, and it
collapses to the familiar

```{math}
u_p = \tfrac{1}{2}V .
```

```{admonition} Reference caveat
:class: warning
The project task pointed to "Eq. 3.11, p. 46" of a textbook that was **not**
bundled with the source files. The equations above were re-derived from the
Rankine–Hugoniot jump conditions and the linear Hugoniot — the standard
impedance-matching result. Before merging, please confirm the sign/notation
conventions and the exact "Case 1" definition against that page. The code is
written so the numbers are easy to check (symmetric impact must return exactly
$V/2$, and the returned root must equate both Hugoniot stresses).
```

## Usage

```python
from alpss.analysis.impedance import Material, particle_velocity

# rho0 [kg/m^3], C0 [m/s], S [-]
copper = Material(density=8930.0, C0=3940.0, S=1.489, name="OFHC Cu")
pmma   = Material(density=1186.0, C0=2598.0, S=1.516, name="PMMA")

# Symmetric impact (target defaults to the flyer material) -> V/2
particle_velocity(1000.0, copper)            # -> 500.0

# Mismatched impedance: copper flyer into a PMMA sample
particle_velocity(1000.0, copper, pmma)      # -> ~886.95 m/s

# Also return the interface stress (Pa)
u_p, P = particle_velocity(1000.0, copper, pmma, return_pressure=True)

# Vectorised over flyer velocity (handy for calibration curves)
import numpy as np
V = np.linspace(0, 3000, 100)
u_p_curve = particle_velocity(V, copper, pmma)
```

## API

```{eval-rst}
.. autofunction:: alpss.analysis.impedance.particle_velocity

.. autoclass:: alpss.analysis.impedance.Material
   :members:

.. autofunction:: alpss.analysis.impedance.check_case1
```

## Tests

The unit tests live in `tests/test_impedance.py` and cover: the symmetric
$V/2$ identity, stress continuity for several mismatched pairs, the stiff↔soft
asymmetry, vectorised/scalar agreement, and input validation. Run them with:

```bash
poetry run pytest tests/test_impedance.py -v
```
