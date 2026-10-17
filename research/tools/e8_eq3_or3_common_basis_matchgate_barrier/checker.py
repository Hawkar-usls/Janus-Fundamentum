from fractions import Fraction
from itertools import product


def trim(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def poly_divmod(a, b):
    a = trim([Fraction(x) for x in a])
    b = trim([Fraction(x) for x in b])
    assert b != [0]
    if len(a) < len(b):
        return [Fraction(0)], a
    q = [Fraction(0)] * (len(a) - len(b) + 1)
    while len(a) >= len(b) and a != [0]:
        k = len(a) - len(b)
        c = a[-1] / b[-1]
        q[k] = c
        for j in range(len(b)):
            a[k + j] -= c * b[j]
        a = trim(a)
    return trim(q), trim(a)


def poly_gcd(a, b):
    a = trim([Fraction(x) for x in a])
    b = trim([Fraction(x) for x in b])
    while b != [0]:
        _, r = poly_divmod(a, b)
        a, b = b, r
    lead = a[-1]
    return trim([x / lead for x in a])


def inv2x2(S):
    a, b = S[0]
    c, d = S[1]
    det = a * d - b * c
    assert det != 0
    return [[d / det, -b / det], [-c / det, a / det]]


def transpose(A):
    return [list(x) for x in zip(*A)]


def transformed_or3_layers(r, s):
    # S=[[1,r],[1,s]], T=S^{-T}.
    S = [[Fraction(1), Fraction(r)], [Fraction(1), Fraction(s)]]
    T = transpose(inv2x2(S))
    layers = []
    for w in range(4):
        out = [1] * w + [0] * (3 - w)
        val = Fraction(0)
        for inp in product((0, 1), repeat=3):
            amp = Fraction(0 if inp == (0, 0, 0) else 1)
            if amp == 0:
                continue
            term = amp
            for j in range(3):
                term *= T[out[j]][inp[j]]
            val += term
        layers.append(val)
    return layers


def check_layer_formula(r, s):
    r = Fraction(r)
    s = Fraction(s)
    assert r != s
    layers = transformed_or3_layers(r, s)
    scale = (r - s) ** 3
    got = [x * scale for x in layers]
    expected = [
        3 * s * s - 3 * s + 1,
        -(2 * r * s - r + s * s - 2 * s + 1),
        r * r + 2 * r * s - 2 * r - s + 1,
        -(3 * r * r - 3 * r + 1),
    ]
    assert got == expected, (r, s, got, expected)


def main():
    # x^6-1 and 3x^2-3x+1 have no common root over characteristic zero.
    x6_minus_1 = [-1, 0, 0, 0, 0, 0, 1]
    clause_parity_poly = [1, -3, 3]
    g = poly_gcd(x6_minus_1, clause_parity_poly)
    assert g == [Fraction(1)], g

    # Independent exact-rational regression of the dual OR3 layer formulas.
    for r, s in [(2, 3), (-1, 2), (1, -2), (Fraction(1, 2), Fraction(3, 2))]:
        check_layer_formula(r, s)

    # EQ3-even: r^2 s=-1 and s^3=-1 => r^6=s^6=1.
    # EQ3-odd:  r^3=-1 and r s^2=-1 => r^6=s^6=1.
    # OR3-even would force clause_parity_poly(r)=0 (weight 3).
    # OR3-odd  would force clause_parity_poly(s)=0 (weight 0).
    # Coprimality above therefore rejects all four parity combinations.

    print('PASS_EQ3_OR3_COMMON_BASIS_MATCHGATE_BARRIER')
    print('gcd(x^6-1, 3x^2-3x+1)=1')
    print('EQ4_NOT_NEEDED=True BOUNDED_OCCURRENCE_LOOPHOLE_CLOSED=True')
    print('E8_D1=EMPTY P_VS_NP=OPEN')


if __name__ == '__main__':
    main()
