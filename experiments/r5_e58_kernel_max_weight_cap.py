#!/usr/bin/env python3
"""R5 E58 exact controls: Exact-One iff ker_F2(A) hits weight 2n/3.

For any binary square cubic carrier A (row/column weight 3):

  * A 1 = 1 over F_2, so the syndrome coset {x:Ax=1} is exactly 1+ker(A).
  * For k in ker(A), every integer row sum is 0 or 2.  If t2(k) is the
    number of rows of sum 2, then

        3 |k| = 2 t2(k) <= 2n.

    Hence every kernel codeword has |k| <= 2n/3.
  * x=1+k has weight n-|k|, so Exact-One exists iff a kernel codeword hits
    the absolute cap 2n/3.

The checker replays one SAT and one UNSAT n=9 permutation carrier.
"""
import itertools


def build_A(p, q):
    n = len(p)
    assert len(q) == n
    assert sorted(p) == list(range(n))
    assert sorted(q) == list(range(n))
    A = [[0] * n for _ in range(n)]
    for i in range(n):
        cols = (i, p[i], q[i])
        assert len(set(cols)) == 3
        for j in cols:
            A[i][j] = 1
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))
    return A


def matvec(A, x):
    return [sum(a * b for a, b in zip(row, x)) for row in A]


def all_binary(n):
    return itertools.product((0, 1), repeat=n)


def check_fixture(name, p, q, expect_exact, expect_kmax):
    A = build_A(p, q)
    n = len(A)

    # Canonical parity solution: A 1 = 1 mod 2.
    one = [1] * n
    assert all(v % 2 == 1 for v in matvec(A, one))

    kernel = []
    parity = []
    exact = []

    for bits in all_binary(n):
        x = list(bits)
        y = matvec(A, x)

        if all(v % 2 == 0 for v in y):
            assert all(v in (0, 2) for v in y)
            w = sum(x)
            t2 = sum(v == 2 for v in y)
            assert 3 * w == 2 * t2
            assert 3 * w <= 2 * n
            assert w % 2 == 0
            kernel.append((w, t2, tuple(x)))

        if all(v % 2 == 1 for v in y):
            parity.append((sum(x), tuple(x)))
            if y == [1] * n:
                exact.append(tuple(x))

    kmax = max(w for w, _, _ in kernel)
    d1 = min(w for w, _ in parity)

    # Coset duality x = 1 + k over F_2 is coordinatewise complement.
    assert d1 == n - kmax

    assert bool(exact) == expect_exact
    assert kmax == expect_kmax
    assert bool(exact) == (3 * kmax == 2 * n)

    print(
        f"{name}: n={n} dimcoset={len(parity)} "
        f"kmax={kmax} cap={2*n/3:g} d1={d1} exact={len(exact)}"
    )


def main():
    check_fixture(
        "SAT9",
        [2, 6, 7, 4, 5, 8, 1, 3, 0],
        [5, 8, 1, 6, 3, 2, 0, 4, 7],
        True,
        6,
    )

    check_fixture(
        "UNSAT9",
        [4, 0, 6, 7, 8, 1, 5, 2, 3],
        [8, 7, 1, 6, 3, 0, 4, 5, 2],
        False,
        4,
    )

    print("R5 E58 kernel maximum-weight cap: PASS")


if __name__ == "__main__":
    main()
