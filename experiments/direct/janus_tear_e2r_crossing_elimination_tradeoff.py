#!/usr/bin/env python3
"""Provider replay for C025-E2R-L1F one-crossing elimination mechanics."""
from itertools import product


def taut(c):
    return any(-x in c for x in c)


def canon(xs):
    c = frozenset(xs)
    return None if taut(c) else c


def resolve(p, q, pivot):
    if pivot not in p or -pivot not in q:
        return None
    return canon((p - {pivot}) | (q - {-pivot}))


def expand_one(c, e, a, b):
    if taut(c):
        return []
    if e in c and -e in c:
        return []
    if e in c:
        base = c - {e}
        out = []
        for lit in (a, b):
            x = canon(base | {lit})
            if x is not None and x not in out:
                out.append(x)
        return out
    if -e in c:
        x = canon((c - {-e}) | {-a, -b})
        return [] if x is None else [x]
    return [c]


def with_state(base, state, e):
    xs = set(base)
    if state:
        xs.add(e if state > 0 else -e)
    return frozenset(xs)


def main():
    e, a, b, y = 20, 1, 2, 10
    A, B = {3}, {4}

    for sa, sb in product((-1, 0, 1), repeat=2):
        p = with_state(A | {y}, sa, e)
        q = with_state(B | {-y}, sb, e)
        r = canon((p - {y}) | (q - {-y}))
        targets = [] if r is None else expand_one(r, e, a, b)
        ep, eq = expand_one(p, e, a, b), expand_one(q, e, a, b)
        for target in targets:
            witnesses = [
                resolve(pp, qq, y)
                for pp in ep for qq in eq
                if y in pp and -y in qq
            ]
            assert target in witnesses, (sa, sb, target, ep, eq, witnesses)

    p = frozenset({3, e})
    q = frozenset({4, -e})
    ep, eq = expand_one(p, e, a, b), expand_one(q, e, a, b)
    pa = next(c for c in ep if a in c)
    pb = next(c for c in ep if b in c)
    r1 = resolve(pa, eq[0], a)
    assert r1 == frozenset({3, 4, -b})
    r2 = resolve(pb, r1, b)
    assert r2 == frozenset({3, 4})

    defs = [
        frozenset({-e, a}),
        frozenset({-e, b}),
        frozenset({e, -a, -b}),
    ]
    assert all(expand_one(d, e, a, b) == [] for d in defs)
    assert len(expand_one(frozenset({3, e}), e, a, b)) <= 2
    assert len(expand_one(frozenset({3, -e}), e, a, b)) <= 2

    neighborhoods = [frozenset({1, 2}), frozenset({3, 4})]
    crossing = frozenset({1, 3})
    descendant = crossing | {2}
    assert not any(crossing <= n for n in neighborhoods)
    assert crossing <= descendant
    assert not any(descendant <= n for n in neighborhoods)

    print("C025_E2R_L1F_NON_E_PIVOT_ALL_POLARITY_CASES = PASS")
    print("C025_E2R_L1F_E_PIVOT_TWO_STEP_SIMULATION = PASS")
    print("C025_E2R_L1F_EXTENSION_DEFINITION_EVAPORATION = PASS")
    print("C025_E2R_L1F_ONE_GATE_LINE_MULTIPLIER_LE_2 = PASS")
    print("C025_E2R_L1F_LOCAL_DESCENDANT_OF_CROSSING_REJECTED_BY_SUPPORT = PASS")
    print("claim_boundary = finite elimination mechanics only; asymptotic tradeoff uses the external NW heavy-width lower bound")


if __name__ == "__main__":
    main()
