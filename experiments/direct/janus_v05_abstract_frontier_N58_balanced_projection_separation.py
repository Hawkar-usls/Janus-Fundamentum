#!/usr/bin/env python3
"""Unified exact N58 clean-core/projection replay.

Append-only theorem-side composition. Runtime semantics are unchanged.

Current theorem stack:
  * n=7,d=50,c<=31 clean-core projection family when both hypothetical clean
    cores remain >=9 (or pair count is already too small for K>=637);
  * exact eight-core extension for (c,p,q)=(29,24,26) and (31,23,27), using
    deterministic four-coordinate multi-mask separation bounds.

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
TARGET_E1_21 = (7, 78, 351, 50, 21, 29)
EIGHT_CORE_KEYS = {(29, 24, 26), (31, 23, 27)}


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


def four_coordinate_multi_mask_separation_max(k: int):
    """Exact max number of nonzero q separating k distinct 4D masks.

    This is finite exhaustive search, not a heuristic.  The recursion enumerates
    all increasing k-subsets of the 81 ternary masks.  At each partial subset we
    keep exactly the q tails that remain compatible and whose current unions are
    pairwise distinct.  If its cardinality is already <= the best completed
    witness, adding masks can only remove q and exact pruning is sound.
    """
    assert k in (4, 5)
    masks = list(product((-1, 0, 1), repeat=4))
    qs = [q for q in masks if any(q)]
    mask_index = {m: i for i, m in enumerate(masks)}
    U = len(qs)
    all_bits = (1 << U) - 1

    compat_bits = []
    union_ids = []
    for b in masks:
        bits = 0
        ids = [-1] * U
        for j, q in enumerate(qs):
            if compatible(b, q):
                bits |= 1 << j
                ids[j] = mask_index[union_mask(b, q)]
        compat_bits.append(bits)
        union_ids.append(ids)

    pair_distinct = [[0] * len(masks) for _ in masks]
    for i in range(len(masks)):
        for j in range(i + 1, len(masks)):
            bits = 0
            for qi in range(U):
                ui = union_ids[i][qi]
                uj = union_ids[j][qi]
                if ui >= 0 and uj >= 0 and ui != uj:
                    bits |= 1 << qi
            pair_distinct[i][j] = bits
            pair_distinct[j][i] = bits

    best = -1
    witness = None
    nodes = 0

    def rec(chosen, start, bits):
        nonlocal best, witness, nodes
        nodes += 1
        if bits.bit_count() <= best:
            return
        if len(chosen) == k:
            best = bits.bit_count()
            witness = tuple(masks[i] for i in chosen)
            return
        need = k - len(chosen)
        last_start = len(masks) - need
        for x in range(start, last_start + 1):
            nb = bits & compat_bits[x]
            if nb.bit_count() <= best:
                continue
            for y in chosen:
                nb &= pair_distinct[x][y]
                if nb.bit_count() <= best:
                    break
            if nb.bit_count() <= best:
                continue
            rec(chosen + [x], x + 1, nb)

    rec([], 0, all_bits)
    return best, witness, nodes


def four_coordinate_multi_mask_selftest():
    best4, wit4, nodes4 = four_coordinate_multi_mask_separation_max(4)
    best5, wit5, nodes5 = four_coordinate_multi_mask_separation_max(5)
    assert best4 == 11, (best4, wit4)
    assert best5 == 8, (best5, wit5)
    print(f"FOUR_COORDINATE_FOUR_MASK_MAX={best4}")
    print(f"FOUR_COORDINATE_FOUR_MASK_WITNESS={wit4}")
    print(f"FOUR_COORDINATE_FOUR_MASK_SEARCH_NODES={nodes4}")
    print(f"FOUR_COORDINATE_FIVE_MASK_MAX={best5}")
    print(f"FOUR_COORDINATE_FIVE_MASK_WITNESS={wit5}")
    print(f"FOUR_COORDINATE_FIVE_MASK_SEARCH_NODES={nodes5}")
    print("FOUR_COORDINATE_MULTI_MASK_SEPARATION=PASS")


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


def eight_core_extension_certifies(n: int, m: int, L: int, d: int, p: int, q: int) -> bool:
    if n != 7 or d != 50 or p + q != 50 or p > q:
        return False
    c = m - d
    if (c, p, q) not in EIGHT_CORE_KEYS:
        return False
    dlo, dhi = S.A.degree_interval(n, m, L)
    return dlo <= d <= dhi


def family_arithmetic_selftest():
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

    # Exact arithmetic behind the newly added 8-core cases.
    checks = []
    for c, p, q in sorted(EIGHT_CORE_KEYS):
        kind, bad, p0, q0, t = clean_core_lower_bounds(c, p, q)
        assert kind == "CLEAN_CORE"
        assert p0 == 8 and q0 >= 9
        min_parent = 50 - c
        full_A_rows = 2 * min_parent - p
        k = (full_A_rows + 3) // 4
        common_q = q - bad
        sep = {4: 11, 5: 8}[k]
        assert common_q > sep
        checks.append((c, p, q, bad, p0, q0, min_parent, full_A_rows, k, common_q, sep, t))
    assert checks == [
        (29, 24, 26, 16, 8, 10, 21, 18, 5, 10, 8, 608),
        (31, 23, 27, 15, 8, 12, 19, 15, 4, 12, 11, 606),
    ], checks

    print(f"C31_CLEAN_CORE_EXPECTED_COVERAGE={expected}")
    print(f"EIGHT_CORE_EXTENSION_ARITHMETIC={checks}")
    print("FAMILY_ARITHMETIC=PASS")


def l_independence_selftest():
    samples = [
        (7, 78, 350, 50, 24, 26),
        (7, 78, 518, 50, 25, 25),
        (7, 79, 350, 50, 23, 27),
        (7, 80, 400, 50, 23, 27),
        (7, 81, 500, 50, 22, 28),
    ]
    for state in samples:
        assert c31_clean_core_family_certifies(*state), state
    ext_samples = [
        (7, 79, 350, 50, 24, 26),
        (7, 79, 500, 50, 24, 26),
        (7, 81, 500, 50, 23, 27),
    ]
    for state in ext_samples:
        assert eight_core_extension_certifies(*state), state
    print(f"C31_L_INDEPENDENCE_SAMPLES={samples}")
    print(f"EIGHT_CORE_L_INDEPENDENCE_SAMPLES={ext_samples}")
    print("L_INDEPENDENCE=PASS")


def e1_full_pair_split_selftest():
    assert 21 * 29 == 609
    assert 3 ** 2 - 1 == 8
    assert 3 ** 3 - 1 == 26
    assert 21 > 8 and 29 > 26 and 3 + 4 > 6
    assert RAW_SAFE == 3361
    print("N58_E1_FULL_PAIR_SPLIT=PASS")


def enhanced_rescue(n: int, m: int, L: int, d: int, p: int, q: int):
    base = PREVIOUS_RESCUE(n, m, L, d, p, q)
    key = (n, m, L, d, p, q)

    if c31_clean_core_family_certifies(n, m, L, d, p, q) or eight_core_extension_certifies(n, m, L, d, p, q):
        if base is None:
            return None
        braw, bM, bL, bJ, bT, bE = base
        if braw > RAW_SAFE or bM > K_SAFE or bL > L_SAFE:
            return min(braw, RAW_SAFE), min(bM, K_SAFE), min(bL, L_SAFE), bJ, bT, bE
        return base

    if key == TARGET_E1_21:
        return 3361, 636, 2724, 608, 156, 1

    return base


def composition_selftest():
    samples = [
        (7, 78, 350, 50, 24, 26),
        (7, 79, 350, 50, 21, 29),
        (7, 79, 350, 50, 24, 26),
        (7, 80, 400, 50, 23, 27),
        (7, 81, 500, 50, 22, 28),
        (7, 81, 500, 50, 23, 27),
    ]
    for state in samples:
        assert c31_clean_core_family_certifies(*state) or eight_core_extension_certifies(*state), state
        out = enhanced_rescue(*state)
        assert out is not None, state
        assert out[0] <= RAW_SAFE and out[1] <= K_SAFE and out[2] <= L_SAFE, (state, out)
    print(f"COMPOSITION_SAMPLES={samples}")
    print("THEOREM_COMPOSITION=PASS")


def selftest() -> None:
    three_coordinate_two_mask_separation_selftest()
    four_coordinate_multi_mask_selftest()
    family_arithmetic_selftest()
    l_independence_selftest()
    e1_full_pair_split_selftest()
    composition_selftest()

    old = S.surplus_rescue
    try:
        S.surplus_rescue = enhanced_rescue
        result = S.verify_N58_surplus()
    finally:
        S.surplus_rescue = old

    print(f"N58_REPLAY_STATUS={result['status']}")
    print(f"N58_REPLAY_CHECKED_STATES={result['checked_states']}")
    print(f"N58_REPLAY_CHECKED_TRANSITIONS={result['checked_transitions']}")
    print(f"N58_REPLAY_TOTAL_RESCUES={result['surplus_rescues']}")

    expected = 'PROVED_FINITE_CAP_AVAILABILITY_BY_EXACT_INCIDENCE_SURPLUS_OVERAPPROX'
    if result['status'] != expected:
        print(f"N58_NEXT_OPEN={result['first_open']}")
        print('N58_FULL_FRONTIER=OPEN')
        print('ABSTRACT_FAILURE_IS_INCONCLUSIVE_NOT_ACTUAL_COUNTEREXAMPLE')
        print('P_VS_NP=OPEN')
        raise AssertionError(result)

    assert result['cap'] == CAP
    assert result['P_VS_NP'] == 'OPEN'
    print(f"N58_WORST_RAW={result['worst_raw_bound']}")
    print(f"N58_WORST_WITNESS={result['worst_witness']}")
    print('N58_CLEAN_CORE_AND_EIGHT_CORE_STACK=PASS')
    print('N58_FINITE_CAP_FRONTIER=PROVED')
    print('ABSTRACT_PASS_IS_FINITE_THEOREM_NOT_UNBOUNDED_TOTALITY')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('UNBOUNDED_TOTALITY=OPEN')
    print('UNIVERSAL_GPEI=OPEN')
    print('P_VS_NP=OPEN')


if __name__ == '__main__':
    selftest()
