#!/usr/bin/env python3
"""Exact regression for GKZ3-1: graphic-kernel Z3 phase solver island."""

from collections import deque
from fractions import Fraction


def rank_q(mat):
    a = [[Fraction(x) for x in row] for row in mat]
    m = len(a)
    n = len(a[0]) if m else 0
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if a[i][c]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        z = a[r][c]
        a[r] = [v / z for v in a[r]]
        for i in range(m):
            if i != r and a[i][c]:
                z = a[i][c]
                a[i] = [a[i][j] - z * a[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def phase_solve(num_vertices, edges):
    """Solve phi(v)-phi(u)=-1 mod 3 for each oriented edge u->v."""
    adj = [[] for _ in range(num_vertices)]
    for ei, (u, v) in enumerate(edges):
        adj[u].append((v, -1, ei))
        adj[v].append((u, +1, ei))

    phi = [None] * num_vertices
    for root in range(num_vertices):
        if phi[root] is not None:
            continue
        phi[root] = 0
        q = deque([root])
        while q:
            u = q.popleft()
            for v, delta, ei in adj[u]:
                want = (phi[u] + delta) % 3
                if phi[v] is None:
                    phi[v] = want
                    q.append(v)
                elif phi[v] != want:
                    return None, (u, v, ei)
    return phi, None


def witness_from_phase(phi, edges):
    beta = list(phi)  # canonical representatives 0,1,2
    x = []
    for u, v in edges:
        diff = beta[v] - beta[u]
        assert diff in (-1, 2)
        x.append((diff + 1) // 3)
        assert x[-1] in (0, 1)
    return x


def matvec(A, x):
    return [sum(a * b for a, b in zip(row, x)) for row in A]


def positive_j3_control():
    # A=J3 has ker={y:sum y=0}, exactly the coboundary space of a directed 3-cycle.
    A = [[1, 1, 1] for _ in range(3)]
    edges = [(0, 1), (1, 2), (2, 0)]
    H = [
        [-1, 1, 0],
        [0, -1, 1],
        [1, 0, -1],
    ]
    assert 3 - rank_q(A) == 2
    assert rank_q(H) == 2
    # A H = 0.
    for i in range(3):
        for j in range(3):
            assert sum(A[i][k] * H[k][j] for k in range(3)) == 0

    phi, conflict = phase_solve(3, edges)
    assert conflict is None and phi is not None
    x = witness_from_phase(phi, edges)
    assert x == [1, 0, 0]
    assert matvec(A, x) == [1, 1, 1]
    return phi, x


def paley11_negative_control():
    q = 11
    residues = {1, 3, 4, 5, 9}
    C = []
    d = 1
    while d not in C:
        C.append(d)
        d = (-2 * d) % q
    assert set(C) == residues

    variables = [(a, d) for d in C for a in range(q)]
    idx = {e: i for i, e in enumerate(variables)}
    edges = [(a, (a + d) % q) for a, d in variables]
    n = len(variables)

    A = [[0] * n for _ in range(n)]
    ri = 0
    for d in C:
        nd = (-2 * d) % q
        for a in range(q):
            for j in (
                idx[(a, d)],
                idx[((a + d) % q, d)],
                idx[((a + 2 * d) % q, nd)],
            ):
                A[ri][j] = 1
            ri += 1

    # Exact kernel equality: rank(A)=45 and root incidence has rank 10.
    assert rank_q(A) == 45
    H = [[0] * q for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        H[i][u] = -1
        H[i][v] = 1
    assert rank_q(H) == 10
    for i in range(n):
        # spot/full AH handled row-wise below
        pass
    for row in A:
        coeff = [0] * q
        for e, aij in enumerate(row):
            if aij:
                u, v = edges[e]
                coeff[u] -= 1
                coeff[v] += 1
        assert coeff == [0] * q

    phi, conflict = phase_solve(q, edges)
    assert phi is None and conflict is not None
    return conflict


def main():
    phi, x = positive_j3_control()
    conflict = paley11_negative_control()
    print("GKZ3-1 exact regression: PASS")
    print(f"J3 positive phase = {phi}, witness = {x}")
    print(f"Paley11 negative phase conflict edge = {conflict}")
    print("soundness/completeness reconstruction controls = PASS")


if __name__ == "__main__":
    main()
