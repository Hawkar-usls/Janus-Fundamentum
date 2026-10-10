from fractions import Fraction
from itertools import product


def inv_transpose_2(S):
    a,c = S[0]
    b,d = S[1]
    det = a*d - b*c
    assert det != 0
    # (S^{-1})^T
    return [[d/det, -b/det],[-c/det, a/det]]


def transform_tensor(values, arity, T):
    out = {}
    for y in product((0,1), repeat=arity):
        total = Fraction(0)
        for x in product((0,1), repeat=arity):
            coeff = Fraction(1)
            for yi,xi in zip(y,x):
                coeff *= T[yi][xi]
            total += coeff * values(x)
        out[y] = total
    return out


def equality_values(d):
    return lambda x: Fraction(int(all(v == x[0] for v in x)))


def or3_values(x):
    return Fraction(int(any(x)))


def support_parities(sig):
    return {sum(x) % 2 for x,v in sig.items() if v != 0}


def symmetric_layers(sig, arity):
    vals = []
    for k in range(arity + 1):
        layer = {v for x,v in sig.items() if sum(x) == k}
        assert len(layer) == 1
        vals.append(next(iter(layer)))
    return vals


def check_case(a,b,variant):
    a,b = Fraction(a), Fraction(b)
    assert a and b
    if variant == 'A':
        S = [[a,a],[b,-b]]
        expected_eq3 = {0}
    else:
        S = [[a,-a],[b,b]]
        expected_eq3 = {1}
    R = inv_transpose_2(S)

    eq3 = transform_tensor(equality_values(3), 3, S)
    eq4 = transform_tensor(equality_values(4), 4, S)
    clause = transform_tensor(or3_values, 3, R)

    assert support_parities(eq3) == expected_eq3
    assert support_parities(eq4) == {0}
    assert support_parities(clause) == {0,1}
    layers = symmetric_layers(clause, 3)
    assert all(v != 0 for v in layers)
    print('variant', variant, 'a,b=', a,b, 'clause_layers=', layers, 'PASS')


def main():
    for a,b in [(1,1),(2,3),(-1,2)]:
        check_case(a,b,'A')
        check_case(a,b,'B')
    # Unnormalized Hadamard Fourier transform of positive OR3: [7,-1,-1,-1].
    H = [[Fraction(1),Fraction(1)],[Fraction(1),Fraction(-1)]]
    fhat = transform_tensor(or3_values,3,H)
    assert symmetric_layers(fhat,3) == [7,-1,-1,-1]
    assert support_parities(fhat) == {0,1}
    print('PASS: both forced common-basis families preserve matchgate parity for EQ3/EQ4 but dual OR3 violates matchgate parity')


if __name__ == '__main__':
    main()
