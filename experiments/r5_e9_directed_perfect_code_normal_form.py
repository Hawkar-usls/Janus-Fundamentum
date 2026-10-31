#!/usr/bin/env python3
"""Regression checker for the exact directed perfect-code normal form."""

from itertools import product


def matrix_from_perms(p, q):
    n = len(p)
    A = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in (i, p[i], q[i]):
            A[i][j] = 1
    return A


def exact_one(A, x):
    return all(sum(A[i][j] * x[j] for j in range(len(x))) == 1 for i in range(len(A)))


def directed_perfect_code(p, q, x):
    return all(x[i] + x[p[i]] + x[q[i]] == 1 for i in range(len(x)))


def validate_two_in_two_out(p, q):
    n = len(p)
    assert sorted(p) == list(range(n))
    assert sorted(q) == list(range(n))
    assert all(len({i, p[i], q[i]}) == 3 for i in range(n))
    indeg = [0] * n
    for i in range(n):
        indeg[p[i]] += 1
        indeg[q[i]] += 1
    assert indeg == [2] * n


def main():
    # Frozen primitive nullity-2 carrier already present in R5 E9.
    p = [9,4,6,1,10,8,7,2,0,5,11,3]
    q = [3,8,4,5,0,11,10,1,7,6,9,2]
    validate_two_in_two_out(p, q)
    A = matrix_from_perms(p, q)

    exact = []
    codes = []
    for x in product((0, 1), repeat=len(p)):
        if exact_one(A, x):
            exact.append(x)
        if directed_perfect_code(p, q, x):
            codes.append(x)
    assert exact == codes
    assert len(exact) == 1
    selected = tuple(i for i, b in enumerate(exact[0]) if b)
    assert selected == (0, 1, 6, 11)

    # Explicitly demonstrate why ordinary kernel semantics is weaker.
    # On a local triple x_i=0, successor pattern (1,1) would satisfy
    # 'at least one selected successor' but violates Exact-One.
    assert (0 + 1 + 1) != 1
    assert (1 or 1)

    print('PASS R5_E9_DIRECTED_PERFECT_CODE_NORMAL_FORM')
    print('outdegree = indegree = 2')
    print('Exact-One witnesses = directed perfect codes =', len(exact))
    print('selected =', selected)
    print('ORDINARY_DIGRAPH_KERNEL_SUBSTITUTION = FORBIDDEN')
    print('P_VS_NP = OPEN')


if __name__ == '__main__':
    main()
