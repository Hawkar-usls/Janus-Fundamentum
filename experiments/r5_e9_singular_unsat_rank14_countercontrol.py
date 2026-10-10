#!/usr/bin/env python3
"""Exact regression for the singular linear-cubic UNSAT countercontrol."""

from fractions import Fraction
from itertools import combinations

P = [5,7,9,10,3,1,14,2,4,6,12,13,8,0,11]
Q = [12,9,14,11,13,10,7,3,1,0,2,5,6,8,4]
G = [1,4,1,1,-2,-2,1,-2,-2,-2,-2,1,1,1,1]


def matrix():
    n = len(P)
    A = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in (i, P[i], Q[i]):
            A[i][j] = 1
    return A


def rank_q(M):
    A = [[Fraction(v) for v in row] for row in M]
    m = len(A)
    n = len(A[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if A[i][c]), None)
        if pivot is None:
            continue
        A[r], A[pivot] = A[pivot], A[r]
        pv = A[r][c]
        A[r] = [z / pv for z in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [A[i][j] - f * A[r][j] for j in range(n)]
        r += 1
    return r


def matvec(A, x):
    return [sum(a*b for a,b in zip(row,x)) for row in A]


def connected(rows):
    n = len(rows)
    adj = [[] for _ in range(2*n)]
    for i,row in enumerate(rows):
        for j in row:
            adj[i].append(n+j)
            adj[n+j].append(i)
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen) == 2*n


def witness_count(rows):
    # Any cubic exact-one witness has weight n/3 = 5.
    n = len(rows)
    count = 0
    for S_tuple in combinations(range(n), n//3):
        S = set(S_tuple)
        if all(len(row & S) == 1 for row in rows):
            count += 1
    return count


def main():
    n = 15
    assert sorted(P) == list(range(n))
    assert sorted(Q) == list(range(n))
    A = matrix()
    rows = [{j for j,v in enumerate(A[i]) if v} for i in range(n)]

    assert all(len(r) == 3 for r in rows)
    coldeg = [sum(A[i][j] for i in range(n)) for j in range(n)]
    assert set(coldeg) == {3}

    for i in range(n):
        for j in range(i):
            assert len(rows[i] & rows[j]) <= 1
    assert connected(rows)

    rank = rank_q(A)
    assert rank == 14
    assert matvec(A, G) == [0] * n
    assert n - rank == 1

    # If lambda*G were {-1,2}-valued, a G=1 coordinate forces
    # lambda in {-1,2}; the G=4 coordinate then becomes -4 or 8.
    assert 1 in G and 4 in G and -2 in G
    for lam in (-1, 2):
        assert any(lam * v not in (-1, 2) for v in G)

    # Finite replay only; theorem-level UNSAT is the 1D-kernel argument above.
    count = witness_count(rows)
    assert count == 0

    print("PASS R5_E9_SINGULAR_UNSAT_RANK14_COUNTERCONTROL")
    print("n = 15")
    print("rank_Q = 14")
    print("nullity_Q = 1")
    print("Levi_connected = true")
    print("linear_cubic = true")
    print("ExactOne_witness_count = 0")
    print("SINGULAR_IFF_SAT = FALSIFIED")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
