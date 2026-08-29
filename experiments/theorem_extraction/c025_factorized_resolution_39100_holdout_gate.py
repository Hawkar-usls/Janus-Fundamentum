#!/usr/bin/env python3
"""Freeze witness 39100 as a factorizer-independent exact holdout.

This gate deliberately contains no factorized-resolution constructor.  It
reconstructs the already-admitted L1 witness, binds to the hash-frozen
independent call-site admission, replays the exact selector transition, selects
the first canonical live root, and proves strict over-cap behavior with the
original monotone capped-elimination implementation.

P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
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
from experiments.theorem_extraction import c025_l1_39100_promotion_gate as promotion

P_VS_NP = "OPEN"
SPEC_PATH = Path("research/C025_FACTORIZED_RESOLUTION_PRODUCT_39100_HOLDOUT_FREEZE_2026-08-29.json")
FINAL_ADMISSION_PATH = Path("research/C025_L1_39100_EXACT_COUNTEREXAMPLE_ADMISSION_2026-08-29.json")
FINAL_ADMISSION_SHA256 = "a218316d5f636d0a0177990a4b00b9e2a94a02f2ac870d8b4bb7369cc78d945b"
EXPECTED_SPEC_SCHEMA = "JANUS/C025/FACTORIZED-RESOLUTION-PRODUCT/39100-HOLDOUT-FREEZE/v1"
EXPECTED_STATUS = "FROZEN_EXACT_HOLDOUT__FACTORIZER_PATHS_ABSENT"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return sha256_bytes(payload)


def git_text(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()


def load_spec() -> dict[str, Any]:
    value = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError("HOLDOUT_SPEC_NOT_OBJECT")
    if value.get("schema") != EXPECTED_SPEC_SCHEMA:
        raise AssertionError("HOLDOUT_SPEC_SCHEMA_DRIFT")
    if value.get("P_VS_NP") != P_VS_NP:
        raise AssertionError("HOLDOUT_SPEC_P_VS_NP_BOUNDARY")
    return value


def admitted_reachability_binding(source: base.CNF, product: base.CNF) -> dict[str, Any]:
    if sha256_file(FINAL_ADMISSION_PATH) != FINAL_ADMISSION_SHA256:
        raise AssertionError("FINAL_ADMISSION_FILE_HASH_DRIFT")
    receipt = json.loads(FINAL_ADMISSION_PATH.read_text(encoding="utf-8"))
    if receipt.get("status") != "FINAL_ADMITTED__L1_REFUTED_BY_EXACT_REACHABLE_39100_COUNTEREXAMPLE":
        raise AssertionError("FINAL_ADMISSION_STATUS")
    if receipt.get("P_VS_NP") != P_VS_NP:
        raise AssertionError("FINAL_ADMISSION_P_VS_NP_BOUNDARY")
    candidate = receipt.get("candidate", {})
    reachability = receipt.get("exact_results", {}).get("reachability", {})
    admission = receipt.get("independent_admission", {})
    if candidate.get("source_fingerprint") != base.fingerprint(source):
        raise AssertionError("FINAL_ADMISSION_SOURCE_BINDING")
    if candidate.get("product_fingerprint") != base.fingerprint(product):
        raise AssertionError("FINAL_ADMISSION_PRODUCT_BINDING")
    if reachability.get("reachable_at_frozen_ordinary_callsite") is not True:
        raise AssertionError("FINAL_ADMISSION_REACHABILITY")
    if reachability.get("selector_pivot_1_exact_product") is not True:
        raise AssertionError("FINAL_ADMISSION_SELECTOR_TRANSITION")
    if reachability.get("unmodified_core_prefix") is not True:
        raise AssertionError("FINAL_ADMISSION_CORE_PREFIX")
    if admission.get("state") != "ADMITTED" or admission.get("errors") != []:
        raise AssertionError("FINAL_ADMISSION_INDEPENDENT_VERIFIER")

    selector_product, selector_stats = base.eliminate_var_capped(source, 1, promotion.CAP)
    if selector_product != product:
        raise AssertionError("LOCAL_SELECTOR_PRODUCT_MISMATCH")
    if not base.verify_elimination_transition(source, 1, product, promotion.CAP):
        raise AssertionError("LOCAL_SELECTOR_TRANSITION_REPLAY")
    return {
        "receipt_path": str(FINAL_ADMISSION_PATH),
        "receipt_sha256": FINAL_ADMISSION_SHA256,
        "evidence_commit": receipt.get("subject", {}).get("evidence_commit"),
        "exact_head_workflow_run": receipt.get("exact_head_workflow", {}).get("run_id"),
        "admission_artifact_id": receipt.get("authority_artifacts", {}).get("admission", {}).get("artifact_id"),
        "composite_artifact_id": receipt.get("authority_artifacts", {}).get("composite", {}).get("artifact_id"),
        "independent_admission_state": admission.get("state"),
        "reachable_at_frozen_ordinary_callsite": True,
        "unmodified_core_prefix": True,
        "local_exact_selector_transition_replayed": True,
        "selector_stats": selector_stats,
    }


def partition_commitment(product: base.CNF, pivot: int) -> dict[str, Any]:
    unaffected: list[base.Clause] = []
    positive_tails: list[base.Clause] = []
    negative_tails: list[base.Clause] = []
    mapping: list[dict[str, Any]] = []

    for index, clause in enumerate(product):
        if pivot in clause and -pivot in clause:
            raise AssertionError("TAUTOLOGICAL_PIVOT_CLAUSE")
        if pivot in clause:
            tail = tuple(lit for lit in clause if lit != pivot)
            positive_tails.append(tail)
            mapping.append({"source_index": index, "role": "P", "tail_index": len(positive_tails) - 1})
        elif -pivot in clause:
            tail = tuple(lit for lit in clause if lit != -pivot)
            negative_tails.append(tail)
            mapping.append({"source_index": index, "role": "N", "tail_index": len(negative_tails) - 1})
        else:
            unaffected.append(clause)
            mapping.append({"source_index": index, "role": "U", "tail_index": len(unaffected) - 1})

    rebuilt: list[base.Clause] = []
    for row in mapping:
        role = row["role"]
        index = int(row["tail_index"])
        if role == "U":
            rebuilt.append(unaffected[index])
        elif role == "P":
            clause = base.canon_clause((pivot, *positive_tails[index]))
            if clause is None:
                raise AssertionError("POSITIVE_PARTITION_REBUILD_TAUTOLOGY")
            rebuilt.append(clause)
        elif role == "N":
            clause = base.canon_clause((-pivot, *negative_tails[index]))
            if clause is None:
                raise AssertionError("NEGATIVE_PARTITION_REBUILD_TAUTOLOGY")
            rebuilt.append(clause)
        else:
            raise AssertionError("UNKNOWN_PARTITION_ROLE")
    if tuple(rebuilt) != product:
        raise AssertionError("PARTITION_REPLAY_MISMATCH")

    return {
        "unaffected_clause_count": len(unaffected),
        "positive_tail_count": len(positive_tails),
        "negative_tail_count": len(negative_tails),
        "source_mapping_count": len(mapping),
        "unaffected_sha256": canonical_json_sha256([list(c) for c in unaffected]),
        "positive_tails_sha256": canonical_json_sha256([list(c) for c in positive_tails]),
        "negative_tails_sha256": canonical_json_sha256([list(c) for c in negative_tails]),
        "source_partition_mapping_sha256": canonical_json_sha256(mapping),
        "partition_replays_source_exactly": True,
    }


def validate_expected(actual: dict[str, Any], expected: dict[str, Any]) -> None:
    for key, value in expected.items():
        if actual.get(key) != value:
            raise AssertionError(f"EXPECTED_HOLDOUT_DRIFT:{key}:{actual.get(key)!r}!={value!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--expected-branch", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    spec = load_spec()
    head = git_text("rev-parse", "HEAD")
    branch = git_text("rev-parse", "--abbrev-ref", "HEAD")
    if head != args.expected_commit:
        raise AssertionError("EXACT_HEAD_MISMATCH")
    if branch != args.expected_branch:
        raise AssertionError("EXACT_BRANCH_MISMATCH")

    reserved_paths = [Path(path) for path in spec["future_factorizer_reserved_paths"]]
    present_reserved = [str(path) for path in reserved_paths if path.exists()]
    if present_reserved:
        raise AssertionError(f"FUTURE_FACTORIZER_ALREADY_PRESENT:{present_reserved}")

    source, product = promotion.candidate()
    reachability = admitted_reachability_binding(source, product)

    live_roots = [v for v in base.canonical_pivot_order(promotion.direct_target_state(source, product)) if v in set(base.vars_of(product))]
    pivot = live_roots[0]
    out, stats = base.eliminate_var_capped(product, pivot, promotion.CAP)
    positive = [clause for clause in product if pivot in clause]
    negative = [clause for clause in product if -pivot in clause]
    unaffected = [clause for clause in product if pivot not in clause and -pivot not in clause]

    if out is not None:
        raise AssertionError("HOLDOUT_PIVOT_UNEXPECTEDLY_FITS_CAP")
    if stats.get("aborted") is not True or int(stats.get("raw_units", -1)) <= promotion.CAP:
        raise AssertionError("STRICT_MONOTONE_CAP_CROSSING_NOT_OBSERVED")

    actual = {
        "family": "DISJOINT_SELECTOR_PRODUCT",
        "seed": promotion.SEED,
        "source_fingerprint": base.fingerprint(source),
        "context_fingerprint": base.fingerprint(product),
        "N": promotion.N,
        "cap": promotion.CAP,
        "context_state_units": base.state_units(product),
        "context_clause_count": len(product),
        "canonical_first_live_root_pivot": pivot,
        "positive_occurrences": len(positive),
        "negative_occurrences": len(negative),
        "unaffected_clauses": len(unaffected),
        "raw_parent_pairs": len(positive) * len(negative),
        "pairs_examined_at_first_crossing": int(stats["pairs"]),
        "tautologies_at_first_crossing": int(stats["tautologies"]),
        "first_crossing_raw_units": int(stats["raw_units"]),
        "first_crossing_margin": int(stats["raw_units"]) - promotion.CAP,
        "reachable_at_frozen_ordinary_callsite": True,
        "original_capped_elimination_result": "NONE__STRICT_CAP_CROSSING",
    }
    validate_expected(actual, spec["expected_holdout"])

    partition = partition_commitment(product, pivot)
    if partition["unaffected_clause_count"] != len(unaffected):
        raise AssertionError("PARTITION_UNAFFECTED_COUNT")
    if partition["positive_tail_count"] != len(positive):
        raise AssertionError("PARTITION_POSITIVE_COUNT")
    if partition["negative_tail_count"] != len(negative):
        raise AssertionError("PARTITION_NEGATIVE_COUNT")

    report = {
        "schema": "JANUS/C025/FACTORIZED-RESOLUTION-PRODUCT/39100-HOLDOUT-EVIDENCE/v1",
        "status": EXPECTED_STATUS,
        "subject": {
            "repository": "Hawkar-usls/Janus-Fundamentum",
            "branch": branch,
            "commit": head,
            "tree": git_text("rev-parse", "HEAD^{tree}"),
        },
        "specification": {
            "path": str(SPEC_PATH),
            "sha256": sha256_file(SPEC_PATH),
            "schema": spec["schema"],
        },
        "chronology": spec["chronology"],
        "holdout": actual,
        "admitted_reachability_binding": reachability,
        "partition_commitment_for_future_independent_replay": partition,
        "future_factorizer_reserved_paths": [str(path) for path in reserved_paths],
        "future_factorizer_paths_present": present_reserved,
        "factorizer_imported_or_executed": False,
        "scientific_boundary": spec["scientific_boundary"],
        "P_VS_NP": P_VS_NP,
    }
    Path(args.out).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
