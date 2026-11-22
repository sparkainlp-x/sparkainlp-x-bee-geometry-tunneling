# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
# SPDX-License-Identifier: AGPL-3.0-only
"""The honeycomb: the bee's hexagonal lattice.

A regular hexagon tiled. Each cell has 6 neighbours, one per shared
edge, at 60-degree steps, at distance sqrt(3) for circumradius 1
(the same construction as symmetry-entropy's honeycomb patch: neighbour
centres at distance sqrt(3), vertices at (sin 60k deg, cos 60k deg)).
The interior angle is 120 degrees; a path that changes direction at a
cell turns by 60 degrees, through that 120-degree corner.

Two graphs live on the tiling, and they are not the same:
  - the CELL graph: hexagon centres, 6 neighbours each, a triangular
    lattice. The tunneling wave hops cell to cell across shared edges.
  - the VERTEX graph: hexagon corners, 3 edges meeting at 120 degrees
    each, a bipartite honeycomb (two sublattices A and B, like
    graphene). A 7-cell patch has 24 vertices and 30 edges, split
    12/12 between the sublattices.

Hales (1999): for unit area the regular hexagon has the least
perimeter of the three regular tilings (3.7224 < 4.0000 square <
4.5590 triangle). The bee minimises wax. Whether that efficiency
buys anything for tunneling is a measured claim, not an assumption --
see lab claim (vii).
"""

from __future__ import annotations

import math
from collections import deque

# Axial coordinates (q, r) for hex cells. The 6 neighbour offsets, in
# order of increasing direction angle (0, 60, 120, 180, 240, 300 deg).
NEIGHBOUR_OFFSETS = ((1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1))
N_NEIGHBOURS = 6
NEIGHBOUR_DISTANCE = math.sqrt(3.0)  # for circumradius 1
INTERIOR_ANGLE_DEG = 120.0
TURN_ANGLE_DEG = 60.0  # direction change at a cell (exterior angle)


def cell_center(q: int, r: int) -> tuple[float, float]:
    """Pixel position of a cell centre (pointy-top axial layout)."""
    return (math.sqrt(3.0) * (q + r / 2.0), 1.5 * r)


def neighbours(q: int, r: int) -> list[tuple[int, int]]:
    """The 6 neighbour cells of (q, r), in direction-angle order."""
    return [(q + dq, r + dr) for dq, dr in NEIGHBOUR_OFFSETS]


def direction_angle(direction: tuple[int, int]) -> float:
    """Angle in degrees of an axial neighbour direction (0..360)."""
    if direction not in NEIGHBOUR_OFFSETS:
        raise ValueError(f"not a neighbour direction: {direction!r}")
    x, y = cell_center(*direction)
    return math.degrees(math.atan2(y, x)) % 360.0


def hex_distance(a: tuple[int, int], b: tuple[int, int]) -> int:
    """Shortest path length in edges between two cells (axial distance)."""
    dq = a[0] - b[0]
    dr = a[1] - b[1]
    return (abs(dq) + abs(dr) + abs(dq + dr)) // 2


def _hexagon_vertices(cx: float, cy: float) -> list[tuple[float, float]]:
    """The 6 vertices of a pointy-top hexagon (circumradius 1)."""
    return [(cx + math.sin(math.radians(60 * k)),
             cy + math.cos(math.radians(60 * k))) for k in range(6)]


def vertex_patch() -> dict:
    """The vertex graph of a 7-cell patch (central hexagon + 6 neighbours).

    Returns vertices, edges, the two sublattices A and B, and the
    bipartite flag (2-colouring by BFS; a conflict means not bipartite).
    The patch has 24 vertices and 30 edges, split 12/12.
    """
    centers = [(0.0, 0.0)]
    for k in range(6):
        a = math.radians(60 * k)
        centers.append((math.sqrt(3) * math.cos(a),
                        math.sqrt(3) * math.sin(a)))

    def _key(pt):
        return (round(pt[0], 9), round(pt[1], 9))

    key_to_pt = {}
    edges = set()
    for cx, cy in centers:
        vs = _hexagon_vertices(cx, cy)
        for i in range(6):
            a, b = vs[i], vs[(i + 1) % 6]
            ka, kb = _key(a), _key(b)
            key_to_pt[ka] = a
            key_to_pt[kb] = b
            edges.add((min(ka, kb), max(ka, kb)))
    verts = set(key_to_pt)
    adj = {v: set() for v in verts}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    color = {}
    for start in verts:
        if start in color:
            continue
        color[start] = 0
        queue = deque([start])
        while queue:
            u = queue.popleft()
            for w in adj[u]:
                if w not in color:
                    color[w] = 1 - color[u]
                    queue.append(w)
                elif color[w] == color[u]:
                    return {"bipartite": False, "A": set(), "B": set(),
                            "n_vertices": len(verts), "n_edges": len(edges)}
    a_set = {key_to_pt[v] for v, c in color.items() if c == 0}
    b_set = {key_to_pt[v] for v, c in color.items() if c == 1}
    return {"bipartite": True, "A": a_set, "B": b_set,
            "n_vertices": len(verts), "n_edges": len(edges)}


def tile_perimeter(shape: str, area: float = 1.0) -> float:
    """Perimeter of a regular tile of the given area (default 1).

    Hexagon: 6*sqrt(2*area/(3*sqrt(3))) -- least of the three.
    Square: 4*sqrt(area). Equilateral triangle:
    3*sqrt(4*area/sqrt(3)) -- most of the three. Hales (1999).
    """
    if area <= 0:
        raise ValueError("area must be positive")
    if shape == "hexagon":
        return 6.0 * math.sqrt(2.0 * area / (3.0 * math.sqrt(3.0)))
    if shape == "square":
        return 4.0 * math.sqrt(area)
    if shape in ("triangle", "equilateral_triangle"):
        return 3.0 * math.sqrt(4.0 * area / math.sqrt(3.0))
    raise ValueError(f"unknown tile shape: {shape!r}")
