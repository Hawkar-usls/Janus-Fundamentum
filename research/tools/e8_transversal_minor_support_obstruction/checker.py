#!/usr/bin/env python3
"""Independent replay for E8 v0.4 transversal-minor support obstruction.

The theorem is symbolic and field-independent. This checker:
  * evaluates the frozen 3-CNF on the eight assignments used by the proof;
  * verifies the relevant determinant expansions symbolically as sparse polynomials;
  * exhaustively replays the key zero/nonzero implication over GF(2), GF(3),
    GF(5), and GF(7).
No SAT/SMT/CAS package is used.
"""

from itertools import permutations, product


def sat(bits):
    x1, x2, x3, x4 = map(bool, bits)
    return int(
        (x1 or (not x2) or x3)
        and (x1 or x2 or x4)
        and ((not x2) or x3 or x4)
    )


# Sparse commutative integer polynomial: monomial tuple -> integer coefficient.
def pvar(name):
    return {(name,): 1}


def padd(a, b):
    out = dict(a)
    for m, c in b.items():
        out[m] = out.get(m, 0) + c
        if out[m] == 0:
            del out[m]
    return out


def pneg(a):
    return {m: -c for m, c in a.items()}


def pmul(a, b):
    out = {}
    for ma, ca in a.items():
        for mb, cb in b.items():
            m = tuple(sorted(ma + mb))
            out[m] = out.get(m, 0) + ca * cb
    return {m: c for m, c in out.items() if c}


def pzero():
    return {}


def pdet(M):
    n = len(M)
    out = pzero()
    for perm in permutations(range(n)):
        inv = sum(1 for i in range(n) for j in range(i + 1, n) if perm[i] > perm[j])
        term = {(): -1 if inv % 2 else 1}
        for i, j in enumerate(perm):
            term = pmul(term, M[i][j])
        out = padd(out, term)
    return out


def substitute_zero(poly, names):
    names = set(names)
    return {m: c for m, c in poly.items() if not any(v in names for v in m)}


def monomial(*names):
    return {tuple(sorted(names)): 1}


def symbolic_expansion_checks():
    z = pzero()
    m = {(i, j): pvar(f"m{i}{j}") for i in range(1, 5) for j in range(1, 5)}

    def minor(ids):
        return pdet([[m[i, j] for j in ids] for i in ids])

    p12 = substitute_zero(minor([1, 2]), {"m11", "m22"})
    assert p12 == pneg(monomial("m12", "m21")), p12

    p14 = substitute_zero(minor([1, 4]), {"m11"})
    assert p14 == pneg(monomial("m14", "m41")), p14

    p24 = substitute_zero(minor([2, 4]), {"m22"})
    assert p24 == pneg(monomial("m24", "m42")), p24

    p124 = substitute_zero(minor([1, 2, 4]), {"m11", "m22"})
    expected124 = pneg(monomial("m12", "m21", "m44"))
    expected124 = padd(expected124, monomial("m12", "m24", "m41"))
    expected124 = padd(expected124, monomial("m14", "m21", "m42"))
    assert p124 == expected124, (p124, expected124)

    p123 = substitute_zero(minor([1, 2, 3]), {"m11", "m22"})
    expected123 = pneg(monomial("m12", "m21", "m33"))
    expected123 = padd(expected123, monomial("m12", "m23", "m31"))
    expected123 = padd(expected123, monomial("m13", "m21", "m32"))
    assert p123 == expected123, (p123, expected123)
    # Once m12=m21=0, every remaining p123 monomial vanishes.
    assert substitute_zero(p123, {"m12", "m21"}) == {}


def finite_field_implication_replay(p):
    hits = 0
    for m12, m21, m14, m41, m24, m42 in product(range(p), repeat=6):
        p12 = (-m12 * m21) % p
        p14 = (-m14 * m41) % p
        p24 = (-m24 * m42) % p
        # Under p12=0, the -m12*m21*m44 term vanishes for every m44.
        p124_reduced = (m12 * m24 * m41 + m14 * m21 * m42) % p
        if p12 == 0 and p14 != 0 and p24 != 0 and p124_reduced == 0:
            hits += 1
            assert m12 == 0 and m21 == 0, (
                p, m12, m21, m14, m41, m24, m42
            )
    assert hits > 0
    return hits


def main():
    frozen = {
        (1, 0, 0, 0): 1,
        (0, 0, 0, 0): 0,
        (0, 1, 0, 0): 0,
        (1, 1, 0, 0): 0,
        (0, 1, 1, 0): 1,
        (0, 0, 0, 1): 1,
        (0, 1, 0, 1): 0,
        (1, 1, 0, 1): 1,
    }
    for bits, expected in frozen.items():
        assert sat(bits) == expected, (bits, sat(bits), expected)

    symbolic_expansion_checks()
    receipts = {p: finite_field_implication_replay(p) for p in (2, 3, 5, 7)}

    print("E8_TRANSVERSAL_MINOR_SUPPORT_OBSTRUCTION replay: PASS")
    print("frozen truth assignments: PASS")
    print("symbolic determinant expansions: PASS")
    print("finite-field implication receipts:", receipts)
    print("The field-independent theorem uses the symbolic identities plus the field no-zero-divisors axiom.")


if __name__ == "__main__":
    main()
