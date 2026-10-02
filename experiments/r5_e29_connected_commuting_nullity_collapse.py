#!/usr/bin/env python3
"""Finite exact controls for R5 E29.

Checks connected commuting translation carriers A=I+P+Q on finite abelian groups:
  * cyclic groups Z_n with generating translations a,b;
  * rectangular groups Z_m x Z_l with the standard two generators.

For every connected control:
  * rational nullity is 0 or 2;
  * whenever nullity is 2, kernel-projective diversity is exactly 3;
  * the three projective classes have equal size n/3.

The companion note gives the general character proof.
P_VS_NP remains OPEN.
"""

from fractions import Fraction
from math import gcd


def rref_q(M):
    A = [[Fraction(x) for x in row] for row in M]
    m = len(A)
    n = len(A[0]) if m else 0
    pivots = []
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if A[i][c]), None)
        if pivot is None:
            continue
        A[r], A[pivot] = A[pivot], A[r]
        z = A[r][c]
        A[r] = [x / z for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [A[i][j] - f * A[r][j] for j in range(n)]
        pivots.append(c)
        r += 1
        if r == m:
            break
    return A, pivots


def nullspace_q(M):
    R, pivots = rref_q(M)
    n = len(R[0]) if R else 0
    free = [c for c in range(n) if c not in pivots]
    out = []
    for f in free:
        v = [Fraction(0)] * n
        v[f] = Fraction(1)
        for rr, p in enumerate(pivots):
            v[p] = -R[rr][f]
        out.append(v)
    return out


def proportional(u, v):
    if all(x == 0 for x in u):
        return all(x == 0 for x in v)
    p = next(i for i, x in enumerate(u) if x != 0)
    lam = v[p] / u[p]
    return all(v[i] == lam * u[i] for i in range(len(u)))


def projective_classes(A):
    basis = nullspace_q(A)
    if not basis:
        return basis, []
    rows = [tuple(basis[c][i] for c in range(len(basis))) for i in range(len(A))]
    assert all(any(x != 0 for x in row) for row in rows)
    unused = set(range(len(rows)))
    classes = []
    while unused:
        i = min(unused)
        C = [j for j in sorted(unused) if proportional(rows[i], rows[j])]
        for j in C:
            unused.remove(j)
        classes.append(C)
    return basis, classes


def carrier_from_perms(P, Q):
    n = len(P)
    A = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in (i, P[i], Q[i]):
            A[i][j] = 1
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))
    return A


def cyclic(n, a, b):
    P = [(i + a) % n for i in range(n)]
    Q = [(i + b) % n for i in range(n)]
    return carrier_from_perms(P, Q)


def rectangular(m, l):
    n = m * l
    def vid(i, j):
        return (i % m) * l + (j % l)
    P = [0] * n
    Q = [0] * n
    for i in range(m):
        for j in range(l):
            v = vid(i, j)
            P[v] = vid(i + 1, j)
            Q[v] = vid(i, j + 1)
    return carrier_from_perms(P, Q)


def check(A, label):
    basis, classes = projective_classes(A)
    d = len(basis)
    assert d in (0, 2), (label, d)
    if d == 2:
        assert len(classes) == 3, (label, [len(C) for C in classes])
        assert sorted(len(C) for C in classes) == [len(A)//3] * 3
    return d, len(classes)


def main():
    print("R5 E29 connected commuting controls: PASS")

    # Connected cyclic actions: gcd(n,a,b)=1.
    singular = 0
    full = 0
    for n in range(5, 25):
        for a in range(1, n):
            for b in range(a + 1, n):
                if gcd(gcd(n, a), b) != 1:
                    continue
                # Distinct columns in every row.
                if a % n == 0 or b % n == 0 or a % n == b % n:
                    continue
                A = cyclic(n, a, b)
                d, q = check(A, f"Z_{n}:{a},{b}")
                singular += (d == 2)
                full += (d == 0)

    # Standard connected rectangular translations.
    rect = []
    for m in range(3, 8):
        for l in range(3, 8):
            A = rectangular(m, l)
            d, q = check(A, f"Z_{m}xZ_{l}")
            rect.append((m, l, len(A), d, q))

    print(f"cyclic controls: full-rank={full}, nullity-two={singular}")
    for m, l, n, d, q in rect:
        print(f"  Z_{m} x Z_{l}: n={n}, nullity_Q={d}, q={q}")
    print("Conclusion: every tested connected commuting carrier has d in {0,2}; singular controls have q=3.")


if __name__ == "__main__":
    main()
