R = {0, 1, 2, 4, 5}  # empty,L,M,R,LR on bits 0,1,2


def twisted_family(T):
    return {x ^ T for x in R}


def nz(x):
    return bool(x)


def check_pattern(T):
    F = twisted_family(T)
    # Required zero/nonzero statuses in an untwisted elementary projection.
    Lh = 1 in F
    Mh = 2 in F
    Rh = 4 in F
    LM = 3 in F
    LR = 5 in F
    MR = 6 in F
    triple = 7 in F

    # Each Pfaffian term is classified only by whether both factors are required nonzero.
    t1 = LM and Rh      # a_LM a_Rh
    t2 = LR and Mh      # a_LR a_Mh
    t3 = Lh and MR      # a_Lh a_MR

    # The five valid twists are arranged so either exactly one term is forced nonzero
    # while triple must vanish, or all terms vanish while triple must be nonzero.
    forced_terms = sum((t1, t2, t3))
    if triple:
        assert forced_terms == 0, (T, F, forced_terms)
        verdict = 'TRIPLE_REQUIRED_NONZERO_BUT_ALL_PFAFFIAN_TERMS_ZERO'
    else:
        assert forced_terms == 1, (T, F, forced_terms)
        verdict = 'TRIPLE_REQUIRED_ZERO_BUT_ONE_PFAFFIAN_TERM_FORCED_NONZERO'
    return verdict


def main():
    valid_twists = sorted(R)
    results = []
    for T in valid_twists:
        F = twisted_family(T)
        assert 0 in F
        results.append((T, check_pattern(T)))
    assert len(results) == 5
    for T, v in results:
        print(f'twist={T:03b} {v} PASS')
    print('PASS_RANK3_SWITCH_NOT_ELEMENTARY_PROJECTED_LINEAR')
    print('USING_ELEMENTARY_PROJECTION_NORMAL_FORM=>NOT_PROJECTED_LINEAR')
    print('FIELD_SCOPE=ALL_FIELDS')
    print('P_VS_NP=OPEN E8_D1=EMPTY')


if __name__ == '__main__':
    main()
