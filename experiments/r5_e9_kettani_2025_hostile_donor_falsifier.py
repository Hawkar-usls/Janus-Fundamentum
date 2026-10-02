#!/usr/bin/env python3
"""Executable falsifiers for the Kettani-2025 cubic monotone P=NP donor.

Checks two independent failures:
1. Fano 7_3: det(A)=24, unique rational solution is (1/3)1, but there is no Boolean Exact-One witness.
2. Finite triangular tori samples satisfy degree <=6, induced-K1,4-free, and >=3 triangles/vertex.
   The theorem note supplies the arbitrary-m unbounded-treewidth proof; this script regression-checks
   the local graph conditions on multiple m.

No third-party dependencies.
"""

from fractions import Fraction
from itertools import combinations, product


def fano_matrix():
    n = 7
    base = {0, 1, 3}
    return [[1 if ((j - i) % n) in base else 0 for j in range(n)] for i in range(n)]


def det_bareiss(M):
    A = [list(map(int, row)) for row in M]
    n = len(A)
    sign = 1
    prev = 1
    for k in range(n - 1):
        if A[k][k] == 0:
            swap = next((r for r in range(k + 1, n) if A[r][k] != 0), None)
            if swap is None:
                return 0
            A[k], A[swap] = A[swap], A[k]
            sign *= -1
        pivot = A[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                A[i][j] = (A[i][j] * pivot - A[i][k] * A[k][j]) // prev
        prev = pivot
        for i in range(k + 1, n):
            A[i][k] = 0
    return sign * A[-1][-1]


def matvec(A, x):
    return [sum(Fraction(a) * b for a, b in zip(row, x)) for row in A]


def exact_one(A, x):
    return all(v == 1 for v in matvec(A, x))


def validate_fano():
    A = fano_matrix()
    n = 7
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[r][c] for r in range(n)) == 3 for c in range(n))

    # Fano linearity: every pair of rows meets exactly once.
    supports = [{c for c, bit in enumerate(row) if bit} for row in A]
    for i, j in combinations(range(n), 2):
        assert len(supports[i] & supports[j]) == 1

    det = det_bareiss(A)
    assert abs(det) == 24, det

    rational = [Fraction(1, 3)] * n
    assert matvec(A, rational) == [Fraction(1)] * n

    witnesses = [bits for bits in product((0, 1), repeat=n) if exact_one(A, bits)]
    assert witnesses == [], witnesses

    return det


def triangular_torus(m):
    gens = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1))
    vertices = [(i, j) for i in range(m) for j in range(m)]
    adj = {}
    for v in vertices:
        adj[v] = {
            ((v[0] + di) % m, (v[1] + dj) % m)
            for di, dj in gens
        }
    return vertices, adj


def neighborhood_independence_number(N, adj):
    N = list(N)
    best = 0
    for k in range(len(N) + 1):
        for S in combinations(N, k):
            if all(v not in adj[u] for u, v in combinations(S, 2)):
                best = max(best, k)
    return best


def validate_triangular_torus(m):
    vertices, adj = triangular_torus(m)
    assert all(len(adj[v]) == 6 for v in vertices)

    for v in vertices:
        N = adj[v]
        # induced K1,4 centered at v exists iff N contains independent set of size 4
        assert neighborhood_independence_number(N, adj) == 3

        # number of triangles containing v equals number of edges within N(v)
        tri_count = sum(1 for u, w in combinations(N, 2) if w in adj[u])
        assert tri_count == 6

        # Verify that horizontal/vertical grid edges are contained in the torus graph.
        i, j = v
        if i + 1 < m:
            assert (i + 1, j) in adj[v]
        if j + 1 < m:
            assert (i, j + 1) in adj[v]

    return len(vertices)


def main():
    det = validate_fano()

    samples = []
    for m in range(5, 11):
        samples.append((m, validate_triangular_torus(m)))

    print("PASS: R5_E9_KETTANI_2025_HOSTILE_DONOR_FALSIFIER")
    print(f"Fano 7_3: det(A)={det}, unique rational x=(1/3)1, Boolean witnesses=0")
    print("Triangular torus samples m=5..10: degree=6, induced-K1,4-free, triangles/vertex=6")
    print(f"sample_sizes={samples}")
    print("The theorem note proves tw(T_m)>=tw(P_m square P_m)=m for arbitrary m>=5.")
    print("KETTANI_2025_DONOR=REJECTED; E8_D1=EMPTY; P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
