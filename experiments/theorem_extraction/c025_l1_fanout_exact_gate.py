#!/usr/bin/env python3
"""Fanout exact Delta/Gamma gate for the frozen C025 L1 candidate.

Frozen candidate (pre-existing v2-gap workflow):
  DISJOINT_SELECTOR_PRODUCT(leaf_nvars=10, leaf_clauses=90, width=4, seed=39100)

Modes:
  reachability  - exact frozen core callsite reachability receipt.
  ordinary      - exact ORIGINAL eliminate_var_capped on a disjoint pivot shard.
  v2            - exact ORIGINAL v2 apply/verify + ORIGINAL capped root elimination
                  on a disjoint canonical pair shard.

The v2 direct state is the semantic state consumed by discover_macro_restore_v2
at the first target call: root=source, residual=selector product, root_vars are
source vars, no extensions have yet been admitted, N and cap are frozen.  The
functions used by v2 depend only on those fields plus ledger work counters; work
counters do not affect acceptance.  progress_phi depends only on residual/root
live-variable counts and the frozen extension cap.

No shard alone can claim universal NO_RESCUE. Aggregation is fail-closed.
P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from experiments.direct import janus_pirc_decision_core_v0_4 as core
from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.theorem_extraction import c025_adversarial_delta_pair_search as adv

P_VS_NP = "OPEN"
LEAF_NVARS = 10
LEAF_CLAUSES = 90
LEAF_WIDTH = 4
SEED = 39100


def candidate():
    source, left, right = adv.build_selector_source(LEAF_NVARS, LEAF_CLAUSES, LEAF_WIDTH, SEED)
    product = adv.direct_selector_product(left, right)
    N = base.input_size_units(source)
    return source, product, N, N * N


def meta(source, product, N, cap):
    return {
        "family": "DISJOINT_SELECTOR_PRODUCT",
        "leaf_nvars": LEAF_NVARS,
        "leaf_clauses": LEAF_CLAUSES,
        "leaf_width": LEAF_WIDTH,
        "seed": SEED,
        "source_fingerprint": base.fingerprint(source),
        "product_fingerprint": base.fingerprint(product),
        "N": N,
        "cap": cap,
        "product_units": base.state_units(product),
        "live_product_variables": len(base.vars_of(product)),
    }


def direct_target_state(source, product, N):
    return base.EngineState(
        root=source,
        residual=product,
        fixed_assignment={},
        root_vars=base.vars_of(source),
        extension_defs=[],
        elimination_history=[base.ElimSnapshot(source, 1, "PURE_ELIM")],
        seen={base.fingerprint(source), base.fingerprint(product)},
        N=N,
        cap_exponent=2,
        extension_exponent=2,
        ledger=base.Ledger(question_count=1),
    )


def run_reachability(source, product, N, cap):
    reach = adv.verify_reachable_callsite(source, product)
    exact_selector, selector_stats = base.eliminate_var_capped(source, 1, cap)
    selector_exact = exact_selector == product and base.verify_elimination_transition(source, 1, product, cap)
    return {
        "schema": "JANUS/C025/L1-FANOUT/REACHABILITY/v1",
        "status": "PASS" if reach["reachable_at_frozen_ordinary_callsite"] and selector_exact else "FAIL",
        "candidate": meta(source, product, N, cap),
        "reachable_at_frozen_ordinary_callsite": bool(reach["reachable_at_frozen_ordinary_callsite"]),
        "selector_pivot_1_exact_product": selector_exact,
        "selector_stats": selector_stats,
        "reachability": reach,
        "P_VS_NP": P_VS_NP,
    }


def run_ordinary(source, product, N, cap, shard_index, shard_count):
    pivots = list(base.vars_of(product))
    selected = [(i, v) for i, v in enumerate(pivots) if i % shard_count == shard_index]
    rows = []
    for i, v in selected:
        out, stats = base.eliminate_var_capped(product, v, cap)
        rows.append({
            "pivot_index": i,
            "pivot": v,
            "overflow": out is None,
            "stats": stats,
            "after_fingerprint": base.fingerprint(out) if out is not None else None,
        })
    return {
        "schema": "JANUS/C025/L1-FANOUT/ORDINARY-SHARD/v1",
        "status": "SHARD_COMPLETE",
        "candidate": meta(source, product, N, cap),
        "shard": {"index": shard_index, "count": shard_count},
        "global_pivot_count": len(pivots),
        "selected_pivot_indices": [i for i, _ in selected],
        "rows": rows,
        "complete_for_selected_indices": len(rows) == len(selected),
        "all_selected_overflow": all(r["overflow"] for r in rows),
        "P_VS_NP": P_VS_NP,
    }


def run_v2(source, product, N, cap, shard_index, shard_count):
    state = direct_target_state(source, product, N)
    pairs = core.v2.all_or_pair_candidates(product)
    selected = [(i, p) for i, p in enumerate(pairs) if i % shard_count == shard_index]
    fresh = core.v2.next_fresh_extension(state)
    before_phi = state.progress_phi()
    rows = []
    rescue = None
    for pair_index, (a, b) in selected:
        macro, cert = core.v2.apply_or_pair_v2(product, a, b, fresh)
        if not core.v2.verify_or_pair_v2(product, macro, cert):
            raise AssertionError(f"V2_CERT_REPLAY_FAILED_AT_{pair_index}")
        macro_units = base.state_units(macro)
        row = {
            "pair_index": pair_index,
            "pair": [a, b],
            "macro_units": macro_units,
            "macro_over_cap": macro_units > cap,
        }
        if macro_units <= cap:
            elim = base.first_capped_elimination(state, macro, roots_only=True)
            if elim is not None:
                pivot, after, stats = elim
                if not base.verify_elimination_transition(macro, pivot, after, cap):
                    raise AssertionError(f"ELIM_REPLAY_FAILED_AT_{pair_index}_{pivot}")
                after_phi = state.progress_phi(after, state.ledger.extension_count + 1)
                row.update({
                    "fitting_root_pivot": int(pivot),
                    "after_units": base.state_units(after),
                    "after_fingerprint": base.fingerprint(after),
                    "before_phi": before_phi,
                    "after_phi": after_phi,
                    "progress_accepts": after_phi < before_phi,
                    "elim_stats": stats,
                })
                if after_phi < before_phi:
                    rescue = dict(row)
                    rows.append(row)
                    break
            else:
                row["fitting_root_pivot"] = None
        rows.append(row)
    complete = rescue is None and len(rows) == len(selected)
    return {
        "schema": "JANUS/C025/L1-FANOUT/V2-SHARD/v1",
        "status": "EXACT_RESCUE_FOUND" if rescue else "SHARD_COMPLETE_NO_RESCUE",
        "candidate": meta(source, product, N, cap),
        "shard": {"index": shard_index, "count": shard_count},
        "global_pair_count": len(pairs),
        "selected_pair_indices": [i for i, _ in selected],
        "tested_rows": rows,
        "tested_count": len(rows),
        "complete_for_selected_indices": complete,
        "rescue": rescue,
        "semantic_state_signature": {
            "root_vars": list(state.root_vars),
            "extension_count": state.ledger.extension_count,
            "extension_defs_count": len(state.extension_defs),
            "N": state.N,
            "state_cap": state.state_cap,
            "extension_cap": state.extension_cap,
            "before_phi": before_phi,
        },
        "authority_boundary": {
            "original_v2_candidate_generator": True,
            "original_v2_apply_verify": True,
            "original_eliminate_var_capped_via_first_capped_elimination": True,
            "original_progress_phi": True,
            "shard_no_rescue_is_not_global_no_rescue": True,
        },
        "P_VS_NP": P_VS_NP,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["reachability", "ordinary", "v2"], required=True)
    ap.add_argument("--shard-index", type=int, default=0)
    ap.add_argument("--shard-count", type=int, default=1)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    if args.shard_count < 1 or not (0 <= args.shard_index < args.shard_count):
        raise ValueError("invalid shard coordinates")

    source, product, N, cap = candidate()
    if args.mode == "reachability":
        report = run_reachability(source, product, N, cap)
    elif args.mode == "ordinary":
        report = run_ordinary(source, product, N, cap, args.shard_index, args.shard_count)
    else:
        report = run_v2(source, product, N, cap, args.shard_index, args.shard_count)

    Path(args.out).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("status") != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
