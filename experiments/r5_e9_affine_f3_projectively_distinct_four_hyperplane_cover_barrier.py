#!/usr/bin/env python3
"""Exact regression for the projectively-distinct F3 hyperplane cover barrier."""

from itertools import product


def dot(a, x):
    return sum(u * v for u, v in zip(a, x)) % 3


def canonical_projective(v):
    j = next(i for i, x in enumerate(v) if x % 3)
    inv = pow(v[j] % 3, -1, 3)
    return tuple((inv * x) % 3 for x in v)


def check(d):
    assert d >= 2
    normals = [
        (1, 0) + (0,) * (d - 2),
        (0, 1) + (0,) * (d - 2),
        (1, 2) + (0,) * (d - 2),
        (1, 1) + (0,) * (d - 2),
    ]
    assert len({canonical_projective(v) for v in normals}) == 4

    points = list(product(range(3), repeat=d))
    uncovered = [x for x in points if all(dot(a, x) != 0 for a in normals)]
    assert uncovered == []
    return len(points)


def main():
    sizes = {d: check(d) for d in range(2, 8)}
    print({'status': 'PASS_F3_FOUR_HYPERPLANE_COVER_BARRIER', 'checked_space_sizes': sizes})
    print('E8_D1 = EMPTY')
    print('P_VS_NP = OPEN')


if __name__ == '__main__':
    main()
