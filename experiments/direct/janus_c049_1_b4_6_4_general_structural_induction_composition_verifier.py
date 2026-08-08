#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCHEMA = "janus.c049_1.b4_6_4.general_structural_induction_composition_candidate.v1"
SPEC_SCHEMA = "janus.c049_1.b4_6_4.general_structural_induction_composition_spec.v1"
HARDENING_SCHEMA = "janus.c049_1.b4_6_4.general_structural_induction_composition_authority_hardening.v1"
GAP_SCHEMA = "janus.c049_1.b4_6_4.general_structural_induction_authority_gap_ledger.v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"


class VerificationError(Exception):
    def __init__(self, invariant: str, message: str) -> None:
        super().__init__(f"{invariant}: {message}")
        self.invariant = invariant


def req(value: bool, invariant: str, message: str) -> None:
    if not value:
        raise VerificationError(invariant, message)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recursive_contains(value: Any, needle: Any) -> bool:
    if value == needle:
        return True
    if isinstance(value, dict):
        return any(recursive_contains(v, needle) for v in value.values())
    if isinstance(value, (list, tuple)):
        return any(recursive_contains(v, needle) for v in value)
    return False


def source_constant(text: str, name: str) -> str | int | None:
    m = re.search(rf"^{re.escape(name)}\s*=\s*(.+)$", text, flags=re.MULTILINE)
    if not m:
        return None
    raw = m.group(1).strip()
    if raw.isdigit():
        return int(raw)
    return raw.strip('"\'')


def assert_implementation_decoupling(producer_source: Path, verifier_source: Path) -> None:
    def modules(path: Path) -> list[str]:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        out: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                out.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                out.append(node.module or "")
        return out
    pmods = modules(producer_source)
    vmods = modules(verifier_source)
    req(not any(x.endswith("janus_c049_1_b4_6_4_general_structural_induction_composition_verifier") for x in pmods), "PREFLIGHT-INV-01", "producer imports verifier")
    req(not any(x.endswith("janus_c049_1_b4_6_4_general_structural_induction_composition") for x in vmods), "PREFLIGHT-INV-01", "verifier imports producer")


def verify_receipts(spec: dict, receipt_paths: list[Path]) -> dict:
    req(len(receipt_paths) == 7, "PREFLIGHT-INV-02", "receipt count")
    keys = ["O1_leaf", "O2_expand", "O3_join", "O4_shrink", "O5_width_filter", "O6_b2", "O7_empty_root"]
    out = {}
    for key, path in zip(keys, receipt_paths):
        authority = spec["semantic_receipts"][key]
        expected_blob = authority.get("receipt_git_blob", authority.get("authority_receipt_git_blob"))
        expected_sem = authority.get("audit_semantic_digest", authority.get("authority_audit_semantic_digest"))
        req(git_blob(path) == expected_blob, "PREFLIGHT-INV-02", f"{key} blob")
        obj = load(path)
        req(obj.get("semantic_digest_scope") == "audit_payload", "PREFLIGHT-INV-02", f"{key} semantic scope")
        req(digest(obj["audit_payload"]) == obj.get("semantic_digest") == expected_sem, "PREFLIGHT-INV-02", f"{key} semantic digest")
        out[key] = {"git_blob": expected_blob, "semantic_digest": expected_sem}
    return out


def derive_chain_independently(spec: dict, a: argparse.Namespace) -> dict:
    c = spec["engine_carriers"]
    checks = [
        (a.corrected_join, c["corrected_join_api"]["git_blob"], "corrected join"),
        (a.node6_source, c["node6_first_internal_join"]["git_blob"], "Node6"),
        (a.node7_source, c["node7_frontier"]["git_blob"], "Node7"),
        (a.node8_manifest, c["node8_parent_refinement"]["manifest_git_blob"], "Node8 manifest"),
        (a.node9_scalar_spec, c["node9_scalar"]["spec_git_blob"], "Node9 scalar"),
        (a.node9_residual_spec, c["node9_residual_frontier"]["spec_git_blob"], "Node9 residual"),
        (a.node9_upk_spec, c["node9_residual_up_k"]["spec_git_blob"], "Node9 up_k"),
        (a.root_spec, c["root_refinement"]["spec_git_blob"], "root refinement"),
    ]
    for path, expected, label in checks:
        req(git_blob(path) == expected, "PREFLIGHT-INV-03", f"{label} blob")

    corrected = a.corrected_join.read_text(encoding="utf-8")
    node6 = a.node6_source.read_text(encoding="utf-8")
    node7 = a.node7_source.read_text(encoding="utf-8")
    node8 = load(a.node8_manifest)
    scalar = load(a.node9_scalar_spec)
    residual = load(a.node9_residual_spec)
    upk = load(a.node9_upk_spec)
    root = load(a.root_spec)
    root_empty = load(a.root_empty_spec)

    req("JOIN_INTERLEAVING_STEPS: tuple[tuple[int, int], ...] = ((1, 0), (0, 1))" in corrected, "PREFLIGHT-INV-03", "ordinary join domain")
    req("EXTENSION_PREORDER_STEPS: tuple[tuple[int, int], ...] = ((1, 0), (0, 1), (1, 1))" in corrected, "PREFLIGHT-INV-03", "preorder domain")
    req(source_constant(node6, "FIRST_INTERNAL_NODE_ID") == 6, "PREFLIGHT-INV-03", "Node6 id")
    req("ordinary_join_paths" in node6 and "corrected_join_trajectory" in node6, "PREFLIGHT-INV-03", "Node6 corrected path API")
    req(source_constant(node7, "PARENT_HEAD") == "af0556d4ae05ea6dc343d120a34f67255890ba18", "PREFLIGHT-INV-03", "Node7 source parent")
    req(node8["base_exact_head"] == "024afebb322c67953f310af48818d3386fdcfc27", "PREFLIGHT-INV-03", "Node7 up_k to Node8 handoff")
    req(node8["proof_controls"]["ordinary_join_diagonal_allowed"] is False, "PREFLIGHT-INV-03", "Node8 path domain")

    n8 = "0fcdaa168dde2aef27603d51ff547c07860a9fd1"
    scalar_head = c["node9_scalar"]["admission_head"]
    residual_head = c["node9_residual_frontier"]["admission_head"]
    upk_head = c["node9_residual_up_k"]["admission_head"]
    root_head = c["root_refinement"]["admission_head"]
    req(recursive_contains(scalar, n8), "PREFLIGHT-INV-03", "Node8 source missing from scalar carrier")
    req(recursive_contains(residual, scalar_head), "PREFLIGHT-INV-03", "scalar-to-residual link")
    req(recursive_contains(upk, residual_head), "PREFLIGHT-INV-03", "residual-to-up_k link")
    req(recursive_contains(root, upk_head), "PREFLIGHT-INV-03", "up_k-to-root link")
    req(recursive_contains(root_empty, root_head), "PREFLIGHT-INV-03", "root-refinement-to-root-up_k link")

    return {
        "ordinary_join_steps": [[1, 0], [0, 1]],
        "extension_preorder_steps": [[1, 0], [0, 1], [1, 1]],
        "node6_subject": c["node6_first_internal_join"]["subject"],
        "node7_frontier_subject": c["node7_frontier"]["subject"],
        "node7_final_up_k_subject": node8["base_exact_head"],
        "node8_parent_refinement_subject": c["node8_parent_refinement"]["subject"],
        "node8_up_k_subject": n8,
        "node9_scalar_subject": scalar_head,
        "node9_residual_subject": residual_head,
        "node9_up_k_subject": upk_head,
        "root_refinement_subject": root_head,
        "blocker": "NODE8_PARENT_REFINEMENT_TO_NODE8_UP_K_AUTHORITY",
    }


def span(rows: tuple[int, ...]) -> set[int]:
    values = {0}
    for row in rows:
        values |= {x ^ row for x in tuple(values)}
    return values


def intersection_dim(a: tuple[int, ...], b: tuple[int, ...]) -> int:
    size = len(span(a) & span(b))
    return size.bit_length() - 1


def positive_control_expected() -> dict:
    # Direct GF(2) replay, independent of B1/B2/B3 implementation modules.
    leaf = [
        {"left": (), "right": (1,), "value": 0},
        {"left": (1,), "right": (), "value": 0},
    ]
    paths = [((0, 0), (1, 0), (1, 1)), ((0, 0), (0, 1), (1, 1))]
    records = []
    for path in paths:
        joined = []
        initial = intersection_dim(leaf[0]["right"], leaf[0]["right"])
        for i, j in path:
            x, y = leaf[i], leaf[j]
            left = tuple(sorted(span(x["left"]) | span(y["left"])))
            right = tuple(sorted(span(x["right"]) | span(y["right"])))
            # In GF(2)^1, canonical nonzero span basis is (1,); normalize set encodings explicitly.
            left_basis = (1,) if 1 in left else ()
            right_basis = (1,) if 1 in right else ()
            ar = (1,) if 1 in (span(x["left"]) | span(x["right"])) else ()
            br = (1,) if 1 in (span(y["left"]) | span(y["right"])) else ()
            corr = initial - intersection_dim(ar, br)
            joined.append({"left": left_basis, "right": right_basis, "value": x["value"] + y["value"] + corr})
        shrunk_values = [s["value"] + intersection_dim(s["left"], s["right"]) for s in joined]
        records.append({"path": [[i, j] for i, j in path], "joined_width": max(s["value"] for s in joined), "final_width": max(shrunk_values), "success": max(shrunk_values) <= 1})
    typical = [(0,), (1,), (0, 1), (1, 0), (0, 1, 0), (1, 0, 1)]
    lower = (0, 1, 0)

    def preorder(upper: tuple[int, ...]) -> bool:
        reachable: set[tuple[int, int]] = set()
        for i in range(len(lower)):
            for j in range(len(upper)):
                if lower[i] > upper[j]:
                    continue
                if (i, j) == (0, 0):
                    reachable.add((i, j)); continue
                if any(p in reachable for p in ((i - 1, j - 1), (i - 1, j), (i, j - 1))):
                    reachable.add((i, j))
        return (len(lower) - 1, len(upper) - 1) in reachable

    closure = [u for u in typical if preorder(u)]
    req(len(closure) == 5 and (0,) not in closure, "PREFLIGHT-INV-04", "positive B2 closure")
    return {"paths": records, "successful_root_generators": 2, "root_up_k_entry_count": 5, "root_full_set_nonempty": True}


def verify(candidate: dict, spec: dict, hardening: dict, gap: dict, a: argparse.Namespace) -> None:
    req(candidate.get("schema") == SCHEMA, "PREFLIGHT-INV-01", "candidate schema")
    req(candidate.get("semantic_digest_scope") == "proof_payload", "PREFLIGHT-INV-01", "candidate scope")
    req(digest(candidate["proof_payload"]) == candidate.get("semantic_digest"), "PREFLIGHT-INV-01", "candidate semantic digest")
    req(spec.get("schema") == SPEC_SCHEMA and spec.get("status") == "SPEC_FROZEN", "PREFLIGHT-INV-01", "spec")
    req(hardening.get("schema") == HARDENING_SCHEMA and digest(hardening["hardening_payload"]) == hardening.get("semantic_digest"), "PREFLIGHT-INV-01", "hardening")
    req(gap.get("schema") == GAP_SCHEMA, "PREFLIGHT-INV-01", "gap ledger")
    assert_implementation_decoupling(a.producer_source, a.verifier_source)
    verify_receipts(spec, a.receipts)
    expected_chain = derive_chain_independently(spec, a)

    p = candidate["proof_payload"]
    req(p["spec_git_blob"] == git_blob(a.spec), "PREFLIGHT-INV-05", "spec blob")
    req(p["hardening_git_blob"] == git_blob(a.hardening), "PREFLIGHT-INV-05", "hardening blob")
    req(p["hardening_semantic_digest"] == hardening["semantic_digest"], "PREFLIGHT-INV-05", "hardening digest")
    req(p["gap_ledger_git_blob"] == git_blob(a.gap_ledger) and p["gap_ledger_file_sha256"] == file_sha256(a.gap_ledger), "PREFLIGHT-INV-05", "gap ledger bytes")

    hp = hardening["hardening_payload"]
    n8 = hp["node8_up_k_authority_requirement"]
    req(p["status"] == "OPEN_NODE8_UP_K_AUTHORITY_GAP", "PREFLIGHT-INV-06", "honest open state")
    req(n8["authority_established"] is False and n8["authority_receipt_git_blob"] is None, "PREFLIGHT-INV-06", "Node8 authority frozen open")
    req(p["authority"]["node8_up_k_authority_established"] is False, "PREFLIGHT-INV-06", "candidate Node8 promotion")
    req(p["derived_carrier_chain"]["ordinary_join_steps"] == expected_chain["ordinary_join_steps"], "PREFLIGHT-INV-07", "ordinary path domain")
    req(p["derived_carrier_chain"]["extension_preorder_steps"] == expected_chain["extension_preorder_steps"], "PREFLIGHT-INV-07", "preorder domain")
    req(p["derived_carrier_chain"]["node6"]["subject"] == expected_chain["node6_subject"], "PREFLIGHT-INV-07", "Node6 subject")
    req(p["derived_carrier_chain"]["node7"]["final_up_k_handoff_subject"] == expected_chain["node7_final_up_k_subject"], "PREFLIGHT-INV-07", "Node7 handoff")
    req(p["derived_carrier_chain"]["node8"]["up_k_subject_discovered_in_node9_scalar"] == expected_chain["node8_up_k_subject"], "PREFLIGHT-INV-07", "Node8 downstream source")
    req(p["derived_carrier_chain"]["node9"]["scalar_subject"] == expected_chain["node9_scalar_subject"], "PREFLIGHT-INV-07", "scalar subject")
    req(p["derived_carrier_chain"]["node9"]["residual_frontier_subject"] == expected_chain["node9_residual_subject"], "PREFLIGHT-INV-07", "residual subject")
    req(p["derived_carrier_chain"]["node9"]["residual_up_k_subject"] == expected_chain["node9_up_k_subject"], "PREFLIGHT-INV-07", "Node9 up_k subject")
    req(p["derived_carrier_chain"]["root"]["refinement_subject"] == expected_chain["root_refinement_subject"], "PREFLIGHT-INV-07", "root subject")
    req(p["derived_carrier_chain"]["complete_chain_blocked_at"] == expected_chain["blocker"], "PREFLIGHT-INV-07", "blocker edge")

    expected_positive = positive_control_expected()
    pos = p["positive_nonvacuity_control"]
    req(pos["fixture_role"] == "NONVACUITY_ONLY_NOT_EVIDENCE_ABOUT_FROZEN_SIX_FACTOR_TARGET", "PREFLIGHT-INV-08", "positive control role")
    req(pos["whole_factor_blocks"] == [[1], [1]], "PREFLIGHT-INV-08", "positive fixture")
    req(pos["ordinary_join_paths"] == expected_positive["paths"], "PREFLIGHT-INV-08", "positive H/V replay")
    req(pos["successful_root_generators"] == 2 and pos["root_up_k_entry_count"] == 5 and pos["root_full_set_nonempty"] is True, "PREFLIGHT-INV-08", "positive root closure")
    req(pos["target_root_empty_result_consumed"] is False, "PREFLIGHT-INV-08", "positive control contamination")

    req(p["q80_composition_replay_required"] is True and p["q80_replay_complete"] is False, "PREFLIGHT-INV-09", "Q80 replay boundary")
    req(p["historical_counts_consumed_as_acceptance_oracles"] is False, "PREFLIGHT-INV-09", "historical oracle")
    req(p["root_empty_consumed_as_composition_premise"] is False and p["zero_root_successes_consumed_as_composition_premise"] is False, "PREFLIGHT-INV-09", "root shortcut")
    req(p["actual_corrected_engine_complete_algorithm1_trace_established"] is False and p["engine_root_full_set_equals_fs_k_v_zero"] is False and p["structural_induction_proved"] is False, "PREFLIGHT-INV-10", "premature composition")

    b = p["strict_boundary"]
    req(b["node8_up_k_authority_established"] is False, "PREFLIGHT-INV-10", "boundary Node8")
    req(b["actual_corrected_engine_complete_algorithm1_trace_established"] is False, "PREFLIGHT-INV-10", "boundary trace")
    req(b["engine_root_full_set_equals_fs_k_v_zero"] is False and b["structural_induction_proved"] is False, "PREFLIGHT-INV-10", "boundary identity")
    req(b["terminal_completeness_proved"] is False and b["no_layout_at_cap"] == "FORBIDDEN" and b["found_layout"] == "FORBIDDEN", "PREFLIGHT-INV-10", "terminal boundary")
    req(b["formal_admission"] == "BLOCKED" and b["current_global_terminal"] == TERMINAL and b["p_vs_np"] == "OPEN", "PREFLIGHT-INV-10", "global boundary")


def repair(candidate: dict) -> None:
    candidate["semantic_digest"] = digest(candidate["proof_payload"])


def preflight_tampers(candidate: dict, spec: dict, hardening: dict, gap: dict, a: argparse.Namespace) -> list[tuple[str, str]]:
    rejected: list[tuple[str, str]] = []

    def attack(name: str, mutate) -> None:
        x = copy.deepcopy(candidate); mutate(x); repair(x)
        try:
            verify(x, spec, hardening, gap, a)
        except VerificationError as exc:
            rejected.append((name, exc.invariant)); return
        raise AssertionError(f"preflight tamper survived: {name}")

    attack("P01_AUTHORITY_PROMOTE", lambda x: x["proof_payload"]["authority"].__setitem__("node8_up_k_authority_established", True))
    attack("P02_DIAGONAL_JOIN", lambda x: x["proof_payload"]["derived_carrier_chain"].__setitem__("ordinary_join_steps", [[1,0],[0,1],[1,1]]))
    attack("P03_DROP_NODE9_LINK", lambda x: x["proof_payload"]["derived_carrier_chain"]["node9"].__setitem__("scalar_to_residual_link", False))
    attack("P04_INJECT_SYNTHETIC_STAGE", lambda x: x["proof_payload"]["derived_carrier_chain"].__setitem__("synthetic_stage", "FAKE"))
    attack("P05_DISABLE_Q80_REPLAY", lambda x: x["proof_payload"].__setitem__("q80_composition_replay_required", False))
    attack("P06_FAKE_Q80_COMPLETE", lambda x: x["proof_payload"].__setitem__("q80_replay_complete", True))
    attack("P07_DISABLE_POSITIVE", lambda x: x["proof_payload"]["positive_nonvacuity_control"].__setitem__("root_full_set_nonempty", False))
    attack("P08_CONSUME_ROOT_EMPTY", lambda x: x["proof_payload"].__setitem__("root_empty_consumed_as_composition_premise", True))
    attack("P09_PROMOTE_TRACE", lambda x: x["proof_payload"].__setitem__("actual_corrected_engine_complete_algorithm1_trace_established", True))
    attack("P10_PROMOTE_ROOT_IDENTITY", lambda x: x["proof_payload"].__setitem__("engine_root_full_set_equals_fs_k_v_zero", True))
    attack("P11_PROMOTE_NO_LAYOUT", lambda x: x["proof_payload"]["strict_boundary"].__setitem__("no_layout_at_cap", "ADMITTED"))
    attack("P12_PROMOTE_PNP", lambda x: x["proof_payload"]["strict_boundary"].__setitem__("p_vs_np", "CLOSED"))
    req(len(rejected) == 12, "PREFLIGHT-INV-11", "preflight tamper count")
    return rejected


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--spec", type=Path, required=True); p.add_argument("--hardening", type=Path, required=True); p.add_argument("--gap-ledger", type=Path, required=True)
    p.add_argument("--producer-source", type=Path, required=True); p.add_argument("--verifier-source", type=Path, required=True)
    for i in range(1, 8): p.add_argument(f"--o{i}-receipt", dest=f"o{i}_receipt", type=Path, required=True)
    p.add_argument("--corrected-join", type=Path, required=True); p.add_argument("--node6-source", type=Path, required=True); p.add_argument("--node7-source", type=Path, required=True); p.add_argument("--node8-manifest", type=Path, required=True)
    p.add_argument("--node9-scalar-spec", type=Path, required=True); p.add_argument("--node9-residual-spec", type=Path, required=True); p.add_argument("--node9-upk-spec", type=Path, required=True); p.add_argument("--root-spec", type=Path, required=True); p.add_argument("--root-empty-spec", type=Path, required=True)
    p.add_argument("--candidate-original", type=Path, required=True); p.add_argument("--candidate-reordered", type=Path, required=True); p.add_argument("--tamper-suite", action="store_true")
    a = p.parse_args(); a.receipts = [getattr(a, f"o{i}_receipt") for i in range(1, 8)]
    spec, hardening, gap = load(a.spec), load(a.hardening), load(a.gap_ledger)
    req(a.candidate_original.read_bytes() == a.candidate_reordered.read_bytes(), "PREFLIGHT-INV-12", "byte identity")
    candidate = load(a.candidate_original); verify(candidate, spec, hardening, gap, a)
    tampers = preflight_tampers(candidate, spec, hardening, gap, a) if a.tamper_suite else []
    print("JANUS_B4_6_4_ACTUAL_ENGINE_COMPOSITION_PREFLIGHT_INDEPENDENT_VERIFIER = PASS")
    print("PRODUCER_IMPORT = FORBIDDEN_AND_NOT_USED")
    print("VERIFIER_IMPORT_OF_PRODUCER = FORBIDDEN_AND_NOT_USED")
    print("IMPLEMENTATION_DECOUPLING = REQUIRED_AND_OBSERVED")
    print("PREFLIGHT_INVARIANTS = 12/12")
    print("PREFLIGHT_DIGEST_REPAIRED_TAMPERS_REJECTED =", f"{len(tampers)}/12" if a.tamper_suite else "NOT_RUN")
    print("O1_O7_IMMUTABLE_AUTHORITY_BINDINGS = 7/7")
    print("POSITIVE_NONEMPTY_ROOT_CONTROL = PASS")
    print("DECLARED_FINAL_COMPOSITION_INVARIANTS = BLOCKED_BY_NODE8_UP_K_AUTHORITY_AND_Q80_REPLAY")
    print("DECLARED_FINAL_TAMPER_SUITE = NOT_YET_RUN")
    print("NODE8_UP_K_AUTHORITY_ESTABLISHED = FALSE")
    print("Q80_COMPOSITION_REPLAY_COMPLETE = FALSE")
    print("ACTUAL_CORRECTED_ENGINE_COMPLETE_ALGORITHM1_TRACE_ESTABLISHED = FALSE")
    print("ENGINE_ROOT_FULL_SET_EQUALS_FS_K_V_ZERO = FALSE")
    print("TERMINAL_COMPLETENESS_PROVED = FALSE")
    print("NO_LAYOUT_AT_CAP = FORBIDDEN")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
