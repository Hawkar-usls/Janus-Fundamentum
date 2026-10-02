#!/usr/bin/env python3
"""Exact finite controls for R5 E43.

Verifies the geometric lemma behind the ternary linear-relation dichotomy:
for a nonzero normal c with all three coordinates nonzero, a plane level
c.x=h can contain at least three Boolean cube vertices only when the three
absolute coefficient magnitudes are equal.

The checker enumerates all triples of cube vertices, computes an exact integer
normal by cross product, and confirms that every plane through >=3 cube vertices
with full-support normal has equal absolute normal coordinates.

It also verifies that every relation of size <=2 is exactly representable by
forcing plus equality/complement constraints relative to one representative bit.
"""

from itertools import combinations, product
from math import gcd

CUBE = list(product((0, 1), repeat=3))


def cross(a, b):
    return (
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0],
    )


def sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def primitive(c):
    g = 0
    for x in c:
        g = gcd(g, abs(x))
    if g:
        c = tuple(x//g for x in c)
    for x in c:
        if x:
            if x < 0:
                c = tuple(-y for y in c)
            break
    return c


def relation(c, h):
    return tuple(x for x in CUBE if dot(c, x) == h)


def reconstruct_two_tuple_relation(R):
    assert 1 <= len(R) <= 2
    if len(R) == 1:
        return {R[0]}
    a, b = R
    same = [i for i in range(3) if a[i] == b[i]]
    diff = [i for i in range(3) if a[i] != b[i]]
    pivot = diff[0]
    out = set()
    for x in CUBE:
        ok = True
        for i in same:
            ok &= (x[i] == a[i])
        for i in diff[1:]:
            ok &= ((x[i] ^ x[pivot]) == (a[i] ^ a[pivot]))
        if ok:
            out.add(x)
    return out


def main():
    normals = set()
    checked_planes = 0
    for p, q, r in combinations(CUBE, 3):
        c = cross(sub(q, p), sub(r, p))
        if c == (0, 0, 0):
            raise AssertionError("three distinct cube vertices should not be collinear")
        c = primitive(c)
        h = dot(c, p)
        R = relation(c, h)
        if len(R) >= 3 and all(ci != 0 for ci in c):
            checked_planes += 1
            normals.add(tuple(sorted(abs(ci) for ci in c)))
            assert abs(c[0]) == abs(c[1]) == abs(c[2])

    assert normals == {(1, 1, 1)}

    # Exhaustive bounded coefficient sanity sweep for arbitrary RHS values.
    for c in product(range(-5, 6), repeat=3):
        if 0 in c:
            continue
        values = sorted(set(dot(c, x) for x in CUBE))
        max_size = max(len(relation(c, h)) for h in values)
        equal_abs = abs(c[0]) == abs(c[1]) == abs(c[2])
        assert (max_size >= 3) == equal_abs
        if not equal_abs:
            for h in values:
                R = relation(c, h)
                assert len(R) <= 2
                if R:
                    assert reconstruct_two_tuple_relation(R) == set(R)

    print("R5 E43 ternary linear relation dichotomy: PASS")
    print(f"full-support >=3-point cube planes checked: {checked_planes}")
    print("only primitive full-support normal magnitude pattern: (1,1,1)")
    print("bounded exact sweep: coefficients in [-5,5]^3, all nonzero: PASS")
    print("all <=2-tuple relations reconstruct by forcing/equality/complement: PASS")


if __name__ == "__main__":
    main()
