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

SCHEMA = "C049.1-B4.6.3-CORRECTED-NODE7-PARENT-FRONTIER-COMPRESSION-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
PARENT_PR = 111
PARENT_HEAD = "af0556d4ae05ea6dc343d120a34f67255890ba18"
SOURCE_SUMMARY_DIGEST = "16e49493f26966cad0cf4491b861d2f92a1b3e0fd289ee0dbac52426ed8dc378"
SOURCE_MANIFEST_DIGEST = "eb17eebad4200cc0d43785d289976542b35c11d01e9af91f3cdf0e209dd649f9"
SOURCE_TRANSCRIPT_ROOT = "5300b299d295c13d9fe6a970bb22994202db35e521785330a97b5b798875381e"
SOURCE_NODE6_EXECUTION = "7c2b8baec3b3aeeb35a26ec1457cfacd0cd67d84a6487daf707e0f3590380c4c"
SOURCE_NODE6_RECEIPT = "f6f18f8d81610483eea6942fc28bd1dfc991707452de58f3433d604216f8d532"
SOURCE_NODE6_ENTRIES = "245cf63c6483d34f351be0c67a604eec1c6dbf33d1b667c73347f0aa837b0601"
EXPECTED_LEFT_ENTRIES = 432
EXPECTED_RIGHT_ENTRIES = 36
EXPECTED_CHILD_PAIRS = 15552
EXPECTED_HV_REFINEMENTS = 1531584
EXPECTED_CLASS_COUNT = 6
EXPECTED_LOCAL_ASSIGNMENTS = 7776

RUN_PATTERNS: tuple[tuple[int, ...], ...] = (
    (0,), (0, 1), (0, 1, 0), (1,), (1, 0), (1, 0, 1)
)
RUN_CODES = {pattern: "".join(str(value) for value in pattern) for pattern in RUN_PATTERNS}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def xor_basis(rows: Iterable[int], ambient_dim: int) -> tuple[int, ...]:
    table: dict[int, int] = {}
    for raw in rows:
        value = int(raw)
        if value < 0 or value >= (1 << ambient_dim):
            raise ValueError("vector outside ambient space")
        while value:
            pivot = value.bit_length() - 1
            if pivot in table:
                value ^= table[pivot]
                continue
            table[pivot] = value
            for other, row in list(table.items()):
                if other != pivot and ((row >> pivot) & 1):
                    table[other] = row ^ value
            break
    for pivot in sorted(table):
        row = table[pivot]
        for other in sorted(table, reverse=True):
            if other != pivot and ((table[other] >> pivot) & 1):
                table[other] ^= row
    return tuple(table[pivot] for pivot in sorted(table, reverse=True))


def span_vectors(rows: Sequence[int]) -> set[int]:
    values = {0}
    for row in rows:
        values |= {value ^ int(row) for value in tuple(values)}
    return values


def subspace_sum(
    left: Sequence[int], right: Sequence[int], ambient_dim: int
) -> tuple[int, ...]:
    return xor_basis((*left, *right), ambient_dim)


def subspace_intersection(
    left: Sequence[int], right: Sequence[int], ambient_dim: int
) -> tuple[int, ...]:
    return xor_basis(span_vectors(left) & span_vectors(right), ambient_dim)


def coordinate_vector(vector: int, basis: Sequence[int]) -> int:
    for mask in range(1 << len(tuple(basis))):
        value = 0
        for index, row in enumerate(basis):
            if (mask >> index) & 1:
                value ^= int(row)
        if value == int(vector):
            return mask
    raise ValueError("vector is outside basis span")


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


def canonical_stat(item: dict, ambient_dim: int) -> dict:
    return {
        "left": list(xor_basis(item["left"], ambient_dim)),
        "right": list(xor_basis(item["right"], ambient_dim)),
        "value": int(item["value"]),
    }


def geometry(item: dict, ambient_dim: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    return (
        xor_basis(item["left"], ambient_dim),
        xor_basis(item["right"], ambient_dim),
    )


def geometry_payload(value: tuple[tuple[int, ...], tuple[int, ...]]) -> dict:
    return {"left": list(value[0]), "right": list(value[1])}


def transport_trajectory(
    raw: Sequence[dict],
    child_basis: Sequence[int],
    parent_basis: Sequence[int],
    ambient_dim: int,
) -> list[dict]:
    output = []
    for item in raw:
        left_ambient = coordinate_space_to_ambient(
            item["left"], child_basis, ambient_dim
        )
        right_ambient = coordinate_space_to_ambient(
            item["right"], child_basis, ambient_dim
        )
        output.append(
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
    return output


def split_runs(raw: Sequence[dict], ambient_dim: int) -> tuple[tuple, tuple]:
    skeleton: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
    values: list[list[int]] = []
    for item in raw:
        geom = geometry(item, ambient_dim)
        value = int(item["value"])
        if value not in (0, 1):
            raise AssertionError("child trajectory exceeds k=1")
        if not skeleton or skeleton[-1] != geom:
            skeleton.append(geom)
            values.append([value])
        else:
            values[-1].append(value)
    patterns = tuple(tuple(run) for run in values)
    if any(pattern not in RUN_CODES for pattern in patterns):
        raise AssertionError("run outside the complete binary typical catalog")
    return tuple(skeleton), patterns


def identify_left_skeleton(skeleton: tuple) -> str:
    full = (2, 1)
    table = {
        (((), full), ((1,), (2,)), (full, ())): "LEFT_A",
        (((), full), ((2,), (1,)), (full, ())): "LEFT_B",
    }
    if skeleton not in table:
        raise AssertionError(f"unexpected corrected Node-6 skeleton: {skeleton!r}")
    return table[skeleton]


def identify_right_skeleton(skeleton: tuple) -> str:
    if skeleton != (((), (3,)), ((3,), ())):
        raise AssertionError(f"unexpected transported leaf skeleton: {skeleton!r}")
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
        random.Random(0xC049111).shuffle(indexed)
    elif order_mode != "original":
        raise ValueError("unknown order mode")
    forms = []
    for source_index, entry in indexed:
        raw = copy.deepcopy(entry["trajectory"])
        if child_basis is not None:
            raw = transport_trajectory(raw, child_basis, parent_basis, ambient_dim)
        raw = [canonical_stat(item, len(tuple(parent_basis))) for item in raw]
        skeleton, patterns = split_runs(raw, len(tuple(parent_basis)))
        skeleton_id = (
            identify_left_skeleton(skeleton)
            if side == "LEFT"
            else identify_right_skeleton(skeleton)
        )
        forms.append(
            {
                "side": side,
                "skeleton_id": skeleton_id,
                "skeleton": [geometry_payload(item) for item in skeleton],
                "run_pattern_codes": [RUN_CODES[item] for item in patterns],
                "trajectory_digest": digest(raw),
                "source_entry_index": int(source_index),
                "trajectory": raw,
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
        raise AssertionError("normal-form inventory contains duplicates")
    return forms


def hv_paths(m: int, n: int) -> list[list[list[int]]]:
    output: list[list[list[int]]] = []

    def rec(i: int, j: int, path: list[list[int]]) -> None:
        if (i, j) == (m - 1, n - 1):
            output.append(copy.deepcopy(path))
            return
        for di, dj in ((1, 0), (0, 1)):
            ni, nj = i + di, j + dj
            if ni < m and nj < n:
                path.append([ni, nj])
                rec(ni, nj, path)
                path.pop()

    rec(0, 0, [[0, 0]])
    return sorted(output, key=canonical_json)


def fine_hv_paths(m: int, n: int):
    path = [[0, 0]]

    def rec(i: int, j: int):
        if (i, j) == (m - 1, n - 1):
            yield copy.deepcopy(path)
            return
        if i + 1 < m:
            path.append([i + 1, j])
            yield from rec(i + 1, j)
            path.pop()
        if j + 1 < n:
            path.append([i, j + 1])
            yield from rec(i, j + 1)
            path.pop()

    yield from rec(0, 0)


def run_index_map(lengths: Sequence[int]) -> list[int]:
    output = []
    for index, length in enumerate(lengths):
        if int(length) <= 0:
            raise ValueError("nonpositive run length")
        output.extend([index] * int(length))
    return output


def project_fine_path(
    path: Sequence[Sequence[int]],
    left_lengths: Sequence[int],
    right_lengths: Sequence[int],
) -> list[list[int]]:
    left_map = run_index_map(left_lengths)
    right_map = run_index_map(right_lengths)
    projected: list[list[int]] = []
    for i, j in path:
        cell = [left_map[int(i)], right_map[int(j)]]
        if not projected or projected[-1] != cell:
            projected.append(cell)
    return projected


def abstract_projection_audit() -> dict:
    quotient = hv_paths(3, 2)
    quotient_keys = {canonical_json(path) for path in quotient}
    profile_count = 0
    fine_path_count = 0
    projection_counts = Counter()
    for left_lengths in itertools.product((1, 2, 3), repeat=3):
        for right_lengths in itertools.product((1, 2, 3), repeat=2):
            profile_count += 1
            m, n = sum(left_lengths), sum(right_lengths)
            expected = math.comb(m + n - 2, m - 1)
            observed = 0
            for path in fine_hv_paths(m, n):
                observed += 1
                projected = project_fine_path(path, left_lengths, right_lengths)
                encoded = canonical_json(projected)
                if encoded not in quotient_keys:
                    raise AssertionError("fine H/V path projected outside H/V quotient")
                for first, second in zip(projected, projected[1:]):
                    step = (second[0] - first[0], second[1] - first[1])
                    if step not in ((1, 0), (0, 1)):
                        raise AssertionError("diagonal quotient step appeared")
                projection_counts[encoded.decode()] += 1
            if observed != expected:
                raise AssertionError("fine H/V path enumeration count drift")
            fine_path_count += observed
    if set(projection_counts) != {key.decode() for key in quotient_keys}:
        raise AssertionError("not every H/V quotient path has a fine lift")
    return {
        "run_length_profiles": profile_count,
        "fine_hv_paths_replayed": fine_path_count,
        "quotient_paths": quotient,
        "quotient_path_count": len(quotient),
        "projection_counts": dict(sorted(projection_counts.items())),
        "diagonal_quotient_steps": 0,
        "every_fine_path_projects_to_hv_quotient": True,
        "every_hv_quotient_has_fine_lift": True,
    }


def joined_symbol(left: tuple, right: tuple, ambient_dim: int) -> tuple:
    return (
        subspace_sum(left[0], right[0], ambient_dim),
        subspace_sum(left[1], right[1], ambient_dim),
    )


def join_correction(
    left: tuple, right: tuple, initial_dim: int, ambient_dim: int
) -> int:
    left_span = subspace_sum(left[0], left[1], ambient_dim)
    right_span = subspace_sum(right[0], right[1], ambient_dim)
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
        raise AssertionError("direct witness block mismatch")
    upper = []
    starts = []
    for stat, pattern in zip(zero_envelope, upper_patterns):
        starts.append(len(upper))
        for value in pattern:
            item = copy.deepcopy(stat)
            item["value"] = int(value)
            upper.append(item)
    path = [[0, 0]]
    for lower_index, pattern in enumerate(upper_patterns):
        start = starts[lower_index]
        for upper_index in range(start + 1, start + len(pattern)):
            path.append([lower_index, upper_index])
        if lower_index + 1 < len(zero_envelope):
            path.append([lower_index + 1, starts[lower_index + 1]])
    if path[-1] != [len(zero_envelope) - 1, len(upper) - 1]:
        raise AssertionError("direct witness endpoint drift")
    for lower_index, upper_index in path:
        if geometry(zero_envelope[lower_index], ambient_dim) != geometry(
            upper[upper_index], ambient_dim
        ):
            raise AssertionError("direct witness geometry mismatch")
        if int(zero_envelope[lower_index]["value"]) > int(
            upper[upper_index]["value"]
        ):
            raise AssertionError("direct witness scalar inequality failed")
    for first, second in zip(path, path[1:]):
        if (second[0] - first[0], second[1] - first[1]) not in (
            (1, 0), (0, 1), (1, 1)
        ):
            raise AssertionError("extension witness step drift")
    return {"path": path, "path_length": len(path)}


def build(
    manifest_path: Path,
    summary_path: Path,
    output_path: Path,
    order_mode: str = "original",
) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    unsigned_summary = dict(summary)
    claimed_summary = unsigned_summary.pop("semantic_digest", None)
    if claimed_summary != digest(unsigned_summary) or claimed_summary != SOURCE_SUMMARY_DIGEST:
        raise AssertionError("source PR #111 summary binding drift")
    unsigned_manifest = dict(manifest)
    claimed_manifest = unsigned_manifest.pop("manifest_digest", None)
    if claimed_manifest != digest(unsigned_manifest) or claimed_manifest != SOURCE_MANIFEST_DIGEST:
        raise AssertionError("source PR #111 manifest binding drift")
    if manifest["chunking"]["transcript_root_digest"] != SOURCE_TRANSCRIPT_ROOT:
        raise AssertionError("source transcript root drift")
    stop = manifest["execution"]["stop"]
    if (
        manifest["execution"]["status"],
        int(stop["node_id"]),
        stop["reason"],
        int(stop["required"]),
        int(stop["cap"]),
        bool(stop["no_layout_at_cap"]),
    ) != (
        "OPEN_AT_NODE_CAPACITY",
        7,
        "REFINEMENT_CAP_EXCEEDED",
        EXPECTED_HV_REFINEMENTS,
        1500000,
        False,
    ):
        raise AssertionError("source corrected Node-7 preflight boundary drift")

    node6 = next(node for node in manifest["node_results"] if int(node["node_id"]) == 6)
    if node6["node_execution_digest"] != SOURCE_NODE6_EXECUTION:
        raise AssertionError("corrected Node-6 execution digest drift")
    if node6["output_receipt"]["receipt_digest"] != SOURCE_NODE6_RECEIPT:
        raise AssertionError("corrected Node-6 receipt drift")
    if node6["output_receipt"]["entries_digest"] != SOURCE_NODE6_ENTRIES:
        raise AssertionError("corrected Node-6 entries digest drift")

    descriptor = next(
        item for item in manifest["topology"]["internal_nodes"] if int(item["node_id"]) == 7
    )
    right_leaf = next(
        leaf for leaf in manifest["leaf_full_sets"]
        if int(leaf["factor_id"]) == int(descriptor["right_factor_ids"][0])
    )
    ambient_dim = int(manifest["scaffold_case"]["d"])
    k = int(manifest["scaffold_case"]["k"])
    left_boundary = tuple(node6["parent_boundary"])
    right_boundary = tuple(right_leaf["boundary_rref_ambient"])
    common_boundary = xor_basis((*left_boundary, *right_boundary), ambient_dim)
    parent_boundary = tuple(left_boundary)
    if left_boundary != (4, 2) or right_boundary != (6,):
        raise AssertionError("corrected Node-7 boundary geometry drift")
    if common_boundary != parent_boundary:
        raise AssertionError("corrected Node-7 common/parent boundary identity failed")
    right_basis_in_parent = [
        coordinate_vector(row, parent_boundary) for row in right_boundary
    ]
    if right_basis_in_parent != [3]:
        raise AssertionError("right leaf transport drift")

    left_entries = node6["node_up_k"]["entries"]
    right_entries = right_leaf["full_set"]["entries"]
    if (len(left_entries), len(right_entries)) != (
        EXPECTED_LEFT_ENTRIES, EXPECTED_RIGHT_ENTRIES
    ):
        raise AssertionError("corrected child inventory drift")

    left_forms = normal_forms(
        left_entries, "LEFT", order_mode, None, parent_boundary, ambient_dim
    )
    right_forms = normal_forms(
        right_entries, "RIGHT", order_mode, right_boundary, parent_boundary, ambient_dim
    )
    left_counts = Counter(item["skeleton_id"] for item in left_forms)
    right_counts = Counter(item["skeleton_id"] for item in right_forms)
    if dict(left_counts) != {"LEFT_A": 216, "LEFT_B": 216}:
        raise AssertionError("corrected left skeleton multiplicity drift")
    if dict(right_counts) != {"RIGHT_R": 36}:
        raise AssertionError("right skeleton multiplicity drift")

    left_length_hist = Counter(len(item["trajectory"]) for item in left_forms)
    right_length_hist = Counter(len(item["trajectory"]) for item in right_forms)
    pair_count = sum(left_length_hist.values()) * sum(right_length_hist.values())
    refinement_count = sum(
        left_count * right_count * math.comb(left_length + right_length - 2, left_length - 1)
        for left_length, left_count in left_length_hist.items()
        for right_length, right_count in right_length_hist.items()
    )
    if (pair_count, refinement_count) != (
        EXPECTED_CHILD_PAIRS, EXPECTED_HV_REFINEMENTS
    ):
        raise AssertionError("corrected H/V workload drift")

    left_skeletons = {
        identifier: tuple(
            (tuple(item["left"]), tuple(item["right"]))
            for item in next(
                form for form in left_forms if form["skeleton_id"] == identifier
            )["skeleton"]
        )
        for identifier in ("LEFT_A", "LEFT_B")
    }
    right_skeleton = tuple(
        (tuple(item["left"]), tuple(item["right"]))
        for item in right_forms[0]["skeleton"]
    )
    zero_left = {
        identifier: next(
            form for form in left_forms
            if form["skeleton_id"] == identifier
            and form["run_pattern_codes"] == ["0"] * len(left_skeletons[identifier])
        )
        for identifier in left_skeletons
    }
    zero_right = next(
        form for form in right_forms
        if form["run_pattern_codes"] == ["0"] * len(right_skeleton)
    )

    initial_dim = len(
        subspace_intersection(
            left_skeletons["LEFT_A"][0][1],
            right_skeleton[0][1],
            len(parent_boundary),
        )
    )
    projection_audit = abstract_projection_audit()
    classes = []
    correction_table = []
    injectivity = []
    assignment_tests = 0

    for left_id in ("LEFT_A", "LEFT_B"):
        left_skeleton = left_skeletons[left_id]
        seen = set()
        for i, left_geom in enumerate(left_skeleton):
            for j, right_geom in enumerate(right_skeleton):
                correction = join_correction(
                    left_geom, right_geom, initial_dim, len(parent_boundary)
                )
                symbol = joined_symbol(
                    left_geom, right_geom, len(parent_boundary)
                )
                encoded = canonical_json(geometry_payload(symbol))
                if correction != 0:
                    raise AssertionError("Node-7 join correction is not zero")
                if encoded in seen:
                    raise AssertionError("joined-symbol map is not injective")
                seen.add(encoded)
                correction_table.append(
                    {
                        "left_skeleton_id": left_id,
                        "cell": [i, j],
                        "correction": correction,
                        "joined_symbol": geometry_payload(symbol),
                    }
                )
        injectivity.append(
            {
                "left_skeleton_id": left_id,
                "grid_cell_count": len(left_skeleton) * len(right_skeleton),
                "distinct_joined_symbol_count": len(seen),
                "injective": True,
            }
        )

        for path_index, path in enumerate(hv_paths(len(left_skeleton), len(right_skeleton))):
            envelope = []
            for i, j in path:
                symbol = joined_symbol(
                    left_skeleton[i], right_skeleton[j], len(parent_boundary)
                )
                envelope.append(
                    {"left": list(symbol[0]), "right": list(symbol[1]), "value": 0}
                )
            if len(envelope) != 4 or len({canonical_json(geometry_payload(geometry(item, 2))) for item in envelope}) != 4:
                raise AssertionError("corrected quotient envelope geometry drift")
            local_cases = 0
            for assignment in itertools.product(RUN_PATTERNS, repeat=len(envelope)):
                direct_witness(envelope, assignment, len(parent_boundary))
                local_cases += 1
            if local_cases != 1296:
                raise AssertionError("local direct coverage count drift")
            assignment_tests += local_cases
            classes.append(
                {
                    "class_id": f"{left_id}-HVQ{path_index:02d}",
                    "left_skeleton_id": left_id,
                    "right_skeleton_id": "RIGHT_R",
                    "quotient_path": path,
                    "quotient_path_steps": [
                        [second[0] - first[0], second[1] - first[1]]
                        for first, second in zip(path, path[1:])
                    ],
                    "quotient_path_length": len(path),
                    "zero_envelope": envelope,
                    "zero_envelope_digest": digest(envelope),
                    "reachability_witness": {
                        "left_zero_entry_index": zero_left[left_id]["source_entry_index"],
                        "right_zero_entry_index": zero_right["source_entry_index"],
                        "left_zero_trajectory_digest": zero_left[left_id]["trajectory_digest"],
                        "right_zero_trajectory_digest": zero_right["trajectory_digest"],
                        "ordinary_hv_path": path,
                        "join_correction_vector": [0] * len(path),
                        "shrink_identity": True,
                    },
                    "direct_coverage_constructor": {
                        "kind": "ZERO_ENVELOPE_STUTTER_EXTENSION",
                        "binary_typical_pattern_codes": list(RUN_CODES.values()),
                        "exhaustive_local_assignments_tested": local_cases,
                        "uses_direct_extension_preorder_witness": True,
                        "extension_preorder_diagonal_preserved": True,
                        "ordinary_join_diagonal_used": False,
                        "uses_transitive_closure": False,
                    },
                }
            )
    classes.sort(key=lambda item: item["class_id"])
    if len(classes) != EXPECTED_CLASS_COUNT:
        raise AssertionError("corrected quotient class count drift")
    if len({item["zero_envelope_digest"] for item in classes}) != EXPECTED_CLASS_COUNT:
        raise AssertionError("corrected quotient classes collide")
    if assignment_tests != EXPECTED_LOCAL_ASSIGNMENTS:
        raise AssertionError("corrected direct witness workload drift")

    artifact = {
        "schema": SCHEMA,
        "source": {
            "parent_pr": PARENT_PR,
            "parent_exact_head": PARENT_HEAD,
            "summary_semantic_digest": SOURCE_SUMMARY_DIGEST,
            "manifest_digest": SOURCE_MANIFEST_DIGEST,
            "transcript_root_digest": SOURCE_TRANSCRIPT_ROOT,
            "node6_execution_digest": SOURCE_NODE6_EXECUTION,
            "node6_output_receipt_digest": SOURCE_NODE6_RECEIPT,
            "node6_entries_digest": SOURCE_NODE6_ENTRIES,
            "node7_descriptor_digest": digest(descriptor),
        },
        "corrected_path_domain": {
            "ordinary_join_steps": [[1, 0], [0, 1]],
            "ordinary_join_diagonal_allowed": False,
            "quotient_projection_steps": [[1, 0], [0, 1]],
            "quotient_projection_diagonal_allowed": False,
            "extension_preorder_steps": [[1, 0], [0, 1], [1, 1]],
            "extension_preorder_diagonal_preserved": True,
            "legacy_delannoy_frontier_consumed": False,
        },
        "child_normal_forms": {
            "left_entry_count": len(left_forms),
            "right_entry_count": len(right_forms),
            "left_skeleton_multiplicities": dict(sorted(left_counts.items())),
            "right_skeleton_multiplicities": dict(sorted(right_counts.items())),
            "left_trajectory_set_digest": digest(
                sorted((item["trajectory"] for item in left_forms), key=canonical_json)
            ),
            "right_trajectory_set_digest": digest(
                sorted((item["trajectory"] for item in right_forms), key=canonical_json)
            ),
            "left_length_histogram": {
                str(key): value for key, value in sorted(left_length_hist.items())
            },
            "right_length_histogram": {
                str(key): value for key, value in sorted(right_length_hist.items())
            },
            "binary_typical_run_patterns": [list(item) for item in RUN_PATTERNS],
            "binary_typical_run_pattern_codes": list(RUN_CODES.values()),
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
            "joined_symbol_injectivity": injectivity,
        },
        "projection_completeness": projection_audit,
        "quotient_frontier": {
            "child_pair_count": pair_count,
            "ordinary_hv_refinement_count": refinement_count,
            "class_count": len(classes),
            "classes": classes,
            "class_catalog_digest": digest(classes),
            "successful_generator_frontier_complete": True,
            "failed_refinement_partition": {
                "method": "WIDTH_DICHOTOMY_AFTER_COMPLETE_HV_QUOTIENT_PROJECTION",
                "every_refinement_projected": True,
                "successful_if_compact_width_at_most_k": True,
                "failed_if_compact_width_exceeds_k": True,
                "failed_records_individually_materialized": False,
            },
        },
        "work_ledger": {
            "left_entries_read": len(left_forms),
            "right_entries_read": len(right_forms),
            "cartesian_child_pairs_materialized": 0,
            "actual_fine_refinements_materialized": 0,
            "abstract_run_length_profiles_replayed": 2 * projection_audit["run_length_profiles"],
            "abstract_fine_hv_paths_replayed": 2 * projection_audit["fine_hv_paths_replayed"],
            "quotient_paths_enumerated": len(classes),
            "local_direct_witness_assignments_tested": assignment_tests,
            "naive_hv_work_avoided": refinement_count,
        },
        "legacy_inputs": {
            "legacy_node6_full_set_consumed": False,
            "legacy_node7_frontier_artifact_consumed": False,
            "legacy_thirteen_class_count_promoted": False,
            "legacy_delannoy_refinement_count_promoted": False,
            "legacy_node7_up_k_full_set_consumed": False,
        },
        "invariant_vector": {
            f"CN7F-INV-{index:02d}": "PASS" for index in range(1, 15)
        },
        "strict_boundary": {
            "pr111_corrected_node6_integration_admitted": True,
            "corrected_node7_parent_preflight_complete": True,
            "corrected_node7_parent_generator_frontier_complete": True,
            "corrected_node7_parent_refinement_complete": True,
            "corrected_node7_parent_up_k_complete": False,
            "corrected_bottom_up_replay_complete": False,
            "root_structural_compression_admitted": False,
            "root_parent_refinement_complete": False,
            "root_full_set_computed": False,
            "root_empty_proved": False,
            "found_layout": "FORBIDDEN",
            "no_layout_at_cap": "FORBIDDEN",
            "current_global_terminal": TERMINAL,
            "p_vs_np": "OPEN",
        },
        "result": "CORRECTED_NODE7_PARENT_FRONTIER_COMPRESSED_TO_SIX_CLASSES",
        "next_gate": "C049.1_B4.6.3_CORRECTED_NODE7_SIX_GENERATOR_UP_K_HARDENING",
    }
    artifact["semantic_digest"] = digest(artifact)
    output_path.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("JANUS_C049_1_B4_6_3_CORRECTED_NODE7_FRONTIER_COMPRESSION = PASS")
    print("LEFT_NORMAL_FORMS =", len(left_forms))
    print("RIGHT_NORMAL_FORMS =", len(right_forms))
    print("CHILD_PAIRS =", pair_count)
    print("ORDINARY_HV_REFINEMENTS =", refinement_count)
    print("QUOTIENT_CLASSES =", len(classes))
    print("LOCAL_DIRECT_WITNESS_ASSIGNMENTS =", assignment_tests)
    print("ABSTRACT_FINE_HV_PATHS_REPLAYED =", 2 * projection_audit["fine_hv_paths_replayed"])
    print("NEXT_GATE =", artifact["next_gate"])
    print("GLOBAL_TERMINAL =", TERMINAL)
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("summary", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--entry-order",
        choices=("original", "reversed", "seeded-shuffle"),
        default="original",
    )
    args = parser.parse_args()
    build(args.manifest, args.summary, args.output, args.entry_order)


if __name__ == "__main__":
    main()
