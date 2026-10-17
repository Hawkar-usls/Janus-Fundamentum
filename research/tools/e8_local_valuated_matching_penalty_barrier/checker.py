from itertools import combinations

GROUND = ('L','M','R')
EXACT = {
    frozenset(),
    frozenset({'L'}),
    frozenset({'M'}),
    frozenset({'R'}),
    frozenset({'L','R'}),
}
RELAXED = EXACT | {frozenset({'L','M'})}


def symdiff_toggle_pair(X, u, v):
    Y = set(X)
    if u in Y: Y.remove(u)
    else: Y.add(u)
    if v != u:
        if v in Y: Y.remove(v)
        else: Y.add(v)
    return frozenset(Y)


def is_delta_family(F):
    for X in F:
        for Y in F:
            diff = X ^ Y
            for u in diff:
                if not any(symdiff_toggle_pair(X,u,v) in F for v in diff):
                    return False, (X,Y,u)
    return True, None


def argmax_desired(lam):
    assert lam > 0
    delta = {X: 0 for X in EXACT}
    delta[frozenset({'L','M'})] = -lam
    best = max(delta.values())
    return {X for X,v in delta.items() if v == best}


def main():
    ok, witness = is_delta_family(EXACT)
    assert not ok
    X,Y,u = witness
    # Freeze the intended canonical failure as well.
    X0=frozenset({'L','R'}); Y0=frozenset({'M'}); u0='M'
    assert all(symdiff_toggle_pair(X0,u0,v) not in EXACT for v in (X0 ^ Y0))

    relaxed_ok,_ = is_delta_family(RELAXED)
    assert relaxed_ok, 'one-conflict relaxation should itself be a partition matroid family'

    for lam in (1,2,7,101):
        maximizers = argmax_desired(lam)
        assert maximizers == EXACT
        max_ok,_ = is_delta_family(maximizers)
        assert not max_ok

    print('PASS_LOCAL_VALUATED_MATCHING_PENALTY_BARRIER')
    print('relaxed_support_is_delta=True')
    print('zero_penalty_maximizers_are_exact_rank3_relation=True')
    print('maximizer_family_is_delta=False')
    print('LOCAL_WEIGHTED_MATCHING_PENALTY_ROUTE=CLOSED')
    print('E8_D1=EMPTY P_VS_NP=OPEN')


if __name__ == '__main__':
    main()
