#!/usr/bin/env python3
"""Deterministic finite probe for local v3 root-free grammar gaps.

This is deliberately NOT a reachability proof and NOT theorem authority.  It
enumerates canonical connected width-3 CNFs under a synthetic frozen original-N
budget, filters out states where earlier exact local lanes or any ordinary
N^2-capped pivot already suffice, then asks the existing frozen v3 discoverer
for a two-elimination tail plan.

A found local gap refutes only the stronger claim "v3 covers every arbitrary
root-free state under the cap".  It does not refute reachable-state totality
until a frozen forward trajectory to that state is proved.  No gap in a finite
probe proves nothing universal.

P_VS_NP remains OPEN.
"""
from __future__ import annotations

from itertools import combinations
import json
from typing import Iterable

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v3 as v3

P_VS_NP = "OPEN"


def width3_universe(nvars: int) -> tuple[base.Clause, ...]:
    out = []
    vars_ = range(1, nvars + 1)
    for vs in combinations(vars_, 3):
        for mask in range(8):
            clause = tuple(v if ((mask >> i) & 1) else -v for i, v in enumerate(vs))
            cc = base.canon_clause(clause)
            assert cc is not None and len(cc) == 3
            out.append(cc)
    return tuple(sorted(set(out), key=lambda c: (len(c), c)))


def connected_and_full(cnf: base.CNF, nvars: int) -> bool:
    if set(base.vars_of(cnf)) != set(range(1, nvars + 1)):
        return False
    adj = {v: set() for v in range(1, nvars + 1)}
    for c in cnf:
        vs = sorted({abs(x) for x in c})
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                adj[vs[i]].add(vs[j])
                adj[vs[j]].add(vs[i])
    seen = {1}
    stack = [1]
    while stack:
        u = stack.pop()
        for w in adj[u]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return len(seen) == nvars


def make_state(cnf: base.CNF, N: int) -> base.EngineState:
    return base.EngineState(
        root=cnf,
        residual=cnf,
        fixed_assignment={},
        root_vars=(),
        extension_defs=[],
        elimination_history=[],
        seen=set(),
        N=N,
        cap_exponent=2,
        extension_exponent=1,
        ledger=base.Ledger(),
    )


def earlier_exact_local_lane(cnf: base.CNF, width: int = 3) -> str | None:
    if () in cnf or not cnf or any(len(c) <= 1 for c in cnf):
        return "TRIVIAL_OR_UNIT"
    if base.solve_2sat_exact(cnf) is not None:
        return "2SAT"
    if base.solve_gf2_explicit_exact(cnf) is not None:
        return "GF2"
    refuted, _ = base.bounded_width_resolution_refutes(cnf, width)
    if refuted:
        return "BOUNDED_WIDTH_REFUTATION"
    return None


def all_pivots_overflow(cnf: base.CNF, cap: int) -> tuple[bool, list[dict]]:
    rows = []
    all_over = True
    for x in base.vars_of(cnf):
        out, stats = base.eliminate_var_capped(cnf, x, cap)
        fit = out is not None
        rows.append({"pivot": x, "fit": fit, "stats": stats})
        if fit:
            all_over = False
    return all_over, rows


def run_rung(nvars: int, clauses: int, N: int, limit: int) -> dict:
    universe = width3_universe(nvars)
    totals = {
        "raw_combinations": 0,
        "connected_examined": 0,
        "outside_cap": 0,
        "earlier_exact_lane": 0,
        "ordinary_pivot_exists": 0,
        "all_pivot_overflow": 0,
        "v3_plan_exists": 0,
        "v3_local_gap": 0,
    }
    first_gap = None
    first_all_overflow = None

    for combo in combinations(universe, clauses):
        totals["raw_combinations"] += 1
        cnf = base.canon_cnf(combo)
        if len(cnf) != clauses or not connected_and_full(cnf, nvars):
            continue
        totals["connected_examined"] += 1
        if totals["connected_examined"] > limit:
            break

        s = base.state_units(cnf)
        if s > N**2:
            totals["outside_cap"] += 1
            continue

        lane = earlier_exact_local_lane(cnf)
        if lane is not None:
            totals["earlier_exact_lane"] += 1
            continue

        overflow, pivot_rows = all_pivots_overflow(cnf, N**2)
        if not overflow:
            totals["ordinary_pivot_exists"] += 1
            continue

        totals["all_pivot_overflow"] += 1
        if first_all_overflow is None:
            first_all_overflow = {
                "cnf": cnf,
                "fingerprint": base.fingerprint(cnf),
                "state_units": s,
                "pivot_scan": pivot_rows,
            }

        state = make_state(cnf, N)
        plan = v3.discover_extension_tail_plan_v3(state)
        if plan is not None:
            totals["v3_plan_exists"] += 1
            continue

        totals["v3_local_gap"] += 1
        first_gap = {
            "cnf": cnf,
            "fingerprint": base.fingerprint(cnf),
            "state_units": s,
            "N": N,
            "state_cap": N**2,
            "pivot_scan": pivot_rows,
            "v3_extension_cap": state.extension_cap,
            "claim_ceiling": "LOCAL_ARBITRARY_ROOT_FREE_GRAMMAR_GAP_NOT_PROVED_REACHABLE",
        }
        break

    return {
        "parameters": {"nvars": nvars, "clauses": clauses, "N": N, "limit": limit},
        "universe_size": len(universe),
        "totals": totals,
        "first_all_pivot_overflow": first_all_overflow,
        "first_local_gap": first_gap,
        "status": "LOCAL_V3_GAP_FOUND" if first_gap is not None else "NO_LOCAL_V3_GAP_IN_BOUNDED_RUNG",
    }


def main() -> int:
    # Canonical bounded ladder.  The first rungs are intentionally small and
    # structural; a later result cannot modify these parameters retroactively.
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
        if row["first_local_gap"] is not None:
            break

    report = {
        "schema": "JANUS/C025/V3-ROOT-FREE-LOCAL-GAP-PROBE/v1",
        "rungs": results,
        "first_local_gap": next((r["first_local_gap"] for r in results if r["first_local_gap"] is not None), None),
        "scientific_boundary": {
            "deterministic_finite_probe_only": True,
            "arbitrary_root_free_states_not_proved_reachable": True,
            "local_gap_is_not_reachable_gap_without_forward_certificate": True,
            "no_gap_is_not_availability_proof": True,
            "does_not_prove_or_refute_P_equals_NP": True,
            "V3_ROOT_FREE_TAIL_AVAILABILITY": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
    }
    report["status"] = "LOCAL_V3_GAP_FOUND" if report["first_local_gap"] is not None else "NO_LOCAL_V3_GAP_IN_BOUNDED_LADDER"
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
