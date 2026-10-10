#!/usr/bin/env python3
"""Exact regression for the AF3 model-count modulo-3 barrier."""

from itertools import combinations, product

ROWS = [
    (1,3,5),(2,3,8),(0,1,6),(0,5,8),(3,4,6),
    (6,7,8),(4,5,7),(1,2,7),(0,2,4),
]
N = 9


def matrix():
    return [[int(j in row) for j in range(N)] for row in ROWS]


def rank_mod(M, p=3):
    A = [[v % p for v in row] for row in M]
    r = 0
    for c in range(len(A[0])):
        q = next((i for i in range(r, len(A)) if A[i][c]), None)
        if q is None:
            continue
        A[r], A[q] = A[q], A[r]
        inv = pow(A[r][c], -1, p)
        A[r] = [(v * inv) % p for v in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [(A[i][j] - f * A[r][j]) % p for j in range(len(A[0]))]
        r += 1
    return r


def connected_linear_cubic(A):
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(N)) == 3 for j in range(N))
    supp = [{j for j, x in enumerate(row) if x} for row in A]
    assert all(len(supp[i] & supp[j]) <= 1 for i, j in combinations(range(N), 2))
    adj = [[] for _ in range(2 * N)]
    for i, S in enumerate(supp):
        for j in S:
            adj[i].append(N + j)
            adj[N + j].append(i)
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    assert len(seen) == 2 * N


def matvec(A, x, mod=None):
    y = [sum(a * b for a, b in zip(row, x)) for row in A]
    return [v % mod for v in y] if mod else y


def main():
    A = matrix()
    connected_linear_cubic(A)

    witnesses = []
    for S in combinations(range(N), N // 3):
        x = [int(i in S) for i in range(N)]
        if matvec(A, x) == [1] * N:
            witnesses.append(S)
    assert witnesses == [(0,3,7), (1,4,8), (2,5,6)]
    assert len(witnesses) == 3
    assert len(witnesses) % 3 == 0

    assert rank_mod(A, 3) == 6
    affine = []
    nowhere = []
    for r in product(range(3), repeat=N):
        if matvec(A, r, 3) == [1] * N:
            affine.append(r)
            if all(r):
                nowhere.append(r)
    assert len(affine) == 27
    assert nowhere == [
        (1,1,2,1,1,2,2,1,1),
        (1,2,1,1,2,1,1,1,2),
        (2,1,1,2,1,1,1,2,1),
    ]

    decoded = []
    for r in nowhere:
        x = tuple(i for i, v in enumerate(r) if v == 2)
        assert x in witnesses
        decoded.append(x)
    assert sorted(decoded) == witnesses

    # Augmented full-support codewords: (r,1) and 2*(r,1).
    Atilde = [row + [2] for row in A]  # [A|-1] over F3
    full = []
    for c in product(range(3), repeat=N + 1):
        if all(c) and matvec(Atilde, c, 3) == [0] * N:
            full.append(c)
    assert len(full) == 6
    assert len(full) % 3 == 0

    print('PASS_AF3_MODEL_COUNT_MOD3_LINEAR_CUBIC_BARRIER')
    print('n=9 rank_F3=6 affine=27 nowhere_zero=3 exactone=3 augmented_full_support=6')
    print('W_mod3=0 while SAT=True')
    print('E8_D1=EMPTY P_VS_NP=OPEN')


if __name__ == '__main__':
    main()
