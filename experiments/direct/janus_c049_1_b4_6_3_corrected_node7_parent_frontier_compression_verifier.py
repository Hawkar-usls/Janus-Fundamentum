#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
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
PARENT_HEAD = "af0556d4ae05ea6dc343d120a34f67255890ba18"
SUMMARY_DIGEST = "16e49493f26966cad0cf4491b861d2f92a1b3e0fd289ee0dbac52426ed8dc378"
MANIFEST_DIGEST = "eb17eebad4200cc0d43785d289976542b35c11d01e9af91f3cdf0e209dd649f9"
TRANSCRIPT_ROOT = "5300b299d295c13d9fe6a970bb22994202db35e521785330a97b5b798875381e"
NODE6_EXECUTION = "7c2b8baec3b3aeeb35a26ec1457cfacd0cd67d84a6487daf707e0f3590380c4c"
NODE6_RECEIPT = "f6f18f8d81610483eea6942fc28bd1dfc991707452de58f3433d604216f8d532"
NODE6_ENTRIES = "245cf63c6483d34f351be0c67a604eec1c6dbf33d1b667c73347f0aa837b0601"
PATTERNS = ((0,), (0, 1), (0, 1, 0), (1,), (1, 0), (1, 0, 1))
CODES = {pattern: "".join(map(str, pattern)) for pattern in PATTERNS}


def packed(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(value: Any) -> str:
    return hashlib.sha256(packed(value)).hexdigest()


def rref(rows: Iterable[int], dimension: int) -> tuple[int, ...]:
    pivots: dict[int, int] = {}
    for raw in rows:
        value = int(raw)
        if not 0 <= value < (1 << dimension):
            raise AssertionError("vector range")
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                for other, row in list(pivots.items()):
                    if other != pivot and ((row >> pivot) & 1):
                        pivots[other] = row ^ value
                break
    for pivot in sorted(pivots):
        row = pivots[pivot]
        for other in sorted(pivots, reverse=True):
            if other != pivot and ((pivots[other] >> pivot) & 1):
                pivots[other] ^= row
    return tuple(pivots[pivot] for pivot in sorted(pivots, reverse=True))


def vectors(rows: Sequence[int]) -> set[int]:
    result = {0}
    for row in rows:
        result |= {value ^ int(row) for value in tuple(result)}
    return result


def space_sum(left: Sequence[int], right: Sequence[int], dimension: int) -> tuple[int, ...]:
    return rref((*left, *right), dimension)


def space_meet(left: Sequence[int], right: Sequence[int], dimension: int) -> tuple[int, ...]:
    return rref(vectors(left) & vectors(right), dimension)


def coordinates(vector: int, basis: Sequence[int]) -> int:
    for mask in range(1 << len(tuple(basis))):
        value = 0
        for index, row in enumerate(basis):
            if (mask >> index) & 1:
                value ^= int(row)
        if value == int(vector):
            return mask
    raise AssertionError("coordinate map")


def lift_space(space: Sequence[int], basis: Sequence[int], ambient: int) -> tuple[int, ...]:
    output = []
    for mask in space:
        value = 0
        for index, row in enumerate(basis):
            if (int(mask) >> index) & 1:
                value ^= int(row)
        output.append(value)
    return rref(output, ambient)


def lower_space(space: Sequence[int], basis: Sequence[int]) -> tuple[int, ...]:
    return rref((coordinates(row, basis) for row in space), len(tuple(basis)))


def stat_geometry(item: dict, dimension: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    return rref(item["left"], dimension), rref(item["right"], dimension)


def geom_json(value: tuple) -> dict:
    return {"left": list(value[0]), "right": list(value[1])}


def canonical_trajectory(raw: Sequence[dict], dimension: int) -> list[dict]:
    return [
        {
            "left": list(rref(item["left"], dimension)),
            "right": list(rref(item["right"], dimension)),
            "value": int(item["value"]),
        }
        for item in raw
    ]


def move_to_parent(
    raw: Sequence[dict],
    child_basis: Sequence[int],
    parent_basis: Sequence[int],
    ambient: int,
) -> list[dict]:
    output = []
    for item in raw:
        left = lower_space(lift_space(item["left"], child_basis, ambient), parent_basis)
        right = lower_space(lift_space(item["right"], child_basis, ambient), parent_basis)
        output.append({"left": list(left), "right": list(right), "value": int(item["value"])})
    return output


def runs(raw: Sequence[dict], dimension: int) -> tuple[tuple, tuple]:
    skeleton = []
    scalars = []
    for item in raw:
        geom = stat_geometry(item, dimension)
        value = int(item["value"])
        if value not in (0, 1):
            raise AssertionError("nonbinary entry")
        if not skeleton or skeleton[-1] != geom:
            skeleton.append(geom)
            scalars.append([value])
        else:
            scalars[-1].append(value)
    scalar_runs = tuple(tuple(item) for item in scalars)
    if any(item not in CODES for item in scalar_runs):
        raise AssertionError("typical catalog")
    return tuple(skeleton), scalar_runs


def left_name(skeleton: tuple) -> str:
    full = (2, 1)
    if skeleton == (((), full), ((1,), (2,)), (full, ())):
        return "LEFT_A"
    if skeleton == (((), full), ((2,), (1,)), (full, ())):
        return "LEFT_B"
    raise AssertionError("corrected left skeleton")


def right_name(skeleton: tuple) -> str:
    if skeleton != (((), (3,)), ((3,), ())):
        raise AssertionError("right skeleton")
    return "RIGHT_R"


def rebuild_forms(
    entries: Sequence[dict],
    side: str,
    mode: str,
    child_basis: Sequence[int] | None,
    parent_basis: Sequence[int],
    ambient: int,
) -> list[dict]:
    indexed = list(enumerate(entries))
    if mode == "reversed":
        indexed.reverse()
    elif mode == "seeded-shuffle":
        random.Random(0x7F111).shuffle(indexed)
    elif mode != "original":
        raise AssertionError("mode")
    output = []
    for source_index, entry in indexed:
        raw = copy.deepcopy(entry["trajectory"])
        if child_basis is not None:
            raw = move_to_parent(raw, child_basis, parent_basis, ambient)
        raw = canonical_trajectory(raw, len(tuple(parent_basis)))
        skeleton, patterns = runs(raw, len(tuple(parent_basis)))
        identifier = left_name(skeleton) if side == "LEFT" else right_name(skeleton)
        output.append(
            {
                "side": side,
                "skeleton_id": identifier,
                "skeleton": [geom_json(item) for item in skeleton],
                "run_pattern_codes": [CODES[item] for item in patterns],
                "trajectory_digest": sha(raw),
                "source_entry_index": int(source_index),
                "trajectory": raw,
            }
        )
    output.sort(
        key=lambda item: packed(
            [
                item["skeleton_id"],
                item["run_pattern_codes"],
                item["trajectory_digest"],
                item["source_entry_index"],
            ]
        )
    )
    if len({item["trajectory_digest"] for item in output}) != len(output):
        raise AssertionError("duplicate forms")
    return output


def coarse_hv_paths(rows: int, columns: int) -> list[list[list[int]]]:
    answer = []
    stack = [[0, 0]]

    def visit(i: int, j: int) -> None:
        if (i, j) == (rows - 1, columns - 1):
            answer.append(copy.deepcopy(stack))
            return
        if i + 1 < rows:
            stack.append([i + 1, j])
            visit(i + 1, j)
            stack.pop()
        if j + 1 < columns:
            stack.append([i, j + 1])
            visit(i, j + 1)
            stack.pop()

    visit(0, 0)
    return sorted(answer, key=packed)


def all_fine_hv_paths(rows: int, columns: int):
    stack = [[0, 0]]

    def visit(i: int, j: int):
        if (i, j) == (rows - 1, columns - 1):
            yield copy.deepcopy(stack)
            return
        if i + 1 < rows:
            stack.append([i + 1, j])
            yield from visit(i + 1, j)
            stack.pop()
        if j + 1 < columns:
            stack.append([i, j + 1])
            yield from visit(i, j + 1)
            stack.pop()

    yield from visit(0, 0)


def index_map(lengths: Sequence[int]) -> list[int]:
    output = []
    for index, length in enumerate(lengths):
        output += [index] * int(length)
    return output


def project(path: Sequence[Sequence[int]], left_lengths: Sequence[int], right_lengths: Sequence[int]) -> list[list[int]]:
    left_map, right_map = index_map(left_lengths), index_map(right_lengths)
    output = []
    for i, j in path:
        cell = [left_map[int(i)], right_map[int(j)]]
        if not output or output[-1] != cell:
            output.append(cell)
    return output


def projection_replay() -> dict:
    quotient = coarse_hv_paths(3, 2)
    allowed = {packed(path) for path in quotient}
    profiles = 0
    fine_paths = 0
    counts = Counter()
    for left_lengths in itertools.product((1, 2, 3), repeat=3):
        for right_lengths in itertools.product((1, 2, 3), repeat=2):
            profiles += 1
            rows, columns = sum(left_lengths), sum(right_lengths)
            observed = 0
            for path in all_fine_hv_paths(rows, columns):
                observed += 1
                image = project(path, left_lengths, right_lengths)
                key = packed(image)
                if key not in allowed:
                    raise AssertionError("projection outside quotient")
                if any(
                    (second[0] - first[0], second[1] - first[1]) not in ((1, 0), (0, 1))
                    for first, second in zip(image, image[1:])
                ):
                    raise AssertionError("diagonal quotient")
                counts[key.decode()] += 1
            if observed != math.comb(rows + columns - 2, rows - 1):
                raise AssertionError("fine path count")
            fine_paths += observed
    if set(counts) != {item.decode() for item in allowed}:
        raise AssertionError("quotient lift completeness")
    return {
        "run_length_profiles": profiles,
        "fine_hv_paths_replayed": fine_paths,
        "quotient_paths": quotient,
        "quotient_path_count": 3,
        "projection_counts": dict(sorted(counts.items())),
        "diagonal_quotient_steps": 0,
        "every_fine_path_projects_to_hv_quotient": True,
        "every_hv_quotient_has_fine_lift": True,
    }


def combine(left: tuple, right: tuple, dimension: int) -> tuple:
    return (
        space_sum(left[0], right[0], dimension),
        space_sum(left[1], right[1], dimension),
    )


def lambda_delta(left: tuple, right: tuple, initial: int, dimension: int) -> int:
    left_span = space_sum(left[0], left[1], dimension)
    right_span = space_sum(right[0], right[1], dimension)
    return initial - len(space_meet(left_span, right_span, dimension))


def witness_ok(envelope: Sequence[dict], patterns: Sequence[tuple[int, ...]], dimension: int) -> bool:
    upper = []
    starts = []
    for stat, pattern in zip(envelope, patterns):
        starts.append(len(upper))
        for scalar in pattern:
            item = copy.deepcopy(stat)
            item["value"] = int(scalar)
            upper.append(item)
    path = [[0, 0]]
    for index, pattern in enumerate(patterns):
        for upper_index in range(starts[index] + 1, starts[index] + len(pattern)):
            path.append([index, upper_index])
        if index + 1 < len(envelope):
            path.append([index + 1, starts[index + 1]])
    if path[-1] != [len(envelope) - 1, len(upper) - 1]:
        return False
    for lower_index, upper_index in path:
        if stat_geometry(envelope[lower_index], dimension) != stat_geometry(upper[upper_index], dimension):
            return False
        if int(envelope[lower_index]["value"]) > int(upper[upper_index]["value"]):
            return False
    return all(
        (second[0] - first[0], second[1] - first[1]) in ((1, 0), (0, 1), (1, 1))
        for first, second in zip(path, path[1:])
    )


def independent_expected(manifest: dict, summary: dict, mode: str = "original") -> dict:
    summary_unsigned = dict(summary)
    if summary_unsigned.pop("semantic_digest", None) != sha(summary_unsigned):
        raise AssertionError("summary digest")
    manifest_unsigned = dict(manifest)
    if manifest_unsigned.pop("manifest_digest", None) != sha(manifest_unsigned):
        raise AssertionError("manifest digest")
    if summary["semantic_digest"] != SUMMARY_DIGEST or manifest["manifest_digest"] != MANIFEST_DIGEST:
        raise AssertionError("source binding")
    if manifest["chunking"]["transcript_root_digest"] != TRANSCRIPT_ROOT:
        raise AssertionError("transcript root")
    stop = manifest["execution"]["stop"]
    if (
        manifest["execution"]["status"], stop["node_id"], stop["reason"],
        stop["required"], stop["cap"], stop["no_layout_at_cap"]
    ) != ("OPEN_AT_NODE_CAPACITY", 7, "REFINEMENT_CAP_EXCEEDED", 1531584, 1500000, False):
        raise AssertionError("preflight stop")

    node6 = next(item for item in manifest["node_results"] if int(item["node_id"]) == 6)
    if (
        node6["node_execution_digest"],
        node6["output_receipt"]["receipt_digest"],
        node6["output_receipt"]["entries_digest"],
    ) != (NODE6_EXECUTION, NODE6_RECEIPT, NODE6_ENTRIES):
        raise AssertionError("node6 binding")
    descriptor = next(
        item for item in manifest["topology"]["internal_nodes"] if int(item["node_id"]) == 7
    )
    right_leaf = next(
        item for item in manifest["leaf_full_sets"]
        if int(item["factor_id"]) == int(descriptor["right_factor_ids"][0])
    )
    parent = tuple(node6["parent_boundary"])
    child = tuple(right_leaf["boundary_rref_ambient"])
    ambient = int(manifest["scaffold_case"]["d"])
    if parent != (4, 2) or child != (6,) or [coordinates(row, parent) for row in child] != [3]:
        raise AssertionError("geometry")

    left_forms = rebuild_forms(node6["node_up_k"]["entries"], "LEFT", mode, None, parent, ambient)
    right_forms = rebuild_forms(right_leaf["full_set"]["entries"], "RIGHT", mode, child, parent, ambient)
    left_counts = Counter(item["skeleton_id"] for item in left_forms)
    right_counts = Counter(item["skeleton_id"] for item in right_forms)
    if dict(left_counts) != {"LEFT_A": 216, "LEFT_B": 216} or dict(right_counts) != {"RIGHT_R": 36}:
        raise AssertionError("multiplicities")

    left_hist = Counter(len(item["trajectory"]) for item in left_forms)
    right_hist = Counter(len(item["trajectory"]) for item in right_forms)
    pairs = sum(left_hist.values()) * sum(right_hist.values())
    refinements = sum(
        lc * rc * math.comb(ll + rl - 2, ll - 1)
        for ll, lc in left_hist.items() for rl, rc in right_hist.items()
    )
    if (pairs, refinements) != (15552, 1531584):
        raise AssertionError("workload")

    left_skeletons = {
        identifier: tuple(
            (tuple(item["left"]), tuple(item["right"]))
            for item in next(form for form in left_forms if form["skeleton_id"] == identifier)["skeleton"]
        )
        for identifier in ("LEFT_A", "LEFT_B")
    }
    right_skeleton = tuple(
        (tuple(item["left"]), tuple(item["right"])) for item in right_forms[0]["skeleton"]
    )
    zero_left = {
        identifier: next(
            item for item in left_forms
            if item["skeleton_id"] == identifier
            and item["run_pattern_codes"] == ["0", "0", "0"]
        )
        for identifier in left_skeletons
    }
    zero_right = next(
        item for item in right_forms if item["run_pattern_codes"] == ["0", "0"]
    )
    initial = len(space_meet(left_skeletons["LEFT_A"][0][1], right_skeleton[0][1], 2))
    correction_table = []
    injectivity = []
    classes = []
    assignments = 0
    for identifier in ("LEFT_A", "LEFT_B"):
        seen = set()
        skeleton = left_skeletons[identifier]
        for i, left_geom in enumerate(skeleton):
            for j, right_geom in enumerate(right_skeleton):
                correction = lambda_delta(left_geom, right_geom, initial, 2)
                symbol = combine(left_geom, right_geom, 2)
                key = packed(geom_json(symbol))
                if correction != 0 or key in seen:
                    raise AssertionError("cell theorem")
                seen.add(key)
                correction_table.append(
                    {
                        "left_skeleton_id": identifier,
                        "cell": [i, j],
                        "correction": 0,
                        "joined_symbol": geom_json(symbol),
                    }
                )
        injectivity.append(
            {
                "left_skeleton_id": identifier,
                "grid_cell_count": 6,
                "distinct_joined_symbol_count": 6,
                "injective": True,
            }
        )
        for path_index, path in enumerate(coarse_hv_paths(3, 2)):
            envelope = []
            for i, j in path:
                symbol = combine(skeleton[i], right_skeleton[j], 2)
                envelope.append({"left": list(symbol[0]), "right": list(symbol[1]), "value": 0})
            local = 0
            for assignment in itertools.product(PATTERNS, repeat=4):
                if not witness_ok(envelope, assignment, 2):
                    raise AssertionError("direct witness")
                local += 1
            assignments += local
            classes.append(
                {
                    "class_id": f"{identifier}-HVQ{path_index:02d}",
                    "left_skeleton_id": identifier,
                    "right_skeleton_id": "RIGHT_R",
                    "quotient_path": path,
                    "quotient_path_steps": [
                        [second[0] - first[0], second[1] - first[1]]
                        for first, second in zip(path, path[1:])
                    ],
                    "quotient_path_length": 4,
                    "zero_envelope": envelope,
                    "zero_envelope_digest": sha(envelope),
                    "reachability_witness": {
                        "left_zero_entry_index": zero_left[identifier]["source_entry_index"],
                        "right_zero_entry_index": zero_right["source_entry_index"],
                        "left_zero_trajectory_digest": zero_left[identifier]["trajectory_digest"],
                        "right_zero_trajectory_digest": zero_right["trajectory_digest"],
                        "ordinary_hv_path": path,
                        "join_correction_vector": [0, 0, 0, 0],
                        "shrink_identity": True,
                    },
                    "direct_coverage_constructor": {
                        "kind": "ZERO_ENVELOPE_STUTTER_EXTENSION",
                        "binary_typical_pattern_codes": list(CODES.values()),
                        "exhaustive_local_assignments_tested": 1296,
                        "uses_direct_extension_preorder_witness": True,
                        "extension_preorder_diagonal_preserved": True,
                        "ordinary_join_diagonal_used": False,
                        "uses_transitive_closure": False,
                    },
                }
            )
    classes.sort(key=lambda item: item["class_id"])
    if len(classes) != 6 or assignments != 7776:
        raise AssertionError("frontier counts")
    return {
        "descriptor": descriptor,
        "left_forms": left_forms,
        "right_forms": right_forms,
        "left_counts": left_counts,
        "right_counts": right_counts,
        "left_hist": left_hist,
        "right_hist": right_hist,
        "pairs": pairs,
        "refinements": refinements,
        "correction_table": correction_table,
        "injectivity": injectivity,
        "projection": projection_replay(),
        "classes": classes,
        "assignments": assignments,
    }


def static_source_gate(source: Path) -> None:
    tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    if any("corrected_node7_parent_frontier_compression" in item for item in imported):
        raise AssertionError("self import")
    if any("janus_c049_1_b1_" in item or "janus_c049_1_b2_" in item for item in imported):
        raise AssertionError("theorem-core import")

    def labels(node: ast.AST) -> set[str]:
        names = {item.id for item in ast.walk(node) if isinstance(item, ast.Name)}
        output = set()
        if names & {"left_forms", "left_entries"}:
            output.add("LEFT")
        if names & {"right_forms", "right_entries"}:
            output.add("RIGHT")
        return output

    class Scan(ast.NodeVisitor):
        def __init__(self) -> None:
            self.stack: list[set[str]] = []

        def visit_For(self, node: ast.For) -> None:
            current = labels(node.iter)
            active = set().union(*self.stack, current) if self.stack else set(current)
            if active == {"LEFT", "RIGHT"}:
                raise AssertionError("child Cartesian loop")
            self.stack.append(current)
            for item in node.body + node.orelse:
                self.visit(item)
            self.stack.pop()

        def visit_Call(self, node: ast.Call) -> None:
            name = node.func.id if isinstance(node.func, ast.Name) else (
                node.func.attr if isinstance(node.func, ast.Attribute) else ""
            )
            if name == "product":
                found = set().union(*(labels(argument) for argument in node.args)) if node.args else set()
                if found == {"LEFT", "RIGHT"}:
                    raise AssertionError("child Cartesian product")
            self.generic_visit(node)

    Scan().visit(tree)
    print("STATIC_NO_CHILD_CARTESIAN_OR_ACTUAL_FINE_REFINEMENT_ENUMERATION = PASS")


def verify(manifest_path: Path, summary_path: Path, artifact_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if artifact.get("schema") != SCHEMA:
        raise AssertionError("schema")
    unsigned = dict(artifact)
    claimed = unsigned.pop("semantic_digest", None)
    if claimed != sha(unsigned):
        raise AssertionError("artifact semantic digest")
    expected = independent_expected(manifest, summary)

    source = artifact["source"]
    if source != {
        "parent_pr": 111,
        "parent_exact_head": PARENT_HEAD,
        "summary_semantic_digest": SUMMARY_DIGEST,
        "manifest_digest": MANIFEST_DIGEST,
        "transcript_root_digest": TRANSCRIPT_ROOT,
        "node6_execution_digest": NODE6_EXECUTION,
        "node6_output_receipt_digest": NODE6_RECEIPT,
        "node6_entries_digest": NODE6_ENTRIES,
        "node7_descriptor_digest": sha(expected["descriptor"]),
    }:
        raise AssertionError("source block")

    domain = artifact["corrected_path_domain"]
    if domain != {
        "ordinary_join_steps": [[1, 0], [0, 1]],
        "ordinary_join_diagonal_allowed": False,
        "quotient_projection_steps": [[1, 0], [0, 1]],
        "quotient_projection_diagonal_allowed": False,
        "extension_preorder_steps": [[1, 0], [0, 1], [1, 1]],
        "extension_preorder_diagonal_preserved": True,
        "legacy_delannoy_frontier_consumed": False,
    }:
        raise AssertionError("path domains")

    child = artifact["child_normal_forms"]
    if child["left_entry_count"] != 432 or child["right_entry_count"] != 36:
        raise AssertionError("entry counts")
    if child["left_skeleton_multiplicities"] != {"LEFT_A": 216, "LEFT_B": 216}:
        raise AssertionError("left skeletons")
    if child["right_skeleton_multiplicities"] != {"RIGHT_R": 36}:
        raise AssertionError("right skeleton")
    if child["left_trajectory_set_digest"] != sha(
        sorted((item["trajectory"] for item in expected["left_forms"]), key=packed)
    ):
        raise AssertionError("left digest")
    if child["right_trajectory_set_digest"] != sha(
        sorted((item["trajectory"] for item in expected["right_forms"]), key=packed)
    ):
        raise AssertionError("right digest")
    if child["left_length_histogram"] != {
        str(key): value for key, value in sorted(expected["left_hist"].items())
    }:
        raise AssertionError("left histogram")
    if child["right_length_histogram"] != {
        str(key): value for key, value in sorted(expected["right_hist"].items())
    }:
        raise AssertionError("right histogram")
    if child["binary_typical_run_patterns"] != [list(item) for item in PATTERNS]:
        raise AssertionError("pattern catalog")

    geometry = artifact["node7_geometry"]
    if geometry["right_basis_in_parent_coordinates"] != [3]:
        raise AssertionError("transport")
    if geometry["join_correction_table"] != expected["correction_table"]:
        raise AssertionError("correction table")
    if geometry["joined_symbol_injectivity"] != expected["injectivity"]:
        raise AssertionError("injectivity")
    if geometry["left_expand_identity"] is not True or geometry["shrink_identity"] is not True:
        raise AssertionError("identity geometry")

    if artifact["projection_completeness"] != expected["projection"]:
        raise AssertionError("projection audit")

    frontier = artifact["quotient_frontier"]
    if frontier["child_pair_count"] != expected["pairs"]:
        raise AssertionError("pair count")
    if frontier["ordinary_hv_refinement_count"] != expected["refinements"]:
        raise AssertionError("refinement count")
    if frontier["class_count"] != 6 or frontier["classes"] != expected["classes"]:
        raise AssertionError("class catalog")
    if frontier["class_catalog_digest"] != sha(expected["classes"]):
        raise AssertionError("class digest")
    if frontier["successful_generator_frontier_complete"] is not True:
        raise AssertionError("frontier incomplete")
    failed = frontier["failed_refinement_partition"]
    if (
        failed["every_refinement_projected"] is not True
        or failed["successful_if_compact_width_at_most_k"] is not True
        or failed["failed_if_compact_width_exceeds_k"] is not True
        or failed["failed_records_individually_materialized"] is not False
    ):
        raise AssertionError("failure partition")

    ledger = artifact["work_ledger"]
    if ledger != {
        "left_entries_read": 432,
        "right_entries_read": 36,
        "cartesian_child_pairs_materialized": 0,
        "actual_fine_refinements_materialized": 0,
        "abstract_run_length_profiles_replayed": 486,
        "abstract_fine_hv_paths_replayed": 47862,
        "quotient_paths_enumerated": 6,
        "local_direct_witness_assignments_tested": 7776,
        "naive_hv_work_avoided": 1531584,
    }:
        raise AssertionError("work ledger")
    if any(artifact["legacy_inputs"].values()):
        raise AssertionError("legacy input consumed")
    if artifact["invariant_vector"] != {
        f"CN7F-INV-{index:02d}": "PASS" for index in range(1, 15)
    }:
        raise AssertionError("invariants")

    for mode in ("reversed", "seeded-shuffle"):
        replay = independent_expected(manifest, summary, mode)
        if replay["classes"] != expected["classes"]:
            raise AssertionError("class order dependence")
        if sha(sorted((item["trajectory"] for item in replay["left_forms"]), key=packed)) != child["left_trajectory_set_digest"]:
            raise AssertionError("left order dependence")
        if sha(sorted((item["trajectory"] for item in replay["right_forms"]), key=packed)) != child["right_trajectory_set_digest"]:
            raise AssertionError("right order dependence")

    strict = artifact["strict_boundary"]
    if strict != {
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
        "current_global_terminal": "OPEN_TRAJECTORY_ENGINE_INCOMPLETE",
        "p_vs_np": "OPEN",
    }:
        raise AssertionError("strict boundary")
    if artifact["result"] != "CORRECTED_NODE7_PARENT_FRONTIER_COMPRESSED_TO_SIX_CLASSES":
        raise AssertionError("result")
    if artifact["next_gate"] != "C049.1_B4.6.3_CORRECTED_NODE7_SIX_GENERATOR_UP_K_HARDENING":
        raise AssertionError("next gate")

    print("JANUS_C049_1_B4_6_3_CORRECTED_NODE7_FRONTIER_COMPRESSION_VERIFIER = PASS")
    print("INVARIANTS = 14/14")
    print("QUOTIENT_CLASSES = 6")
    print("LOCAL_DIRECT_WITNESS_ASSIGNMENTS = 7776")
    print("ABSTRACT_FINE_HV_PATHS_REPLAYED = 47862")
    print("NEXT_GATE = C049.1_B4.6.3_CORRECTED_NODE7_SIX_GENERATOR_UP_K_HARDENING")
    print("CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE")


def tamper_test(manifest: Path, summary: Path, artifact: Path) -> None:
    original = json.loads(artifact.read_text(encoding="utf-8"))
    attacks = []

    def add(name: str, mutate) -> None:
        value = copy.deepcopy(original)
        mutate(value)
        unsigned = dict(value)
        unsigned.pop("semantic_digest", None)
        value["semantic_digest"] = sha(unsigned)
        attacks.append((name, value))

    add("SOURCE_HEAD", lambda value: value["source"].__setitem__("parent_exact_head", "0" * 40))
    add("LEFT_COUNT", lambda value: value["child_normal_forms"].__setitem__("left_entry_count", 431))
    add("ORDINARY_DIAGONAL", lambda value: value["corrected_path_domain"].__setitem__("ordinary_join_diagonal_allowed", True))
    add("DELETE_CLASS", lambda value: value["quotient_frontier"]["classes"].pop())
    add("DIAGONAL_QUOTIENT", lambda value: value["quotient_frontier"]["classes"][0]["quotient_path_steps"].__setitem__(0, [1, 1]))
    add("JOIN_CORRECTION", lambda value: value["node7_geometry"]["join_correction_table"][0].__setitem__("correction", 1))
    add("ZERO_ENVELOPE", lambda value: value["quotient_frontier"]["classes"][0]["zero_envelope"][0].__setitem__("value", 1))
    add("PROJECTION_COUNT", lambda value: value["projection_completeness"].__setitem__("fine_hv_paths_replayed", 23930))

    def closure_only(value: dict) -> None:
        block = value["quotient_frontier"]["classes"][0]["direct_coverage_constructor"]
        block["uses_direct_extension_preorder_witness"] = False
        block["uses_transitive_closure"] = True

    add("CLOSURE_ONLY", closure_only)
    add("LEGACY_INPUT", lambda value: value["legacy_inputs"].__setitem__("legacy_thirteen_class_count_promoted", True))
    add("UP_K_OVERCLAIM", lambda value: value["strict_boundary"].__setitem__("corrected_node7_parent_up_k_complete", True))
    add("ROOT_OVERCLAIM", lambda value: value["strict_boundary"].__setitem__("root_full_set_computed", True))

    root = Path("/tmp/c049-corrected-node7-frontier-tampers")
    root.mkdir(parents=True, exist_ok=True)
    rejected = 0
    for name, value in attacks:
        path = root / f"{name}.json"
        path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
        try:
            verify(manifest, summary, path)
        except Exception:
            rejected += 1
        else:
            raise AssertionError(f"digest-repaired tamper accepted: {name}")
    if rejected != 12:
        raise AssertionError("tamper rejection count")
    print("DIGEST_REPAIRED_TAMPERS_REJECTED = 12/12")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("summary", type=Path)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--producer-source", type=Path)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    if args.producer_source is not None:
        static_source_gate(args.producer_source)
    verify(args.manifest, args.summary, args.artifact)
    if args.tamper_self_test:
        tamper_test(args.manifest, args.summary, args.artifact)


if __name__ == "__main__":
    main()
