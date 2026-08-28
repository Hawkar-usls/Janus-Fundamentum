#!/usr/bin/env python3
"""Independent no-import admission verifier for the C025 L1/39100 receipt.

This module intentionally imports no producer or theorem-engine module.  It
checks the composite as data, recomputes hashes from the checkout and exercises
semantic tamper rejection before it may emit ADMITTED.
"""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Callable

P_VS_NP = "OPEN"
SOURCE_FP = "bc07cfeb7d1ef62916d7319ed59edc8d2e4a92ce34881a13186d2c47991c66bc"
PRODUCT_FP = "037cbc224816408ca1c76c65c9bb78ad660d3b612c40ef91d1ac76943c7c79c3"
N = 1102
CAP = 1_214_404
ROOTS = list(range(2, 22))
PAIR_COUNT = 744
ROUTE_COUNT = 14_880
VERIFIER_PATH = Path("experiments/theorem_extraction/c025_l1_39100_admission_verifier.py")
EXPECTED_SOURCE_PATHS = {
    "experiments/theorem_extraction/c025_l1_39100_promotion_gate.py",
    "experiments/theorem_extraction/c025_l1_39100_admission_verifier.py",
    "experiments/theorem_extraction/c025_l1_uniform_exact_checker.cpp",
    "experiments/theorem_extraction/c025_uniform_exact_checker_general.cpp",
    "experiments/theorem_extraction/c025_l1_fanout_exact_gate.py",
    "experiments/direct/janus_pirc_decision_core_v0_4.py",
    "experiments/direct/janus_unified_macro_restore_v2.py",
    "experiments/direct/janus_unified_proof_carrying_akinator_jec.py",
    "research/C025_L1_39100_EXACT_COUNTEREXAMPLE_PROMOTION_GATE_2026-08-28.json",
    "research/C025_L1_39100_UNIFORM_V2_SEMANTIC_EQUIVALENCE_LEMMA_2026-08-28.json",
    ".github/workflows/validate-c025-l1-39100-promotion.yml",
}
EXPECTED_IMMUTABLE_RECEIPTS = {
    "research/C025_ROOSTERS_V5_1_THEOREM_INTEGRATION_TEST_RESULT_2026-08-28.json": "f7abce3eeef0d531dfbd5bedc527df4ab9970d9acc3072fca8eed291bbdae328",
    "research/C025_L1_39100_COUNTEREXAMPLE_CANDIDATE_PENDING_FROZEN_CALLSITE_2026-08-28.json": "542656965eecd016f88d8f0bf3ff58e24111d6a680defa9974b6a9907ccc6215",
    "research/C025_ROOSTERS_THEOREM_GOVERNANCE_V1_2_2026-08-28.json": "123ca3a8f6f71b2394f8532af8c28f10d7783bd0bf8f6e9a855e7f0e56eabe04",
}
EXPECTED_EVIDENCE_PATHS = {
    "c025-l1-39100-identity/identity.json",
    "c025-l1-39100-identity/product.txt",
    *{f"c025-l1-39100-ordinary-{i}/ordinary-{i}.json" for i in range(8)},
    "c025-l1-39100-gamma/gamma.json",
    "c025-l1-39100-gamma/gamma-independent.json",
    "c025-l1-39100-gamma/gamma-general.json",
    "c025-l1-39100-gamma/checker-independent",
    "c025-l1-39100-gamma/checker-general",
    "c025-l1-39100-reachability/reachability.json",
    *{f"c025-l1-39100-original-v2-{i}/original-v2-{i}.json" for i in range(64)},
}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def committed_sha256(commit: str, path: str) -> str | None:
    try:
        payload = subprocess.check_output(
            ["git", "show", f"{commit}:{path}"],
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return sha256_bytes(payload)


def expect(condition: bool, label: str, errors: list[str]) -> None:
    if not condition:
        errors.append(label)


def project_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend(alias.name for alias in node.names if alias.name == "experiments" or alias.name.startswith("experiments."))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "experiments" or module.startswith("experiments."):
                found.append(module)
    return sorted(found)


def validate(
    receipt: dict[str, Any],
    *,
    expected_repository: str,
    expected_commit: str,
    expected_branch: str,
    check_checkout: bool,
    evidence_dir: Path | None = None,
) -> list[str]:
    errors: list[str] = []
    expect(receipt.get("schema") == "JANUS/C025/L1-39100-EXACT-COUNTEREXAMPLE/COMPOSITE/v1", "SCHEMA", errors)
    expect(receipt.get("production_state") == "EXACT_COUNTEREXAMPLE_PRODUCED__INDEPENDENT_ADMISSION_REQUIRED", "PRODUCTION_STATE", errors)
    semantic = receipt.get("semantic_receipt", {})
    expect(receipt.get("semantic_sha256") == sha256_bytes(canonical_json_bytes(semantic)), "SEMANTIC_DIGEST", errors)

    subject = semantic.get("subject", {})
    expect(subject.get("repository") == expected_repository, "REPOSITORY_IDENTITY", errors)
    expect(subject.get("commit") == expected_commit, "COMMIT_IDENTITY", errors)
    expect(subject.get("branch") == expected_branch, "BRANCH_IDENTITY", errors)
    expect(subject.get("fixed_algorithm") == "PIRC_DECISION_CORE_V0_4", "ALGORITHM_IDENTITY", errors)

    candidate = semantic.get("candidate", {})
    expect(candidate.get("source_fingerprint") == SOURCE_FP, "SOURCE_FINGERPRINT", errors)
    expect(candidate.get("product_fingerprint") == PRODUCT_FP, "PRODUCT_FINGERPRINT", errors)
    expect(candidate.get("source_canonical_sha256") == SOURCE_FP, "SOURCE_CANONICAL_HASH", errors)
    expect(candidate.get("product_canonical_sha256") == PRODUCT_FP, "PRODUCT_CANONICAL_HASH", errors)
    expect(candidate.get("N") == N and candidate.get("cap") == CAP, "N_CAP", errors)
    expect(candidate.get("product_units") == 72_901 and candidate.get("product_clauses") == 8_100, "PRODUCT_SIZE", errors)
    expect(candidate.get("live_roots") == ROOTS and candidate.get("live_root_count") == len(ROOTS), "ROOT_SET", errors)
    expect(candidate.get("v2_pair_count") == PAIR_COUNT and candidate.get("pair_root_route_count") == ROUTE_COUNT, "GRAMMAR_SCOPE", errors)

    reachability = semantic.get("reachability", {})
    expect(reachability.get("exact") is True, "REACHABILITY_EXACT", errors)
    expect(reachability.get("reachable_at_frozen_ordinary_callsite") is True, "REACHABILITY_CALLSITE", errors)
    expect(reachability.get("selector_pivot_1_exact_product") is True, "SELECTOR_TRANSITION", errors)
    reach_receipt = reachability.get("receipt", {})
    expect(reach_receipt.get("status") == "PASS" and reach_receipt.get("unmodified_core_prefix") is True, "REACHABILITY_RECEIPT", errors)

    delta = semantic.get("Delta", {})
    rows = delta.get("rows", [])
    expect(delta.get("strictly_positive") is True and delta.get("original_eliminate_var_capped") is True, "DELTA_AUTHORITY", errors)
    expect(delta.get("pivot_count") == len(ROOTS), "DELTA_PIVOT_COUNT", errors)
    expect(delta.get("covered_pivot_indices") == list(range(len(ROOTS))), "DELTA_COVERAGE", errors)
    expect(len(rows) == len(ROOTS), "DELTA_ROW_COUNT", errors)
    if len(rows) == len(ROOTS):
        expect([row.get("pivot") for row in rows] == ROOTS, "DELTA_PIVOT_ORDER", errors)
        expect([row.get("pivot_index") for row in rows] == list(range(len(ROOTS))), "DELTA_INDEX_ORDER", errors)
        expect(all(row.get("overflow") is True for row in rows), "DELTA_ALL_OVERFLOW", errors)
        expect(all(int(row.get("stats", {}).get("raw_units", -1)) > CAP for row in rows), "DELTA_CAP_CROSSINGS", errors)
    expect(int(delta.get("minimum_observed_first_crossing_margin", -1)) > 0, "DELTA_POSITIVE_MARGIN", errors)
    expect(delta.get("first_crossing_margin_is_not_promoted_to_exact_Delta_value") is True, "DELTA_MARGIN_BOUNDARY", errors)

    gamma = semantic.get("Gamma", {})
    expect(gamma.get("strictly_positive_by_complete_cap_crossing") is True, "GAMMA_AUTHORITY", errors)
    expect(gamma.get("candidate_pair_count") == PAIR_COUNT, "GAMMA_PAIR_COUNT", errors)
    expect(gamma.get("root_count_per_pair") == len(ROOTS), "GAMMA_ROOT_COUNT", errors)
    expect(gamma.get("complete_pair_root_scope") == ROUTE_COUNT, "GAMMA_ROUTE_SCOPE", errors)
    expect(gamma.get("first_exact_rescue") is None, "GAMMA_RESCUE_ABSENT", errors)
    expect(gamma.get("backend_verdicts_agree") is True, "GAMMA_BACKEND_AGREEMENT", errors)
    expect(gamma.get("parent_order_independent_fit_verdict") is True, "GAMMA_ORDER_INVARIANCE", errors)
    for backend_name in ("independent_backend", "general_backend"):
        backend = gamma.get(backend_name, {})
        expected_schema = {
            "independent_backend": "JANUS/C025/L1-UNIFORM-INDEPENDENT-EXACT-CHECKER/v1",
            "general_backend": "JANUS/C025/GENERAL-UNIFORM-EXACT-V2-CHECKER/v1",
        }[backend_name]
        expect(backend.get("schema") == expected_schema, f"{backend_name.upper()}_SCHEMA", errors)
        expect(backend.get("status") == "COMPLETE_NO_V2_RESCUE", f"{backend_name.upper()}_STATUS", errors)
        expect(backend.get("pair_count") == PAIR_COUNT and backend.get("root_count") == len(ROOTS), f"{backend_name.upper()}_SCOPE", errors)
        expect(backend.get("route_count") == ROUTE_COUNT and backend.get("rescue") is None, f"{backend_name.upper()}_COMPLETE", errors)
        expect(int(backend.get("minimum_first_crossing_margin", -1)) > 0, f"{backend_name.upper()}_CAP", errors)

    original_v2 = semantic.get("original_frozen_v2", {})
    expect(original_v2.get("status") == "COMPLETE_ORIGINAL_FROZEN_V2_NO_RESCUE", "ORIGINAL_V2_STATUS", errors)
    expect(original_v2.get("shard_count") == 64, "ORIGINAL_V2_SHARD_COUNT", errors)
    expect(original_v2.get("candidate_pair_count") == PAIR_COUNT, "ORIGINAL_V2_PAIR_COUNT", errors)
    expect(original_v2.get("covered_candidate_indices") == list(range(PAIR_COUNT)), "ORIGINAL_V2_COVERAGE", errors)
    expect(original_v2.get("tested_pair_count") == PAIR_COUNT, "ORIGINAL_V2_TESTED", errors)
    expect(original_v2.get("first_exact_rescue") is None, "ORIGINAL_V2_RESCUE", errors)
    expect(original_v2.get("direct_state_is_exact_reached_callsite_state") is True, "ORIGINAL_V2_STATE_BINDING", errors)
    expect(all(original_v2.get(key) is True for key in (
        "uses_original_v2_candidate_generator",
        "uses_original_v2_apply_and_verify",
        "uses_original_capped_root_elimination",
        "uses_original_progress_gate",
    )), "ORIGINAL_V2_AUTHORITY", errors)

    equivalence = semantic.get("semantic_equivalence", {})
    pre = equivalence.get("preconditions", {})
    expect(pre.get("product_clause_count") == 8_100 and pre.get("product_widths") == [8], "EQUIV_PRODUCT_SHAPE", errors)
    expect(pre.get("product_unique") is True and pre.get("product_tautology_free") is True, "EQUIV_CANONICAL", errors)
    expect(pre.get("live_roots") == ROOTS and pre.get("fresh_extension") == 22 and pre.get("fresh_absent") is True, "EQUIV_VARIABLES", errors)
    expect(pre.get("candidate_pair_count") == PAIR_COUNT, "EQUIV_PAIR_SCOPE", errors)
    samples = equivalence.get("original_macro_equivalence_samples", [])
    expect([sample.get("pair_index") for sample in samples] == [0, 1, 10, 372, 743], "EQUIV_SAMPLE_INDICES", errors)
    expect(all(sample.get("original_certificate_verified") is True for sample in samples), "EQUIV_ORIGINAL_VERIFY", errors)
    boundary = equivalence.get("original_python_boundary_route", {})
    expect(boundary.get("pair_index") == 0 and boundary.get("pair") == [2, 3] and boundary.get("pivot") == 2, "BOUNDARY_ROUTE_IDENTITY", errors)
    expect(boundary.get("original_certificate_verified") is True and boundary.get("elimination_fit") is False, "BOUNDARY_ORIGINAL_RESULT", errors)
    expect(boundary.get("strict_cap_crossing") is True and int(boundary.get("elimination_stats", {}).get("raw_units", -1)) > CAP, "BOUNDARY_CAP", errors)
    controls = equivalence.get("positive_rescue_controls", [])
    expect([control.get("leaf_clauses") for control in controls] == [80, 88], "POSITIVE_CONTROL_IDENTITIES", errors)
    expect(all(control.get("status") == "EXACT_V2_RESCUE_FOUND" and control.get("rescue") is not None for control in controls), "POSITIVE_CONTROL_RESULTS", errors)

    provenance = receipt.get("provenance", {})
    evidence_hashes = provenance.get("evidence_file_sha256", {})
    source_hashes = provenance.get("source_file_sha256", {})
    immutable_hashes = provenance.get("immutable_parent_receipts", {})
    expect(set(evidence_hashes) == EXPECTED_EVIDENCE_PATHS, "EVIDENCE_MANIFEST_SCOPE", errors)
    expect(set(source_hashes) == EXPECTED_SOURCE_PATHS, "SOURCE_MANIFEST_SCOPE", errors)
    expect(immutable_hashes == EXPECTED_IMMUTABLE_RECEIPTS, "IMMUTABLE_MANIFEST", errors)
    expect(all(isinstance(value, str) and len(value) == 64 for value in evidence_hashes.values()), "EVIDENCE_HASH_FORMAT", errors)
    expect(all(isinstance(value, str) and len(value) == 64 for value in source_hashes.values()), "SOURCE_HASH_FORMAT", errors)

    backend_provenance = semantic.get("backend_provenance", {})
    backend_bindings = {
        "independent": (
            "experiments/theorem_extraction/c025_l1_uniform_exact_checker.cpp",
            "c025-l1-39100-gamma/checker-independent",
            "c025-l1-39100-gamma/gamma-independent.json",
            1,
        ),
        "general": (
            "experiments/theorem_extraction/c025_uniform_exact_checker_general.cpp",
            "c025-l1-39100-gamma/checker-general",
            "c025-l1-39100-gamma/gamma-general.json",
            4,
        ),
    }
    for name, (source_path, binary_path, raw_path, threads) in backend_bindings.items():
        backend = backend_provenance.get(name, {})
        expect(backend.get("source_path") == source_path, f"{name.upper()}_SOURCE_PATH", errors)
        expect(backend.get("source_sha256") == source_hashes.get(source_path), f"{name.upper()}_SOURCE_BINDING", errors)
        expect(backend.get("binary_sha256") == evidence_hashes.get(binary_path), f"{name.upper()}_BINARY_BINDING", errors)
        expect(backend.get("raw_receipt_sha256") == evidence_hashes.get(raw_path), f"{name.upper()}_RAW_BINDING", errors)
        expect(backend.get("execution_threads") == threads, f"{name.upper()}_SCHEDULE", errors)

    results = semantic.get("candidate_results", {})
    expect(results.get("L1_ROOT_PHASE_POLYNOMIAL_GRAMMAR_TOTALITY") == "REFUTED_BY_EXACT_REACHABLE_39100_COUNTEREXAMPLE", "L1_VERDICT", errors)
    boundary_claims = semantic.get("scientific_boundary", {})
    expect(boundary_claims.get("finite_witness_refutes_only_L1") is True, "CLAIM_SCOPE", errors)
    expect(boundary_claims.get("P2_REACHABLE_PRESERVATION") == "OPEN", "P2_BOUNDARY", errors)
    expect(boundary_claims.get("ROOT_FREE_V3_TAIL") == "OPEN", "V3_BOUNDARY", errors)
    expect(semantic.get("P_VS_NP") == P_VS_NP and receipt.get("P_VS_NP") == P_VS_NP, "P_VS_NP_BOUNDARY", errors)

    expect(provenance.get("old_unknown_or_pending_receipt_rewritten") is False, "APPEND_ONLY_LINEAGE", errors)
    expect(provenance.get("raw_ci_stdout_reconstructed") is False, "RAW_STDOUT_PROVENANCE", errors)
    expect(provenance.get("generation_modes", {}).get("Gamma_primary") == "independent_exact_CXX_backend_OMP1", "GAMMA_PRIMARY_MODE", errors)
    expect(provenance.get("generation_modes", {}).get("Gamma_replay") == "general_exact_CXX_backend_OMP4", "GAMMA_REPLAY_MODE", errors)

    if check_checkout:
        try:
            current_head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        except (OSError, subprocess.CalledProcessError):
            current_head = ""
        expect(current_head == expected_commit, "CHECKOUT_HEAD", errors)
        imports = project_imports(VERIFIER_PATH) if VERIFIER_PATH.is_file() else ["VERIFIER_MISSING"]
        expect(not imports, "VERIFIER_PROJECT_IMPORT", errors)
        for path_text, expected_hash in source_hashes.items():
            path = Path(path_text)
            expect(path.is_file() and sha256_file(path) == expected_hash, f"SOURCE_HASH:{path_text}", errors)
            expect(committed_sha256(expected_commit, path_text) == expected_hash, f"COMMITTED_SOURCE_HASH:{path_text}", errors)
        for path_text, expected_hash in immutable_hashes.items():
            path = Path(path_text)
            expect(path.is_file() and sha256_file(path) == expected_hash, f"IMMUTABLE_HASH:{path_text}", errors)
            expect(committed_sha256(expected_commit, path_text) == expected_hash, f"COMMITTED_IMMUTABLE_HASH:{path_text}", errors)
        expect(evidence_dir is not None and evidence_dir.is_dir(), "EVIDENCE_DIRECTORY", errors)
        if evidence_dir is not None and evidence_dir.is_dir():
            actual_paths = {str(path.relative_to(evidence_dir)) for path in evidence_dir.rglob("*") if path.is_file()}
            expect(actual_paths == EXPECTED_EVIDENCE_PATHS, "EVIDENCE_DIRECTORY_SCOPE", errors)
            for path_text, expected_hash in evidence_hashes.items():
                path = evidence_dir / path_text
                expect(path.is_file() and sha256_file(path) == expected_hash, f"EVIDENCE_HASH:{path_text}", errors)
            try:
                identity_raw = json.loads((evidence_dir / "c025-l1-39100-identity/identity.json").read_text(encoding="utf-8"))
                gamma_raw = json.loads((evidence_dir / "c025-l1-39100-gamma/gamma.json").read_text(encoding="utf-8"))
                independent_raw = json.loads((evidence_dir / "c025-l1-39100-gamma/gamma-independent.json").read_text(encoding="utf-8"))
                general_raw = json.loads((evidence_dir / "c025-l1-39100-gamma/gamma-general.json").read_text(encoding="utf-8"))
                reachability_raw = json.loads((evidence_dir / "c025-l1-39100-reachability/reachability.json").read_text(encoding="utf-8"))
                product_payload = (evidence_dir / "c025-l1-39100-identity/product.txt").read_bytes()
            except (OSError, json.JSONDecodeError):
                expect(False, "CORE_EVIDENCE_PARSE", errors)
            else:
                expect(identity_raw.get("status") == "EXACT_IDENTITY_PASS", "IDENTITY_STATUS", errors)
                expect(identity_raw.get("candidate") == candidate, "IDENTITY_CANDIDATE_BINDING", errors)
                expect(identity_raw.get("product_text_bytes") == len(product_payload), "PRODUCT_BYTES", errors)
                expect(identity_raw.get("product_text_sha256") == sha256_bytes(product_payload), "PRODUCT_SHA", errors)
                expect(gamma_raw.get("Gamma") == gamma, "GAMMA_RECEIPT_BINDING", errors)
                expect(gamma_raw.get("semantic_equivalence") == equivalence, "EQUIVALENCE_RECEIPT_BINDING", errors)
                expect(gamma_raw.get("backend_provenance") == backend_provenance, "BACKEND_RECEIPT_BINDING", errors)
                expect(reachability_raw == reach_receipt, "REACHABILITY_RECEIPT_BINDING", errors)
                expect(independent_raw.get("schema") == "JANUS/C025/L1-UNIFORM-INDEPENDENT-EXACT-CHECKER/v1", "INDEPENDENT_RAW_SCHEMA", errors)
                expect(independent_raw.get("status") == "COMPLETE_NO_V2_RESCUE", "INDEPENDENT_RAW_STATUS", errors)
                expect(independent_raw.get("candidate_pair_count") == PAIR_COUNT, "INDEPENDENT_RAW_PAIRS", errors)
                expect(independent_raw.get("root_pivot_count_per_pair") == len(ROOTS), "INDEPENDENT_RAW_ROOTS", errors)
                expect(independent_raw.get("checked_pair_pivot_scope") == ROUTE_COUNT, "INDEPENDENT_RAW_SCOPE", errors)
                expect(independent_raw.get("cap") == CAP and independent_raw.get("rescue") is None, "INDEPENDENT_RAW_RESULT", errors)
                expect(general_raw.get("schema") == "JANUS/C025/GENERAL-UNIFORM-EXACT-V2-CHECKER/v1", "GENERAL_RAW_SCHEMA", errors)
                expect(general_raw.get("status") == "COMPLETE_NO_V2_RESCUE", "GENERAL_RAW_STATUS", errors)
                expect(general_raw.get("candidate_pair_count") == PAIR_COUNT, "GENERAL_RAW_PAIRS", errors)
                expect(general_raw.get("root_pivot_count") == len(ROOTS), "GENERAL_RAW_ROOTS", errors)
                expect(general_raw.get("cap") == CAP and general_raw.get("rescue") is None, "GENERAL_RAW_RESULT", errors)

            ordinary_rows: list[dict[str, Any]] = []
            for shard_index in range(8):
                ordinary_path = evidence_dir / f"c025-l1-39100-ordinary-{shard_index}/ordinary-{shard_index}.json"
                try:
                    ordinary_receipt = json.loads(ordinary_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    expect(False, f"ORDINARY_PARSE:{shard_index}", errors)
                    continue
                expect(ordinary_receipt.get("shard") == {"index": shard_index, "count": 8}, f"ORDINARY_COORD:{shard_index}", errors)
                expect(ordinary_receipt.get("complete_for_selected_indices") is True, f"ORDINARY_COMPLETE:{shard_index}", errors)
                expect(ordinary_receipt.get("all_selected_overflow") is True, f"ORDINARY_OVERFLOW:{shard_index}", errors)
                expect(ordinary_receipt.get("candidate") == candidate, f"ORDINARY_CANDIDATE:{shard_index}", errors)
                ordinary_rows.extend(ordinary_receipt.get("rows", []))
            ordinary_rows.sort(key=lambda row: int(row.get("pivot_index", -1)))
            expect(ordinary_rows == rows, "ORDINARY_ROWS_BINDING", errors)
            original_covered: set[int] = set()
            for shard_index in range(64):
                shard_path = evidence_dir / f"c025-l1-39100-original-v2-{shard_index}/original-v2-{shard_index}.json"
                try:
                    shard = json.loads(shard_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    expect(False, f"ORIGINAL_V2_PARSE:{shard_index}", errors)
                    continue
                expected_indices = list(range(shard_index, PAIR_COUNT, 64))
                rows = shard.get("tested_rows", [])
                authority = shard.get("authority_boundary", {})
                candidate_shard = shard.get("candidate", {})
                expect(shard.get("schema") == "JANUS/C025/L1-FANOUT/V2-SHARD/v1", f"ORIGINAL_V2_SCHEMA:{shard_index}", errors)
                expect(shard.get("shard") == {"index": shard_index, "count": 64}, f"ORIGINAL_V2_COORD:{shard_index}", errors)
                expect(shard.get("status") == "SHARD_COMPLETE_NO_RESCUE", f"ORIGINAL_V2_COMPLETE:{shard_index}", errors)
                expect(shard.get("global_pair_count") == PAIR_COUNT, f"ORIGINAL_V2_GLOBAL:{shard_index}", errors)
                expect(shard.get("selected_pair_indices") == expected_indices, f"ORIGINAL_V2_SELECTED:{shard_index}", errors)
                expect([row.get("pair_index") for row in rows] == expected_indices, f"ORIGINAL_V2_ROWS:{shard_index}", errors)
                expect(shard.get("tested_count") == len(expected_indices), f"ORIGINAL_V2_TESTED:{shard_index}", errors)
                expect(shard.get("complete_for_selected_indices") is True and shard.get("rescue") is None, f"ORIGINAL_V2_NO_RESCUE:{shard_index}", errors)
                expect(candidate_shard.get("source_fingerprint") == SOURCE_FP and candidate_shard.get("product_fingerprint") == PRODUCT_FP, f"ORIGINAL_V2_FP:{shard_index}", errors)
                expect(candidate_shard.get("N") == N and candidate_shard.get("cap") == CAP, f"ORIGINAL_V2_CAP:{shard_index}", errors)
                expect(all(authority.get(key) is True for key in (
                    "original_v2_candidate_generator",
                    "original_v2_apply_verify",
                    "original_eliminate_var_capped_via_first_capped_elimination",
                    "original_progress_phi",
                )), f"ORIGINAL_V2_AUTHORITY:{shard_index}", errors)
                expect(all(row.get("macro_over_cap") is True or row.get("fitting_root_pivot") is None for row in rows), f"ORIGINAL_V2_ROOT_RESULT:{shard_index}", errors)
                original_covered.update(expected_indices)
            expect(original_covered == set(range(PAIR_COUNT)), "ORIGINAL_V2_BUNDLE_COVERAGE", errors)
    return errors


def refresh_semantic_digest(receipt: dict[str, Any]) -> None:
    receipt["semantic_sha256"] = sha256_bytes(canonical_json_bytes(receipt["semantic_receipt"]))


def run_tamper_tests(
    receipt: dict[str, Any],
    validator: Callable[[dict[str, Any]], list[str]],
) -> dict[str, Any]:
    tests: list[tuple[str, Callable[[dict[str, Any]], None], bool]] = [
        ("PRODUCT_FINGERPRINT", lambda r: r["semantic_receipt"]["candidate"].__setitem__("product_fingerprint", "0" * 64), True),
        ("DROP_ORDINARY_PIVOT", lambda r: r["semantic_receipt"]["Delta"]["rows"].pop(), True),
        ("GAMMA_SCOPE", lambda r: r["semantic_receipt"]["Gamma"].__setitem__("complete_pair_root_scope", ROUTE_COUNT - 1), True),
        ("INJECT_GAMMA_RESCUE", lambda r: r["semantic_receipt"]["Gamma"].__setitem__("first_exact_rescue", {"pair_index": 0}), True),
        ("REACHABILITY_FALSE", lambda r: r["semantic_receipt"]["reachability"].__setitem__("reachable_at_frozen_ordinary_callsite", False), True),
        ("ORIGINAL_V2_SCOPE", lambda r: r["semantic_receipt"]["original_frozen_v2"]["covered_candidate_indices"].pop(), True),
        ("DROP_EVIDENCE_BINDING", lambda r: r["provenance"]["evidence_file_sha256"].pop("c025-l1-39100-gamma/gamma-general.json"), False),
        ("SEMANTIC_DIGEST", lambda r: r.__setitem__("semantic_sha256", "f" * 64), False),
    ]
    outcomes = []
    rejected = 0
    for name, mutate, recompute in tests:
        specimen = copy.deepcopy(receipt)
        mutate(specimen)
        if recompute:
            refresh_semantic_digest(specimen)
        errors = validator(specimen)
        was_rejected = bool(errors)
        rejected += int(was_rejected)
        outcomes.append({"test": name, "rejected": was_rejected, "error_count": len(errors)})
    return {"tests": outcomes, "rejected": rejected, "total": len(tests), "false_accepts": len(tests) - rejected}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--expected-repository", required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--expected-branch", required=True)
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    receipt_path = Path(args.receipt)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    errors = validate(
        receipt,
        expected_repository=args.expected_repository,
        expected_commit=args.expected_commit,
        expected_branch=args.expected_branch,
        check_checkout=True,
        evidence_dir=Path(args.evidence_dir),
    )
    validator = lambda specimen: validate(
        specimen,
        expected_repository=args.expected_repository,
        expected_commit=args.expected_commit,
        expected_branch=args.expected_branch,
        check_checkout=False,
    )
    tamper = run_tamper_tests(receipt, validator)
    if tamper["false_accepts"]:
        errors.append("TAMPER_FALSE_ACCEPT")

    admitted = not errors
    report = {
        "schema": "JANUS/C025/L1-39100-EXACT-COUNTEREXAMPLE/ADMISSION/v1",
        "admission_state": "ADMITTED" if admitted else "REJECTED_UNKNOWN_NO_ADMISSION",
        "subject": receipt.get("semantic_receipt", {}).get("subject"),
        "composite_file_sha256": sha256_file(receipt_path),
        "semantic_sha256": receipt.get("semantic_sha256"),
        "verifier": {
            "path": str(VERIFIER_PATH),
            "sha256": sha256_file(VERIFIER_PATH),
            "implementation_policy": "SEPARATE_IMPLEMENTATION_NO_PRODUCER_IMPORT",
            "project_module_import_count": len(project_imports(VERIFIER_PATH)),
        },
        "tamper_rejection": tamper,
        "errors": errors,
        "candidate_results": {
            "L1_ROOT_PHASE_POLYNOMIAL_GRAMMAR_TOTALITY": "REFUTED_BY_EXACT_REACHABLE_39100_COUNTEREXAMPLE" if admitted else "OPEN__ADMISSION_REJECTED",
        },
        "scientific_boundary": {
            "P2_REACHABLE_PRESERVATION": "OPEN",
            "ROOT_FREE_V3_TAIL": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
        "P_VS_NP": P_VS_NP,
    }
    Path(args.out).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if admitted else 1


if __name__ == "__main__":
    raise SystemExit(main())
