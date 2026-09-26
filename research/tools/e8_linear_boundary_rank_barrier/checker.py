#!/usr/bin/env python3
"""Independent finite replay for the E8 equality-interface rank barrier.

This checker is not the theorem proof.  It verifies the frozen construction for
small k and multiple fields, and checks the exact O(k)-size 3-CNF encoding.
"""

from itertools import product


def eq_cnf_value(a, b):
    assert len(a) == len(b)
    # (¬x_i ∨ y_i ∨ y_i) ∧ (x_i ∨ ¬y_i ∨ ¬y_i)
    for x, y in zip(a, b):
        c1 = (not x) or y or y
        c2 = x or (not y) or (not y)
        if not (c1 and c2):
            return 0
    return 1


def matrix_for_k(k):
    assn = list(product((0, 1), repeat=k))
    return [[eq_cnf_value(a, b) for b in assn] for a in assn]


def rank_mod_p(matrix, p):
    a = [[x % p for x in row] for row in matrix]
    rows = len(a)
    cols = len(a[0]) if rows else 0
    r = 0
    for c in range(cols):
        pivot = next((i for i in range(r, rows) if a[i][c] % p), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        inv = pow(a[r][c], -1, p)
        a[r] = [(v * inv) % p for v in a[r]]
        for i in range(rows):
            if i != r and a[i][c] % p:
                factor = a[i][c] % p
                a[i] = [(u - factor * v) % p for u, v in zip(a[i], a[r])]
        r += 1
        if r == rows:
            break
    return r


def assert_identity(m):
    n = len(m)
    for i, row in enumerate(m):
        assert len(row) == n
        for j, v in enumerate(row):
            assert v == int(i == j), (i, j, v)


def main():
    fields = (2, 3, 5, 7, 101)
    receipt = []
    for k in range(1, 9):
        m = matrix_for_k(k)
        n = 1 << k
        assert len(m) == n
        assert_identity(m)
        ranks = {p: rank_mod_p(m, p) for p in fields}
        assert all(r == n for r in ranks.values()), (k, ranks)
        receipt.append((k, n, ranks))

    print("E8_LINEAR_BOUNDARY_RANK_BARRIER finite replay: PASS")
    print("3-CNF encoding: 2k clauses; compatibility matrix: I_(2^k)")
    for k, n, ranks in receipt:
        print(f"k={k:2d} dimension={n:4d} ranks={ranks}")
    print("NOTE: finite replay supports construction only; symbolic rank proof carries theorem scope.")


if __name__ == "__main__":
    main()
