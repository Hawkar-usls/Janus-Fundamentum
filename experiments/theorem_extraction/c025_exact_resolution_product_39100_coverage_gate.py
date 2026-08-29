#!/usr/bin/env python3
"""Produce the 39100 exact resolution-product successor coverage bundle.

This producer may call the constructor but has no admission authority.  The
standard-library no-project-import verifier is executed separately.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.theorem_extraction import c025_exact_resolution_product_factor as factorizer
from experiments.theorem_extraction import c025_l1_39100_promotion_gate as promotion

P_VS_NP = "OPEN"
SPEC_PATH = Path("research/C025_EXACT_RESOLUTION_PRODUCT_FACTOR_39100_COVERAGE_GATE_2026-08-29.json")
HOLDOUT_SPEC_PATH = Path("research/C025_FACTORIZED_RESOLUTION_PRODUCT_39100_HOLDOUT_FREEZE_2026-08-29.json")
CONSTRUCTOR_PATH = Path("experiments/theorem_extraction/c025_exact_resolution_product_factor.py")
VERIFIER_PATH = Path("experiments/theorem_extraction/c025_exact_resolution_product_factor_verifier.py")
EXPECTED_HOLDOUT_TREE = "09d10acc2cdcecd20f8cca4692679ebe0057e1f5"


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_text(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()


def constructor_static_audit(path: Path) -> dict[str, Any]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    called_names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                called_names.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                called_names.append(node.func.attr)
    forbidden = sorted(set(called_names) & {
        "resolve_on_var",
        "eliminate_var_capped",
        "verify_elimination_transition",
        "explicit_elimination_diagnostic",
    })
    return {
        "path": str(path),
        "sha256": sha256_file(path),
        "forbidden_cross_product_or_elimination_calls": forbidden,
        "forbidden_calls_absent": not forbidden,
        "declared_single_source_scan_comment_present": "There is intentionally no loop over P x N" in source,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--expected-factorizer-parent", required=True)
    parser.add_argument("--expected-branch", required=True)
    parser.add_argument("--source-out", required=True)
    parser.add_argument("--factor-out", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    head = git_text("rev-parse", "HEAD")
    branch = git_text("rev-parse", "--abbrev-ref", "HEAD")
    parents = git_text("rev-list", "--parents", "-n", "1", "HEAD").split()
    parent_tree = git_text("show", "-s", "--format=%T", args.expected_factorizer_parent)
    if head != args.expected_commit:
        raise AssertionError("EXACT_HEAD_MISMATCH")
    if branch != args.expected_branch:
        raise AssertionError("EXACT_BRANCH_MISMATCH")
    if len(parents) != 2 or parents[1] != args.expected_factorizer_parent:
        raise AssertionError("FACTORIZER_NOT_DIRECT_CHILD_OF_HOLDOUT_FREEZE")
    if parent_tree != EXPECTED_HOLDOUT_TREE:
        raise AssertionError("HOLDOUT_PARENT_TREE_MISMATCH")

    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    holdout_spec = json.loads(HOLDOUT_SPEC_PATH.read_text(encoding="utf-8"))
    if spec.get("P_VS_NP") != P_VS_NP or holdout_spec.get("P_VS_NP") != P_VS_NP:
        raise AssertionError("P_VS_NP_BOUNDARY")
    if spec.get("holdout_authority", {}).get("freeze_tree") != EXPECTED_HOLDOUT_TREE:
        raise AssertionError("SPEC_HOLDOUT_TREE")

    source, product = promotion.candidate()
    target_state = promotion.direct_target_state(source, product)
    pivot = base.canonical_pivot_order(target_state)[0]
    if pivot != 2:
        raise AssertionError("CANONICAL_HOLDOUT_PIVOT_DRIFT")
    subject = {
        "repository": "Hawkar-usls/Janus-Fundamentum",
        "branch": branch,
        "factorizer_commit": head,
        "factorizer_parent": args.expected_factorizer_parent,
        "holdout_commit": spec["holdout_authority"]["freeze_commit"],
        "holdout_tree": EXPECTED_HOLDOUT_TREE,
        "holdout_workflow_run": spec["holdout_authority"]["workflow_run"],
        "witness": 39100,
    }
    source_doc = {
        "schema": "JANUS/C025/EXACT-RESOLUTION-PRODUCT-FACTOR/SOURCE/v1",
        "source_cnf": [list(clause) for clause in product],
        "source_fingerprint": base.fingerprint(product),
        "source_state_units": base.state_units(product),
        "source_clause_count": len(product),
        "root_variables": list(target_state.root_vars),
        "pivot": pivot,
        "N": promotion.N,
        "cap": promotion.CAP,
        "subject": subject,
        "P_VS_NP": P_VS_NP,
    }
    Path(args.source_out).write_text(json.dumps(source_doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    factor = factorizer.construct_exact_resolution_product_factor(
        product,
        pivot=pivot,
        state_cap=promotion.CAP,
        root_variables=target_state.root_vars,
        subject=subject,
    )
    Path(args.factor_out).write_text(json.dumps(factor, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ledger = factor["resource_ledger"]
    audit = constructor_static_audit(CONSTRUCTOR_PATH)
    if not audit["forbidden_calls_absent"]:
        raise AssertionError("CONSTRUCTOR_HIDDEN_EXPANSION_CALL")
    if ledger.get("explicit_resolution_pairs_avoided") != 1_960_200:
        raise AssertionError("HOLDOUT_PAIR_SCOPE")
    if ledger.get("hidden_expansion_executed") is not False:
        raise AssertionError("HIDDEN_EXPANSION_FLAG")

    expected = spec.get("expected_resource_receipt", {})
    if expected.get("status") == "BOUND_BY_EXACT_HEAD_GATE":
        for key in (
            "input_state_units",
            "partition_scan_literal_visits",
            "verification_literal_visits",
            "verification_hash_work",
            "representation_structural_units",
            "certificate_reference_units",
            "combined_structural_units",
            "representation_bytes",
            "certificate_bytes",
            "combined_serialized_bytes",
            "explicit_resolution_pairs_avoided",
            "hidden_expansion_executed",
        ):
            if ledger.get(key) != expected.get(key):
                raise AssertionError(f"EXPECTED_RESOURCE_DRIFT:{key}")
        if ledger.get("max_live_representation_units") != expected.get("atomic_max_live_representation_units"):
            raise AssertionError("EXPECTED_RESOURCE_DRIFT:atomic_max_live_representation_units")
        if promotion.CAP - ledger["max_live_representation_units"] != expected.get("atomic_cap_margin"):
            raise AssertionError("EXPECTED_RESOURCE_DRIFT:atomic_cap_margin")
        if promotion.CAP - ledger["combined_serialized_bytes"] != expected.get("serialized_cap_margin"):
            raise AssertionError("EXPECTED_RESOURCE_DRIFT:serialized_cap_margin")

    report = {
        "schema": "JANUS/C025/EXACT-RESOLUTION-PRODUCT-FACTOR/39100-PRODUCER/v1",
        "production_state": "EXACT_LOCAL_FACTOR_PRODUCED__INDEPENDENT_ADMISSION_REQUIRED",
        "subject": subject,
        "holdout_binding": spec["holdout_authority"],
        "source": {
            "path": args.source_out,
            "sha256": sha256_file(Path(args.source_out)),
            "fingerprint": source_doc["source_fingerprint"],
            "state_units": source_doc["source_state_units"],
            "clauses": source_doc["source_clause_count"],
            "pivot": pivot,
        },
        "factor": {
            "path": args.factor_out,
            "sha256": sha256_file(Path(args.factor_out)),
            "node_fingerprint": factor["factor_node"]["factor_node_fingerprint"],
            "resource_ledger": ledger,
        },
        "constructor_static_audit": audit,
        "implementation_sha256": {
            str(CONSTRUCTOR_PATH): sha256_file(CONSTRUCTOR_PATH),
            str(VERIFIER_PATH): sha256_file(VERIFIER_PATH),
            str(SPEC_PATH): sha256_file(SPEC_PATH),
            str(HOLDOUT_SPEC_PATH): sha256_file(HOLDOUT_SPEC_PATH),
        },
        "admission": {
            "state": "PENDING_SEPARATE_STANDARD_LIBRARY_VERIFIER",
            "producer_has_admission_authority": False,
        },
        "scientific_boundary": spec["scientific_boundary"],
        "P_VS_NP": P_VS_NP,
    }
    Path(args.out).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
