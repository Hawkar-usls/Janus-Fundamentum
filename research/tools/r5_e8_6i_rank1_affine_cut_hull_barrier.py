#!/usr/bin/env python3
from __future__ import annotations

from itertools import combinations, product

NAMES = ("0", "a", "b", "c", "u", "v")
PAIRS = tuple((i, j) for i in range(6) for j in range(i, 6))
PAIR_INDEX = {p: k for k, p in enumerate(PAIRS)}


def q(a: int, b: int, c: int, u: int, v: int) -> int:
    return (
        (a & b) ^ (a & u) ^ (a & c) ^ (a & v)
        ^ (b & c) ^ (b & v) ^ (c & u) ^ (u & v)
    )


def moment(vals: tuple[int, int, int, int, int]) -> int:
    w = (1,) + vals
    out = 0
    for k, (i, j) in enumerate(PAIRS):
        out |= ((w[i] & w[j]) << k)
    return out


def bit(v: int, k: int) -> int:
    return (v >> k) & 1


def row_reduce(rows: list[int], width: int) -> tuple[list[int], list[int]]:
    rows = [r for r in rows if r]
    pivots: list[int] = []
    rank = 0
    for col in range(width):
        pivot = next((i for i in range(rank, len(rows)) if bit(rows[i], col)), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and bit(rows[i], col):
                rows[i] ^= rows[rank]
        pivots.append(col)
        rank += 1
        if rank == len(rows):
            break
    return rows[:rank], pivots


def in_span(x: int, basis: list[int], width: int) -> bool:
    r1, _ = row_reduce(list(basis), width)
    r2, _ = row_reduce(list(basis) + [x], width)
    return len(r1) == len(r2)


def nullspace_basis(rows: list[int], width: int) -> list[int]:
    rref, pivots = row_reduce(rows, width)
    free = [c for c in range(width) if c not in pivots]
    out: list[int] = []
    for f in free:
        x = 1 << f
        for row, p in reversed(list(zip(rref, pivots))):
            s = 0
            for j in free:
                if bit(row, j) and bit(x, j):
                    s ^= 1
            if s:
                x |= 1 << p
        out.append(x)
    return out


def dot(x: int, y: int) -> int:
    return (x & y).bit_count() & 1


def first_row(v: int) -> tuple[int, ...]:
    return tuple(bit(v, PAIR_INDEX[(0, j)]) for j in range(6))


def is_rank1_moment(v: int) -> bool:
    w = first_row(v)
    for k, (i, j) in enumerate(PAIRS):
        if bit(v, k) != (w[i] & w[j]):
            return False
    return True


def main() -> None:
    concrete: list[tuple[tuple[int, int, int, int, int], int]] = []
    for vals in product((0, 1), repeat=5):
        a, b, c, u, v = vals
        if (u & v) == 0 and q(a, b, c, u, v) == 1:
            concrete.append((vals, moment(vals)))

    assert len(concrete) == 12

    base = concrete[0][1]
    differences = [m ^ base for _, m in concrete[1:]]
    basis, _ = row_reduce(differences, len(PAIRS))
    assert len(basis) == 11

    # The 12 concrete points are affinely independent.
    assert (1 << len(basis)) == 2048

    # Exhaustively materialize the affine hull.
    hull: set[int] = set()
    for mask in range(1 << len(basis)):
        x = base
        for i, b in enumerate(basis):
            if (mask >> i) & 1:
                x ^= b
        hull.add(x)
    assert len(hull) == 2048

    rank1_hull = {x for x in hull if is_rank1_moment(x)}
    concrete_moments = {m for _, m in concrete}
    assert rank1_hull == concrete_moments
    assert len(rank1_hull) == 12
    assert len(hull - rank1_hull) == 2036

    # Explicit 3-point affine combination:
    # 00110, 01001, 01100 in (a,b,c,u,v) notation.
    witnesses = ((0, 0, 1, 1, 0), (0, 1, 0, 0, 1), (0, 1, 1, 0, 0))
    lookup = {vals: m for vals, m in concrete}
    spurious = lookup[witnesses[0]] ^ lookup[witnesses[1]] ^ lookup[witnesses[2]]
    assert spurious in hull
    assert not is_rank1_moment(spurious)
    assert first_row(spurious) == (1, 0, 0, 0, 1, 1)

    # All affine equations valid on the concrete set are represented by the
    # annihilator of the difference space. Enumerate all of them and verify
    # that the explicit spurious point satisfies every one.
    annihilator = nullspace_basis(basis, len(PAIRS))
    assert len(annihilator) == 10
    equation_count = 0
    for mask in range(1 << len(annihilator)):
        normal = 0
        for i, b in enumerate(annihilator):
            if (mask >> i) & 1:
                normal ^= b
        rhs = dot(normal, base)
        assert all(dot(normal, m) == rhs for _, m in concrete)
        assert dot(normal, spurious) == rhs
        equation_count += 1
    assert equation_count == 1024

    # Sanity: the original local affine relaxation constraints hold.
    # Z_uv = 0.
    assert bit(spurious, PAIR_INDEX[(4, 5)]) == 0
    # Expanded majority moment equation:
    terms = ((1, 2), (1, 4), (1, 3), (1, 5),
             (2, 3), (2, 5), (3, 4), (4, 5))
    lhs = 0
    for p in terms:
        lhs ^= bit(spurious, PAIR_INDEX[tuple(sorted(p))])
    assert lhs == 1

    print("SINGLE_CLAUSE_CONCRETE_RANK1_POINTS = 12")
    print("AFFINE_HULL_DIMENSION = 11")
    print("AFFINE_HULL_SIZE = 2048")
    print("RANK1_POINTS_IN_HULL = 12")
    print("SPURIOUS_POINTS_IN_HULL = 2036")
    print("VALID_AFFINE_EQUATIONS_ENUMERATED = 1024")
    print("EXPLICIT_SPURIOUS_FIRST_ROW = 1,0,0,0,1,1")
    print("AFFINE_CUT_SEPARATION = FALSIFIED")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
