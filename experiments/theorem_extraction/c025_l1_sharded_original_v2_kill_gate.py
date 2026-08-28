#!/usr/bin/env python3
"""Sharded exact attack on the frozen C025 L1 root-phase grammar candidate.

The candidate family/parameters were frozen before this scan by the existing
v2-gap workflow:
  DISJOINT_SELECTOR_PRODUCT leaf_nvars=10, leaf_clauses=90,
  leaf_width=4, seed=39100.

Each shard runs on the exact reachable callsite of the unmodified
PIRC_DECISION_CORE_V0_4 and exhausts a disjoint subset of the ORIGINAL frozen
v2 candidate list.  Candidate semantics are not approximated:
  all_or_pair_candidates -> apply_or_pair_v2 -> verify_or_pair_v2 ->
  first_capped_elimination(roots_only=True) -> progress_phi.

A shard-level NO_RESCUE has authority only over its listed candidate indices.
Only the aggregator may conclude full-v2 NO_RESCUE after every shard is present
and complete.  P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path

from experiments.direct import janus_pirc_decision_core_v0_4 as core
from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.theorem_extraction import c025_adversarial_delta_pair_search as adv

P_VS_NP = "OPEN"
LEAF_NVARS = 10
LEAF_CLAUSES = 90
LEAF_WIDTH = 4
SEED = 39100


class ShardDone(Exception):
    pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard-index", type=int, required=True)
    ap.add_argument("--shard-count", type=int, required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    if args.shard_count < 1 or not (0 <= args.shard_index < args.shard_count):
        raise ValueError("invalid shard coordinates")

    source, left, right = adv.build_selector_source(
        LEAF_NVARS, LEAF_CLAUSES, LEAF_WIDTH, SEED
    )
    product = adv.direct_selector_product(left, right)
    source_fp = base.fingerprint(source)
    product_fp = base.fingerprint(product)
    N = base.input_size_units(source)
    cap = N * N

    ordinary_rows = [adv.raw_units_probe(product, v, cap) for v in base.vars_of(product)]
    all_ordinary_overflow = all(r["overflow"] for r in ordinary_rows)
    if not all_ordinary_overflow:
        raise AssertionError("FROZEN_CANDIDATE_NO_LONGER_ALL_ORDINARY_OVERFLOW")

    original_v2 = core.v2.discover_macro_restore_v2
    receipt = None

    def wrapped_v2(state: base.EngineState):
        nonlocal receipt
        if base.fingerprint(state.residual) != product_fp:
            return original_v2(state)

        if state.N != N or state.state_cap != cap:
            raise AssertionError("TARGET_BUDGET_DRIFT")
        if state.residual != product:
            raise AssertionError("TARGET_RESIDUAL_FINGERPRINT_COLLISION")

        pairs = core.v2.all_or_pair_candidates(state.residual)
        selected = [(i, p) for i, p in enumerate(pairs) if i % args.shard_count == args.shard_index]
        fresh = core.v2.next_fresh_extension(state)
        before_phi = state.progress_phi()
        roots_live = sorted(v for v in state.root_vars if v in set(base.vars_of(state.residual)))
        if not roots_live:
            raise AssertionError("TARGET_HAS_NO_LIVE_ROOTS")

        tested = 0
        macro_over_cap = 0
        no_fitting_root = 0
        progress_rejected = 0
        rescue = None
        for pair_index, (a, b) in selected:
            tested += 1
            macro_cnf, macro_cert = core.v2.apply_or_pair_v2(state.residual, a, b, fresh)
            if not core.v2.verify_or_pair_v2(state.residual, macro_cnf, macro_cert):
                raise AssertionError(f"ORIGINAL_V2_CERT_REPLAY_FAILED_AT_{pair_index}")
            if base.state_units(macro_cnf) > state.state_cap:
                macro_over_cap += 1
                continue

            elim = base.first_capped_elimination(state, macro_cnf, roots_only=True)
            if elim is None:
                no_fitting_root += 1
                continue
            pivot, after, elim_stats = elim
            if not base.verify_elimination_transition(macro_cnf, pivot, after, state.state_cap):
                raise AssertionError(f"ORIGINAL_ELIM_REPLAY_FAILED_AT_{pair_index}_{pivot}")
            after_phi = state.progress_phi(after, state.ledger.extension_count + 1)
            if after_phi >= before_phi:
                progress_rejected += 1
                continue

            rescue = {
                "pair_index_zero_based": pair_index,
                "pair": [a, b],
                "pivot": int(pivot),
                "macro_units": int(base.state_units(macro_cnf)),
                "macro_fingerprint": base.fingerprint(macro_cnf),
                "after_units": int(base.state_units(after)),
                "after_fingerprint": base.fingerprint(after),
                "before_phi": list(before_phi) if isinstance(before_phi, tuple) else before_phi,
                "after_phi": list(after_phi) if isinstance(after_phi, tuple) else after_phi,
                "elim_stats": deepcopy(elim_stats),
                "macro_cert": deepcopy(macro_cert),
            }
            break

        receipt = {
            "schema": "JANUS/C025/L1-SHARDED-ORIGINAL-V2-KILL-GATE/SHARD/v1",
            "status": "EXACT_RESCUE_FOUND_IN_SHARD" if rescue else "SHARD_COMPLETE_NO_RESCUE",
            "shard": {"index": args.shard_index, "count": args.shard_count},
            "frozen_candidate": {
                "family": "DISJOINT_SELECTOR_PRODUCT",
                "leaf_nvars": LEAF_NVARS,
                "leaf_clauses": LEAF_CLAUSES,
                "leaf_width": LEAF_WIDTH,
                "seed": SEED,
                "source_fingerprint": source_fp,
                "product_fingerprint": product_fp,
                "N": N,
                "cap": cap,
                "product_units": base.state_units(product),
                "all_ordinary_pivots_overflow": True,
                "ordinary_pivot_count": len(ordinary_rows),
            },
            "reachability": {
                "observed_at_unmodified_core_v2_callsite": True,
                "root_variables_live": len(roots_live),
            },
            "v2_scope": {
                "candidate_count_global": len(pairs),
                "selected_indices": [i for i, _ in selected],
                "selected_count": len(selected),
                "tested_count": tested,
                "macro_over_cap": macro_over_cap,
                "no_fitting_root": no_fitting_root,
                "progress_rejected": progress_rejected,
                "complete_for_selected_indices": rescue is None and tested == len(selected),
            },
            "rescue": rescue,
            "authority_boundary": {
                "uses_original_v2_candidate_generator": True,
                "uses_original_v2_apply_and_verify": True,
                "uses_original_capped_root_elimination": True,
                "uses_original_progress_gate": True,
                "shard_no_rescue_is_not_full_scope_no_rescue": True,
                "aggregator_requires_all_shards_complete": True,
                "P_VS_NP": P_VS_NP,
            },
            "P_VS_NP": P_VS_NP,
        }
        raise ShardDone()

    core.v2.discover_macro_restore_v2 = wrapped_v2
    terminal = None
    try:
        try:
            terminal = core.solve_decision_core(source)
        except ShardDone:
            pass
    finally:
        core.v2.discover_macro_restore_v2 = original_v2

    if receipt is None:
        raise AssertionError(
            "FROZEN_CORE_DID_NOT_REACH_TARGET_V2_CALLSITE: "
            + json.dumps({
                "status": terminal.get("status") if terminal else None,
                "reason": terminal.get("reason") if terminal else None,
                "residual": terminal.get("residual_fingerprint") if terminal else None,
            }, sort_keys=True)
        )

    Path(args.out).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
