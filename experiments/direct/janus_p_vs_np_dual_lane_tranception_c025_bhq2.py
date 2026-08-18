#!/usr/bin/env python3
"""JANUS dual-lane P-vs-NP run over frozen/revealed controls.

This run deliberately cannot output P=NP or P!=NP from finite evidence.
It combines:
  * restored C025 certified residual quotient controls;
  * BH-Q2 proof-carrying signed coordinate maps;
  * a blocked-equality signed-orbit probe;
  * Tranception-style forward/reverse witness replay.

Forward asks whether a compact certified route can be built.
Reverse asks whether every absorbed state can return with its proof/witness map.
No return path => no absorption. No universal construction/lower bound => OPEN.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from janus_certified_residual_quotient import run as run_c025
from janus_c025_core import normalize_subsumption, restrict_formula, satisfies
from janus_c025_families import equality_family
from janus_tear_policy0a_bh_q2_buzz_physarum_signed_singularity_probe import (
    apply_signed_map,
    invert_signed_map,
    signed_map_roundtrip_ok,
)
from janus_tear_policy0a_masked_tseitin import canonical_cnf as bh_canonical_cnf


RUN_ID = "JANUS-P-VS-NP-DUAL-LANE-TRANCEPTION-C025-BHQ2-v1"


def digest_json(obj: object) -> str:
    payload = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def lift_assignment_from_canonical(
    mapping: dict[int, tuple[int, bool]],
    canonical_assignment: dict[int, bool],
) -> dict[int, bool]:
    """Lift a canonical witness back through x_src -> (+/-)x_dst."""
    return {
        source: bool(canonical_assignment[target]) ^ bool(flip)
        for source, (target, flip) in mapping.items()
    }


def audit_blocked_equality_signed_orbit(n: int = 14) -> dict[str, Any]:
    """Attack C025 blocked-equality width with an explicit signed orbit.

    At the C025 blocked cut all x variables are assigned and every residual is
    exactly n unit clauses over y. Those 2^n fixed-coordinate Boolean functions
    are distinct, but for SAT decision they form one signed-coordinate orbit.

    We do NOT call them semantically equal. Each absorption carries a bijective
    polarity map and is accepted only after exact forward, inverse and full
    witness replay. The enumerated total map volume is charged explicitly.
    """
    formula, x_vars, y_vars = equality_family(n)
    expected = bh_canonical_cnf((index,) for index in range(1, n + 1))
    canonical_witness = {index: True for index in range(1, n + 1)}

    raw_states = set()
    orbit_states = set()
    forward_passes = 0
    inverse_passes = 0
    residual_witness_passes = 0
    full_witness_passes = 0
    normalization_passes = 0
    total_map_entries = 0
    polarity_flips = 0

    for bits in itertools.product((False, True), repeat=n):
        prefix = dict(zip(x_vars, bits))
        raw = restrict_formula(formula, prefix)
        normalized, certificate = normalize_subsumption(raw)
        # The certificate is part of the C025 proof-carrying input layer.
        # For this cut, normalization should preserve a unit-only residual.
        if certificate is not None:
            normalization_passes += 1

        signs: dict[int, bool] = {}
        for clause in normalized:
            if len(clause) != 1:
                raise AssertionError("blocked equality cut is not unit-only")
            literal = clause[0]
            variable = abs(literal)
            if variable in signs:
                raise AssertionError("duplicate equality unit variable")
            signs[variable] = literal < 0

        if set(signs) != set(y_vars):
            raise AssertionError("blocked equality cut lost a y variable")

        mapping = {
            old_variable: (canonical_variable, bool(signs[old_variable]))
            for canonical_variable, old_variable in enumerate(sorted(y_vars), start=1)
        }
        total_map_entries += len(mapping)
        polarity_flips += sum(int(flip) for _, flip in mapping.values())

        if not signed_map_roundtrip_ok(mapping):
            raise AssertionError("Buzz literal round-trip failed")

        canonical = apply_signed_map(normalized, mapping)
        if canonical != expected:
            raise AssertionError("signed orbit failed to reach singularity representative")
        forward_passes += 1

        inverse = invert_signed_map(mapping)
        restored = apply_signed_map(canonical, inverse)
        if restored != normalized:
            raise AssertionError("Buzz inverse did not restore residual")
        inverse_passes += 1

        lifted = lift_assignment_from_canonical(mapping, canonical_witness)
        if not satisfies(normalized, lifted):
            raise AssertionError("lifted residual witness invalid")
        residual_witness_passes += 1

        full_assignment = dict(prefix)
        full_assignment.update(lifted)
        if not satisfies(formula, full_assignment):
            raise AssertionError("reverse witness failed original equality formula")
        full_witness_passes += 1

        raw_states.add(normalized)
        orbit_states.add(canonical)

    expected_raw = 1 << n
    return {
        "family": "BLOCKED_EQUALITY",
        "n": n,
        "prefix_assignments": expected_raw,
        "raw_fixed_coordinate_states": len(raw_states),
        "expected_raw_fixed_coordinate_states": expected_raw,
        "signed_orbit_singularities": len(orbit_states),
        "forward_map_passes": forward_passes,
        "inverse_map_passes": inverse_passes,
        "residual_witness_passes": residual_witness_passes,
        "full_formula_witness_passes": full_witness_passes,
        "normalization_certificates_seen": normalization_passes,
        "per_residual_map_entries": n,
        "enumerated_total_map_entries": total_map_entries,
        "polarity_flips_total": polarity_flips,
        "all_absorptions_reversible": (
            forward_passes == expected_raw
            and inverse_passes == expected_raw
            and residual_witness_passes == expected_raw
            and full_witness_passes == expected_raw
        ),
        "compression_ratio_raw_to_orbit": (
            len(raw_states) / max(1, len(orbit_states))
        ),
        "cost_boundary": (
            "Per-residual signed map construction/replay is O(n) in this frozen family, "
            "but this audit enumerates 2^n prefixes. Enumeration is evidence, not a "
            "universal polynomial construction."
        ),
        "semantic_boundary": (
            "The residual functions are not equal over fixed coordinates. They are "
            "SAT-preserving signed-coordinate isomorphs with explicit witness lift."
        ),
    }


def build_dual_lane(c025: dict[str, Any], orbit: dict[str, Any]) -> dict[str, Any]:
    absorption = c025["absorption_compression"]
    equality = c025["equality_order_sensitivity"]
    merge_barrier = c025["semantic_merge_barrier"]
    chain = c025["chain_positive_control"]

    p_equal_forward_gates = {
        "certified_fake_width_collapse_exists": (
            absorption["normalized_residual_states"] == 1
            and absorption["witness_valid"]
        ),
        "bounded_width_positive_control": bool(chain["all_exact"] and chain["all_small_frontier"]),
        "signed_orbit_collapses_blocked_equality_cut": (
            orbit["raw_fixed_coordinate_states"] == orbit["expected_raw_fixed_coordinate_states"]
            and orbit["signed_orbit_singularities"] == 1
        ),
        "buzz_reverse_witness_replay": bool(orbit["all_absorptions_reversible"]),
        "semantic_oracle_forbidden": (
            merge_barrier["equivalence_mismatches"] == 0
            and merge_barrier["resolution_proof_failures"] == 0
        ),
    }

    # These are theorem-level gates. They are intentionally false because the
    # present run contains no universal construction/bound for arbitrary CNF.
    p_equal_theorem_gates = {
        "universal_polynomial_order_or_decomposition_discovery": False,
        "universal_polynomial_certified_state_bound": False,
        "universal_polynomial_merge_proof_volume_bound": False,
        "universal_polynomial_transition_terminal_verification_bound": False,
        "universal_polynomial_witness_recovery_bound": False,
        "constructible_for_every_cnf": False,
    }

    p_not_equal_obstruction_gates = {
        "blocked_equality_has_2pow_n_fixed_coordinate_width": (
            equality["blocked_cut_states_exact"] == equality["blocked_expected_cut_states"]
        ),
        "blocked_order_hits_budget_open": equality["blocked_budget_status"] == "OPEN",
        "same_family_has_good_exact_order": equality["interleaved_budget_status"] == "EXACT",
        "signed_orbit_defeats_this_cut_as_general_obstruction": (
            orbit["signed_orbit_singularities"] == 1 and orbit["all_absorptions_reversible"]
        ),
    }
    p_not_equal_theorem_gates = {
        "obstruction_survives_all_polynomially_discoverable_decompositions": False,
        "obstruction_survives_all_polynomially_checkable_proof_systems": False,
        "algorithm_independent_superpolynomial_lower_bound": False,
    }

    tranception_reverse = {
        "forward_lane": (
            "CNF -> certified normalization -> proof-carrying orbit/singularity -> decision/witness"
        ),
        "reverse_lane": (
            "decision/witness -> inverse Buzz map -> pre-absorption residual -> original formula witness"
        ),
        "reverse_equality_cut_pass": bool(orbit["all_absorptions_reversible"]),
        "p_equal_reverse_terminal": (
            "OPEN: no universal construction and no universal polynomial total-work bound"
        ),
        "p_not_equal_reverse_terminal": (
            "OPEN: current exponential-width witness is representation/proof-architecture scoped"
        ),
        "physical_retrocausality_claim": False,
    }

    p_equal_status = "OPEN"
    p_not_equal_status = "OPEN"
    janus_status = "DUAL_OPEN"

    return {
        "P_EQUALS_NP_LANE": {
            "finite_forward_gates": p_equal_forward_gates,
            "theorem_gates": p_equal_theorem_gates,
            "status": p_equal_status,
            "promotion_allowed": False,
        },
        "JANUS": {
            "role": "CLAIM_BOUNDARY_AND_BIDIRECTIONAL_VERIFIER",
            "status": janus_status,
            "located_bottleneck": "UNIVERSAL_CERTIFIED_RESIDUAL_ORBIT_AUTOMATON_COMPLEXITY",
            "forbidden_shortcuts": [
                "FINITE_COMPRESSION => P_EQUALS_NP",
                "ONE_EXPONENTIAL_REPRESENTATION => P_NOT_EQUALS_NP",
                "SEMANTIC_EQUIVALENCE_ORACLE => FREE_COMPRESSION",
                "NO_RETURN_PATH => ABSORPTION",
            ],
        },
        "P_NOT_EQUALS_NP_LANE": {
            "restricted_obstruction_gates": p_not_equal_obstruction_gates,
            "theorem_gates": p_not_equal_theorem_gates,
            "status": p_not_equal_status,
            "promotion_allowed": False,
        },
        "TRANCEPTION_REVERSE": tranception_reverse,
    }


def run(n: int = 14) -> dict[str, Any]:
    c025 = run_c025()
    if c025["status"] != "PASS":
        raise AssertionError("restored C025 control suite did not pass")

    orbit = audit_blocked_equality_signed_orbit(n=n)
    dual = build_dual_lane(c025, orbit)

    result: dict[str, Any] = {
        "artifact_id": RUN_ID,
        "status": "PASS",
        "run_scope": "FROZEN_REVEALED_CONTROLS_ONLY_NO_NEW_HOLDOUT",
        "c025_restored": {
            "status": c025["status"],
            "base_repository_commit_recorded_by_c025": c025["base_repository_commit"],
            "absorption_compression": c025["absorption_compression"],
            "equality_order_sensitivity": c025["equality_order_sensitivity"],
            "semantic_merge_barrier": c025["semantic_merge_barrier"],
            "chain_positive_control": c025["chain_positive_control"],
        },
        "bh_q2_signed_orbit_attack": orbit,
        "dual_lane": dual,
        "mathematical_verdict": {
            "P_VS_NP": "OPEN",
            "P_EQUALS_NP": "NOT_ESTABLISHED",
            "P_NOT_EQUALS_NP": "NOT_ESTABLISHED",
            "new_result": (
                "The C025 blocked-equality 2^n fixed-coordinate cut collapses to one "
                "explicit signed-coordinate orbit with exact inverse witness replay. "
                "This removes that particular cut as a general P!=NP obstruction, but "
                "does not supply a universal polynomial orbit discovery/construction."
            ),
            "next_exact_target": (
                "Define a general proof-carrying residual-orbit automaton whose transform "
                "class is polynomially discoverable, whose absorption certificates and "
                "Buzz inverse maps are polynomially checkable, and whose total state + "
                "certificate + discovery + witness-recovery work is polynomial on every CNF; "
                "or prove a superpolynomial lower bound for a frozen such architecture without "
                "promoting it to P!=NP beyond that architecture."
            ),
        },
        "claim_boundary": [
            "FINITE FAMILY PASS != P_EQUALS_NP",
            "RESTRICTED ARCHITECTURE OPEN != P_NOT_EQUALS_NP",
            "SIGNED ORBIT != FIXED-COORDINATE SEMANTIC EQUALITY",
            "REVERSE REPLAY != PHYSICAL RETROCAUSALITY",
            "P_VS_NP = OPEN",
        ],
    }
    result["integrity_sha256"] = digest_json(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--equality-n", type=int, default=14)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    result = run(n=args.equality_n)
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    if args.self_test:
        assert result["status"] == "PASS"
        assert result["mathematical_verdict"]["P_VS_NP"] == "OPEN"
        assert result["bh_q2_signed_orbit_attack"]["signed_orbit_singularities"] == 1
        assert result["bh_q2_signed_orbit_attack"]["all_absorptions_reversible"]


if __name__ == "__main__":
    main()
