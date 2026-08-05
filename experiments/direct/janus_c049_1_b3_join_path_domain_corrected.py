from __future__ import annotations

from typing import Iterator, Sequence

from janus_c049_1_b3_expand_join_shrink_core import (
    Statistic,
    extension_preorder_witness,
    join_trajectory as _legacy_join_trajectory,
)

JOIN_INTERLEAVING_STEPS: tuple[tuple[int, int], ...] = ((1, 0), (0, 1))
EXTENSION_PREORDER_STEPS: tuple[tuple[int, int], ...] = ((1, 0), (0, 1), (1, 1))


def ordinary_join_paths(m: int, n: int) -> Iterator[tuple[tuple[int, int], ...]]:
    """Enumerate linear interleavings of two nonempty child trajectories.

    A join advances exactly one child order at every step.  Diagonal steps are
    deliberately absent; they belong to extension-preorder comparison only.
    """
    if m <= 0 or n <= 0:
        return

    def rec(i: int, j: int, path: list[tuple[int, int]]):
        if i == m - 1 and j == n - 1:
            yield tuple(path)
            return
        for di, dj in JOIN_INTERLEAVING_STEPS:
            ni, nj = i + di, j + dj
            if ni < m and nj < n:
                path.append((ni, nj))
                yield from rec(ni, nj, path)
                path.pop()

    yield from rec(0, 0, [(0, 0)])


def validate_ordinary_join_path(
    path: Sequence[Sequence[int]], m: int, n: int
) -> tuple[tuple[int, int], ...]:
    parsed = tuple((int(point[0]), int(point[1])) for point in path)
    if not parsed or parsed[0] != (0, 0) or parsed[-1] != (m - 1, n - 1):
        raise ValueError("bad ordinary join path endpoints")
    if len(set(parsed)) != len(parsed):
        raise ValueError("ordinary join path repeats a point")
    for current, following in zip(parsed, parsed[1:]):
        step = (following[0] - current[0], following[1] - current[1])
        if step not in JOIN_INTERLEAVING_STEPS:
            raise ValueError("ordinary join path contains a non-interleaving step")
    return parsed


def join_trajectory(
    g1: Sequence[Statistic],
    g2: Sequence[Statistic],
    path: Sequence[Sequence[int]],
    boundary: Sequence[int],
    ambient_dim: int,
):
    """Strict B3 join wrapper using the ordinary interleaving path domain."""
    parsed = validate_ordinary_join_path(path, len(g1), len(g2))
    return _legacy_join_trajectory(g1, g2, parsed, boundary, ambient_dim)
