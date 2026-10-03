#!/usr/bin/env python3
"""R5 E56 exact controls: binary syndrome weight floor for square cubic Exact-One.

For any binary n x n incidence matrix A with every row and column of weight 3,
and any Boolean vector x satisfying A x = 1 (mod 2), every row has integer
sum 1 or 3. If t3(x) is the number of rows with sum 3, then

    3 |x| = n + 2 t3(x).

Hence |x| >= n/3, and equality holds iff A x = 1 over the integers, i.e.
iff x is an Exact-One solution.

For A = I + P + Q this is the permutation form

    S XOR P(S) XOR Q(S) = V,

with every point covered either once or three times. The triple-covered set is
T = S intersect P(S) intersect Q(S), and

    3 |S| = n + 2 |T|.

Exact-One is therefore equivalent to reaching the global parity-coset weight
floor n/3, or equivalently to driving the triple-overlap count to zero.
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


def image_set(p, S):
    return {p[i] for i in S}


def check_fixture(name, p, q, expect_exact):
    A = build_A(p, q)
    n = len(p)
    parity = []
    exact = []

    pinv = [0] * n
    qinv = [0] * n
    for i, j in enumerate(p):
        pinv[j] = i
    for i, j in enumerate(q):
        qinv[j] = i

    for x in itertools.product((0, 1), repeat=n):
        y = matvec(A, x)
        if all(v % 2 == 1 for v in y):
            w = sum(x)
            t3 = sum(v == 3 for v in y)
            assert all(v in (1, 3) for v in y)
            assert 3 * w == n + 2 * t3

            is_exact = all(v == 1 for v in y)
            assert is_exact == (t3 == 0)
            assert is_exact == (3 * w == n)

            # Row convention A_i={i,p(i),q(i)} means the three coverage sets
            # on row coordinates are S, p^{-1}(S), q^{-1}(S).
            S = {i for i, b in enumerate(x) if b}
            Pm1S = image_set(pinv, S)
            Qm1S = image_set(qinv, S)
            assert S ^ Pm1S ^ Qm1S == set(range(n))
            T = S & Pm1S & Qm1S
            assert len(T) == t3
            assert 3 * len(S) == n + 2 * len(T)

            parity.append((w, t3, x))
            if is_exact:
                exact.append(x)

    assert bool(exact) == expect_exact
    if parity:
        d = min(w for w, _, _ in parity)
        assert bool(exact) == (3 * d == n)
        min_t = min(t for w, t, _ in parity if w == d)
        assert 3 * d == n + 2 * min_t
    else:
        d = None

    print(f"{name}: n={n} parity={len(parity)} exact={len(exact)} d={d}")


def main():
    # SAT fixture, n=9. Minimum parity-coset weight reaches n/3=3.
    check_fixture(
        "SAT9",
        [2, 6, 7, 4, 5, 8, 1, 3, 0],
        [5, 8, 1, 6, 3, 2, 0, 4, 7],
        True,
    )

    # UNSAT fixture with nonempty parity coset. Its minimum parity solution has
    # weight 5 > n/3=3 and exactly three triple-covered rows.
    check_fixture(
        "UNSAT9",
        [4, 0, 6, 7, 8, 1, 5, 2, 3],
        [8, 7, 1, 6, 3, 0, 4, 5, 2],
        False,
    )

    print("R5 E56 binary syndrome weight floor: PASS")


if __name__ == "__main__":
    main()
