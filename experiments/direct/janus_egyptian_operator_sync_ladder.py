#!/usr/bin/env python3
"""Pyramid-Text-inspired JANUS synchronization ladder.

This file does NOT treat ancient Egyptian texts as mathematical evidence.
It freezes four modern operator translations inspired by attested motifs and
lets revealed-control metrics decide KEEP/REJECT without reinterpretation.

PT355 -> verified blocker removal
PT366 -> seed invariant before expansion
PT477 -> cheap route pruning before expensive event-horizon work
PT222 -> mandatory forward/reverse replay

P_VS_NP remains OPEN regardless of finite outcomes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Any

from janus_certified_residual_quotient import run as run_c025
from janus_p_vs_np_dual_lane_tranception_c025_bhq2 import (
    audit_blocked_equality_signed_orbit,
)
from janus_tear_policy0a_bh_q2_buzz_physarum_signed_singularity_probe import (
    Handle,
    Policy0ABHQ2,
    apply_signed_map,
    digest,
    graph_tautology_cnf,
    invert_signed_map,
    signed_map_roundtrip_ok,
    signed_typed_signature,
)
from janus_tear_policy0a_masked_tseitin import canonical_cnf


RUN_ID = "JANUS-EGYPTIAN-OPERATOR-SYNC-PT355-366-477-222-v1"


def sha256_json(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def stop_result(stages: list[dict[str, Any]], stage: str, reason: str) -> dict[str, Any]:
    result = {
        "artifact_id": RUN_ID,
        "status": f"STOP_AT_{stage}",
        "stop_reason": reason,
        "stages": stages,
        "mathematical_verdict": {"P_VS_NP": "OPEN"},
        "claim_boundary": [
            "ANCIENT_TEXT != MODERN_ALGORITHM",
            "METRIC_DELTA != ANCIENT_PREDICTION",
            "FINITE_PASS != P_EQUALS_NP",
            "FINITE_FAIL != P_NOT_EQUALS_NP",
        ],
    }
    result["integrity_sha256"] = sha256_json(result)
    return result


def stage_pt355() -> dict[str, Any]:
    """Verified blocker removal: replay frozen C025 certified normalization."""
    c025 = run_c025()
    absorption = c025["absorption_compression"]
    raw = int(absorption["raw_residual_states"])
    normalized = int(absorption["normalized_residual_states"])
    certificates = int(absorption["cut_certificates"])
    passed = bool(
        c025["status"] == "PASS"
        and raw == absorption["expected_raw_states"]
        and normalized == 1
        and certificates == raw
        and absorption["witness_valid"]
        and absorption["automaton_status"] == "EXACT"
    )
    improved = passed and normalized < raw
    return {
        "stage": "PT355",
        "operator": "VERIFIED_BLOCKER_REMOVAL",
        "raw_residual_states": raw,
        "normalized_residual_states": normalized,
        "compression_ratio": raw / max(1, normalized),
        "normalization_certificates": certificates,
        "subsumption_steps": int(absorption["cut_subsumption_steps"]),
        "witness_valid": bool(absorption["witness_valid"]),
        "test_pass": passed,
        "metric_improved": improved,
        "continue": improved,
        "meaning": "A frozen proof-carrying normalization removes representational blockers without changing the witnessed answer.",
    }


def random_signed_map(variables: list[int], rng: random.Random) -> dict[int, tuple[int, bool]]:
    targets = list(variables)
    rng.shuffle(targets)
    return {
        source: (target, bool(rng.getrandbits(1)))
        for source, target in zip(variables, targets)
    }


def seed_fixture() -> tuple[tuple[tuple[int, ...], ...], list[int]]:
    cnf = canonical_cnf(
        (
            (1, 2, -3),
            (-1, 4),
            (2, -4, 5),
            (-2, 3),
            (-5, 1, 4),
            (3, -4),
        )
    )
    variables = sorted({abs(lit) for clause in cnf for lit in clause})
    return cnf, variables


def stage_pt366(samples: int = 256) -> dict[str, Any]:
    """Seed survives reversible coordinate transformations before expansion."""
    rng = random.Random(366)
    base, variables = seed_fixture()
    raw_forms = set()
    signatures = set()
    reverse_passes = 0
    for _ in range(samples):
        mapping = random_signed_map(variables, rng)
        transformed = apply_signed_map(base, mapping)
        raw_forms.add(transformed)
        signatures.add(signed_typed_signature(transformed))
        if not signed_map_roundtrip_ok(mapping):
            continue
        inverse = invert_signed_map(mapping)
        if apply_signed_map(transformed, inverse) == base:
            reverse_passes += 1

    passed = reverse_passes == samples and len(signatures) == 1
    improved = passed and len(raw_forms) > len(signatures)
    return {
        "stage": "PT366",
        "operator": "SEED_INVARIANT_BEFORE_CHILD_EXPANSION",
        "samples": samples,
        "bytewise_distinct_raw_forms": len(raw_forms),
        "seed_signature_classes": len(signatures),
        "reverse_map_passes": reverse_passes,
        "recognition_compression_ratio": len(raw_forms) / max(1, len(signatures)),
        "test_pass": passed,
        "metric_improved": improved,
        "continue": improved,
        "meaning": "The cheap seed signature survives reversible signed-coordinate changes and collapses multiple raw shapes before expensive canonicalization.",
    }


def thoth_route_signature(cnf: tuple[tuple[int, ...], ...]) -> tuple[str, int]:
    """Stronger cheap invariant for route pruning; attraction only, never a proof.

    It records which unsigned signed-profile classes co-occur inside clauses.
    Any signed variable permutation preserves this fingerprint, so unequal
    fingerprints are a safe reason NOT to enter the expensive event horizon.
    """
    variables = sorted({abs(lit) for clause in cnf for lit in clause})
    widths = sorted({len(clause) for clause in cnf})
    width_index = {width: i for i, width in enumerate(widths)}
    pos = {v: [0] * len(widths) for v in variables}
    neg = {v: [0] * len(widths) for v in variables}
    visits = 0

    for clause in cnf:
        slot = width_index[len(clause)]
        for lit in clause:
            (pos if lit > 0 else neg)[abs(lit)][slot] += 1
            visits += 1

    profile = {
        v: tuple(sorted((tuple(pos[v]), tuple(neg[v]))))
        for v in variables
    }
    profile_id = {v: digest(("PT477-V", profile[v])) for v in variables}

    clause_rows = []
    for clause in cnf:
        row = tuple(sorted(profile_id[abs(lit)] for lit in clause))
        clause_rows.append((len(clause), row))
        visits += len(clause)

    return digest(("PT477-ROUTE", tuple(sorted(profile.values())), tuple(sorted(clause_rows)))), visits


class ThothRoutePolicy(Policy0ABHQ2):
    def solve(self, cnf, variable_count):
        self.thoth_route_checks = 0
        self.thoth_route_edge_visits = 0
        return super().solve(cnf, variable_count)

    def quotient_lookup(self, cnf):
        self.physarum_signature_checks += 1
        seed = signed_typed_signature(cnf)
        route, visits = thoth_route_signature(cnf)
        self.thoth_route_checks += 1
        self.thoth_route_edge_visits += visits
        signature = digest(("PT477", seed, route))
        bucket = self.buckets.get(signature)
        if not bucket:
            return Handle(signature, None), None

        self.event_horizon_collisions += 1
        for entry in bucket:
            if entry.representative == cnf:
                self.absorption_hits += 1
                return Handle(signature, entry.canonicalization), entry.answer

        current_q = self.canonicalize(cnf)
        for entry in bucket:
            if entry.canonicalization is None:
                entry.canonicalization = self.canonicalize(entry.representative)
            ok, mapping = self.buzz_verify(cnf, current_q, entry)
            if not ok:
                continue
            self.absorption_hits += 1
            self.bytewise_distinct_absorptions += 1
            if mapping and any(flip for _, flip in mapping.values()):
                self.polarity_flip_absorptions += 1
            return Handle(signature, current_q), entry.answer

        return Handle(signature, current_q), None


def stage_pt477(orders: tuple[int, ...] = (3, 4, 5, 6, 7, 8, 9)) -> dict[str, Any]:
    """Route-prune before horizon; charge the new fingerprint's own work."""
    rows = []
    base_canonical = 0
    pruned_canonical = 0
    pruned_route = 0
    base_escapes = 0
    pruned_escapes = 0
    base_collisions = 0
    pruned_collisions = 0
    answers_match = True
    states_match = True
    absorptions_match = True

    # Independent invariance control for the new route fingerprint.
    rng = random.Random(477)
    fixture, variables = seed_fixture()
    route_signatures = set()
    for _ in range(256):
        transformed = apply_signed_map(fixture, random_signed_map(variables, rng))
        route_signatures.add(thoth_route_signature(transformed)[0])
    route_invariant_pass = len(route_signatures) == 1

    for order in orders:
        cnf, variable_count = graph_tautology_cnf(order)
        baseline_solver = Policy0ABHQ2()
        baseline = baseline_solver.solve(cnf, variable_count)
        pruned_solver = ThothRoutePolicy()
        pruned = pruned_solver.solve(cnf, variable_count)

        answers_match &= baseline.answer == pruned.answer
        states_match &= baseline.residual_states == pruned.residual_states
        absorptions_match &= (
            baseline.bytewise_distinct_absorptions == pruned.bytewise_distinct_absorptions
            and baseline.polarity_flip_absorptions == pruned.polarity_flip_absorptions
        )

        base_cost = baseline.signed_refinement_edge_visits + baseline.q0_fallback_refinement_edge_visits
        pruned_cost = pruned.signed_refinement_edge_visits + pruned.q0_fallback_refinement_edge_visits
        base_canonical += base_cost
        pruned_canonical += pruned_cost
        pruned_route += pruned_solver.thoth_route_edge_visits
        base_escapes += baseline.hawking_escape_count
        pruned_escapes += pruned.hawking_escape_count
        base_collisions += baseline.event_horizon_collisions
        pruned_collisions += pruned.event_horizon_collisions

        rows.append({
            "order": order,
            "answer": pruned.answer,
            "states_baseline": baseline.residual_states,
            "states_pruned": pruned.residual_states,
            "absorptions_baseline": baseline.bytewise_distinct_absorptions,
            "absorptions_pruned": pruned.bytewise_distinct_absorptions,
            "canonical_edge_visits_baseline": base_cost,
            "canonical_edge_visits_pruned": pruned_cost,
            "route_edge_visits_charged": pruned_solver.thoth_route_edge_visits,
            "hawking_escapes_baseline": baseline.hawking_escape_count,
            "hawking_escapes_pruned": pruned.hawking_escape_count,
            "event_horizon_collisions_baseline": baseline.event_horizon_collisions,
            "event_horizon_collisions_pruned": pruned.event_horizon_collisions,
        })

    charged_pruned_total = pruned_canonical + pruned_route
    strict_cost_improvement = charged_pruned_total < base_canonical
    no_escape_regression = pruned_escapes <= base_escapes
    no_collision_regression = pruned_collisions <= base_collisions
    passed = bool(
        route_invariant_pass
        and answers_match
        and states_match
        and absorptions_match
        and no_escape_regression
        and no_collision_regression
    )
    improved = passed and strict_cost_improvement
    return {
        "stage": "PT477",
        "operator": "THOTH_ROUTE_PRUNE",
        "orders": list(orders),
        "route_signature_signed_invariance": route_invariant_pass,
        "answers_match": answers_match,
        "states_match": states_match,
        "certified_absorptions_match": absorptions_match,
        "baseline_canonical_edge_visits": base_canonical,
        "pruned_canonical_edge_visits": pruned_canonical,
        "new_route_edge_visits_charged": pruned_route,
        "pruned_total_charged_edge_visits": charged_pruned_total,
        "charged_cost_ratio": charged_pruned_total / max(1, base_canonical),
        "baseline_hawking_escapes": base_escapes,
        "pruned_hawking_escapes": pruned_escapes,
        "baseline_event_horizon_collisions": base_collisions,
        "pruned_event_horizon_collisions": pruned_collisions,
        "test_pass": passed,
        "metric_improved": improved,
        "continue": improved,
        "rows": rows,
        "meaning": "The Thoth gate may reject incompatible candidate routes before signed canonicalization, but it is promoted only if its own charged work is lower and all certified merges survive.",
    }


def stage_pt222(n: int = 14) -> dict[str, Any]:
    """Tranception: every accepted route must return to residual and full witness."""
    audit = audit_blocked_equality_signed_orbit(n=n)
    expected = 1 << n
    passed = bool(
        audit["all_absorptions_reversible"]
        and audit["normalization_certificate_passes"] == expected
        and audit["forward_map_passes"] == expected
        and audit["inverse_map_passes"] == expected
        and audit["residual_witness_passes"] == expected
        and audit["full_formula_witness_passes"] == expected
    )
    return {
        "stage": "PT222",
        "operator": "TRANCEPTION_FORWARD_REVERSE_REPLAY",
        "n": n,
        "accepted_routes": expected,
        "normalization_certificate_passes": audit["normalization_certificate_passes"],
        "forward_map_passes": audit["forward_map_passes"],
        "inverse_map_passes": audit["inverse_map_passes"],
        "residual_witness_passes": audit["residual_witness_passes"],
        "full_formula_witness_passes": audit["full_formula_witness_passes"],
        "signed_orbit_singularities": audit["signed_orbit_singularities"],
        "all_absorptions_reversible": audit["all_absorptions_reversible"],
        "test_pass": passed,
        "metric_improved": passed,
        "continue": passed,
        "meaning": "Reverse replay is a falsification/safety gate, not physical retrocausality.",
    }


def run() -> dict[str, Any]:
    stages: list[dict[str, Any]] = []

    pt355 = stage_pt355()
    stages.append(pt355)
    if not pt355["continue"]:
        return stop_result(stages, "PT355", "verified blocker removal did not improve the frozen metric")

    pt366 = stage_pt366()
    stages.append(pt366)
    if not pt366["continue"]:
        return stop_result(stages, "PT366", "seed invariant did not compress raw recognition with exact reverse maps")

    pt477 = stage_pt477()
    stages.append(pt477)
    if not pt477["continue"]:
        return stop_result(stages, "PT477", "route pruning failed to reduce charged horizon work without regression")

    pt222 = stage_pt222()
    stages.append(pt222)
    if not pt222["continue"]:
        return stop_result(stages, "PT222", "forward/reverse witness replay was not complete")

    result: dict[str, Any] = {
        "artifact_id": RUN_ID,
        "status": "PASS_CONTINUE",
        "run_scope": "REVEALED_CALIBRATION_ONLY_NO_NEW_HOLDOUT",
        "stages": stages,
        "surviving_operator_chain": [
            "PT355_VERIFIED_BLOCKER_REMOVAL",
            "PT366_SEED_INVARIANT",
            "PT477_THOTH_ROUTE_PRUNE",
            "PT222_TRANCEPTION_FORWARD_REVERSE",
        ],
        "mathematical_verdict": {
            "P_VS_NP": "OPEN",
            "P_EQUALS_NP": "NOT_ESTABLISHED",
            "P_NOT_EQUALS_NP": "NOT_ESTABLISHED",
        },
        "next_gate": "Freeze the surviving operator chain and only then test a new preregistered holdout or a stronger revealed-family stress test.",
        "claim_boundary": [
            "Ancient texts supplied heuristic operator prompts only.",
            "The frozen metrics, not textual interpretation, decide promotion.",
            "Reverse replay is verification, not physical backwards time.",
            "No specific pyramid resonance frequency is used in this run.",
        ],
    }
    result["integrity_sha256"] = sha256_json(result)
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
        assert result["status"] in {"PASS_CONTINUE", "STOP_AT_PT355", "STOP_AT_PT366", "STOP_AT_PT477", "STOP_AT_PT222"}


if __name__ == "__main__":
    main()
