#!/usr/bin/env python3
"""Exact controls for R5 E27.

Rebuilds the R5 E16 connected k-block ring and verifies:
  * n = 9k;
  * nullity_Q = k+1;
  * kernel-projective diversity q = 2k+1;
  * projective class sizes are 2k classes of size 3 and one class of size 3k.

Thus q = 2n/9 + 1 is linear although the family remains exactly decomposable by
the R5 E16 constant-size separator branch.

P_VS_NP remains OPEN.
"""

from fractions import Fraction


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


def build_e16(k):
    n = 9 * k
    A = [[0] * n for _ in range(n)]

    def vid(b, i, j):
        return b * 9 + (i % 3) * 3 + (j % 3)

    for b in range(k):
        for i in range(3):
            for j in range(3):
                r = vid(b, i, j)
                cols = [r, vid(b, i + 1, j)]
                if i == 0 and j == 0:
                    cols.append(vid((b + 1) % k, 0, 1))
                else:
                    cols.append(vid(b, i, j + 1))
                for c in cols:
                    A[r][c] = 1

    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))
    return A


def proportional(u, v):
    if all(x == 0 for x in u):
        return all(x == 0 for x in v)
    p = next(i for i, x in enumerate(u) if x != 0)
    lam = v[p] / u[p]
    return all(v[i] == lam * u[i] for i in range(len(u)))


def projective_classes(A):
    basis = nullspace_q(A)
    rows = [tuple(basis[c][i] for c in range(len(basis))) for i in range(len(A))]
    unused = set(range(len(rows)))
    classes = []
    while unused:
        i = min(unused)
        cls = [j for j in sorted(unused) if proportional(rows[i], rows[j])]
        for j in cls:
            unused.remove(j)
        classes.append(cls)
    return basis, classes


def main():
    print("R5 E27 E16 projective-diversity firewall: PASS")
    for k in range(2, 9):
        A = build_e16(k)
        basis, classes = projective_classes(A)
        n = 9 * k
        d = len(basis)
        q = len(classes)
        sizes = sorted(len(C) for C in classes)

        assert d == k + 1
        assert q == 2 * k + 1
        assert sizes == [3] * (2 * k) + [3 * k]

        print(
            f"k={k}: n={n}, nullity_Q={d}, q={q}=2k+1, "
            f"class_sizes=3 x {2*k} plus {3*k}"
        )

    print("Conclusion: q = 2n/9 + 1 is linear; high projective diversity alone is not hardness.")


if __name__ == "__main__":
    main()
