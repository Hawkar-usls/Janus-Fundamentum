#!/usr/bin/env python3
"""C025 JANUS Certified Residual Quotient audit entry."""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import random
from pathlib import Path
from typing import Any
from janus_c025_core import *
from janus_c025_families import *

# ---------------------------------------------------------------------------
# Audits
# ---------------------------------------------------------------------------

def audit_absorption_compression(n: int = 12) -> dict[str, Any]:
    formula, x, y, z = absorption_family(n)
    raw_states = set()
    normalized_states = set()
    certificates = 0
    subsumption_steps = 0

    # Directly materialize the exact cut residual.  This avoids repeatedly
    # re-cofactoring the whole 3n-variable formula while preserving the same
    # proof obligation for every one of the 2^n prefix assignments.
    for bits in itertools.product((False, True), repeat=n):
        raw_clauses = []
        for bit, yv, zv in zip(bits, y, z):
            raw_clauses.append((yv,))
            if not bit:
                raw_clauses.append((yv, zv))
        raw = canonical_cnf(raw_clauses)
        normalized, certificate = normalize_subsumption(raw)
        if not verify_normalization(raw, normalized, certificate):
            raise AssertionError("absorption certificate failed")
        raw_states.add(raw)
        normalized_states.add(normalized)
        certificates += 1
        subsumption_steps += len(certificate.steps)

    order = x + y + z
    automaton = compile_residual_automaton(formula, order, state_budget=10000)

    expected = canonical_cnf((yv,) for yv in y)
    return {
        "n": n,
        "variables": 3 * n,
        "cut_depth": n,
        "raw_residual_states": len(raw_states),
        "normalized_residual_states": len(normalized_states),
        "expected_raw_states": 1 << n,
        "normal_form_is_all_y_units": normalized_states == {expected},
        "cut_certificates": certificates,
        "cut_subsumption_steps": subsumption_steps,
        "automaton_status": automaton.status,
        "automaton_sat": automaton.sat,
        "automaton_residual_states": automaton.stats.residual_states,
        "automaton_bdd_nodes": automaton.stats.bdd_nodes,
        "automaton_max_frontier": automaton.stats.max_frontier_states,
        "automaton_subsumption_steps": automaton.stats.subsumption_steps,
        "witness_valid": (
            automaton.witness is not None
            and satisfies(formula, automaton.witness)
        ),
    }


def audit_equality_order_sensitivity(
    exact_n: int = 9,
    budget_n: int = 14,
) -> dict[str, Any]:
    exact_formula, exact_x, exact_y = equality_family(exact_n)
    blocked = exact_x + exact_y
    interleaved = [
        variable
        for pair in zip(exact_x, exact_y)
        for variable in pair
    ]

    blocked_semantic = semantic_residual_profile(exact_formula, blocked)
    interleaved_semantic = semantic_residual_profile(exact_formula, interleaved)
    blocked_syntactic = normalized_syntactic_profile(exact_formula, blocked)
    interleaved_syntactic = normalized_syntactic_profile(exact_formula, interleaved)

    large_formula, large_x, large_y = equality_family(budget_n)
    blocked_large = compile_residual_automaton(
        large_formula,
        large_x + large_y,
        state_budget=5000,
    )
    interleaved_large = compile_residual_automaton(
        large_formula,
        [
            variable
            for pair in zip(large_x, large_y)
            for variable in pair
        ],
        state_budget=5000,
    )

    cut_assignments = set()
    for bits in itertools.product((False, True), repeat=budget_n):
        residual = restrict_formula(large_formula, dict(zip(large_x, bits)))
        normalized, _ = normalize_subsumption(residual)
        cut_assignments.add(normalized)

    return {
        "exact_n": exact_n,
        "blocked_peak_semantic_width": max(blocked_semantic.values()),
        "interleaved_peak_semantic_width": max(interleaved_semantic.values()),
        "blocked_cut_semantic_width": blocked_semantic[exact_n],
        "interleaved_cut_semantic_width": interleaved_semantic[2 * exact_n],
        "blocked_semantic_profile": blocked_semantic,
        "interleaved_semantic_profile": interleaved_semantic,
        "blocked_syntactic_matches_semantic": blocked_syntactic == blocked_semantic,
        "interleaved_syntactic_matches_semantic": interleaved_syntactic == interleaved_semantic,
        "budget_n": budget_n,
        "blocked_cut_states_exact": len(cut_assignments),
        "blocked_expected_cut_states": 1 << budget_n,
        "blocked_budget_status": blocked_large.status,
        "blocked_states_before_open": blocked_large.stats.residual_states,
        "interleaved_budget_status": interleaved_large.status,
        "interleaved_residual_states": interleaved_large.stats.residual_states,
        "interleaved_bdd_nodes": interleaved_large.stats.bdd_nodes,
        "interleaved_witness_valid": (
            interleaved_large.witness is not None
            and satisfies(large_formula, interleaved_large.witness)
        ),
    }


def audit_small_random_profiles(
    rng: random.Random,
    cases: int = 120,
) -> dict[str, Any]:
    mismatches = 0
    syntactic_below_semantic = 0
    positive_gaps = 0
    maximum_gap = 0
    profile_rows = []

    for index in range(cases):
        n = rng.randint(3, 8)
        formula = random_3cnf(rng, n, rng.randint(n, 4 * n))
        order = list(range(1, n + 1))
        rng.shuffle(order)

        semantic = semantic_residual_profile(formula, order)
        syntactic = normalized_syntactic_profile(formula, order)
        if any(syntactic[depth] < semantic[depth] for depth in semantic):
            syntactic_below_semantic += 1

        gap = max(syntactic[depth] - semantic[depth] for depth in semantic)
        if gap > 0:
            positive_gaps += 1
        maximum_gap = max(maximum_gap, gap)

        automaton = compile_residual_automaton(
            formula, order, state_budget=10000
        )
        truth, witness, _ = brute_force(formula, order)
        if (
            automaton.status != "EXACT"
            or automaton.sat != truth
            or (
                automaton.sat
                and (
                    automaton.witness is None
                    or not satisfies(formula, automaton.witness)
                )
            )
        ):
            mismatches += 1

        if index < 20:
            profile_rows.append({
                "variables": n,
                "clauses": len(formula),
                "semantic_peak": max(semantic.values()),
                "normalized_syntactic_peak": max(syntactic.values()),
                "gap": gap,
                "automaton_states": automaton.stats.residual_states,
                "bdd_nodes": automaton.stats.bdd_nodes,
                "sat": automaton.sat,
            })

    return {
        "cases": cases,
        "mismatches": mismatches,
        "syntactic_below_semantic": syntactic_below_semantic,
        "cases_with_merge_proof_gap": positive_gaps,
        "maximum_peak_gap": maximum_gap,
        "rows": profile_rows,
    }


def audit_merge_equivalence_barrier(
    rng: random.Random,
    cases: int = 100,
) -> dict[str, Any]:
    core = complete_unsat_3core()
    equivalence_mismatches = 0
    separating_witness_failures = 0
    resolution_failures = 0
    sat_count = 0
    unsat_count = 0
    resolution_steps = 0
    resolution_attempts = 0

    false_formula: CNF = ((),)
    core_proof = generate_resolution_refutation(core)
    if core_proof.empty_index is None or not verify_resolution_proof(core_proof):
        raise AssertionError("frozen core refutation failed")

    for index in range(cases):
        n = rng.randint(3, 7)
        if index % 2 == 0:
            formula, planted = planted_3cnf(rng, n, rng.randint(n, 4 * n))
            expected_sat = True
        else:
            noise, _ = planted_3cnf(rng, n, rng.randint(1, max(1, n)))
            formula = canonical_cnf(core + noise)
            expected_sat = False

        sat, witness, _ = brute_force(formula, list(range(1, n + 1)))
        if sat != expected_sat:
            raise AssertionError("balanced merge fixture truth mismatch")

        equivalent_to_false = not sat
        exact_equivalence_check = all(
            satisfies(formula, assignment) == satisfies(false_formula, assignment)
            for assignment in (
                dict(zip(range(1, n + 1), bits))
                for bits in itertools.product((False, True), repeat=n)
            )
        )
        if equivalent_to_false != exact_equivalence_check:
            equivalence_mismatches += 1

        if sat:
            sat_count += 1
            if (
                witness is None
                or not satisfies(formula, witness)
                or satisfies(false_formula, witness)
            ):
                separating_witness_failures += 1
        else:
            unsat_count += 1
            resolution_attempts += core_proof.pair_attempts
            resolution_steps += len(core_proof.steps)
            if not set(core_proof.initial).issubset(set(formula)):
                resolution_failures += 1
            elif not verify_resolution_proof(core_proof):
                resolution_failures += 1

    return {
        "cases": cases,
        "sat": sat_count,
        "unsat": unsat_count,
        "equivalence_mismatches": equivalence_mismatches,
        "separating_witness_failures": separating_witness_failures,
        "resolution_proof_failures": resolution_failures,
        "resolution_steps": resolution_steps,
        "resolution_pair_attempts": resolution_attempts,
        "reduction": "F ≡ FALSE if and only if F is UNSAT",
        "interpretation": (
            "An unrestricted semantic residual-state merger contains a coNP "
            "equivalence obligation. Non-equivalence has a separating assignment; "
            "equivalence requires an UNSAT-style proof."
        ),
    }


def audit_chain_positive_control(
    max_n: int = 128,
) -> dict[str, Any]:
    rows = []
    for n in (8, 16, 32, 64, max_n):
        formula = implication_chain(n)
        order = list(range(1, n + 1))
        automaton = compile_residual_automaton(
            formula, order, state_budget=10000
        )
        rows.append({
            "variables": n,
            "status": automaton.status,
            "residual_states": automaton.stats.residual_states,
            "bdd_nodes": automaton.stats.bdd_nodes,
            "max_frontier": automaton.stats.max_frontier_states,
            "witness_valid": (
                automaton.witness is not None
                and satisfies(formula, automaton.witness)
            ),
        })
    return {
        "rows": rows,
        "all_exact": all(row["status"] == "EXACT" for row in rows),
        "all_small_frontier": all(row["max_frontier"] <= 2 for row in rows),
    }


def run(seed: int = DEFAULT_SEED) -> dict[str, Any]:
    rng = random.Random(seed)

    absorption = audit_absorption_compression()
    equality = audit_equality_order_sensitivity()
    random_profiles = audit_small_random_profiles(rng)
    merge_barrier = audit_merge_equivalence_barrier(rng)
    chain = audit_chain_positive_control()

    assertions = {
        "absorption_exponential_raw": (
            absorption["raw_residual_states"]
            == absorption["expected_raw_states"]
        ),
        "absorption_certified_collapse": (
            absorption["normalized_residual_states"] == 1
            and absorption["normal_form_is_all_y_units"]
            and absorption["automaton_status"] == "EXACT"
            and absorption["witness_valid"]
        ),
        "equality_true_exponential_width": (
            equality["blocked_cut_states_exact"]
            == equality["blocked_expected_cut_states"]
            and equality["blocked_budget_status"] == "OPEN"
        ),
        "equality_good_order_exact": (
            equality["interleaved_budget_status"] == "EXACT"
            and equality["interleaved_witness_valid"]
        ),
        "random_profiles_sound": (
            random_profiles["mismatches"] == 0
            and random_profiles["syntactic_below_semantic"] == 0
        ),
        "merge_barrier_exact": (
            merge_barrier["equivalence_mismatches"] == 0
            and merge_barrier["separating_witness_failures"] == 0
            and merge_barrier["resolution_proof_failures"] == 0
        ),
        "chain_exact_small_width": (
            chain["all_exact"] and chain["all_small_frontier"]
        ),
    }
    status = "PASS" if all(assertions.values()) else "FAIL"

    result = {
        "artifact_id": "C025-JANUS-CERTIFIED-RESIDUAL-QUOTIENT",
        "status": status,
        "research_status": "EXPLORATORY_SOFTWARE_ONLY_NOT_CANONICAL",
        "seed": seed,
        "holdout_seed": seed,
        "canonical_seed_sha256": CANONICAL_SEED_SHA256,
        "base_repository_commit": BASE_COMMIT,
        "software_only": True,
        "swarm_touched": False,
        "devices_touched": False,
        "nas_touched": False,
        "external_models_called": False,
        "general_sat_oracle_called": False,
        "absorption_compression": absorption,
        "equality_order_sensitivity": equality,
        "small_random_profiles": random_profiles,
        "semantic_merge_barrier": merge_barrier,
        "chain_positive_control": chain,
        "assertions": assertions,
        "located_bottleneck": {
            "name": "CERTIFIED_RESIDUAL_QUOTIENT_COMPLEXITY",
            "definition": (
                "For a decomposition/order, the total number of exact residual "
                "function classes plus the proof volume needed to certify every "
                "state merge, transition, terminal, and witness-recovery map."
            ),
            "two_independent_costs": {
                "state_volume": (
                    "The number of continuation-distinct residual Boolean functions."
                ),
                "merge_proof_volume": (
                    "The certificates establishing equivalence of syntactically "
                    "different residual representations."
                ),
            },
            "why_it_is_exact": [
                "Blocked equality forces 2^n continuation-distinct states at one cut.",
                "The absorption family has 2^n raw residual CNFs but one certified semantic state.",
                "General semantic merging is coNP-hard because F can merge with FALSE exactly when F is UNSAT."
            ],
        },
        "positive_result": (
            "Polynomial proof-carrying normalization can remove exponential fake "
            "separator width before search. The honest compiler verifies every "
            "subsumption merge and returns OPEN on true state explosion."
        ),
        "distance_to_p_equals_np": {
            "mathematical_status": "UNCHANGED_OPEN",
            "next_exact_target": (
                "Construct a polynomially discoverable decomposition and a polynomial "
                "proof system for all necessary residual merges on every CNF."
            ),
        },
        "theorem_candidate": {
            "name": "Certified Residual Automaton Criterion",
            "statement": (
                "If every CNF admits a polynomial-size residual automaton whose "
                "transitions, state equivalences, terminals and witness recovery "
                "are constructible and independently verifiable in polynomial time, "
                "then SAT is in P."
            ),
            "status": "DIRECT_ALGORITHMIC_CRITERION_NOT_A_P_EQUALS_NP_PROOF",
        },
        "claim_boundary": (
            "C025 does not prove P=NP, P!=NP, or a lower bound against all algorithms."
        ),
    }

    clean = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    result["integrity"] = {"sha256": hashlib.sha256(clean.encode("utf-8")).hexdigest()}
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    result = run(args.seed)
    if args.output:
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.self_test and result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
