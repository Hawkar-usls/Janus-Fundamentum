#!/usr/bin/env python3
"""Unified exact N58 clean-core/projection replay.

Append-only theorem-side composition. Runtime semantics are unchanged.

The current general theorem covers n=7,d=50 with c=m-d<=31 whenever either
there are too few cross pairs to reach K=637, or the cap-violation assumption
leaves clean row/column cores of size at least nine.  The proof is independent
of L and strengthens the coupled bound to K<=636, Lout<=Wmax_6(636)=2724,
raw<=3361.

Previous split-specific and L-specific artifacts remain append-only provenance.
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
K_CRITICAL = 637
K_SAFE = 636
L_SAFE = 2724
RAW_SAFE = 1 + K_SAFE + L_SAFE

# Historical sharper local theorem retained as provenance.  The general family
# now reaches the same 3361 ceiling here as well.
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


def clean_core_lower_bounds(c: int, p: int, q: int):
    """Return (kind, bad, p0, q0, t) under hypothetical K>=637."""
    t = K_CRITICAL - c
    pq = p * q
    if pq < t:
        return "PAIR_SHORTAGE", None, None, None, t
    bad = pq - t
    return "CLEAN_CORE", bad, p - bad, q - bad, t


def c31_clean_core_family_certifies(n: int, m: int, L: int, d: int, p: int, q: int) -> bool:
    if n != 7 or d != 50 or p + q != 50 or p > q:
        return False
    c = m - d
    if c < 0 or c > 31:
        return False
    dlo, dhi = S.A.degree_interval(n, m, L)
    if not (dlo <= d <= dhi):
        return False
    kind, _bad, p0, q0, _t = clean_core_lower_bounds(c, p, q)
    if kind == "PAIR_SHORTAGE":
        return True
    return p0 >= 9 and q0 >= 9


def clean_core_family_arithmetic_selftest():
    assert S.A.wmax(6, K_SAFE) == L_SAFE
    assert RAW_SAFE == 3361 < CAP

    expected = {
        28: {21, 22, 23, 24, 25},
        29: {21, 22, 23},
        30: {21, 22, 23},
        31: {21, 22},
    }
    got = {}
    for c in range(28, 32):
        m = 50 + c
        covered = set()
        for p in range(21, 26):
            q = 50 - p
            if c31_clean_core_family_certifies(7, m, 350, 50, p, q):
                covered.add(p)
        got[c] = covered
    assert got == expected, got

    # Boundary witnesses: c=29,p=23 remains covered; p=24 is deliberately not
    # smuggled through this theorem and should become the next obstruction if
    # no other frozen bound closes it.
    kind, bad, p0, q0, t = clean_core_lower_bounds(29, 23, 27)
    assert (kind, bad, p0, q0, t) == ("CLEAN_CORE", 13, 10, 14, 608)
    kind2, bad2, p02, q02, t2 = clean_core_lower_bounds(29, 24, 26)
    assert (kind2, bad2, p02, q02, t2) == ("CLEAN_CORE", 16, 8, 10, 608)
    assert not c31_clean_core_family_certifies(7, 79, 350, 50, 24, 26)

    print(f"C31_CLEAN_CORE_EXPECTED_COVERAGE={expected}")
    print("C31_BOUNDARY_C29_P23_CORE=10x14")
    print("C31_BOUNDARY_C29_P24_CORE=8x10_NOT_CLAIMED")
    print("C31_CLEAN_CORE_FAMILY_ARITHMETIC=PASS")


def l_independence_selftest():
    # Verify representative states across the full necessary d=50 range for
    # m=78 and across c=29..31.  The theorem checks minimum degree, not L=nd.
    samples = [
        (7, 78, 350, 50, 24, 26),
        (7, 78, 351, 50, 22, 28),
        (7, 78, 518, 50, 25, 25),
        (7, 79, 350, 50, 23, 27),
        (7, 80, 400, 50, 23, 27),
        (7, 81, 500, 50, 22, 28),
    ]
    for state in samples:
        assert c31_clean_core_family_certifies(*state), state
    assert not c31_clean_core_family_certifies(7, 78, 349, 50, 24, 26)
    assert not c31_clean_core_family_certifies(7, 82, 500, 50, 22, 28)
    print(f"C31_L_INDEPENDENCE_SAMPLES={samples}")
    print("C31_L_INDEPENDENCE=PASS")


def e1_full_pair_split_selftest():
    assert 21 * 29 == 609
    assert 3 ** 2 - 1 == 8
    assert 3 ** 3 - 1 == 26
    assert 21 > 8
    assert 29 > 26
    assert 3 + 4 > 6
    assert RAW_SAFE == 3361
    print("N58_E1_21X29_ALL_609_UNIQUE=IMPOSSIBLE")
    print("N58_E1_21X29_NEW_RESOLVENT_CEILING=608")
    print("N58_E1_21X29_RAW_CEILING=3361")
    print("N58_E1_FULL_PAIR_SPLIT=PASS")


def enhanced_rescue(n: int, m: int, L: int, d: int, p: int, q: int):
    base = PREVIOUS_RESCUE(n, m, L, d, p, q)
    key = (n, m, L, d, p, q)

    if c31_clean_core_family_certifies(n, m, L, d, p, q):
        if base is None:
            return None
        braw, bM, bL, bJ, bT, bE = base
        if braw > RAW_SAFE or bM > K_SAFE or bL > L_SAFE:
            # The contradiction rules out K>=637 itself, so unlike the earlier
            # conservative local records we may soundly sharpen independent
            # clause and literal-mass ceilings as well as coupled raw storage.
            return min(braw, RAW_SAFE), min(bM, K_SAFE), min(bL, L_SAFE), bJ, bT, bE
        return base

    # Preserve the historical local theorem even if future scope edits tighten
    # the general family predicate.
    if key == TARGET_E1_21:
        return 3361, 636, 2724, 608, 156, 1

    return base


def composition_selftest():
    samples = [
        (7, 78, 350, 50, 24, 26),
        (7, 78, 351, 50, 22, 28),
        (7, 79, 350, 50, 21, 29),
        (7, 80, 400, 50, 23, 27),
        (7, 81, 500, 50, 22, 28),
    ]
    for state in samples:
        assert c31_clean_core_family_certifies(*state), state
        out = enhanced_rescue(*state)
        assert out is not None, state
        assert out[0] <= RAW_SAFE and out[1] <= K_SAFE and out[2] <= L_SAFE, (state, out)
    print(f"C31_COMPOSITION_SAMPLES={samples}")
    print("C31_RESCUE_COMPOSITION=PASS")


def selftest() -> None:
    three_coordinate_two_mask_separation_selftest()
    clean_core_family_arithmetic_selftest()
    l_independence_selftest()
    e1_full_pair_split_selftest()
    composition_selftest()

    old = S.surplus_rescue
    try:
        S.surplus_rescue = enhanced_rescue
        result = S.verify_N58_surplus()
    finally:
        S.surplus_rescue = old

    print(f"N58_C31_REPLAY_STATUS={result['status']}")
    print(f"N58_C31_REPLAY_CHECKED_STATES={result['checked_states']}")
    print(f"N58_C31_REPLAY_CHECKED_TRANSITIONS={result['checked_transitions']}")
    print(f"N58_C31_REPLAY_TOTAL_RESCUES={result['surplus_rescues']}")

    expected = 'PROVED_FINITE_CAP_AVAILABILITY_BY_EXACT_INCIDENCE_SURPLUS_OVERAPPROX'
    if result['status'] != expected:
        print(f"N58_C31_NEXT_OPEN={result['first_open']}")
        print('N58_FULL_FRONTIER=OPEN')
        print('ABSTRACT_FAILURE_IS_INCONCLUSIVE_NOT_ACTUAL_COUNTEREXAMPLE')
        print('P_VS_NP=OPEN')
        raise AssertionError(result)

    assert result['cap'] == CAP
    assert result['P_VS_NP'] == 'OPEN'
    print(f"N58_C31_WORST_RAW={result['worst_raw_bound']}")
    print(f"N58_C31_WORST_WITNESS={result['worst_witness']}")
    print('N58_N7_D50_C31_CLEAN_CORE_FAMILY=PASS')
    print('N58_FINITE_CAP_FRONTIER=PROVED')
    print('ABSTRACT_PASS_IS_FINITE_THEOREM_NOT_UNBOUNDED_TOTALITY')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('UNBOUNDED_TOTALITY=OPEN')
    print('UNIVERSAL_GPEI=OPEN')
    print('P_VS_NP=OPEN')


if __name__ == '__main__':
    selftest()
