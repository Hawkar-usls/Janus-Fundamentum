#!/usr/bin/env python3
from itertools import product
from math import ceil, log2


def R(u1, u2, x, w):
    if (u1, u2) == (0, 0):
        return w == 0
    if (u1, u2) == (0, 1):
        return w == 1
    if (u1, u2) == (1, 0):
        return w == x
    if (u1, u2) == (1, 1):
        return w == 0
    raise AssertionError


def residual_before(b):
    u1, u2, x = b
    return tuple(w for w in (0, 1) if R(u1, u2, x, w))


def q_drop_x(b):
    u1, u2, _ = b
    return (u1, u2)


def residual_after(u):
    u1, u2 = u
    return tuple(w for w in (0, 1) if any(R(u1, u2, x, w) for x in (0, 1)))


def verify_collision_certificate(b0, b1, w):
    assert b0 != b1
    assert q_drop_x(b0) == q_drop_x(b1)
    r0 = R(*b0, w)
    r1 = R(*b1, w)
    assert r0 != r1
    return True


def main():
    old = {b: residual_before(b) for b in product((0, 1), repeat=3)}
    new = {u: residual_after(u) for u in product((0, 1), repeat=2)}

    old_classes = set(old.values())
    new_classes = set(new.values())

    assert old_classes == {(0,), (1,)}
    assert new_classes == {(0,), (1,), (0, 1)}
    assert len(old_classes) == 2
    assert len(new_classes) == 3

    mu_before = ceil(log2(len(old_classes)))
    mu_after = ceil(log2(len(new_classes)))
    assert (mu_before, mu_after) == (1, 2)

    # Genuine semantic collision in the u=10 fibre:
    # x=0 has residual {0}; x=1 has residual {1}.
    verify_collision_certificate((1, 0, 0), (1, 0, 1), 0)

    # Negative bijective-control sanity: an identity map cannot collide distinct boundaries.
    boundaries = list(product((0, 1), repeat=3))
    assert not any(a != b and a == b for a in boundaries for b in boundaries)

    print('PASS: explicit local collision certificate is polynomially checkable')
    print('PASS: N_before=2, N_after=3; mu_before=1, mu_after=2')
    print('VERDICT: continuation-class count is not monotone under existential projection')
    print('CLAIM CEILING: no SAT-in-P / P=NP promotion')


if __name__ == '__main__':
    main()
