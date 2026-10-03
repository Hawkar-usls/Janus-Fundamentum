#!/usr/bin/env python3
"""R5 E62 exact controls: hypergraph perfect matching / balanced odd-cycle frontier."""

import itertools
from fractions import Fraction

P_SAT = [7, 6, 11, 10, 8, 4, 9, 5, 0, 3, 2, 1]
Q_SAT = [11, 8, 3, 4, 7, 9, 0, 10, 2, 1, 6, 5]
P_UNSAT = [6, 3, 7, 10, 11, 1, 4, 8, 9, 5, 2, 0]
Q_UNSAT = [3, 4, 5, 8, 7, 0, 9, 6, 2, 11, 1, 10]


def build_A(p, q):
    n = len(p)
    A = [[0] * n for _ in range(n)]
    for i in range(n):
        cols = (i, p[i], q[i])
        assert len(set(cols)) == 3
        for j in cols:
            A[i][j] = 1
    assert all(sum(r) == 3 for r in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))
    return A


def dual_hyperedges(A):
    n = len(A)
    return [frozenset(i for i in range(n) if A[i][j]) for j in range(n)]


def verify_hypergraph(E):
    n = len(E)
    assert all(len(e) == 3 for e in E)
    deg = [sum(v in e for e in E) for v in range(n)]
    assert all(d == 3 for d in deg)
    assert all(len(E[i] & E[j]) <= 1 for i in range(n) for j in range(i + 1, n))


def exact_one_witnesses(A):
    n = len(A)
    out = []
    if n % 3:
        return out
    for S in itertools.combinations(range(n), n // 3):
        if all(sum(A[i][j] for j in S) == 1 for i in range(n)):
            out.append(frozenset(S))
    return out


def perfect_matchings(E):
    n = len(E)
    out = []
    if n % 3:
        return out
    for M in itertools.combinations(range(n), n // 3):
        covered = set()
        ok = True
        for j in M:
            if covered & E[j]:
                ok = False
                break
            covered |= set(E[j])
        if ok and covered == set(range(n)):
            out.append(frozenset(M))
    return out


def verify_fractional_point(A):
    n = len(A)
    z = [Fraction(1, 3)] * n
    y = [sum(Fraction(a) * b for a, b in zip(row, z)) for row in A]
    assert y == [Fraction(1)] * n


def independent_sets_cycle(l):
    out = []
    for c in itertools.product((0, 1), repeat=l):
        if all(not (c[i - 1] and c[i]) for i in range(l)):
            out.append(c)
    return out


def cycle_signature(l):
    """External interface s_i=1-c_{i-1}-c_i for a strong cycle."""
    out = set()
    for c in independent_sets_cycle(l):
        s = tuple(1 - c[i - 1] - c[i] for i in range(l))
        assert all(v in (0, 1) for v in s)
        out.add(s)
    return out


def brute_cycle_signature(l):
    out = set()
    for s in itertools.product((0, 1), repeat=l):
        for c in itertools.product((0, 1), repeat=l):
            if all(c[i - 1] + c[i] + s[i] == 1 for i in range(l)):
                out.add(s)
                break
    return out


def lucas(n):
    if n == 0:
        return 2
    if n == 1:
        return 1
    a, b = 2, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def verify_strong_cycle(E, cycle_edges):
    l = len(cycle_edges)
    cycle_vertices = []
    for i in range(l):
        a = cycle_edges[i - 1]
        b = cycle_edges[i]
        I = E[a] & E[b]
        assert len(I) == 1
        cycle_vertices.append(next(iter(I)))
    assert len(set(cycle_vertices)) == l
    V = set(cycle_vertices)
    for e in cycle_edges:
        assert len(E[e] & V) == 2

    external_edges = []
    for i, v in enumerate(cycle_vertices):
        incident = [e for e in range(len(E)) if v in E[e]]
        pair = {cycle_edges[i - 1], cycle_edges[i]}
        outside = [e for e in incident if e not in pair]
        assert len(outside) == 1
        external_edges.append(outside[0])
    return tuple(cycle_vertices), tuple(external_edges)


def main():
    fixtures = [
        ("SAT12", P_SAT, Q_SAT, True, (0, 2, 6), (0, 2, 3, 4, 9)),
        ("UNSAT12_E57", P_UNSAT, Q_UNSAT, False, (0, 1, 3), (0, 1, 2, 8, 6)),
    ]
    for name, p, q, expect_sat, tri, five in fixtures:
        A = build_A(p, q)
        E = dual_hyperedges(A)
        verify_hypergraph(E)
        verify_fractional_point(A)

        X = exact_one_witnesses(A)
        M = perfect_matchings(E)
        assert set(X) == set(M)
        assert bool(M) == expect_sat

        tri_v, tri_ext = verify_strong_cycle(E, tri)
        five_v, five_ext = verify_strong_cycle(E, five)
        assert len(set(tri_ext)) == 3
        assert len(set(five_ext)) == 5

        print(f"{name}: exact_one={len(X)} perfect_matchings={len(M)}")
        print(f"  strong-3 cycle={tri} vertices={tri_v} external={tri_ext}")
        print(f"  strong-5 cycle={five} vertices={five_v} external={five_ext}")

    for l in (3, 5, 7, 9):
        R = cycle_signature(l)
        assert R == brute_cycle_signature(l)
        assert len(R) == lucas(l)
        print(f"R_{l}: states={len(R)}=Lucas({l})")

    R3 = cycle_signature(3)
    expected3 = {
        (0, 0, 1),
        (0, 1, 0),
        (1, 0, 0),
        (1, 1, 1),
    }
    assert R3 == expected3
    assert all((sum(s) & 1) == 1 for s in R3)
    assert all(s in R3 for s in itertools.product((0, 1), repeat=3) if (sum(s) & 1) == 1)

    R5 = cycle_signature(5)
    assert len(R5) == 11
    a = (0, 0, 0, 0, 1)
    b = (0, 0, 0, 1, 0)
    c = (0, 1, 0, 0, 0)
    assert a in R5 and b in R5 and c in R5
    xor3 = tuple(a[i] ^ b[i] ^ c[i] for i in range(5))
    assert xor3 == (0, 1, 0, 1, 1)
    assert xor3 not in R5

    print("R5 E62 hypergraph/balanced strong-odd-cycle frontier: PASS")
    print("R3 is affine XOR=1; R5 has 11 states and is non-affine")


if __name__ == "__main__":
    main()
