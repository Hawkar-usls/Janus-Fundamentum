#!/usr/bin/env python3
"""Exact regression for the linear-cubic trace/rank theorem LCT-1."""

from fractions import Fraction
from math import floor


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
        for i in range(r + 1, m):
            if a[i][c]:
                z = a[i][c]
                a[i] = [a[i][j] - z * a[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def cyclic_n3(n):
    # Lines {i,i+1,i+3}; for n>=7 their six directed differences are distinct.
    A = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in (i, (i + 1) % n, (i + 3) % n):
            A[i][j] = 1
    return A


def transpose(A):
    return [list(x) for x in zip(*A)]


def matmul(A, B):
    BT = transpose(B)
    return [[sum(x * y for x, y in zip(row, col)) for col in BT] for row in A]


def is_linear_cubic(A):
    n = len(A)
    if any(len(row) != n or sum(row) != 3 for row in A):
        return False
    AT = transpose(A)
    if any(sum(col) != 3 for col in AT):
        return False
    # Both primal and dual J2-free checks.
    for rows in (A, AT):
        for i in range(n):
            for j in range(i + 1, n):
                if sum(x * y for x, y in zip(rows[i], rows[j])) > 1:
                    return False
    return True


def valid_switch(A, r1, r2, c1, c2):
    if not (A[r1][c1] and A[r2][c2] and not A[r1][c2] and not A[r2][c1]):
        return None
    B = [row[:] for row in A]
    B[r1][c1] = B[r2][c2] = 0
    B[r1][c2] = B[r2][c1] = 1
    return B if is_linear_cubic(B) else None


def perturb(A, limit=4):
    B = [row[:] for row in A]
    n = len(B)
    done = 0
    for r1 in range(n):
        for r2 in range(r1 + 1, n):
            for c1 in range(n):
                if not B[r1][c1]:
                    continue
                for c2 in range(n):
                    C = valid_switch(B, r1, r2, c1, c2)
                    if C is not None:
                        B = C
                        done += 1
                        break
                if done and done <= limit and B is not A:
                    break
            if done >= limit:
                return B
        if done >= limit:
            return B
    return B


def check(A, tag):
    assert is_linear_cubic(A), tag
    n = len(A)
    B = matmul(transpose(A), A)

    tr = sum(B[i][i] for i in range(n))
    tr2 = sum(B[i][j] * B[j][i] for i in range(n) for j in range(n))
    assert tr == 3 * n, (tag, tr)
    assert tr2 == 15 * n, (tag, tr2)
    assert all(sum(B[i][j] for j in range(n)) == 9 for i in range(n)), tag

    r = rank_q(A)
    nu = n - r
    refined = Fraction(2 * n * (n - 7), 5 * n - 27)
    assert Fraction(nu, 1) <= refined, (tag, n, r, nu, refined)
    assert nu <= floor(refined), (tag, nu, floor(refined))
    assert 5 * r >= 3 * n, (tag, r, n)
    return n, r, nu, floor(refined)


def main():
    rows = []
    for n in range(7, 41):
        A = cyclic_n3(n)
        rows.append(check(A, f"cyclic-{n}"))
        C = perturb(A, limit=min(5, max(1, n // 8)))
        rows.append(check(C, f"switched-{n}"))

    # Fano plane / C3(7): refined theorem forces nonsingularity.
    n, r, nu, bd = check(cyclic_n3(7), "fano-control")
    assert (n, r, nu, bd) == (7, 7, 0, 0)

    print("LCT-1 exact regression: PASS")
    print(f"instances checked = {len(rows) + 1}")
    print(f"largest n = {max(x[0] for x in rows)}")
    print(f"largest observed nullity = {max(x[2] for x in rows)}")
    print("identities: tr(A^T A)=3n, tr((A^T A)^2)=15n, (A^T A)1=9*1")


if __name__ == "__main__":
    main()
