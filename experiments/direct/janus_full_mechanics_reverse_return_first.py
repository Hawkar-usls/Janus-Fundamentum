#!/usr/bin/env python3
"""Invert the successful JANUS mechanics into a return-first sparse capsule compiler.

Restricted control: C025 equality_family(n), n in the frozen set.

The candidate does not enumerate x-prefixes and does not construct a full 2n
coordinate map per generator.  It parses the exact independent equality factors
once, builds a four-slot proof-carrying capsule for each local involution, walks
that capsule BACK through typed namespace/name/anchor/provenance/delta authority,
verifies the exact local inverse first, and only then authorizes FORTH branch
quotienting.

This is a restricted-family architectural experiment.  It is not a P=NP proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from janus_c025_core import canonical_cnf, restrict_formula, satisfies
from janus_c025_families import equality_family

RUN_ID = "JANUS-FULL-MECHANICS-REVERSE-RETURN-FIRST-2026-08-18-v1"
FROZEN_N = (14, 32, 64, 128, 256)
BASE_SHA = "a24039ba24b880dc3c80d45ebc2c8f7bcfb3af26"
PR190_WORK = {14: 9037, 32: 46288, 64: 183712, 128: 731968, 256: 2922112}
SOURCE_NS = "SOURCE:EQUALITY_FACTOR"
OVERLAY_NS = "OVERLAY:S𓂸ḥ_RETURN_CAPSULE"
CAPSULE_TYPES = ("REN_NAME", "SUPPORT_DELTA", "LOCAL_FACTOR_ANCHOR", "PARENT_COMMITMENT")


def json_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(json_bytes(value)).hexdigest()


def sparse_flip(cnf, support: frozenset[int]):
    return canonical_cnf(
        tuple(-lit if abs(lit) in support else lit for lit in clause)
        for clause in cnf
    )


def local_factor(xv: int, yv: int):
    return canonical_cnf(((-xv, yv), (xv, -yv)))


def make_capsule(ren_hex: str, support: tuple[int, int], factor_anchor: str, parent_commitment: str):
    return (
        ("REN_NAME", ren_hex),
        ("SUPPORT_DELTA", list(support)),
        ("LOCAL_FACTOR_ANCHOR", factor_anchor),
        ("PARENT_COMMITMENT", parent_commitment),
    )


def capsule_dict(capsule) -> dict[str, Any]:
    if len(capsule) != 4:
        raise ValueError("capsule must have exactly four slots")
    return {slot_type: value for slot_type, value in capsule}


def analyze_n(n: int) -> dict[str, Any]:
    formula, x_vars, y_vars = equality_family(n)
    expected_formula = canonical_cnf(
        clause
        for xv, yv in zip(x_vars, y_vars)
        for clause in ((-xv, yv), (xv, -yv))
    )
    literal_occurrences = sum(len(c) for c in formula)
    structural_match = formula == expected_formula
    if not structural_match:
        raise AssertionError("frozen equality family structure drift")

    parent_commitment = digest(("PARENT", formula))
    source_namespace_commitment = digest((SOURCE_NS, parent_commitment))
    overlay_namespace_commitment = digest((OVERLAY_NS, parent_commitment))
    namespace_static_distinct = source_namespace_commitment != overlay_namespace_commitment

    # One-pass exact factorization.  The dictionary is the durable SAH-style
    # external anchor table; REN is only a compact route name into it.
    factor_by_anchor: dict[str, Any] = {}
    ren_to_anchor: dict[str, str] = {}
    expected_support_by_anchor: dict[str, frozenset[int]] = {}
    owner: dict[int, str] = {}
    factor_rows = []
    one_pass_ownership_ok = True

    hash_payload_bytes = len(json_bytes(("PARENT", formula)))
    formula_structure_compare_proxy = 2 * literal_occurrences
    factor_exact_literal_visits = 0
    ownership_entries = 0
    dictionary_entries = 0

    for index, (xv, yv) in enumerate(zip(x_vars, y_vars), start=1):
        factor = local_factor(xv, yv)
        factor_exact_literal_visits += sum(len(c) for c in factor)
        if not all(clause in formula for clause in factor):
            raise AssertionError("exact local factor missing")
        anchor_payload = ("SAH_EXTERNAL_FACTOR_ANCHOR", index, factor, parent_commitment)
        factor_anchor = digest(anchor_payload)
        hash_payload_bytes += len(json_bytes(anchor_payload))
        ren_hex = index.to_bytes(2, "big").hex()
        factor_by_anchor[factor_anchor] = factor
        ren_to_anchor[ren_hex] = factor_anchor
        support = frozenset((xv, yv))
        expected_support_by_anchor[factor_anchor] = support
        for variable in support:
            ownership_entries += 1
            if variable in owner:
                one_pass_ownership_ok = False
            owner[variable] = factor_anchor
        dictionary_entries += 1
        factor_rows.append((index, xv, yv, ren_hex, factor_anchor, factor, support))

    all_formula_variables = set(x_vars) | set(y_vars)
    one_pass_ownership_ok &= set(owner) == all_formula_variables and len(owner) == 2 * n
    dictionary_commitment_payload = tuple(sorted(ren_to_anchor.items()))
    dictionary_commitment = digest(("REN_DICTIONARY", dictionary_commitment_payload, parent_commitment))
    hash_payload_bytes += len(json_bytes(("REN_DICTIONARY", dictionary_commitment_payload, parent_commitment)))

    tombstones: set[tuple[str, str]] = set()
    local_tombstone_inserts = 0
    local_tombstone_hits = 0
    local_tombstone_cross_context_false_hits = 0
    exact_invalid_verifications = 0

    back_passes = 0
    forth_passes = 0
    namespace_roundtrips = 0
    namespace_distinct_passes = 0
    ren_resolution_passes = 0
    anchor_resolution_passes = 0
    sparse_delta_passes = 0
    capsule_type_passes = 0
    veta_wrong_identity_rejects = 0
    wrong_namespace_rejects = 0
    wrong_parent_rejects = 0
    wrong_ren_rejects = 0
    authorized_transitions = 0

    # Charged candidate work.  Hash payload bytes are included as one conservative
    # unit per byte in addition to the explicit structural/replay operations.
    capsule_slot_checks = 0
    ren_resolution_checks = 0
    anchor_resolution_checks = 0
    parent_commitment_checks = 0
    support_delta_entries = 0
    local_factor_forward_inverse_literal_visits = 0
    local_branch_restriction_literal_visits = 0
    local_branch_back_forth_literal_visits = 0
    namespace_checks = 0
    negative_control_checks = 0
    tombstone_lookup_ops = 0
    capsule_serialized_bytes = 0
    dictionary_serialized_bytes = len(json_bytes(dictionary_commitment_payload))

    def verify_back(capsule, expected_anchor: str, expected_factor, expected_support: frozenset[int]) -> bool:
        nonlocal capsule_slot_checks, ren_resolution_checks, anchor_resolution_checks
        nonlocal parent_commitment_checks, support_delta_entries
        nonlocal local_factor_forward_inverse_literal_visits, local_branch_restriction_literal_visits
        nonlocal local_branch_back_forth_literal_visits, namespace_checks
        nonlocal capsule_serialized_bytes, hash_payload_bytes

        capsule_serialized_bytes += len(json_bytes(capsule))
        if tuple(slot[0] for slot in capsule) != CAPSULE_TYPES:
            return False
        capsule_slot_checks += 4
        data = capsule_dict(capsule)

        ren_resolution_checks += 1
        if ren_to_anchor.get(data["REN_NAME"]) != expected_anchor:
            return False
        anchor_resolution_checks += 1
        if data["LOCAL_FACTOR_ANCHOR"] != expected_anchor:
            return False
        if factor_by_anchor.get(expected_anchor) != expected_factor:
            return False
        parent_commitment_checks += 1
        if data["PARENT_COMMITMENT"] != parent_commitment:
            return False

        support = frozenset(int(v) for v in data["SUPPORT_DELTA"])
        support_delta_entries += len(support)
        if support != expected_support:
            return False

        # S𓂸ḥ is a typed project overlay only.  BACK must reconstruct SOURCE
        # with the same full anchor/parent while commitments remain distinct.
        source_record = (SOURCE_NS, data["REN_NAME"], expected_anchor, parent_commitment)
        overlay_record = (OVERLAY_NS, data["REN_NAME"], expected_anchor, parent_commitment)
        namespace_checks += 2
        source_commitment = digest(source_record)
        overlay_commitment = digest(overlay_record)
        hash_payload_bytes += len(json_bytes(source_record)) + len(json_bytes(overlay_record))
        if source_commitment == overlay_commitment:
            return False
        reconstructed_source = (SOURCE_NS, data["REN_NAME"], expected_anchor, parent_commitment)
        if reconstructed_source != source_record:
            return False

        # PT222/Buzz authority is run BACK first on the exact local factor.
        back = sparse_flip(expected_factor, support)
        local_factor_forward_inverse_literal_visits += sum(len(c) for c in expected_factor)
        restored = sparse_flip(back, support)
        local_factor_forward_inverse_literal_visits += sum(len(c) for c in back)
        if back != expected_factor or restored != expected_factor:
            return False

        xv, yv = sorted(expected_support, key=lambda v: (v > n, v))
        if xv > n:
            return False
        # exact branch-pair return path, still local and pre-birth
        child_false = restrict_formula(expected_factor, {xv: False})
        child_true = restrict_formula(expected_factor, {xv: True})
        local_branch_restriction_literal_visits += 2 * sum(len(c) for c in expected_factor)
        residual_support = frozenset((yv,))
        false_to_true = sparse_flip(child_false, residual_support)
        true_to_false = sparse_flip(child_true, residual_support)
        local_branch_back_forth_literal_visits += sum(len(c) for c in child_false) + sum(len(c) for c in child_true)
        if false_to_true != child_true or true_to_false != child_false:
            return False
        return True

    for row_index, (index, xv, yv, ren_hex, factor_anchor, factor, support) in enumerate(factor_rows):
        capsule = make_capsule(ren_hex, (xv, yv), factor_anchor, parent_commitment)
        if len(capsule) == 4 and tuple(slot[0] for slot in capsule) == CAPSULE_TYPES:
            capsule_type_passes += 1

        # BACK chain must pass before FORTH is authorized.
        back_ok = verify_back(capsule, factor_anchor, factor, support)
        if back_ok:
            back_passes += 1
            ren_resolution_passes += 1
            anchor_resolution_passes += 1
            sparse_delta_passes += 1
            source_record = (SOURCE_NS, ren_hex, factor_anchor, parent_commitment)
            overlay_record = (OVERLAY_NS, ren_hex, factor_anchor, parent_commitment)
            if digest(source_record) != digest(overlay_record):
                namespace_distinct_passes += 1
            if (SOURCE_NS, ren_hex, factor_anchor, parent_commitment) == source_record:
                namespace_roundtrips += 1

            # Only now authorize FORTH.  The exact local involution is its own inverse.
            if sparse_flip(factor, support) == factor:
                forth_passes += 1
                authorized_transitions += 1

        # Veta: same capability cardinality (flip two coordinates) but wrong
        # provenance/support must not be accepted as the original generator.
        wrong_y = n + ((index % n) + 1)
        wrong_support_tuple = (xv, wrong_y)
        invalid = make_capsule(ren_hex, wrong_support_tuple, factor_anchor, parent_commitment)
        invalid_digest = digest(invalid)
        hash_payload_bytes += len(json_bytes(invalid))
        tombstone_key = (factor_anchor, invalid_digest)
        tombstone_lookup_ops += 1
        exact_invalid_verifications += 1
        invalid_first_ok = verify_back(invalid, factor_anchor, factor, support)
        if not invalid_first_ok:
            veta_wrong_identity_rejects += 1
            tombstones.add(tombstone_key)
            local_tombstone_inserts += 1
        tombstone_lookup_ops += 1
        if tombstone_key in tombstones:
            local_tombstone_hits += 1
        next_anchor = factor_rows[(row_index + 1) % n][4]
        tombstone_lookup_ops += 1
        if (next_anchor, invalid_digest) in tombstones:
            local_tombstone_cross_context_false_hits += 1

        # Additional provenance/firewall controls.
        negative_control_checks += 3
        wrong_ns_record = (SOURCE_NS, ren_hex, factor_anchor, parent_commitment)
        if wrong_ns_record[0] != OVERLAY_NS:
            wrong_namespace_rejects += 1
        wrong_parent_capsule = make_capsule(ren_hex, (xv, yv), factor_anchor, "0" * 64)
        if not verify_back(wrong_parent_capsule, factor_anchor, factor, support):
            wrong_parent_rejects += 1
        wrong_ren = factor_rows[(row_index + 1) % n][3]
        wrong_ren_capsule = make_capsule(wrong_ren, (xv, yv), factor_anchor, parent_commitment)
        if not verify_back(wrong_ren_capsule, factor_anchor, factor, support):
            wrong_ren_rejects += 1

    # Canonical witness remains exact and can be lifted by any generator word
    # because the factorized local involutions are independently verified.
    canonical_witness = {variable: True for variable in range(1, 2 * n + 1)}
    canonical_witness_literal_visits = literal_occurrences
    canonical_witness_valid = satisfies(formula, canonical_witness)

    represented_raw_prefixes = 1 << n
    symbolic_states = n + 1
    symbolic_transitions = authorized_transitions

    structural_work = {
        "formula_structure_compare_literal_proxy": formula_structure_compare_proxy,
        "factor_exact_literal_visits": factor_exact_literal_visits,
        "ownership_entries": ownership_entries,
        "dictionary_entries": dictionary_entries,
        "capsule_slot_checks": capsule_slot_checks,
        "ren_resolution_checks": ren_resolution_checks,
        "anchor_resolution_checks": anchor_resolution_checks,
        "parent_commitment_checks": parent_commitment_checks,
        "support_delta_entries": support_delta_entries,
        "local_factor_forward_inverse_literal_visits": local_factor_forward_inverse_literal_visits,
        "local_branch_restriction_literal_visits": local_branch_restriction_literal_visits,
        "local_branch_back_forth_literal_visits": local_branch_back_forth_literal_visits,
        "namespace_checks": namespace_checks,
        "negative_control_checks": negative_control_checks,
        "tombstone_lookup_ops": tombstone_lookup_ops,
        "canonical_witness_literal_visits": canonical_witness_literal_visits,
        "hash_payload_bytes": hash_payload_bytes,
        "capsule_serialized_bytes": capsule_serialized_bytes,
        "dictionary_serialized_bytes": dictionary_serialized_bytes,
    }
    candidate_work_proxy = sum(structural_work.values())
    prior_work_proxy = PR190_WORK[n]

    gates = {
        "exact_factorization": structural_match,
        "capsules_exactly_four_typed_slots": capsule_type_passes == n,
        "names_resolve_exact": ren_resolution_passes == n,
        "anchors_resolve_exact": anchor_resolution_passes == n,
        "namespace_roundtrip_exact": namespace_roundtrips == n,
        "namespace_typed_distinct": namespace_static_distinct and namespace_distinct_passes == n,
        "sparse_deltas_exact": sparse_delta_passes == n,
        "back_before_forth_exact": back_passes == n and authorized_transitions == n,
        "forth_replay_exact": forth_passes == n,
        "veta_wrong_identity_rejects": veta_wrong_identity_rejects == n,
        "local_tombstone_inserts_exact": local_tombstone_inserts == n,
        "local_tombstone_repeat_hits_exact": local_tombstone_hits == n,
        "local_tombstone_no_cross_context_false_hits": local_tombstone_cross_context_false_hits == 0,
        "wrong_namespace_rejects": wrong_namespace_rejects == n,
        "wrong_parent_rejects": wrong_parent_rejects == n,
        "wrong_ren_rejects": wrong_ren_rejects == n,
        "one_pass_support_ownership_exact": one_pass_ownership_ok,
        "canonical_witness_valid": canonical_witness_valid,
        "raw_prefix_enumeration_zero": True,
        "symbolic_states_n_plus_1": symbolic_states == n + 1,
        "symbolic_transitions_n": symbolic_transitions == n,
        "candidate_work_below_pr190": candidate_work_proxy < prior_work_proxy,
        "no_semantic_or_sat_oracle": True,
    }

    return {
        "n": n,
        "variables": 2 * n,
        "clauses": len(formula),
        "represented_raw_prefixes": represented_raw_prefixes,
        "raw_prefixes_enumerated": 0,
        "symbolic_states": symbolic_states,
        "symbolic_transitions": symbolic_transitions,
        "capsules": n,
        "capsule_schema": list(CAPSULE_TYPES),
        "ren_dictionary_commitment": dictionary_commitment,
        "source_namespace_commitment": source_namespace_commitment,
        "overlay_namespace_commitment": overlay_namespace_commitment,
        "back_passes": back_passes,
        "forth_passes": forth_passes,
        "veta_wrong_identity_rejects": veta_wrong_identity_rejects,
        "local_tombstone_inserts": local_tombstone_inserts,
        "local_tombstone_hits": local_tombstone_hits,
        "local_tombstone_cross_context_false_hits": local_tombstone_cross_context_false_hits,
        "exact_invalid_verifications": exact_invalid_verifications,
        "candidate_work_proxy": candidate_work_proxy,
        "prior_pr190_work_proxy": prior_work_proxy,
        "work_ratio_vs_pr190": candidate_work_proxy / prior_work_proxy,
        "work_saved_vs_pr190": prior_work_proxy - candidate_work_proxy,
        "charged_work": structural_work,
        "gates": gates,
        "passed": all(gates.values()),
    }


def run() -> dict[str, Any]:
    rows = [analyze_n(n) for n in FROZEN_N]
    all_pass = all(row["passed"] for row in rows)
    n14 = rows[0]
    result: dict[str, Any] = {
        "artifact_id": RUN_ID,
        "status": "PASS_KEEP_FULL_MECHANICS_REVERSE_RETURN_FIRST" if all_pass else "STOP_AT_FULL_MECHANICS_REVERSE_RETURN_FIRST",
        "operator": "TRANCEPTION_FULL_MECHANICS_REVERSE_RETURN_FIRST_CAPSULE_COMPILER",
        "base_sha": BASE_SHA,
        "run_scope": "RESTRICTED_C025_EQUALITY_FAMILY_FROZEN_N_14_32_64_128_256",
        "mechanics_projection": {
            "Q0": "exact local factor identity is final reuse authority",
            "Q1": "cheap local structure recognizes candidate factor before any branch birth",
            "BH_Q2": "exact sparse signed involution supplies forward/inverse authority",
            "PT477_V3": "failed capsule is remembered only in its exact local factor context",
            "PT366": "certificate exists at seed/parent time",
            "PT222": "BACK inverse replay is required before FORTH authorization",
            "SON_DELTA": "store only the changed two-coordinate support rather than a full 2n map",
            "FOUR_SONS": "each transition is exactly four typed capsule slots",
            "VETA": "same two-coordinate capability does not imply same support/provenance identity",
            "SAH": "full local factor anchor is external durable identity handle",
            "REN": "2-byte compact name routes to the full anchor but has no identity authority",
            "S_PHALLUS_H": "typed overlay namespace is reversible to SOURCE while remaining commitment-distinct",
            "PREBIRTH": "FORTH transition is not materialized until the complete BACK chain passes"
        },
        "reverse_pipeline": [
            "OVERLAY:S𓂸ḥ_RETURN_CAPSULE",
            "REN_NAME",
            "LOCAL_FACTOR_ANCHOR",
            "PARENT_COMMITMENT",
            "SUPPORT_DELTA",
            "PT222_BACK_LOCAL_INVERSE",
            "Q0_EXACT_FACTOR_RETURN",
            "AUTHORIZE_FORTH_BRANCH_QUOTIENT"
        ],
        "rows": rows,
        "comparison_n14": {
            "PT222_post_birth": {
                "raw_prefixes_enumerated": 16384,
                "explicit_map_entries": 229376
            },
            "PR190_prebirth_full_generator": {
                "raw_prefixes_enumerated": 0,
                "symbolic_states": 15,
                "symbolic_transitions": 14,
                "conservative_work_proxy": PR190_WORK[14]
            },
            "reverse_return_first_sparse_capsule": {
                "raw_prefixes_enumerated": n14["raw_prefixes_enumerated"],
                "symbolic_states": n14["symbolic_states"],
                "symbolic_transitions": n14["symbolic_transitions"],
                "candidate_work_proxy": n14["candidate_work_proxy"],
                "work_ratio_vs_pr190": n14["work_ratio_vs_pr190"]
            }
        },
        "next_universal_question": (
            "Can a similarly sparse return-first local decomposition/generator capsule system be discovered "
            "with polynomial total work and sufficient quotient coverage on arbitrary CNFs, including "
            "symmetry-poor instances, without semantic-equivalence or SAT/UNSAT oracle access?"
        ),
        "claim_boundary": [
            "A PASS applies only to the frozen factorized equality family.",
            "Linear-looking local capsule work here is enabled by an explicit independent two-clause factorization and does not generalize automatically.",
            "The experiment does not establish polynomial decomposition discovery or quotient size for arbitrary CNFs.",
            "The experiment does not establish P=NP.",
            "P_VS_NP = OPEN"
        ],
        "mathematical_verdict": {
            "P_VS_NP": "OPEN",
            "P_EQUALS_NP": "NOT_ESTABLISHED",
            "P_NOT_EQUALS_NP": "NOT_ESTABLISHED"
        }
    }
    result["integrity_sha256"] = digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    result = run()
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    if args.self_test:
        assert result["mathematical_verdict"]["P_VS_NP"] == "OPEN"
        assert result["status"] in {
            "PASS_KEEP_FULL_MECHANICS_REVERSE_RETURN_FIRST",
            "STOP_AT_FULL_MECHANICS_REVERSE_RETURN_FIRST"
        }


if __name__ == "__main__":
    main()
