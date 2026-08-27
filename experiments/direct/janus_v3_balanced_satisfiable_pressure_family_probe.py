#!/usr/bin/env python3
"""Deterministic satisfiable balanced-pressure family for local v3 stress.

For n variables, include every width-3 clause that is satisfied by the all-ones
assignment.  Equivalently, for each variable triple include all 8 sign patterns
except the all-negative clause.  The witness is therefore known exactly without
a SAT oracle.  All clauses have equal width and the construction distributes
positive/negative incidence symmetrically across variable names.

For the local structural probe only, choose the smallest synthetic original-N
whose N^2 cap contains the explicit root-free residual.  This makes the cap as
hostile as possible without placing the state outside it.  Such states are NOT
claimed reachable from a root CNF with that N.

P_VS_NP remains OPEN.
"""
from __future__ import annotations

from itertools import combinations
from math import isqrt
import json

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v3 as v3

P_VS_NP = "OPEN"


def build_family(nvars: int) -> base.CNF:
    rows = []
    for vs in combinations(range(1, nvars + 1), 3):
        for mask in range(1, 8):  # mask=0 is all-negative, false under all-ones
            rows.append(tuple(v if ((mask >> i) & 1) else -v for i, v in enumerate(vs)))
    cnf = base.canon_cnf(rows)
    witness = {v: 1 for v in range(1, nvars + 1)}
    assert base.verify_total_assignment(cnf, witness)
    return cnf


def smallest_cap_N(s: int) -> int:
    q = isqrt(s)
    return q if q*q == s else q + 1


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


def analyze(nvars: int) -> dict:
    cnf = build_family(nvars)
    s = base.state_units(cnf)
    N = smallest_cap_N(s)
    cap = N**2

    # Exact earlier-lane facts needed for interpreting the local probe.
    assert base.solve_2sat_exact(cnf) is None
    gf2 = base.solve_gf2_explicit_exact(cnf)
    refuted, width_cert = base.bounded_width_resolution_refutes(cnf, 3)
    assert refuted is False, "KNOWN_SAT_WITNESS_CONTRADICTS_REFUTATION"

    pivot_rows = []
    fit = []
    for x in base.vars_of(cnf):
        out, stats = base.eliminate_var_capped(cnf, x, cap)
        row = {"pivot": x, "fit": out is not None, "stats": stats}
        pivot_rows.append(row)
        if out is not None:
            fit.append(x)

    state = make_state(cnf, N)
    plan = None
    if not fit:
        plan = v3.discover_extension_tail_plan_v3(state)

    if fit:
        classification = "ORDINARY_EXACT_PIVOT_EXISTS"
    elif plan is not None:
        classification = "ALL_ORDINARY_PIVOTS_OVERFLOW_BUT_V3_PLAN_EXISTS"
    else:
        classification = "LOCAL_V3_GRAMMAR_GAP_FOUND_NOT_PROVED_REACHABLE"

    plan_receipt = None
    if plan is not None:
        plan_receipt = {
            "pair": plan.macro_cert["represents"],
            "replaced_occurrences": plan.macro_cert["replaced_occurrences"],
            "extension": plan.macro_cert["extension"],
            "pivots": list(plan.pivots),
            "macro_state_units": base.state_units(plan.macro_cnf),
            "after1_state_units": base.state_units(plan.after_each_elim[0]),
            "after2_state_units": base.state_units(plan.after_each_elim[1]),
            "before_live": len(base.vars_of(cnf)),
            "after_live": len(base.vars_of(plan.after)),
        }

    return {
        "nvars": nvars,
        "clauses": len(cnf),
        "state_units": s,
        "synthetic_N": N,
        "state_cap": cap,
        "headroom": cap - s,
        "known_witness": "ALL_ONES",
        "fingerprint": base.fingerprint(cnf),
        "gf2_lane_returned_object": gf2 is not None,
        "bounded_width3_refuted": refuted,
        "bounded_width3_work": width_cert.get("work"),
        "ordinary_fit_pivots": fit,
        "all_ordinary_pivots_overflow": not fit,
        "pivot_scan": pivot_rows,
        "v3_plan": plan_receipt,
        "classification": classification,
    }


def main() -> int:
    rows = [analyze(n) for n in (5, 6, 7)]
    report = {
        "schema": "JANUS/C025/V3-BALANCED-SATISFIABLE-PRESSURE-FAMILY/v1",
        "family": "ALL_WIDTH3_CLAUSES_SATISFIED_BY_ALL_ONES",
        "rows": rows,
        "first_local_gap": next((r for r in rows if r['classification'].startswith('LOCAL_V3_GRAMMAR_GAP')), None),
        "scientific_boundary": {
            "deterministic_constructed_family": True,
            "SAT_status_has_explicit_all_ones_witness": True,
            "synthetic_original_N_is_for_local_structural_stress_only": True,
            "states_not_proved_reachable_under_frozen_forward_machine": True,
            "local_gap_would_require_reachability_certificate_to_refute_reachable_totality": True,
            "finite_success_does_not_prove_availability": True,
            "V3_ROOT_FREE_TAIL_AVAILABILITY": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
    }
    report['status'] = 'LOCAL_V3_GAP_FOUND' if report['first_local_gap'] is not None else 'NO_LOCAL_V3_GAP_IN_CONSTRUCTED_FAMILY'
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
