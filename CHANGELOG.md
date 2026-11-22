# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
# SPDX-License-Identifier: AGPL-3.0-only
# Changelog

## 0.1.0 (2026-11-21)

First release. Quantum tunneling (Josephson-style) through a hexagonal
honeycomb geometry -- the bee's geometry.

- Honeycomb lattice (axial coordinates): 6 neighbours per cell at
  60-degree steps, distance sqrt(3); interior angle 120 degrees;
  bipartite vertex lattice (7-cell patch: 24 vertices, 30 edges,
  12/12); Hales least-perimeter order.
- Tunneling model reusing josephson-membrane v0.3.0's measured per-link
  law (each barrier link contributes one factor (1 - h)) and extended
  with the hexagonal geometry: a 60-degree turn costs a factor 0.8,
  and the critical current scales with the number of parallel
  hexagon-edge paths.
- Measured claims (bars frozen before evaluation, frozen seeds
  {42, 7, 1234, 2026, 2718}): 6/7 pass, 30/30 tests pass.
  - (i) geometry PASS (all 8 checks exact).
  - (ii) turn-cost PASS: slope -0.2231, expected log(0.8) = -0.2231,
    R^2 = 1.0000.
  - (iii) axis-vs-off-axis PASS: ratio 3.05 (bar >= 2).
  - (iv) current-phase PASS: max sine error 0.00e+00, I_c slope 1.0000.
  - (v) height PASS: T(0.99)/T(0) = 1.01e-04.
  - (vi) width-exponential PASS: slope -1.4030 per edge, R^2 = 0.999989.
  - (vii) current-density FAIL (honest): honeycomb/square per unit
    width = 0.5774 (bar >= 1). The bee's wax efficiency does not buy
    current density.
