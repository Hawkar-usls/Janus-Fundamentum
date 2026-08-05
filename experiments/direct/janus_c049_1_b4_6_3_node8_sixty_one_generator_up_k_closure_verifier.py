#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import itertools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

EXPECTED_SCHEMA = "C049.1-B4.6.3-NODE8-SIXTY-ONE-GENERATOR-UP-K-CLOSURE-v1"
SOURCE_SCHEMA = "C049.1-B4.6.3-NODE8-PARENT-FRONTIER-STRUCTURAL-COMPRESSION-v1"
SOURCE_SHA = "93dcd5610eb9df079823b172a4f824ce1c09859e759c6b771dc95b99af394d34"
SOURCE_SEMANTIC = "209f5a013ec492b67066abc3dcf08af183d2ec5ec0000f3d8d03a033cb32f9db"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
PATTERNS = ((0,), (0, 1), (0, 1, 0), (1,), (1, 0), (1, 0, 1))


def canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def h(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True, order=True)
class Point:
    left: tuple[int, ...]
    right: tuple[int, ...]
    level: int


def reduce_basis(rows: Iterable[int], dimension: int) -> tuple[int, ...]:
    pivots: list[int] = []
    for raw in rows:
        value = int(raw)
        if not 0 <= value < (1 << dimension):
            raise AssertionError("vector range")
        for row in pivots:
            value = min(value, value ^ row)
        if value == 0:
            continue
        pivot = value.bit_length() - 1
        updated = []
        for row in pivots:
            updated.append(row ^ value if ((row >> pivot) & 1) else row)
        updated.append(value)
        pivots = sorted(updated, reverse=True)
    return tuple(pivots)


def contained(big: Sequence[int], small: Sequence[int]) -> bool:
    basis = tuple(big)
    for raw in small:
        value = int(raw)
        for row in basis:
            value = min(value, value ^ row)
        if value:
            return False
    return True


def reduce_trajectory(seq: Sequence[Point]) -> tuple[Point, ...]:
    data = list(seq)
    while True:
        for i in range(1, len(data)):
            if data[i - 1] == data[i]:
                del data[i]
                break
        else:
            removed = False
            for i in range(len(data)):
                for j in range(i + 2, len(data)):
                    if (data[i].left, data[i].right) != (data[j].left, data[j].right):
                        continue
                    values = [x.level for x in data[i : j + 1]]
                    lo, hi = values[0], values[-1]
                    monotone_interval = (
                        lo <= hi and all(lo <= z <= hi for z in values[1:-1])
                    ) or (
                        lo >= hi and all(lo >= z >= hi for z in values[1:-1])
                    )
                    if monotone_interval:
                        del data[i + 1 : j]
                        removed = True
                        break
                if removed:
                    break
            if not removed:
                return tuple(data)
            continue
        continue


def parse(raw: Sequence[dict], dimension: int) -> tuple[Point, ...]:
    if not raw:
        raise AssertionError("empty")
    result = tuple(
        Point(
            reduce_basis(item["left"], dimension),
            reduce_basis(item["right"], dimension),
            int(item["value"]),
        )
        for item in raw
    )
    if any(item.level not in (0, 1) for item in result):
        raise AssertionError("nonbinary")
    if result[0].right != result[-1].left:
        raise AssertionError("endpoints")
    for a, b in zip(result, result[1:]):
        if not contained(b.left, a.left) or not contained(a.right, b.right):
            raise AssertionError("monotonicity")
    if reduce_trajectory(result) != result:
        raise AssertionError("noncompact")
    return result


def serial(seq: Sequence[Point]) -> list[dict]:
    return [
        {"left": list(x.left), "right": list(x.right), "value": x.level}
        for x in seq
    ]


def key(seq: Sequence[Point]) -> tuple:
    return tuple((x.left, x.right, x.level) for x in seq)


def point_leq(a: Point, b: Point) -> bool:
    return a.left == b.left and a.right == b.right and a.level <= b.level


def path_witness(lower: Sequence[Point], upper: Sequence[Point]) -> dict | None:
    reachable: dict[tuple[int, int], tuple[int, int] | None] = {}
    for i, a in enumerate(lower):
        for j, b in enumerate(upper):
            if not point_leq(a, b):
                continue
            if i == 0 and j == 0:
                reachable[(i, j)] = None
                continue
            for prev in ((i - 1, j - 1), (i - 1, j), (i, j - 1)):
                if prev in reachable:
                    reachable[(i, j)] = prev
                    break
    end = (len(lower) - 1, len(upper) - 1)
    if end not in reachable:
        return None
    path = []
    cursor: tuple[int, int] | None = end
    while cursor is not None:
        path.append(cursor)
        cursor = reachable[cursor]
    path.reverse()
    return {"path": [[i, j] for i, j in path], "path_length": len(path)}


def witness_ok(lower: Sequence[Point], upper: Sequence[Point], witness: dict) -> bool:
    raw = witness.get("path")
    if not isinstance(raw, list) or not raw:
        return False
    path = []
    for cell in raw:
        if not isinstance(cell, list) or len(cell) != 2:
            return False
        i, j = cell
        if not isinstance(i, int) or not isinstance(j, int):
            return False
        if not (0 <= i < len(lower) and 0 <= j < len(upper)):
            return False
        path.append((i, j))
    if path[0] != (0, 0) or path[-1] != (len(lower) - 1, len(upper) - 1):
        return False
    if any(
        (b[0] - a[0], b[1] - a[1]) not in ((1, 0), (0, 1), (1, 1))
        for a, b in zip(path, path[1:])
    ):
        return False
    if any(not point_leq(lower[i], upper[j]) for i, j in path):
        return False
    return witness.get("path_length") == len(path)


def runs(seq: Sequence[Point]) -> tuple[tuple, tuple[tuple[int, ...], ...]]:
    skeleton = []
    values: list[list[int]] = []
    for item in seq:
        geom = (item.left, item.right)
        if not skeleton or skeleton[-1] != geom:
            skeleton.append(geom)
            values.append([item.level])
        else:
            values[-1].append(item.level)
    patterns = tuple(tuple(x) for x in values)
    if any(pattern not in PATTERNS for pattern in patterns):
        raise AssertionError("run pattern")
    if len(set(skeleton)) != len(skeleton):
        raise AssertionError("repeated geometry")
    return tuple(skeleton), patterns


def scalar_relation() -> tuple[list[dict], dict[tuple[int, ...], tuple[tuple[int, ...], ...]]]:
    edges = []
    allowed = {}
    for lower in PATTERNS:
        lo = tuple(Point((), (), x) for x in lower)
        targets = []
        for upper in PATTERNS:
            up = tuple(Point((), (), x) for x in upper)
            witness = path_witness(lo, up)
            if witness is not None:
                targets.append(upper)
                edges.append(
                    {
                        "lower": list(lower),
                        "upper": list(upper),
                        "direct_witness": witness,
                    }
                )
        allowed[lower] = tuple(sorted(targets))
    edges.sort(key=canon)
    return edges, allowed


def source_records(source: dict) -> list[dict]:
    proof = source["proof_payload"]
    classes = proof["quotient_frontier"]["classes"]
    if len(classes) != 61:
        raise AssertionError("61 input classes")
    records = []
    for item in classes:
        gamma = parse(item["canonical_generator"], 3)
        skeleton, patterns = runs(gamma)
        if h(serial(gamma)) != item["generator_digest"]:
            raise AssertionError("source generator digest")
        records.append(
            {
                "class_id": item["class_id"],
                "gamma": gamma,
                "skeleton": skeleton,
                "patterns": patterns,
            }
        )
    records.sort(key=lambda x: (key(x["gamma"]), x["class_id"]))
    if len({key(x["gamma"]) for x in records}) != 61:
        raise AssertionError("source uniqueness")
    return records


def independently_minimize(records: Sequence[dict]) -> tuple[list[dict], list[dict], dict]:
    relation = {}
    for i, lower in enumerate(records):
        for j, upper in enumerate(records):
            witness = path_witness(lower["gamma"], upper["gamma"])
            if witness is not None:
                relation[(i, j)] = witness
    retained_indices = []
    for j in range(len(records)):
        dominated = any(
            i != j and (i, j) in relation and (j, i) not in relation
            for i in range(len(records))
        )
        duplicate = any(
            i < j and (i, j) in relation and (j, i) in relation
            for i in range(len(records))
        )
        if not dominated and not duplicate:
            retained_indices.append(j)
    retained = [records[i] for i in retained_indices]
    retained.sort(key=lambda x: (key(x["gamma"]), x["class_id"]))
    retained_ids = {x["class_id"] for x in retained}
    removals = []
    for j, removed in enumerate(records):
        if removed["class_id"] in retained_ids:
            continue
        candidates = [i for i in retained_indices if (i, j) in relation]
        if not candidates:
            raise AssertionError("no retained predecessor")
        i = min(candidates, key=lambda z: (key(records[z]["gamma"]), records[z]["class_id"]))
        witness = relation[(i, j)]
        if not witness_ok(records[i]["gamma"], removed["gamma"], witness):
            raise AssertionError("removal witness")
        payload = {
            "removed_class_id": removed["class_id"],
            "retained_class_id": records[i]["class_id"],
            "removed_generator": serial(removed["gamma"]),
            "retained_generator": serial(records[i]["gamma"]),
            "direct_witness": witness,
            "witness_kind": "EXTENSION_PREORDER_DIRECT",
            "reason": "STRICTLY_COVERED",
        }
        payload["removal_digest"] = h(payload)
        removals.append(payload)
    removals.sort(key=lambda x: x["removed_class_id"])
    summary = {
        "ordered_pair_tests": 3721,
        "relation_edges": len(relation),
        "self_relation_edges": sum((i, i) in relation for i in range(61)),
        "cross_relation_edges": sum(i != j for i, j in relation),
        "strict_cross_relation_edges": sum(
            i != j and (j, i) not in relation for i, j in relation
        ),
        "equivalent_cross_relation_pairs": sum(
            i < j and (i, j) in relation and (j, i) in relation
            for i in range(61)
            for j in range(61)
        ),
    }
    return retained, removals, summary


def candidate(skeleton: Sequence[tuple], assignment: Sequence[Sequence[int]]) -> tuple[Point, ...]:
    out = []
    for (left, right), values in zip(skeleton, assignment):
        out.extend(Point(left, right, int(value)) for value in values)
    return tuple(out)


def independently_close(retained: Sequence[dict], allowed: dict) -> list[dict]:
    entries = []
    seen = set()
    for source_index, record in enumerate(retained):
        options = [allowed[pattern] for pattern in record["patterns"]]
        for assignment in itertools.product(*options):
            upper = candidate(record["skeleton"], assignment)
            if reduce_trajectory(upper) != upper:
                raise AssertionError("noncompact closure entry")
            k0 = key(upper)
            if k0 in seen:
                raise AssertionError("duplicate closure entry")
            seen.add(k0)
            witness = path_witness(record["gamma"], upper)
            if witness is None or not witness_ok(record["gamma"], upper, witness):
                raise AssertionError("closure witness")
            entries.append(
                {
                    "trajectory": serial(upper),
                    "source_generator_index": source_index,
                    "source_class_id": record["class_id"],
                    "source_run_patterns": [list(x) for x in record["patterns"]],
                    "upper_run_patterns": [list(x) for x in assignment],
                    "direct_witness": witness,
                    "witness_kind": "EXTENSION_PREORDER_DIRECT",
                }
            )
    entries.sort(key=lambda x: canon(x["trajectory"]))
    return entries


def stream_hash(entries: Sequence[dict]) -> str:
    hasher = hashlib.sha256()
    for entry in entries:
        hasher.update(canon(entry["trajectory"]))
        hasher.update(b"\n")
    return hasher.hexdigest()


def expected_replay(source_path: Path) -> dict:
    if file_hash(source_path) != SOURCE_SHA:
        raise AssertionError("source bytes")
    source = json.loads(source_path.read_text())
    if source.get("schema") != SOURCE_SCHEMA or source.get("semantic_digest") != SOURCE_SEMANTIC:
        raise AssertionError("source binding")
    proof = source.get("proof_payload", {})
    if proof.get("admit") is not True or set(proof.get("invariant_vector", {}).values()) != {"PASS"}:
        raise AssertionError("source admission")
    records = source_records(source)
    retained, removals, relation = independently_minimize(records)
    if len(retained) != 28 or len(removals) != 33:
        raise AssertionError("minimization counts")
    if relation != {
        "ordered_pair_tests": 3721,
        "relation_edges": 104,
        "self_relation_edges": 61,
        "cross_relation_edges": 43,
        "strict_cross_relation_edges": 43,
        "equivalent_cross_relation_pairs": 0,
    }:
        raise AssertionError("relation summary")
    edges, allowed = scalar_relation()
    if len(edges) != 20:
        raise AssertionError("scalar relation")
    entries = independently_close(retained, allowed)
    if len(entries) != 15948:
        raise AssertionError("closure count")
    input_payload = [
        {
            "class_id": x["class_id"],
            "generator": serial(x["gamma"]),
            "generator_digest": h(serial(x["gamma"])),
        }
        for x in records
    ]
    retained_payload = [
        {
            "class_id": x["class_id"],
            "generator": serial(x["gamma"]),
            "generator_digest": h(serial(x["gamma"])),
            "skeleton_length": len(x["skeleton"]),
            "run_patterns": [list(p) for p in x["patterns"]],
        }
        for x in retained
    ]
    allowed_payload = {
        "".join(str(z) for z in lower): ["".join(str(z) for z in upper) for upper in allowed[lower]]
        for lower in PATTERNS
    }
    transitivity_checks = 0
    for x in retained:
        for p in x["patterns"]:
            for mid in allowed[p]:
                transitivity_checks += len(allowed[mid])
                if not set(allowed[mid]).issubset(set(allowed[p])):
                    raise AssertionError("idempotence")
    return {
        "source": source,
        "records": records,
        "input_payload": input_payload,
        "retained": retained,
        "retained_payload": retained_payload,
        "removals": removals,
        "relation": relation,
        "edges": edges,
        "allowed_payload": allowed_payload,
        "entries": entries,
        "transitivity_checks": transitivity_checks,
    }


def static_producer_check(path: Path) -> None:
    source = path.read_text()
    tree = ast.parse(source)
    forbidden_names = {
        "enumerate_compact_trajectories",
        "enumerate_global_compact_universe",
        "global_universe",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in forbidden_names:
            raise AssertionError("forbidden global universe enumeration")
        if isinstance(node, ast.Attribute) and node.attr in forbidden_names:
            raise AssertionError("forbidden global universe enumeration")
    if "itertools.product(*options)" not in source:
        raise AssertionError("reachable-only product construction missing")
    print("STATIC_NO_GLOBAL_COMPACT_UNIVERSE_ENUMERATION = PASS")


def verify(source_path: Path, artifact_value: dict, replay: dict) -> None:
    if artifact_value.get("schema") != EXPECTED_SCHEMA:
        raise AssertionError("artifact schema")
    if artifact_value.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("digest scope")
    proof = artifact_value.get("proof_payload")
    if not isinstance(proof, dict) or artifact_value.get("semantic_digest") != h(proof):
        raise AssertionError("semantic digest")
    if proof.get("admit") is not True:
        raise AssertionError("admit")
    if proof.get("source") != {
        "artifact_sha256": SOURCE_SHA,
        "semantic_digest": SOURCE_SEMANTIC,
        "schema": SOURCE_SCHEMA,
        "post_shrink_class_count": 61,
    }:
        raise AssertionError("source fields")
    input_family = proof["input_family"]
    if input_family["generator_count"] != 61 or input_family["generators"] != replay["input_payload"]:
        raise AssertionError("input family")
    if input_family["family_digest"] != h(replay["input_payload"]):
        raise AssertionError("input digest")
    mini = proof["preorder_minimization"]
    for field, expected in replay["relation"].items():
        if mini.get(field) != expected:
            raise AssertionError("relation field")
    if mini["retained_generator_count"] != 28 or mini["direct_removal_count"] != 33:
        raise AssertionError("minimization counts")
    if mini["retained_generators"] != replay["retained_payload"]:
        raise AssertionError("retained family")
    if mini["retained_family_digest"] != h(replay["retained_payload"]):
        raise AssertionError("retained digest")
    if mini["removals"] != replay["removals"]:
        raise AssertionError("removals")
    if mini["all_removals_direct"] is not True or mini["transitive_closure_used"] is not False:
        raise AssertionError("removal boundary")
    scalar = proof["scalar_typical_catalog"]
    if scalar["patterns"] != [list(x) for x in PATTERNS]:
        raise AssertionError("patterns")
    if scalar["relation_edges"] != replay["edges"] or scalar["relation_edge_count"] != 20:
        raise AssertionError("scalar edges")
    if scalar["allowed_upper_patterns"] != replay["allowed_payload"]:
        raise AssertionError("scalar allowed")
    closure = proof["reachable_closure"]
    if closure["complete_reachable_catalog"] != 15948 or closure["reachable_entry_count"] != 15948:
        raise AssertionError("closure counts")
    if closure["entries"] != replay["entries"]:
        raise AssertionError("closure entries")
    if closure["reachable_entries_digest"] != h(replay["entries"]):
        raise AssertionError("closure digest")
    if closure["reachable_stream_sha256"] != stream_hash(replay["entries"]):
        raise AssertionError("stream digest")
    if closure["all_entries_have_direct_witness"] is not True or closure["transitive_closure_used"] is not False:
        raise AssertionError("closure witness boundary")
    if closure["global_compact_universe_enumerated"] is not False or closure["global_universe_entries_enumerated"] != 0:
        raise AssertionError("global universe boundary")
    idem = proof["idempotence"]
    if idem != {
        "proved": True,
        "method": "BLOCKWISE_UPWARD_SET_TRANSITIVITY",
        "scalar_transitivity_checks": replay["transitivity_checks"],
        "global_repeated_geometry_blocks": 0,
    }:
        raise AssertionError("idempotence")
    if proof.get("invariant_vector") != {f"N8U-INV-{i:02d}": "PASS" for i in range(1, 11)}:
        raise AssertionError("invariant vector")
    strict = proof["strict_boundary"]
    expected_strict = {
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
    }
    if strict != expected_strict:
        raise AssertionError("strict boundary")
    if proof.get("next_gate") != "C049.1_B4.6.3_NODE8_UP_K_INTEGRATION_AND_NODE9_PARENT_REFINEMENT":
        raise AssertionError("next gate")


def rehash(value: dict) -> None:
    value["semantic_digest"] = h(value["proof_payload"])


def tamper_tests(source_path: Path, artifact: dict, replay: dict) -> None:
    proof = artifact["proof_payload"]
    attacks = []

    def scalar_set(container: dict, key: str, value: Any):
        old = container[key]
        container[key] = value
        return lambda: container.__setitem__(key, old)

    attacks.append(("source_sha", lambda: scalar_set(proof["source"], "artifact_sha256", "0" * 64)))
    attacks.append(("input_generator", lambda: scalar_set(proof["input_family"]["generators"][0]["generator"][0], "value", 1)))

    def pop_restore(seq: list):
        value = seq.pop()
        return lambda: seq.append(value)

    attacks.append(("retained_delete", lambda: pop_restore(proof["preorder_minimization"]["retained_generators"])))
    attacks.append(("closure_only_removal", lambda: scalar_set(proof["preorder_minimization"]["removals"][0], "witness_kind", "TRANSITIVE_CLOSURE_ONLY")))
    attacks.append(("reachable_delete", lambda: pop_restore(proof["reachable_closure"]["entries"])))
    attacks.append(("source_class", lambda: scalar_set(proof["reachable_closure"]["entries"][0], "source_class_id", "N8-FAKE")))

    def reverse_restore(seq: list):
        seq.reverse()
        return lambda: seq.reverse()

    attacks.append(("entry_order", lambda: reverse_restore(proof["reachable_closure"]["entries"])))
    attacks.append(("pattern_catalog", lambda: pop_restore(proof["scalar_typical_catalog"]["patterns"])))
    attacks.append(("idempotence", lambda: scalar_set(proof["idempotence"], "proved", False)))
    attacks.append(("false_root", lambda: scalar_set(proof["strict_boundary"], "negative_root_reached", True)))

    original_digest = artifact["semantic_digest"]
    rejected = 0
    for name, apply in attacks:
        undo = apply()
        rehash(artifact)
        try:
            verify(source_path, artifact, replay)
        except Exception:
            rejected += 1
        else:
            raise AssertionError(f"tamper attack accepted: {name}")
        finally:
            undo()
            artifact["semantic_digest"] = original_digest
    if rejected != 10:
        raise AssertionError("tamper count")
    print("TAMPER_ATTACKS_REJECTED = 10/10")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--producer-source", type=Path, required=True)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    static_producer_check(args.producer_source)
    replay = expected_replay(args.source)
    artifact = json.loads(args.artifact.read_text())
    verify(args.source, artifact, replay)
    if args.tamper_self_test:
        tamper_tests(args.source, artifact, replay)
    print("JANUS_C049_1_B4_6_3_NODE8_UP_K_CLOSURE_VERIFIER = PASS")
    print("INVARIANTS = 10/10")
    print("INPUT_GENERATORS = 61")
    print("RETAINED_GENERATORS = 28")
    print("DIRECT_REMOVALS = 33")
    print("REACHABLE_ENTRIES = 15948")
    print("ADMIT_NODE8_UP_K_CLOSURE = TRUE")


if __name__ == "__main__":
    main()
