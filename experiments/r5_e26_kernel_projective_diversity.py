#!/usr/bin/env python3
"""Exact controls for R5 E26 kernel-projective diversity.

Checks the theorem that proportional kernel-row classes carry at most one free
Boolean bit after the R5 E18 projective rules, and that q free projective classes
give an exact O(2^q poly(n)) solver.

The toroidal R5 E10/E25 family with 3|k has nullity two but only three distinct
kernel row types, so its globally supported trades have constant description
complexity even though their support is Theta(n).

P_VS_NP remains OPEN.
"""

from fractions import Fraction
from itertools import product


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


def matvec(A, x):
    return [sum(a*b for a, b in zip(row, x)) for row in A]


def toroidal_matrix(k):
    n = k*k
    A = [[0] * n for _ in range(n)]

    def vid(i, j):
        return (i % k) * k + (j % k)

    for i in range(k):
        for j in range(k):
            r = vid(i, j)
            for v in (vid(i, j), vid(i+1, j), vid(i, j+1)):
                A[r][v] = 1
    return A


def kernel_rows(A):
    basis = nullspace_q(A)
    n = len(A[0])
    return [tuple(basis[c][i] for c in range(len(basis))) for i in range(n)]


def proportional_ratio(u, v):
    """Return lambda with v=lambda*u, or None if not proportional."""
    if all(x == 0 for x in u):
        return Fraction(0) if all(x == 0 for x in v) else None
    idx = next(i for i, x in enumerate(u) if x != 0)
    lam = v[idx] / u[idx]
    if all(v[i] == lam * u[i] for i in range(len(u))):
        return lam
    return None


def projective_classes(rows):
    unused = set(range(len(rows)))
    classes = []
    while unused:
        i = min(unused)
        u = rows[i]
        cls = []
        for j in sorted(unused):
            lam = proportional_ratio(u, rows[j])
            if lam is not None:
                cls.append((j, lam))
        for j, _ in cls:
            unused.remove(j)
        classes.append(cls)
    return classes


def class_allowed_states(rows, cls):
    """Allowed centered value of a representative in {-1,2}."""
    rep = cls[0][0]
    u = rows[rep]
    allowed = []
    for a in (-1, 2):
        ok = True
        for j, lam in cls:
            # rows[j] = lam * rows[rep], so y_j = lam*y_rep
            if lam * a not in (-1, 2):
                ok = False
                break
        if ok:
            allowed.append(a)
    return allowed


def exact_by_projective_classes(A):
    rows = kernel_rows(A)
    if not rows or len(rows[0]) == 0:
        return False, 0, 0

    classes = projective_classes(rows)
    free = []
    forced = {}
    for ci, cls in enumerate(classes):
        allowed = class_allowed_states(rows, cls)
        if not allowed:
            return False, len(classes), 0
        if len(allowed) == 1:
            forced[ci] = allowed[0]
        else:
            assert set(allowed) == {-1, 2}
            free.append(ci)

    class_of = {}
    ratio_to_rep = {}
    for ci, cls in enumerate(classes):
        for j, lam in cls:
            class_of[j] = ci
            ratio_to_rep[j] = lam

    for bits in product((-1, 2), repeat=len(free)):
        rep_value = dict(forced)
        rep_value.update(dict(zip(free, bits)))
        y = []
        for j in range(len(rows)):
            yj = ratio_to_rep[j] * rep_value[class_of[j]]
            if yj not in (-1, 2):
                break
            y.append(int(yj))
        else:
            if matvec(A, y) == [0] * len(A):
                x = [(v + 1) // 3 for v in y]
                if all(v in (0, 1) for v in x) and matvec(A, x) == [1] * len(A):
                    return True, len(classes), len(free)

    return False, len(classes), len(free)


def check_tori():
    rows = []
    for k in (3, 6, 9):
        A = toroidal_matrix(k)
        K = nullspace_q(A)
        assert len(K) == 2
        kr = kernel_rows(A)
        assert len(set(kr)) == 3
        sat, qproj, qfree = exact_by_projective_classes(A)
        assert sat
        assert qproj == 3
        assert qfree == 3
        rows.append((k, k*k, len(K), qproj, qfree))
    return rows


def main():
    rows = check_tori()
    print("R5 E26 kernel-projective diversity controls: PASS")
    for k, n, d, qproj, qfree in rows:
        print(
            f"k={k}: n={n}, nullity_Q={d}, projective_classes={qproj}, "
            f"free_classes={qfree}, exact states={2**qfree}"
        )
    print("E25 lesson: trade support can be 2n/3 while projective description uses q=3 bits.")


if __name__ == "__main__":
    main()
