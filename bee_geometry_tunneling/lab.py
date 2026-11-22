# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
# SPDX-License-Identifier: AGPL-3.0-only
"""The laboratory: the pipeline and the measured claims.

Pipeline: honeycomb -> path -> barrier -> transmission -> measure.

The tunneling model reuses josephson-membrane v0.3.0's measured per-link
law (each barrier link contributes one factor (1 - h), so T = T(0) *
(1 - h)^w) and extends it with the hexagonal geometry: a 60-degree
turn costs a factor TAU_TURN, and the critical current of a honeycomb
junction scales with the number of parallel hexagon-edge paths.

Claims, bars frozen before evaluation (from the design, not fitted):

(i)   Geometry: each cell has 6 neighbours at 60-degree steps, distance
      sqrt(3); interior angle 120 degrees; the 7-cell vertex patch is
      bipartite (24 vertices, 30 edges, 12/12); Hales order holds
      (hexagon < square < triangle perimeter for unit area). Exact.
(ii)  Turn cost: at fixed barrier width and height, log transmission is
      linear in the number of 60-degree turns with slope = log(TAU_TURN)
      within 0.05, R^2 >= 0.90 (mean over seeds).
(iii) Axis vs off-axis: a straight (on-axis) path transmits at least 2x
      a zigzag (off-axis) path through the same barrier -- same number
      of barrier links, differing only in turns (mean over seeds).
(iv)  Current-phase: I(dphi) = I_c sin(dphi) exactly (max error < 1e-12),
      and I_c scales linearly with the number of parallel paths
      (slope = I_C_PER_PATH within 1e-9, R^2 >= 1 - 1e-12).
(v)   Height: at width 2, mean transmission strictly decreases with
      height over (0, 0.25, 0.5, 0.75, 0.9, 0.99), and
      T(0.99)/T(0) <= 0.20.
(vi)  Width exponential: at height 0.75, over widths 0..3, log(mean T)
      against width has slope < -0.10 per edge and R^2 >= 0.90.
(vii) Current density: the honeycomb junction carries at least as much
      critical current per unit width as a square junction (ratio >= 1).
      The design says otherwise (1/sqrt(3) = 0.577): the bee's wax
      efficiency does not buy current density. Recorded as measured.

A claim that fails is recorded as FAIL, honestly, with its measured
numbers. The test suite asserts the measurements are as computed and
the verdicts follow from them; it does not move a bar to force a pass.
"""

from __future__ import annotations

import numpy as np

from . import honeycomb as hc
from . import paths as pa
from . import tunneling as tn

FROZEN_SEEDS = (42, 7, 1234, 2026, 2718)
HEIGHTS = (0.0, 0.25, 0.5, 0.75, 0.9, 0.99)
WIDTHS = (0, 1, 2, 3)
HEIGHT_SWEEP_WIDTH = 2
WIDTH_SWEEP_HEIGHT = 0.75
AXIS_STEPS = 6
AXIS_HEIGHT = 0.5
TURN_STEPS = 6
TURN_HEIGHT = 0.5
BAR_TURN_SLOPE_TOL = 0.05
BAR_TURN_R2 = 0.90
BAR_AXIS_RATIO = 2.0
BAR_SINE_ERR = 1e-12
BAR_IC_SLOPE_TOL = 1e-9
BAR_IC_R2 = 1.0 - 1e-12
BAR_SUPPRESSION = 0.20
BAR_WIDTH_SLOPE = -0.10
BAR_WIDTH_R2 = 0.90
BAR_DENSITY_RATIO = 1.0


def _mean_transmission(path, height, width, seeds=FROZEN_SEEDS) -> float:
    """Mean transmission over the frozen seeds (one disorder draw per
    barrier link per seed)."""
    ts = [tn.transmission(path, height, width, rng=np.random.default_rng(s))
          for s in seeds]
    return float(np.mean(ts))


def _mean_log_transmission(path, height, width, seeds=FROZEN_SEEDS) -> float:
    ts = [tn.transmission(path, height, width, rng=np.random.default_rng(s))
          for s in seeds]
    return float(np.mean([np.log(max(t, 1e-300)) for t in ts]))


def _linfit(x, y):
    """Least-squares slope, intercept, R^2."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    a, b = np.polyfit(x, y, 1)
    pred = a * x + b
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return float(a), float(b), float(r2)


def claim_geometry() -> dict:
    """(i) The honeycomb geometry is exact."""
    nbs = hc.neighbours(0, 0)
    dists = [np.hypot(*(np.array(hc.cell_center(*c)) - np.array(hc.cell_center(0, 0))))
             for c in nbs]
    angles = sorted(hc.direction_angle(d) for d in hc.NEIGHBOUR_OFFSETS)
    expected_angles = [0.0, 60.0, 120.0, 180.0, 240.0, 300.0]
    patch = hc.vertex_patch()
    per = {s: hc.tile_perimeter(s) for s in ("hexagon", "square", "triangle")}
    checks = {
        "n_neighbours": len(nbs) == 6,
        "neighbour_distance_sqrt3": all(abs(d - np.sqrt(3)) < 1e-12 for d in dists),
        "angles_60_deg_steps": all(abs(a - e) < 1e-9
                                   for a, e in zip(angles, expected_angles)),
        "interior_angle_120": hc.INTERIOR_ANGLE_DEG == 120.0,
        "patch_bipartite": patch["bipartite"] is True,
        "patch_24_vertices_30_edges": (patch["n_vertices"], patch["n_edges"]) == (24, 30),
        "patch_12_12": (len(patch["A"]), len(patch["B"])) == (12, 12),
        "hales_order": per["hexagon"] < per["square"] < per["triangle"],
    }
    verdict = "PASS" if all(checks.values()) else "FAIL"
    return {"id": "(i)", "name": "geometry", "verdict": verdict,
            "checks": checks, "perimeters": per}


def claim_turn_cost(seeds=FROZEN_SEEDS) -> dict:
    """(ii) Log transmission is linear in the number of 60-degree turns,
    slope = log(TAU_TURN)."""
    turns = list(range(0, AXIS_STEPS))
    log_t = [_mean_log_transmission(pa.path_with_turns(TURN_STEPS, m),
                                    TURN_HEIGHT, TURN_STEPS, seeds)
             for m in turns]
    slope, _, r2 = _linfit(turns, log_t)
    expected = float(np.log(tn.TAU_TURN))
    verdict = ("PASS" if abs(slope - expected) <= BAR_TURN_SLOPE_TOL
               and r2 >= BAR_TURN_R2 else "FAIL")
    return {"id": "(ii)", "name": "turn-cost", "verdict": verdict,
            "slope": slope, "expected_slope": expected, "r2": r2,
            "log_t": log_t, "bar_slope_tol": BAR_TURN_SLOPE_TOL,
            "bar_r2": BAR_TURN_R2}


def claim_axis(seeds=FROZEN_SEEDS) -> dict:
    """(iii) Straight (on-axis) transmits >= 2x zigzag (off-axis) through
    the same barrier: same links, differing only in turns."""
    straight = pa.straight_path((1, 0), AXIS_STEPS)
    zigzag = pa.zigzag_path(AXIS_STEPS)
    t_on = _mean_transmission(straight, AXIS_HEIGHT, AXIS_STEPS, seeds)
    t_off = _mean_transmission(zigzag, AXIS_HEIGHT, AXIS_STEPS, seeds)
    ratio = t_on / t_off if t_off > 0 else float("inf")
    verdict = "PASS" if ratio >= BAR_AXIS_RATIO else "FAIL"
    return {"id": "(iii)", "name": "axis-vs-off-axis", "verdict": verdict,
            "t_on_axis": t_on, "t_off_axis": t_off, "ratio": ratio,
            "turns_on": pa.turn_count(straight),
            "turns_off": pa.turn_count(zigzag), "bar": BAR_AXIS_RATIO}


def claim_current_phase() -> dict:
    """(iv) The Josephson sine law across the honeycomb junction is exact,
    and I_c scales linearly with the number of parallel paths."""
    dphis = np.linspace(0.0, 2.0 * np.pi, 64, endpoint=False)
    ic = tn.junction_critical_current(3)
    errs = [abs(tn.josephson_current(p, ic) - ic * np.sin(p)) for p in dphis]
    max_err = float(max(errs))
    widths = list(range(1, 7))
    ics = [tn.junction_critical_current(w) for w in widths]
    slope, _, r2 = _linfit(widths, ics)
    verdict = ("PASS" if max_err < BAR_SINE_ERR
               and abs(slope - tn.I_C_PER_PATH) < BAR_IC_SLOPE_TOL
               and r2 >= BAR_IC_R2 else "FAIL")
    return {"id": "(iv)", "name": "current-phase", "verdict": verdict,
            "max_sine_error": max_err, "ic_slope": slope,
            "ic_slope_expected": tn.I_C_PER_PATH, "r2": r2,
            "bar_sine_err": BAR_SINE_ERR, "bar_r2": BAR_IC_R2}


def claim_height(seeds=FROZEN_SEEDS) -> dict:
    """(v) Transmission strictly decreases with barrier height; the
    nearly-closed barrier transmits at most a fifth of the open chain."""
    path = pa.straight_path((1, 0), AXIS_STEPS)
    ts = [_mean_transmission(path, h, HEIGHT_SWEEP_WIDTH, seeds)
          for h in HEIGHTS]
    strictly = all(ts[i] > ts[i + 1] for i in range(len(ts) - 1))
    ratio = ts[-1] / ts[0] if ts[0] > 0 else float("inf")
    verdict = "PASS" if strictly and ratio <= BAR_SUPPRESSION else "FAIL"
    return {"id": "(v)", "name": "height", "verdict": verdict,
            "transmissions": ts, "heights": list(HEIGHTS),
            "strictly_decreasing": strictly, "ratio_t099_t0": ratio,
            "bar": BAR_SUPPRESSION}


def claim_width(seeds=FROZEN_SEEDS) -> dict:
    """(vi) Log transmission is linear in barrier width (edges crossed),
    exponential falloff, not linear and not a step."""
    path = pa.straight_path((1, 0), AXIS_STEPS)
    ts = [_mean_transmission(path, WIDTH_SWEEP_HEIGHT, w, seeds)
          for w in WIDTHS]
    log_t = [np.log(max(t, 1e-300)) for t in ts]
    slope, _, r2 = _linfit(list(WIDTHS), log_t)
    verdict = "PASS" if slope < BAR_WIDTH_SLOPE and r2 >= BAR_WIDTH_R2 else "FAIL"
    return {"id": "(vi)", "name": "width-exponential", "verdict": verdict,
            "slope": slope, "r2": r2, "transmissions": ts,
            "widths": list(WIDTHS), "bar_slope": BAR_WIDTH_SLOPE,
            "bar_r2": BAR_WIDTH_R2}


def claim_current_density() -> dict:
    """(vii) The honeycomb junction carries at least as much critical
    current per unit width as a square junction. Measured: 1/sqrt(3)."""
    ratio = tn.current_density_ratio()
    verdict = "PASS" if ratio >= BAR_DENSITY_RATIO else "FAIL"
    return {"id": "(vii)", "name": "current-density", "verdict": verdict,
            "ratio": ratio, "bar": BAR_DENSITY_RATIO,
            "honeycomb_per_unit_width": tn.paths_per_unit_width(tn.NEIGHBOUR_SPACING),
            "square_per_unit_width": tn.paths_per_unit_width(tn.SQUARE_SPACING)}


def evaluate_all(seeds=FROZEN_SEEDS) -> list[dict]:
    """Run every claim on the frozen seeds. Bars are frozen; verdicts are measured."""
    return [
        claim_geometry(),
        claim_turn_cost(seeds),
        claim_axis(seeds),
        claim_current_phase(),
        claim_height(seeds),
        claim_width(seeds),
        claim_current_density(),
    ]


def report(results: list[dict]) -> str:
    """The measured claims table, with the numbers."""
    lines = ["Bee geometry tunneling -- measured claims (bars frozen before evaluation)",
             ""]
    for r in results:
        if r["id"] == "(i)":
            failed = [k for k, v in r["checks"].items() if not v]
            lines.append(f"(i) geometry: {r['verdict']} -- "
                         f"{'all 8 checks exact' if not failed else 'FAILED: ' + ', '.join(failed)} "
                         f"(perimeters hex {r['perimeters']['hexagon']:.4f} < "
                         f"square {r['perimeters']['square']:.4f} < "
                         f"triangle {r['perimeters']['triangle']:.4f})")
        elif r["id"] == "(ii)":
            lines.append(f"(ii) turn-cost: {r['verdict']} -- slope "
                         f"{r['slope']:.4f}, expected log(0.8) = {r['expected_slope']:.4f}, "
                         f"R^2 = {r['r2']:.4f} (bars |slope - expected| <= {r['bar_slope_tol']}, R^2 >= {r['bar_r2']})")
        elif r["id"] == "(iii)":
            lines.append(f"(iii) axis-vs-off-axis: {r['verdict']} -- "
                         f"T_on = {r['t_on_axis']:.4f} ({r['turns_on']} turns), "
                         f"T_off = {r['t_off_axis']:.4f} ({r['turns_off']} turns), "
                         f"ratio {r['ratio']:.2f} (bar >= {r['bar']})")
        elif r["id"] == "(iv)":
            lines.append(f"(iv) current-phase: {r['verdict']} -- max sine error "
                         f"{r['max_sine_error']:.2e}, I_c slope {r['ic_slope']:.4f} "
                         f"(expected {r['ic_slope_expected']}), R^2 = {r['r2']:.6f}")
        elif r["id"] == "(v)":
            lines.append(f"(v) height: {r['verdict']} -- strictly decreasing "
                         f"{r['strictly_decreasing']}, T(0.99)/T(0) = {r['ratio_t099_t0']:.2e} "
                         f"(bar <= {r['bar']})")
        elif r["id"] == "(vi)":
            lines.append(f"(vi) width-exponential: {r['verdict']} -- slope "
                         f"{r['slope']:.4f} per edge, R^2 = {r['r2']:.6f} "
                         f"(bars slope < {r['bar_slope']}, R^2 >= {r['bar_r2']})")
        elif r["id"] == "(vii)":
            lines.append(f"(vii) current-density: {r['verdict']} -- honeycomb/square "
                         f"per unit width = {r['ratio']:.4f} (bar >= {r['bar']}); "
                         f"honeycomb {r['honeycomb_per_unit_width']:.4f} vs square "
                         f"{r['square_per_unit_width']:.4f} paths per unit width")
    n_pass = sum(1 for r in results if r["verdict"] == "PASS")
    lines.append("")
    lines.append(f"{n_pass}/{len(results)} claims pass. Synthetic, classical. No headline.")
    return "\n".join(lines)
