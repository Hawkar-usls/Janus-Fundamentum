#!/usr/bin/env python3
"""C025 root-free v3 microscope after the sequential raw-budget theorem.

Classifies bounded arbitrary root-free states that survive earlier exact local
lanes and have no ordinary N^2-capped pivot into:

  SEQUENTIAL_CERTIFIED
      a B2 macro + two old pivots satisfy the generic sequential raw bounds;

  BOUND_FALSE_NEGATIVE_V3_PLAN
      no sequential generic certificate is found, but frozen v3 still finds an
      exact plan (e.g. because tautology/duplicate cancellation beats the upper
      bound);

  TRUE_LOCAL_V3_GAP
      frozen v3 itself finds no plan.

A TRUE_LOCAL_V3_GAP is only a grammar gap on an arbitrary synthetic root-free
state. It is NOT a reachable-state counterexample without a frozen forward
reachability certificate. Absence of a gap in this finite probe proves nothing
universal. P_VS_NP remains OPEN.
"""
from __future__ import annotations

from itertools import combinations
import json

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.direct import janus_unified_macro_restore_v3 as v3
from experiments.direct import janus_generic_raw_elimination_budget_certificate as rawcert
from experiments.direct import janus_v3_root_free_local_gap_probe as oldprobe

P_VS_NP = "OPEN"


def sequential_certificate_scan(cnf: base.CNF, N: int):
    cap = N * N
    V0 = tuple(base.vars_of(cnf))
    fresh = max(V0, default=0) + 1
    scanned_macros = 0
    cap_admissible_macros = 0
    first_budget_passes = 0
    second_liveness_passes = 0
    second_budget_passes = 0

    for a, b in v2.all_or_pair_candidates(cnf):
        scanned_macros += 1
        try:
            macro, macro_cert = v2.apply_or_pair_v2(cnf, a, b, fresh)
        except ValueError:
            continue
        if not v2.verify_or_pair_v2(cnf, macro, macro_cert):
            raise AssertionError("B2_MACRO_REPLAY_FAILED")
        if base.state_units(macro) > cap:
            continue
        cap_admissible_macros += 1

        for x in V0:
            B1 = rawcert.raw_budget(macro, x)
            if B1.bound > cap:
                continue
            first_budget_passes += 1
            after1, stats1 = base.eliminate_var_capped(macro, x, cap)
            if after1 is None:
                raise AssertionError("GENERIC_FIRST_BOUND_CERTIFIED_BUT_ABORTED")
            if int(stats1["raw_units"]) > B1.bound:
                raise AssertionError("FIRST_ACTUAL_RAW_EXCEEDS_BOUND")

            live1 = set(base.vars_of(after1))
            for y in V0:
                if y == x or y not in live1:
                    continue
                second_liveness_passes += 1
                B2 = rawcert.raw_budget(after1, y)
                if B2.bound > cap:
                    continue
                second_budget_passes += 1
                after2, stats2 = base.eliminate_var_capped(after1, y, cap)
                if after2 is None:
                    raise AssertionError("GENERIC_SECOND_BOUND_CERTIFIED_BUT_ABORTED")
                if int(stats2["raw_units"]) > B2.bound:
                    raise AssertionError("SECOND_ACTUAL_RAW_EXCEEDS_BOUND")

                V2 = set(base.vars_of(after2))
                if len(V2) > len(V0) - 1:
                    raise AssertionError("SEQUENTIAL_CERTIFICATE_WITHOUT_ROOT_FREE_PROGRESS")
                return {
                    "exists": True,
                    "pair": [a, b],
                    "pivots": [x, y],
                    "macro_units": base.state_units(macro),
                    "first_bound": B1.bound,
                    "first_actual_raw": int(stats1["raw_units"]),
                    "second_bound": B2.bound,
                    "second_actual_raw": int(stats2["raw_units"]),
                    "after_units": base.state_units(after2),
                    "before_live": len(V0),
                    "after_live": len(V2),
                    "counters": {
                        "scanned_macros": scanned_macros,
                        "cap_admissible_macros": cap_admissible_macros,
                        "first_budget_passes": first_budget_passes,
                        "second_liveness_passes": second_liveness_passes,
                        "second_budget_passes": second_budget_passes,
                    },
                }

    return {
        "exists": False,
        "counters": {
            "scanned_macros": scanned_macros,
            "cap_admissible_macros": cap_admissible_macros,
            "first_budget_passes": first_budget_passes,
            "second_liveness_passes": second_liveness_passes,
            "second_budget_passes": second_budget_passes,
        },
    }


def run_rung(nvars: int, clauses: int, N: int, limit: int) -> dict:
    universe = oldprobe.width3_universe(nvars)
    totals = {
        "raw_combinations": 0,
        "connected_examined": 0,
        "outside_cap": 0,
        "earlier_exact_lane": 0,
        "ordinary_pivot_exists": 0,
        "all_pivot_overflow": 0,
        "sequential_certified": 0,
        "bound_false_negative_v3_plan": 0,
        "true_local_v3_gap": 0,
    }
    first_all_overflow = None
    first_seq = None
    first_false_negative = None
    first_gap = None

    for combo in combinations(universe, clauses):
        totals["raw_combinations"] += 1
        cnf = base.canon_cnf(combo)
        if len(cnf) != clauses or not oldprobe.connected_and_full(cnf, nvars):
            continue
        totals["connected_examined"] += 1
        if totals["connected_examined"] > limit:
            break

        s = base.state_units(cnf)
        cap = N * N
        if s > cap:
            totals["outside_cap"] += 1
            continue
        lane = oldprobe.earlier_exact_local_lane(cnf)
        if lane is not None:
            totals["earlier_exact_lane"] += 1
            continue

        overflow, pivot_rows = oldprobe.all_pivots_overflow(cnf, cap)
        if not overflow:
            totals["ordinary_pivot_exists"] += 1
            continue
        totals["all_pivot_overflow"] += 1

        base_row = {
            "cnf": cnf,
            "fingerprint": base.fingerprint(cnf),
            "state_units": s,
            "N": N,
            "state_cap": cap,
            "pivot_scan": pivot_rows,
        }
        if first_all_overflow is None:
            first_all_overflow = base_row

        seq = sequential_certificate_scan(cnf, N)
        state = oldprobe.make_state(cnf, N)
        plan = v3.discover_extension_tail_plan_v3(state)

        if seq["exists"]:
            totals["sequential_certified"] += 1
            if plan is None:
                raise AssertionError("SEQUENTIAL_SUFFICIENT_CERTIFICATE_BUT_FROZEN_V3_FOUND_NO_PLAN")
            if first_seq is None:
                first_seq = {**base_row, "sequential_certificate": seq}
            continue

        if plan is not None:
            totals["bound_false_negative_v3_plan"] += 1
            if first_false_negative is None:
                first_false_negative = {
                    **base_row,
                    "sequential_scan": seq,
                    "v3_plan": {
                        "pair": plan.macro_cert.get("represents"),
                        "pivots": list(plan.pivots),
                        "macro_units": base.state_units(plan.macro_cnf),
                        "after_units": base.state_units(plan.after),
                    },
                    "claim_ceiling": "GENERIC_SEQUENTIAL_BOUND_IS_SUFFICIENT_NOT_NECESSARY",
                }
            continue

        totals["true_local_v3_gap"] += 1
        first_gap = {
            **base_row,
            "sequential_scan": seq,
            "claim_ceiling": "ARBITRARY_ROOT_FREE_LOCAL_GRAMMAR_GAP_NOT_PROVED_REACHABLE",
        }
        break

    return {
        "parameters": {"nvars": nvars, "clauses": clauses, "N": N, "limit": limit},
        "universe_size": len(universe),
        "totals": totals,
        "first_all_pivot_overflow": first_all_overflow,
        "first_sequential_certified": first_seq,
        "first_bound_false_negative": first_false_negative,
        "first_true_local_v3_gap": first_gap,
        "status": "TRUE_LOCAL_V3_GAP_FOUND" if first_gap is not None else "NO_TRUE_LOCAL_V3_GAP_IN_BOUNDED_RUNG",
    }


def main() -> int:
    # Freeze the old probe ladder verbatim so the comparison is auditable.
    rungs = (
        (4, 8, 8, 12000),
        (4, 10, 9, 12000),
        (5, 10, 9, 12000),
        (5, 12, 10, 12000),
    )
    results = []
    for args in rungs:
        row = run_rung(*args)
        results.append(row)
        if row["first_true_local_v3_gap"] is not None:
            break

    first_gap = next((r["first_true_local_v3_gap"] for r in results if r["first_true_local_v3_gap"] is not None), None)
    first_false_negative = next((r["first_bound_false_negative"] for r in results if r["first_bound_false_negative"] is not None), None)
    report = {
        "schema": "JANUS/C025/V3-SEQUENTIAL-BUDGET-LOCAL-GAP-MICROSCOPE/v1",
        "rungs": results,
        "first_true_local_v3_gap": first_gap,
        "first_bound_false_negative": first_false_negative,
        "scientific_boundary": {
            "deterministic_finite_probe_only": True,
            "generic_budget_is_sufficient_not_necessary": True,
            "arbitrary_root_free_states_not_proved_reachable": True,
            "true_local_gap_is_not_reachable_gap_without_forward_certificate": True,
            "no_gap_is_not_availability_proof": True,
            "heuristic_or_predictive_layer_has_theorem_authority": False,
            "V3_ROOT_FREE_TAIL_AVAILABILITY": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
    }
    report["status"] = "TRUE_LOCAL_V3_GAP_FOUND" if first_gap is not None else "NO_TRUE_LOCAL_V3_GAP_IN_BOUNDED_LADDER"
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
