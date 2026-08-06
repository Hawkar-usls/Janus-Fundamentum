#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
import random
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA = "C049.1-B4.6.3-CORRECTED-NODE7-INTEGRATION-NODE8-ATTACK-BOOTSTRAP-v1"
BASE_PR = 113
BASE_EXACT_HEAD = "024afebb322c67953f310af48818d3386fdcfc27"
UPK_SHA256 = "924e55a651518ce004964f5d7c5ea30e67424ca34507f18eb568341fc96528e0"
UPK_SEMANTIC = "cfd99ea716076414847749fb98185cea63c2cf44e9ceaa659bf37eb9e8fc366a"
CLOSURE_DIGEST = "99a702ea7005e4a41d99fc4454040314ab106632672b267bffb5f59e29afa728"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
RUN_PATTERNS: tuple[tuple[int, ...], ...] = (
    (0,),
    (0, 1),
    (0, 1, 0),
    (1,),
    (1, 0),
    (1, 0, 1),
)
EXPECTED_LEFT_HISTOGRAM = {
    "4": 96,
    "5": 384,
    "6": 960,
    "7": 1536,
    "8": 1824,
    "9": 1536,
    "10": 960,
    "11": 384,
    "12": 96,
}
LEAF3_LENGTH_HISTOGRAM = {"2": 4, "3": 8, "4": 12, "5": 8, "6": 4}
LEAF3_ENTRY_COUNT = 36
LEAF3_RECEIPT = "80f424b87fd39e80013e1bb96b3dcec47d281a322f9964472b2ca32bd039e086"
EXPECTED_NODE7_ENTRIES = 7776
EXPECTED_NODE8_PAIRS = 279936
EXPECTED_NODE8_HV_REFINEMENTS = 70875648
PAIR_CAP = 10000
REFINEMENT_CAP = 2000000


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_rref(rows: Iterable[int], ambient_dim: int = 2) -> tuple[int, ...]:
    work = sorted({int(value) for value in rows if int(value)}, reverse=True)
    if any(value < 0 or value >= (1 << ambient_dim) for value in work):
        raise ValueError("vector outside ambient GF(2) space")
    pivot = 0
    for column in range(ambient_dim - 1, -1, -1):
        candidate = next(
            (index for index in range(pivot, len(work)) if (work[index] >> column) & 1),
            None,
        )
        if candidate is None:
            continue
        work[pivot], work[candidate] = work[candidate], work[pivot]
        row = work[pivot]
        for index in range(len(work)):
            if index != pivot and ((work[index] >> column) & 1):
                work[index] ^= row
        pivot += 1
    return tuple(sorted((value for value in work if value), key=int.bit_length, reverse=True))


def canonical_stat(item: dict[str, Any]) -> dict[str, Any]:
    value = int(item["value"])
    if value not in (0, 1):
        raise AssertionError("k=1 scalar outside {0,1}")
    return {
        "left": list(canonical_rref(item["left"])),
        "right": list(canonical_rref(item["right"])),
        "value": value,
    }


def geometry(item: dict[str, Any]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    return tuple(item["left"]), tuple(item["right"])


def reorder(items: list[Any], mode: str) -> list[Any]:
    output = list(items)
    if mode == "reversed":
        output.reverse()
    elif mode == "seeded-shuffle":
        random.Random(0xC049114).shuffle(output)
    elif mode != "original":
        raise ValueError("unknown entry order")
    return output


def load_admitted_generators(upk_path: Path, order_mode: str) -> tuple[dict, list[dict[str, Any]]]:
    if file_sha256(upk_path) != UPK_SHA256:
        raise AssertionError("PR #113 frozen Node-7 up_k byte boundary drift")
    source = json.loads(upk_path.read_text(encoding="utf-8"))
    if source.get("semantic_digest") != UPK_SEMANTIC:
        raise AssertionError("PR #113 Node-7 up_k semantic boundary drift")
    if source.get("schema") != "C049.1-B4.6.3-CORRECTED-NODE7-SIX-GENERATOR-UP-K-v2":
        raise AssertionError("PR #113 Node-7 up_k schema drift")
    if source.get("next_gate_after_admission") != (
        "C049.1_B4.6.3_CORRECTED_NODE7_INTEGRATION_AND_NODE8_PARENT_REFINEMENT"
    ):
        raise AssertionError("PR #113 next-gate binding drift")
    closure = source.get("reachable_closure", {})
    if (
        int(closure.get("entry_count", -1)),
        closure.get("entries_digest"),
        bool(closure.get("full_entries_stored")),
    ) != (EXPECTED_NODE7_ENTRIES, CLOSURE_DIGEST, False):
        raise AssertionError("PR #113 reachable closure receipt drift")

    generators: list[dict[str, Any]] = []
    for item in reorder(list(source["input_generators"]), order_mode):
        trajectory = [canonical_stat(stat) for stat in item["trajectory"]]
        geometries = [geometry(stat) for stat in trajectory]
        if len(trajectory) != 4 or len(set(geometries)) != 4:
            raise AssertionError("corrected Node-7 generator geometry drift")
        if any(int(stat["value"]) != 0 for stat in trajectory):
            raise AssertionError("corrected Node-7 generator is not a zero envelope")
        generators.append(
            {
                "generator_id": str(item["generator_id"]),
                "trajectory": trajectory,
                "trajectory_digest": digest(trajectory),
            }
        )
    generators.sort(key=lambda item: canonical_json(item["trajectory"]))
    if len(generators) != 6 or len({canonical_json(item["trajectory"]) for item in generators}) != 6:
        raise AssertionError("six-generator admission boundary drift")
    return source, generators


def reconstruct_closure(generators: Sequence[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    reachable: dict[bytes, list[dict[str, Any]]] = {}
    for generator in generators:
        skeleton = [geometry(stat) for stat in generator["trajectory"]]
        for assignment in itertools.product(RUN_PATTERNS, repeat=4):
            trajectory: list[dict[str, Any]] = []
            for (left, right), pattern in zip(skeleton, assignment):
                for value in pattern:
                    trajectory.append({"left": list(left), "right": list(right), "value": int(value)})
            key = canonical_json(trajectory)
            reachable[key] = trajectory
    entries = [reachable[key] for key in sorted(reachable)]
    if len(entries) != EXPECTED_NODE7_ENTRIES:
        raise AssertionError("corrected Node-7 closure cardinality drift")
    if hashlib.sha256(canonical_json(entries)).hexdigest() != CLOSURE_DIGEST:
        raise AssertionError("corrected Node-7 closure stream digest drift")
    return entries


def length_histogram(entries: Sequence[Sequence[dict[str, Any]]]) -> dict[str, int]:
    return {
        str(length): count
        for length, count in sorted(Counter(len(item) for item in entries).items())
    }


def ordinary_hv_path_count(left_length: int, right_length: int) -> int:
    if left_length <= 0 or right_length <= 0:
        return 0
    return math.comb(left_length + right_length - 2, left_length - 1)


def exact_refinement_count(left_histogram: dict[str, int], right_histogram: dict[str, int]) -> int:
    return sum(
        int(left_count)
        * int(right_count)
        * ordinary_hv_path_count(int(left_length), int(right_length))
        for left_length, left_count in left_histogram.items()
        for right_length, right_count in right_histogram.items()
    )


def seal(artifact: dict[str, Any]) -> dict[str, Any]:
    artifact = copy.deepcopy(artifact)
    artifact["certificate_bytes"] = 0
    while True:
        unsigned = dict(artifact)
        unsigned.pop("semantic_digest", None)
        artifact["semantic_digest"] = digest(unsigned)
        raw = canonical_json(artifact) + b"\n"
        if int(artifact["certificate_bytes"]) == len(raw):
            return artifact
        artifact["certificate_bytes"] = len(raw)


def build(upk_path: Path, order_mode: str) -> dict[str, Any]:
    source, generators = load_admitted_generators(upk_path, order_mode)
    entries = reconstruct_closure(generators)
    left_histogram = length_histogram(entries)
    if left_histogram != EXPECTED_LEFT_HISTOGRAM:
        raise AssertionError("corrected Node-7 length histogram drift")

    child_pairs = len(entries) * LEAF3_ENTRY_COUNT
    refinements = exact_refinement_count(left_histogram, LEAF3_LENGTH_HISTOGRAM)
    if child_pairs != EXPECTED_NODE8_PAIRS:
        raise AssertionError("corrected Node-8 child-pair count drift")
    if refinements != EXPECTED_NODE8_HV_REFINEMENTS:
        raise AssertionError("corrected Node-8 H/V refinement count drift")

    artifact = {
        "schema": SCHEMA,
        "status": "DRAFT_ATTACK_BOOTSTRAP",
        "source": {
            "base_pr": BASE_PR,
            "base_exact_head": BASE_EXACT_HEAD,
            "corrected_node7_up_k_sha256": UPK_SHA256,
            "corrected_node7_up_k_semantic_digest": UPK_SEMANTIC,
            "corrected_node7_closure_digest": CLOSURE_DIGEST,
            "source_certificate_bytes": int(source["certificate_bytes"]),
        },
        "corrected_node7_reconstruction": {
            "input_generators": len(generators),
            "retained_generators": len(source["preorder"]["retained_generator_ids"]),
            "direct_removals": len(source["preorder"]["direct_removals"]),
            "closure_entries": len(entries),
            "closure_entries_digest": CLOSURE_DIGEST,
            "full_entries_stored_in_bootstrap_artifact": False,
            "length_histogram": left_histogram,
            "binary_typical_patterns": [list(pattern) for pattern in RUN_PATTERNS],
            "assignments_per_generator": len(RUN_PATTERNS) ** 4,
        },
        "node8_attack_preflight": {
            "left_child_node_id": 7,
            "right_child_leaf_id": 3,
            "left_entry_count": len(entries),
            "right_entry_count": LEAF3_ENTRY_COUNT,
            "right_leaf_receipt": LEAF3_RECEIPT,
            "right_length_histogram": LEAF3_LENGTH_HISTOGRAM,
            "child_pairs": child_pairs,
            "ordinary_join_steps": [[1, 0], [0, 1]],
            "diagonal_join_steps": 0,
            "ordinary_hv_refinements": refinements,
            "pair_cap": PAIR_CAP,
            "refinement_cap": REFINEMENT_CAP,
            "pair_cap_exceeded": child_pairs > PAIR_CAP,
            "refinement_cap_exceeded": refinements > REFINEMENT_CAP,
            "generic_node8_pair_records_materialized": 0,
            "generic_node8_refinement_records_materialized": 0,
            "result": "HONEST_OPEN_AT_CORRECTED_NODE8_CHILD_PAIR_CAPABILITY",
        },
        "work_ledger": {
            "node7_generators_replayed": len(generators),
            "node7_typical_assignments_replayed": len(generators) * (len(RUN_PATTERNS) ** 4),
            "node7_closure_entries_materialized": len(entries),
            "node8_histogram_pair_classes": len(left_histogram) * len(LEAF3_LENGTH_HISTOGRAM),
            "node8_child_pairs_not_materialized": child_pairs,
            "node8_hv_refinements_not_materialized": refinements,
        },
        "admission_boundary": {
            "pr113_node7_six_generator_up_k_admitted": True,
            "corrected_node7_executor_integration_implemented": False,
            "corrected_node7_integration_admitted": False,
            "corrected_node8_parent_preflight_candidate_complete": True,
            "corrected_node8_parent_refinement_started": False,
            "corrected_node8_parent_refinement_complete": False,
            "corrected_node8_parent_up_k_complete": False,
            "corrected_bottom_up_replay_complete": False,
            "root_parent_refinement_complete": False,
            "root_full_set_computed": False,
            "root_empty_proved": False,
            "found_layout": "FORBIDDEN",
            "no_layout_at_cap": "FORBIDDEN",
            "current_global_terminal": TERMINAL,
            "p_vs_np": "OPEN",
        },
        "next_gate_status": "CLOSED_PENDING_CURRENT_GATE_EXACT_HEAD_ADMISSION",
        "certificate_bytes": 0,
    }
    return seal(artifact)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("upk", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--entry-order",
        default="original",
        choices=("original", "reversed", "seeded-shuffle"),
    )
    args = parser.parse_args()
    artifact = build(args.upk, args.entry_order)
    args.output.write_bytes(canonical_json(artifact) + b"\n")
    print(
        json.dumps(
            {
                "artifact_bytes": args.output.stat().st_size,
                "artifact_sha256": file_sha256(args.output),
                "semantic_digest": artifact["semantic_digest"],
                "node7_entries": artifact["corrected_node7_reconstruction"]["closure_entries"],
                "node8_pairs": artifact["node8_attack_preflight"]["child_pairs"],
                "node8_hv_refinements": artifact["node8_attack_preflight"]["ordinary_hv_refinements"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
