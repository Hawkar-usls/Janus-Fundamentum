#!/usr/bin/env python3
"""Exact finite controls for R5 E20 kernel 3-circuit saturation.

Checks:
  * the Boolean relation induced by a 3-circuit coefficient triple;
  * the complete 12-type relation taxonomy on a large primitive integer box;
  * the hard equal-coefficient circuit gives Exact-One;
  * the E19 Paley-root quotient contains the forbidden circuit
      r_03 + r_31 - r_01 = 0,
    whose alphabet relation is empty.

The companion note supplies the symbolic proof that the 12-type taxonomy is
exhaustive for every nonzero rational coefficient triple.
"""

from itertools import product
from math import gcd


ALPHABET = (-1, 2)


def allowed_bits(coeff):
    out = []
    for bits in product((0, 1), repeat=3):
        y = tuple(3 * b - 1 for b in bits)
        if sum(c * v for c, v in zip(coeff, y)) == 0:
            out.append(bits)
    return tuple(out)


def primitive(coeff):
    a, b, c = coeff
    g = gcd(abs(a), gcd(abs(b), abs(c)))
    a, b, c = a // g, b // g, c // g
    for v in (a, b, c):
        if v:
            if v < 0:
                a, b, c = -a, -b, -c
            break
    return (a, b, c)


def relation_kind(rel):
    if not rel:
        return "EMPTY_UNSAT"
    if len(rel) == 1:
        return "SINGLETON_FORCED"
    if rel == ((0, 0, 0), (1, 1, 1)):
        return "EQUALITY"
    if len(rel) == 2:
        # The only non-equality two-state types have one coordinate fixed to 1
        # and the other two complementary.
        cols = list(zip(*rel))
        fixed_one = [i for i, col in enumerate(cols) if col == (1, 1)]
        complementary = [i for i, col in enumerate(cols) if col in ((0, 1), (1, 0))]
        if len(fixed_one) == 1 and len(complementary) == 2:
            return "FORCED_ONE_PLUS_XOR"
    if rel == ((0, 0, 1), (0, 1, 0), (1, 0, 0)):
        return "EXACT_ONE"
    return "UNEXPECTED"


def check_relation_taxonomy(box=9):
    relations = {}
    for a in range(-box, box + 1):
        for b in range(-box, box + 1):
            for c in range(-box, box + 1):
                if 0 in (a, b, c):
                    continue
                coeff = primitive((a, b, c))
                if coeff != (a, b, c):
                    continue
                rel = allowed_bits(coeff)
                relations.setdefault(rel, coeff)

    kinds = {relation_kind(rel) for rel in relations}
    assert "UNEXPECTED" not in kinds
    assert len(relations) == 12

    counts = {}
    for rel in relations:
        k = relation_kind(rel)
        counts[k] = counts.get(k, 0) + 1

    assert counts == {
        "EMPTY_UNSAT": 1,
        "SINGLETON_FORCED": 6,
        "EQUALITY": 1,
        "FORCED_ONE_PLUS_XOR": 3,
        "EXACT_ONE": 1,
    }

    # Equal coefficients are exactly the hard 1-in-3 local relation.
    assert allowed_bits((1, 1, 1)) == (
        (0, 0, 1),
        (0, 1, 0),
        (1, 0, 0),
    )

    # Representative tractable types.
    assert allowed_bits((1, -2, 1)) == ((0, 0, 0), (1, 1, 1))
    assert relation_kind(allowed_bits((1, -2, -2))) == "FORCED_ONE_PLUS_XOR"
    assert allowed_bits((1, 1, -1)) == ()
    return counts


def paley_orientation(i, j, p=11):
    residues = {1, 3, 4, 5, 9}
    return ((j - i) % p) in residues


def root(i, j, p=11):
    v = [0] * p
    v[i] = 1
    v[j] = -1
    return tuple(v)


def vecadd(*vecs):
    return tuple(sum(v[i] for v in vecs) for i in range(len(vecs[0])))


def scale(a, v):
    return tuple(a * x for x in v)


def check_e19_paley_forbidden_circuit():
    # 0 -> 3 -> 1, together with 0 -> 1, is a transitive Paley triangle.
    assert paley_orientation(0, 3)
    assert paley_orientation(3, 1)
    assert paley_orientation(0, 1)

    r03 = root(0, 3)
    r31 = root(3, 1)
    r01 = root(0, 1)

    dep = vecadd(r03, r31, scale(-1, r01))
    assert dep == (0,) * 11

    # Pairwise nonproportional, hence this is a genuine 3-circuit in the
    # ten-dimensional A_10 root kernel used by R5 E19.
    assert r03 != r31 and r03 != r01 and r31 != r01
    assert r03 != scale(-1, r31)
    assert r03 != scale(-1, r01)
    assert r31 != scale(-1, r01)

    rel = allowed_bits((1, 1, -1))
    assert rel == ()
    return ("0->3", "3->1", "0->1"), (1, 1, -1)


def main():
    counts = check_relation_taxonomy()
    arcs, coeff = check_e19_paley_forbidden_circuit()
    print("R5 E20 kernel 3-circuit controls: PASS")
    print("relation taxonomy:", counts)
    print("E19 local forbidden circuit:", arcs, "coeff=", coeff, "allowed=EMPTY")


if __name__ == "__main__":
    main()
