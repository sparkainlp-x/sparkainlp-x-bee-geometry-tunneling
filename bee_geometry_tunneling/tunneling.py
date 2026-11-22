# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
# SPDX-License-Identifier: AGPL-3.0-only
"""Tunneling through the honeycomb: the transmission model and the
Josephson current-phase relation across a honeycomb junction.

Reused, not reinvented (from josephson-membrane v0.3.0, claims (h)-(k)):
the per-link rule. Each barrier link contributes one factor (1 - h),
so a barrier of w links transmits T = T(0) * (1 - h)^w to within 12%
-- the measured law there, taken here as the designed rule. The
transmission falls strictly with barrier height, exponentially with
barrier width (log-linear slope -1.353 per link, R^2 = 0.999996
there), graded not a step. The Josephson laws are inputs, not
discoveries: I_s = I_c sin(dphi) (Brian Josephson is the source of
the law), f = 2eV/h, and the SQUID modulation I_c(Phi) =
2 I_c |cos(pi Phi / Phi_0)|.

Extended here, into the hexagonal geometry:
  - a TURN costs a factor TAU_TURN per 60-degree direction change
    (through the hexagon's 120-degree corner). A path with m turns
    transmits tau^m times the straight path, at the same barrier.
  - a small per-link disorder: each barrier link's coupling is
    (1 - h) * (1 + eps), eps ~ N(0, DISORDER_SIGMA), drawn per seed.
    The claims use the mean over the frozen seeds; the disorder is
    what the seeds average over.
  - the critical current of a honeycomb junction scales with the
    number N of parallel hexagon-edge paths across it: I_c = N * I_C_PER_PATH,
    one path per cell of the junction's cross-section. Per unit
    junction width the honeycomb carries fewer paths than a square
    lattice (neighbour spacing sqrt(3) vs 1) -- see lab claim (vii).

Transmission of a path (a probability, 0 <= T <= 1):
    T = tau^m * (1 - h)^w * prod(1 + eps_i),
clamped to [0, 1], where w is the number of barrier links, m the
turn count, and eps_i the disorder on barrier link i. At h = 0 the
barrier is a no-op (T = tau^m); at h = 1 the chain is cut (T = 0).

Synthetic and classical throughout. No real quantum measurement is
claimed, and no physical junction is implied.
"""

from __future__ import annotations

import numpy as np

from .paths import barrier_links, turn_count

# --- Designed constants (fixed before measuring) ---
TAU_TURN = 0.8          # transmission factor per 60-degree turn
DISORDER_SIGMA = 0.05   # per-link coupling disorder (sd)
I_C_PER_PATH = 1.0      # unit critical current per parallel path
NEIGHBOUR_SPACING = float(np.sqrt(3.0))  # honeycomb neighbour distance
SQUARE_SPACING = 1.0    # square-lattice path spacing (comparison)


def transmission(path: list[tuple[int, int]], height: float,
                 width: int, rng: np.random.Generator | None = None) -> float:
    """Tunneling probability of a path through a barrier of `width` links
    at height `height`. See module docstring for the rule."""
    if not 0.0 <= height <= 1.0:
        raise ValueError("height must be in [0, 1]")
    rng = rng or np.random.default_rng()
    links = barrier_links(path, width)
    m = turn_count(path)
    t = float(TAU_TURN) ** m
    for _ in links:
        eps = float(rng.normal(0.0, DISORDER_SIGMA))
        t *= (1.0 - height) * (1.0 + eps)
    return float(min(max(t, 0.0), 1.0))


def josephson_current(dphi: float, critical_current: float) -> float:
    """The Josephson DC law: I_s = I_c sin(dphi). Brian Josephson is the
    source of the law; the law is an input here, not a discovery."""
    return float(critical_current * np.sin(dphi))


def junction_critical_current(n_paths: int) -> float:
    """I_c of a honeycomb junction with n_paths parallel hexagon-edge
    paths across it: one unit of critical current per path."""
    if n_paths < 0:
        raise ValueError("n_paths must be >= 0")
    return float(n_paths * I_C_PER_PATH)


def paths_per_unit_width(spacing: float) -> float:
    """Parallel paths per unit junction width for a lattice whose paths
    are spaced `spacing` apart."""
    return 1.0 / float(spacing)


def current_density_ratio() -> float:
    """Honeycomb vs square critical current per unit junction width:
    (1/sqrt(3)) / (1/1) = 1/sqrt(3). Below 1: the honeycomb carries
    less current per unit width, because its cells are wider apart."""
    return paths_per_unit_width(NEIGHBOUR_SPACING) / paths_per_unit_width(SQUARE_SPACING)
