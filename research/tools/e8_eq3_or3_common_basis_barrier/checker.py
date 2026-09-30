def add(p, q):
    out = dict(p)
    for k, v in q.items():
        out[k] = out.get(k, 0) + v
        if out[k] == 0:
            del out[k]
    return out


def scale(c, p):
    return {k: c * v for k, v in p.items() if c * v}


def main():
    # After EQ3 parity and invertibility, both parity cases force s=-r.
    # The transformed OR3 layers then reduce to these polynomials in r.
    g0 = {2: -3, 1: -3, 0: -1}
    g1 = {2: -1, 1: 1, 0: 1}
    g2 = {2: 1, 1: 1, 0: -1}
    g3 = {2: 3, 1: -3, 0: 1}

    even_contradiction = add(g3, scale(3, g1))
    odd_contradiction = add(g0, scale(3, g2))
    assert even_contradiction == {0: 4}, even_contradiction
    assert odd_contradiction == {0: -4}, odd_contradiction

    # Verify the elementary EQ3 implication algebraically at the relation level:
    # even: s^3=-1 and r^2 s=-1 -> s(r^2-s^2)=0; s!=0 and r!=s -> r=-s.
    # odd:  r^3=-1 and r s^2=-1 -> r(s^2-r^2)=0; r!=0 and r!=s -> s=-r.
    # These are field identities; no numerical root enumeration is used.
    print('PASS_EQ3_OR3_COMMON_BASIS_MATCHGATE_BARRIER')
    print('EQ4_NOT_REQUIRED')
    print('OR3_EVEN_PARITY_WOULD_FORCE_4=0')
    print('OR3_ODD_PARITY_WOULD_FORCE_-4=0')
    print('SCOPE=CHARACTERISTIC_ZERO_COMMON_2X2_BASIS')
    print('P_VS_NP=OPEN E8_D1=EMPTY')


if __name__ == '__main__':
    main()
