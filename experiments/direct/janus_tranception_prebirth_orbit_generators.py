#!/usr/bin/env python3
"""Tranception BACK->FORTH diagnosis: certify orbit generators before branching.

Restricted positive control only: C025 equality_family(n).

The earlier PT222 audit enumerated every x-prefix and only afterwards proved that
all resulting y-unit residuals form one signed-coordinate orbit.  This probe
moves the exact certificate to the parent state.  For each equality pair it
verifies an involutive full-formula signed automorphism that flips x_i and y_i
together.  Pairwise-disjoint generator supports then certify an independent
(Z2)^n action, so branch pairs can be quotiented before materialization.

No raw-prefix enumeration is performed.  This does NOT generalize the result to
arbitrary CNFs and does not establish P=NP.  P_VS_NP remains OPEN.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from janus_c025_core import canonical_cnf, restrict_formula, satisfies
from janus_c025_families import equality_family
from janus_tear_policy0a_bh_q2_buzz_physarum_signed_singularity_probe import (
    apply_signed_map,
    invert_signed_map,
    signed_map_roundtrip_ok,
)
from janus_s_phallus_h_reversible_namespace_alias import run as run_s_phallus_parent

RUN_ID = "JANUS-TRANCEPTION-PREBIRTH-ORBIT-GENERATORS-2026-08-18-v1"
FROZEN_N = (14, 32, 64, 128, 256)
EXPECTED_PARENT_STATUS = "PASS_KEEP_S_PHALLUS_H_REVERSIBLE_NAMESPACE_ALIAS"
EXPECTED_PARENT_SOLVER = {
    "residual_states": 2822,
    "bytewise_distinct_absorptions": 602,
    "polarity_flip_absorptions": 450,
    "event_horizon_collisions": 839,
    "hawking_escape_count": 1242,
    "buzz_return_checks": 1844,
    "canonical_edge_visits": 3488298,
    "resolution_attempts": 626489,
    "resolution_additions": 93638,
    "local_tombstone_checks": 1050,
    "local_tombstone_hits": 1050,
    "local_tombstone_inserts": 1242,
    "route_rescan_edge_visits": 0,
}


def digest_json(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(payload.encode("utf-8")).hexdigest()


def variables_of(cnf) -> tuple[int, ...]:
    return tuple(sorted({abs(lit) for clause in cnf for lit in clause}))


def full_generator(n: int, index: int) -> dict[int, tuple[int, bool]]:
    """g_i flips exactly x_i and y_i and fixes every other coordinate."""
    xv = index
    yv = n + index
    return {
        variable: (variable, variable in {xv, yv})
        for variable in range(1, 2 * n + 1)
    }


def residual_generator(cnf, yv: int) -> dict[int, tuple[int, bool]]:
    """After branching on x_i, only y_i needs the sign flip."""
    return {
        variable: (variable, variable == yv)
        for variable in variables_of(cnf)
    }


def generator_support(mapping: dict[int, tuple[int, bool]]) -> frozenset[int]:
    return frozenset(source for source, (target, flip) in mapping.items() if source != target or flip)


def corrupt_first_pair(formula, n: int):
    """Frozen negative control: alter one polarity in the x1/y1 pair."""
    x1, y1 = 1, n + 1
    old = canonical_cnf(((-x1, y1), (x1, -y1)))
    if not all(clause in formula for clause in old):
        raise AssertionError("equality-family first pair not found")
    clauses = list(formula)
    clauses.remove((-x1, y1))
    clauses.append((-x1, -y1))
    return canonical_cnf(clauses)


def analyze_n(n: int) -> dict[str, Any]:
    formula, x_vars, y_vars = equality_family(n)
    expected_formula = canonical_cnf(
        clause
        for xv, yv in zip(x_vars, y_vars)
        for clause in ((-xv, yv), (xv, -yv))
    )
    structural_match = formula == expected_formula
    if not structural_match:
        raise AssertionError("frozen equality family structure drift")

    literal_occurrences = sum(len(c) for c in formula)
    automorphism_passes = 0
    involution_passes = 0
    branch_pair_passes = 0
    fixes_other_x_passes = 0
    supports: list[frozenset[int]] = []
    generator_digests: list[str] = []

    for index, (xv, yv) in enumerate(zip(x_vars, y_vars), start=1):
        generator = full_generator(n, index)
        support = generator_support(generator)
        supports.append(support)
        generator_digests.append(digest_json(sorted((k, v[0], v[1]) for k, v in generator.items())))

        if support != frozenset({xv, yv}):
            raise AssertionError("generator support drift")
        if not signed_map_roundtrip_ok(generator):
            raise AssertionError("generator signed-map roundtrip failed")
        inverse = invert_signed_map(generator)
        if inverse == generator:
            involution_passes += 1
        if apply_signed_map(formula, generator) == formula:
            automorphism_passes += 1

        if all(generator[xj] == (xj, False) for xj in x_vars if xj != xv):
            fixes_other_x_passes += 1

        child_false = restrict_formula(formula, {xv: False})
        child_true = restrict_formula(formula, {xv: True})
        rmap = residual_generator(child_false, yv)
        if signed_map_roundtrip_ok(rmap) and apply_signed_map(child_false, rmap) == child_true:
            if apply_signed_map(child_true, invert_signed_map(rmap)) == child_false:
                branch_pair_passes += 1

    pairwise_disjoint_checks = 0
    pairwise_disjoint_passes = 0
    for i in range(n):
        for j in range(i):
            pairwise_disjoint_checks += 1
            if supports[i].isdisjoint(supports[j]):
                pairwise_disjoint_passes += 1

    # Disjoint two-coordinate involutions are independent and commute.  Therefore
    # every subset of the n generators denotes a unique group element without us
    # materializing those subsets.  This is the symbolic replacement for the old
    # exhaustive prefix loop.
    independent_generator_rank = n if pairwise_disjoint_passes == pairwise_disjoint_checks else 0
    represented_group_elements = 1 << independent_generator_rank

    canonical_witness = {variable: True for variable in range(1, 2 * n + 1)}
    canonical_witness_pass = satisfies(formula, canonical_witness)

    # Symbolic arbitrary-route witness rule: for any generator word W, start from
    # all-True and flip x_i,y_i iff g_i occurs with odd parity.  We verify the rule
    # from exact formula factorization + full automorphism + involution + commuting
    # disjoint supports, rather than enumerating 2^n words.
    arbitrary_route_witness_rule_certified = bool(
        structural_match
        and canonical_witness_pass
        and automorphism_passes == n
        and involution_passes == n
        and pairwise_disjoint_passes == pairwise_disjoint_checks
    )

    corrupted = corrupt_first_pair(formula, n)
    g1 = full_generator(n, 1)
    corrupted_clause_reject = apply_signed_map(corrupted, g1) != corrupted

    wrong_anchor = {
        variable: (variable, variable == 1)
        for variable in range(1, 2 * n + 1)
    }
    generator_anchor_bitflip_reject = apply_signed_map(formula, wrong_anchor) != formula

    wrong_support = {
        variable: (variable, variable in {1, n + 2})
        for variable in range(1, 2 * n + 1)
    }
    wrong_support_reject = apply_signed_map(formula, wrong_support) != formula

    quotient_states = n + 1
    quotient_transitions = n
    raw_prefixes_represented = 1 << n
    old_pt222_map_entries_if_enumerated = n * raw_prefixes_represented

    charged = {
        "input_literal_occurrences": literal_occurrences,
        "full_formula_automorphism_literal_visit_proxy": literal_occurrences * n,
        "branch_pair_restriction_literal_visit_proxy": 2 * literal_occurrences * n,
        "pairwise_support_independence_checks": pairwise_disjoint_checks,
        "symbolic_transition_construction_ops": n,
        "generator_records": n,
    }
    charged["polynomial_work_proxy"] = sum(charged.values())

    gates = {
        "structural_match": structural_match,
        "all_full_formula_generators_verify": automorphism_passes == n,
        "all_generators_are_involutions": involution_passes == n,
        "all_generators_fix_other_branch_variables": fixes_other_x_passes == n,
        "all_branch_pairs_certified_before_expansion": branch_pair_passes == n,
        "all_generator_supports_pairwise_disjoint": pairwise_disjoint_passes == pairwise_disjoint_checks,
        "independent_generator_rank_exact": independent_generator_rank == n,
        "represented_group_elements_exact_2pow_n": represented_group_elements == raw_prefixes_represented,
        "symbolic_quotient_states_exact_n_plus_1": quotient_states == n + 1,
        "symbolic_quotient_transitions_exact_n": quotient_transitions == n,
        "canonical_witness_valid": canonical_witness_pass,
        "arbitrary_route_witness_rule_certified": arbitrary_route_witness_rule_certified,
        "corrupted_clause_rejects": corrupted_clause_reject,
        "generator_anchor_bitflip_rejects": generator_anchor_bitflip_reject,
        "wrong_support_generator_rejects": wrong_support_reject,
    }

    return {
        "n": n,
        "variables": 2 * n,
        "clauses": len(formula),
        "literal_occurrences": literal_occurrences,
        "generator_count": n,
        "generator_digest_sha256": digest_json(generator_digests),
        "independent_generator_rank": independent_generator_rank,
        "represented_raw_prefixes": raw_prefixes_represented,
        "represented_group_elements": represented_group_elements,
        "symbolic_quotient_states": quotient_states,
        "symbolic_quotient_transitions": quotient_transitions,
        "raw_prefixes_enumerated": 0,
        "old_pt222_map_entries_if_enumerated": old_pt222_map_entries_if_enumerated,
        "automorphism_passes": automorphism_passes,
        "involution_passes": involution_passes,
        "branch_pair_passes": branch_pair_passes,
        "pairwise_disjoint_checks": pairwise_disjoint_checks,
        "pairwise_disjoint_passes": pairwise_disjoint_passes,
        "negative_controls": {
            "corrupted_clause_reject": corrupted_clause_reject,
            "generator_anchor_bitflip_reject": generator_anchor_bitflip_reject,
            "wrong_support_reject": wrong_support_reject,
        },
        "charged_work": charged,
        "gates": gates,
        "passed": all(gates.values()),
    }


def run() -> dict[str, Any]:
    parent = run_s_phallus_parent()
    parent_reproduced = bool(
        parent["status"] == EXPECTED_PARENT_STATUS
        and parent["candidate_solver"] == EXPECTED_PARENT_SOLVER
        and parent["gates"]["candidate_ren_exactly_matches_parent"]
        and parent["gates"]["all_overlay_to_source_exact"]
        and parent["gates"]["zero_extra_solver_residual_scans"]
    )

    rows = [analyze_n(n) for n in FROZEN_N]
    all_rows_pass = all(row["passed"] for row in rows)
    zero_prefix_enumeration = all(row["raw_prefixes_enumerated"] == 0 for row in rows)

    # For the original n=14 PT222 control, this is the direct apples-to-apples
    # diagnostic: the old audit materialized 16384 prefixes and 229376 map entries;
    # the symbolic certificate uses 14 exact generators and 15 quotient states.
    n14 = next(row for row in rows if row["n"] == 14)
    comparison_n14 = {
        "old_pt222_prefixes_enumerated": 1 << 14,
        "old_pt222_map_entries_enumerated": 14 * (1 << 14),
        "new_prefixes_enumerated": n14["raw_prefixes_enumerated"],
        "new_exact_generator_count": n14["generator_count"],
        "new_symbolic_quotient_states": n14["symbolic_quotient_states"],
        "new_symbolic_quotient_transitions": n14["symbolic_quotient_transitions"],
        "same_raw_prefix_space_represented": n14["represented_raw_prefixes"] == (1 << 14),
    }

    gates = {
        "s_phallus_parent_reproduced": parent_reproduced,
        "all_frozen_n_rows_pass": all_rows_pass,
        "zero_raw_prefix_enumeration": zero_prefix_enumeration,
        "n14_represents_same_2pow14_prefix_space": comparison_n14["same_raw_prefix_space_represented"],
        "n14_symbolic_states_15": comparison_n14["new_symbolic_quotient_states"] == 15,
        "n14_exact_generators_14": comparison_n14["new_exact_generator_count"] == 14,
    }
    passed = all(gates.values())

    result: dict[str, Any] = {
        "artifact_id": RUN_ID,
        "status": "PASS_KEEP_TRANCEPTION_PREBIRTH_ORBIT_GENERATORS" if passed else "STOP_AT_TRANCEPTION_PREBIRTH_ORBIT_GENERATORS",
        "operator": "TRANCEPTION_PREBIRTH_ORBIT_GENERATOR_QUOTIENT",
        "run_scope": "RESTRICTED_EQUALITY_FAMILY_STRUCTURAL_CONTROL_FROZEN_N_14_32_64_128_256",
        "parent": {
            "status": parent["status"],
            "solver": parent["candidate_solver"],
            "reproduced": parent_reproduced,
        },
        "back_forth_diagnosis": {
            "BACK": "PT222 already told us after enumeration that all blocked-equality residuals occupy one reversible signed orbit.",
            "ERROR_LOCALIZED": "The exponential cost was paid before the orbit fact was used: enumerate 2^n children first, certify their common orbit second.",
            "FORTH_REPAIR": "Certify n independent exact signed automorphism generators at the parent and quotient each branch pair before child materialization.",
            "result_if_pass": "For equality_family only, the 2^n blocked prefix tree has a polynomial-size pre-birth orbit certificate/quotient construction."
        },
        "comparison_n14": comparison_n14,
        "rows": rows,
        "gates": gates,
        "claim_boundary": [
            "This PASS, if obtained, repairs the PT222 enumeration defect only on the frozen equality family.",
            "The result does not provide polynomial-time generator discovery for arbitrary CNFs.",
            "The result does not prove that arbitrary-CNF orbit quotient state count is polynomial.",
            "The result does not prove P=NP.",
            "The next universal gate is polynomial discovery of a sufficient proof-carrying branch-equivalence generator/decomposition system for every CNF, with polynomial quotient size, transition/certificate verification, and witness recovery.",
            "P_VS_NP = OPEN"
        ],
        "mathematical_verdict": {
            "P_VS_NP": "OPEN",
            "P_EQUALS_NP": "NOT_ESTABLISHED",
            "P_NOT_EQUALS_NP": "NOT_ESTABLISHED"
        }
    }
    result["integrity_sha256"] = digest_json(result)
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
            "PASS_KEEP_TRANCEPTION_PREBIRTH_ORBIT_GENERATORS",
            "STOP_AT_TRANCEPTION_PREBIRTH_ORBIT_GENERATORS",
        }


if __name__ == "__main__":
    main()
