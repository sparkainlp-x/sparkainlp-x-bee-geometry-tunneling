# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
# SPDX-License-Identifier: AGPL-3.0-only
"""Tests for the honeycomb geometry."""
import math

import numpy as np
import pytest

from bee_geometry_tunneling import honeycomb as hc


def test_six_neighbours_at_60_degree_steps():
    nbs = hc.neighbours(0, 0)
    assert len(nbs) == 6
    assert len(set(nbs)) == 6
    angles = sorted(hc.direction_angle(d) for d in hc.NEIGHBOUR_OFFSETS)
    expected = [0.0, 60.0, 120.0, 180.0, 240.0, 300.0]
    assert all(abs(a - e) < 1e-9 for a, e in zip(angles, expected))


def test_neighbour_distance_is_sqrt3():
    c0 = np.array(hc.cell_center(0, 0))
    for nb in hc.neighbours(0, 0):
        d = np.hypot(*(np.array(hc.cell_center(*nb)) - c0))
        assert abs(d - math.sqrt(3)) < 1e-12


def test_neighbours_are_symmetric():
    for q, r in [(0, 0), (2, -1), (-3, 4)]:
        for nb in hc.neighbours(q, r):
            assert (q, r) in hc.neighbours(*nb)


def test_interior_angle_is_120_degrees():
    assert hc.INTERIOR_ANGLE_DEG == 120.0
    assert hc.TURN_ANGLE_DEG == 60.0


def test_hex_distance():
    assert hc.hex_distance((0, 0), (0, 0)) == 0
    assert hc.hex_distance((0, 0), (1, 0)) == 1
    assert hc.hex_distance((0, 0), (4, 0)) == 4
    assert hc.hex_distance((0, 0), (2, -2)) == 2
    assert hc.hex_distance((0, 0), (3, -1)) == 3


def test_vertex_patch_bipartite_24_vertices_30_edges_12_12():
    patch = hc.vertex_patch()
    assert patch["bipartite"] is True
    assert patch["n_vertices"] == 24
    assert patch["n_edges"] == 30
    assert len(patch["A"]) == 12
    assert len(patch["B"]) == 12
    assert not (patch["A"] & patch["B"])


def test_hales_perimeter_order():
    per_hex = hc.tile_perimeter("hexagon")
    per_sq = hc.tile_perimeter("square")
    per_tri = hc.tile_perimeter("triangle")
    assert per_hex < per_sq < per_tri
    assert abs(per_hex - 3.7224) < 1e-3
    assert abs(per_sq - 4.0) < 1e-12
    assert abs(per_tri - 4.5590) < 1e-3


def test_tile_perimeter_rejects_bad_input():
    with pytest.raises(ValueError):
        hc.tile_perimeter("pentagon")
    with pytest.raises(ValueError):
        hc.tile_perimeter("hexagon", area=0.0)


def test_direction_angle_rejects_non_neighbour():
    with pytest.raises(ValueError):
        hc.direction_angle((2, 0))
