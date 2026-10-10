#!/usr/bin/env python3
from itertools import product

P = 3

v1 = (1,1,2,2)
v2 = (1,2,1,2)
v3 = (1,2,2,1)
B = (v1,v2,v3)


def add_scaled(y):
    return tuple(sum(y[j] * B[j][i] for j in range(3)) % P for i in range(4))


def forward(a):
    return tuple((-(a[0] + a[j])) % P for j in (1,2,3))


def rank_mod(rows):
    A = [list(r) for r in rows]
    r = 0
    for c in range(len(A[0])):
        pivot = next((i for i in range(r, len(A)) if A[i][c] % P), None)
        if pivot is None:
            continue
        A[r], A[pivot] = A[pivot], A[r]
        inv = 1 if A[r][c] % P == 1 else 2
        A[r] = [(inv*x) % P for x in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c] % P:
                f = A[i][c] % P
                A[i] = [(A[i][j] - f*A[r][j]) % P for j in range(len(A[0]))]
        r += 1
    return r


def main():
    assert rank_mod(B) == 3
    assert all(sum(v) % P == 0 for v in B)

    zero_sum = [a for a in product(range(P), repeat=4) if sum(a) % P == 0]
    assert len(zero_sum) == 27
    for a in zero_sum:
        y = forward(a)
        assert add_scaled(y) == a, (a, y, add_scaled(y))

    proper = [a for a in product((1,2), repeat=4) if sum(a) % P == 0]
    assert len(proper) == 6
    axis = {(s if j == 0 else 0, s if j == 1 else 0, s if j == 2 else 0)
            for j in range(3) for s in (1,2)}
    assert {forward(a) for a in proper} == axis

    for a in zero_sum:
        y = forward(a)
        is_proper = a in proper
        is_one_nonzero = sum(1 for z in y if z != 0) == 1
        assert is_proper == is_one_nonzero, (a, y)

    print("PASS: C4 EXACT2_4 is invertibly equivalent to ONE_NONZERO_3 over GF(3)")


if __name__ == "__main__":
    main()
