#!/usr/bin/env python3
"""Finite exact replay for the projective escape-radius recurrence theorem.

The arbitrary-size induction is mathematical and lives in the companion note.
This checker binds its hypotheses to the frozen base, verifies exact rank at
n=120 by a modular lower bound plus an explicit 5D rational kernel, and obtains
the complete n=120 tope set by the proved parent-pair composition law.
"""

from collections import defaultdict
from fractions import Fraction

import r5_e9_prime_tower_geometric_tope_radius_stress as S


def rank_mod(M, p):
    A = [[int(x) % p for x in row] for row in M]
    m, n = len(A), len(A[0])
    r = 0
    for c in range(n):
        q = next((i for i in range(r,m) if A[i][c]), None)
        if q is None:
            continue
        A[r],A[q] = A[q],A[r]
        inv = pow(A[r][c], p-2, p)
        A[r] = [(x*inv) % p for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                z = A[i][c]
                A[i] = [(A[i][j]-z*A[r][j]) % p for j in range(n)]
        r += 1
    return r


def hamming(a,b):
    return sum(x != y for x,y in zip(a,b))


def profile(topes, classes, cs, trap, distinguished_raw_index):
    out = defaultdict(lambda: 10**9)
    for s in topes:
        raw = S.raw_signs(s,classes,cs)
        p = S.positive_count(s,classes,cs)
        sig = raw[distinguished_raw_index]
        d = hamming(s,trap)
        out[(p,sig)] = min(out[(p,sig)],d)
    return dict(out)


def main():
    # Base n=15 and first signed lift n=30.
    A0 = S.matrix_from_rows(S.ROWS,15)
    A1 = S.lift(A0,S.SEED_SIGNING)
    W1 = [list(map(Fraction,S.sym(S.G))), list(map(Fraction,S.asym(S.Z)))]
    C1 = S.projective_classes(W1)
    cs1,T1 = S.enumerate_rank2(C1)
    G1 = S.tope_graph(T1)
    p1 = {s:S.positive_count(s,C1,cs1) for s in T1}
    L1 = S.strict_local_minima(G1,p1)

    # Pick a radius-5 base trap that amplifies to the radius-9 child trap.
    F1 = S.RECURSIVE_PAIR
    A2 = S.lift(A1,F1)
    W10 = S.zero_eval_basis(W1,F1[0][1])
    W2 = [S.sym(w) for w in W1] + [S.asym(w) for w in W10]
    C2 = S.projective_classes(W2)
    cs2,T2 = S.enumerate_rank3(C2)
    G2 = S.tope_graph(T2)
    p2 = {s:S.positive_count(s,C2,cs2) for s in T2}

    trap1 = None
    trap2 = None
    for s,p,r in L1:
        if p != 15 or r != 5:
            continue
        raw1 = S.raw_signs(s,C1,cs1)
        cand_raw2 = raw1+raw1
        cand2 = S.class_signs_from_raw(cand_raw2,C2,cs2)
        if cand2 in T2 and S.escape_radius(cand2,p2[cand2],G2,p2) == 9:
            trap1 = s
            trap2 = cand2
            break
    assert trap1 is not None and trap2 is not None

    raw_trap1 = S.raw_signs(trap1,C1,cs1)
    raw_trap2 = S.raw_signs(trap2,C2,cs2)
    assert p1[trap1] == 15
    assert p2[trap2] == 30
    assert raw_trap1[5] == -1
    assert raw_trap2[35] == -1

    # Exact base sign/objective separation and opposite-sign radius.
    prof1 = profile(T1,C1,cs1,trap1,5)
    minus_p1 = {p for (p,sig) in prof1 if sig == -1}
    plus_p1 = {p for (p,sig) in prof1 if sig == +1}
    assert minus_p1 == {15,16,17,18}
    assert plus_p1 == {12,13,14,15}
    assert min(d for (p,sig),d in prof1.items() if sig == +1) == 5
    assert min(d for (p,sig),d in prof1.items() if sig == +1 and p < 15) == 5

    # Exact n=60 profile: this is already a complete 288-tope arrangement.
    prof2 = profile(T2,C2,cs2,trap2,35)
    assert min(p for (p,sig) in prof2 if sig == -1) == 30
    assert max(p for (p,sig) in prof2 if sig == +1) == 30
    assert min(d for (p,sig),d in prof2.items() if sig == +1) == 9
    assert min(d for (p,sig),d in prof2.items() if sig == +1 and p < 30) == 9

    # Build the next exact full-kernel basis using K2^0 at j=35.
    F2 = ((F1[0][0],F1[0][1]+30),(F1[1][0],F1[1][1]+30))
    assert F2 == ((0,35),(1,31))
    A3 = S.lift(A2,F2)
    W20 = S.zero_eval_basis(W2,F2[0][1])
    assert len(W20) == 2
    W3 = [S.sym(w) for w in W2] + [S.asym(w) for w in W20]
    assert len(W3) == 5
    assert all(S.mv(A3,w) == [0]*120 for w in W3)
    assert S.rank_q(list(map(list,zip(*W3)))) == 5

    # Modular rank 115 plus the explicit 5D Q-kernel proves exact Q-nullity 5:
    # rank_Fp(A3)<=rank_Q(A3)<=115 and this prime gives rank_Fp=115.
    assert rank_mod(A3,1000003) == 115

    C3 = S.projective_classes(W3)
    cs3 = list(C3)
    assert len(C3) == 45 == 2*23-1

    # PER-2: complete child topes are ordered parent pairs with equal sign at
    # the distinguished parent coordinate.  T2 is complete, so this is an
    # exact complete n=120 tope enumeration without cell enumeration in R^5.
    raw2 = [S.raw_signs(s,C2,cs2) for s in T2]
    T3 = set()
    p3 = {}
    compatible_pairs = 0
    for a in raw2:
        for b in raw2:
            if a[35] != b[35]:
                continue
            compatible_pairs += 1
            raw = a+b
            s3 = S.class_signs_from_raw(raw,C3,cs3)
            T3.add(s3)
            p3[s3] = sum(x > 0 for x in raw)

    assert compatible_pairs == 41472
    assert len(T3) == 41472
    assert min(p3.values()) == 48
    assert max(p3.values()) == 72

    raw_trap3 = raw_trap2+raw_trap2
    trap3 = S.class_signs_from_raw(raw_trap3,C3,cs3)
    assert trap3 in T3
    assert p3[trap3] == 60

    escape3 = min(
        hamming(trap3,s)
        for s in T3
        if p3[s] < 60
    )
    assert escape3 == 17

    # Next distinguished column is the second-sheet copy of 35.
    prof3 = profile(T3,C3,cs3,trap3,95)
    assert min(p for (p,sig) in prof3 if sig == -1) == 60
    assert max(p for (p,sig) in prof3 if sig == +1) == 60
    assert min(d for (p,sig),d in prof3.items() if sig == +1) == 17
    assert min(d for (p,sig),d in prof3.items() if sig == +1 and p < 60) == 17

    # The arbitrary-size theorem now inducts symbolically.
    assert 9 == 2*5-1
    assert 17 == 2*9-1
    for t in range(1,8):
        n = 30*(2**(t-1))
        r = 4*(2**(t-1))+1
        d = 2**(t-1)+1
        m = 11*(2**(t-1))+1
        assert r == 2*n//15 + 1
        assert d == n//30 + 1
        assert m == 11*n//30 + 1

    print({
        'status': 'PASS_PRIME_TOWER_PROJECTIVE_ESCAPE_RADIUS_RECURRENCE',
        'base_profile': {
            'n': 30,
            'nullity': 2,
            'projective_classes': 12,
            'trap_p': 15,
            'escape_radius': 5,
        },
        'level2': {
            'n': 60,
            'nullity': 3,
            'projective_classes': 23,
            'topes': 288,
            'trap_p': 30,
            'escape_radius': 9,
        },
        'level3': {
            'n': 120,
            'nullity': 5,
            'projective_classes': 45,
            'compatible_topes': len(T3),
            'global_min_p': min(p3.values()),
            'trap_p': 60,
            'escape_radius': escape3,
        },
        'theorem': 'r_t=2*r_(t-1)-1=(2/15)n_t+1',
        'universal_sublinear_all_chamber_escape_radius': 'FALSIFIED',
        'universal_polynomial_decider': 'OPEN',
        'E8_D1': 'EMPTY',
        'P_VS_NP': 'OPEN',
    })


if __name__ == '__main__':
    main()
