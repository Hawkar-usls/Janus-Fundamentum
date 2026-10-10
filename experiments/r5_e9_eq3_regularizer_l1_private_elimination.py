#!/usr/bin/env python3
"""Exact regression for EQ3 regularizer L1 private elimination."""

ROWS = [
    (2,5,6),(1,4,7),(5,7,9),(0,3,7),(4,6,9),
    (2,4,8),(3,8,9),(0,5,8),(1,3,6),
]


def x_of(q, r):
    return [q,q,q,1-r-q,1-r-q,1-r-q,r,r,r,q]


def row_sums(x):
    return [sum(x[j] for j in row) for row in ROWS]


def F_g(q, r):
    x = x_of(q,r)
    assert row_sums(x) == [1]*9
    return sum(abs(2*t-1) for t in x)


def phi(q):
    return 4*abs(2*q-1) + 6*max(1, abs(q))


def hinge(q):
    pos = lambda a: max(0,a)
    return 10 + 8*pos(-q) + 6*pos(-q-1) + 14*pos(q-1)


def main():
    # Frozen affine form satisfies all nine gadget equations for arbitrary q,r.
    for q in range(-8,9):
        for r in range(-10,11):
            assert row_sums(x_of(q,r)) == [1]*9

    # Exact minimization identity. The searched r-window is safely wider than
    # the interval between 0 and -2q for these regression samples.
    vals = []
    for q in range(-20,21):
        brute = min(F_g(q,r) for r in range(-30,31))
        assert brute == phi(q), (q, brute, phi(q))
        assert phi(q) == hinge(q)
        vals.append(phi(q))

    # Discrete convexity on the sampled window: first differences nondecreasing.
    diffs = [b-a for a,b in zip(vals, vals[1:])]
    assert all(a <= b for a,b in zip(diffs,diffs[1:])), diffs

    equality = [q for q in range(-20,21) if phi(q) == 10]
    assert equality == [0,1], equality

    # Closed-form piecewise checks.
    for q in range(-20,-0):
        assert phi(q) == 14*abs(q)+4
    assert phi(0) == phi(1) == 10
    for q in range(2,21):
        assert phi(q) == 14*q-4

    print("PASS: frozen EQ3 affine form satisfies all gadget rows")
    print("PASS: min_r F_G(q,r) = 4|2q-1| + 6 max(1,|q|)")
    print("PASS: phi is discrete convex on exact regression window")
    print("PASS: phi(q)=10 iff q in {0,1}")
    print("P_VS_NP=OPEN; E8_D1=EMPTY")


if __name__ == "__main__":
    main()
