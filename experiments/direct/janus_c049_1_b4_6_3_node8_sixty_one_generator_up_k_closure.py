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

SCHEMA = "C049.1-B4.6.3-NODE8-SIXTY-ONE-GENERATOR-UP-K-CLOSURE-v1"
SOURCE_SCHEMA = "C049.1-B4.6.3-NODE8-PARENT-FRONTIER-STRUCTURAL-COMPRESSION-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
CANONICAL_REPOSITORY = "Hawkar-usls/Janus-Fundamentum"
RENAMING_WITNESS = "2026-08-05T05:05:00+03:00"
EXPECTED_SOURCE_SHA256 = "93dcd5610eb9df079823b172a4f824ce1c09859e759c6b771dc95b99af394d34"
EXPECTED_SOURCE_SEMANTIC_DIGEST = "209f5a013ec492b67066abc3dcf08af183d2ec5ec0000f3d8d03a033cb32f9db"
EXPECTED_INPUT_GENERATORS = 61
EXPECTED_RETAINED_GENERATORS = 28
EXPECTED_DIRECT_REMOVALS = 33
EXPECTED_REACHABLE_ENTRIES = 15948
EXPECTED_AMBIENT_DIM = 3
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
    basis = tuple(int(x) for x in big)
    for raw in small:
        x = int(raw)
        for row in basis:
            x = min(x, x ^ row)
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
        {"left": list(stat.left), "right": list(stat.right), "value": stat.value}
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


def split_runs(gamma: Sequence[Statistic]) -> tuple[tuple, tuple[tuple[int, ...], ...]]:
    skeleton: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
    patterns: list[list[int]] = []
    for stat in gamma:
        symbol = (stat.left, stat.right)
        if not skeleton or skeleton[-1] != symbol:
            skeleton.append(symbol)
            patterns.append([stat.value])
        else:
            patterns[-1].append(stat.value)
    result = tuple(tuple(item) for item in patterns)
    if any(pattern not in RUN_PATTERNS for pattern in result):
        raise AssertionError("generator run outside binary typical catalog")
    if len(set(skeleton)) != len(skeleton):
        raise AssertionError("generator skeleton repeats a geometry block")
    return tuple(skeleton), result


def statistic_leq(lower: Statistic, upper: Statistic) -> bool:
    return (
        lower.left == upper.left
        and lower.right == upper.right
        and lower.value <= upper.value
    )


def extension_preorder_witness(
    lower: Sequence[Statistic], upper: Sequence[Statistic], ledger: Ledger | None = None
) -> dict | None:
    if ledger is not None:
        ledger.charge("preorder_calls")
    parent: dict[tuple[int, int], tuple[int, int] | None] = {}
    for i in range(len(lower)):
        for j in range(len(upper)):
            if ledger is not None:
                ledger.charge("lattice_cells")
            if not statistic_leq(lower[i], upper[j]):
                continue
            if (i, j) == (0, 0):
                parent[(i, j)] = None
                continue
            for previous in ((i - 1, j - 1), (i - 1, j), (i, j - 1)):
                if ledger is not None:
                    ledger.charge("lattice_predecessor_tests")
                if previous in parent:
                    parent[(i, j)] = previous
                    break
    terminal = (len(lower) - 1, len(upper) - 1)
    if terminal not in parent:
        return None
    path: list[tuple[int, int]] = []
    cursor: tuple[int, int] | None = terminal
    while cursor is not None:
        path.append(cursor)
        cursor = parent[cursor]
    path.reverse()
    if ledger is not None:
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


def scalar_catalog(ledger: Ledger) -> tuple[tuple[int, ...], ...]:
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


def scalar_relation(patterns: Sequence[tuple[int, ...]], ledger: Ledger) -> dict:
    edges = []
    allowed: dict[tuple[int, ...], list[tuple[int, ...]]] = {}
    for lower in patterns:
        lower_gamma = tuple(Statistic((), (), value) for value in lower)
        for upper in patterns:
            upper_gamma = tuple(Statistic((), (), value) for value in upper)
            witness = extension_preorder_witness(lower_gamma, upper_gamma, ledger)
            if witness is not None:
                edges.append(
                    {
                        "lower": list(lower),
                        "upper": list(upper),
                        "direct_witness": witness,
                    }
                )
                allowed.setdefault(lower, []).append(upper)
    for lower in patterns:
        allowed.setdefault(lower, [])
        allowed[lower].sort()
    edges.sort(key=canonical_json)
    return {
        "patterns": [list(pattern) for pattern in patterns],
        "relation_edges": edges,
        "relation_edge_count": len(edges),
        "allowed_upper_patterns": {
            "".join(str(x) for x in lower): [
                "".join(str(x) for x in upper) for upper in allowed[lower]
            ]
            for lower in patterns
        },
    }


def reorder_classes(classes: Sequence[dict], order_mode: str) -> list[dict]:
    result = list(copy.deepcopy(classes))
    if order_mode == "reversed":
        result.reverse()
    elif order_mode == "seeded-shuffle":
        random.Random(0xC04910861).shuffle(result)
    elif order_mode != "original":
        raise ValueError("unknown input order")
    return result


def normalize_records(classes: Sequence[dict], ambient_dim: int) -> list[dict]:
    records = []
    for source_index, item in enumerate(classes):
        gamma = decode(item["canonical_generator"], ambient_dim)
        skeleton, run_patterns = split_runs(gamma)
        records.append(
            {
                "class_id": str(item["class_id"]),
                "source_index": source_index,
                "source_generator_digest": str(item["generator_digest"]),
                "gamma": gamma,
                "skeleton": skeleton,
                "run_patterns": run_patterns,
            }
        )
    records.sort(key=lambda item: (trajectory_key(item["gamma"]), item["class_id"]))
    if len({trajectory_key(item["gamma"]) for item in records}) != len(records):
        raise AssertionError("duplicate input generator")
    return records


def minimize_generators(records: Sequence[dict], ledger: Ledger) -> tuple[list[dict], list[dict], dict]:
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
    retained_set = set(retained_indices)
    removals = []
    for j, removed in enumerate(records):
        if j in retained_set:
            continue
        candidates = [i for i in retained_indices if (i, j) in relation]
        if not candidates:
            raise AssertionError("removed generator lacks retained direct predecessor")
        i = min(candidates, key=lambda index: (trajectory_key(records[index]["gamma"]), records[index]["class_id"]))
        witness = relation[(i, j)]
        if not verify_witness(records[i]["gamma"], removed["gamma"], witness):
            raise AssertionError("removal witness failed")
        removal = {
            "removed_class_id": removed["class_id"],
            "retained_class_id": records[i]["class_id"],
            "removed_generator": encode(removed["gamma"]),
            "retained_generator": encode(records[i]["gamma"]),
            "direct_witness": witness,
            "witness_kind": "EXTENSION_PREORDER_DIRECT",
            "reason": "STRICTLY_COVERED",
        }
        removal["removal_digest"] = digest(removal)
        removals.append(removal)
    retained = [records[index] for index in retained_indices]
    retained.sort(key=lambda item: (trajectory_key(item["gamma"]), item["class_id"]))
    removals.sort(key=lambda item: item["removed_class_id"])
    summary = {
        "ordered_pair_tests": len(records) ** 2,
        "relation_edges": len(relation),
        "self_relation_edges": sum((i, i) in relation for i in range(len(records))),
        "cross_relation_edges": sum(i != j for i, j in relation),
        "strict_cross_relation_edges": sum(
            i != j and (j, i) not in relation for i, j in relation
        ),
        "equivalent_cross_relation_pairs": sum(
            i < j and (i, j) in relation and (j, i) in relation
            for i in range(len(records))
            for j in range(len(records))
        ),
    }
    return retained, removals, summary


def build_candidate(
    skeleton: Sequence[tuple[tuple[int, ...], tuple[int, ...]]],
    assignment: Sequence[Sequence[int]],
) -> tuple[Statistic, ...]:
    stats = []
    for (left, right), values in zip(skeleton, assignment):
        stats.extend(Statistic(left, right, int(value)) for value in values)
    return tuple(stats)


def reachable_catalog(
    retained: Sequence[dict],
    scalar: dict,
    ledger: Ledger,
) -> list[dict]:
    code_to_pattern = {
        "".join(str(x) for x in pattern): pattern for pattern in RUN_PATTERNS
    }
    allowed = {
        code_to_pattern[lower]: tuple(code_to_pattern[upper] for upper in uppers)
        for lower, uppers in scalar["allowed_upper_patterns"].items()
    }
    entries = []
    seen: set[tuple] = set()
    for source_index, record in enumerate(retained):
        options = [allowed[pattern] for pattern in record["run_patterns"]]
        for assignment in itertools.product(*options):
            candidate = build_candidate(record["skeleton"], assignment)
            ledger.charge("reachable_candidates_constructed")
            if compactify(candidate) != candidate:
                raise AssertionError("reachable candidate is noncompact")
            key = trajectory_key(candidate)
            if key in seen:
                raise AssertionError("reachable catalog duplicate across retained generators")
            seen.add(key)
            witness = extension_preorder_witness(record["gamma"], candidate, ledger)
            if witness is None or not verify_witness(record["gamma"], candidate, witness):
                raise AssertionError("reachable entry lacks direct witness")
            entries.append(
                {
                    "trajectory": encode(candidate),
                    "source_generator_index": source_index,
                    "source_class_id": record["class_id"],
                    "source_run_patterns": [list(pattern) for pattern in record["run_patterns"]],
                    "upper_run_patterns": [list(pattern) for pattern in assignment],
                    "direct_witness": witness,
                    "witness_kind": "EXTENSION_PREORDER_DIRECT",
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


def prove_idempotence(retained: Sequence[dict], scalar: dict) -> dict:
    code_to_pattern = {
        "".join(str(x) for x in pattern): pattern for pattern in RUN_PATTERNS
    }
    allowed = {
        code_to_pattern[lower]: {code_to_pattern[upper] for upper in uppers}
        for lower, uppers in scalar["allowed_upper_patterns"].items()
    }
    checks = 0
    for record in retained:
        for lower_pattern in record["run_patterns"]:
            first = allowed[lower_pattern]
            for middle in first:
                second = allowed[middle]
                checks += len(second)
                if not second.issubset(first):
                    raise AssertionError("scalar upward set is not transitive/idempotent")
    return {
        "proved": True,
        "method": "BLOCKWISE_UPWARD_SET_TRANSITIVITY",
        "scalar_transitivity_checks": checks,
        "global_repeated_geometry_blocks": 0,
    }


def build(source_path: Path, output_path: Path, order_mode: str = "original") -> dict:
    source_sha = file_sha256(source_path)
    if source_sha != EXPECTED_SOURCE_SHA256:
        raise AssertionError("source node-8 compression byte digest drift")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    if source.get("schema") != SOURCE_SCHEMA:
        raise AssertionError("source schema drift")
    if source.get("semantic_digest") != EXPECTED_SOURCE_SEMANTIC_DIGEST:
        raise AssertionError("source semantic digest drift")
    proof = source.get("proof_payload", {})
    if proof.get("admit") is not True:
        raise AssertionError("source node-8 frontier is not admitted")
    if set(proof.get("invariant_vector", {}).values()) != {"PASS"}:
        raise AssertionError("source invariant vector is not green")
    if proof.get("next_gate") != "C049.1_B4.6.3_NODE8_SIXTY_ONE_GENERATOR_UP_K_CLOSURE":
        raise AssertionError("source next gate drift")
    classes = proof["quotient_frontier"]["classes"]
    if len(classes) != EXPECTED_INPUT_GENERATORS:
        raise AssertionError("source generator count drift")
    ambient_dim = int(proof["ambient_dim"])
    k = int(proof["k"])
    if ambient_dim != EXPECTED_AMBIENT_DIM or k != EXPECTED_K:
        raise AssertionError("ambient or k drift")

    ledger = Ledger()
    patterns = scalar_catalog(ledger)
    scalar = scalar_relation(patterns, ledger)
    records = normalize_records(reorder_classes(classes, order_mode), ambient_dim)
    retained, removals, relation_summary = minimize_generators(records, ledger)
    entries = reachable_catalog(retained, scalar, ledger)
    idempotence = prove_idempotence(retained, scalar)

    if len(retained) != EXPECTED_RETAINED_GENERATORS:
        raise AssertionError("retained generator count drift")
    if len(removals) != EXPECTED_DIRECT_REMOVALS:
        raise AssertionError("direct removal count drift")
    if len(entries) != EXPECTED_REACHABLE_ENTRIES:
        raise AssertionError("reachable entry count drift")
    if relation_summary != {
        "ordered_pair_tests": 3721,
        "relation_edges": 104,
        "self_relation_edges": 61,
        "cross_relation_edges": 43,
        "strict_cross_relation_edges": 43,
        "equivalent_cross_relation_pairs": 0,
    }:
        raise AssertionError("preorder relation summary drift")

    retained_payload = [
        {
            "class_id": record["class_id"],
            "generator": encode(record["gamma"]),
            "generator_digest": digest(encode(record["gamma"])),
            "skeleton_length": len(record["skeleton"]),
            "run_patterns": [list(pattern) for pattern in record["run_patterns"]],
        }
        for record in retained
    ]
    input_payload = [
        {
            "class_id": record["class_id"],
            "generator": encode(record["gamma"]),
            "generator_digest": digest(encode(record["gamma"])),
        }
        for record in records
    ]

    invariant_vector = {f"N8U-INV-{index:02d}": "PASS" for index in range(1, 11)}
    proof_payload = {
        "admit": True,
        "node_id": 8,
        "ambient_dim": ambient_dim,
        "k": k,
        "source": {
            "artifact_sha256": source_sha,
            "semantic_digest": source["semantic_digest"],
            "schema": source["schema"],
            "post_shrink_class_count": len(classes),
        },
        "input_family": {
            "generator_count": len(records),
            "family_digest": digest(input_payload),
            "generators": input_payload,
        },
        "preorder_minimization": {
            **relation_summary,
            "retained_generator_count": len(retained_payload),
            "direct_removal_count": len(removals),
            "retained_family_digest": digest(retained_payload),
            "retained_generators": retained_payload,
            "removals": removals,
            "all_removals_direct": True,
            "transitive_closure_used": False,
        },
        "scalar_typical_catalog": scalar,
        "reachable_closure": {
            "complete_reachable_catalog": len(entries),
            "reachable_entry_count": len(entries),
            "reachable_entries_digest": digest(entries),
            "reachable_stream_sha256": stream_digest(entries),
            "entries": entries,
            "all_entries_have_direct_witness": True,
            "transitive_closure_used": False,
            "global_compact_universe_enumerated": False,
            "global_universe_entries_enumerated": 0,
        },
        "idempotence": idempotence,
        "work_ledger": ledger.snapshot(),
        "invariant_vector": invariant_vector,
        "strict_boundary": {
            "node8_parent_generator_frontier_complete": True,
            "node8_parent_refinement_complete": True,
            "node8_parent_up_k_complete": True,
            "node8_integrated_into_bottom_up_executor": False,
            "node9_parent_refinement_started": False,
            "negative_root_reached": False,
            "terminal_completeness_proved": False,
            "found_layout_enabled": False,
            "no_layout_at_cap_enabled": False,
            "current_global_terminal": TERMINAL,
            "p_vs_np": "OPEN",
        },
        "next_gate": "C049.1_B4.6.3_NODE8_UP_K_INTEGRATION_AND_NODE9_PARENT_REFINEMENT",
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
        "semantic_digest_scope": "proof_payload",
        "proof_payload": proof_payload,
    }
    artifact["semantic_digest"] = digest(proof_payload)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(canonical_json(artifact) + b"\n")
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--entry-order",
        choices=("original", "reversed", "seeded-shuffle"),
        default="original",
    )
    args = parser.parse_args()
    artifact = build(args.source, args.output, args.entry_order)
    proof = artifact["proof_payload"]
    print("JANUS_C049_1_B4_6_3_NODE8_SIXTY_ONE_GENERATOR_UP_K_CLOSURE = PASS")
    print("INPUT_GENERATORS =", proof["input_family"]["generator_count"])
    print("RETAINED_GENERATORS =", proof["preorder_minimization"]["retained_generator_count"])
    print("DIRECT_REMOVALS =", proof["preorder_minimization"]["direct_removal_count"])
    print("RELATION_EDGES =", proof["preorder_minimization"]["relation_edges"])
    print("COMPLETE_REACHABLE_CATALOG =", proof["reachable_closure"]["complete_reachable_catalog"])
    print("IDEMPOTENT =", proof["idempotence"]["proved"])
    print("ADMIT_NODE8_UP_K_CLOSURE =", proof["admit"])
    print("SEMANTIC_DIGEST =", artifact["semantic_digest"])
    print("GLOBAL_TERMINAL =", proof["strict_boundary"]["current_global_terminal"])


if __name__ == "__main__":
    main()
