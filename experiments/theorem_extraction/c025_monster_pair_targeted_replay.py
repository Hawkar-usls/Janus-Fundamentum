#!/usr/bin/env python3
"""Targeted ORIGINAL-semantics replay of a candidate v2 rescue on the reachable monster.

A search-only fast screen suggested pair (-12,-15).  This file gives that screen
zero theorem authority.  It reconstructs the frozen reachable monster, verifies
that the pair belongs to frozen v2's exhaustive candidate grammar, applies the
OR-pair macro using the ORIGINAL v2.apply_or_pair_v2 implementation, replays the
macro verifier, and then calls the ORIGINAL base.first_capped_elimination with
roots_only=True.  A successful exact return proves only that the current v2
grammar CONTAINS a rescue for this witness; it does not prove universal L1.
"""
from __future__ import annotations

import json

from experiments.direct import janus_pirc_decision_core_v0_4 as core
from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.theorem_extraction import c025_adversarial_delta_pair_search as adv

P_VS_NP = "OPEN"
SOURCE_FP = "69e4c811b0e34534c09beb27b75578ba3bfb6625c27aaeea1f8838f44d6281c4"
PRODUCT_FP = "e10600e0f79ad6f143f3b67b04d4b616da5f59e4a4832af5cbb329a574f0dac7"
PAIR = (-12, -15)


def main() -> int:
    source, left, right = adv.build_selector_source(8, 72, 4, 29100)
    product = adv.direct_selector_product(left, right)
    assert base.fingerprint(source) == SOURCE_FP
    assert base.fingerprint(product) == PRODUCT_FP
    N = base.input_size_units(source)
    assert N == 882

    ledger = base.Ledger()
    state = base.EngineState(
        root=source,
        residual=product,
        fixed_assignment={},
        root_vars=base.vars_of(source),
        extension_defs=[],
        elimination_history=[],
        seen=set(),
        N=N,
        cap_exponent=2,
        extension_exponent=2,
        ledger=ledger,
    )
    candidates = core.v2.all_or_pair_candidates(product)
    if PAIR not in candidates:
        raise AssertionError("SCREENED_PAIR_NOT_IN_FROZEN_V2_GRAMMAR")
    pair_index = candidates.index(PAIR)
    fresh = core.v2.next_fresh_extension(state)
    assert fresh == 18

    before_phi = state.progress_phi()
    macro_cnf, macro_cert = core.v2.apply_or_pair_v2(product, PAIR[0], PAIR[1], fresh)
    if not core.v2.verify_or_pair_v2(product, macro_cnf, macro_cert):
        raise AssertionError("ORIGINAL_V2_MACRO_REPLAY_FAILED")
    if base.state_units(macro_cnf) > state.state_cap:
        raise AssertionError("SCREENED_MACRO_EXCEEDS_CAP")

    elim = base.first_capped_elimination(state, macro_cnf, roots_only=True)
    if elim is None:
        result = {
            "schema": "JANUS/C025/MONSTER-PAIR-TARGETED-REPLAY/v1",
            "status": "SCREEN_CANDIDATE_REJECTED_BY_ORIGINAL_SEMANTICS",
            "source_fingerprint": SOURCE_FP,
            "product_fingerprint": PRODUCT_FP,
            "pair": list(PAIR),
            "pair_candidate_index_zero_based": pair_index,
            "pair_candidate_count": len(candidates),
            "macro_state_units": base.state_units(macro_cnf),
            "state_cap": state.state_cap,
            "scientific_boundary": {
                "fast_screen_has_theorem_authority": False,
                "original_v2_macro_used": True,
                "original_root_elimination_used": True,
                "L1": "OPEN",
                "P_VS_NP": P_VS_NP,
            },
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    pivot, after, elim_stats = elim
    if not base.verify_elimination_transition(macro_cnf, pivot, after, state.state_cap):
        raise AssertionError("ORIGINAL_ROOT_ELIMINATION_REPLAY_FAILED")
    after_phi = state.progress_phi(after, 1)
    strict_progress = after_phi < before_phi
    if not strict_progress:
        raise AssertionError("SCREENED_RESCUE_FAILS_FROZEN_PROGRESS_GATE")

    report = {
        "schema": "JANUS/C025/MONSTER-PAIR-TARGETED-REPLAY/v1",
        "status": "EXACT_V2_GRAMMAR_RESCUE_WITNESS_CONFIRMED",
        "source_fingerprint": SOURCE_FP,
        "product_fingerprint": PRODUCT_FP,
        "N": N,
        "state_cap": state.state_cap,
        "product_state_units": base.state_units(product),
        "pair": list(PAIR),
        "pair_candidate_index_zero_based": pair_index,
        "pair_candidate_count": len(candidates),
        "replaced_occurrences": int(macro_cert.get("replaced_occurrences", 0)),
        "fresh_extension": fresh,
        "macro_state_units": base.state_units(macro_cnf),
        "macro_fingerprint": base.fingerprint(macro_cnf),
        "selected_root_pivot_by_original_first_capped": int(pivot),
        "after_state_units": base.state_units(after),
        "after_fingerprint": base.fingerprint(after),
        "elimination_stats": elim_stats,
        "before_phi": before_phi,
        "after_phi": after_phi,
        "strict_progress": strict_progress,
        "candidate_results": {
            "L1_ROOT_PHASE_POLYNOMIAL_GRAMMAR_TOTALITY": "SURVIVES_THIS_WITNESS_BECAUSE_EXACT_V2_RESCUE_EXISTS__NOT_PROVED",
            "L1A_ALL_PIVOT_OVERFLOW_FORCES_FREQUENT_PAIR": "REFUTED_BY_REACHABLE_WITNESS",
            "L1B_ALL_PIVOT_OVERFLOW_FORCES_PAIR_DENSITY": "REFUTED_BY_REACHABLE_WITNESS"
        },
        "scientific_boundary": {
            "fast_screen_has_theorem_authority": False,
            "pair_membership_in_frozen_exhaustive_v2_grammar_verified": True,
            "original_v2_apply_and_verify_used": True,
            "original_first_capped_elimination_roots_only_used": True,
            "exact_rescue_existence_on_one_witness_is_not_universal_totality": True,
            "L1": "OPEN",
            "P2_REACHABLE_PRESERVATION": "OPEN",
            "P_VS_NP": P_VS_NP
        }
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
