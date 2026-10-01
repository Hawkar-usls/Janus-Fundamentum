#!/usr/bin/env python3
"""Exact algebra regression for the Tovey EQ3/OR3 common-basis barrier.

The companion JSON contains the symbolic theorem proof. This checker verifies the
critical transformed OR3 layer formulas after the EQ3 parity lemma has forced
r=c/a=-d/b=-s, and the two integer polynomial identities that make both OR3
parity choices impossible over characteristic zero.
"""

from itertools import product


def poly_add(p, q):
    n = max(len(p), len(q))
    out = [0] * n
    for i in range(n):
        out[i] = (p[i] if i < len(p) else 0) + (q[i] if i < len(q) else 0)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return tuple(out)


def poly_scale(c, p):
    return tuple(c * x for x in p)


def poly_eval(p, s):
    out = 0
    power = 1
    for c in p:
        out += c * power
        power *= s
    return out


def transformed_or_layers_by_direct_sum(a, b, c, d):
    """Return unscaled symmetric layers of T^(tensor 3) OR3.

    T is adj(S^T)=[[d,-b],[-c,a]], so the common det(S)^(-3) factor is omitted.
    OR3 is 0 only on 000 and 1 on the other seven Boolean inputs.
    """
    T = ((d, -b), (-c, a))
    layers = []
    for k in range(4):
        out_bits = (1,) * k + (0,) * (3 - k)
        total = 0
        for in_bits in product((0, 1), repeat=3):
            if in_bits == (0, 0, 0):
                continue
            term = 1
            for o, i in zip(out_bits, in_bits):
                term *= T[o][i]
            total += term
        layers.append(total)
    return tuple(layers)


def main():
    # After EQ3 parity, the symbolic proof forces r=c/a=-s with s=d/b.
    # Removing nonzero monomial scales a^3,a^2 b,a b^2,b^3 from the four
    # OR3 Hamming-weight layers gives these exact polynomials in s.
    g0 = (-1, 3, -3)      # -(1-3s+3s^2)
    g1 = (1, -1, -1)      # 1-s-s^2
    g2 = (-1, -1, 1)      # s^2-s-1
    g3 = (1, 3, 3)        # 1+3s+3s^2

    # Exact obstruction identities.
    # g3 = 4 - 3*g1, so g1=0 => g3=4 != 0 in characteristic zero.
    assert g3 == poly_add((4,), poly_scale(-3, g1))
    # g0 = -4 - 3*g2, so g2=0 => g0=-4 != 0 in characteristic zero.
    assert g0 == poly_add((-4,), poly_scale(-3, g2))

    # Independent direct tensor checks on several integer s values using a=b=1,
    # c=-s,d=s. These samples verify that the normalized formulas agree with
    # the actual dual-basis expansion; the theorem itself is symbolic.
    for s in (-5, -2, -1, 1, 2, 4):
        if s == 0:
            continue
        a = b = 1
        c = -s
        d = s
        raw = transformed_or_layers_by_direct_sum(a, b, c, d)
        # Layer scales are b^3, a*b^2, a^2*b, a^3, all 1 in this normalization.
        expected = tuple(poly_eval(g, s) for g in (g0, g1, g2, g3))
        assert raw == expected, (s, raw, expected)

    print("PASS_TOVEY_EQ3_OR3_COMMON_BASIS_MATCHGATE_BARRIER")
    print("eq3_parity_forces_ratio_r_minus_s=True")
    print("or3_even_parity_obstruction=g3_4_minus_3g1")
    print("or3_odd_parity_obstruction=g0_minus4_minus_3g2")
    print("characteristic_zero_constant_obstruction=4")
    print("E8_D1=EMPTY P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
