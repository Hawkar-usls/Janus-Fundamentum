#!/usr/bin/env python3
"""Compute-optimized exact junction-relief microscope.

Same frozen witness, v2 pair, root set and raw-unit decomposition as the original
microscope.  The sole optimization is deletion of post-hoc canon_cnf(raw) from
each uncapped profile: C025's cap and J(F,a,b,x) are defined on raw pre-subsumption
units, so post-subsumption canonical_units are irrelevant to every verdict here.
"""
from __future__ import annotations

import json

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.theorem_extraction import c025_v2_junction_relief_microscope as slow

P_VS_NP = "OPEN"


def raw_profile_fast(cnf: base.CNF, pivot: int) -> dict:
    pos = [c for c in cnf if pivot in c]
    neg = [c for c in cnf if -pivot in c]
    retained = {c for c in cnf if pivot not in c and -pivot not in c}
    resolvents: set[base.Clause] = set()
    non_taut = 0
    taut = 0
    for p in pos:
        for n in neg:
            r = base.resolve_on_var(p, n, pivot)
            if r is None:
                taut += 1
            else:
                non_taut += 1
                resolvents.add(r)
    unique_new = resolvents - retained
    raw = retained | resolvents
    retained_units = slow.state_units_of_set(retained)
    new_units = sum(1 + len(c) for c in unique_new)
    raw_units = slow.state_units_of_set(raw)
    if raw_units != retained_units + new_units:
        raise AssertionError("RAW_UNIT_DECOMPOSITION_DRIFT")
    return {
        "pivot": pivot,
        "positive_parents": len(pos),
        "negative_parents": len(neg),
        "parent_pairs": len(pos) * len(neg),
        "tautology_pairs": taut,
        "non_tautology_pairs": non_taut,
        "unique_resolvents": len(resolvents),
        "resolvent_collisions": non_taut - len(resolvents),
        "duplicates_to_retained": len(resolvents & retained),
        "retained_count": len(retained),
        "retained_units": retained_units,
        "unique_new_resolvents": len(unique_new),
        "unique_new_resolvent_units": new_units,
        "raw_units": raw_units,
    }


def main() -> int:
    source, product, _ = slow.build_witness()
    N, cap = slow.EXPECTED_N, slow.EXPECTED_CAP
    before_units = base.state_units(product)
    t = slow.pair_frequency(product, *slow.WINNING_PAIR)
    macro, cert = v2.apply_or_pair_v2(product, *slow.WINNING_PAIR, slow.FRESH_EXTENSION)
    if not v2.verify_or_pair_v2(product, macro, cert):
        raise AssertionError("V2_MACRO_REPLAY_FAILED")
    if cert["replaced_occurrences"] != t or base.state_units(macro) != 25031:
        raise AssertionError("WINNING_MACRO_DRIFT")

    rows = []
    for root in range(2, 14):
        pre = raw_profile_fast(product, root)
        post = raw_profile_fast(macro, root)
        relief = pre["raw_units"] - post["raw_units"]
        retained_delta = post["retained_units"] - pre["retained_units"]
        new_delta = post["unique_new_resolvent_units"] - pre["unique_new_resolvent_units"]
        if relief != -(retained_delta + new_delta):
            raise AssertionError("RELIEF_DECOMPOSITION_DRIFT")
        rows.append({
            "root_pivot": root,
            "pre": pre,
            "post": post,
            "junction_relief": relief,
            "post_cap_margin": cap - post["raw_units"],
            "retained_units_delta": retained_delta,
            "unique_new_resolvent_units_delta": new_delta,
            "restored_under_cap": post["raw_units"] <= cap,
        })

    winner = next(r for r in rows if r["root_pivot"] == slow.WINNING_ROOT)
    pre, post = winner["pre"], winner["post"]
    p, q = pre["positive_parents"], pre["negative_parents"]
    predicted_p = p - t + 1
    predicted_q = q + 1
    guaranteed = t * (q + 1) - (p + q + 1)
    if post["positive_parents"] > predicted_p or post["negative_parents"] > predicted_q:
        raise AssertionError("PARENT_COUNT_RELIEF_LEMMA_VIOLATED")
    if pre["parent_pairs"] - post["parent_pairs"] < guaranteed:
        raise AssertionError("PARENT_PRODUCT_RELIEF_LEMMA_VIOLATED")

    # Exact frozen-v2 first-rescue consistency remains mandatory.
    state = base.EngineState(
        root=source, residual=product, fixed_assignment={}, root_vars=base.vars_of(source),
        extension_defs=[], elimination_history=[], seen=set(), N=N,
        cap_exponent=2, extension_exponent=2, ledger=base.Ledger(),
    )
    frozen = v2.discover_macro_restore_v2(state)
    if frozen is None:
        raise AssertionError("FROZEN_V2_RESCUE_DISAPPEARED")
    fm, fr, fa, fc, fs = frozen
    if tuple(fc["represents"]) != slow.WINNING_PAIR or int(fr) != slow.WINNING_ROOT:
        raise AssertionError("FROZEN_V2_FIRST_RESCUE_DRIFT")

    report = {
        "schema": "JANUS/C025/V2-JUNCTION-RELIEF-MICROSCOPE-FAST/v1",
        "status": "EXACT_WITNESS_RELIEF_DECOMPOSED",
        "source_fingerprint": slow.EXPECTED_SOURCE_FP,
        "product_fingerprint": slow.EXPECTED_PRODUCT_FP,
        "N": N,
        "state_cap": cap,
        "product_state_units": before_units,
        "winning_pair": list(slow.WINNING_PAIR),
        "winning_pair_frequency": t,
        "old_frequent_pair_sufficient_threshold": before_units - 2*N + 11,
        "macro_state_units": base.state_units(macro),
        "macro_state_unit_reduction": before_units - base.state_units(macro),
        "parent_pair_relief_identity": {
            "p": p, "q": q, "t": t,
            "predicted_precanonical_positive_after": predicted_p,
            "predicted_precanonical_negative_after": predicted_q,
            "guaranteed_parent_pair_relief": guaranteed,
            "observed_parent_pair_relief": pre["parent_pairs"] - post["parent_pairs"],
            "status": "PASS"
        },
        "winning_root_relief": winner,
        "all_root_profiles": rows,
        "roots_restored_under_cap_by_same_macro": [r["root_pivot"] for r in rows if r["restored_under_cap"]],
        "frozen_v2_first_rescue": {
            "pair": fc["represents"],
            "replaced_occurrences": fc["replaced_occurrences"],
            "root_pivot": int(fr),
            "elimination_raw_units": int(fs["raw_units"]),
            "after_state_units": base.state_units(fa),
        },
        "exact_observation": {
            "winning_raw_relief": winner["junction_relief"],
            "retained_mass_change": winner["retained_units_delta"],
            "unique_new_resolvent_mass_change": winner["unique_new_resolvent_units_delta"],
            "removed_post_subsumption_measurement": True,
            "reason": "post-subsumption canonical_units do not enter raw cap or junction-relief definitions"
        },
        "scientific_boundary": {
            "same_scientific_measurement_as_slow_microscope": True,
            "only_irrelevant_post_subsumption_cost_removed": True,
            "single_frozen_reachable_witness": True,
            "finite_observation_is_not_totality_proof": True,
            "L1A": "REFUTED", "L1B": "REFUTED", "L1": "OPEN",
            "P2_REACHABLE_PRESERVATION": "OPEN", "P_VS_NP": P_VS_NP
        },
        "P_VS_NP": P_VS_NP
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
