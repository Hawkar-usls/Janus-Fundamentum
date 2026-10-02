#!/usr/bin/env python3
"""Exact controls for R5 E53.

Enumerates one E12 gadget as an Exact-Cover module:
  * every internal element z/Z/t must be covered exactly once;
  * boundary x1,x2,x3,p1,p2,p3 may be covered 0/1 times locally.
Verifies that the only boundary signatures are
  (a,b) in {(0,0),(1,0),(0,1),(1,1)},
where a means all three unprimed ports are covered and b all three primed ports.
Also records the exact multiplicities 3,2,2,1 of local internal states.

For the frozen q=6 source, builds the RXC3 incidence matrix R, verifies det(R)=-9,
and checks that the unique rational solution of R a=1 is a=(1/3)1, hence no
Boolean quotient solution exists.

P_VS_NP remains OPEN.
"""

from fractions import Fraction
from itertools import combinations
from collections import Counter


def gadget():
    boundary = ["x1", "x2", "x3", "p1", "p2", "p3"]
    z = [f"z{i}" for i in range(1, 7)]
    Z = [f"Z{i}" for i in range(1, 7)]
    t = [f"t{i}" for i in range(1, 4)]
    internal = z + Z + t
    triples = [
        ("L1", {"x1", "z1", "z4"}),
        ("L2", {"x2", "z2", "z5"}),
        ("L3", {"x3", "z3", "z6"}),
        ("L4", {"z1", "z2", "z3"}),
        ("L5", {"z4", "z5", "z6"}),
        ("P1", {"p1", "Z1", "Z4"}),
        ("P2", {"p2", "Z2", "Z5"}),
        ("P3", {"p3", "Z3", "Z6"}),
        ("P4", {"Z1", "Z2", "Z3"}),
        ("P5", {"Z4", "Z5", "Z6"}),
        ("D1", {"z2", "z6", "t1"}),
        ("D2", {"z3", "z4", "t2"}),
        ("D3", {"z1", "z5", "t3"}),
        ("D4", {"Z2", "Z6", "t2"}),
        ("D5", {"Z3", "Z4", "t3"}),
        ("D6", {"Z1", "Z5", "t1"}),
        ("D7", {"t1", "t2", "t3"}),
    ]
    return boundary, internal, triples


def local_states():
    boundary, internal, triples = gadget()
    names = [name for name, _ in triples]
    sets = [T for _, T in triples]
    out = []

    for mask in range(1 << len(triples)):
        chosen = [j for j in range(len(triples)) if (mask >> j) & 1]
        counts = Counter()
        for j in chosen:
            counts.update(sets[j])

        if any(counts[e] != 1 for e in internal):
            continue
        if any(counts[e] > 1 for e in boundary):
            continue

        u = tuple(counts[e] for e in ("x1", "x2", "x3"))
        p = tuple(counts[e] for e in ("p1", "p2", "p3"))
        assert len(set(u)) == 1
        assert len(set(p)) == 1
        a, b = u[0], p[0]
        out.append(((a, b), tuple(names[j] for j in chosen)))

    return out


def rx_fixture():
    q = 6
    source_sets = [tuple(sorted({i, (i + 1) % q, (i + 3) % q})) for i in range(q)]
    return q, source_sets


def source_matrix(q, source_sets):
    R = [[0] * q for _ in range(q)]
    for j, C in enumerate(source_sets):
        for i in C:
            R[i][j] = 1
    return R


def solve_q(M, rhs):
    A = [[Fraction(x) for x in row] + [Fraction(b)] for row, b in zip(M, rhs)]
    m = len(A)
    n = len(M[0])
    pivots = []
    r = 0
    det = Fraction(1) if m == n else None
    swaps = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if A[i][c]), None)
        if pivot is None:
            continue
        if pivot != r:
            A[r], A[pivot] = A[pivot], A[r]
            swaps += 1
        z = A[r][c]
        if det is not None:
            det *= z
        A[r] = [x / z for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [A[i][j] - f * A[r][j] for j in range(n + 1)]
        pivots.append(c)
        r += 1
    if det is not None and swaps % 2:
        det = -det
    if len(pivots) != n:
        return None, det, len(pivots)
    sol = [Fraction(0)] * n
    for rr, c in enumerate(pivots):
        sol[c] = A[rr][-1]
    return sol, det, len(pivots)


def main():
    states = local_states()
    sigs = Counter(sig for sig, _ in states)
    assert len(states) == 8
    assert sigs == Counter({(0, 0): 3, (1, 0): 2, (0, 1): 2, (1, 1): 1})
    assert set(sigs) == {(0, 0), (1, 0), (0, 1), (1, 1)}

    q, source_sets = rx_fixture()
    R = source_matrix(q, source_sets)
    sol, det, rank = solve_q(R, [1] * q)
    assert rank == q
    assert det == -9
    assert sol == [Fraction(1, 3)] * q
    assert any(x.denominator != 1 for x in sol)

    print("R5 E53 E12 Boolean boundary quotient controls: PASS")
    print("one gadget: 8 internal states; boundary signatures (00)x3,(10)x2,(01)x2,(11)x1")
    print("global quotient: R a=1 and R b=1; frozen q=6 R has det=-9 and unique a=b=(1/3)1 -> UNSAT")


if __name__ == "__main__":
    main()
