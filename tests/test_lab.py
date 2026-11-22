# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
# SPDX-License-Identifier: AGPL-3.0-only
"""Tests for the lab claims: every verdict follows from its numbers."""
import numpy as np

from bee_geometry_tunneling import lab


def test_claim_geometry_verdict_follows_its_numbers():
    r = lab.claim_geometry()
    assert r["verdict"] == ("PASS" if all(r["checks"].values()) else "FAIL")
    assert r["verdict"] == "PASS"


def test_claim_turn_cost_verdict_follows_its_numbers():
    r = lab.claim_turn_cost()
    expect = (abs(r["slope"] - r["expected_slope"]) <= r["bar_slope_tol"]
              and r["r2"] >= r["bar_r2"])
    assert r["verdict"] == ("PASS" if expect else "FAIL")
    assert r["verdict"] == "PASS"


def test_claim_axis_verdict_follows_its_numbers():
    r = lab.claim_axis()
    assert r["verdict"] == ("PASS" if r["ratio"] >= r["bar"] else "FAIL")
    assert r["verdict"] == "PASS"
    assert r["turns_on"] == 0
    assert r["turns_off"] == 5


def test_claim_current_phase_verdict_follows_its_numbers():
    r = lab.claim_current_phase()
    expect = (r["max_sine_error"] < r["bar_sine_err"]
              and abs(r["ic_slope"] - r["ic_slope_expected"]) < lab.BAR_IC_SLOPE_TOL
              and r["r2"] >= r["bar_r2"])
    assert r["verdict"] == ("PASS" if expect else "FAIL")
    assert r["verdict"] == "PASS"


def test_claim_height_verdict_follows_its_numbers():
    r = lab.claim_height()
    expect = r["strictly_decreasing"] and r["ratio_t099_t0"] <= r["bar"]
    assert r["verdict"] == ("PASS" if expect else "FAIL")
    assert r["verdict"] == "PASS"


def test_claim_width_verdict_follows_its_numbers():
    r = lab.claim_width()
    expect = r["slope"] < r["bar_slope"] and r["r2"] >= r["bar_r2"]
    assert r["verdict"] == ("PASS" if expect else "FAIL")
    assert r["verdict"] == "PASS"


def test_claim_current_density_is_an_honest_fail():
    # The honeycomb carries 1/sqrt(3) = 0.577 of the square's current per
    # unit width. The directional claim (ratio >= 1) FAILS, as designed:
    # the bee's wax efficiency does not buy current density.
    r = lab.claim_current_density()
    assert abs(r["ratio"] - 1.0 / np.sqrt(3)) < 1e-12
    assert r["ratio"] < r["bar"]
    assert r["verdict"] == "FAIL"


def test_evaluate_all_returns_seven_claims_with_verdicts():
    results = lab.evaluate_all()
    assert len(results) == 7
    assert [r["id"] for r in results] == ["(i)", "(ii)", "(iii)", "(iv)",
                                          "(v)", "(vi)", "(vii)"]
    assert all(r["verdict"] in ("PASS", "FAIL") for r in results)
    verdicts = [r["verdict"] for r in results]
    assert verdicts == ["PASS", "PASS", "PASS", "PASS", "PASS", "PASS", "FAIL"]
    text = lab.report(results)
    assert "TODO" not in text and "TO COMPLETE" not in text
    assert "No headline" in text
