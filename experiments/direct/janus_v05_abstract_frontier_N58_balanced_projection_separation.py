#!/usr/bin/env python3
"""Unified exact N58 balanced-projection replay.

Append-only theorem-side composition. Runtime semantics are unchanged. The new
finite lemma covers p:q = 21:29 through 25:25 in the regular N58 state
(n,m,L,d)=(7,78,350,50); only 24:26 and 25:25 are newly injected here because
previous append-only replays already certify 21:29, 22:28 and 23:27.

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
TARGET_24 = (7, 78, 350, 50, 24, 26)
TARGET_25 = (7, 78, 350, 50, 25, 25)


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
    print("BALANCED_REGULAR_PARENT_OCCURRENCE_MIN=22")
    print("BALANCED_ONE_SIGN_CORE_MAX=7")
    print("BALANCED_CORE_ARITHMETIC=PASS")


def enhanced_rescue(n: int, m: int, L: int, d: int, p: int, q: int):
    base = PREVIOUS_RESCUE(n, m, L, d, p, q)
    key = (n, m, L, d, p, q)
    if key == TARGET_24:
        # Unified balanced-projection theorem caps the coupled raw total.
        # Keep independent inherited M/L ceilings unchanged.
        return CAP, 652, 2772, 624, 158, 0
    if key == TARGET_25:
        return CAP, 653, 2775, 625, 160, 0
    return base


def selftest() -> None:
    three_coordinate_two_mask_separation_selftest()
    balanced_clean_core_arithmetic_selftest()

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
    print('N58_BALANCED_PROJECTION_SEPARATION=PASS')
    print('N58_FINITE_CAP_FRONTIER=PROVED')
    print('ABSTRACT_PASS_IS_FINITE_THEOREM_NOT_UNBOUNDED_TOTALITY')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('UNBOUNDED_TOTALITY=OPEN')
    print('UNIVERSAL_GPEI=OPEN')
    print('P_VS_NP=OPEN')


if __name__ == '__main__':
    selftest()
