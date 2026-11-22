# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
# SPDX-License-Identifier: AGPL-3.0-only
"""Bee geometry tunneling: quantum tunneling (Josephson-style) through a
hexagonal honeycomb geometry -- the bee's geometry.

The honeycomb is the geometry the tunneling happens through. The model
reuses josephson-membrane v0.3.0's measured per-link law (each barrier
link contributes one factor (1 - h)) and the honeycomb geometry from
symmetry-entropy (6 neighbours, 120-degree angles, bipartite vertex
lattice, Hales efficiency), and extends them: a 60-degree turn costs a
factor, the critical current scales with the number of parallel
hexagon-edge paths, and the axis of the honeycomb changes the
transmission. Synthetic and classical throughout; no real quantum
measurement is claimed.
"""

from __future__ import annotations

from . import honeycomb, paths, tunneling
from .lab import evaluate_all, report
from .tunneling import josephson_current, transmission

__all__ = [
    "evaluate_all",
    "honeycomb",
    "josephson_current",
    "paths",
    "report",
    "transmission",
    "tunneling",
]
