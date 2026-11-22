# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
# SPDX-License-Identifier: AGPL-3.0-only
"""Paths through the honeycomb: the routes a tunneling wave takes.

A path is a sequence of cells, each step to a neighbour (one shared
hexagon edge crossed per step). The direction can continue straight
(no turn) or change by 60 degrees at a cell (one turn, through the
hexagon's 120-degree corner). Two neighbour directions are adjacent
when they differ by one step in direction-angle order.

Builders:
  straight_path -- all steps in one direction (0 turns). Exists only
      along the 6 symmetry axes; this is the on-axis route.
  zigzag_path -- alternating two adjacent directions (a turn at every
      step). The off-axis route: same barrier, many more turns.
  path_with_turns -- n steps split into n_turns + 1 straight segments
      alternating two adjacent directions, as evenly as possible.

The barrier is a block of WIDTH consecutive links of the path,
centred (the same construction as josephson-membrane's tunneling:
a set of consecutive suppressed links). A path's barrier links are
the ones the wave must tunnel through; the turns are the geometric
cost of the route. Straight and zigzag paths through the same barrier
have the same number of barrier links and differ only in turns --
that is what makes the axis claim a clean geometric comparison.
"""

from __future__ import annotations

from .honeycomb import NEIGHBOUR_OFFSETS


def _step(cell: tuple[int, int], direction: tuple[int, int]) -> tuple[int, int]:
    return (cell[0] + direction[0], cell[1] + direction[1])


def straight_path(direction: tuple[int, int], n_steps: int,
                  start: tuple[int, int] = (0, 0)) -> list[tuple[int, int]]:
    """n_steps in one neighbour direction. 0 turns."""
    if direction not in NEIGHBOUR_OFFSETS:
        raise ValueError(f"not a neighbour direction: {direction!r}")
    if n_steps < 0:
        raise ValueError("n_steps must be >= 0")
    path = [start]
    for _ in range(n_steps):
        path.append(_step(path[-1], direction))
    return path


def zigzag_path(n_steps: int, dir_a: tuple[int, int] = (1, 0),
                dir_b: tuple[int, int] = (0, 1),
                start: tuple[int, int] = (0, 0)) -> list[tuple[int, int]]:
    """Alternating two adjacent neighbour directions. A turn at every step
    after the first: n_steps - 1 turns for n_steps steps."""
    idx_a = NEIGHBOUR_OFFSETS.index(dir_a)
    idx_b = NEIGHBOUR_OFFSETS.index(dir_b)
    if (idx_b - idx_a) % 6 not in (1, 5):
        raise ValueError("zigzag directions must be adjacent (60 deg apart)")
    path = [start]
    for i in range(n_steps):
        d = dir_a if i % 2 == 0 else dir_b
        path.append(_step(path[-1], d))
    return path


def path_with_turns(n_steps: int, n_turns: int,
                    dir_a: tuple[int, int] = (1, 0),
                    dir_b: tuple[int, int] = (0, 1),
                    start: tuple[int, int] = (0, 0)) -> list[tuple[int, int]]:
    """n_steps split into n_turns + 1 straight segments alternating two
    adjacent directions, as evenly as possible. Exactly n_turns turns
    (each segment junction is a 60-degree turn), same edge count as a
    straight path of n_steps."""
    if n_turns < 0 or n_turns > max(0, n_steps - 1):
        raise ValueError(f"n_turns must be in [0, {max(0, n_steps - 1)}]")
    idx_a = NEIGHBOUR_OFFSETS.index(dir_a)
    idx_b = NEIGHBOUR_OFFSETS.index(dir_b)
    if (idx_b - idx_a) % 6 not in (1, 5):
        raise ValueError("turn directions must be adjacent (60 deg apart)")
    n_segments = n_turns + 1
    base, extra = divmod(n_steps, n_segments)
    path = [start]
    for seg in range(n_segments):
        d = dir_a if seg % 2 == 0 else dir_b
        for _ in range(base + (1 if seg < extra else 0)):
            path.append(_step(path[-1], d))
    return path


def directions(path: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """The step direction of each link of the path."""
    return [(path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1])
            for i in range(len(path) - 1)]


def edge_count(path: list[tuple[int, int]]) -> int:
    """Number of hexagon edges crossed = number of links."""
    return len(path) - 1


def turn_count(path: list[tuple[int, int]]) -> int:
    """Number of 60-degree direction changes (turns through the 120-degree
    interior corner)."""
    dirs = directions(path)
    return sum(1 for i in range(1, len(dirs)) if dirs[i] != dirs[i - 1])


def barrier_links(path: list[tuple[int, int]], width: int) -> list[int]:
    """Indices of the barrier links: a block of `width` consecutive links,
    centred on the path. The wave tunnels through exactly these links."""
    n = edge_count(path)
    if width < 0:
        raise ValueError("width must be >= 0")
    w = min(width, n)
    start = (n - w) // 2
    return list(range(start, start + w))
