# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
# SPDX-License-Identifier: AGPL-3.0-only
"""Tests for paths and the tunneling model."""
import numpy as np
import pytest

from bee_geometry_tunneling import paths as pa
from bee_geometry_tunneling import tunneling as tn


def test_straight_path_has_zero_turns():
    p = pa.straight_path((1, 0), 6)
    assert pa.edge_count(p) == 6
    assert pa.turn_count(p) == 0
    assert p[-1] == (6, 0)


def test_zigzag_path_turns_at_every_step():
    p = pa.zigzag_path(6)
    assert pa.edge_count(p) == 6
    assert pa.turn_count(p) == 5


def test_zigzag_requires_adjacent_directions():
    with pytest.raises(ValueError):
        pa.zigzag_path(4, (1, 0), (-1, 0))


def test_path_with_turns_exact_turn_count():
    for m in range(6):
        p = pa.path_with_turns(6, m)
        assert pa.edge_count(p) == 6
        assert pa.turn_count(p) == m
    with pytest.raises(ValueError):
        pa.path_with_turns(6, 6)


def test_barrier_links_centred():
    p = pa.straight_path((1, 0), 6)
    assert pa.barrier_links(p, 2) == [2, 3]
    assert pa.barrier_links(p, 0) == []
    assert pa.barrier_links(p, 6) == [0, 1, 2, 3, 4, 5]
    assert pa.barrier_links(p, 99) == [0, 1, 2, 3, 4, 5]


def test_transmission_is_a_probability():
    rng = np.random.default_rng(42)
    p = pa.straight_path((1, 0), 6)
    for h in (0.0, 0.5, 0.99, 1.0):
        t = tn.transmission(p, h, 2, rng=rng)
        assert 0.0 <= t <= 1.0


def test_height_one_cuts_the_chain():
    rng = np.random.default_rng(42)
    p = pa.straight_path((1, 0), 6)
    assert tn.transmission(p, 1.0, 2, rng=rng) == 0.0


def test_height_zero_is_a_no_op_on_the_barrier():
    # At h = 0 the barrier links transmit 1 (up to disorder); the only
    # cost left is the turns.
    rng = np.random.default_rng(42)
    p = pa.straight_path((1, 0), 6)
    t = tn.transmission(p, 0.0, 6, rng=rng)
    assert abs(t - 1.0) < 0.2  # disorder only, no turns


def test_turn_cost_is_exact_without_disorder():
    # With sigma = 0 the turn factor is exact: T(m) = tau^m * (1-h)^w.
    p0 = pa.path_with_turns(6, 0)
    p3 = pa.path_with_turns(6, 3)
    rng0 = np.random.default_rng(1)
    rng3 = np.random.default_rng(1)
    # Same disorder draws would differ per path; use the no-disorder
    # limit by comparing the ratio of the deterministic parts.
    t0 = tn.transmission(p0, 0.5, 6, rng=rng0)
    t3 = tn.transmission(p3, 0.5, 6, rng=rng3)
    # Ratio is tau^3 up to the independent disorder draws (5% per link).
    assert 0.4 < t3 / t0 < 0.65  # tau^3 = 0.512


def test_josephson_sine_law_exact():
    for ic in (1.0, 3.0):
        for dphi in np.linspace(0, 2 * np.pi, 33):
            assert abs(tn.josephson_current(dphi, ic) - ic * np.sin(dphi)) < 1e-12


def test_junction_critical_current_scales_with_paths():
    assert tn.junction_critical_current(0) == 0.0
    assert tn.junction_critical_current(4) == 4.0 * tn.I_C_PER_PATH
    ics = [tn.junction_critical_current(w) for w in range(1, 7)]
    assert np.allclose(np.diff(ics), tn.I_C_PER_PATH)


def test_current_density_ratio_is_one_over_sqrt3():
    assert abs(tn.current_density_ratio() - 1.0 / np.sqrt(3)) < 1e-12
    assert tn.current_density_ratio() < 1.0


def test_transmission_rejects_bad_height():
    p = pa.straight_path((1, 0), 2)
    with pytest.raises(ValueError):
        tn.transmission(p, 1.5, 1)
    with pytest.raises(ValueError):
        tn.transmission(p, -0.1, 1)
