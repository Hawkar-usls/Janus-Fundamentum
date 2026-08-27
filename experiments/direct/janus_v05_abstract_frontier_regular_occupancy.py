#!/usr/bin/env python3
"""Exact theorem-side N58 refinement using regular-incidence occupancy coupling.

The v0.5 runtime is unchanged.  We inherit the global-raw + resource-simplex
abstraction and invoke the new regular-incidence bound only when the existing
abstract transfer would exceed the fixed N^2 cap and L == n*d proves that every
live variable has the selected minimum degree d.

A PASS is a finite N=58 cap-availability theorem for this overapproximation.
A FAIL remains abstraction-inconclusive, not an actual CNF counterexample.
P vs NP remains OPEN.
"""

from functools import lru_cache

from experiments.direct import janus_v05_abstract_frontier_support_mass as A
from experiments.direct import janus_v05_abstract_frontier_global_raw_universe as G

P_VS_NP = "OPEN"
THEOREM_RUNTIME_HEURISTICS = "FORBIDDEN"


@lru_cache(maxsize=None)
def regular_new_resolvent_ceiling(n: int, m: int, L: int, d: int, p: int, q: int) -> tuple[int, int]:
    """Return (Jmax, worst_T) under the regular-incidence theorem.

    J counts only new distinct non-tautological resolvents not already present
    in the retained raw set.  This routine is valid only when L=n*d.
    """
    assert p + q == d
    assert L == n * d
    if p == 0 or q == 0:
        return 0, 0

    r = n - 1
    c = m - d
    pq = p * q
    if c == 0:
        Tlo = Thi = 0
    else:
        # Unit-free retained clauses have width >=2.  The d pivot-parent
        # clauses are also unit-free, so their total tail mass is >=d.
        Tlo = 2 * c
        Thi = min(c * r, L - 2 * d)
        if Thi < Tlo:
            return 0, Thi

    best_J = 0
    worst_T = Tlo
    max_new_universe = max(0, 3 ** r - c)

    for T in range(Tlo, Thi + 1):
        # For each nonpivot y: t_y<=c and a_y+b_y=t_y.
        # Hence a_y*b_y <= t_y^2/4 <= c*t_y/4.
        # The omitted-pair count is integral, so summing gives <=floor(c*T/4).
        omitted_pair_support = (c * T) // 4
        support_lower = r * pq - omitted_pair_support

        lo, hi = 0, min(pq, max_new_universe)
        # F(J)=Wmax(r,c+J)-T+(pq-J)r is nonincreasing because each added
        # distinct signed clause increases Wmax by at most r while -J*r drops r.
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

    return best_J, worst_T


def regular_rescue(n: int, m: int, L: int, d: int, p: int, q: int) -> tuple[int, int, int, int, int]:
    """Return (raw, M, Lcap, J, T) for a regular-incidence transition."""
    assert L == n * d
    r = n - 1
    c = m - d

    if p == 0 or q == 0:
        K = min(c, 3 ** r)
        raw = 1 + K + A.wmax(r, K)
        return raw, K, A.wmax(r, K), 0, 0

    J, T = regular_new_resolvent_ceiling(n, m, L, d, p, q)
    K = min(c + J, 3 ** r)
    Lcap = A.wmax(r, K)
    raw = 1 + K + Lcap
    return raw, K, Lcap, J, T


def add_box(boxes: list[tuple[int, int, int]], M: int, L: int, S: int) -> None:
    if M < 7 or L < 14 or S < 22:
        return
    if any(a >= M and b >= L and c >= S for a, b, c in boxes):
        return
    boxes[:] = [(a, b, c) for a, b, c in boxes if not (M >= a and L >= b and S >= c)]
    boxes.append((M, L, S))


def verify_N58_regular() -> dict:
    N = 58
    previous_frontier = 57
    cap = N * N
    roots = A.hard_roots(N)
    max_n = max(roots, default=A.TAIL_N)
    boxes: dict[int, list[tuple[int, int, int]]] = {n: [] for n in range(7, max_n + 1)}
    rootsets = {n: set(rows) for n, rows in roots.items()}

    checked_states = 0
    checked_transitions = 0
    regular_rescues = 0
    worst_raw = -1
    worst_witness = None
    layer_counts: dict[int, int] = {}

    for n in range(max_n, 6, -1):
        candidates = set(rootsets.get(n, set()))
        bs = boxes[n]
        max_M = max((M for M, _, _ in bs), default=0)
        for m in range(7, max_M + 1):
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

                    if raw > cap and L == n * d:
                        rraw, rM, rL, J, T = regular_rescue(n, m, L, d, p, q)
                        if rraw < raw:
                            raw, M, Lb, R = rraw, rM, min(Lb, rL), J
                            regular_rescues += 1
                            rescue_meta = {"kind": "REGULAR_INCIDENCE_RETAINED_OCCUPANCY", "T": T, "J": J}

                    if raw > worst_raw:
                        worst_raw = raw
                        worst_witness = {
                            "state": [n, m, L],
                            "d": d,
                            "p": p,
                            "q": q,
                            "raw_bound": raw,
                            "m_out_bound": M,
                            "L_out_bound": Lb,
                            "R_or_J": R,
                            "rescue": rescue_meta,
                        }

                    if raw > cap:
                        return {
                            "N": N,
                            "status": "ABSTRACT_BOUND_OPEN",
                            "cap": cap,
                            "checked_states": checked_states,
                            "checked_transitions": checked_transitions,
                            "regular_rescues": regular_rescues,
                            "layer_counts": layer_counts,
                            "first_open": worst_witness,
                            "claim_ceiling": "ABSTRACTION_INCONCLUSIVE_NOT_ACTUAL_COUNTEREXAMPLE",
                            "P_VS_NP": "OPEN",
                        }

                    for n2 in range(7, n):
                        add_box(boxes[n2], M, Lb, raw)

    return {
        "N": N,
        "status": "PROVED_FINITE_CAP_AVAILABILITY_BY_EXACT_REGULAR_OCCUPANCY_OVERAPPROX",
        "cap": cap,
        "root_states": sum(len(v) for v in roots.values()),
        "checked_states": checked_states,
        "checked_transitions": checked_transitions,
        "regular_rescues": regular_rescues,
        "layer_counts": layer_counts,
        "box_counts": {str(n): len(boxes[n]) for n in boxes},
        "worst_raw_bound": worst_raw,
        "worst_witness": worst_witness,
        "claim_ceiling": "FINITE_N58_ORDINARY_ELIMINATION_CAP_AVAILABILITY_ONLY",
        "P_VS_NP": "OPEN",
    }


def verify_frozen_second_open_arithmetic() -> None:
    J, T = regular_new_resolvent_ceiling(7, 77, 350, 50, 22, 28)
    assert J == 609, (J, T)
    assert T == 162, T
    # J=610 is impossible at the worst T: 2727-162+6*6 = 2601 < 2603.
    assert A.wmax(6, 637) == 2727
    assert 2727 - 162 + (616 - 610) * 6 == 2601
    assert 6 * 616 - (27 * 162) // 4 == 2603
    assert A.wmax(6, 636) == 2724
    raw = 1 + 636 + 2724
    assert raw == 3361
    assert raw < 58 * 58
    print('REGULAR_N58_SECOND_OPEN_J_CEILING=609')
    print('REGULAR_N58_SECOND_OPEN_RAW_CEILING=3361')
    print('REGULAR_N58_SECOND_OPEN_LOCAL_REPAIR=PASS')


def selftest() -> None:
    verify_frozen_second_open_arithmetic()
    result = verify_N58_regular()
    print(f"REGULAR_OCCUPANCY_N58_STATUS={result['status']}")
    print(f"REGULAR_OCCUPANCY_N58_CHECKED_STATES={result['checked_states']}")
    print(f"REGULAR_OCCUPANCY_N58_CHECKED_TRANSITIONS={result['checked_transitions']}")
    print(f"REGULAR_OCCUPANCY_N58_RESCUES={result['regular_rescues']}")
    if result['status'] != 'PROVED_FINITE_CAP_AVAILABILITY_BY_EXACT_REGULAR_OCCUPANCY_OVERAPPROX':
        print(f"REGULAR_OCCUPANCY_N58_FIRST_OPEN={result['first_open']}")
        print('ABSTRACT_FAILURE_IS_INCONCLUSIVE_NOT_ACTUAL_COUNTEREXAMPLE')
        raise AssertionError(result)
    print(f"REGULAR_OCCUPANCY_N58_WORST_RAW={result['worst_raw_bound']}")
    print('REGULAR_OCCUPANCY_N58=PASS')
    print('ABSTRACT_PASS_IS_FINITE_THEOREM_NOT_UNBOUNDED_TOTALITY')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('UNBOUNDED_TOTALITY=OPEN')
    print('UNIVERSAL_GPEI=OPEN')
    print('P_VS_NP=OPEN')


if __name__ == '__main__':
    selftest()
