#!/usr/bin/env python3
"""Exact flat-CNF to resolution-product factor constructor.

For one pivot x, a canonical CNF is partitioned as

    U and (and_i (x or A_i)) and (and_j (-x or B_j)).

The emitted node denotes exactly

    U and ((and_i A_i) or (and_j B_j)),

which is existential elimination of x.  Construction scans source clauses once
and never enumerates the positive-times-negative resolution cross-product.

This module constructs one local factor node.  It does not implement operations
on nested factor DAGs and does not claim successor totality.  P_VS_NP is OPEN.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base

P_VS_NP = "OPEN"
CANONICALIZATION_VERSION = "C025_CANON_CNF_SORT_LEN_TUPLE_SUBSUMPTION_V1"
NODE_SCHEMA = "JANUS/C025/EXACT-RESOLUTION-PRODUCT-FACTOR/NODE/v1"
CERT_SCHEMA = "JANUS/C025/EXACT-RESOLUTION-PRODUCT-FACTOR/CERTIFICATE/v1"
BUNDLE_SCHEMA = "JANUS/C025/EXACT-RESOLUTION-PRODUCT-FACTOR/BUNDLE/v1"
REPRESENTATION_FIXED_UNITS = 32
CERTIFICATE_FIXED_UNITS = 16
LEDGER_FIXED_UNITS = 24


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_value(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def clauses_json(rows: Iterable[base.Clause]) -> list[list[int]]:
    return [list(clause) for clause in rows]


def clause_storage_units(rows: Sequence[base.Clause]) -> int:
    return sum(1 + len(clause) for clause in rows)


def _require_canonical_source(source: base.CNF) -> None:
    for clause in source:
        if base.canon_clause(clause) != clause:
            raise ValueError("SOURCE_CLAUSE_NOT_CANONICAL")
    if tuple(sorted(set(source), key=lambda clause: (len(clause), clause))) != source:
        raise ValueError("SOURCE_CNF_ORDER_OR_DUPLICATE_DRIFT")
    # Strict subsumption can only occur from a shorter clause into a longer one.
    # Equal-width states such as the frozen 39100 holdout therefore take no
    # quadratic subset path; mixed-width inputs are still checked exactly.
    if len({len(clause) for clause in source}) > 1:
        sets = [frozenset(clause) for clause in source]
        for right_index, right in enumerate(sets):
            for left_index in range(right_index):
                if sets[left_index] <= right:
                    raise ValueError("SOURCE_CNF_CONTAINS_SUBSUMED_CLAUSE")


def construct_exact_resolution_product_factor(
    source: base.CNF,
    *,
    pivot: int,
    state_cap: int,
    root_variables: Sequence[int],
    subject: dict[str, Any],
) -> dict[str, Any]:
    """Construct one exact factor node without executing a resolvent product."""
    if not isinstance(pivot, int) or pivot <= 0:
        raise ValueError("PIVOT_MUST_BE_POSITIVE_VARIABLE")
    if state_cap < 1:
        raise ValueError("STATE_CAP_MUST_BE_POSITIVE")
    _require_canonical_source(source)

    roots = tuple(sorted(set(int(value) for value in root_variables)))
    if any(value <= 0 for value in roots) or tuple(root_variables) != roots:
        raise ValueError("ROOT_VARIABLES_NOT_CANONICAL")
    if pivot not in roots:
        raise ValueError("PIVOT_NOT_ORIGINAL_ROOT")

    unaffected: list[base.Clause] = []
    positive_tails: list[base.Clause] = []
    negative_tails: list[base.Clause] = []
    mapping: list[dict[str, Any]] = []
    partition_scan_literal_visits = 0

    # Single source scan.  There is intentionally no loop over P x N.
    for source_index, clause in enumerate(source):
        partition_scan_literal_visits += len(clause)
        if pivot in clause and -pivot in clause:
            raise ValueError("CANONICAL_SOURCE_CONTAINS_PIVOT_TAUTOLOGY")
        if pivot in clause:
            tail = tuple(literal for literal in clause if literal != pivot)
            positive_tails.append(tail)
            mapping.append({"source_index": source_index, "role": "P", "tail_index": len(positive_tails) - 1})
        elif -pivot in clause:
            tail = tuple(literal for literal in clause if literal != -pivot)
            negative_tails.append(tail)
            mapping.append({"source_index": source_index, "role": "N", "tail_index": len(negative_tails) - 1})
        else:
            unaffected.append(clause)
            mapping.append({"source_index": source_index, "role": "U", "tail_index": len(unaffected) - 1})

    if not positive_tails or not negative_tails:
        raise ValueError("PIVOT_MUST_OCCUR_IN_BOTH_POLARITIES")
    if len(mapping) != len(source):
        raise AssertionError("PARTITION_NOT_TOTAL")
    if any(pivot in clause or -pivot in clause for clause in (*unaffected, *positive_tails, *negative_tails)):
        raise AssertionError("PIVOT_SURVIVED_FACTOR_ATOM")

    unaffected_json = clauses_json(unaffected)
    positive_json = clauses_json(positive_tails)
    negative_json = clauses_json(negative_tails)
    commitments = {
        "unaffected_clause_commitment": sha256_value(unaffected_json),
        "positive_tail_family_commitment": sha256_value(positive_json),
        "negative_tail_family_commitment": sha256_value(negative_json),
        "source_partition_commitment": sha256_value(mapping),
    }

    live_before = set(base.vars_of(source))
    live_after = {
        abs(literal)
        for clause in (*unaffected, *positive_tails, *negative_tails)
        for literal in clause
    }
    live_roots_before = sum(variable in live_before for variable in roots)
    live_roots_after = sum(variable in live_after for variable in roots)
    if live_roots_after != live_roots_before - 1 or pivot in live_after:
        raise AssertionError("LOCAL_ROOT_PROGRESS_NOT_EXACTLY_ONE")

    node_core = {
        "schema": NODE_SCHEMA,
        "node_type": "EXACT_RESOLUTION_PRODUCT_FACTOR",
        "pivot": pivot,
        "source_state_fingerprint": base.fingerprint(source),
        "source_clause_count": len(source),
        "source_state_units": base.state_units(source),
        "canonicalization_version": CANONICALIZATION_VERSION,
        "latent_semantics": "U_AND_OR_OF_POSITIVE_TAIL_CONJUNCTION_AND_NEGATIVE_TAIL_CONJUNCTION",
        "unaffected_clauses": unaffected_json,
        "positive_tail_family": positive_json,
        "negative_tail_family": negative_json,
        **commitments,
        "sharing": {
            "policy": "EXPLICIT_ATOMS_NO_IMPLICIT_EXPANSION_V1",
            "unaffected_atoms": len(unaffected),
            "positive_tail_atoms": len(positive_tails),
            "negative_tail_atoms": len(negative_tails),
            "all_atoms_resolve_to_committed_literal_lists": True,
        },
        "local_progress": {
            "progress_order": "LEXICOGRAPHIC_LIVE_ORIGINAL_ROOTS_THEN_LIVE_VARIABLES",
            "before": [live_roots_before, len(live_before)],
            "after": [live_roots_after, len(live_after)],
            "pivot_removed": True,
            "new_boolean_variables": 0,
            "strict": (live_roots_after, len(live_after)) < (live_roots_before, len(live_before)),
        },
        "subject": subject,
    }
    factor_node_fingerprint = sha256_value(node_core)
    factor_node = {**node_core, "factor_node_fingerprint": factor_node_fingerprint}

    certificate = {
        "schema": CERT_SCHEMA,
        "source_state_fingerprint": base.fingerprint(source),
        "pivot": pivot,
        "source_partition_mapping": mapping,
        "source_partition_commitment": commitments["source_partition_commitment"],
        "factor_node_fingerprint": factor_node_fingerprint,
        "partition_counts": {
            "U": len(unaffected),
            "P": len(positive_tails),
            "N": len(negative_tails),
            "total": len(mapping),
        },
        "identity": "EXISTS_PIVOT_SOURCE_EQUALS_U_AND_OR_AND_POSITIVE_TAILS_AND_NEGATIVE_TAILS",
    }

    representation_structural_units = (
        REPRESENTATION_FIXED_UNITS
        + clause_storage_units(unaffected)
        + clause_storage_units(positive_tails)
        + clause_storage_units(negative_tails)
    )
    certificate_reference_units = CERTIFICATE_FIXED_UNITS + 3 * len(mapping)
    combined_structural_units = representation_structural_units + certificate_reference_units + LEDGER_FIXED_UNITS
    input_state_units = base.state_units(source)
    atomic_max_live_units = input_state_units + combined_structural_units
    representation_bytes = len(canonical_json_bytes(factor_node))
    certificate_bytes = len(canonical_json_bytes(certificate))
    ledger_core = {
        "input_state_units": input_state_units,
        "input_bytes": len(canonical_json_bytes(clauses_json(source))),
        "partition_scan_literal_visits": partition_scan_literal_visits,
        "factor_nodes_created": 1,
        "tail_references": len(positive_tails) + len(negative_tails),
        "unique_tail_bytes": len(canonical_json_bytes({"P": positive_json, "N": negative_json})),
        "representation_bytes": representation_bytes,
        "certificate_bytes": certificate_bytes,
        "representation_structural_units": representation_structural_units,
        "certificate_reference_units": certificate_reference_units,
        "combined_structural_units": combined_structural_units,
        "verification_literal_visits": partition_scan_literal_visits * 2,
        "verification_hash_work": 6,
        "explicit_resolution_pairs_avoided": len(positive_tails) * len(negative_tails),
        "explicit_non_tautological_resolvents_if_diagnostic_only": None,
        "max_live_representation_units": atomic_max_live_units,
        "progress_before": [live_roots_before, len(live_before)],
        "progress_after": [live_roots_after, len(live_after)],
        "state_cap": state_cap,
        "hidden_expansion_executed": False,
        "factor_node_under_cap": combined_structural_units <= state_cap,
        "atomic_source_plus_factor_under_cap": atomic_max_live_units <= state_cap,
    }
    resource_ledger = {
        **ledger_core,
        "resource_ledger_bytes_without_self_field": len(canonical_json_bytes(ledger_core)),
    }
    combined_serialized_bytes = (
        representation_bytes
        + certificate_bytes
        + int(resource_ledger["resource_ledger_bytes_without_self_field"])
    )
    resource_ledger["combined_serialized_bytes"] = combined_serialized_bytes
    resource_ledger["combined_serialized_bytes_under_cap"] = combined_serialized_bytes <= state_cap

    if not resource_ledger["factor_node_under_cap"]:
        raise ValueError("FACTOR_NODE_EXCEEDS_STATE_CAP")
    if not resource_ledger["atomic_source_plus_factor_under_cap"]:
        raise ValueError("ATOMIC_FACTOR_TRANSITION_EXCEEDS_STATE_CAP")
    if not resource_ledger["combined_serialized_bytes_under_cap"]:
        raise ValueError("SERIALIZED_FACTOR_CERTIFICATE_EXCEEDS_STATE_CAP")

    return {
        "schema": BUNDLE_SCHEMA,
        "construction_state": "EXACT_FACTOR_NODE_CONSTRUCTED__INDEPENDENT_ADMISSION_REQUIRED",
        "factor_node": factor_node,
        "certificate": certificate,
        "resource_ledger": resource_ledger,
        "scientific_boundary": {
            "one_local_factor_transition_only": True,
            "nested_factor_dag_operations": "OPEN",
            "successor_grammar_totality": "OPEN",
            "P2_REACHABLE_PRESERVATION": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
        "P_VS_NP": P_VS_NP,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    source_doc = json.loads(Path(args.source).read_text(encoding="utf-8"))
    source = tuple(tuple(int(literal) for literal in clause) for clause in source_doc["source_cnf"])
    bundle = construct_exact_resolution_product_factor(
        source,
        pivot=int(source_doc["pivot"]),
        state_cap=int(source_doc["cap"]),
        root_variables=[int(value) for value in source_doc["root_variables"]],
        subject=dict(source_doc["subject"]),
    )
    Path(args.out).write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(bundle["resource_ledger"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
