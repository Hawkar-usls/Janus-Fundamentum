#!/usr/bin/env python3
"""Exact microscope for v2 junction relief on the frozen L1A/L1B witness.

The witness is reconstructed from frozen leaf CNFs and both source/product
fingerprints are checked.  The winning frozen-v2 pair (2,3) is replayed exactly.
For every root pivot, this microscope computes uncapped exact raw resolution
profiles before and after the macro, decomposing raw state units into retained
mass and unique-new-resolvent mass.  It also checks the proved pivot-involving
parent-product identity on root pivot 2.

This is finite witness analysis, not a totality proof. P_VS_NP remains OPEN.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.theorem_extraction import c025_adversarial_delta_pair_dispersion_attack as build

P_VS_NP = "OPEN"
WITNESS_PATH = Path("research/C025_L1A_L1B_WITNESS_CNF_2026-08-28.json")
EXPECTED_N = 614
EXPECTED_CAP = 376996
EXPECTED_SOURCE_FP = "03506158fa7d60deb18f1832f1733e27f511d354024aff21f7afd33e27935b0f"
EXPECTED_PRODUCT_FP = "3559df2656aade8e446d3a5eeedd419578fcebcf07ebecd35b2556ae35f68089"
WINNING_PAIR = (2, 3)
WINNING_ROOT = 2
FRESH_EXTENSION = 14


def state_units_of_set(rows: set[base.Clause]) -> int:
    return 1 + len(rows) + sum(len(c) for c in rows)


def raw_resolution_profile(cnf: base.CNF, pivot: int) -> dict:
    pos = [c for c in cnf if pivot in c]
    neg = [c for c in cnf if -pivot in c]
    retained = {c for c in cnf if pivot not in c and -pivot not in c}
    resolvents: set[base.Clause] = set()
    non_taut_pairs = 0
    tautologies = 0
    for p in pos:
        for n in neg:
            r = base.resolve_on_var(p, n, pivot)
            if r is None:
                tautologies += 1
            else:
                non_taut_pairs += 1
                resolvents.add(r)
    unique_new = resolvents - retained
    raw = retained | resolvents
    retained_units = state_units_of_set(retained)
    unique_new_units = sum(1 + len(c) for c in unique_new)
    raw_units = state_units_of_set(raw)
    if raw_units != retained_units + unique_new_units:
        raise AssertionError("RAW_UNIT_DECOMPOSITION_DRIFT")
    return {
        "pivot": pivot,
        "positive_parents": len(pos),
        "negative_parents": len(neg),
        "parent_pairs": len(pos) * len(neg),
        "tautology_pairs": tautologies,
        "non_tautology_pairs": non_taut_pairs,
        "unique_resolvents": len(resolvents),
        "resolvent_collisions": non_taut_pairs - len(resolvents),
        "duplicates_to_retained": len(resolvents & retained),
        "retained_count": len(retained),
        "retained_units": retained_units,
        "unique_new_resolvents": len(unique_new),
        "unique_new_resolvent_units": unique_new_units,
        "raw_units": raw_units,
        "canonical_units": base.state_units(base.canon_cnf(raw)),
    }


def pair_frequency(cnf: base.CNF, a: int, b: int) -> int:
    return sum(1 for c in cnf if a in c and b in c)


def build_witness() -> tuple[base.CNF, base.CNF, dict]:
    data = json.loads(WITNESS_PATH.read_text())
    left = base.canon_cnf(data["left_leaf"])
    right = base.canon_cnf(data["right_leaf"])
    source = build.build_source(left, right)
    product = build.build_product_global(left, right)
    if base.fingerprint(source) != EXPECTED_SOURCE_FP:
        raise AssertionError("SOURCE_FINGERPRINT_DRIFT")
    if base.fingerprint(product) != EXPECTED_PRODUCT_FP:
        raise AssertionError("PRODUCT_FINGERPRINT_DRIFT")
    N = base.input_size_units(source)
    if N != EXPECTED_N or N * N != EXPECTED_CAP:
        raise AssertionError("ROOT_RELATIVE_CAP_DRIFT")
    return source, product, data


def main() -> int:
    source, product, _data = build_witness()
    before_units = base.state_units(product)
    t = pair_frequency(product, *WINNING_PAIR)
    macro, cert = v2.apply_or_pair_v2(product, *WINNING_PAIR, FRESH_EXTENSION)
    if not v2.verify_or_pair_v2(product, macro, cert):
        raise AssertionError("V2_MACRO_REPLAY_FAILED")
    if cert["replaced_occurrences"] != t:
        raise AssertionError("PAIR_FREQUENCY_CERT_DRIFT")
    if base.state_units(macro) != 25031:
        raise AssertionError("WINNING_MACRO_SIZE_DRIFT")

    roots = tuple(range(2, 14))
    rows = []
    for root in roots:
        pre = raw_resolution_profile(product, root)
        post = raw_resolution_profile(macro, root)
        relief = pre["raw_units"] - post["raw_units"]
        retained_delta = post["retained_units"] - pre["retained_units"]
        new_resolvent_delta = post["unique_new_resolvent_units"] - pre["unique_new_resolvent_units"]
        if relief != -(retained_delta + new_resolvent_delta):
            raise AssertionError("RELIEF_DECOMPOSITION_DRIFT")
        rows.append({
            "root_pivot": root,
            "pre": pre,
            "post": post,
            "junction_relief": relief,
            "post_cap_margin": EXPECTED_CAP - post["raw_units"],
            "retained_units_delta": retained_delta,
            "unique_new_resolvent_units_delta": new_resolvent_delta,
            "restored_under_cap": post["raw_units"] <= EXPECTED_CAP,
        })

    winner = next(r for r in rows if r["root_pivot"] == WINNING_ROOT)
    pre = winner["pre"]
    post = winner["post"]
    p, q = pre["positive_parents"], pre["negative_parents"]
    predicted_p = p - t + 1
    predicted_q = q + 1
    guaranteed_pair_relief = t * (q + 1) - (p + q + 1)
    if post["positive_parents"] > predicted_p or post["negative_parents"] > predicted_q:
        raise AssertionError("PARENT_COUNT_RELIEF_LEMMA_VIOLATED")
    if pre["parent_pairs"] - post["parent_pairs"] < guaranteed_pair_relief:
        raise AssertionError("PARENT_PRODUCT_RELIEF_LEMMA_VIOLATED")

    # Reconstruct the exact frozen-v2 state context and require its first rescue
    # to be the same pair/root recorded in the falsification certificate.
    state = base.EngineState(
        root=source,
        residual=product,
        fixed_assignment={},
        root_vars=base.vars_of(source),
        extension_defs=[],
        elimination_history=[],
        seen=set(),
        N=EXPECTED_N,
        cap_exponent=2,
        extension_exponent=2,
        ledger=base.Ledger(),
    )
    frozen = v2.discover_macro_restore_v2(state)
    if frozen is None:
        raise AssertionError("FROZEN_V2_RESCUE_DISAPPEARED")
    frozen_macro, frozen_root, frozen_after, frozen_cert, frozen_stats = frozen
    if tuple(frozen_cert["represents"]) != WINNING_PAIR or int(frozen_root) != WINNING_ROOT:
        raise AssertionError("FROZEN_V2_FIRST_RESCUE_DRIFT")
    if base.fingerprint(frozen_macro) != base.fingerprint(macro):
        raise AssertionError("FROZEN_V2_MACRO_FINGERPRINT_DRIFT")

    restored = [r for r in rows if r["restored_under_cap"]]
    report = {
        "schema": "JANUS/C025/V2-JUNCTION-RELIEF-MICROSCOPE/v1",
        "status": "EXACT_WITNESS_RELIEF_DECOMPOSED",
        "source_fingerprint": EXPECTED_SOURCE_FP,
        "product_fingerprint": EXPECTED_PRODUCT_FP,
        "N": EXPECTED_N,
        "state_cap": EXPECTED_CAP,
        "product_state_units": before_units,
        "winning_pair": list(WINNING_PAIR),
        "winning_pair_frequency": t,
        "old_frequent_pair_sufficient_threshold": before_units - 2 * EXPECTED_N + 11,
        "macro_state_units": base.state_units(macro),
        "macro_state_unit_reduction": before_units - base.state_units(macro),
        "winning_root": WINNING_ROOT,
        "parent_pair_relief_identity": {
            "p": p,
            "q": q,
            "t": t,
            "predicted_precanonical_positive_after": predicted_p,
            "predicted_precanonical_negative_after": predicted_q,
            "guaranteed_parent_pair_relief": guaranteed_pair_relief,
            "observed_parent_pair_relief": pre["parent_pairs"] - post["parent_pairs"],
            "status": "PASS"
        },
        "winning_root_relief": winner,
        "all_root_profiles": rows,
        "roots_restored_under_cap_by_same_macro": [r["root_pivot"] for r in restored],
        "frozen_v2_first_rescue": {
            "pair": frozen_cert["represents"],
            "replaced_occurrences": frozen_cert["replaced_occurrences"],
            "root_pivot": int(frozen_root),
            "elimination_raw_units": int(frozen_stats["raw_units"]),
            "after_state_units": base.state_units(frozen_after),
        },
        "exact_observation": {
            "macro_representation_reduction": before_units - base.state_units(macro),
            "winning_raw_relief": winner["junction_relief"],
            "retained_mass_change": winner["retained_units_delta"],
            "unique_new_resolvent_mass_change": winner["unique_new_resolvent_units_delta"],
            "interpretation": "On this exact reachable witness, v2 rescue is dominated by reduction in unique-new-resolvent mass rather than macro representation shrinkage. This is a finite structural observation, not a universal theorem."
        },
        "next_proof_obligation": {
            "quantity": "J(F,a,b,x)=U_raw(F,x)-U_raw(M_ab(F),x)",
            "target": "derive a universal lower bound on J from syntactic parent incidence plus tautology/collision structure strong enough to imply existence of a capped v2 root rescue on every reachable all-pivot-overflow root state",
            "status": "OPEN"
        },
        "scientific_boundary": {
            "single_frozen_reachable_witness": True,
            "finite_observation_is_not_totality_proof": True,
            "L1A": "REFUTED",
            "L1B": "REFUTED",
            "L1": "OPEN",
            "P2_REACHABLE_PRESERVATION": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
        "P_VS_NP": P_VS_NP,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
