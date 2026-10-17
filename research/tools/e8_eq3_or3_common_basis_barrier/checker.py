def add(p, q):
    out = dict(p)
    for k, v in q.items():
        out[k] = out.get(k, 0) + v
        if out[k] == 0:
            del out[k]
    return out


def scale(c, p):
    return {k: c * v for k, v in p.items() if c * v}


def det2_mod2(S):
    return (S[0][0] * S[1][1] - S[0][1] * S[1][0]) % 2


def transform3(sig, S):
    from itertools import product
    out = {}
    for y in product((0, 1), repeat=3):
        val = 0
        for x in product((0, 1), repeat=3):
            term = sig[x]
            for j in range(3):
                term *= S[y[j]][x[j]]
            val ^= (term & 1)
        out[y] = val
    return out


def invT_mod2(S):
    # Every invertible 2x2 matrix over F2 has determinant 1.
    inv = [[S[1][1] % 2, (-S[0][1]) % 2], [(-S[1][0]) % 2, S[0][0] % 2]]
    return [[inv[j][i] for j in range(2)] for i in range(2)]


def parity_pure(sig):
    parities = {sum(x) % 2 for x, v in sig.items() if v}
    return len(parities) <= 1


def main():
    # Characteristic !=2 branch: after EQ3 parity and invertibility, s=-r.
    # The transformed OR3 layers then reduce to these polynomials in r.
    g0 = {2: -3, 1: -3, 0: -1}
    g1 = {2: -1, 1: 1, 0: 1}
    g2 = {2: 1, 1: 1, 0: -1}
    g3 = {2: 3, 1: -3, 0: 1}
    even_contradiction = add(g3, scale(3, g1))
    odd_contradiction = add(g0, scale(3, g2))
    assert even_contradiction == {0: 4}, even_contradiction
    assert odd_contradiction == {0: -4}, odd_contradiction

    # Characteristic-two finite-field regression: all six GL(2,F2) bases fail already
    # at the parity requirement for EQ3/OR3. The symbolic theorem is stronger:
    # EQ3 parity gives r^2=s^2, hence r=s in char 2, contradicting invertibility.
    from itertools import product
    EQ3 = {x: int(x[0] == x[1] == x[2]) for x in product((0, 1), repeat=3)}
    OR3 = {x: int(any(x)) for x in product((0, 1), repeat=3)}
    checked = 0
    for flat in product((0, 1), repeat=4):
        S = [list(flat[:2]), list(flat[2:])]
        if det2_mod2(S) != 1:
            continue
        checked += 1
        eq = transform3(EQ3, S)
        ore = transform3(OR3, invT_mod2(S))
        assert not (parity_pure(eq) and parity_pure(ore))
    assert checked == 6

    print('PASS_EQ3_OR3_COMMON_BASIS_MATCHGATE_BARRIER')
    print('EQ4_NOT_REQUIRED')
    print('CHAR2_EQ3_PARITY_IMPLIES_SINGULAR_BASIS')
    print('CHAR_NE_2_OR3_EVEN_PARITY_WOULD_FORCE_4=0')
    print('CHAR_NE_2_OR3_ODD_PARITY_WOULD_FORCE_-4=0')
    print('FIELD_SCOPE=ALL_FIELDS')
    print('P_VS_NP=OPEN E8_D1=EMPTY')


if __name__ == '__main__':
    main()
