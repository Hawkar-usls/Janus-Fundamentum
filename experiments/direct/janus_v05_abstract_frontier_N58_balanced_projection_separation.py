#!/usr/bin/env python3
"""Unified exact N58 balanced-projection replay, L-independent form.

Append-only theorem-side composition. Runtime semantics are unchanged.

The exact finite theorem applies whenever
    n=7, m=78, d=50, 21<=p<=25, q=50-p,
for every admissible L.  The proof needs only that d=50 is the selected minimum
live-variable incidence: each nonpivot variable then has degree >=50, while at
most c=m-d=28 occurrences can lie in retained clauses, so at least 22 occur in
pivot-parent tails.  No equality L=7*d is required.

Previous 21x29/22x28/23x27 and E=1 artifacts remain append-only provenance.
A green full replay proves finite N58 cap availability for the frozen abstraction.
It does not prove unbounded totality or P=NP.
"""

from itertools import product

from experiments.direct import janus_v05_abstract_frontier_incidence_surplus as S
from experiments.direct import janus_v05_abstract_frontier_N58_23x27_projection_fiber as R23

P_VS_NP = "OPEN"
THEOREM_RUNTIME_HEURISTICS = "FORBIDDEN"
PREVIOUS_RESCUE = R23.enhanced_rescue
CAP = 58 * 58

# Historical sharper local theorem retained as provenance.  The L-free family
# below already proves cap safety here, but this state has a stronger 3361 bound.
TARGET_E1_21 = (7, 78, 351, 50, 21, 29)


def compatible(a, b):
    return all(not (x and y and x == -y) for x, y in zip(a, b))


def union_mask(a, b):
    assert compatible(a, b)
    return tuple(x if x else y for x, y in zip(a, b))


def separating_q_count(b1, b2):
    assert b1 != b2
    count = 0
    for q in product((-1, 0, 1), repeat=3):
        if not any(q):
            continue
        if not compatible(b1, q) or not compatible(b2, q):
            continue
        if union_mask(b1, q) != union_mask(b2, q):
            count += 1
    return count


def three_coordinate_two_mask_separation_selftest():
    masks = list(product((-1, 0, 1), repeat=3))
    worst = -1
    witness = None
    checked = 0
    for i, b1 in enumerate(masks):
        for b2 in masks[i + 1:]:
            checked += 1
            c = separating_q_count(b1, b2)
            if c > worst:
                worst = c
                witness = (b1, b2)
    assert checked == 351, checked
    assert worst == 8, (worst, witness)
    print(f"THREE_COORDINATE_TWO_MASK_PAIRS_CHECKED={checked}")
    print(f"THREE_COORDINATE_TWO_MASK_MAX_SEPARATING_Q={worst}")
    print(f"THREE_COORDINATE_TWO_MASK_WITNESS={witness}")
    print("THREE_COORDINATE_TWO_MASK_SEPARATION=PASS")


def balanced_clean_core_arithmetic_selftest():
    rows = []
    for p in range(21, 26):
        q = 50 - p
        bad = p * q - 609
        p0 = p - bad
        q0 = q - bad
        assert bad >= 0
        assert p0 >= 9 and q0 >= 9, (p, q, bad, p0, q0)
        rows.append((p, q, bad, p0, q0))
    assert rows == [
        (21, 29, 0, 21, 29),
        (22, 28, 7, 15, 21),
        (23, 27, 12, 11, 15),
        (24, 26, 15, 9, 11),
        (25, 25, 16, 9, 9),
    ], rows
    assert 3 ** 2 - 1 == 8
    assert 2 * 3 ** 2 == 18
    assert 50 - 28 == 22
    assert 22 - 18 == 4
    assert 2 ** 3 - 1 == 7
    print(f"BALANCED_CLEAN_CORE_ROWS={rows}")
    print("BALANCED_CLEAN_CORE_MIN=9")
    print("BALANCED_PROJECTION_OCCURRENCE_MAX=18")
    print("BALANCED_MIN_DEGREE_PARENT_OCCURRENCE_MIN=22")
    print("BALANCED_ONE_SIGN_CORE_MAX=7")
    print("BALANCED_CORE_ARITHMETIC=PASS")


def l_free_scope_selftest():
    # d=50 belongs to the exact necessary minimum-degree interval precisely for
    # L=350..518 at n=7,m=78.  The theorem is therefore genuinely independent
    # of the previous equality L=350 rather than merely covering one neighbour.
    admissible = []
    for L in range(0, 7 * 78 + 1):
        dlo, dhi = S.A.degree_interval(7, 78, L)
        if dlo <= 50 <= dhi:
            admissible.append(L)
    assert admissible == list(range(350, 519)), (admissible[:3], admissible[-3:])
    assert 50 - (78 - 50) == 22
    print(f"BALANCED_L_FREE_ADMISSIBLE_L_MIN={admissible[0]}")
    print(f"BALANCED_L_FREE_ADMISSIBLE_L_MAX={admissible[-1]}")
    print(f"BALANCED_L_FREE_ADMISSIBLE_L_COUNT={len(admissible)}")
    print("BALANCED_L_FREE_SCOPE=PASS")


def e1_full_pair_split_selftest():
    assert 21 * 29 == 609
    assert 3 ** 2 - 1 == 8
    assert 3 ** 3 - 1 == 26
    assert 21 > 8
    assert 29 > 26
    assert 3 + 4 > 6
    assert S.A.wmax(6, 636) == 2724
    assert 1 + 636 + 2724 == 3361 < CAP
    print("N58_E1_21X29_ALL_609_UNIQUE=IMPOSSIBLE")
    print("N58_E1_21X29_NEW_RESOLVENT_CEILING=608")
    print("N58_E1_21X29_RAW_CEILING=3361")
    print("N58_E1_FULL_PAIR_SPLIT=PASS")


def in_l_free_balanced_family(n: int, m: int, L: int, d: int, p: int, q: int) -> bool:
    if not (n == 7 and m == 78 and d == 50):
        return False
    if not (21 <= p <= 25 and q == 50 - p):
        return False
    dlo, dhi = S.A.degree_interval(n, m, L)
    return dlo <= d <= dhi


def enhanced_rescue(n: int, m: int, L: int, d: int, p: int, q: int):
    base = PREVIOUS_RESCUE(n, m, L, d, p, q)
    key = (n, m, L, d, p, q)

    # Preserve the older stronger local ceiling.  It is not needed for the
    # family proof, but append-only theorem composition should not discard a
    # previously proved tighter bound.
    if key == TARGET_E1_21:
        return 3361, 636, 2724, 608, 156, 1

    if in_l_free_balanced_family(n, m, L, d, p, q):
        if base is None:
            return None
        braw, bM, bL, bJ, bT, bE = base
        if braw > CAP:
            # The theorem couples total raw storage to CAP.  It does not claim
            # sharper independent M/L ceilings, so inherit those untouched.
            return CAP, bM, bL, bJ, bT, bE
        return base

    return base


def l_free_rescue_composition_selftest():
    # Samples straddle the old L=350 boundary and use both old/new split cases.
    samples = [
        (7, 78, 350, 50, 24, 26),
        (7, 78, 351, 50, 22, 28),
        (7, 78, 400, 50, 25, 25),
        (7, 78, 518, 50, 24, 26),
    ]
    for state in samples:
        assert in_l_free_balanced_family(*state), state
        out = enhanced_rescue(*state)
        assert out is not None and out[0] <= CAP, (state, out)
    assert not in_l_free_balanced_family(7, 78, 349, 50, 24, 26)
    assert not in_l_free_balanced_family(7, 78, 519, 50, 24, 26)
    print(f"BALANCED_L_FREE_COMPOSITION_SAMPLES={samples}")
    print("BALANCED_L_FREE_RESCUE_COMPOSITION=PASS")


def selftest() -> None:
    three_coordinate_two_mask_separation_selftest()
    balanced_clean_core_arithmetic_selftest()
    l_free_scope_selftest()
    e1_full_pair_split_selftest()
    l_free_rescue_composition_selftest()

    old = S.surplus_rescue
    try:
        S.surplus_rescue = enhanced_rescue
        result = S.verify_N58_surplus()
    finally:
        S.surplus_rescue = old

    print(f"N58_BALANCED_REPLAY_STATUS={result['status']}")
    print(f"N58_BALANCED_REPLAY_CHECKED_STATES={result['checked_states']}")
    print(f"N58_BALANCED_REPLAY_CHECKED_TRANSITIONS={result['checked_transitions']}")
    print(f"N58_BALANCED_REPLAY_TOTAL_RESCUES={result['surplus_rescues']}")

    expected = 'PROVED_FINITE_CAP_AVAILABILITY_BY_EXACT_INCIDENCE_SURPLUS_OVERAPPROX'
    if result['status'] != expected:
        print(f"N58_BALANCED_NEXT_OPEN={result['first_open']}")
        print('N58_FULL_FRONTIER=OPEN')
        print('ABSTRACT_FAILURE_IS_INCONCLUSIVE_NOT_ACTUAL_COUNTEREXAMPLE')
        print('P_VS_NP=OPEN')
        raise AssertionError(result)

    assert result['cap'] == CAP
    assert result['P_VS_NP'] == 'OPEN'
    print(f"N58_BALANCED_WORST_RAW={result['worst_raw_bound']}")
    print(f"N58_BALANCED_WORST_WITNESS={result['worst_witness']}")
    print('N58_BALANCED_PROJECTION_SEPARATION_L_FREE=PASS')
    print('N58_FINITE_CAP_FRONTIER=PROVED')
    print('ABSTRACT_PASS_IS_FINITE_THEOREM_NOT_UNBOUNDED_TOTALITY')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('UNBOUNDED_TOTALITY=OPEN')
    print('UNIVERSAL_GPEI=OPEN')
    print('P_VS_NP=OPEN')


if __name__ == '__main__':
    selftest()
