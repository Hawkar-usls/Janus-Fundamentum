#!/usr/bin/env python3
"""Exact symbolic regression for the E8 v4.3 weighted OR2+XOR3 edge-gauge barrier."""

from itertools import product
import sympy as sp

r1, r2, r3 = sp.symbols("r1 r2 r3")
R = [r1, r2, r3]
T = [sp.Matrix([[r, 1], [r, -1]]) for r in R]


def f1(a, y):
    return int(bool(a) or (not bool(y)))


def f2(y, b, z):
    return int((y ^ b ^ z) == 1)


def f3(z, c):
    return int((not bool(z)) or bool(c))


def composite():
    H = {}
    for a, b, c in product((0, 1), repeat=3):
        H[(a, b, c)] = sum(
            f1(a, y) * f2(y, b, z) * f3(z, c)
            for y, z in product((0, 1), repeat=2)
        )
    return H


def transform(H):
    out = {}
    for ybits in product((0, 1), repeat=3):
        expr = 0
        for xbits in product((0, 1), repeat=3):
            val = H[xbits]
            if not val:
                continue
            term = sp.Integer(val)
            for j in range(3):
                term *= T[j][ybits[j], xbits[j]]
            expr += term
        out[ybits] = sp.factor(expr)
    return out


def main():
    H = composite()
    values = [H[b] for b in product((0, 1), repeat=3)]
    assert values == [0, 1, 1, 1, 1, 2, 1, 2], values
    assert {b for b, v in H.items() if v != 0} == {
        b for b in product((0, 1), repeat=3) if any(b)
    }

    out = transform(H)
    odd_sum = sp.factor(sum(v for b, v in out.items() if sum(b) % 2 == 1))
    even_sum = sp.factor(sum(v for b, v in out.items() if sum(b) % 2 == 0))
    assert odd_sum == -8, odd_sum
    assert even_sum == 8, even_sum

    # Freeze the full transformed amplitudes as a stronger regression.
    expected = {
        (0, 0, 0): r1*r2 + r1*r3 + r1 + r2*r3 + 2*r2 + r3 + 2,
        (0, 0, 1): -r1*r2 + r1*r3 - r1 + r2*r3 - 2*r2 + r3 - 2,
        (0, 1, 0): r1*r2 - r1*r3 - r1 + r2*r3 + 2*r2 - r3 - 2,
        (0, 1, 1): -r1*r2 - r1*r3 + r1 + r2*r3 - 2*r2 - r3 + 2,
        (1, 0, 0): r1*r2 + r1*r3 + r1 - r2*r3 - 2*r2 - r3 - 2,
        (1, 0, 1): -r1*r2 + r1*r3 - r1 - r2*r3 + 2*r2 - r3 + 2,
        (1, 1, 0): r1*r2 - r1*r3 - r1 - r2*r3 - 2*r2 + r3 + 2,
        (1, 1, 1): -r1*r2 - r1*r3 + r1 - r2*r3 + 2*r2 + r3 - 2,
    }
    for bits in expected:
        assert sp.expand(out[bits] - expected[bits]) == 0, bits

    print("PASS: exact sum-product gadget composite is H=(0,1,1,1,1,2,1,2)")
    print("PASS: under arbitrary Hadamard-type external gauges, odd-sector sum is -8")
    print("PASS: under arbitrary Hadamard-type external gauges, even-sector sum is +8")
    print("PASS: weighted composite can never have pure matchgate parity in characteristic zero")


if __name__ == "__main__":
    main()
