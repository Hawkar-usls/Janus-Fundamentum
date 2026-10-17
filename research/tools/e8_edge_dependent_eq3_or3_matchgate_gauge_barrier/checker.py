from fractions import Fraction
from itertools import product


def inv2x2(S):
    a, b = S[0]
    c, d = S[1]
    det = a * d - b * c
    assert det != 0
    return [[d / det, -b / det], [-c / det, a / det]]


def transpose(A):
    return [list(x) for x in zip(*A)]


def dual_hadamard(r):
    S = [[Fraction(1), Fraction(r)], [Fraction(1), -Fraction(r)]]
    return transpose(inv2x2(S))


def transformed_or3(r1, r2, r3):
    rs = [Fraction(r1), Fraction(r2), Fraction(r3)]
    assert all(r != 0 for r in rs)
    T = [dual_hadamard(r) for r in rs]
    out = {}
    for bits in product((0, 1), repeat=3):
        val = Fraction(0)
        for inp in product((0, 1), repeat=3):
            amp = 0 if inp == (0, 0, 0) else 1
            if not amp:
                continue
            term = Fraction(1)
            for j in range(3):
                term *= T[j][bits[j]][inp[j]]
            val += term
        out[bits] = val
    scale = 8 * rs[0] * rs[1] * rs[2]
    return {k: v * scale for k, v in out.items()}


def expected_amplitudes(r1, r2, r3):
    a, b, c = map(Fraction, (r1, r2, r3))
    return {
        (0, 0, 0): a*b + a*c + a + b*c + b + c + 1,
        (0, 0, 1): -a*b + a*c - a + b*c - b + c - 1,
        (0, 1, 0): a*b - a*c - a + b*c + b - c - 1,
        (0, 1, 1): -a*b - a*c + a + b*c - b - c + 1,
        (1, 0, 0): a*b + a*c + a - b*c - b - c - 1,
        (1, 0, 1): -a*b + a*c - a - b*c + b - c + 1,
        (1, 1, 0): a*b - a*c - a - b*c - b + c + 1,
        (1, 1, 1): -a*b - a*c + a - b*c + b + c - 1,
    }


def check_pair_sum_identities(r1, r2, r3):
    A = transformed_or3(r1, r2, r3)
    E = expected_amplitudes(r1, r2, r3)
    assert A == E
    a, b, c = map(Fraction, (r1, r2, r3))

    # If OR3 were even-parity, all four odd-weight amplitudes would vanish.
    assert A[(0,0,1)] + A[(0,1,0)] == 2 * (-a + b*c - 1)
    assert A[(1,0,0)] + A[(1,1,1)] == 2 * ( a - b*c - 1)
    # Simultaneous vanishing would require b*c=a+1 and b*c=a-1.

    # If OR3 were odd-parity, all four even-weight amplitudes would vanish.
    assert A[(0,0,0)] + A[(0,1,1)] == 2 * ( a + b*c + 1)
    assert A[(1,0,1)] + A[(1,1,0)] == 2 * (-a - b*c + 1)
    # Simultaneous vanishing would require a+b*c=-1 and a+b*c=1.


def check_conjugated_parity_operator(r):
    # S=[[1,r],[1,-r]] must conjugate Z to an anti-diagonal involution.
    r = Fraction(r)
    S = [[Fraction(1), r], [Fraction(1), -r]]
    Sinv = inv2x2(S)
    ZS = [[S[0][0], S[0][1]], [-S[1][0], -S[1][1]]]
    A = [[sum(Sinv[i][k] * ZS[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    assert A[0][0] == 0 and A[1][1] == 0
    # A^2=I.
    A2 = [[sum(A[i][k] * A[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    assert A2 == [[1, 0], [0, 1]]


def main():
    for r in [1, -1, 2, Fraction(1, 3), -Fraction(5, 2)]:
        check_conjugated_parity_operator(r)

    for triple in [(1, 2, 3), (-1, 2, 5), (Fraction(1,2), -3, Fraction(4,5)), (7, -2, -1)]:
        check_pair_sum_identities(*triple)

    print('PASS_EDGE_DEPENDENT_EQ3_OR3_MATCHGATE_GAUGE_BARRIER')
    print('Independent Hadamard-type edge parameters still cannot make OR3 parity-pure.')
    print('LOCAL_EDGE_GAUGE_ROUTE=CLOSED_ON_DEGREE3_3CLAUSE')
    print('E8_D1=EMPTY P_VS_NP=OPEN')


if __name__ == '__main__':
    main()
