#!/usr/bin/env python3
"""Focused reachable-prefix probe for the C025 root-phase grammar gap.

This reuses the frozen v0.4 core.  It stops only *after* the core itself has
reached an ordinary-all-pivots-overflow root-phase call site and the unmodified
v2 discovery result for that same state has been observed.  Stopping the
irrelevant suffix cannot manufacture reachability of the already-observed
prefix.  Finite absence of a witness is not proof.
"""
from __future__ import annotations

import argparse
import json
from copy import deepcopy

from experiments.direct import janus_pirc_decision_core_v0_4 as core
from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.theorem_extraction import c025_root_pivot_grammar_falsifier as common

P_VS_NP = "OPEN"


class GapObserved(RuntimeError):
    pass


def observe_one(cnf: base.CNF, meta: dict) -> dict:
    original_first = base.first_capped_elimination
    original_v2 = core.v2.discover_macro_restore_v2
    pending = None
    observed = None

    def wrapped_first(state: base.EngineState, cnf_arg=None, roots_only: bool = False):
        nonlocal pending
        result = original_first(state, cnf_arg, roots_only)
        if cnf_arg is None and not roots_only and result is None:
            live = set(base.vars_of(state.residual))
            roots_live = [v for v in state.root_vars if v in live]
            if roots_live:
                s = base.state_units(state.residual)
                n = len(live)
                P, tmax, pair = common.pair_stats(state.residual)
                threshold = s - 2 * state.N + 11
                density_threshold = 2 * n * (n - 1) * threshold if n >= 2 else 0
                pending = {
                    "source_case": deepcopy(meta),
                    "normalized_root_fingerprint": base.fingerprint(state.root),
                    "reachable_state_fingerprint": base.fingerprint(state.residual),
                    "N": int(state.N),
                    "state_cap": int(state.state_cap),
                    "state_units": int(s),
                    "live_variables": n,
                    "root_variables_live": len(roots_live),
                    "pair_incidences_P": int(P),
                    "max_pair_frequency": int(tmax),
                    "max_pair": list(pair) if pair is not None else None,
                    "frequent_pair_threshold": int(threshold),
                    "pair_density_threshold": int(density_threshold),
                    "L1A_frequent_pair_forced": bool(tmax >= threshold),
                    "L1B_pair_density_forced": bool(P >= density_threshold),
                    "event_prefix": deepcopy(state.ledger.events),
                    "reachable_state_cnf": [list(c) for c in state.residual],
                }
        return result

    def wrapped_v2(state: base.EngineState):
        nonlocal pending, observed
        result = original_v2(state)
        if pending is not None and pending["reachable_state_fingerprint"] == base.fingerprint(state.residual):
            observed = deepcopy(pending)
            observed["v2_rescue_exists"] = result is not None
            if result is not None:
                macro_cnf, pivot, after, cert, elim_stats = result
                observed["v2_rescue"] = {
                    "pair": list(cert.get("represents", [])),
                    "reused_occurrences": cert.get("reused_occurrences"),
                    "root_pivot": int(pivot),
                    "macro_state_units": base.state_units(macro_cnf),
                    "after_state_units": base.state_units(after),
                    "elimination_raw_units": int(elim_stats.get("raw_units", 0)),
                }
            raise GapObserved
        return result

    base.first_capped_elimination = wrapped_first
    core.v2.discover_macro_restore_v2 = wrapped_v2
    terminal = None
    try:
        terminal = core.solve_decision_core(cnf)
    except GapObserved:
        pass
    finally:
        base.first_capped_elimination = original_first
        core.v2.discover_macro_restore_v2 = original_v2

    return {
        "source_case": deepcopy(meta),
        "source_fingerprint": base.fingerprint(cnf),
        "gap_observed": observed is not None,
        "gap": observed,
        "terminal_if_no_gap": None if terminal is None else {
            "status": terminal["status"],
            "reason": terminal["reason"],
            "N": int(terminal["N"]),
            "max_state_units": int(terminal["ledger"]["max_state_units"]),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-leaf-clauses", type=int, default=60)
    args = parser.parse_args()
    rows = []
    for leaf_clauses, seed in ((40, 29100), (50, 29200), (60, 29300)):
        if leaf_clauses > args.max_leaf_clauses:
            continue
        meta = {
            "family": "SELECTOR_PRODUCT",
            "leaf_nvars": 8,
            "leaf_clauses": leaf_clauses,
            "leaf_width": 4,
            "seed": seed,
        }
        cnf = common.selector_product_case(8, leaf_clauses, 4, seed)
        row = observe_one(cnf, meta)
        rows.append(row)
        gap = row.get("gap")
        if gap is not None and gap.get("v2_rescue_exists") is False:
            break

    gaps = [r["gap"] for r in rows if r.get("gap") is not None]
    l1 = next((g for g in gaps if g.get("v2_rescue_exists") is False), None)
    l1a = next((g for g in gaps if not g.get("L1A_frequent_pair_forced", True)), None)
    l1b = next((g for g in gaps if not g.get("L1B_pair_density_forced", True)), None)
    report = {
        "schema": "JANUS/C025/SELECTOR-PRODUCT-REACHABLE-GAP-PROBE/v1",
        "status": "L1_REACHABLE_COUNTEREXAMPLE_FOUND" if l1 else "NO_L1_COUNTEREXAMPLE_IN_BOUNDED_SELECTOR_PROBE",
        "rows": rows,
        "candidate_results": {
            "L1": "REFUTED" if l1 else "NOT_REFUTED__NOT_PROVED",
            "L1A": "REFUTED" if l1a else "NOT_REFUTED__NOT_PROVED",
            "L1B": "REFUTED" if l1b else "NOT_REFUTED__NOT_PROVED",
        },
        "counterexamples": {"L1": l1, "L1A": l1a, "L1B": l1b},
        "scientific_boundary": {
            "uses_frozen_v0_4_prefix": True,
            "gap_recorded_only_after_frozen_ordinary_failure": True,
            "v2_result_from_unmodified_frozen_discovery": True,
            "suffix_stop_after_gap_does_not_promote_unreachable_state": True,
            "finite_absence_is_not_proof": True,
            "P_VS_NP": P_VS_NP,
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
