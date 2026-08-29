#!/usr/bin/env python3
"""Independent append-only verifier for the final C025 L1/39100 ledger.

The expensive mathematical evidence was admitted at the exact evidence commit.
This verifier does not recreate that evidence.  It checks that the final theorem
ledger is an atomic, one-parent append on the admitted evidence tree, that the
authority identifiers and exact numerical conclusions were transcribed without
drift, and that historical UNKNOWN/PENDING receipts remain byte-identical.
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
EVIDENCE_COMMIT = "817523b67e9d032458227d43db1c3a0f73c260f8"
EVIDENCE_TREE = "38f73488928901690a0d1987b07565ae82c342f6"
BRANCH = "research/c025-phase5-9-polynomial-pivot-grammar-2026-08-28"
REPOSITORY = "Hawkar-usls/Janus-Fundamentum"

RECEIPT_PATH = Path("research/C025_L1_39100_EXACT_COUNTEREXAMPLE_ADMISSION_2026-08-29.json")
CENTRAL_PATH = Path("research/C025_POLYNOMIAL_COMPLETE_PIVOT_GRAMMAR_ROOT_PHASE_SPEC_2026-08-28.json")
COMPOSITION_PATH = Path("research/C025_ROOT_PHASE_GRAMMAR_COMPOSITION_LEMMA_2026-08-28.json")
VERIFIER_PATH = Path("experiments/theorem_extraction/c025_l1_39100_final_ledger_verifier.py")
WORKFLOW_PATH = Path(".github/workflows/validate-c025-l1-39100-final-ledger.yml")

EXPECTED_COMMIT_DELTA = {
    str(RECEIPT_PATH),
    str(CENTRAL_PATH),
    str(COMPOSITION_PATH),
    str(VERIFIER_PATH),
    str(WORKFLOW_PATH),
}

IMMUTABLE_RECEIPTS = {
    "research/C025_L1_39100_COUNTEREXAMPLE_CANDIDATE_PENDING_FROZEN_CALLSITE_2026-08-28.json":
        "542656965eecd016f88d8f0bf3ff58e24111d6a680defa9974b6a9907ccc6215",
    "research/C025_ROOSTERS_V5_1_THEOREM_INTEGRATION_TEST_RESULT_2026-08-28.json":
        "f7abce3eeef0d531dfbd5bedc527df4ab9970d9acc3072fca8eed291bbdae328",
    "research/C025_ROOSTERS_THEOREM_GOVERNANCE_V1_2_2026-08-28.json":
        "123ca3a8f6f71b2394f8532af8c28f10d7783bd0bf8f6e9a855e7f0e56eabe04",
}

PARENT_LEDGER_HASHES = {
    str(CENTRAL_PATH): "e0176d4a76b191a3349513915d5ff5bc1dd05fd2098ed7ac4a914e0ebd266c2e",
    str(COMPOSITION_PATH): "8289aff99a82f5417d361f33531e2668468c4380189597722f4bc79ef9a4fa5b",
}

BOUND_IMPLEMENTATION_HASHES = {
    ".github/workflows/validate-c025-l1-39100-promotion.yml":
        "01988786380dade97dd0d103ec281994874d46cdbd9c7f237d92244f9bf23706",
    "experiments/direct/janus_pirc_decision_core_v0_4.py":
        "77f9e819d7f8ba34b1f55ea605c024251ab2ab2f886822421da184a8ef1f2d52",
    "experiments/direct/janus_unified_macro_restore_v2.py":
        "0b88dffbda2775609c5ccc2d08c0845a2899d218155a1e7f070d2900636c7e73",
    "experiments/direct/janus_unified_proof_carrying_akinator_jec.py":
        "90f8d00d2faeb3812151e7c6d3a80667ad460ddb878e01ea3d14a7c3ca491c98",
    "experiments/theorem_extraction/c025_l1_39100_promotion_gate.py":
        "d3954c56f46c5b0e2c87c598c2d006cd533c4c6aaf932d6abd53fa9bf39b9984",
    "experiments/theorem_extraction/c025_l1_39100_admission_verifier.py":
        "2e6705523ea67cf09cf9e13d72a380d34c5d227e101e91ca92a5ccfbe7fd0ab1",
    "experiments/theorem_extraction/c025_l1_fanout_exact_gate.py":
        "fd9ab05325da9318ea73de66d80389a7f09a7f887279f2d5eefb13d4928f88bf",
    "experiments/theorem_extraction/c025_l1_uniform_exact_checker.cpp":
        "78ee15e3e9e778c19acfd2e50ad8459c59cc035b9d65d13e5662e6ac2db51cb4",
    "experiments/theorem_extraction/c025_uniform_exact_checker_general.cpp":
        "3a1a0a87aa88c73e317636d68b0047c2562433d0c87e00dc14938ebed10bc52a",
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_output(*args: str, text: bool = True) -> str | bytes:
    return subprocess.check_output(["git", *args], text=text, stderr=subprocess.DEVNULL)


def committed_bytes(commit: str, path: str) -> bytes | None:
    try:
        payload = git_output("show", f"{commit}:{path}", text=False)
    except (OSError, subprocess.CalledProcessError):
        return None
    assert isinstance(payload, bytes)
    return payload


def committed_sha256(commit: str, path: str) -> str | None:
    payload = committed_bytes(commit, path)
    return sha256_bytes(payload) if payload is not None else None


def expect(condition: bool, label: str, errors: list[str]) -> None:
    if not condition:
        errors.append(label)


def project_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend(
                alias.name for alias in node.names
                if alias.name == "experiments" or alias.name.startswith("experiments.")
            )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "experiments" or module.startswith("experiments."):
                found.append(module)
    return sorted(found)


def validate_documents(
    receipt: dict[str, Any],
    central: dict[str, Any],
    composition: dict[str, Any],
    *,
    expected_ledger_parent: str,
    check_checkout: bool,
) -> list[str]:
    errors: list[str] = []

    expect(
        receipt.get("schema") == "JANUS/C025/L1-39100-EXACT-COUNTEREXAMPLE/FINAL-ADMISSION/v1",
        "RECEIPT_SCHEMA", errors,
    )
    expect(
        receipt.get("status") == "FINAL_ADMITTED__L1_REFUTED_BY_EXACT_REACHABLE_39100_COUNTEREXAMPLE",
        "RECEIPT_STATUS", errors,
    )
    subject = receipt.get("subject", {})
    expect(subject.get("repository") == REPOSITORY, "SUBJECT_REPOSITORY", errors)
    expect(subject.get("branch") == BRANCH, "SUBJECT_BRANCH", errors)
    expect(subject.get("evidence_commit") == EVIDENCE_COMMIT, "SUBJECT_EVIDENCE_COMMIT", errors)
    expect(subject.get("evidence_tree") == EVIDENCE_TREE, "SUBJECT_EVIDENCE_TREE", errors)
    expect(subject.get("fixed_algorithm") == "PIRC_DECISION_CORE_V0_4", "SUBJECT_ALGORITHM", errors)

    run = receipt.get("exact_head_workflow", {})
    expect(run.get("name") == "validate-c025-l1-39100-promotion", "RUN_NAME", errors)
    expect(run.get("run_id") == 33_219_176_031, "RUN_ID", errors)
    expect(run.get("head_sha") == EVIDENCE_COMMIT, "RUN_HEAD", errors)
    expect(run.get("event") == "push", "RUN_EVENT", errors)
    expect(run.get("status") == "COMPLETED" and run.get("conclusion") == "SUCCESS", "RUN_RESULT", errors)
    jobs = run.get("job_accounting", {})
    expected_jobs = {
        "total": 77,
        "successful": 77,
        "failed_or_cancelled": 0,
        "identity": 1,
        "reachability": 1,
        "gamma": 1,
        "ordinary_shards": 8,
        "original_v2_shards": 64,
        "assemble": 1,
        "admission": 1,
    }
    expect(jobs == expected_jobs, "RUN_JOB_ACCOUNTING", errors)
    expect(
        sum(jobs.get(key, -1000) for key in (
            "identity", "reachability", "gamma", "ordinary_shards",
            "original_v2_shards", "assemble", "admission",
        )) == jobs.get("total"),
        "RUN_JOB_SUM", errors,
    )

    artifacts = receipt.get("authority_artifacts", {})
    admission_artifact = artifacts.get("admission", {})
    composite_artifact = artifacts.get("composite", {})
    expect(admission_artifact.get("artifact_id") == 9_705_452_984, "ADMISSION_ARTIFACT_ID", errors)
    expect(
        admission_artifact.get("github_digest") ==
        "sha256:22342b3b725aae051ef286ecde1f53fc27eb2e3da481fea08e4dea066f6d8c0a",
        "ADMISSION_ARTIFACT_DIGEST", errors,
    )
    expect(
        admission_artifact.get("downloaded_zip_sha256") ==
        admission_artifact.get("github_digest", "").removeprefix("sha256:"),
        "ADMISSION_ZIP_BINDING", errors,
    )
    expect(
        admission_artifact.get("admission_json_sha256") ==
        "e9b8f3e4953cfe6a499af2fae1c1282e180b212f2aa3225131bacca639b5541b",
        "ADMISSION_JSON_DIGEST", errors,
    )
    expect(composite_artifact.get("artifact_id") == 9_705_449_755, "COMPOSITE_ARTIFACT_ID", errors)
    expect(
        composite_artifact.get("github_digest") ==
        "sha256:e0fa2898e62e32a34193dff16f8961856833a45ecb0d9d9babac2a911a3d7c1d",
        "COMPOSITE_ARTIFACT_DIGEST", errors,
    )
    expect(
        composite_artifact.get("downloaded_zip_sha256") ==
        composite_artifact.get("github_digest", "").removeprefix("sha256:"),
        "COMPOSITE_ZIP_BINDING", errors,
    )
    expect(
        composite_artifact.get("composite_json_sha256") ==
        "82750cf5126b8c7a358e3529972bb6944529946b049c7920a0a1b1468eac7fa2",
        "COMPOSITE_JSON_DIGEST", errors,
    )
    expect(
        composite_artifact.get("semantic_sha256") ==
        "8b3a333a7547eab44218ba4e7fda2a9a7d3e15414382c5d06af7b9b574bd5341",
        "SEMANTIC_DIGEST", errors,
    )
    expect(
        artifacts.get("gamma", {}).get("github_digest") ==
        "sha256:7c0de0ec5e83edddcf15fd248062c7b28b94f753bd8338cfa74993d9c07c049a",
        "GAMMA_ARTIFACT_DIGEST", errors,
    )
    expect(
        artifacts.get("reachability", {}).get("github_digest") ==
        "sha256:6ccca8ff1bbf63e78e0b4fab16cb309339e0e2b383a416237302abbc83831fa9",
        "REACHABILITY_ARTIFACT_DIGEST", errors,
    )

    candidate = receipt.get("candidate", {})
    expect(candidate.get("seed") == 39_100, "CANDIDATE_SEED", errors)
    expect(
        candidate.get("source_fingerprint") ==
        "bc07cfeb7d1ef62916d7319ed59edc8d2e4a92ce34881a13186d2c47991c66bc",
        "SOURCE_FINGERPRINT", errors,
    )
    expect(
        candidate.get("product_fingerprint") ==
        "037cbc224816408ca1c76c65c9bb78ad660d3b612c40ef91d1ac76943c7c79c3",
        "PRODUCT_FINGERPRINT", errors,
    )
    expect(candidate.get("N") == 1_102 and candidate.get("cap") == 1_214_404, "N_CAP", errors)
    expect(candidate.get("product_units") == 72_901 and candidate.get("product_clauses") == 8_100, "PRODUCT_SIZE", errors)
    expect(candidate.get("live_roots") == 20 and candidate.get("v2_candidate_pairs") == 744, "GRAMMAR_SIZE", errors)

    results = receipt.get("exact_results", {})
    reachability = results.get("reachability", {})
    expect(reachability.get("reachable_at_frozen_ordinary_callsite") is True, "REACHABLE_CALLSITE", errors)
    expect(reachability.get("selector_pivot_1_exact_product") is True, "SELECTOR_EXACT_PRODUCT", errors)
    expect(reachability.get("unmodified_core_prefix") is True, "UNMODIFIED_PREFIX", errors)
    delta = results.get("Delta", {})
    expect(delta.get("strictly_positive") is True, "DELTA_POSITIVE", errors)
    expect(delta.get("original_ordinary_pivots") == 20, "DELTA_SCOPE", errors)
    expect(delta.get("all_original_ordinary_pivots_overflow") is True, "DELTA_ALL_OVERFLOW", errors)
    expect(delta.get("minimum_observed_first_crossing_margin") == 2, "DELTA_MARGIN", errors)
    expect(delta.get("ordinary_parent_pairs_examined_until_crossing") == 13_474_988, "DELTA_WORK", errors)
    gamma = results.get("Gamma", {})
    expect(gamma.get("strictly_positive") is True, "GAMMA_POSITIVE", errors)
    expect(gamma.get("complete_pair_root_scope") == 14_880, "GAMMA_SCOPE", errors)
    expect(gamma.get("first_exact_rescue") is None, "GAMMA_NO_RESCUE", errors)
    expect(gamma.get("independent_exact_backend_minimum_crossing_margin") == 1, "GAMMA_INDEPENDENT_MARGIN", errors)
    expect(gamma.get("general_exact_backend_minimum_crossing_margin") == 1, "GAMMA_GENERAL_MARGIN", errors)
    expect(gamma.get("literal_original_v2_canonical_pairs_replayed") == 744, "ORIGINAL_V2_PAIR_SCOPE", errors)
    expect(gamma.get("literal_original_v2_shards") == 64, "ORIGINAL_V2_SHARDS", errors)
    expect(gamma.get("literal_original_v2_result") == "COMPLETE_ORIGINAL_FROZEN_V2_NO_RESCUE", "ORIGINAL_V2_RESULT", errors)

    admission = receipt.get("independent_admission", {})
    expect(admission.get("state") == "ADMITTED", "ADMISSION_STATE", errors)
    expect(admission.get("project_module_import_count") == 0, "ADMISSION_IMPORT_BOUNDARY", errors)
    expect(admission.get("tamper_tests_rejected") == 8, "ADMISSION_TAMPER_REJECTIONS", errors)
    expect(admission.get("tamper_tests_total") == 8, "ADMISSION_TAMPER_TOTAL", errors)
    expect(admission.get("tamper_false_accepts") == 0, "ADMISSION_TAMPER_FALSE_ACCEPTS", errors)
    expect(admission.get("errors") == [], "ADMISSION_ERRORS", errors)
    replay = admission.get("detached_exact_head_replay", {})
    expect(replay.get("state") == "ADMITTED", "DETACHED_REPLAY_STATE", errors)
    expect(replay.get("byte_identical_admission_json") is True, "DETACHED_REPLAY_IDENTITY", errors)
    expect(replay.get("admission_json_sha256") == admission_artifact.get("admission_json_sha256"), "DETACHED_REPLAY_DIGEST", errors)

    expect(receipt.get("bound_implementation_sha256") == BOUND_IMPLEMENTATION_HASHES, "IMPLEMENTATION_MANIFEST", errors)
    lineage = receipt.get("append_only_lineage", {})
    expect(lineage.get("historical_timeout_run") == 33_196_344_106, "TIMEOUT_RUN", errors)
    expect(lineage.get("historical_timeout_verdict_remains") == "UNKNOWN_RESOURCE_LIMIT", "TIMEOUT_VERDICT", errors)
    expect(lineage.get("old_unknown_or_pending_receipt_rewritten") is False, "APPEND_ONLY_POLICY", errors)
    expected_parent_hashes = {**IMMUTABLE_RECEIPTS, **PARENT_LEDGER_HASHES}
    expect(lineage.get("parent_file_sha256") == expected_parent_hashes, "PARENT_HASH_MANIFEST", errors)
    expect(
        lineage.get("promotion_gate_sha256") ==
        "f4b4ee4d8b0c220fc4143bc87bc4fdc24096f4247eef7187f2ef9c11e7442c83",
        "PROMOTION_GATE_RECEIPT_HASH", errors,
    )
    expect(
        lineage.get("semantic_equivalence_lemma_sha256") ==
        "b1a8c754620a260316868048979208d6631cd5d9e27da76e1a16645943a0b302",
        "EQUIVALENCE_LEMMA_HASH", errors,
    )

    verdict = receipt.get("verdict", {})
    expect(
        verdict.get("L1_ROOT_PHASE_POLYNOMIAL_GRAMMAR_TOTALITY") ==
        "REFUTED_BY_EXACT_REACHABLE_39100_COUNTEREXAMPLE",
        "L1_VERDICT", errors,
    )
    for lemma_id in (
        "L1A_ALL_PIVOT_OVERFLOW_FORCES_FREQUENT_PAIR",
        "L1B_ALL_PIVOT_OVERFLOW_FORCES_PAIR_DENSITY",
        "L1C_ALL_PIVOT_OVERFLOW_FORCES_DRAINABLE_ROOT_PAIR",
    ):
        expect(verdict.get(lemma_id) == "REFUTED_PREVIOUSLY", f"{lemma_id}_VERDICT", errors)
    expect(verdict.get("P2_REACHABLE_PRESERVATION") == "OPEN", "P2_BOUNDARY", errors)
    expect(verdict.get("ROOT_FREE_V3_TAIL") == "OPEN", "V3_BOUNDARY", errors)

    expect(
        central.get("schema") == "JANUS/C025/POLYNOMIAL-COMPLETE-PIVOT-GRAMMAR/ROOT-PHASE/v1.2",
        "CENTRAL_SCHEMA", errors,
    )
    expect(
        central.get("status") == "L1_REFUTED_BY_EXACT_REACHABLE_39100_COUNTEREXAMPLE__SUCCESSOR_GRAMMAR_REQUIRED",
        "CENTRAL_STATUS", errors,
    )
    main_candidate = central.get("main_candidate", {})
    expect(main_candidate.get("id") == "L1_ROOT_PHASE_POLYNOMIAL_GRAMMAR_TOTALITY", "CENTRAL_L1_ID", errors)
    expect(main_candidate.get("status") == verdict.get("L1_ROOT_PHASE_POLYNOMIAL_GRAMMAR_TOTALITY"), "CENTRAL_L1_STATUS", errors)
    expect(main_candidate.get("witness") == str(RECEIPT_PATH), "CENTRAL_WITNESS", errors)
    counterexample = central.get("admitted_counterexample", {})
    expect(counterexample.get("receipt") == str(RECEIPT_PATH), "CENTRAL_RECEIPT_BINDING", errors)
    expect(counterexample.get("source_fingerprint") == candidate.get("source_fingerprint"), "CENTRAL_SOURCE_FP", errors)
    expect(counterexample.get("product_fingerprint") == candidate.get("product_fingerprint"), "CENTRAL_PRODUCT_FP", errors)
    expect(counterexample.get("N") == candidate.get("N") and counterexample.get("cap") == candidate.get("cap"), "CENTRAL_N_CAP", errors)
    expect(counterexample.get("reachable") is True, "CENTRAL_REACHABLE", errors)
    expect(counterexample.get("Delta_strictly_positive") is True, "CENTRAL_DELTA", errors)
    expect(counterexample.get("Gamma_strictly_positive") is True, "CENTRAL_GAMMA", errors)
    expect(counterexample.get("ordinary_overflow_pivots") == 20, "CENTRAL_ORDINARY_SCOPE", errors)
    expect(counterexample.get("frozen_v2_candidate_pairs") == 744, "CENTRAL_PAIR_SCOPE", errors)
    expect(counterexample.get("complete_pair_root_scope") == 14_880, "CENTRAL_ROUTE_SCOPE", errors)
    expect(counterexample.get("exact_head_workflow_run") == run.get("run_id"), "CENTRAL_RUN_BINDING", errors)
    expect(counterexample.get("independent_admission") == "ADMITTED", "CENTRAL_ADMISSION", errors)
    expect(
        central.get("proof_obligations_if_L1_survives_status") ==
        "INAPPLICABLE__L1_DID_NOT_SURVIVE_EXACT_FALSIFICATION",
        "CENTRAL_OLD_ROUTE_STATUS", errors,
    )

    expect(
        composition.get("schema") == "JANUS/C025/ROOT-PHASE-GRAMMAR-COMPOSITION-LEMMA/v1.1",
        "COMPOSITION_SCHEMA", errors,
    )
    expect(
        composition.get("status") ==
        "CONDITIONAL_LEMMA_REMAINS_PROVED__L1_PREMISE_REFUTED__ROUTE_INAPPLICABLE",
        "COMPOSITION_STATUS", errors,
    )
    premise = composition.get("premise", {})
    expect(premise.get("status") == verdict.get("L1_ROOT_PHASE_POLYNOMIAL_GRAMMAR_TOTALITY"), "COMPOSITION_PREMISE", errors)
    expect(premise.get("witness") == str(RECEIPT_PATH), "COMPOSITION_WITNESS", errors)
    lemma = composition.get("lemma", {})
    expect(
        lemma.get("status") ==
        "PROVED_CONDITIONALLY_ON_L1__NOT_APPLICABLE_TO_FROZEN_ALGORITHM_BECAUSE_L1_IS_FALSE",
        "COMPOSITION_LEMMA_STATUS", errors,
    )
    applicability = composition.get("applicability_after_counterexample", {})
    expect(applicability.get("logical_implication_remains_valid") is True, "IMPLICATION_VALID", errors)
    expect(applicability.get("premise_is_false_for_frozen_algorithm") is True, "PREMISE_FALSE", errors)
    expect(applicability.get("may_be_used_to_claim_frozen_root_phase_corridor") is False, "ROUTE_INAPPLICABLE", errors)

    expect(receipt.get("P_VS_NP") == P_VS_NP, "RECEIPT_P_VS_NP", errors)
    expect(verdict.get("P_VS_NP") == P_VS_NP, "VERDICT_P_VS_NP", errors)
    expect(central.get("P_VS_NP") == P_VS_NP, "CENTRAL_P_VS_NP", errors)
    expect(central.get("scientific_boundary", {}).get("P_VS_NP") == P_VS_NP, "CENTRAL_BOUNDARY_P_VS_NP", errors)
    expect(composition.get("P_VS_NP") == P_VS_NP, "COMPOSITION_P_VS_NP", errors)
    expect(composition.get("scientific_boundary", {}).get("P_VS_NP") == P_VS_NP, "COMPOSITION_BOUNDARY_P_VS_NP", errors)

    if check_checkout:
        try:
            current_head = str(git_output("rev-parse", "HEAD")).strip()
            parent_line = str(git_output("rev-list", "--parents", "-n", "1", "HEAD")).strip().split()
            evidence_tree = str(git_output("show", "-s", "--format=%T", EVIDENCE_COMMIT)).strip()
            parent_tree = str(git_output("show", "-s", "--format=%T", expected_ledger_parent)).strip()
            changed_paths = {
                line for line in str(git_output(
                    "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"
                )).splitlines() if line
            }
        except (OSError, subprocess.CalledProcessError):
            current_head = ""
            parent_line = []
            evidence_tree = ""
            parent_tree = ""
            changed_paths = set()
        expect(len(parent_line) == 2, "SINGLE_PARENT_COMMIT", errors)
        expect(len(parent_line) == 2 and parent_line[0] == current_head, "CURRENT_HEAD_IDENTITY", errors)
        expect(len(parent_line) == 2 and parent_line[1] == expected_ledger_parent, "LEDGER_PARENT", errors)
        expect(evidence_tree == EVIDENCE_TREE, "EVIDENCE_COMMIT_TREE", errors)
        expect(parent_tree == EVIDENCE_TREE, "LEDGER_PARENT_TREE", errors)
        expect(changed_paths == EXPECTED_COMMIT_DELTA, "ATOMIC_LEDGER_COMMIT_SCOPE", errors)
        expect(committed_bytes(expected_ledger_parent, str(RECEIPT_PATH)) is None, "RECEIPT_APPEND_ONLY", errors)
        expect(project_imports(VERIFIER_PATH) == [], "VERIFIER_PROJECT_IMPORT", errors)
        for path_text, expected_hash in IMMUTABLE_RECEIPTS.items():
            path = Path(path_text)
            expect(path.is_file() and sha256_file(path) == expected_hash, f"CURRENT_IMMUTABLE:{path_text}", errors)
            expect(committed_sha256(EVIDENCE_COMMIT, path_text) == expected_hash, f"EVIDENCE_IMMUTABLE:{path_text}", errors)
            expect(committed_sha256(expected_ledger_parent, path_text) == expected_hash, f"PARENT_IMMUTABLE:{path_text}", errors)
        for path_text, expected_hash in PARENT_LEDGER_HASHES.items():
            expect(committed_sha256(EVIDENCE_COMMIT, path_text) == expected_hash, f"EVIDENCE_PARENT_LEDGER:{path_text}", errors)
            expect(committed_sha256(expected_ledger_parent, path_text) == expected_hash, f"PARENT_LEDGER:{path_text}", errors)
        for path_text, expected_hash in BOUND_IMPLEMENTATION_HASHES.items():
            expect(committed_sha256(EVIDENCE_COMMIT, path_text) == expected_hash, f"EVIDENCE_IMPLEMENTATION:{path_text}", errors)
            expect(committed_sha256(expected_ledger_parent, path_text) == expected_hash, f"PARENT_IMPLEMENTATION:{path_text}", errors)
        expect(
            committed_sha256(EVIDENCE_COMMIT, "research/C025_L1_39100_EXACT_COUNTEREXAMPLE_PROMOTION_GATE_2026-08-28.json") ==
            lineage.get("promotion_gate_sha256"),
            "EVIDENCE_PROMOTION_GATE_RECEIPT", errors,
        )
        expect(
            committed_sha256(EVIDENCE_COMMIT, "research/C025_L1_39100_UNIFORM_V2_SEMANTIC_EQUIVALENCE_LEMMA_2026-08-28.json") ==
            lineage.get("semantic_equivalence_lemma_sha256"),
            "EVIDENCE_EQUIVALENCE_LEMMA", errors,
        )
    return errors


def run_tamper_tests(
    receipt: dict[str, Any],
    central: dict[str, Any],
    composition: dict[str, Any],
    validator: Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], list[str]],
) -> dict[str, Any]:
    tests: list[tuple[str, Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], None]]] = [
        ("EVIDENCE_COMMIT", lambda r, _c, _m: r["subject"].__setitem__("evidence_commit", "0" * 40)),
        ("RUN_JOB_ACCOUNTING", lambda r, _c, _m: r["exact_head_workflow"]["job_accounting"].__setitem__("successful", 76)),
        ("GAMMA_SCOPE", lambda r, _c, _m: r["exact_results"]["Gamma"].__setitem__("complete_pair_root_scope", 14_879)),
        ("ADMISSION_STATE", lambda r, _c, _m: r["independent_admission"].__setitem__("state", "PENDING")),
        ("CENTRAL_L1_STATUS", lambda _r, c, _m: c["main_candidate"].__setitem__("status", "OPEN")),
        ("COMPOSITION_APPLICABILITY", lambda _r, _c, m: m["applicability_after_counterexample"].__setitem__("may_be_used_to_claim_frozen_root_phase_corridor", True)),
        ("P_VS_NP_BOUNDARY", lambda r, _c, _m: r.__setitem__("P_VS_NP", "CLOSED")),
    ]
    outcomes: list[dict[str, Any]] = []
    rejected = 0
    for name, mutate in tests:
        r_specimen = copy.deepcopy(receipt)
        c_specimen = copy.deepcopy(central)
        m_specimen = copy.deepcopy(composition)
        mutate(r_specimen, c_specimen, m_specimen)
        errors = validator(r_specimen, c_specimen, m_specimen)
        was_rejected = bool(errors)
        rejected += int(was_rejected)
        outcomes.append({"test": name, "rejected": was_rejected, "error_count": len(errors)})
    return {
        "tests": outcomes,
        "rejected": rejected,
        "total": len(tests),
        "false_accepts": len(tests) - rejected,
    }


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", default=str(RECEIPT_PATH))
    parser.add_argument("--central", default=str(CENTRAL_PATH))
    parser.add_argument("--composition", default=str(COMPOSITION_PATH))
    parser.add_argument("--expected-ledger-parent", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    receipt_path = Path(args.receipt)
    central_path = Path(args.central)
    composition_path = Path(args.composition)
    receipt = load_json(receipt_path)
    central = load_json(central_path)
    composition = load_json(composition_path)

    errors = validate_documents(
        receipt,
        central,
        composition,
        expected_ledger_parent=args.expected_ledger_parent,
        check_checkout=True,
    )
    validator = lambda r, c, m: validate_documents(
        r, c, m,
        expected_ledger_parent=args.expected_ledger_parent,
        check_checkout=False,
    )
    tamper = run_tamper_tests(receipt, central, composition, validator)
    if tamper["false_accepts"]:
        errors.append("TAMPER_FALSE_ACCEPT")

    validated = not errors
    try:
        current_head = str(git_output("rev-parse", "HEAD")).strip()
    except (OSError, subprocess.CalledProcessError):
        current_head = "UNKNOWN"
    report = {
        "schema": "JANUS/C025/L1-39100/FINAL-LEDGER-VALIDATION/v1",
        "ledger_state": "VALIDATED_FINAL_ADMISSION_LEDGER" if validated else "REJECTED_UNKNOWN_NO_LEDGER_AUTHORITY",
        "subject": {
            "repository": REPOSITORY,
            "branch": BRANCH,
            "ledger_commit": current_head,
            "ledger_parent": args.expected_ledger_parent,
            "evidence_commit": EVIDENCE_COMMIT,
            "evidence_tree": EVIDENCE_TREE,
        },
        "document_sha256": {
            str(RECEIPT_PATH): sha256_file(receipt_path),
            str(CENTRAL_PATH): sha256_file(central_path),
            str(COMPOSITION_PATH): sha256_file(composition_path),
            str(VERIFIER_PATH): sha256_file(VERIFIER_PATH),
            str(WORKFLOW_PATH): sha256_file(WORKFLOW_PATH),
        },
        "authority": {
            "exact_head_run": 33_219_176_031,
            "admission_artifact": 9_705_452_984,
            "composite_artifact": 9_705_449_755,
            "reachable": True,
            "Delta_strictly_positive": True,
            "Gamma_strictly_positive": True,
            "original_frozen_v2_pairs_replayed": 744,
            "L1_ROOT_PHASE_POLYNOMIAL_GRAMMAR_TOTALITY":
                "REFUTED_BY_EXACT_REACHABLE_39100_COUNTEREXAMPLE",
        },
        "tamper_rejection": tamper,
        "errors": errors,
        "scientific_boundary": {
            "P2_REACHABLE_PRESERVATION": "OPEN",
            "ROOT_FREE_V3_TAIL": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
        "P_VS_NP": P_VS_NP,
    }
    Path(args.out).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if validated else 1


if __name__ == "__main__":
    raise SystemExit(main())
