#!/usr/bin/env python3
"""Append-only exact abstract verifier with regular-state repair.

Base: frozen N<=57 exact abstract frontier.
Normal transfer: global raw signed-clause universe refinement.
Repair: ONLY when that transfer exceeds cap and L == n*d for the candidate
minimum degree (hence every live variable is exactly d-regular), invoke the
proved exact regular global-support feasibility ceiling.

This changes theorem-side accounting only. Runtime semantics remain frozen.
A PASS is a finite cap-availability theorem for the checked N. A failure is an
abstract OPEN, not automatically an actual CNF/runtime counterexample.
"""

from experiments.direct import janus_v05_abstract_frontier_support_mass as A
from experiments.direct import janus_v05_abstract_frontier_global_raw_universe as G
from experiments.direct.janus_regular_min_degree_global_support_feasibility import regular_raw_ceiling

P_VS_NP = "OPEN"
THEOREM_RUNTIME_HEURISTICS = "FORBIDDEN"


def verify_N_regular(N: int, previous_frontier: int) -> dict:
    assert previous_frontier == N - 1
    assert previous_frontier >= 57
    cap = N * N
    roots = A.hard_roots(N)
    max_n = max(roots, default=A.TAIL_N)
    rectangles: dict[int, list[tuple[int, int]]] = {n: [] for n in range(7, max_n + 1)}
    rootsets = {n: set(rows) for n, rows in roots.items()}

    checked_states = 0
    checked_transitions = 0
    repaired_regular_transitions = 0
    worst_raw = -1
    worst = None
    layers: dict[int, int] = {}

    for n in range(max_n, 6, -1):
        candidates = set(rootsets.get(n, set()))
        rects = rectangles[n]
        max_M = max((M for M, _ in rects), default=0)

        for m in range(7, max_M + 1):
            Lcap = max((Lb for M, Lb in rects if M >= m), default=-1)
            if Lcap < 0:
                continue
            # Strong-induction gate: states no larger than the already-proved
            # previous frontier are discharged there.
            Llo = max(2 * m, n, previous_frontier - n - m)
            Lhi = min(Lcap, n * m, cap - 1 - m)
            if Llo > Lhi:
                continue
            for L in range(Llo, Lhi + 1):
                dlo, dhi = A.degree_interval(n, m, L)
                if dlo <= dhi:
                    candidates.add((m, L))

        layers[n] = len(candidates)
        for m, L in sorted(candidates):
            checked_states += 1
            dlo, dhi = A.degree_interval(n, m, L)
            for d in range(dlo, dhi + 1):
                for p in range(0, d // 2 + 1):
                    q = d - p
                    checked_transitions += 1
                    raw, m_out, L_out, R = G.transfer_bounds_global(n, m, L, d, p, q)
                    repair = None

                    # Exact regular-state theorem is invoked only as a repair
                    # for a transition not already certified by the ordinary
                    # global-support transfer.
                    if raw > cap and p > 0 and q > 0 and L == n * d:
                        reg_raw, reg_witness = regular_raw_ceiling(n, m, d, p, q)
                        if reg_raw < raw:
                            repair = {
                                "old_raw_bound": raw,
                                "regular_raw_bound": reg_raw,
                                "regular_witness": reg_witness,
                            }
                            raw = reg_raw
                            repaired_regular_transitions += 1

                    if raw > worst_raw:
                        worst_raw = raw
                        worst = {
                            "state": [n, m, L],
                            "d": d,
                            "p": p,
                            "q": q,
                            "raw_bound": raw,
                            "m_out_bound": m_out,
                            "L_out_bound": L_out,
                            "distinct_resolvent_bound": R,
                            "regular_repair": repair,
                        }

                    if raw > cap:
                        return {
                            "N": N,
                            "status": "ABSTRACT_BOUND_OPEN",
                            "cap": cap,
                            "checked_states": checked_states,
                            "checked_transitions": checked_transitions,
                            "regular_repairs_applied": repaired_regular_transitions,
                            "layer_counts": layers,
                            "first_open": {
                                "state": [n, m, L],
                                "d": d,
                                "p": p,
                                "q": q,
                                "raw_bound": raw,
                                "m_out_bound": m_out,
                                "L_out_bound": L_out,
                                "distinct_resolvent_bound": R,
                                "regular_repair_attempt": repair,
                            },
                            "claim_ceiling": "ABSTRACTION_INCONCLUSIVE_NOT_ACTUAL_COUNTEREXAMPLE",
                            "P_VS_NP": "OPEN",
                        }

                    # We intentionally keep the older safe m/L output caps even
                    # when only raw is repaired.  That is conservative.  The
                    # known N58 repaired state has n=7 so every successor is
                    # already n<=6 terminal-safe, but this remains sound in
                    # general because we do not tighten downstream caps here.
                    for n2 in range(7, n):
                        A.add_pareto_rectangle(rectangles[n2], m_out, L_out)

    return {
        "N": N,
        "status": "PROVED_FINITE_CAP_AVAILABILITY_BY_EXACT_REGULAR_REPAIR_OVERAPPROX",
        "cap": cap,
        "root_states": sum(len(v) for v in roots.values()),
        "checked_states": checked_states,
        "checked_transitions": checked_transitions,
        "regular_repairs_applied": repaired_regular_transitions,
        "layer_counts": layers,
        "pareto_rectangle_counts": {str(n): len(rectangles[n]) for n in rectangles},
        "worst_raw_bound": worst_raw,
        "worst_witness": worst,
        "claim_ceiling": "FINITE_N_ORDINARY_ELIMINATION_CAP_AVAILABILITY_ONLY",
        "P_VS_NP": "OPEN",
    }


def clear_caches() -> None:
    G.transfer_bounds_global.cache_clear()
    A.wmax.cache_clear()
    A.omission_product_max.cache_clear()
    A.support_resolvent_ceiling.cache_clear()


def selftest() -> None:
    # Freeze the exact local repair number first.
    reg, witness = regular_raw_ceiling(7, 77, 50, 22, 28)
    assert reg == 3361, (reg, witness)
    assert reg < 58 * 58
    print('REGULAR_SUPPORT_N58_SECOND_OPEN_LOCAL_REPAIR=PASS:3361')

    result = verify_N_regular(58, 57)
    print(f"REGULAR_REPAIR_N58_STATUS={result['status']}")
    print(f"REGULAR_REPAIR_N58_CHECKED_STATES={result['checked_states']}")
    print(f"REGULAR_REPAIR_N58_CHECKED_TRANSITIONS={result['checked_transitions']}")
    print(f"REGULAR_REPAIR_N58_APPLIED={result['regular_repairs_applied']}")
    if result['status'] != 'PROVED_FINITE_CAP_AVAILABILITY_BY_EXACT_REGULAR_REPAIR_OVERAPPROX':
        print(f"REGULAR_REPAIR_N58_FIRST_OPEN={result['first_open']}")
        print('ABSTRACT_FAILURE_IS_INCONCLUSIVE_NOT_ACTUAL_COUNTEREXAMPLE')
        raise AssertionError(result)
    print(f"REGULAR_REPAIR_N58_WORST_RAW={result['worst_raw_bound']}")
    assert result['worst_raw_bound'] <= 58 * 58
    print('V05_REGULAR_SUPPORT_ABSTRACT_FRONTIER_N58=PASS')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('UNBOUNDED_TOTALITY=OPEN')
    print('UNIVERSAL_GPEI=OPEN')
    print('P_VS_NP=OPEN')


if __name__ == '__main__':
    selftest()
