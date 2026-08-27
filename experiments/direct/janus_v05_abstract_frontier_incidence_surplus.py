#!/usr/bin/env python3
"""N58 theorem-side verifier with minimum-incidence surplus occupancy coupling.

No runtime semantics change.  The refinement is invoked only when the inherited
resource-simplex/global-raw transfer is over cap.  A failed abstract check is
inconclusive and is not an actual CNF counterexample.  P vs NP remains OPEN.
"""

from functools import lru_cache

from experiments.direct import janus_v05_abstract_frontier_support_mass as A
from experiments.direct import janus_v05_abstract_frontier_global_raw_universe as G

P_VS_NP = "OPEN"
THEOREM_RUNTIME_HEURISTICS = "FORBIDDEN"


@lru_cache(maxsize=None)
def surplus_new_resolvent_ceiling(n: int, m: int, L: int, d: int, p: int, q: int):
    assert p + q == d
    E = L - n * d
    assert E >= 0
    if p == 0 or q == 0:
        return 0, 0, E

    r = n - 1
    c = m - d
    pq = p * q
    if c == 0:
        Tlo = Thi = 0
    else:
        Tlo = max(2 * c, E)
        Thi = min(c * r, L - 2 * d)
        if Thi < Tlo:
            return None

    best_J = 0
    worst_T = Tlo
    max_new = max(0, 3 ** r - c)

    for T in range(Tlo, Thi + 1):
        omitted_pair_support = (c * (T - E)) // 4
        support_lower = r * pq - omitted_pair_support
        lo, hi = 0, min(pq, max_new)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            support_upper = A.wmax(r, c + mid) - T + (pq - mid) * r
            if support_upper >= support_lower:
                lo = mid
            else:
                hi = mid - 1
        if lo > best_J:
            best_J = lo
            worst_T = T

    return best_J, worst_T, E


def surplus_rescue(n: int, m: int, L: int, d: int, p: int, q: int):
    result = surplus_new_resolvent_ceiling(n, m, L, d, p, q)
    if result is None:
        return None
    J, T, E = result
    r = n - 1
    c = m - d
    K = min(c + J, 3 ** r)
    Lcap = A.wmax(r, K)
    raw = 1 + K + Lcap
    return raw, K, Lcap, J, T, E


def add_box(boxes, M: int, L: int, S: int) -> None:
    if M < 7 or L < 14 or S < 22:
        return
    if any(a >= M and b >= L and c >= S for a, b, c in boxes):
        return
    boxes[:] = [(a, b, c) for a, b, c in boxes if not (M >= a and L >= b and S >= c)]
    boxes.append((M, L, S))


def verify_N58_surplus() -> dict:
    N = 58
    previous_frontier = 57
    cap = N * N
    roots = A.hard_roots(N)
    max_n = max(roots, default=A.TAIL_N)
    boxes = {n: [] for n in range(7, max_n + 1)}
    rootsets = {n: set(rows) for n, rows in roots.items()}
    checked_states = checked_transitions = rescues = 0
    worst_raw = -1
    worst_witness = None
    layer_counts = {}

    for n in range(max_n, 6, -1):
        candidates = set(rootsets.get(n, set()))
        bs = boxes[n]
        maxM = max((M for M, _, _ in bs), default=0)
        for m in range(7, maxM + 1):
            Lcap = max((min(Lb, Sb - 1 - m) for M, Lb, Sb in bs if M >= m), default=-1)
            if Lcap < 0:
                continue
            Llo = max(2 * m, n, previous_frontier - n - m)
            Lhi = min(Lcap, n * m, cap - 1 - m)
            if Llo > Lhi:
                continue
            for L in range(Llo, Lhi + 1):
                dlo, dhi = A.degree_interval(n, m, L)
                if dlo <= dhi:
                    candidates.add((m, L))
        layer_counts[n] = len(candidates)

        for m, L in sorted(candidates):
            checked_states += 1
            dlo, dhi = A.degree_interval(n, m, L)
            for d in range(dlo, dhi + 1):
                for p in range(0, d // 2 + 1):
                    q = d - p
                    checked_transitions += 1
                    raw, M, Lb, R = G.transfer_bounds_global(n, m, L, d, p, q)
                    rescue_meta = None
                    if raw > cap:
                        sr = surplus_rescue(n, m, L, d, p, q)
                        if sr is not None:
                            sraw, sM, sL, J, T, E = sr
                            if sraw < raw:
                                raw, M, Lb, R = sraw, sM, min(Lb, sL), J
                                rescues += 1
                                rescue_meta = {"kind": "MIN_INCIDENCE_SURPLUS_OCCUPANCY", "E": E, "T": T, "J": J}

                    if raw > worst_raw:
                        worst_raw = raw
                        worst_witness = {
                            "state": [n, m, L], "d": d, "p": p, "q": q,
                            "raw_bound": raw, "m_out_bound": M, "L_out_bound": Lb,
                            "R_or_J": R, "rescue": rescue_meta,
                        }
                    if raw > cap:
                        return {
                            "N": N, "status": "ABSTRACT_BOUND_OPEN", "cap": cap,
                            "checked_states": checked_states,
                            "checked_transitions": checked_transitions,
                            "surplus_rescues": rescues,
                            "layer_counts": layer_counts,
                            "first_open": worst_witness,
                            "claim_ceiling": "ABSTRACTION_INCONCLUSIVE_NOT_ACTUAL_COUNTEREXAMPLE",
                            "P_VS_NP": "OPEN",
                        }
                    for n2 in range(7, n):
                        add_box(boxes[n2], M, Lb, raw)

    return {
        "N": N,
        "status": "PROVED_FINITE_CAP_AVAILABILITY_BY_EXACT_INCIDENCE_SURPLUS_OVERAPPROX",
        "cap": cap,
        "root_states": sum(len(v) for v in roots.values()),
        "checked_states": checked_states,
        "checked_transitions": checked_transitions,
        "surplus_rescues": rescues,
        "layer_counts": layer_counts,
        "box_counts": {str(n): len(boxes[n]) for n in boxes},
        "worst_raw_bound": worst_raw,
        "worst_witness": worst_witness,
        "claim_ceiling": "FINITE_N58_ORDINARY_ELIMINATION_CAP_AVAILABILITY_ONLY",
        "P_VS_NP": "OPEN",
    }


def frozen_E1_check() -> None:
    J, T, E = surplus_new_resolvent_ceiling(7, 77, 351, 50, 22, 28)
    assert (J, T, E) == (607, 162, 1), (J, T, E)
    assert A.wmax(6, 635) == 2721
    assert 2721 - 162 + (616 - 608) * 6 == 2607
    assert 6 * 616 - (27 * 161) // 4 == 2610
    assert A.wmax(6, 634) == 2718
    raw = 1 + 634 + 2718
    assert raw == 3353 and raw < 58 * 58
    print('SURPLUS_E1_N58_J_CEILING=607')
    print('SURPLUS_E1_N58_RAW_CEILING=3353')
    print('SURPLUS_E1_LOCAL_REPAIR=PASS')


def selftest() -> None:
    frozen_E1_check()
    result = verify_N58_surplus()
    print(f"INCIDENCE_SURPLUS_N58_STATUS={result['status']}")
    print(f"INCIDENCE_SURPLUS_N58_CHECKED_STATES={result['checked_states']}")
    print(f"INCIDENCE_SURPLUS_N58_CHECKED_TRANSITIONS={result['checked_transitions']}")
    print(f"INCIDENCE_SURPLUS_N58_RESCUES={result['surplus_rescues']}")
    if result['status'] != 'PROVED_FINITE_CAP_AVAILABILITY_BY_EXACT_INCIDENCE_SURPLUS_OVERAPPROX':
        print(f"INCIDENCE_SURPLUS_N58_FIRST_OPEN={result['first_open']}")
        print('ABSTRACT_FAILURE_IS_INCONCLUSIVE_NOT_ACTUAL_COUNTEREXAMPLE')
        raise AssertionError(result)
    print(f"INCIDENCE_SURPLUS_N58_WORST_RAW={result['worst_raw_bound']}")
    print('INCIDENCE_SURPLUS_N58=PASS')
    print('ABSTRACT_PASS_IS_FINITE_THEOREM_NOT_UNBOUNDED_TOTALITY')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('UNBOUNDED_TOTALITY=OPEN')
    print('UNIVERSAL_GPEI=OPEN')
    print('P_VS_NP=OPEN')


if __name__ == '__main__':
    selftest()
