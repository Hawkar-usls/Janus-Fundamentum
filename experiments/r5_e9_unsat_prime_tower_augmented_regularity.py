#!/usr/bin/env python3
"""Exact finite replay for the arbitrary-t augmented-regularity theorem.

The theorem is inductive and not proved by these finite runs.  The checker
verifies its algebraic invariants on the first four lifted levels.
"""
from __future__ import annotations


def zeros(n: int, m: int) -> list[list[int]]:
    return [[0] * m for _ in range(n)]


def seed_A0() -> list[list[int]]:
    rows = [
        (0,5,12),(1,7,9),(2,9,14),(3,10,11),(3,4,13),
        (1,5,10),(6,7,14),(2,3,7),(1,4,8),(0,6,9),
        (2,10,12),(5,11,13),(6,8,12),(0,8,13),(4,11,14),
    ]
    A = zeros(15, 15)
    for i, triple in enumerate(rows):
        for j in triple:
            A[i][j] = 1
    return A


def lift(A: list[list[int]], F: tuple[tuple[int,int], tuple[int,int]]) -> list[list[int]]:
    n = len(A)
    E = zeros(n, n)
    for i, j in F:
        assert A[i][j] == 1
        E[i][j] = 1
    out = zeros(2*n, 2*n)
    for i in range(n):
        for j in range(n):
            # Integer A-E and E; entries are still 0/1.
            out[i][j] = A[i][j] - E[i][j]
            out[i][n+j] = E[i][j]
            out[n+i][j] = E[i][j]
            out[n+i][n+j] = A[i][j] - E[i][j]
    return out


def gf2_rref(M: list[list[int]]) -> tuple[list[list[int]], list[int]]:
    A = [[x & 1 for x in row] for row in M]
    m = len(A)
    n = len(A[0]) if m else 0
    pivots: list[int] = []
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if A[i][c]), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        for i in range(m):
            if i != r and A[i][c]:
                A[i] = [a ^ b for a, b in zip(A[i], A[r])]
        pivots.append(c)
        r += 1
        if r == m:
            break
    return A, pivots


def gf2_rank(M: list[list[int]]) -> int:
    return len(gf2_rref(M)[1])


def gf2_nullspace(M: list[list[int]]) -> list[list[int]]:
    R, pivots = gf2_rref(M)
    n = len(R[0]) if R else len(M[0])
    free = [j for j in range(n) if j not in pivots]
    basis: list[list[int]] = []
    for f in free:
        x = [0] * n
        x[f] = 1
        for row in range(len(pivots)-1, -1, -1):
            p = pivots[row]
            s = 0
            for j in free:
                s ^= (R[row][j] & x[j])
            x[p] = s
        basis.append(x)
    return basis


def mat_vec(A: list[list[int]], x: list[int]) -> list[int]:
    return [sum(a*b for a, b in zip(row, x)) & 1 for row in A]


def block_double_basis(K: list[list[int]]) -> list[list[int]]:
    n = len(K[0])
    out: list[list[int]] = []
    for v in K:
        out.append(v + [0]*n)
    for v in K:
        out.append([0]*n + v)
    return out


def verify_augmented_dual_network_support(A: list[list[int]], K: list[list[int]]) -> None:
    n = len(A)
    k = len(K)
    assert k % 2 == 0

    # H rows: kernel rows extended by zero on e_b; global (1,...,1,1).
    H = [v + [0] for v in K] + [[1]*(n+1)]
    Aug = [row + [1] for row in A]

    # Every H row is orthogonal to every row of [A|1].
    for h in H:
        for row in Aug:
            assert sum(a*b for a, b in zip(h, row)) % 2 == 0

    assert gf2_rank(H) == k + 1
    root = k

    # Every original column is root plus a subset of one local two-row block.
    for j in range(n):
        support = {i for i in range(k+1) if H[i][j]}
        assert root in support
        local = support - {root}
        blocks = {i // 2 for i in local}
        assert len(blocks) <= 1, (j, support)
        assert len(local) <= 2

    # The distinguished syndrome column is exactly the root column.
    support_b = {i for i in range(k+1) if H[i][n]}
    assert support_b == {root}


def main() -> None:
    A0 = seed_A0()
    A1 = lift(A0, ((0,12),(2,9)))

    K1 = gf2_nullspace(A1)
    assert len(K1) == 2
    assert all(v[5] == 0 and v[1] == 0 for v in K1)

    # Bind to the displayed theorem basis up to basis choice: exact supports from
    # the frozen RREF are not required, only full dimension and zero coordinates.
    assert all(mat_vec(A1, v) == [0]*len(A1) for v in K1)

    A = A1
    K = K1
    F = ((0,5),(1,1))

    for t in range(1, 5):
        n = len(A)
        expected_k = 1 << t
        K_exact = gf2_nullspace(A)
        assert len(K_exact) == expected_k, (t, len(K_exact), expected_k)
        assert len(K) == expected_k
        assert gf2_rank(K) == expected_k
        assert all(mat_vec(A, v) == [0]*n for v in K)

        j1, j2 = F[0][1], F[1][1]
        assert all(v[j1] == 0 and v[j2] == 0 for v in K)

        # The recursive basis is a complete basis, not just a kernel subspace.
        assert gf2_rank(K + K_exact) == expected_k

        verify_augmented_dual_network_support(A, K)

        print(
            f"t={t} n={n} nu_F2={expected_k} augmented_dual_rank={expected_k+1} "
            f"distinguished=({j1},{j2}) NETWORK_SUPPORT_PASS"
        )

        if t < 4:
            old_n = n
            A = lift(A, F)
            K = block_double_basis(K)
            # Upper-right crossed copies of the old distinguished incidences.
            F = ((F[0][0], old_n + F[0][1]),
                 (F[1][0], old_n + F[1][1]))

    print("Prime-tower augmented-regularity finite replay: PASS")
    print("Scientific ceiling: arbitrary-t regularity is proved symbolically in the theorem; P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
