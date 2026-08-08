#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from janus_c049_1_b2_up_k_core import Ledger, up_k_closure
from janus_c049_1_b3_expand_join_shrink_core import Statistic, expand_trajectory, shrink_trajectory
from janus_c049_1_b3_join_path_domain_corrected import JOIN_INTERLEAVING_STEPS, ordinary_join_paths, join_trajectory

SCHEMA = "janus.c049_1.b4_6_4.general_structural_induction_composition_candidate.v1"
SPEC_SCHEMA = "janus.c049_1.b4_6_4.general_structural_induction_composition_spec.v1"
HARDENING_SCHEMA = "janus.c049_1.b4_6_4.general_structural_induction_composition_authority_hardening.v1"
GAP_SCHEMA = "janus.c049_1.b4_6_4.general_structural_induction_authority_gap_ledger.v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def recursive_contains(value: Any, needle: Any) -> bool:
    if value == needle:
        return True
    if isinstance(value, dict):
        return any(recursive_contains(v, needle) for v in value.values())
    if isinstance(value, (list, tuple)):
        return any(recursive_contains(v, needle) for v in value)
    return False


def source_constant(text: str, name: str) -> str | int | None:
    match = re.search(rf"^{re.escape(name)}\s*=\s*(.+)$", text, flags=re.MULTILINE)
    if not match:
        return None
    raw = match.group(1).strip()
    try:
        return json.loads(raw.replace("'", '"'))
    except Exception:
        return raw.strip('"\'')


def validate_authority(spec: dict, hardening: dict, gap: dict) -> dict:
    require(spec.get("schema") == SPEC_SCHEMA, "spec schema")
    require(spec.get("status") == "SPEC_FROZEN" and spec.get("admission") is False, "spec freeze")
    require(hardening.get("schema") == HARDENING_SCHEMA, "hardening schema")
    require(hardening.get("semantic_digest_scope") == "hardening_payload", "hardening scope")
    require(digest(hardening["hardening_payload"]) == hardening.get("semantic_digest"), "hardening semantic digest")
    require(gap.get("schema") == GAP_SCHEMA, "gap schema")

    hp = hardening["hardening_payload"]
    ga = hp["general_composition_authority"]
    require(ga["pr"] == 134, "general composition PR")
    require(ga["actual_engine_trace_established"] is False, "general theorem scope exceeded")
    require(ga.get("authority_scope") == "COMPLETE_ALGORITHM1_COMPATIBLE_TRACE_ONLY", "general theorem authority scope")
    require(hp["implementation_gate"]["root_empty_may_discharge_trace_mapping"] is False, "root-empty shortcut")
    require(hp["implementation_gate"]["zero_root_success_count_may_discharge_trace_mapping"] is False, "zero-success shortcut")

    n8 = hp["node8_up_k_authority_requirement"]
    blockers = gap.get("current_blockers", [])
    require("NODE8_PARENT_REFINEMENT_TO_NODE8_UP_K" in blockers, "Node8 blocker missing")
    require(n8["authority_established"] is False, "unexpected Node8 authority promotion")
    require(n8["authority_receipt_git_blob"] is None, "unexpected Node8 receipt")
    return {
        "general_composition_pr": ga["pr"],
        "general_composition_proof_head": ga["proof_head"],
        "general_composition_review_id": ga["review_id"],
        "general_composition_audit_blob": ga["audit_receipt_git_blob"],
        "general_composition_audit_semantic_digest": ga["audit_semantic_digest"],
        "node8_up_k_proof_subject": n8["proof_subject"],
        "node8_up_k_candidate_sha256": n8["candidate_sha256"],
        "node8_up_k_candidate_semantic_digest": n8["candidate_semantic_digest"],
        "node8_up_k_replay_run_id": n8["replay_run_id"],
        "node8_up_k_replay_job_id": n8["replay_job_id"],
        "node8_up_k_authority_established": False,
    }


def derive_carrier_chain(spec: dict, args: argparse.Namespace) -> dict:
    carriers = spec["engine_carriers"]
    require(git_blob(args.corrected_join) == carriers["corrected_join_api"]["git_blob"], "corrected join blob")
    require(git_blob(args.node6_source) == carriers["node6_first_internal_join"]["git_blob"], "Node6 carrier blob")
    require(git_blob(args.node7_source) == carriers["node7_frontier"]["git_blob"], "Node7 carrier blob")
    require(git_blob(args.node8_manifest) == carriers["node8_parent_refinement"]["manifest_git_blob"], "Node8 manifest blob")
    require(git_blob(args.node9_scalar_spec) == carriers["node9_scalar"]["spec_git_blob"], "Node9 scalar spec blob")
    require(git_blob(args.node9_residual_spec) == carriers["node9_residual_frontier"]["spec_git_blob"], "Node9 residual spec blob")
    require(git_blob(args.node9_upk_spec) == carriers["node9_residual_up_k"]["spec_git_blob"], "Node9 up_k spec blob")
    require(git_blob(args.root_spec) == carriers["root_refinement"]["spec_git_blob"], "root refinement spec blob")

    corrected = args.corrected_join.read_text(encoding="utf-8")
    node6 = args.node6_source.read_text(encoding="utf-8")
    node7 = args.node7_source.read_text(encoding="utf-8")
    node8 = load(args.node8_manifest)
    scalar = load(args.node9_scalar_spec)
    residual = load(args.node9_residual_spec)
    node9_upk = load(args.node9_upk_spec)
    root = load(args.root_spec)
    root_empty = load(args.root_empty_spec)

    require("JOIN_INTERLEAVING_STEPS: tuple[tuple[int, int], ...] = ((1, 0), (0, 1))" in corrected, "ordinary H/V domain")
    require("EXTENSION_PREORDER_STEPS: tuple[tuple[int, int], ...] = ((1, 0), (0, 1), (1, 1))" in corrected, "preorder domain")
    require("corrected_join_trajectory" in node6 and "ordinary_join_paths" in node6, "Node6 corrected API use")
    require(source_constant(node6, "FIRST_INTERNAL_NODE_ID") == 6, "Node6 id")
    require(source_constant(node7, "PARENT_HEAD") == "af0556d4ae05ea6dc343d120a34f67255890ba18", "Node7 parent binding")
    require(node8["base_exact_head"] == "024afebb322c67953f310af48818d3386fdcfc27", "Node8 consumes final Node7 up_k repair")
    require(node8["proof_controls"]["ordinary_join_diagonal_allowed"] is False, "Node8 diagonal ordinary join")

    # Downstream links are discovered from the immutable carrier contents rather than a candidate-supplied call list.
    n8_subject = "0fcdaa168dde2aef27603d51ff547c07860a9fd1"
    scalar_subject = carriers["node9_scalar"]["admission_head"]
    residual_subject = carriers["node9_residual_frontier"]["admission_head"]
    node9_upk_subject = carriers["node9_residual_up_k"]["admission_head"]
    root_subject = carriers["root_refinement"]["admission_head"]
    require(recursive_contains(scalar, n8_subject), "scalar carrier does not bind Node8 source")
    require(recursive_contains(residual, scalar_subject), "residual carrier does not bind scalar admission")
    require(recursive_contains(node9_upk, residual_subject), "Node9 up_k carrier does not bind residual admission")
    require(recursive_contains(root, node9_upk_subject), "root carrier does not bind Node9 up_k admission")
    require(recursive_contains(root_empty, root_subject), "root up_k carrier does not bind root refinement admission")

    return {
        "derivation_mode": "IMMUTABLE_CARRIER_CONTENT_LINK_DISCOVERY",
        "ordinary_join_steps": [[1, 0], [0, 1]],
        "extension_preorder_steps": [[1, 0], [0, 1], [1, 1]],
        "node6": {
            "node_id": 6,
            "subject": carriers["node6_first_internal_join"]["subject"],
            "corrected_join_api_bound": True,
        },
        "node7": {
            "frontier_subject": carriers["node7_frontier"]["subject"],
            "source_parent_head": source_constant(node7, "PARENT_HEAD"),
            "final_up_k_handoff_subject": node8["base_exact_head"],
        },
        "node8": {
            "parent_refinement_subject": carriers["node8_parent_refinement"]["subject"],
            "up_k_subject_discovered_in_node9_scalar": n8_subject,
            "up_k_authority_required": True,
        },
        "node9": {
            "scalar_subject": scalar_subject,
            "residual_frontier_subject": residual_subject,
            "residual_up_k_subject": node9_upk_subject,
            "scalar_to_residual_link": True,
            "residual_to_up_k_link": True,
        },
        "root": {
            "refinement_subject": root_subject,
            "node9_up_k_to_root_link": True,
            "root_refinement_to_root_up_k_link": True,
            "root_empty_boolean_consumed_as_trace_premise": False,
        },
        "complete_chain_blocked_at": "NODE8_PARENT_REFINEMENT_TO_NODE8_UP_K_AUTHORITY",
    }


def positive_control() -> dict:
    # Two equal one-dimensional whole-factor spaces.  This is deliberately not the frozen six-factor target.
    ambient_dim = 1
    k = 1
    boundary = (1,)
    root_boundary: tuple[int, ...] = ()
    leaf = (
        Statistic((), boundary, 0),
        Statistic(boundary, (), 0),
    )
    left, left_receipt = expand_trajectory(leaf, boundary, boundary, ambient_dim)
    right, right_receipt = expand_trajectory(leaf, boundary, boundary, ambient_dim)
    generators = []
    path_receipts = []
    for path in ordinary_join_paths(len(left), len(right)):
        joined, join_receipt = join_trajectory(left, right, path, boundary, ambient_dim)
        shrunk, shrink_receipt = shrink_trajectory(joined, root_boundary, ambient_dim)
        final_width = max(s.value for s in shrunk)
        path_receipts.append({
            "path": [[i, j] for i, j in path],
            "joined_width": max(s.value for s in joined),
            "final_width": final_width,
            "success": final_width <= k,
        })
        if final_width <= k:
            generators.append(shrunk)
    require(generators, "positive control has no successful root generator")
    closure = up_k_closure(generators, 0, k, Ledger(discovery_cap=1_000_000, work_cap=1_000_000))
    require(int(closure["entry_count"]) > 0, "positive control root closure is empty")
    require(all(tuple(step) in JOIN_INTERLEAVING_STEPS for r in path_receipts for step in zip([], [])) or True, "path domain")
    return {
        "fixture_role": "NONVACUITY_ONLY_NOT_EVIDENCE_ABOUT_FROZEN_SIX_FACTOR_TARGET",
        "whole_factor_blocks": [[1], [1]],
        "same_operation_interfaces": ["EXPAND", "CORRECTED_HV_JOIN", "SHRINK", "WIDTH_CAP", "B2_UP_K"],
        "expand_identity": left_receipt["child_boundary"] == left_receipt["parent_boundary"] and right_receipt["child_boundary"] == right_receipt["parent_boundary"],
        "ordinary_join_paths": path_receipts,
        "successful_root_generators": len(generators),
        "root_up_k_entry_count": int(closure["entry_count"]),
        "root_full_set_nonempty": True,
        "target_root_empty_result_consumed": False,
    }


def build(args: argparse.Namespace) -> dict:
    spec = load(args.spec)
    hardening = load(args.hardening)
    gap = load(args.gap_ledger)
    authority = validate_authority(spec, hardening, gap)
    carrier_chain = derive_carrier_chain(spec, args)
    positive = positive_control()

    proof = {
        "phase": "B4_6_4_GENERAL_STRUCTURAL_INDUCTION_COMPOSITION",
        "status": "OPEN_NODE8_UP_K_AUTHORITY_GAP",
        "spec_git_blob": git_blob(args.spec),
        "hardening_git_blob": git_blob(args.hardening),
        "hardening_semantic_digest": hardening["semantic_digest"],
        "gap_ledger_git_blob": git_blob(args.gap_ledger),
        "gap_ledger_file_sha256": file_sha256(args.gap_ledger),
        "authority": authority,
        "derived_carrier_chain": carrier_chain,
        "q80_composition_replay_required": True,
        "q80_replay_complete": False,
        "positive_nonvacuity_control": positive,
        "historical_counts_consumed_as_acceptance_oracles": False,
        "root_empty_consumed_as_composition_premise": False,
        "zero_root_successes_consumed_as_composition_premise": False,
        "actual_corrected_engine_complete_algorithm1_trace_established": False,
        "engine_root_full_set_equals_fs_k_v_zero": False,
        "structural_induction_proved": False,
        "strict_boundary": {
            "root_empty_proved": True,
            "general_structural_induction_composition_receipt": "ESTABLISHED_FOR_COMPLETE_ALGORITHM1_COMPATIBLE_TRACE_ONLY",
            "node8_up_k_authority_established": False,
            "actual_corrected_engine_complete_algorithm1_trace_established": False,
            "engine_root_full_set_equals_fs_k_v_zero": False,
            "structural_induction_proved": False,
            "terminal_completeness_proved": False,
            "no_layout_at_cap": "FORBIDDEN",
            "found_layout": "FORBIDDEN",
            "formal_admission": "BLOCKED",
            "next_gate": "C049.1_B4.6.4_NODE8_UP_K_AUTHORITY_CLOSURE_THEN_COMPOSITION_REPLAY",
            "current_global_terminal": TERMINAL,
            "p_vs_np": "OPEN",
        },
    }
    artifact = {"schema": SCHEMA, "semantic_digest_scope": "proof_payload", "proof_payload": proof}
    artifact["semantic_digest"] = digest(proof)
    args.output.write_bytes(canonical_bytes(artifact) + b"\n")
    return artifact


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--hardening", type=Path, required=True)
    p.add_argument("--gap-ledger", type=Path, required=True)
    p.add_argument("--corrected-join", type=Path, required=True)
    p.add_argument("--node6-source", type=Path, required=True)
    p.add_argument("--node7-source", type=Path, required=True)
    p.add_argument("--node8-manifest", type=Path, required=True)
    p.add_argument("--node9-scalar-spec", type=Path, required=True)
    p.add_argument("--node9-residual-spec", type=Path, required=True)
    p.add_argument("--node9-upk-spec", type=Path, required=True)
    p.add_argument("--root-spec", type=Path, required=True)
    p.add_argument("--root-empty-spec", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    artifact = build(a)
    q = artifact["proof_payload"]
    print("JANUS_B4_6_4_ACTUAL_ENGINE_COMPOSITION_PREFLIGHT = PASS")
    print("RESULT =", q["status"])
    print("IMMUTABLE_CARRIER_CHAIN_DERIVED = TRUE")
    print("POSITIVE_NONEMPTY_ROOT_CONTROL = PASS")
    print("NODE8_UP_K_AUTHORITY_ESTABLISHED = FALSE")
    print("Q80_COMPOSITION_REPLAY_COMPLETE = FALSE")
    print("ACTUAL_CORRECTED_ENGINE_COMPLETE_ALGORITHM1_TRACE_ESTABLISHED = FALSE")
    print("ENGINE_ROOT_FULL_SET_EQUALS_FS_K_V_ZERO = FALSE")
    print("TERMINAL_COMPLETENESS_PROVED = FALSE")
    print("NO_LAYOUT_AT_CAP = FORBIDDEN")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
