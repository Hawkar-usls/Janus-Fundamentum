#!/usr/bin/env python3
"""Exact finite-field regression for E8 v4.5 all-characteristics closure."""

from itertools import product


def inv_transpose(T, p):
    A, B, C, D = T
    det = (A * D - B * C) % p
    if det == 0:
        return None
    q = pow(det, -1, p)
    return (D*q % p, -C*q % p, -B*q % p, A*q % p)


def entry(M, i, j):
    A, B, C, D = M
    return ((A, B), (C, D))[i][j]


def transform(sig, arity, M, p):
    out = {}
    for y in product((0, 1), repeat=arity):
        val = 0
        for x in product((0, 1), repeat=arity):
            s = sig.get(x, 0) % p
            if not s:
                continue
            term = s
            for j in range(arity):
                term = term * entry(M, y[j], x[j]) % p
            val = (val + term) % p
        out[y] = val
    return out


def parity(out):
    even = any(v for x, v in out.items() if sum(x) % 2 == 0)
    odd = any(v for x, v in out.items() if sum(x) % 2 == 1)
    if even and not odd:
        return "even"
    if odd and not even:
        return "odd"
    return None


OR2 = {x: 1 for x in product((0, 1), repeat=2) if any(x)}
XOR3 = {x: 1 for x in product((0, 1), repeat=3) if sum(x) % 2 == 1}
EQ3 = {(0, 0, 0): 1, (1, 1, 1): 1}


def scan(p):
    pair = []
    triple = []
    for T in product(range(p), repeat=4):
        S = inv_transpose(T, p)
        if S is None:
            continue
        po = parity(transform(OR2, 2, T, p))
        px = parity(transform(XOR3, 3, T, p))
        if po and px:
            pair.append((T, po, px))
            pe = parity(transform(EQ3, 3, S, p))
            if pe:
                triple.append((T, po, px, pe))
    return pair, triple


def main():
    pair7, triple7 = scan(7)
    assert len(pair7) == 72
    assert not triple7

    fam_ee = []
    fam_eo = []
    for T, po, px in pair7:
        A, B, C, D = T
        if A == (2*B) % 7 and D == (2*C) % 7 and B and C:
            fam_ee.append(T)
            assert (po, px) == ("even", "even")
        elif B == (2*A) % 7 and C == (2*D) % 7 and A and D:
            fam_eo.append(T)
            assert (po, px) == ("even", "odd")
        else:
            raise AssertionError((T, po, px))
    assert len(fam_ee) == 36
    assert len(fam_eo) == 36

    for T, _, _ in pair7:
        A, B, C, D = T
        e0 = (D**3 - C**3) % 7
        e1 = (-B*D**2 + A*C**2) % 7
        e2 = (D*B**2 - C*A**2) % 7
        e3 = (A**3 - B**3) % 7
        assert e0 == 0 and e3 == 0
        assert e1 != 0 and e2 != 0

    for p in (3, 5, 11, 13):
        pair, triple = scan(p)
        assert not pair
        assert not triple

    print("PASS: GF(7) has exactly 72 OR2+XOR3 pure-parity common bases")
    print("PASS: exactly 36 EE and 36 EO bases, matching the two classified families")
    print("PASS: dual EQ3 mixes weight-1 and weight-2 parity for all 72 bases")
    print("PASS: no OR2+XOR3 parity basis over GF(3), GF(5), GF(11), GF(13) controls")


if __name__ == "__main__":
    main()
