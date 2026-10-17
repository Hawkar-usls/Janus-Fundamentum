#!/usr/bin/env python3
"""Regression checker for the R5 E9 commuting two-permutation exact terminal.

Verifies two exact controls:
- cyclic Fano 7_3: commuting, connected, linear, nullity 0, UNSAT;
- TD(3,3) / affine 9_3: commuting, connected, linear, nullity 2,
  exactly three Exact-One witnesses, recovered by Z3 propagation.

Dependency-free; exact rational rank via fractions.Fraction.
"""

from collections import deque
from fractions import Fraction
from itertools import product


def inverse_perm(p):
    inv = [-1] * len(p)
    for i, j in enumerate(p):
        inv[j] = i
    assert all(v >= 0 for v in inv)
    return inv


def compose(p, q):
    return [p[q[i]] for i in range(len(p))]


def commute(p, q):
    return compose(p, q) == compose(q, p)


def orbit(p, q, start=0):
    pinv, qinv = inverse_perm(p), inverse_perm(q)
    gens = (p, q, pinv, qinv)
    seen = {start}
    dq = deque([start])
    while dq:
        i = dq.popleft()
        for g in gens:
            j = g[i]
            if j not in seen:
                seen.add(j)
                dq.append(j)
    return seen


def matrix_from_perms(p, q):
    n = len(p)
    A = [[0] * n for _ in range(n)]
    for i in range(n):
        support = [i, p[i], q[i]]
        assert len(set(support)) == 3
        for j in support:
            A[i][j] = 1
    return A


def validate_cubic_linear(A):
    n = len(A)
    assert all(len(row) == n for row in A)
    row_supports = []
    for row in A:
        s = [j for j, bit in enumerate(row) if bit]
        assert len(s) == 3
        row_supports.append(s)
    col_deg = [sum(A[i][j] for i in range(n)) for j in range(n)]
    assert col_deg == [3] * n

    seen_pairs = set()
    for s in row_supports:
        for a in range(3):
            for b in range(a + 1, 3):
                pair = tuple(sorted((s[a], s[b])))
                assert pair not in seen_pairs
                seen_pairs.add(pair)


def rank_q(M):
    a = [[Fraction(v) for v in row] for row in M]
    m = len(a)
    n = len(a[0]) if m else 0
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if a[i][c] != 0), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        pv = a[r][c]
        a[r] = [v / pv for v in a[r]]
        for i in range(m):
            if i != r and a[i][c] != 0:
                f = a[i][c]
                a[i] = [a[i][j] - f * a[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def exact_one(A, x):
    return all(sum(row[j] * x[j] for j in range(len(x))) == 1 for row in A)


def enumerate_witnesses(A):
    n = len(A)
    return [x for x in product((0, 1), repeat=n) if exact_one(A, x)]


def propagate_colors(p, q, orientation=1):
    """Return a Z3 coloring or None.

    orientation=1 imposes p:+1, q:+2.
    orientation=-1 imposes p:+2, q:+1.
    """
    n = len(p)
    pinv, qinv = inverse_perm(p), inverse_perm(q)
    if orientation == 1:
        steps = ((p, 1), (q, 2), (pinv, 2), (qinv, 1))
    else:
        steps = ((p, 2), (q, 1), (pinv, 1), (qinv, 2))

    color = [None] * n
    color[0] = 0
    dq = deque([0])
    while dq:
        i = dq.popleft()
        for g, delta in steps:
            j = g[i]
            want = (color[i] + delta) % 3
            if color[j] is None:
                color[j] = want
                dq.append(j)
            elif color[j] != want:
                return None
    if any(c is None for c in color):
        return None
    return color


def witnesses_from_coloring(color):
    out = []
    for target in range(3):
        out.append(tuple(1 if c == target else 0 for c in color))
    return out


def check_fano():
    n = 7
    p = [(i + 1) % n for i in range(n)]
    q = [(i + 3) % n for i in range(n)]
    assert commute(p, q)
    assert len(orbit(p, q)) == n
    A = matrix_from_perms(p, q)
    validate_cubic_linear(A)
    r = rank_q(A)
    ws = enumerate_witnesses(A)
    assert r == 7
    assert n - r == 0
    assert len(ws) == 0
    assert propagate_colors(p, q, 1) is None
    assert propagate_colors(p, q, -1) is None
    return {"name": "FANO_7_3", "rank": r, "nullity": n - r, "witnesses": len(ws)}


def check_td33():
    pts = [(x, y) for x in range(3) for y in range(3)]
    idx = {g: i for i, g in enumerate(pts)}
    p = [idx[((x + 1) % 3, y)] for x, y in pts]
    q = [idx[(x, (y + 1) % 3)] for x, y in pts]
    n = len(pts)
    assert commute(p, q)
    assert len(orbit(p, q)) == n
    A = matrix_from_perms(p, q)
    validate_cubic_linear(A)
    r = rank_q(A)
    ws = enumerate_witnesses(A)
    assert r == 7
    assert n - r == 2
    assert len(ws) == 3

    c1 = propagate_colors(p, q, 1)
    c2 = propagate_colors(p, q, -1)
    assert c1 is not None
    assert c2 is not None

    from_c1 = set(witnesses_from_coloring(c1))
    from_c2 = set(witnesses_from_coloring(c2))
    brute = set(ws)
    assert from_c1 == brute
    assert from_c2 == brute
    assert all(exact_one(A, x) for x in from_c1)
    return {"name": "TD33_9_3", "rank": r, "nullity": n - r, "witnesses": len(ws)}


def main():
    fano = check_fano()
    td33 = check_td33()
    print("PASS R5_E9_COMMUTING_TWO_PERM_EXACT_TERMINAL")
    print(fano)
    print(td33)
    print("verified_nullity_dichotomy_controls = {0,2}")
    print("verified_sat_witness_count_for_nullity2_control = 3")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
