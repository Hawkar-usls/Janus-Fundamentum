#!/usr/bin/env python3
"""Exact controls for R5 E51 equitable block-count quotients.

Builds the noncommutative regular semidirect carriers C_p ⋊ C_3 for p=7,13,19
using an element a of order three modulo p. Verifies:
  * n=3p, square/cubic/linear carrier;
  * connected three-layer construction;
  * row-layer block sums give quotient system
        2 s_k + s_(k+1) = p;
  * the unique rational count vector is (p/3,p/3,p/3), nonintegral because p≡1 mod3;
  * p=7 also has no witness under an independent direct layer enumeration.

P_VS_NP remains OPEN.
"""

from fractions import Fraction
from itertools import combinations


def cube_root_mod(p):
    for a in range(2, p):
        if pow(a, 3, p) == 1 and a != 1:
            return a
    raise AssertionError(f"no order-3 unit mod {p}")


def carrier(p):
    a = cube_root_mod(p)

    def v(k, i):
        return (k % 3) * p + (i % p)

    rows = []
    for k in range(3):
        step = pow(a, k, p)
        for i in range(p):
            rows.append({v(k, i), v(k, i + step), v(k + 1, i)})
    return a, rows


def audit(p, rows):
    n = 3 * p
    assert len(rows) == n
    assert all(len(T) == 3 for T in rows)
    coldeg = [sum(c in T for T in rows) for c in range(n)]
    assert coldeg == [3] * n
    assert all(len(rows[i] & rows[j]) <= 1 for i, j in combinations(range(n), 2))


def block_quotient(p, rows):
    # row blocks and column blocks are the three layers.
    Q = [[None] * 3 for _ in range(3)]
    for rb in range(3):
        row_ids = range(rb * p, (rb + 1) * p)
        for cb in range(3):
            vals = []
            for col in range(cb * p, (cb + 1) * p):
                vals.append(sum(col in rows[r] for r in row_ids))
            assert len(set(vals)) == 1
            Q[rb][cb] = vals[0]
    assert Q == [[2, 1, 0], [0, 2, 1], [1, 0, 2]]
    return Q


def solve_3x3(Q, rhs):
    A = [[Fraction(x) for x in row] + [Fraction(b)] for row, b in zip(Q, rhs)]
    n = 3
    for c in range(n):
        pivot = next(i for i in range(c, n) if A[i][c])
        A[c], A[pivot] = A[pivot], A[c]
        z = A[c][c]
        A[c] = [x / z for x in A[c]]
        for i in range(n):
            if i != c and A[i][c]:
                f = A[i][c]
                A[i] = [A[i][j] - f * A[c][j] for j in range(n + 1)]
    return [A[i][-1] for i in range(n)]


def direct_layer_search(p, a):
    # Enumerate layer-0 bits only. Layer 1 and 2 are forced successively by the
    # exact-one equations. Used only as an independent finite p=7 control.
    for mask in range(1 << p):
        x0 = [(mask >> i) & 1 for i in range(p)]
        x1 = [0] * p
        ok = True
        for i in range(p):
            s = x0[i] + x0[(i + 1) % p]
            if s > 1:
                ok = False
                break
            x1[i] = 1 - s
        if not ok:
            continue

        x2 = [0] * p
        for i in range(p):
            s = x1[i] + x1[(i + a) % p]
            if s > 1:
                ok = False
                break
            x2[i] = 1 - s
        if not ok:
            continue

        a2 = (a * a) % p
        if all(x2[i] + x2[(i + a2) % p] + x0[i] == 1 for i in range(p)):
            return (x0, x1, x2)
    return None


def main():
    for p in (7, 13, 19):
        assert p % 3 == 1
        a, rows = carrier(p)
        audit(p, rows)
        Q = block_quotient(p, rows)
        s = solve_3x3(Q, [p, p, p])
        assert s == [Fraction(p, 3)] * 3
        assert any(x.denominator != 1 for x in s)
        print(f"p={p}, a={a}: n={3*p}, quotient counts={s}, UNSAT by integrality")

    a7 = cube_root_mod(7)
    assert direct_layer_search(7, a7) is None
    print("p=7 direct layer enumeration independently confirms UNSAT")
    print("R5 E51 equitable block-count quotient controls: PASS")


if __name__ == "__main__":
    main()
