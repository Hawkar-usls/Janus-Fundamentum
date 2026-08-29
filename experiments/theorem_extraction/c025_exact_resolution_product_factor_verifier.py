#!/usr/bin/env python3
"""Independent standard-library verifier for one exact resolution-product node.

The verifier does not import or call the constructor, JANUS engine, candidate
generator, or any project module.  It reconstructs the complete U/P/N partition
from the supplied flat source, recomputes every commitment/resource charge, and
executes the eight tamper cases frozen in the 2026-08-26 preregistration.
"""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

P_VS_NP = "OPEN"
CANONICALIZATION_VERSION = "C025_CANON_CNF_SORT_LEN_TUPLE_SUBSUMPTION_V1"
NODE_SCHEMA = "JANUS/C025/EXACT-RESOLUTION-PRODUCT-FACTOR/NODE/v1"
CERT_SCHEMA = "JANUS/C025/EXACT-RESOLUTION-PRODUCT-FACTOR/CERTIFICATE/v1"
BUNDLE_SCHEMA = "JANUS/C025/EXACT-RESOLUTION-PRODUCT-FACTOR/BUNDLE/v1"
REPRESENTATION_FIXED_UNITS = 32
CERTIFICATE_FIXED_UNITS = 16
LEDGER_FIXED_UNITS = 24
VERIFIER_PATH = Path("experiments/theorem_extraction/c025_exact_resolution_product_factor_verifier.py")
CONSTRUCTOR_PATH = Path("experiments/theorem_extraction/c025_exact_resolution_product_factor.py")
HOLDOUT_TREE = "09d10acc2cdcecd20f8cca4692679ebe0057e1f5"
EXPECTED_SOURCE_FINGERPRINT = "037cbc224816408ca1c76c65c9bb78ad660d3b612c40ef91d1ac76943c7c79c3"
EXPECTED_REPOSITORY = "Hawkar-usls/Janus-Fundamentum"
EXPECTED_BRANCH = "research/c025-phase5-9-polynomial-pivot-grammar-2026-08-28"
EXPECTED_HOLDOUT_COMMIT = "1978ad6a8b6eadbbd6b684369098492e2389fda6"
EXPECTED_HOLDOUT_RUN = 33247500837
EXPECTED_N = 1102
EXPECTED_CAP = 1_214_404
EXPECTED_PIVOT = 2
EXPECTED_ROOTS = tuple(range(1, 22))

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_value(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def fingerprint(cnf: CNF) -> str:
    return sha256_bytes(json.dumps([list(clause) for clause in cnf], separators=(",", ":")).encode("ascii"))


def literal_key(literal: int) -> tuple[int, bool]:
    return abs(literal), literal < 0


def canon_clause(raw: Iterable[int]) -> Clause | None:
    values = set(int(literal) for literal in raw)
    if 0 in values:
        raise ValueError("LITERAL_ZERO")
    if any(-literal in values for literal in values):
        return None
    return tuple(sorted(values, key=literal_key))


def parse_canonical_source(source_doc: dict[str, Any]) -> CNF:
    raw = source_doc.get("source_cnf")
    if not isinstance(raw, list):
        raise ValueError("SOURCE_CNF_NOT_LIST")
    clauses: list[Clause] = []
    for row in raw:
        if not isinstance(row, list):
            raise ValueError("SOURCE_CLAUSE_NOT_LIST")
        clause = tuple(int(literal) for literal in row)
        if canon_clause(clause) != clause:
            raise ValueError("SOURCE_CLAUSE_NOT_CANONICAL")
        clauses.append(clause)
    cnf = tuple(clauses)
    if tuple(sorted(set(cnf), key=lambda clause: (len(clause), clause))) != cnf:
        raise ValueError("SOURCE_ORDER_OR_DUPLICATE")
    if len({len(clause) for clause in cnf}) > 1:
        sets = [frozenset(clause) for clause in cnf]
        for right_index, right in enumerate(sets):
            for left_index in range(right_index):
                if sets[left_index] <= right:
                    raise ValueError("SOURCE_SUBSUMPTION")
    return cnf


def parse_clause_family(raw: Any, label: str) -> list[Clause]:
    if not isinstance(raw, list):
        raise ValueError(f"{label}_NOT_LIST")
    out: list[Clause] = []
    for row in raw:
        if not isinstance(row, list):
            raise ValueError(f"{label}_ROW_NOT_LIST")
        clause = tuple(int(literal) for literal in row)
        if canon_clause(clause) != clause:
            raise ValueError(f"{label}_ROW_NOT_CANONICAL")
        out.append(clause)
    return out


def vars_of(rows: Sequence[Clause]) -> set[int]:
    return {abs(literal) for clause in rows for literal in clause}


def state_units(rows: Sequence[Clause]) -> int:
    return 1 + len(rows) + sum(len(clause) for clause in rows)


def clause_storage_units(rows: Sequence[Clause]) -> int:
    return sum(1 + len(clause) for clause in rows)


def source_partition(source: CNF, pivot: int) -> tuple[list[Clause], list[Clause], list[Clause], list[dict[str, Any]], int]:
    unaffected: list[Clause] = []
    positive: list[Clause] = []
    negative: list[Clause] = []
    mapping: list[dict[str, Any]] = []
    visits = 0
    for source_index, clause in enumerate(source):
        visits += len(clause)
        if pivot in clause and -pivot in clause:
            raise ValueError("SOURCE_PIVOT_TAUTOLOGY")
        if pivot in clause:
            positive.append(tuple(literal for literal in clause if literal != pivot))
            mapping.append({"source_index": source_index, "role": "P", "tail_index": len(positive) - 1})
        elif -pivot in clause:
            negative.append(tuple(literal for literal in clause if literal != -pivot))
            mapping.append({"source_index": source_index, "role": "N", "tail_index": len(negative) - 1})
        else:
            unaffected.append(clause)
            mapping.append({"source_index": source_index, "role": "U", "tail_index": len(unaffected) - 1})
    return unaffected, positive, negative, mapping, visits


def exact_identity_truth_table() -> dict[str, Any]:
    """Exhaust the two family-conjunction truth values in the frozen identity.

    A denotes AND_i A_i and B denotes AND_j B_j.  U is conjoined unchanged on
    both sides, so the only nontrivial identity is

        exists x ((x or A) and ((not x) or B)) == (A or B).
    """
    rows: list[dict[str, Any]] = []
    mismatches = 0
    for positive_family_conjunction in (False, True):
        for negative_family_conjunction in (False, True):
            source_exists = any(
                (pivot_value or positive_family_conjunction)
                and ((not pivot_value) or negative_family_conjunction)
                for pivot_value in (False, True)
            )
            factor_value = positive_family_conjunction or negative_family_conjunction
            matches = source_exists == factor_value
            mismatches += int(not matches)
            rows.append({
                "positive_family_conjunction": positive_family_conjunction,
                "negative_family_conjunction": negative_family_conjunction,
                "exists_source": source_exists,
                "factor_value": factor_value,
                "matches": matches,
            })
    return {
        "identity": "EXISTS_X_X_OR_A_AND_NOT_X_OR_B_EQUALS_A_OR_B",
        "rows": rows,
        "tested": len(rows),
        "mismatches": mismatches,
        "exact": mismatches == 0,
    }


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


def validate(
    source_doc: dict[str, Any],
    bundle: dict[str, Any],
    *,
    expected_commit: str,
    expected_factorizer_parent: str,
    check_checkout: bool,
) -> list[str]:
    errors: list[str] = []
    try:
        source = parse_canonical_source(source_doc)
        pivot = int(source_doc.get("pivot"))
        cap = int(source_doc.get("cap"))
        roots = tuple(int(value) for value in source_doc.get("root_variables", []))
        subject = source_doc.get("subject", {})
        expect(set(source_doc) == {
            "schema", "source_cnf", "source_fingerprint", "source_state_units",
            "source_clause_count", "root_variables", "pivot", "N", "cap",
            "subject", "P_VS_NP",
        }, "SOURCE_FIELDS", errors)
        expect(source_doc.get("schema") == "JANUS/C025/EXACT-RESOLUTION-PRODUCT-FACTOR/SOURCE/v1", "SOURCE_SCHEMA", errors)
        source_fp = fingerprint(source)
        expect(source_doc.get("source_fingerprint") == source_fp, "SOURCE_FINGERPRINT", errors)
        expect(source_doc.get("source_fingerprint") == EXPECTED_SOURCE_FINGERPRINT, "HOLDOUT_FINGERPRINT", errors)
        expect(source_doc.get("source_state_units") == state_units(source), "SOURCE_UNITS", errors)
        expect(source_doc.get("source_clause_count") == len(source), "SOURCE_CLAUSE_COUNT", errors)
        expect(source_doc.get("P_VS_NP") == P_VS_NP, "SOURCE_P_VS_NP", errors)
        expect(source_doc.get("N") == EXPECTED_N, "SOURCE_N", errors)
        expect(cap == EXPECTED_CAP, "SOURCE_CAP", errors)
        expect(pivot == EXPECTED_PIVOT, "SOURCE_PIVOT", errors)
        expect(roots == EXPECTED_ROOTS, "SOURCE_ROOTS", errors)
        expect(subject == {
            "repository": EXPECTED_REPOSITORY,
            "branch": EXPECTED_BRANCH,
            "factorizer_commit": expected_commit,
            "factorizer_parent": expected_factorizer_parent,
            "holdout_commit": EXPECTED_HOLDOUT_COMMIT,
            "holdout_tree": HOLDOUT_TREE,
            "holdout_workflow_run": EXPECTED_HOLDOUT_RUN,
            "witness": 39100,
        }, "SOURCE_SUBJECT", errors)

        expect(set(bundle) == {
            "schema", "construction_state", "factor_node", "certificate",
            "resource_ledger", "scientific_boundary", "P_VS_NP",
        }, "BUNDLE_FIELDS", errors)
        expect(bundle.get("schema") == BUNDLE_SCHEMA, "BUNDLE_SCHEMA", errors)
        expect(
            bundle.get("construction_state") == "EXACT_FACTOR_NODE_CONSTRUCTED__INDEPENDENT_ADMISSION_REQUIRED",
            "CONSTRUCTION_STATE", errors,
        )
        expect(bundle.get("P_VS_NP") == P_VS_NP, "BUNDLE_P_VS_NP", errors)
        node = bundle.get("factor_node", {})
        cert = bundle.get("certificate", {})
        ledger = bundle.get("resource_ledger", {})
        expect(set(node) == {
            "schema", "node_type", "pivot", "source_state_fingerprint",
            "source_clause_count", "source_state_units", "canonicalization_version",
            "latent_semantics", "unaffected_clauses", "positive_tail_family",
            "negative_tail_family", "unaffected_clause_commitment",
            "positive_tail_family_commitment", "negative_tail_family_commitment",
            "source_partition_commitment", "sharing", "local_progress", "subject",
            "factor_node_fingerprint",
        }, "NODE_FIELDS", errors)
        expect(set(cert) == {
            "schema", "source_state_fingerprint", "pivot", "source_partition_mapping",
            "source_partition_commitment", "factor_node_fingerprint", "partition_counts",
            "identity",
        }, "CERT_FIELDS", errors)
        expect(node.get("schema") == NODE_SCHEMA, "NODE_SCHEMA", errors)
        expect(node.get("node_type") == "EXACT_RESOLUTION_PRODUCT_FACTOR", "NODE_TYPE", errors)
        expect(node.get("pivot") == pivot and cert.get("pivot") == pivot, "PIVOT_BINDING", errors)
        expect(node.get("source_state_fingerprint") == source_fp, "NODE_SOURCE_FP", errors)
        expect(cert.get("source_state_fingerprint") == source_fp, "CERT_SOURCE_FP", errors)
        expect(node.get("source_clause_count") == len(source), "NODE_SOURCE_COUNT", errors)
        expect(node.get("source_state_units") == state_units(source), "NODE_SOURCE_UNITS", errors)
        expect(node.get("canonicalization_version") == CANONICALIZATION_VERSION, "CANONICALIZATION_VERSION", errors)
        expect(
            node.get("latent_semantics") ==
            "U_AND_OR_OF_POSITIVE_TAIL_CONJUNCTION_AND_NEGATIVE_TAIL_CONJUNCTION",
            "LATENT_SEMANTICS", errors,
        )
        expect(node.get("subject") == subject, "NODE_SUBJECT", errors)

        unaffected, positive, negative, mapping, visits = source_partition(source, pivot)
        node_unaffected = parse_clause_family(node.get("unaffected_clauses"), "NODE_U")
        node_positive = parse_clause_family(node.get("positive_tail_family"), "NODE_P")
        node_negative = parse_clause_family(node.get("negative_tail_family"), "NODE_N")
        expect(node_unaffected == unaffected, "PARTITION_U", errors)
        expect(node_positive == positive, "PARTITION_P", errors)
        expect(node_negative == negative, "PARTITION_N", errors)
        expect((len(unaffected), len(positive), len(negative)) == (5130, 990, 1980), "HOLDOUT_PARTITION_COUNTS", errors)
        expect(cert.get("source_partition_mapping") == mapping, "PARTITION_MAPPING", errors)
        expect(len(mapping) == len(source), "PARTITION_TOTAL", errors)
        expect(bool(positive) and bool(negative), "BOTH_POLARITIES", errors)
        expect(all(pivot not in row and -pivot not in row for row in (*unaffected, *positive, *negative)), "PIVOT_REMOVED", errors)

        unaffected_json = [list(clause) for clause in unaffected]
        positive_json = [list(clause) for clause in positive]
        negative_json = [list(clause) for clause in negative]
        commitments = {
            "unaffected_clause_commitment": sha256_value(unaffected_json),
            "positive_tail_family_commitment": sha256_value(positive_json),
            "negative_tail_family_commitment": sha256_value(negative_json),
            "source_partition_commitment": sha256_value(mapping),
        }
        for key, value in commitments.items():
            expect(node.get(key) == value, f"NODE_COMMITMENT:{key}", errors)
        expect(cert.get("source_partition_commitment") == commitments["source_partition_commitment"], "CERT_PARTITION_COMMITMENT", errors)
        expect(node.get("sharing") == {
            "policy": "EXPLICIT_ATOMS_NO_IMPLICIT_EXPANSION_V1",
            "unaffected_atoms": len(unaffected),
            "positive_tail_atoms": len(positive),
            "negative_tail_atoms": len(negative),
            "all_atoms_resolve_to_committed_literal_lists": True,
        }, "SHARING_POLICY", errors)

        node_core = dict(node)
        supplied_node_fp = node_core.pop("factor_node_fingerprint", None)
        expected_node_fp = sha256_value(node_core)
        expect(supplied_node_fp == expected_node_fp, "FACTOR_NODE_FINGERPRINT", errors)
        expect(cert.get("factor_node_fingerprint") == expected_node_fp, "CERT_NODE_FINGERPRINT", errors)
        expect(cert.get("schema") == CERT_SCHEMA, "CERT_SCHEMA", errors)
        expect(
            cert.get("partition_counts") == {
                "U": len(unaffected), "P": len(positive), "N": len(negative), "total": len(mapping)
            },
            "CERT_PARTITION_COUNTS", errors,
        )
        expect(
            cert.get("identity") ==
            "EXISTS_PIVOT_SOURCE_EQUALS_U_AND_OR_AND_POSITIVE_TAILS_AND_NEGATIVE_TAILS",
            "CERT_IDENTITY", errors,
        )
        expect(exact_identity_truth_table()["exact"] is True, "EXACT_BOOLEAN_IDENTITY", errors)

        live_before = vars_of(source)
        live_after = vars_of([*unaffected, *positive, *negative])
        roots_set = set(roots)
        before_progress = [len(live_before & roots_set), len(live_before)]
        after_progress = [len(live_after & roots_set), len(live_after)]
        expected_progress = {
            "progress_order": "LEXICOGRAPHIC_LIVE_ORIGINAL_ROOTS_THEN_LIVE_VARIABLES",
            "before": before_progress,
            "after": after_progress,
            "pivot_removed": True,
            "new_boolean_variables": 0,
            "strict": tuple(after_progress) < tuple(before_progress),
        }
        expect(node.get("local_progress") == expected_progress, "LOCAL_PROGRESS", errors)
        expect(after_progress[0] == before_progress[0] - 1, "ONE_ROOT_REMOVED", errors)
        expect(pivot not in live_after, "PIVOT_ABSENT_AFTER", errors)

        representation_structural_units = (
            REPRESENTATION_FIXED_UNITS
            + clause_storage_units(unaffected)
            + clause_storage_units(positive)
            + clause_storage_units(negative)
        )
        certificate_reference_units = CERTIFICATE_FIXED_UNITS + 3 * len(mapping)
        combined_structural_units = representation_structural_units + certificate_reference_units + LEDGER_FIXED_UNITS
        input_units = state_units(source)
        atomic_max = input_units + combined_structural_units
        representation_bytes = len(canonical_json_bytes(node))
        certificate_bytes = len(canonical_json_bytes(cert))
        expected_ledger_core = {
            "input_state_units": input_units,
            "input_bytes": len(canonical_json_bytes([list(clause) for clause in source])),
            "partition_scan_literal_visits": visits,
            "factor_nodes_created": 1,
            "tail_references": len(positive) + len(negative),
            "unique_tail_bytes": len(canonical_json_bytes({"P": positive_json, "N": negative_json})),
            "representation_bytes": representation_bytes,
            "certificate_bytes": certificate_bytes,
            "representation_structural_units": representation_structural_units,
            "certificate_reference_units": certificate_reference_units,
            "combined_structural_units": combined_structural_units,
            "verification_literal_visits": visits * 2,
            "verification_hash_work": 6,
            "explicit_resolution_pairs_avoided": len(positive) * len(negative),
            "explicit_non_tautological_resolvents_if_diagnostic_only": None,
            "max_live_representation_units": atomic_max,
            "progress_before": before_progress,
            "progress_after": after_progress,
            "state_cap": cap,
            "hidden_expansion_executed": False,
            "factor_node_under_cap": combined_structural_units <= cap,
            "atomic_source_plus_factor_under_cap": atomic_max <= cap,
        }
        expected_ledger = {
            **expected_ledger_core,
            "resource_ledger_bytes_without_self_field": len(canonical_json_bytes(expected_ledger_core)),
        }
        expected_ledger["combined_serialized_bytes"] = (
            representation_bytes
            + certificate_bytes
            + expected_ledger["resource_ledger_bytes_without_self_field"]
        )
        expected_ledger["combined_serialized_bytes_under_cap"] = expected_ledger["combined_serialized_bytes"] <= cap
        expect(ledger == expected_ledger, "RESOURCE_LEDGER", errors)
        expect(expected_ledger["factor_node_under_cap"] is True, "FACTOR_UNDER_CAP", errors)
        expect(expected_ledger["atomic_source_plus_factor_under_cap"] is True, "ATOMIC_UNDER_CAP", errors)
        expect(expected_ledger["combined_serialized_bytes_under_cap"] is True, "SERIALIZED_UNDER_CAP", errors)
        expect(expected_ledger["hidden_expansion_executed"] is False, "NO_HIDDEN_EXPANSION", errors)
        expect(expected_ledger["explicit_resolution_pairs_avoided"] == 1_960_200, "HOLDOUT_PAIR_SCOPE", errors)

        boundary = bundle.get("scientific_boundary", {})
        expect(boundary.get("one_local_factor_transition_only") is True, "LOCAL_ONLY_BOUNDARY", errors)
        expect(boundary.get("nested_factor_dag_operations") == "OPEN", "NESTED_DAG_BOUNDARY", errors)
        expect(boundary.get("successor_grammar_totality") == "OPEN", "TOTALITY_BOUNDARY", errors)
        expect(boundary.get("P2_REACHABLE_PRESERVATION") == "OPEN", "P2_BOUNDARY", errors)
        expect(boundary.get("P_VS_NP") == P_VS_NP, "BOUNDARY_P_VS_NP", errors)

        if check_checkout:
            current_head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
            parent_line = subprocess.check_output(
                ["git", "rev-list", "--parents", "-n", "1", "HEAD"], text=True
            ).strip().split()
            parent_tree = subprocess.check_output(
                ["git", "show", "-s", "--format=%T", expected_factorizer_parent], text=True
            ).strip()
            expect(current_head == expected_commit, "CHECKOUT_HEAD", errors)
            expect(len(parent_line) == 2 and parent_line[1] == expected_factorizer_parent, "CHECKOUT_PARENT", errors)
            expect(parent_tree == HOLDOUT_TREE, "CHECKOUT_PARENT_TREE", errors)
            expect(project_imports(VERIFIER_PATH) == [], "VERIFIER_PROJECT_IMPORT", errors)
    except Exception as exc:  # fail closed on malformed/tampered structures
        errors.append(f"VALIDATION_EXCEPTION:{type(exc).__name__}:{exc}")
    return errors


def refresh_node_fingerprint(bundle: dict[str, Any]) -> None:
    node = bundle["factor_node"]
    core = dict(node)
    core.pop("factor_node_fingerprint", None)
    value = sha256_value(core)
    node["factor_node_fingerprint"] = value
    bundle["certificate"]["factor_node_fingerprint"] = value


def run_tamper_tests(
    source_doc: dict[str, Any],
    bundle: dict[str, Any],
    validator: Callable[[dict[str, Any], dict[str, Any]], list[str]],
) -> dict[str, Any]:
    def change_pivot(source: dict[str, Any], factor: dict[str, Any]) -> None:
        source["pivot"] = 3
        factor["factor_node"]["pivot"] = 3
        factor["certificate"]["pivot"] = 3
        refresh_node_fingerprint(factor)

    def drop_source_clause(source: dict[str, Any], _factor: dict[str, Any]) -> None:
        source["source_cnf"].pop()
        cnf = tuple(tuple(row) for row in source["source_cnf"])
        source["source_fingerprint"] = fingerprint(cnf)
        source["source_clause_count"] = len(cnf)
        source["source_state_units"] = state_units(cnf)

    def duplicate_mapping(_source: dict[str, Any], factor: dict[str, Any]) -> None:
        mapping = factor["certificate"]["source_partition_mapping"]
        mapping[-1] = copy.deepcopy(mapping[-2])

    def change_tail_literal(_source: dict[str, Any], factor: dict[str, Any]) -> None:
        row = factor["factor_node"]["positive_tail_family"][0]
        row[0] = -row[0]
        row.sort(key=lambda literal: (abs(literal), literal < 0))
        factor["factor_node"]["positive_tail_family_commitment"] = sha256_value(
            factor["factor_node"]["positive_tail_family"]
        )
        refresh_node_fingerprint(factor)

    def wrong_role(_source: dict[str, Any], factor: dict[str, Any]) -> None:
        factor["certificate"]["source_partition_mapping"][0]["role"] = "N"

    def change_source_fingerprint(source: dict[str, Any], factor: dict[str, Any]) -> None:
        value = "0" * 64
        source["source_fingerprint"] = value
        factor["factor_node"]["source_state_fingerprint"] = value
        factor["certificate"]["source_state_fingerprint"] = value
        refresh_node_fingerprint(factor)

    def change_node_fingerprint(_source: dict[str, Any], factor: dict[str, Any]) -> None:
        factor["factor_node"]["factor_node_fingerprint"] = "f" * 64
        factor["certificate"]["factor_node_fingerprint"] = "f" * 64

    def under_report_bytes(_source: dict[str, Any], factor: dict[str, Any]) -> None:
        factor["resource_ledger"]["representation_bytes"] -= 1
        factor["resource_ledger"]["certificate_bytes"] -= 1

    tests = [
        ("CHANGE_PIVOT", change_pivot),
        ("DROP_SOURCE_CLAUSE", drop_source_clause),
        ("DUPLICATE_MAPPING_OMIT_ANOTHER", duplicate_mapping),
        ("CHANGE_TAIL_LITERAL", change_tail_literal),
        ("MOVE_CLAUSE_TO_WRONG_ROLE", wrong_role),
        ("CHANGE_SOURCE_FINGERPRINT", change_source_fingerprint),
        ("CHANGE_FACTOR_NODE_FINGERPRINT", change_node_fingerprint),
        ("UNDER_REPORT_RESOURCE_BYTES", under_report_bytes),
    ]
    outcomes: list[dict[str, Any]] = []
    rejected = 0
    for name, mutate in tests:
        source_specimen = copy.deepcopy(source_doc)
        factor_specimen = copy.deepcopy(bundle)
        mutate(source_specimen, factor_specimen)
        errors = validator(source_specimen, factor_specimen)
        was_rejected = bool(errors)
        rejected += int(was_rejected)
        outcomes.append({"test": name, "rejected": was_rejected, "error_count": len(errors)})
    return {
        "tests": outcomes,
        "rejected": rejected,
        "total": len(tests),
        "false_accepts": len(tests) - rejected,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--factor", required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--expected-factorizer-parent", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    source_path = Path(args.source)
    factor_path = Path(args.factor)
    source_doc = json.loads(source_path.read_text(encoding="utf-8"))
    bundle = json.loads(factor_path.read_text(encoding="utf-8"))
    errors = validate(
        source_doc,
        bundle,
        expected_commit=args.expected_commit,
        expected_factorizer_parent=args.expected_factorizer_parent,
        check_checkout=True,
    )
    validator = lambda source, factor: validate(
        source,
        factor,
        expected_commit=args.expected_commit,
        expected_factorizer_parent=args.expected_factorizer_parent,
        check_checkout=False,
    )
    tamper = run_tamper_tests(source_doc, bundle, validator)
    if tamper["false_accepts"]:
        errors.append("TAMPER_FALSE_ACCEPT")

    admitted = not errors
    ledger = bundle.get("resource_ledger", {})
    report = {
        "schema": "JANUS/C025/EXACT-RESOLUTION-PRODUCT-FACTOR/INDEPENDENT-ADMISSION/v1",
        "admission_state": "ADMITTED_LOCAL_39100_FACTOR_TRANSITION" if admitted else "REJECTED_UNKNOWN_NO_ADMISSION",
        "subject": source_doc.get("subject"),
        "source_file_sha256": sha256_file(source_path),
        "factor_file_sha256": sha256_file(factor_path),
        "verifier": {
            "path": str(VERIFIER_PATH),
            "sha256": sha256_file(VERIFIER_PATH),
            "implementation_policy": "STANDARD_LIBRARY_ONLY_NO_CONSTRUCTOR_OR_PROJECT_IMPORT",
            "project_module_import_count": len(project_imports(VERIFIER_PATH)),
        },
        "constructor": {
            "path": str(CONSTRUCTOR_PATH),
            "sha256": sha256_file(CONSTRUCTOR_PATH),
            "called_by_verifier": False,
        },
        "coverage": {
            "reachable_witness": 39100,
            "pivot": source_doc.get("pivot"),
            "source_fingerprint": source_doc.get("source_fingerprint"),
            "exact_resolution_pairs_not_materialized": ledger.get("explicit_resolution_pairs_avoided"),
            "combined_structural_units": ledger.get("combined_structural_units"),
            "atomic_max_live_representation_units": ledger.get("max_live_representation_units"),
            "state_cap": ledger.get("state_cap"),
            "strict_local_progress": bundle.get("factor_node", {}).get("local_progress", {}).get("strict"),
            "exact_boolean_identity": exact_identity_truth_table(),
        },
        "tamper_rejection": tamper,
        "errors": errors,
        "scientific_boundary": {
            "frozen_L1_remains_refuted": True,
            "one_successor_local_move_covers_39100": admitted,
            "nested_factor_dag_operations": "OPEN",
            "successor_grammar_totality": "OPEN",
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
