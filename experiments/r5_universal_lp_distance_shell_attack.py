#!/usr/bin/env python3
"""Universal LP-rounding attack control: Tutte-12 distance-shell fractional pins.

This audits a *universal-algorithm candidate*, not a polynomial solver.
On the E64/E123 UNSAT square/cubic/C4-free n=63 incidence carrier,
ALL 189 one-check pin states admit an exact rational 0<=x<=1 solution
to A x = 1. No LP library, floating arithmetic or external solver used.

E64 gives the canonical incidence matrix; E65 the independent GF(2)
kernel linear algebra.
"""
from __future__ import annotations

from collections import Counter, deque
from fractions import Fraction

from r5_e64_connected_postquotient_nullity_firewall import tutte12_incidence
from r5_e65_transpose_asymmetry_quantized_defect import gf2_rref_basis

SHELL = {
    0: Fraction(1),
    2: Fraction(0),
    4: Fraction(1, 2),
    6: Fraction(1, 4),
}
EXPECTED_PROFILE = Counter({0: 1, 2: 6, 4: 24, 6: 32})


def levy_graph(A):
    n = len(A)
    adj = [[] for _ in range(2*n)]
    for i, row in enumerate(A):
        assert len(row) == n
        for j, v in enumerate(row):
            if v:
                assert v == 1
                adj[i].append(n+j)
                adj[n+j].append(i)
    assert all(len(s) == 3 for s in adj)
    return adj


def distance_shells(adj, source):
    d = [-1]*len(adj)
    d[source] = 0
    q = deque([source])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if d[v] < 0:
                d[v] = d[u] + 1
                q.append(v)
    assert all(v >= 0 for v in d)
    return d


def exact_boolean_unsat(A):
    """Independent finite certificate, not a complexity bound."""
    n = len(A)
    _, _, basis = gf2_rref_basis(A)
    assert n == 63 and len(basis) == 14
    allone = (1 << n) - 1
    max_weight = 0
    for mask in range(1 << len(basis)):
        word = 0
        for i, b in enumerate(basis):
            if mask >> i & 1:
                word ^= b
        max_weight = max(max_weight, word.bit_count())
        # Every true Exact-One solution x yields k=1+x over F2,
        # with |k|=2n/3=42. This test is exact, exhaustive.
        assert word.bit_count() != 2*n//3
        assert (allone ^ word).bit_count() != n//3
    assert max_weight == 40
    return len(basis), max_weight


def main():
    A = tutte12_incidence()
    n = len(A)
    assert n == 63
    adj = levy_graph(A)
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))

    d, topweight = exact_boolean_unsat(A)
    assert (d, topweight) == (14, 40)

    pins_checked = 0
    shells_checked = 0
    for selected in range(n):
        distances = distance_shells(adj, n+selected)[n:]
        assert Counter(distances) == EXPECTED_PROFILE
        assert set(distances) == set(SHELL)
        x = [SHELL[t] for t in distances]
        assert all(Fraction(0) <= v <= Fraction(1) for v in x)
        assert sum(x) == Fraction(n,3)
        assert x[selected] == 1
        # Global exact Ax=1, not merely local consistency.
        assert all(
            sum((x[j] for j, v in enumerate(row) if v), Fraction(0))
            == 1 for row in A
        )
        shells_checked += 1
        incident = [i for i in range(n) if A[i][selected]]
        assert len(incident) == 3
        for check in incident:
            assert sorted(x[j] for j in range(n) if A[check][j]) == [
                Fraction(0), Fraction(0), Fraction(1)
            ]
            pins_checked += 1

    assert shells_checked == 63
    assert pins_checked == 189
    print("R5 universal LP-rounding attack: exact distance-shell control PASS")
    print("E123: n=63, connected cubic C4-free, GF2 dimension=14, max kernel weight=40 < 42")
    print("E123: all 189 first-check pinned LPs feasible over Q in [0,1]^63")
    print("distance shell profile: d=0:1 d=2:6 d=4:24 d=6:32")
    print("pin feasible vector: x=(1,0,1/2,1/4) on those shells")
    print("Therefore first-check LP extension support=111 at every check despite Boolean UNSAT")
    print("UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
