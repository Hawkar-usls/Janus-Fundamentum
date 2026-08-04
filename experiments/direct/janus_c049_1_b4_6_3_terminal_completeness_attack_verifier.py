#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA = "C049.1-B4.6.3-TERMINAL-CONTRACT-ATTACK-LEDGER-v1"
PHASE = "B4.6.3_A_TERMINAL_CONTRACT_ATTACK_GATE"
SOURCE_HEAD = "ce7b665e7964f813af12d49a20a1b915bc998398"
UPSTREAM_SCHEMA = "C049.1-B4.6.2-FULL-ITERATIVE-COMPRESSION-CYCLE-v1"
UPSTREAM_DIGEST = "5e7df2407456fe41a5dadda4f8855df5f7ab2ae96dfac637d8857c2c4c0c44e6"
GLOBAL_TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"

POSITIVE_FIXTURE = {
    "ambient_dimension": 2,
    "k": 1,
    "whole_factor_blocks": [[1], [2], [1]],
    "affine_offsets": [0, 1, 1],
}
NO_LAYOUT_FIXTURE = {
    "ambient_dimension": 2,
    "k": 1,
    "whole_factor_blocks": [[1, 2], [1, 2]],
    "affine_offsets": [0, 1],
}
INSERTION_OBSTRUCTION_FIXTURE = {
    "ambient_dimension": 4,
    "k": 1,
    "whole_factor_blocks": [[1], [2], [4], [8], [3], [12]],
    "affine_offsets": [0, 0, 0, 0, 0, 0],
    "previous_factor_order": [0, 4, 2, 3, 1],
    "new_factor_id": 5,
}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def rref(rows: Iterable[int], d: int) -> tuple[int, ...]:
    basis: dict[int, int] = {}
    for raw in rows:
        value = int(raw)
        if value < 0 or value >= (1 << d):
            raise AssertionError("row outside ambient GF(2) space")
        for pivot in sorted(basis, reverse=True):
            if (value >> pivot) & 1:
                value ^= basis[pivot]
        if not value:
            continue
        pivot = value.bit_length() - 1
        for other in list(basis):
            if (basis[other] >> pivot) & 1:
                basis[other] ^= value
        basis[pivot] = value
    return tuple(basis[pivot] for pivot in sorted(basis))


def reduce_vector(value: int, basis: Sequence[int]) -> int:
    out = int(value)
    for pivot, row in sorted(
        ((int(row).bit_length() - 1, int(row)) for row in basis), reverse=True
    ):
        if (out >> pivot) & 1:
            out ^= row
    return out


def span_vectors(basis: Sequence[int]) -> list[int]:
    values = [0]
    for row in basis:
        values += [value ^ int(row) for value in values]
    return sorted(set(values))


def intersection(left: Sequence[int], right: Sequence[int], d: int) -> tuple[int, ...]:
    left_basis = rref(left, d)
    right_basis = rref(right, d)
    return rref(
        (value for value in span_vectors(left_basis) if reduce_vector(value, right_basis) == 0),
        d,
    )


def exact_cut_transcript(fixture: dict, order: Sequence[int]) -> list[dict]:
    blocks = fixture["whole_factor_blocks"]
    d = int(fixture["ambient_dimension"])
    if sorted(int(value) for value in order) != list(range(len(blocks))):
        raise AssertionError("order is not a whole-factor permutation")
    cuts = []
    for cut in range(len(order) + 1):
        left_ids = [int(value) for value in order[:cut]]
        right_ids = [int(value) for value in order[cut:]]
        left = rref((row for index in left_ids for row in blocks[index]), d)
        right = rref((row for index in right_ids for row in blocks[index]), d)
        boundary = intersection(left, right, d)
        cuts.append(
            {
                "cut": cut,
                "left_factor_ids": left_ids,
                "right_factor_ids": right_ids,
                "boundary_rref": list(boundary),
                "width": len(boundary),
            }
        )
    return cuts


def exhaustive_oracle(fixture: dict) -> dict:
    n = len(fixture["whole_factor_blocks"])
    k = int(fixture["k"])
    accepted = []
    tested = 0
    work = 0
    for order_tuple in itertools.permutations(range(n)):
        tested += 1
        order = list(order_tuple)
        cuts = exact_cut_transcript(fixture, order)
        work += len(cuts)
        maximum_width = max(item["width"] for item in cuts)
        if maximum_width <= k:
            accepted.append(
                {
                    "factor_order": order,
                    "exact_cut_transcript": cuts,
                    "exact_maximum_width": maximum_width,
                    "layout_digest": digest({"factor_order": order, "exact_cut_transcript": cuts}),
                }
            )
    accepted.sort(key=lambda item: (item["factor_order"], item["layout_digest"]))
    return {
        "complete": True,
        "permutations_tested": tested,
        "cut_recomputations": work,
        "layout_count_at_cap": len(accepted),
        "selected_layout": accepted[0] if accepted else None,
        "accepted_layout_digests": [item["layout_digest"] for item in accepted],
    }


def insertion_candidates(fixture: dict) -> dict:
    previous = [int(value) for value in fixture["previous_factor_order"]]
    new_factor = int(fixture["new_factor_id"])
    k = int(fixture["k"])
    candidates = []
    for position in range(len(previous) + 1):
        order = previous[:position] + [new_factor] + previous[position:]
        cuts = exact_cut_transcript(fixture, order)
        maximum_width = max(item["width"] for item in cuts)
        candidates.append(
            {
                "insertion_position": position,
                "factor_order": order,
                "exact_width_vector": [item["width"] for item in cuts],
                "exact_maximum_width": maximum_width,
                "accepted": maximum_width <= k,
            }
        )
    return {
        "candidate_count": len(candidates),
        "accepted_count": sum(1 for item in candidates if item["accepted"]),
        "candidates": candidates,
        "cut_recomputations": sum(len(item["exact_width_vector"]) for item in candidates),
    }


def budget_prefix(fixture: dict, permutation_cap: int) -> dict:
    n = len(fixture["whole_factor_blocks"])
    k = int(fixture["k"])
    records = []
    work = 0
    for index, order_tuple in enumerate(itertools.permutations(range(n))):
        if index >= permutation_cap:
            break
        order = list(order_tuple)
        cuts = exact_cut_transcript(fixture, order)
        work += len(cuts)
        maximum_width = max(item["width"] for item in cuts)
        records.append(
            {
                "permutation_index": index,
                "factor_order": order,
                "exact_cut_transcript": cuts,
                "exact_maximum_width": maximum_width,
                "accepted": maximum_width <= k,
            }
        )
    return {
        "complete": False,
        "permutation_cap": permutation_cap,
        "permutations_tested": len(records),
        "cut_recomputations": work,
        "verified_prefix": records,
    }


def verify_upstream(upstream: dict) -> None:
    expected_fixture = {**POSITIVE_FIXTURE, "initial_order": [0]}
    if upstream.get("schema") != UPSTREAM_SCHEMA:
        raise AssertionError("upstream schema mismatch")
    if upstream.get("manifest_digest") != UPSTREAM_DIGEST:
        raise AssertionError("upstream manifest digest mismatch")
    if upstream.get("fixture") != expected_fixture:
        raise AssertionError("upstream fixture mismatch")
    if upstream.get("all_rounds_executed") is not True:
        raise AssertionError("upstream rounds incomplete")
    if upstream.get("final_reconstructed_factor_order") != [0, 1, 2]:
        raise AssertionError("upstream final order mismatch")
    if upstream.get("final_exact_maximum_width") != 1:
        raise AssertionError("upstream final width mismatch")
    strict = upstream.get("strict_boundary", {})
    if strict.get("terminal_completeness_proved") is not False:
        raise AssertionError("upstream terminal boundary mismatch")
    if strict.get("current_global_terminal") != GLOBAL_TERMINAL:
        raise AssertionError("upstream global terminal mismatch")


def verify_fixed_point(artifact: dict) -> None:
    claimed = artifact.get("artifact_digest")
    body = copy.deepcopy(artifact)
    body.pop("artifact_digest", None)
    if claimed != digest(body):
        raise AssertionError("artifact digest mismatch")
    actual_size = len(canonical_json(artifact)) + 1
    if artifact["certificate_accounting"]["fixed_point_serialized_bytes"] != actual_size:
        raise AssertionError("certificate byte count mismatch")
    if artifact["work_ledger"]["certificate_byte_charge"] != actual_size:
        raise AssertionError("certificate work charge mismatch")
    expected_final = artifact["work_ledger"]["oracle_cut_recomputations"] + actual_size
    if artifact["work_ledger"]["cumulative_work_final"] != expected_final:
        raise AssertionError("cumulative work mismatch")


def verify_positive(case: dict, upstream: dict) -> None:
    if case["case_id"] != "POSITIVE_CYCLE_FOUND_LAYOUT" or case["fixture"] != POSITIVE_FIXTURE:
        raise AssertionError("positive case identity mismatch")
    expected_binding = {
        "schema": upstream["schema"],
        "manifest_digest": upstream["manifest_digest"],
        "result": upstream["result"],
        "round_count": upstream["round_count"],
        "root_full_sets_computed": upstream["audit"]["root_full_sets_computed"],
        "layouts_reconstructed": upstream["audit"]["layouts_reconstructed"],
        "failed_refinements": upstream["audit"]["failed_refinements"],
        "cumulative_work_final": upstream["work_ledger"]["cumulative_work_final"],
    }
    if case["upstream_binding"] != expected_binding:
        raise AssertionError("positive upstream binding mismatch")
    oracle = exhaustive_oracle(POSITIVE_FIXTURE)
    if case["independent_oracle"] != oracle or oracle["layout_count_at_cap"] != 6:
        raise AssertionError("positive oracle mismatch")
    order = [0, 1, 2]
    cuts = exact_cut_transcript(POSITIVE_FIXTURE, order)
    expected = {
        "terminal": "FOUND_LAYOUT",
        "found_layout": True,
        "no_layout_at_cap": False,
        "factor_order": order,
        "exact_cut_transcript": cuts,
        "exact_maximum_width": 1,
        "scope": "FROZEN_FIXTURE_ONLY",
        "production_terminal_completeness_claim": False,
        "reason": "UPSTREAM_ANCESTRY_REPLAY_PLUS_INDEPENDENT_EXACT_WIDTH_WITNESS",
    }
    if case["terminal_decision"] != expected:
        raise AssertionError("positive terminal mismatch")


def verify_negative(case: dict) -> None:
    if case["case_id"] != "KNOWN_NO_LAYOUT_REQUIRES_ROOT_COMPLETENESS" or case["fixture"] != NO_LAYOUT_FIXTURE:
        raise AssertionError("negative case identity mismatch")
    oracle = exhaustive_oracle(NO_LAYOUT_FIXTURE)
    if case["independent_oracle"] != oracle or oracle["layout_count_at_cap"] != 0:
        raise AssertionError("negative oracle mismatch")
    if case["trajectory_engine_evidence"] != {
        "complete_root_full_set_transcript_present": False,
        "root_acceptance_biconditional_proved": False,
    }:
        raise AssertionError("negative evidence mismatch")
    expected = {
        "terminal": "OPEN_TERMINAL_COMPLETENESS_PENDING",
        "found_layout": False,
        "no_layout_at_cap": False,
        "oracle_no_layout_at_cap": True,
        "reason": "EXHAUSTIVE_FIXTURE_ORACLE_IS_NOT_A_ROOT_FULL_SET_COMPLETENESS_CERTIFICATE",
    }
    if case["terminal_decision"] != expected:
        raise AssertionError("negative terminal promoted without root proof")


def verify_insertion(case: dict) -> None:
    if case["case_id"] != "INSERTION_FAILURE_MUST_NOT_BECOME_NO_LAYOUT" or case["fixture"] != INSERTION_OBSTRUCTION_FIXTURE:
        raise AssertionError("insertion case identity mismatch")
    insertions = insertion_candidates(INSERTION_OBSTRUCTION_FIXTURE)
    oracle = exhaustive_oracle(INSERTION_OBSTRUCTION_FIXTURE)
    if insertions["accepted_count"] != 0 or oracle["layout_count_at_cap"] != 72:
        raise AssertionError("insertion obstruction constants drift")
    if case["insertion_only_search"] != insertions or case["independent_oracle"] != oracle:
        raise AssertionError("insertion evidence mismatch")
    selected = oracle["selected_layout"]
    expected = {
        "terminal": "FOUND_LAYOUT",
        "found_layout": True,
        "no_layout_at_cap": False,
        "factor_order": selected["factor_order"],
        "exact_cut_transcript": selected["exact_cut_transcript"],
        "exact_maximum_width": selected["exact_maximum_width"],
        "scope": "BOUNDED_ATTACK_FIXTURE_ONLY",
        "production_terminal_completeness_claim": False,
        "reason": "COMPLETE_BOUNDED_ORACLE_REJECTS_INSERTION_ONLY_FALSE_NEGATIVE",
    }
    if case["terminal_decision"] != expected:
        raise AssertionError("insertion failure misclassified")


def verify_budget(case: dict) -> None:
    if case["case_id"] != "BUDGET_CUTOFF_PRESERVES_VERIFIED_PREFIX" or case["fixture"] != POSITIVE_FIXTURE:
        raise AssertionError("budget case identity mismatch")
    prefix = budget_prefix(POSITIVE_FIXTURE, 2)
    if case["bounded_search"] != prefix:
        raise AssertionError("budget prefix mismatch")
    expected = {
        "terminal": "OPEN_WORK_BUDGET",
        "found_layout": False,
        "no_layout_at_cap": False,
        "reason": "PERMUTATION_CAP_REACHED_BEFORE_COMPLETE_DISCOVERY_TRANSCRIPT",
    }
    if case["terminal_decision"] != expected:
        raise AssertionError("budget cutoff misclassified")


def verify(artifact: dict, upstream: dict) -> None:
    verify_upstream(upstream)
    verify_fixed_point(artifact)
    if artifact.get("schema") != SCHEMA or artifact.get("phase") != PHASE:
        raise AssertionError("artifact schema/phase mismatch")
    if artifact.get("source_head") != SOURCE_HEAD:
        raise AssertionError("source head mismatch")
    if artifact.get("upstream_manifest_digest") != UPSTREAM_DIGEST:
        raise AssertionError("upstream digest binding mismatch")
    cases = artifact.get("cases")
    if not isinstance(cases, list) or len(cases) != 4:
        raise AssertionError("case inventory mismatch")
    verify_positive(cases[0], upstream)
    verify_negative(cases[1])
    verify_insertion(cases[2])
    verify_budget(cases[3])
    expected_work = sum(
        case.get("independent_oracle", {}).get("cut_recomputations", 0)
        + case.get("insertion_only_search", {}).get("cut_recomputations", 0)
        + case.get("bounded_search", {}).get("cut_recomputations", 0)
        for case in cases
    )
    if artifact["work_ledger"]["oracle_cut_recomputations"] != expected_work:
        raise AssertionError("oracle work mismatch")
    if artifact["work_ledger"]["monotone"] is not True:
        raise AssertionError("work ledger is not monotone")
    if artifact["attack_ledger"] != {
        "case_count": 4,
        "false_no_layout_attempts_rejected": 3,
        "found_layout_fixture_witnesses": 2,
        "no_layout_fixture_oracles": 1,
        "open_budget_terminals": 1,
        "root_completeness_counterexamples_found": 0,
        "claim": "TERMINAL_CONTRACT_HARDENED_NOT_TERMINAL_COMPLETENESS_PROVED",
    }:
        raise AssertionError("attack ledger mismatch")
    if artifact["induction_obligations"] != {
        "leaf_full_set_completeness": "REQUIRED_GENERAL_LEMMA_NOT_PROVED_HERE",
        "child_pair_cartesian_exhaustion": "UPSTREAM_POSITIVE_TRANSCRIPT_REPLAYED",
        "lattice_path_exhaustion": "UPSTREAM_POSITIVE_TRANSCRIPT_REPLAYED",
        "refinement_success_and_failure_partition": "UPSTREAM_POSITIVE_TRANSCRIPT_REPLAYED",
        "up_k_language_preservation": "B2_LOCAL_REPLAY_AVAILABLE_GENERAL_COMPOSITION_PENDING",
        "internal_node_full_set_biconditional": "OPEN",
        "root_acceptance_biconditional": "OPEN",
        "complete_negative_root_certificate": "ABSENT",
    }:
        raise AssertionError("induction obligation ledger mismatch")
    if artifact["result"] != "TERMINAL_CONTRACT_ATTACK_LEDGER_CLOSED":
        raise AssertionError("result mismatch")
    if artifact["strict_boundary"] != {
        "found_layout_enabled_for_verified_fixtures": True,
        "no_layout_at_cap_enabled": False,
        "terminal_completeness_proved": False,
        "empty_full_set_may_imply_no_layout": False,
        "budget_cut_may_imply_no_layout": False,
        "current_global_terminal": GLOBAL_TERMINAL,
        "next_gate": "C049.1_B4.6.3_B_ROOT_FULL_SET_BICONDITIONAL",
        "p_vs_np": "OPEN",
    }:
        raise AssertionError("strict boundary mismatch")


def repair_fixed_point(artifact: dict) -> dict:
    repaired = copy.deepcopy(artifact)
    work = int(repaired["work_ledger"]["oracle_cut_recomputations"])
    repaired["artifact_digest"] = "0" * 64
    repaired["certificate_accounting"]["fixed_point_serialized_bytes"] = 0
    repaired["work_ledger"]["certificate_byte_charge"] = 0
    repaired["work_ledger"]["cumulative_work_final"] = work
    for _ in range(64):
        body = copy.deepcopy(repaired)
        body.pop("artifact_digest", None)
        repaired["artifact_digest"] = digest(body)
        size = len(canonical_json(repaired)) + 1
        changed = False
        for container, key, value in (
            (repaired["certificate_accounting"], "fixed_point_serialized_bytes", size),
            (repaired["work_ledger"], "certificate_byte_charge", size),
            (repaired["work_ledger"], "cumulative_work_final", work + size),
        ):
            if container[key] != value:
                container[key] = value
                changed = True
        if not changed:
            body = copy.deepcopy(repaired)
            body.pop("artifact_digest", None)
            repaired["artifact_digest"] = digest(body)
            if len(canonical_json(repaired)) + 1 == size:
                return repaired
    raise AssertionError("tamper repair fixed point failed")


def expect_rejected(candidate: dict, upstream: dict, label: str) -> None:
    try:
        verify(repair_fixed_point(candidate), upstream)
    except AssertionError:
        return
    raise AssertionError(f"digest-repaired tamper accepted: {label}")


def tamper_self_test(artifact: dict, upstream: dict) -> None:
    candidate = copy.deepcopy(artifact)
    candidate["cases"][1]["terminal_decision"].update(
        {"terminal": "NO_LAYOUT_AT_CAP", "no_layout_at_cap": True}
    )
    expect_rejected(candidate, upstream, "fake negative terminal")

    candidate = copy.deepcopy(artifact)
    candidate["cases"][0]["independent_oracle"]["accepted_layout_digests"].pop()
    expect_rejected(candidate, upstream, "deleted positive root witness")

    candidate = copy.deepcopy(artifact)
    candidate["cases"][2]["terminal_decision"].update(
        {"terminal": "NO_LAYOUT_AT_CAP", "found_layout": False, "no_layout_at_cap": True}
    )
    expect_rejected(candidate, upstream, "insertion-only false negative")

    candidate = copy.deepcopy(artifact)
    candidate["cases"][3]["terminal_decision"].update(
        {"terminal": "NO_LAYOUT_AT_CAP", "no_layout_at_cap": True}
    )
    expect_rejected(candidate, upstream, "budget cutoff false negative")

    candidate = copy.deepcopy(artifact)
    candidate["cases"][0]["terminal_decision"]["factor_order"] = [0, 2, 1]
    expect_rejected(candidate, upstream, "altered found-layout order")

    print("TAMPER_CONTROLS = 5 / 5 REJECTED")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    parser.add_argument("--b4-6-2-artifact", required=True)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    artifact = json.loads(Path(args.artifact).read_text())
    upstream = json.loads(Path(args.b4_6_2_artifact).read_text())
    verify(artifact, upstream)
    if args.tamper_self_test:
        tamper_self_test(artifact, upstream)
    print("JANUS_C049_1_B4_6_3_TERMINAL_CONTRACT_VERIFIER = PASS")
    print("ARTIFACT_DIGEST =", artifact["artifact_digest"])
    print("GLOBAL_TERMINAL =", artifact["strict_boundary"]["current_global_terminal"])


if __name__ == "__main__":
    main()
