#!/usr/bin/env python3
from itertools import product


def B(x):
    x1, x2 = x
    return (x1 ^ x2, x2)


def B_inv(y):
    y1, y2 = y
    return (y1 ^ y2, y2)


def residuals_before():
    out = {}
    for x in product((0, 1), repeat=2):
        out[x] = tuple(z for z in product((0, 1), repeat=2) if z == x)
    return out


def residuals_after():
    out = {}
    for y in product((0, 1), repeat=2):
        x = B_inv(y)
        out[y] = tuple(z for z in product((0, 1), repeat=2) if z == x)
    return out


def main():
    cube = list(product((0, 1), repeat=2))

    # Exact forward/inverse cycle.
    assert len({B(x) for x in cube}) == 4
    for x in cube:
        assert B_inv(B(x)) == x
    for y in cube:
        assert B(B_inv(y)) == y

    r0 = residuals_before()
    r1 = residuals_after()

    # Equality zipper has one distinct continuation for every interface state.
    assert len(set(r0.values())) == 4
    assert len(set(r1.values())) == 4

    # Re-encoding only permutes residual continuations.
    assert set(r0.values()) == set(r1.values())

    # The inverse step returns the original continuation map after coordinate pullback.
    for x in cube:
        assert r1[B(x)] == r0[x]

    print('PASS: two-bit invertible XOR re-encoding preserves all 4 continuation classes')
    print('PASS: inverse re-encoding closes the definitional cycle exactly')
    print('VERDICT: strict semantic progress cannot be claimed on every reversible macro-step')
    print('CLAIM CEILING: U-PAIR-1G progress measure fails; P vs NP remains OPEN')


if __name__ == '__main__':
    main()
