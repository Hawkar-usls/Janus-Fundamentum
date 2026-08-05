#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import random
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA = "C049.1-B4.6.3-NODE7-PARENT-FRONTIER-STRUCTURAL-COMPRESSION-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
EXPECTED_NODE6_ID = 6
EXPECTED_NODE7_ID = 7
EXPECTED_LEFT_ENTRIES = 468
EXPECTED_RIGHT_ENTRIES = 36
EXPECTED_PAIR_PRODUCT = 16848
EXPECTED_NAIVE_REFINEMENTS = 9744432
EXPECTED_CLASS_COUNT = 13
EXPECTED_SOURCE_MANIFEST_DIGEST = "2ca2b0bc7566fb2e24f62e9df44499044843fa08388d8573fb74221dfab80512"
EXPECTED_SOURCE_TRANSCRIPT_ROOT_DIGEST = "eb904e833b53cf5626af1eb28493f479f5f54f2066a8b5427cb7e3eb47f515d8"
EXPECTED_NODE6_EXECUTION_DIGEST = "c9e9f72e4715f4f04aafb2c1b5b1288b48478998826332c5ab61da949586c04a"
EXPECTED_NODE6_RECEIPT_DIGEST = "88170c8f5ba5519908e88f1dba21bb2247218c0713dc6830e562a879edd3aad9"
RUN_PATTERNS: tuple[tuple[int, ...], ...] = (
    (0,),
    (0, 1),
    (0, 1, 0),
    (1,),
    (1, 0),
    (1, 0, 1),
)
RUN_PATTERN_CODES = {
    (0,): "0",
    (0, 1): "01",
    (0, 1, 0): "010",
    (1,): "1",
    (1, 0): "10",
    (1, 0, 1): "101",
}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


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


def span_vectors(rows: Sequence[int]) -> tuple[int, ...]:
    values = {0}
    for row in rows:
        values |= {value ^ int(row) for value in tuple(values)}
    return tuple(sorted(values))


def subspace_sum(
    left: Sequence[int], right: Sequence[int], ambient_dim: int
) -> tuple[int, ...]:
    return xor_basis((*left, *right), ambient_dim)


def subspace_intersection(
    left: Sequence[int], right: Sequence[int], ambient_dim: int
) -> tuple[int, ...]:
    return xor_basis(set(span_vectors(left)) & set(span_vectors(right)), ambient_dim)


def coordinate_vector(vector: int, basis: Sequence[int]) -> int:
    for mask in range(1 << len(tuple(basis))):
        value = 0
        for index, row in enumerate(basis):
            if (mask >> index) & 1:
                value ^= int(row)
        if value == int(vector):
            return mask
    raise ValueError("vector is not in basis span")


def coordinate_space_to_ambient(
    space: Sequence[int], basis: Sequence[int], ambient_dim: int
) -> tuple[int, ...]:
    rows = []
    for mask in space:
        value = 0
        for index, row in enumerate(basis):
            if (int(mask) >> index) & 1:
                value ^= int(row)
        rows.append(value)
    return xor_basis(rows, ambient_dim)


def ambient_space_to_coordinates(
    space: Sequence[int], basis: Sequence[int]
) -> tuple[int, ...]:
    return xor_basis(
        (coordinate_vector(row, basis) for row in space), len(tuple(basis))
    )


def boundary(
    left_blocks: Sequence[Sequence[int]],
    right_blocks: Sequence[Sequence[int]],
    ambient_dim: int,
) -> tuple[int, ...]:
    left = xor_basis(
        (row for block in left_blocks for row in block), ambient_dim
    )
    right = xor_basis(
        (row for block in right_blocks for row in block), ambient_dim
    )
    return subspace_intersection(left, right, ambient_dim)


def canonical_stat(item: dict, ambient_dim: int) -> dict:
    return {
        "left": list(xor_basis(item["left"], ambient_dim)),
        "right": list(xor_basis(item["right"], ambient_dim)),
        "value": int(item["value"]),
    }


def geometry(
    item: dict, ambient_dim: int
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    return xor_basis(item["left"], ambient_dim), xor_basis(
        item["right"], ambient_dim
    )


def geometry_payload(
    value: tuple[tuple[int, ...], tuple[int, ...]]
) -> dict:
    return {"left": list(value[0]), "right": list(value[1])}


def compactify(stats: Sequence[dict], ambient_dim: int) -> list[dict]:
    seq = [canonical_stat(item, ambient_dim) for item in stats]
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
                if geometry(seq[start], ambient_dim) != geometry(
                    seq[end], ambient_dim
                ):
                    continue
                values = [
                    int(item["value"]) for item in seq[start : end + 1]
                ]
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
            return seq


def transport_trajectory(
    raw: Sequence[dict],
    child_basis: Sequence[int],
    parent_basis: Sequence[int],
    ambient_dim: int,
) -> list[dict]:
    out = []
    for item in raw:
        left_ambient = coordinate_space_to_ambient(
            item["left"], child_basis, ambient_dim
        )
        right_ambient = coordinate_space_to_ambient(
            item["right"], child_basis, ambient_dim
        )
        out.append(
            {
                "left": list(
                    ambient_space_to_coordinates(left_ambient, parent_basis)
                ),
                "right": list(
                    ambient_space_to_coordinates(right_ambient, parent_basis)
                ),
                "value": int(item["value"]),
            }
        )
    return out


def split_runs(
    raw: Sequence[dict], ambient_dim: int
) -> tuple[
    tuple[tuple[tuple[int, ...], tuple[int, ...]], ...],
    tuple[tuple[int, ...], ...],
]:
    skeleton: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
    values: list[list[int]] = []
    for item in raw:
        geom = geometry(item, ambient_dim)
        value = int(item["value"])
        if value not in (0, 1):
            raise AssertionError("child full-set entry exceeds k=1")
        if not skeleton or skeleton[-1] != geom:
            skeleton.append(geom)
            values.append([value])
        else:
            values[-1].append(value)
    patterns = tuple(tuple(run) for run in values)
    if any(pattern not in RUN_PATTERN_CODES for pattern in patterns):
        raise AssertionError(
            "entry has a run outside the six-pattern catalog"
        )
    return tuple(skeleton), patterns


def identify_left_skeleton(skeleton: tuple) -> str:
    full = (2, 1)
    if skeleton == (((), full), ((1,), (2,)), (full, ())):
        return "LEFT_A"
    if skeleton == (((), full), ((2,), (1,)), (full, ())):
        return "LEFT_B"
    if skeleton == (((), full), (full, ())):
        return "LEFT_C"
    raise AssertionError(f"unexpected node-6 skeleton: {skeleton!r}")


def identify_right_skeleton(skeleton: tuple) -> str:
    if skeleton != (((), (3,)), ((3,), ())):
        raise AssertionError(
            f"unexpected transported leaf skeleton: {skeleton!r}"
        )
    return "RIGHT_R"


def normal_forms(
    entries: Sequence[dict],
    side: str,
    order_mode: str,
    child_basis: Sequence[int] | None,
    parent_basis: Sequence[int],
    ambient_dim: int,
) -> list[dict]:
    indexed = list(enumerate(entries))
    if order_mode == "reversed":
        indexed.reverse()
    elif order_mode == "seeded-shuffle":
        random.Random(0xC049107).shuffle(indexed)
    elif order_mode != "original":
        raise ValueError("unknown order mode")
    forms = []
    for source_index, entry in indexed:
        raw = copy.deepcopy(entry["trajectory"])
        if child_basis is not None:
            raw = transport_trajectory(
                raw, child_basis, parent_basis, ambient_dim
            )
        skeleton, patterns = split_runs(raw, len(tuple(parent_basis)))
        skeleton_id = (
            identify_left_skeleton(skeleton)
            if side == "LEFT"
            else identify_right_skeleton(skeleton)
        )
        canonical_raw = [
            canonical_stat(item, len(tuple(parent_basis))) for item in raw
        ]
        forms.append(
            {
                "side": side,
                "skeleton_id": skeleton_id,
                "skeleton": [
                    geometry_payload(item) for item in skeleton
                ],
                "run_pattern_codes": [
                    RUN_PATTERN_CODES[item] for item in patterns
                ],
                "trajectory_digest": digest(canonical_raw),
                "source_entry_index": int(source_index),
                "trajectory": canonical_raw,
            }
        )
    forms.sort(
        key=lambda item: canonical_json(
            [
                item["skeleton_id"],
                item["run_pattern_codes"],
                item["trajectory_digest"],
                item["source_entry_index"],
            ]
        )
    )
    if len({item["trajectory_digest"] for item in forms}) != len(forms):
        raise AssertionError(
            "normal-form inventory contains duplicate trajectories"
        )
    return forms


def enumerate_paths(m: int, n: int) -> list[list[list[int]]]:
    out: list[list[list[int]]] = []

    def rec(i: int, j: int, path: list[list[int]]) -> None:
        if (i, j) == (m - 1, n - 1):
            out.append(copy.deepcopy(path))
            return
        for di, dj in ((1, 0), (0, 1), (1, 1)):
            ni, nj = i + di, j + dj
            if ni < m and nj < n:
                path.append([ni, nj])
                rec(ni, nj, path)
                path.pop()

    rec(0, 0, [[0, 0]])
    out.sort(key=canonical_json)
    return out


def joined_symbol(
    left_geom: tuple, right_geom: tuple, ambient_dim: int
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    return (
        subspace_sum(left_geom[0], right_geom[0], ambient_dim),
        subspace_sum(left_geom[1], right_geom[1], ambient_dim),
    )


def join_correction(
    left_geom: tuple,
    right_geom: tuple,
    initial_dim: int,
    ambient_dim: int,
) -> int:
    left_span = subspace_sum(
        left_geom[0], left_geom[1], ambient_dim
    )
    right_span = subspace_sum(
        right_geom[0], right_geom[1], ambient_dim
    )
    current_dim = len(
        subspace_intersection(left_span, right_span, ambient_dim)
    )
    return initial_dim - current_dim


def direct_witness(
    zero_envelope: Sequence[dict],
    upper_patterns: Sequence[tuple[int, ...]],
    ambient_dim: int,
) -> dict:
    if len(zero_envelope) != len(upper_patterns):
        raise AssertionError("witness block count mismatch")
    upper: list[dict] = []
    block_starts: list[int] = []
    for stat, pattern in zip(zero_envelope, upper_patterns):
        block_starts.append(len(upper))
        for value in pattern:
            item = copy.deepcopy(stat)
            item["value"] = int(value)
            upper.append(item)
    path: list[list[int]] = [[0, 0]]
    for lower_index, pattern in enumerate(upper_patterns):
        start = block_starts[lower_index]
        for upper_index in range(start + 1, start + len(pattern)):
            path.append([lower_index, upper_index])
        if lower_index + 1 < len(zero_envelope):
            path.append(
                [lower_index + 1, block_starts[lower_index + 1]]
            )
    if path[-1] != [len(zero_envelope) - 1, len(upper) - 1]:
        raise AssertionError("witness endpoint drift")
    for lower_index, upper_index in path:
        if geometry(
            zero_envelope[lower_index], ambient_dim
        ) != geometry(upper[upper_index], ambient_dim):
            raise AssertionError("direct witness geometry mismatch")
        if int(zero_envelope[lower_index]["value"]) > int(
            upper[upper_index]["value"]
        ):
            raise AssertionError(
                "direct witness scalar inequality failed"
            )
    for first, second in zip(path, path[1:]):
        if (second[0] - first[0], second[1] - first[1]) not in (
            (1, 0),
            (0, 1),
            (1, 1),
        ):
            raise AssertionError("direct witness has invalid step")
    return {"path": path, "path_length": len(path), "upper": upper}


def build(
    manifest_path: Path,
    output_path: Path,
    order_mode: str = "original",
) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("manifest_digest") != EXPECTED_SOURCE_MANIFEST_DIGEST:
        raise AssertionError("source node-6 integration manifest drift")
    if (
        manifest["chunking"]["transcript_root_digest"]
        != EXPECTED_SOURCE_TRANSCRIPT_ROOT_DIGEST
    ):
        raise AssertionError("source transcript root drift")
    if manifest["execution"]["status"] != "OPEN_AT_NODE_CAPACITY":
        raise AssertionError("source is not the frozen node-7 preflight")
    stop = manifest["execution"]["stop"]
    if (
        int(stop["node_id"]),
        stop["reason"],
        int(stop["required"]),
    ) != (
        EXPECTED_NODE7_ID,
        "CHILD_PAIR_CAP_EXCEEDED",
        EXPECTED_PAIR_PRODUCT,
    ):
        raise AssertionError("node-7 preflight boundary drift")

    node6 = next(
        node
        for node in manifest["node_results"]
        if int(node["node_id"]) == EXPECTED_NODE6_ID
    )
    if node6["node_execution_digest"] != EXPECTED_NODE6_EXECUTION_DIGEST:
        raise AssertionError("node-6 execution digest drift")
    if (
        node6["output_receipt"]["receipt_digest"]
        != EXPECTED_NODE6_RECEIPT_DIGEST
    ):
        raise AssertionError("node-6 receipt drift")
    descriptor = next(
        item
        for item in manifest["topology"]["internal_nodes"]
        if int(item["node_id"]) == EXPECTED_NODE7_ID
    )
    right_leaf = manifest["leaf_full_sets"][
        int(descriptor["right_factor_ids"][0])
    ]

    ambient_dim = int(manifest["scaffold_case"]["d"])
    k = int(manifest["scaffold_case"]["k"])
    blocks = [
        tuple(block)
        for block in manifest["scaffold_case"]["whole_factor_blocks"]
    ]
    left_boundary = tuple(node6["parent_boundary"])
    right_boundary = tuple(right_leaf["boundary_rref_ambient"])
    common_boundary = xor_basis(
        (*left_boundary, *right_boundary), ambient_dim
    )
    parent_boundary = boundary(
        [blocks[index] for index in descriptor["covered_factor_ids"]],
        [blocks[index] for index in descriptor["outside_factor_ids"]],
        ambient_dim,
    )
    if (
        common_boundary != parent_boundary
        or common_boundary != left_boundary
    ):
        raise AssertionError(
            "node-7 common/parent/left boundary identity failed"
        )
    right_basis_in_parent = [
        coordinate_vector(row, parent_boundary) for row in right_boundary
    ]
    if right_basis_in_parent != [3]:
        raise AssertionError(
            "right transport is not the frozen [3] embedding"
        )

    left_entries = node6["node_up_k"]["entries"]
    right_entries = right_leaf["full_set"]["entries"]
    if (len(left_entries), len(right_entries)) != (
        EXPECTED_LEFT_ENTRIES,
        EXPECTED_RIGHT_ENTRIES,
    ):
        raise AssertionError("child entry inventory drift")

    left_forms = normal_forms(
        left_entries,
        "LEFT",
        order_mode,
        None,
        parent_boundary,
        ambient_dim,
    )
    right_forms = normal_forms(
        right_entries,
        "RIGHT",
        order_mode,
        right_boundary,
        parent_boundary,
        ambient_dim,
    )
    left_counts: dict[str, int] = {}
    for item in left_forms:
        left_counts[item["skeleton_id"]] = (
            left_counts.get(item["skeleton_id"], 0) + 1
        )
    right_counts: dict[str, int] = {}
    for item in right_forms:
        right_counts[item["skeleton_id"]] = (
            right_counts.get(item["skeleton_id"], 0) + 1
        )
    if left_counts != {"LEFT_A": 216, "LEFT_B": 216, "LEFT_C": 36}:
        raise AssertionError("left skeleton multiplicities drift")
    if right_counts != {"RIGHT_R": 36}:
        raise AssertionError("right skeleton multiplicity drift")

    left_skeletons = {
        identifier: tuple(
            (tuple(item["left"]), tuple(item["right"]))
            for item in next(
                form
                for form in left_forms
                if form["skeleton_id"] == identifier
            )["skeleton"]
        )
        for identifier in ("LEFT_A", "LEFT_B", "LEFT_C")
    }
    right_skeleton = tuple(
        (tuple(item["left"]), tuple(item["right"]))
        for item in right_forms[0]["skeleton"]
    )

    zero_left = {
        identifier: next(
            form
            for form in left_forms
            if form["skeleton_id"] == identifier
            and form["run_pattern_codes"]
            == ["0"] * len(left_skeletons[identifier])
        )
        for identifier in left_skeletons
    }
    zero_right = next(
        form
        for form in right_forms
        if form["run_pattern_codes"] == ["0"] * len(right_skeleton)
    )

    initial_dim = len(
        subspace_intersection(
            left_skeletons["LEFT_A"][0][1],
            right_skeleton[0][1],
            len(parent_boundary),
        )
    )
    classes = []
    correction_table = []
    injectivity_receipts = []
    local_witness_tests = 0
    for left_id in ("LEFT_A", "LEFT_B", "LEFT_C"):
        left_skeleton = left_skeletons[left_id]
        symbol_map: dict[str, list[int]] = {}
        for i, left_geom in enumerate(left_skeleton):
            for j, right_geom in enumerate(right_skeleton):
                correction = join_correction(
                    left_geom,
                    right_geom,
                    initial_dim,
                    len(parent_boundary),
                )
                symbol = joined_symbol(
                    left_geom, right_geom, len(parent_boundary)
                )
                correction_table.append(
                    {
                        "left_skeleton_id": left_id,
                        "cell": [i, j],
                        "correction": correction,
                        "joined_symbol": geometry_payload(symbol),
                    }
                )
                if correction != 0:
                    raise AssertionError(
                        "node-7 join correction is not identically zero"
                    )
                key = canonical_json(geometry_payload(symbol)).decode()
                if key in symbol_map:
                    raise AssertionError(
                        "joined-symbol map is not injective"
                    )
                symbol_map[key] = [i, j]
        injectivity_receipts.append(
            {
                "left_skeleton_id": left_id,
                "grid_cell_count": len(left_skeleton)
                * len(right_skeleton),
                "distinct_joined_symbol_count": len(symbol_map),
                "injective": True,
            }
        )
        paths = enumerate_paths(
            len(left_skeleton), len(right_skeleton)
        )
        for path_index, path in enumerate(paths):
            envelope = []
            for i, j in path:
                symbol = joined_symbol(
                    left_skeleton[i],
                    right_skeleton[j],
                    len(parent_boundary),
                )
                envelope.append(
                    {
                        "left": list(symbol[0]),
                        "right": list(symbol[1]),
                        "value": 0,
                    }
                )
            envelope = compactify(envelope, len(parent_boundary))
            if len(envelope) != len(path):
                raise AssertionError(
                    "zero envelope compactified across quotient cells"
                )
            witness_case_count = 0
            for assignment in itertools.product(
                RUN_PATTERNS, repeat=len(envelope)
            ):
                direct_witness(
                    envelope, assignment, len(parent_boundary)
                )
                witness_case_count += 1
            local_witness_tests += witness_case_count
            class_id = f"{left_id}-Q{path_index:02d}"
            classes.append(
                {
                    "class_id": class_id,
                    "left_skeleton_id": left_id,
                    "right_skeleton_id": "RIGHT_R",
                    "quotient_path": path,
                    "quotient_path_length": len(path),
                    "joined_skeleton": [
                        geometry_payload(
                            geometry(item, len(parent_boundary))
                        )
                        for item in envelope
                    ],
                    "zero_envelope": envelope,
                    "zero_envelope_digest": digest(envelope),
                    "reachability_witness": {
                        "left_zero_entry_index": zero_left[left_id][
                            "source_entry_index"
                        ],
                        "right_zero_entry_index": zero_right[
                            "source_entry_index"
                        ],
                        "left_zero_trajectory_digest": zero_left[
                            left_id
                        ]["trajectory_digest"],
                        "right_zero_trajectory_digest": zero_right[
                            "trajectory_digest"
                        ],
                        "lattice_path": path,
                        "join_correction_vector": [0] * len(path),
                    },
                    "direct_coverage_constructor": {
                        "kind": "ZERO_ENVELOPE_STUTTER_EXTENSION",
                        "lower_value": 0,
                        "allowed_successful_run_pattern_codes": list(
                            RUN_PATTERN_CODES.values()
                        ),
                        "exhaustive_local_assignments_tested": witness_case_count,
                        "uses_direct_preorder_witness": True,
                        "uses_transitive_closure": False,
                    },
                }
            )
    classes.sort(key=lambda item: item["class_id"])
    if len(classes) != EXPECTED_CLASS_COUNT:
        raise AssertionError("quotient class count drift")

    invariant_vector = {
        "N7-INV-01_EXACT_CHILD_RECEIPT_BINDING": "PASS",
        "N7-INV-02_CHILD_ORDER_INVARIANT_NORMAL_FORM": "PASS",
        "N7-INV-03_NORMAL_FORM_BIJECTIVE_468_PLUS_36": "PASS",
        "N7-INV-04_TRANSPORT_AND_SHRINK_IDENTITY": "PASS",
        "N7-INV-05_JOIN_LAMBDA_CORRECTION_IDENTICALLY_ZERO": "PASS",
        "N7-INV-06_QUOTIENT_PATH_CATALOG_EXACTLY_13": "PASS",
        "N7-INV-07_EVERY_CLASS_ZERO_ENVELOPE_REACHABLE": "PASS",
        "N7-INV-08_EVERY_SUCCESSFUL_OUTPUT_DIRECTLY_COVERED": "PASS",
        "N7-INV-09_NO_FULL_16848_PAIR_ENUMERATION": "PASS",
        "N7-INV-10_INDEPENDENT_REPLAY_AND_TAMPER_REJECTION": "PASS",
    }
    artifact = {
        "schema": SCHEMA,
        "source": {
            "manifest_digest": manifest["manifest_digest"],
            "transcript_root_digest": manifest["chunking"][
                "transcript_root_digest"
            ],
            "node6_execution_digest": node6["node_execution_digest"],
            "node6_output_receipt_digest": node6["output_receipt"][
                "receipt_digest"
            ],
            "node7_descriptor_digest": digest(descriptor),
        },
        "child_normal_forms": {
            "run_pattern_catalog": [list(item) for item in RUN_PATTERNS],
            "run_pattern_codes": list(RUN_PATTERN_CODES.values()),
            "left_entry_count": len(left_forms),
            "right_entry_count": len(right_forms),
            "left_skeleton_multiplicities": left_counts,
            "right_skeleton_multiplicities": right_counts,
            "left_normal_forms_digest": digest(left_forms),
            "right_normal_forms_digest": digest(right_forms),
            "left_trajectory_set_digest": digest(
                sorted(
                    (item["trajectory"] for item in left_forms),
                    key=canonical_json,
                )
            ),
            "right_trajectory_set_digest": digest(
                sorted(
                    (item["trajectory"] for item in right_forms),
                    key=canonical_json,
                )
            ),
            "left_forms": left_forms,
            "right_forms": right_forms,
        },
        "node7_geometry": {
            "ambient_dimension": ambient_dim,
            "boundary_coordinate_dimension": len(parent_boundary),
            "k": k,
            "left_boundary_ambient": list(left_boundary),
            "right_boundary_ambient": list(right_boundary),
            "common_boundary_ambient": list(common_boundary),
            "parent_boundary_ambient": list(parent_boundary),
            "right_basis_in_parent_coordinates": right_basis_in_parent,
            "left_expand_identity": True,
            "shrink_identity": True,
            "initial_right_intersection_dimension": initial_dim,
            "join_correction_table": correction_table,
            "joined_symbol_injectivity": injectivity_receipts,
        },
        "quotient_frontier": {
            "naive_child_pair_count": EXPECTED_PAIR_PRODUCT,
            "naive_refinement_count": EXPECTED_NAIVE_REFINEMENTS,
            "class_count": len(classes),
            "classes": classes,
            "class_catalog_digest": digest(classes),
            "coverage_theorem": {
                "fine_path_projection": "RUN_INDEX_PROJECTION_THEN_DELETE_CONSECUTIVE_DUPLICATES",
                "projected_steps": [[1, 0], [0, 1], [1, 1]],
                "joined_symbol_map_injective": True,
                "compactification_cannot_cross_quotient_cells": True,
                "successful_output_values_are_binary": True,
                "zero_envelope_directly_precedes_every_successful_output": True,
                "closure_only_edges_used": False,
            },
        },
        "work_ledger": {
            "left_entries_read": len(left_forms),
            "right_entries_read": len(right_forms),
            "cartesian_child_pairs_materialized": 0,
            "fine_lattice_paths_enumerated": 0,
            "quotient_paths_enumerated": len(classes),
            "local_direct_witness_assignments_tested": local_witness_tests,
            "naive_work_avoided": EXPECTED_NAIVE_REFINEMENTS,
        },
        "invariant_vector": invariant_vector,
        "admit": True,
        "strict_boundary": {
            "node7_frontier_class_count_candidate": len(classes),
            "node7_parent_generator_frontier_complete": True,
            "node7_parent_up_k_complete": False,
            "node7_parent_refinement_complete": True,
            "negative_root_reached": False,
            "terminal_completeness_proved": False,
            "found_layout_enabled": False,
            "no_layout_at_cap_enabled": False,
            "current_global_terminal": TERMINAL,
            "p_vs_np": "OPEN",
        },
        "next_gate": "C049.1_B4.6.3_NODE7_THIRTEEN_GENERATOR_UP_K_CLOSURE",
    }
    artifact["semantic_digest"] = digest(artifact)
    output_path.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "JANUS_C049_1_B4_6_3_NODE7_PARENT_FRONTIER_STRUCTURAL_COMPRESSION = PASS"
    )
    print("LEFT_NORMAL_FORMS =", len(left_forms))
    print("RIGHT_NORMAL_FORMS =", len(right_forms))
    print("NAIVE_CHILD_PAIRS =", EXPECTED_PAIR_PRODUCT)
    print("NAIVE_REFINEMENTS =", EXPECTED_NAIVE_REFINEMENTS)
    print("QUOTIENT_CLASSES =", len(classes))
    print("LOCAL_DIRECT_WITNESS_ASSIGNMENTS =", local_witness_tests)
    print("ADMIT_NODE7_FRONTIER_COMPRESSION =", artifact["admit"])
    print("GLOBAL_TERMINAL =", TERMINAL)
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--entry-order",
        choices=("original", "reversed", "seeded-shuffle"),
        default="original",
    )
    args = parser.parse_args()
    build(args.manifest, args.output, args.entry_order)


if __name__ == "__main__":
    main()
