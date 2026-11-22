# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
# SPDX-License-Identifier: AGPL-3.0-only
# Bee Geometry Tunneling

**SYNTHETIC classical emulation only. No claim about physical reality.
No headline claim is emitted.**

Quantum tunneling (Josephson-style) through a hexagonal honeycomb
geometry — the bee's geometry. The honeycomb is the geometry the
tunneling happens through: the wave hops from cell to cell across
shared hexagon edges, and the route it takes — straight along a
symmetry axis or zigzagging off-axis — changes what gets through.

## What it builds on

- **josephson-membrane v0.3.0** (claims (h)–(k)): the measured per-link
  law. Each barrier link contributes one factor (1 − h), so a barrier
  of w links transmits T = T(0)·(1 − h)^w; the transmission falls
  strictly with barrier height (T(0.99)/T(0) = 1.12e-04 at width 2)
  and exponentially with barrier width (log-linear slope −1.353 per
  link, R² = 0.999996), graded not a step. That law is reused here as
  the designed rule, not re-measured from scratch. The Josephson laws
  are inputs, not discoveries: I_s = I_c sin(Δφ) (Brian Josephson is
  the source of the law), f = 2eV/h. Note josephson-membrane claim (d):
  the membrane's own phase response does NOT follow the sine law —
  it is even in Δφ and its best fit is a cosine (R² = −32.75). Nothing
  here re-litigates that FAIL; the sine law is used as the designed
  junction rule, and the membrane's failure stands.
- **symmetry-entropy** (honeycomb): the hexagonal lattice — 6
  neighbours per cell at 60-degree steps, distance √3 for circumradius
  1, interior angle 120 degrees, the vertex lattice bipartite
  (7-cell patch: 24 vertices, 30 edges, 12/12), and Hales' result
  that the hexagon has the least perimeter for unit area (3.7224 <
  4.0000 square < 4.5590 triangle). The bee minimises wax.

## The model

A path is a sequence of honeycomb cells, each step crossing one shared
hexagon edge. The barrier is a block of w consecutive links of the
path, centred. The transmission of a path is a probability:

    T = τ^m · (1 − h)^w · Π(1 + ε_i)

where m is the number of 60-degree turns (each costs a factor τ = 0.8,
through the hexagon's 120-degree corner), w is the number of barrier
links, h is the barrier height, and ε_i ~ N(0, 0.05) is a small
per-link disorder, drawn per frozen seed. At h = 0 the barrier is a
no-op; at h = 1 the chain is cut (T = 0).

A honeycomb junction is a band of cells; its critical current scales
with the number N of parallel hexagon-edge paths across it:
I_c = N · i_c, one unit per path. Per unit junction width the
honeycomb carries 1/√3 paths (neighbour spacing √3) against 1 for a
square lattice (spacing 1).

## Measured claims (v0.1.0)

Bars frozen before evaluation. Frozen seeds {42, 7, 1234, 2026, 2718}.
30/30 tests pass. **6/7 claims pass.**

| Claim | Result |
|---|---|
| (i) Geometry: 6 neighbours, 60° steps, distance √3, 120°, vertex patch bipartite 24v/30e 12/12, Hales order | **PASS** — all 8 checks exact |
| (ii) Turn cost: log T linear in turns, slope = log(0.8) | **PASS** — slope −0.2231, expected −0.2231, R² = 1.0000 |
| (iii) Axis vs off-axis: straight transmits ≥ 2× zigzag through the same barrier | **PASS** — T_on = 0.0151 (0 turns), T_off = 0.0049 (5 turns), ratio 3.05 |
| (iv) Current-phase: I = I_c sin(Δφ) exact; I_c linear in parallel paths | **PASS** — max sine error 0.00e+00, I_c slope 1.0000, R² = 1.000000 |
| (v) Height: T strictly decreasing; T(0.99)/T(0) ≤ 0.20 at width 2 | **PASS** — T(0.99)/T(0) = 1.01e-04 |
| (vi) Width exponential: log T linear in barrier edges | **PASS** — slope −1.4030 per edge, R² = 0.999989 |
| (vii) Current density: honeycomb ≥ square per unit width | **FAIL** — ratio 0.5774 (bar ≥ 1.0); honeycomb 0.5774 vs square 1.0000 paths per unit width |

## The FAIL in one paragraph

The honeycomb's Hales efficiency — least perimeter per unit area, the
bee minimising wax — does not buy current density. A honeycomb
junction's parallel paths are spaced √3 apart (the neighbour
distance), a square junction's 1 apart, so per unit junction width
the honeycomb carries 1/√3 = 0.577 as many paths, and hence 0.577
the critical current. The claim that the honeycomb carries at least
as much current per unit width as a square junction FAILS at 0.5774.
The geometry's advantage in one domain (wax) is a disadvantage in
another (current density). Per unit area it is worse still (0.385).
The bar was not moved and the rule was not tuned; the FAIL is the
measurement.

## Reading

**The hexagonal geometry steers tunneling by turning, not by
blocking.** A straight path along a honeycomb symmetry axis transmits
3.05× a zigzag path through the same barrier — same links, same
height, only the turns differ — and each 60-degree turn costs exactly
a factor 0.8 in log-transmission. The barrier itself behaves as in
josephson-membrane (exponential in edges, graded in height). But the
bee's efficiency does not extend to current: per unit width the
honeycomb junction carries less, not more, than a square one.

## Run it

```bash
make test    # 30 tests
make run     # full claim table
```

Requires Python ≥ 3.10 and NumPy. No other dependencies, no network.

## Files

- `bee_geometry_tunneling/honeycomb.py` — the hexagonal lattice (cells,
  neighbours, vertex patch, Hales perimeters).
- `bee_geometry_tunneling/paths.py` — straight, zigzag, and
  fixed-turn-count paths; barrier links.
- `bee_geometry_tunneling/tunneling.py` — the transmission model, the
  Josephson current-phase relation, junction critical current.
- `bee_geometry_tunneling/lab.py` — the measured claims (i)–(vii).

## Honest limits

Synthetic and classical throughout. The per-link law is a designed
rule taken from josephson-membrane's measurement, not a new law; the
turn factor τ = 0.8 is a designed parameter, not a measured physical
constant; the disorder is a 5% per-link jitter averaged over 5 seeds.
No physical junction is implied, no real quantum measurement is
claimed, and no partner, funding, or endorsement exists. Brisson sole
author; Brian Josephson is cited only as the source of the Josephson
law.
