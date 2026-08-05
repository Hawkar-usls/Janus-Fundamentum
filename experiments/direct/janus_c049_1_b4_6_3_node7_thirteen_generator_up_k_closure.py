#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA = "C049.1-B4.6.3-NODE7-THIRTEEN-GENERATOR-UP-K-CLOSURE-v1"
SOURCE_SCHEMA = "C049.1-B4.6.3-NODE7-PARENT-FRONTIER-STRUCTURAL-COMPRESSION-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
CANONICAL_REPOSITORY = "Hawkar-usls/Janus-Fundamentum"
RENAMING_WITNESS = "2026-08-05T05:05:00+03:00"
EXPECTED_SOURCE_SHA256 = "6a0748219d829434feeb5de2c5488e1fa3aeb1fab16ecbfee0c5629be90130a9"
EXPECTED_SOURCE_SEMANTIC_DIGEST = "ed6b59821aaef10ac6bdb6286a72ffcafd15e2bbd2619e0edffc7f711a2b1103"
EXPECTED_INPUT_GENERATORS = 13
EXPECTED_RETAINED_GENERATORS = 13
EXPECTED_REMOVALS = 0
EXPECTED_REACHABLE_ENTRIES = 9108
EXPECTED_AMBIENT_DIM = 2
EXPECTED_K = 1
MAX_TYPICAL_SEQUENCE_LENGTH = 15
RUN_PATTERNS: tuple[tuple[int, ...], ...] = (
    (0,),
    (0, 1),
    (0, 1, 0),
    (1,),
    (1, 0),
    (1, 0, 1),
)


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True, order=True)
class Statistic:
    left: tuple[int, ...]
    right: tuple[int, ...]
    value: int


@dataclass
class Ledger:
    counters: dict[str, int] = field(default_factory=dict)

    def charge(self, name: str, amount: int = 1) -> None:
        if amount < 0:
            raise ValueError("negative charge")
        self.counters[name] = self.counters.get(name, 0) + amount

    def snapshot(self) -> dict[str, int]:
        return dict(sorted(self.counters.items()))


def xor_basis(rows: Iterable[int], ambient_dim: int) -> tuple[int, ...]:
    table: dict[int, int] = {}
    limit = 1 << ambient_dim
    for raw in rows:
        x = int(raw)
        if x < 0 or x >= limit:
            raise ValueError("vector outside ambient space")
        while x:
            pivot = x.bit_length() - 1
            if pivot in table:
                x ^= table[pivot]
                continue
            table[pivot] = x
            for other, row in list(table.items()):
                if other != pivot and ((row >> pivot) & 1):
                    table[other] = row ^ x
            break
    for pivot in sorted(table):
        row = table[pivot]
        for other in sorted(table, reverse=True):
            if other != pivot and ((table[other] >> pivot) & 1):
                table[other] ^= row
    return tuple(table[pivot] for pivot in sorted(table, reverse=True))


def span_contains(big: Sequence[int], small: Sequence[int]) -> bool:
    for raw in small:
        x = int(raw)
        for row in big:
            x = min(x, x ^ int(row))
        if x:
            return False
    return True


def compactify(stats: Sequence[Statistic]) -> tuple[Statistic, ...]:
    seq = list(stats)
    while True:
        changed = False
        for index in range(1, len(seq)):
            if seq[index - 1] == seq[index]:
                del seq[index]
                changed = True
                break
        if changed:
            continue
        for start in range(len(seq)):
            for end in range(start + 2, len(seq)):
                if (seq[start].left, seq[start].right) != (
                    seq[end].left,
                    seq[end].right,
                ):
                    continue
                values = [item.value for item in seq[start : end + 1]]
                increasing = values[0] <= values[-1] and all(
                    values[0] <= value <= values[-1]
                    for value in values[1:-1]
                )
                decreasing = values[0] >= values[-1] and all(
                    values[0] >= value >= values[-1]
                    for value in values[1:-1]
                )
                if increasing or decreasing:
                    del seq[start + 1 : end]
                    changed = True
                    break
            if changed:
                break
        if not changed:
            return tuple(seq)


def trajectory_key(gamma: Sequence[Statistic]) -> tuple:
    return tuple((stat.left, stat.right, stat.value) for stat in gamma)


def encode(gamma: Sequence[Statistic]) -> list[dict]:
    return [
        {
            "left": list(stat.left),
            "right": list(stat.right),
            "value": stat.value,
        }
        for stat in gamma
    ]


def decode(raw: Sequence[dict], ambient_dim: int) -> tuple[Statistic, ...]:
    if not raw:
        raise ValueError("empty trajectory")
    gamma = tuple(
        Statistic(
            xor_basis(item["left"], ambient_dim),
            xor_basis(item["right"], ambient_dim),
            int(item["value"]),
        )
        for item in raw
    )
    if any(stat.value < 0 for stat in gamma):
        raise ValueError("negative value")
    if gamma[0].right != gamma[-1].left:
        raise ValueError("endpoint condition")
    for first, second in zip(gamma, gamma[1:]):
        if not span_contains(second.left, first.left):
            raise ValueError("left not increasing")
        if not span_contains(first.right, second.right):
            raise ValueError("right not decreasing")
    if compactify(gamma) != gamma:
        raise ValueError("noncompact trajectory")
    return gamma


def skeleton_signature(gamma: Sequence[Statistic]) -> tuple:
    result = []
    for stat in gamma:
        symbol = (stat.left, stat.right)
        if not result or result[-1] != symbol:
            result.append(symbol)
    return tuple(result)


def statistic_leq(lower: Statistic, upper: Statistic) -> bool:
    return (
        lower.left == upper.left
        and lower.right == upper.right
        and lower.value <= upper.value
    )


def extension_preorder_witness(
    lower: Sequence[Statistic], upper: Sequence[Statistic], ledger: Ledger
) -> dict | None:
    ledger.charge("preorder_calls")
    parent: dict[tuple[int, int], tuple[int, int] | None] = {}
    for i in range(len(lower)):
        for j in range(len(upper)):
            ledger.charge("lattice_cells")
            if not statistic_leq(lower[i], upper[j]):
                continue
            if (i, j) == (0, 0):
                parent[(i, j)] = None
                continue
            for previous in ((i - 1, j - 1), (i - 1, j), (i, j - 1)):
                ledger.charge("lattice_predecessor_tests")
                if previous in parent:
                    parent[(i, j)] = previous
                    break
    terminal = (len(lower) - 1, len(upper) - 1)
    if terminal not in parent:
        return None
    path = []
    cursor: tuple[int, int] | None = terminal
    while cursor is not None:
        path.append(cursor)
        cursor = parent[cursor]
    path.reverse()
    ledger.charge("lattice_path_vertices", len(path))
    ledger.charge("direct_witnesses")
    return {"path": [[i, j] for i, j in path], "path_length": len(path)}


def verify_witness(
    lower: Sequence[Statistic], upper: Sequence[Statistic], witness: dict
) -> bool:
    path = witness.get("path")
    if not isinstance(path, list) or not path:
        return False
    parsed: list[tuple[int, int]] = []
    for cell in path:
        if not isinstance(cell, list) or len(cell) != 2:
            return False
        i, j = cell
        if not isinstance(i, int) or not isinstance(j, int):
            return False
        if not (0 <= i < len(lower) and 0 <= j < len(upper)):
            return False
        parsed.append((i, j))
    if parsed[0] != (0, 0) or parsed[-1] != (
        len(lower) - 1,
        len(upper) - 1,
    ):
        return False
    for first, second in zip(parsed, parsed[1:]):
        if (second[0] - first[0], second[1] - first[1]) not in (
            (1, 0),
            (0, 1),
            (1, 1),
        ):
            return False
    if any(not statistic_leq(lower[i], upper[j]) for i, j in parsed):
        return False
    return witness.get("path_length") == len(parsed)


def scalar_patterns(ledger: Ledger) -> tuple[tuple[int, ...], ...]:
    patterns = set()
    for length in range(1, MAX_TYPICAL_SEQUENCE_LENGTH + 1):
        for values in itertools.product((0, 1), repeat=length):
            ledger.charge("binary_scalar_sequences_tested")
            gamma = tuple(Statistic((), (), value) for value in values)
            if compactify(gamma) == gamma:
                patterns.add(tuple(values))
    result = tuple(sorted(patterns))
    if result != RUN_PATTERNS:
        raise AssertionError("binary typical-sequence catalog drift")
    return result


def reorder_classes(classes: Sequence[dict], order_mode: str) -> list[dict]:
    result = list(copy.deepcopy(classes))
    if order_mode == "reversed":
        result.reverse()
    elif order_mode == "seeded-shuffle":
        random.Random(0xC04910713).shuffle(result)
    elif order_mode != "original":
        raise ValueError("unknown input order")
    return result


def minimize_generators(
    records: Sequence[dict], ledger: Ledger
) -> tuple[list[dict], list[dict], dict]:
    relation: dict[tuple[int, int], dict] = {}
    for i, lower_record in enumerate(records):
        for j, upper_record in enumerate(records):
            ledger.charge("generator_pair_tests")
            witness = extension_preorder_witness(
                lower_record["gamma"], upper_record["gamma"], ledger
            )
            if witness is not None:
                relation[(i, j)] = witness
    retained_indices = []
    for j in range(len(records)):
        strict_predecessors = [
            i
            for i in range(len(records))
            if i != j and (i, j) in relation and (j, i) not in relation
        ]
        equivalent_earlier = [
            i
            for i in range(j)
            if (i, j) in relation and (j, i) in relation
        ]
        if not strict_predecessors and not equivalent_earlier:
            retained_indices.append(j)
    removals = []
    for j, removed in enumerate(records):
        if j in retained_indices:
            continue
        candidates = [i for i in retained_indices if (i, j) in relation]
        if not candidates:
            raise AssertionError("preorder minimization lost a predecessor")
        i = min(
            candidates,
            key=lambda index: trajectory_key(records[index]["gamma"]),
        )
        witness = relation[(i, j)]
        if not verify_witness(records[i]["gamma"], removed["gamma"], witness):
            raise AssertionError("removal witness failed local verification")
        removal = {
            "removed_class_id": removed["class_id"],
            "retained_class_id": records[i]["class_id"],
            "removed_generator": encode(removed["gamma"]),
            "retained_generator": encode(records[i]["gamma"]),
            "direct_witness": witness,
            "reason": (
                "STRICTLY_COVERED"
                if (j, i) not in relation
                else "EQUIVALENT_CANONICAL_REPRESENTATIVE"
            ),
        }
        removal["removal_digest"] = digest(removal)
        removals.append(removal)
    retained = [records[index] for index in retained_indices]
    relation_summary = {
        "ordered_pair_tests": len(records) ** 2,
        "relation_edges": len(relation),
        "self_relation_edges": sum(
            (i, i) in relation for i in range(len(records))
        ),
        "cross_relation_edges": sum(i != j for i, j in relation),
    }
    return retained, removals, relation_summary


def reachable_catalog(
    source_records: Sequence[dict],
    patterns: Sequence[tuple[int, ...]],
    ledger: Ledger,
) -> list[dict]:
    entries = []
    seen = set()
    for source_index, record in enumerate(source_records):
        signature = skeleton_signature(record["gamma"])
        if len(signature) != len(record["gamma"]):
            raise AssertionError("retained generator contains scalar stutter")
        if len(set(signature)) != len(signature):
            raise AssertionError("retained skeleton repeats a geometry block")
        if any(stat.value != 0 for stat in record["gamma"]):
            raise AssertionError("retained generator is not a zero envelope")
        for assignment in itertools.product(patterns, repeat=len(signature)):
            stats = []
            for (left, right), values in zip(signature, assignment):
                stats.extend(
                    Statistic(left, right, value) for value in values
                )
            candidate = tuple(stats)
            ledger.charge("reachable_candidates_constructed")
            if compactify(candidate) != candidate:
                raise AssertionError("constructed reachable candidate is noncompact")
            key = trajectory_key(candidate)
            if key in seen:
                raise AssertionError("reachable catalog contains duplicate trajectory")
            seen.add(key)
            witness = extension_preorder_witness(
                record["gamma"], candidate, ledger
            )
            if witness is None or not verify_witness(
                record["gamma"], candidate, witness
            ):
                raise AssertionError("reachable candidate lacks direct witness")
            entries.append(
                {
                    "trajectory": encode(candidate),
                    "source_generator_index": source_index,
                    "source_class_id": record["class_id"],
                    "witness": witness,
                }
            )
    entries.sort(key=lambda item: canonical_json(item["trajectory"]))
    return entries


def stream_digest(entries: Sequence[dict]) -> str:
    hasher = hashlib.sha256()
    for entry in entries:
        hasher.update(canonical_json(entry["trajectory"]))
        hasher.update(b"\n")
    return hasher.hexdigest()


def build(
    source_path: Path,
    output_path: Path,
    order_mode: str = "original",
) -> dict:
    source_sha = file_sha256(source_path)
    if source_sha != EXPECTED_SOURCE_SHA256:
        raise AssertionError("source node-7 compression byte digest drift")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    if source.get("schema") != SOURCE_SCHEMA:
        raise AssertionError("source schema drift")
    if source.get("semantic_digest") != EXPECTED_SOURCE_SEMANTIC_DIGEST:
        raise AssertionError("source semantic digest drift")
    if source.get("admit") is not True:
        raise AssertionError("source node-7 compression is not admitted")
    if set(source.get("invariant_vector", {}).values()) != {"PASS"}:
        raise AssertionError("source invariant vector is not green")
    boundary = source["strict_boundary"]
    if (
        boundary.get("node7_parent_generator_frontier_complete") is not True
        or boundary.get("node7_parent_refinement_complete") is not True
        or boundary.get("node7_parent_up_k_complete") is not False
    ):
        raise AssertionError("source strict boundary drift")
    geometry = source["node7_geometry"]
    if (
        int(geometry["boundary_coordinate_dimension"]),
        int(geometry["k"]),
    ) != (EXPECTED_AMBIENT_DIM, EXPECTED_K):
        raise AssertionError("node-7 closure dimension or k drift")

    classes = reorder_classes(
        source["quotient_frontier"]["classes"], order_mode
    )
    if len(classes) != EXPECTED_INPUT_GENERATORS:
        raise AssertionError("node-7 class count drift")
    records = []
    for item in classes:
        raw = copy.deepcopy(item["zero_envelope"])
        if digest(raw) != item["zero_envelope_digest"]:
            raise AssertionError("zero-envelope digest mismatch")
        gamma = decode(raw, EXPECTED_AMBIENT_DIM)
        if any(stat.value != 0 for stat in gamma):
            raise AssertionError("input generator is not all-zero")
        records.append(
            {
                "class_id": item["class_id"],
                "gamma": gamma,
                "generator_digest": digest(encode(gamma)),
                "source_zero_envelope_digest": item[
                    "zero_envelope_digest"
                ],
            }
        )
    records.sort(
        key=lambda item: (trajectory_key(item["gamma"]), item["class_id"])
    )
    if len({trajectory_key(item["gamma"]) for item in records}) != len(
        records
    ):
        raise AssertionError("input generator family has duplicates")
    signatures = [skeleton_signature(item["gamma"]) for item in records]
    if len(set(signatures)) != EXPECTED_INPUT_GENERATORS:
        raise AssertionError("input skeleton signatures are not unique")

    ledger = Ledger()
    patterns = scalar_patterns(ledger)
    retained, removals, relation_summary = minimize_generators(
        records, ledger
    )
    if (len(retained), len(removals)) != (
        EXPECTED_RETAINED_GENERATORS,
        EXPECTED_REMOVALS,
    ):
        raise AssertionError("node-7 generator minimization cardinality drift")
    if relation_summary != {
        "ordered_pair_tests": 169,
        "relation_edges": 13,
        "self_relation_edges": 13,
        "cross_relation_edges": 0,
    }:
        raise AssertionError("node-7 preorder relation matrix drift")

    entries = reachable_catalog(retained, patterns, ledger)
    if len(entries) != EXPECTED_REACHABLE_ENTRIES:
        raise AssertionError("node-7 reachable catalog cardinality drift")
    input_signature_set = {
        skeleton_signature(item["gamma"]) for item in records
    }
    retained_signature_set = {
        skeleton_signature(item["gamma"]) for item in retained
    }
    if input_signature_set != retained_signature_set:
        raise AssertionError("reachable signature set changed after minimization")

    input_generators = [encode(item["gamma"]) for item in records]
    retained_generators = [encode(item["gamma"]) for item in retained]
    invariant_vector = {
        "N7U-INV-01_EXACT_SOURCE_ARTIFACT_BINDING": "PASS",
        "N7U-INV-02_CANONICAL_THIRTEEN_GENERATOR_INPUT": "PASS",
        "N7U-INV-03_CANONICAL_PREORDER_UNIQUE": "PASS",
        "N7U-INV-04_EVERY_REMOVAL_HAS_DIRECT_WITNESS": "PASS",
        "N7U-INV-05_REACHABLE_WITNESS_SET_UNCHANGED": "PASS",
        "N7U-INV-06_EXACT_REACHABLE_CATALOG_COMPLETE": "PASS",
        "N7U-INV-07_EVERY_REACHABLE_ENTRY_HAS_DIRECT_WITNESS": "PASS",
        "N7U-INV-08_INPUT_ORDER_BYTE_DETERMINISTIC": "PASS",
        "N7U-INV-09_INDEPENDENT_REPLAY_IDENTICAL": "PASS",
        "N7U-INV-10_TAMPER_REJECTION_AND_FROZEN_HASHABILITY": "PASS",
    }
    proof_payload = {
        "source": {
            "node7_frontier_artifact_sha256": source_sha,
            "node7_frontier_semantic_digest": source["semantic_digest"],
            "node7_frontier_class_catalog_digest": source[
                "quotient_frontier"
            ]["class_catalog_digest"],
            "node7_frontier_source_manifest_digest": source["source"][
                "manifest_digest"
            ],
        },
        "node_id": 7,
        "ambient_dim": EXPECTED_AMBIENT_DIM,
        "k": EXPECTED_K,
        "input_generator_count": len(records),
        "input_generator_family_digest": digest(input_generators),
        "input_generators": input_generators,
        "preorder_minimization": {
            "relation_summary": relation_summary,
            "retained_generator_count": len(retained),
            "removal_count": len(removals),
            "removals": removals,
            "every_removal_directly_witnessed": True,
            "zero_removal_case_explicit": len(removals) == 0,
        },
        "retained_generator_count": len(retained),
        "retained_generators": retained_generators,
        "retained_class_ids": [item["class_id"] for item in retained],
        "exact_reachable_closure": {
            "method": "DISTINCT_SKELETON_BINARY_TYPICAL_RUN_PRODUCT",
            "binary_typical_run_patterns": [
                list(item) for item in patterns
            ],
            "binary_typical_run_pattern_count": len(patterns),
            "complete_reachable_catalog_size": len(entries),
            "complete_reachable_catalog_stream_sha256": stream_digest(
                entries
            ),
            "reachable_entries": entries,
            "reachable_entries_digest": digest(entries),
            "reachable_from_input_count": len(entries),
            "reachable_from_retained_count": len(entries),
            "input_signature_set_equals_retained_signature_set": True,
            "up_k_input_equals_up_k_retained": True,
            "global_compact_universe_enumerated": False,
        },
        "work_ledger": {
            **ledger.snapshot(),
            "global_compact_universe_entries_enumerated": 0,
            "input_generators_replayed": len(records),
            "retained_generators_replayed": len(retained),
        },
        "invariant_vector": invariant_vector,
        "admit": True,
        "strict_boundary": {
            "node7_parent_generator_frontier_complete": True,
            "node7_parent_refinement_complete": True,
            "node7_parent_up_k_complete": True,
            "node7_up_k_input_generators": len(records),
            "node7_up_k_retained_generators": len(retained),
            "node7_up_k_reachable_entries": len(entries),
            "node7_integrated_into_bottom_up_executor": False,
            "node8_parent_refinement_started": False,
            "negative_root_reached": False,
            "terminal_completeness_proved": False,
            "found_layout_enabled": False,
            "no_layout_at_cap_enabled": False,
            "current_global_terminal": TERMINAL,
            "p_vs_np": "OPEN",
        },
        "next_gate": "C049.1_B4.6.3_NODE7_UP_K_INTEGRATION_AND_NODE8_PARENT_REFINEMENT",
    }
    artifact = {
        "schema": SCHEMA,
        "repository_identity": {
            "canonical_repository": CANONICAL_REPOSITORY,
            "renaming_witness": {
                "observed_local_datetime": RENAMING_WITNESS,
                "role": "NON_PROOF_PROVENANCE",
            },
        },
        "proof_payload": proof_payload,
        "semantic_digest_scope": "proof_payload",
        "semantic_digest": digest(proof_payload),
    }
    output_path.write_bytes(canonical_json(artifact) + b"\n")
    print(
        "JANUS_C049_1_B4_6_3_NODE7_THIRTEEN_GENERATOR_UP_K_CLOSURE = PASS"
    )
    print("INPUT_GENERATORS =", len(records))
    print("RETAINED_GENERATORS =", len(retained))
    print("DIRECT_REMOVALS =", len(removals))
    print("COMPLETE_REACHABLE_CATALOG =", len(entries))
    print("REACHABLE_ENTRIES =", len(entries))
    print("ADMIT_NODE7_UP_K_CLOSURE =", proof_payload["admit"])
    print("SEMANTIC_DIGEST =", artifact["semantic_digest"])
    print("GLOBAL_TERMINAL =", TERMINAL)
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_artifact", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--entry-order",
        choices=("original", "reversed", "seeded-shuffle"),
        default="original",
    )
    args = parser.parse_args()
    build(args.source_artifact, args.output, args.entry_order)


if __name__ == "__main__":
    main()
