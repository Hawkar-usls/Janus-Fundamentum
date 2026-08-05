#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import itertools
import json
import random
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA = "C049.1-B4.6.3-NODE7-PARENT-FRONTIER-STRUCTURAL-COMPRESSION-v1"
EXPECTED_MANIFEST = "2ca2b0bc7566fb2e24f62e9df44499044843fa08388d8573fb74221dfab80512"
EXPECTED_TRANSCRIPT = "eb904e833b53cf5626af1eb28493f479f5f54f2066a8b5427cb7e3eb47f515d8"
EXPECTED_NODE6_EXECUTION = "c9e9f72e4715f4f04aafb2c1b5b1288b48478998826332c5ab61da949586c04a"
EXPECTED_NODE6_RECEIPT = "88170c8f5ba5519908e88f1dba21bb2247218c0713dc6830e562a879edd3aad9"
PATTERNS = ((0,), (0, 1), (0, 1, 0), (1,), (1, 0), (1, 0, 1))
CODES = {
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
    for raw in rows:
        x = int(raw)
        if x < 0 or x >= 1 << ambient_dim:
            raise AssertionError("vector range")
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


def span_vectors(space: Sequence[int]) -> set[int]:
    out = {0}
    for row in space:
        out |= {value ^ int(row) for value in tuple(out)}
    return out


def subspace_sum(
    left: Sequence[int], right: Sequence[int], ambient_dim: int
) -> tuple[int, ...]:
    return xor_basis((*left, *right), ambient_dim)


def subspace_intersection(
    left: Sequence[int], right: Sequence[int], ambient_dim: int
) -> tuple[int, ...]:
    return xor_basis(
        span_vectors(left) & span_vectors(right), ambient_dim
    )


def coordinate_vector(vector: int, basis: Sequence[int]) -> int:
    for mask in range(1 << len(basis)):
        value = 0
        for index, row in enumerate(basis):
            if (mask >> index) & 1:
                value ^= int(row)
        if value == int(vector):
            return mask
    raise AssertionError("coordinate failure")


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
        (coordinate_vector(row, basis) for row in space), len(basis)
    )


def geometry(
    item: dict, ambient_dim: int
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    return xor_basis(item["left"], ambient_dim), xor_basis(
        item["right"], ambient_dim
    )


def geometry_payload(value: tuple) -> dict:
    return {"left": list(value[0]), "right": list(value[1])}


def canonical_trajectory(raw: Sequence[dict], ambient_dim: int) -> list[dict]:
    return [
        {
            "left": list(xor_basis(item["left"], ambient_dim)),
            "right": list(xor_basis(item["right"], ambient_dim)),
            "value": int(item["value"]),
        }
        for item in raw
    ]


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


def split_runs(raw: Sequence[dict], ambient_dim: int) -> tuple:
    skeleton = []
    values = []
    for item in raw:
        geom = geometry(item, ambient_dim)
        value = int(item["value"])
        if value not in (0, 1):
            raise AssertionError("nonbinary child")
        if not skeleton or skeleton[-1] != geom:
            skeleton.append(geom)
            values.append([value])
        else:
            values[-1].append(value)
    patterns = tuple(tuple(value) for value in values)
    if any(pattern not in CODES for pattern in patterns):
        raise AssertionError("run catalog violation")
    return tuple(skeleton), patterns


def identify_left_skeleton(skeleton: tuple) -> str:
    full = (2, 1)
    table = {
        (((), full), ((1,), (2,)), (full, ())): "LEFT_A",
        (((), full), ((2,), (1,)), (full, ())): "LEFT_B",
        (((), full), (full, ())): "LEFT_C",
    }
    if skeleton not in table:
        raise AssertionError("left skeleton")
    return table[skeleton]


def identify_right_skeleton(skeleton: tuple) -> str:
    if skeleton != (((), (3,)), ((3,), ())):
        raise AssertionError("right skeleton")
    return "RIGHT_R"


def normal_forms(
    entries: Sequence[dict],
    side: str,
    mode: str,
    child_basis: Sequence[int] | None,
    parent_basis: Sequence[int],
    ambient_dim: int,
) -> list[dict]:
    indexed = list(enumerate(entries))
    if mode == "reversed":
        indexed.reverse()
    elif mode == "seeded-shuffle":
        random.Random(0xC049107).shuffle(indexed)
    elif mode != "original":
        raise AssertionError("mode")
    out = []
    for source_index, entry in indexed:
        raw = copy.deepcopy(entry["trajectory"])
        if child_basis is not None:
            raw = transport_trajectory(
                raw, child_basis, parent_basis, ambient_dim
            )
        raw = canonical_trajectory(raw, len(parent_basis))
        skeleton, patterns = split_runs(raw, len(parent_basis))
        skeleton_id = (
            identify_left_skeleton(skeleton)
            if side == "LEFT"
            else identify_right_skeleton(skeleton)
        )
        out.append(
            {
                "side": side,
                "skeleton_id": skeleton_id,
                "skeleton": [
                    geometry_payload(item) for item in skeleton
                ],
                "run_pattern_codes": [CODES[item] for item in patterns],
                "trajectory_digest": digest(raw),
                "source_entry_index": source_index,
                "trajectory": raw,
            }
        )
    out.sort(
        key=lambda item: canonical_json(
            [
                item["skeleton_id"],
                item["run_pattern_codes"],
                item["trajectory_digest"],
                item["source_entry_index"],
            ]
        )
    )
    return out


def quotient_paths(m: int, n: int) -> list[list[list[int]]]:
    out = []

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
    return sorted(out, key=canonical_json)


def joined_symbol(left: tuple, right: tuple, ambient_dim: int) -> tuple:
    return (
        subspace_sum(left[0], right[0], ambient_dim),
        subspace_sum(left[1], right[1], ambient_dim),
    )


def join_correction(
    left: tuple, right: tuple, initial_dim: int, ambient_dim: int
) -> int:
    return initial_dim - len(
        subspace_intersection(
            subspace_sum(left[0], left[1], ambient_dim),
            subspace_sum(right[0], right[1], ambient_dim),
            ambient_dim,
        )
    )


def direct_witness_is_valid(
    envelope: Sequence[dict],
    assignment: Sequence[tuple[int, ...]],
    ambient_dim: int,
) -> bool:
    upper = []
    starts = []
    for stat, pattern in zip(envelope, assignment):
        starts.append(len(upper))
        for value in pattern:
            item = copy.deepcopy(stat)
            item["value"] = value
            upper.append(item)
    path = [[0, 0]]
    for index, pattern in enumerate(assignment):
        for upper_index in range(
            starts[index] + 1, starts[index] + len(pattern)
        ):
            path.append([index, upper_index])
        if index + 1 < len(envelope):
            path.append([index + 1, starts[index + 1]])
    if path[-1] != [len(envelope) - 1, len(upper) - 1]:
        return False
    for lower_index, upper_index in path:
        if geometry(
            envelope[lower_index], ambient_dim
        ) != geometry(upper[upper_index], ambient_dim):
            return False
        if envelope[lower_index]["value"] > upper[upper_index]["value"]:
            return False
    return all(
        (second[0] - first[0], second[1] - first[1])
        in ((1, 0), (0, 1), (1, 1))
        for first, second in zip(path, path[1:])
    )


def independently_replay(manifest: dict, mode: str = "original") -> dict:
    if manifest["manifest_digest"] != EXPECTED_MANIFEST:
        raise AssertionError("manifest binding")
    if manifest["chunking"]["transcript_root_digest"] != EXPECTED_TRANSCRIPT:
        raise AssertionError("transcript binding")
    node6 = next(
        node for node in manifest["node_results"] if node["node_id"] == 6
    )
    if node6["node_execution_digest"] != EXPECTED_NODE6_EXECUTION:
        raise AssertionError("node6 execution")
    if (
        node6["output_receipt"]["receipt_digest"]
        != EXPECTED_NODE6_RECEIPT
    ):
        raise AssertionError("node6 receipt")
    descriptor = next(
        item
        for item in manifest["topology"]["internal_nodes"]
        if item["node_id"] == 7
    )
    right_leaf = manifest["leaf_full_sets"][2]
    parent = tuple(node6["parent_boundary"])
    right = tuple(right_leaf["boundary_rref_ambient"])
    ambient_dim = int(manifest["scaffold_case"]["d"])
    if (
        parent != (4, 2)
        or right != (6,)
        or [coordinate_vector(value, parent) for value in right] != [3]
    ):
        raise AssertionError("transport")

    left_forms = normal_forms(
        node6["node_up_k"]["entries"],
        "LEFT",
        mode,
        None,
        parent,
        ambient_dim,
    )
    right_forms = normal_forms(
        right_leaf["full_set"]["entries"],
        "RIGHT",
        mode,
        right,
        parent,
        ambient_dim,
    )
    if len(left_forms) != 468 or len(right_forms) != 36:
        raise AssertionError("counts")
    left_counts = {
        key: sum(item["skeleton_id"] == key for item in left_forms)
        for key in ("LEFT_A", "LEFT_B", "LEFT_C")
    }
    if left_counts != {"LEFT_A": 216, "LEFT_B": 216, "LEFT_C": 36}:
        raise AssertionError("left multiplicity")
    if {item["skeleton_id"] for item in right_forms} != {"RIGHT_R"}:
        raise AssertionError("right multiplicity")

    left_skeletons = {
        key: tuple(
            (tuple(item["left"]), tuple(item["right"]))
            for item in next(
                form
                for form in left_forms
                if form["skeleton_id"] == key
            )["skeleton"]
        )
        for key in left_counts
    }
    right_skeleton = tuple(
        (tuple(item["left"]), tuple(item["right"]))
        for item in right_forms[0]["skeleton"]
    )
    initial_dim = len(
        subspace_intersection(
            left_skeletons["LEFT_A"][0][1],
            right_skeleton[0][1],
            2,
        )
    )
    zero_left = {
        key: next(
            item
            for item in left_forms
            if item["skeleton_id"] == key
            and item["run_pattern_codes"]
            == ["0"] * len(left_skeletons[key])
        )
        for key in left_skeletons
    }
    zero_right = next(
        item
        for item in right_forms
        if item["run_pattern_codes"] == ["0", "0"]
    )

    classes = []
    correction_table = []
    injectivity = []
    assignment_tests = 0
    for key in ("LEFT_A", "LEFT_B", "LEFT_C"):
        seen = set()
        for i, left_geom in enumerate(left_skeletons[key]):
            for j, right_geom in enumerate(right_skeleton):
                correction = join_correction(
                    left_geom, right_geom, initial_dim, 2
                )
                symbol = joined_symbol(left_geom, right_geom, 2)
                if correction != 0:
                    raise AssertionError("correction")
                encoded = canonical_json(geometry_payload(symbol))
                if encoded in seen:
                    raise AssertionError("injectivity")
                seen.add(encoded)
                correction_table.append(
                    {
                        "left_skeleton_id": key,
                        "cell": [i, j],
                        "correction": correction,
                        "joined_symbol": geometry_payload(symbol),
                    }
                )
        injectivity.append(
            {
                "left_skeleton_id": key,
                "grid_cell_count": len(left_skeletons[key])
                * len(right_skeleton),
                "distinct_joined_symbol_count": len(seen),
                "injective": True,
            }
        )
        for path_index, path in enumerate(
            quotient_paths(
                len(left_skeletons[key]), len(right_skeleton)
            )
        ):
            envelope = [
                {
                    "left": list(
                        joined_symbol(
                            left_skeletons[key][i], right_skeleton[j], 2
                        )[0]
                    ),
                    "right": list(
                        joined_symbol(
                            left_skeletons[key][i], right_skeleton[j], 2
                        )[1]
                    ),
                    "value": 0,
                }
                for i, j in path
            ]
            case_count = 0
            for assignment in itertools.product(
                PATTERNS, repeat=len(envelope)
            ):
                if not direct_witness_is_valid(envelope, assignment, 2):
                    raise AssertionError("direct witness")
                case_count += 1
            assignment_tests += case_count
            classes.append(
                {
                    "class_id": f"{key}-Q{path_index:02d}",
                    "left_skeleton_id": key,
                    "right_skeleton_id": "RIGHT_R",
                    "quotient_path": path,
                    "quotient_path_length": len(path),
                    "joined_skeleton": [
                        geometry_payload(geometry(item, 2))
                        for item in envelope
                    ],
                    "zero_envelope": envelope,
                    "zero_envelope_digest": digest(envelope),
                    "reachability_witness": {
                        "left_zero_entry_index": zero_left[key][
                            "source_entry_index"
                        ],
                        "right_zero_entry_index": zero_right[
                            "source_entry_index"
                        ],
                        "left_zero_trajectory_digest": zero_left[key][
                            "trajectory_digest"
                        ],
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
                            CODES.values()
                        ),
                        "exhaustive_local_assignments_tested": case_count,
                        "uses_direct_preorder_witness": True,
                        "uses_transitive_closure": False,
                    },
                }
            )
    classes.sort(key=lambda item: item["class_id"])
    return {
        "left_forms": left_forms,
        "right_forms": right_forms,
        "classes": classes,
        "correction_table": correction_table,
        "injectivity": injectivity,
        "assignment_tests": assignment_tests,
        "descriptor": descriptor,
    }


def verify_source_no_pair_enumeration(source_path: Path) -> None:
    tree = ast.parse(
        source_path.read_text(encoding="utf-8"), filename=str(source_path)
    )

    def inventory_labels(node: ast.AST) -> set[str]:
        names = {
            item.id for item in ast.walk(node) if isinstance(item, ast.Name)
        }
        labels = set()
        if names & {"left_forms", "left_entries"}:
            labels.add("LEFT")
        if names & {"right_forms", "right_entries"}:
            labels.add("RIGHT")
        return labels

    class Scan(ast.NodeVisitor):
        def __init__(self) -> None:
            self.active: list[set[str]] = []

        def visit_For(self, node: ast.For) -> None:
            labels = inventory_labels(node.iter)
            combined = (
                set().union(*self.active, labels)
                if self.active
                else set(labels)
            )
            if combined == {"LEFT", "RIGHT"}:
                raise AssertionError(
                    "producer statically nests left/right child inventory iteration"
                )
            self.active.append(labels)
            for child in node.body:
                self.visit(child)
            for child in node.orelse:
                self.visit(child)
            self.active.pop()

        def inspect_comprehension(
            self,
            generators: Sequence[ast.comprehension],
            payloads: Sequence[ast.AST],
        ) -> None:
            labels = set()
            for generator in generators:
                labels |= inventory_labels(generator.iter)
            if labels == {"LEFT", "RIGHT"}:
                raise AssertionError(
                    "producer materializes a left/right Cartesian comprehension"
                )
            for payload in payloads:
                self.visit(payload)

        def visit_ListComp(self, node: ast.ListComp) -> None:
            self.inspect_comprehension(node.generators, [node.elt])

        def visit_SetComp(self, node: ast.SetComp) -> None:
            self.inspect_comprehension(node.generators, [node.elt])

        def visit_DictComp(self, node: ast.DictComp) -> None:
            self.inspect_comprehension(
                node.generators, [node.key, node.value]
            )

        def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
            self.inspect_comprehension(node.generators, [node.elt])

        def visit_Call(self, node: ast.Call) -> None:
            name = None
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name == "product":
                labels = (
                    set().union(
                        *(inventory_labels(argument) for argument in node.args)
                    )
                    if node.args
                    else set()
                )
                if labels == {"LEFT", "RIGHT"}:
                    raise AssertionError(
                        "producer passes both child inventories to Cartesian product"
                    )
            self.generic_visit(node)

    Scan().visit(tree)
    print("STATIC_NO_CHILD_CARTESIAN_ENUMERATION = PASS")


def verify(manifest_path: Path, artifact_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if artifact.get("schema") != SCHEMA:
        raise AssertionError("schema")
    unsigned = {
        key: value
        for key, value in artifact.items()
        if key != "semantic_digest"
    }
    if digest(unsigned) != artifact.get("semantic_digest"):
        raise AssertionError("semantic digest")
    expected = independently_replay(manifest)
    if artifact["source"] != {
        "manifest_digest": EXPECTED_MANIFEST,
        "transcript_root_digest": EXPECTED_TRANSCRIPT,
        "node6_execution_digest": EXPECTED_NODE6_EXECUTION,
        "node6_output_receipt_digest": EXPECTED_NODE6_RECEIPT,
        "node7_descriptor_digest": digest(expected["descriptor"]),
    }:
        raise AssertionError("source block")

    child = artifact["child_normal_forms"]
    if child["run_pattern_catalog"] != [list(item) for item in PATTERNS]:
        raise AssertionError("run catalog")
    if child["run_pattern_codes"] != list(CODES.values()):
        raise AssertionError("run codes")
    if child["left_forms"] != expected["left_forms"]:
        raise AssertionError("left normal forms")
    if child["right_forms"] != expected["right_forms"]:
        raise AssertionError("right normal forms")
    if child["left_normal_forms_digest"] != digest(
        expected["left_forms"]
    ):
        raise AssertionError("left normal digest")
    if child["right_normal_forms_digest"] != digest(
        expected["right_forms"]
    ):
        raise AssertionError("right normal digest")
    if child["left_trajectory_set_digest"] != digest(
        sorted(
            (item["trajectory"] for item in expected["left_forms"]),
            key=canonical_json,
        )
    ):
        raise AssertionError("left set digest")
    if child["right_trajectory_set_digest"] != digest(
        sorted(
            (item["trajectory"] for item in expected["right_forms"]),
            key=canonical_json,
        )
    ):
        raise AssertionError("right set digest")

    geometry_block = artifact["node7_geometry"]
    if geometry_block["right_basis_in_parent_coordinates"] != [3]:
        raise AssertionError("transport geometry")
    if not geometry_block["left_expand_identity"]:
        raise AssertionError("left expansion")
    if not geometry_block["shrink_identity"]:
        raise AssertionError("shrink identity")
    if (
        geometry_block["join_correction_table"]
        != expected["correction_table"]
    ):
        raise AssertionError("correction certificate")
    if (
        geometry_block["joined_symbol_injectivity"]
        != expected["injectivity"]
    ):
        raise AssertionError("injectivity certificate")

    frontier = artifact["quotient_frontier"]
    if frontier["naive_child_pair_count"] != 16848:
        raise AssertionError("pair count")
    if frontier["naive_refinement_count"] != 9744432:
        raise AssertionError("refinement count")
    if frontier["class_count"] != 13:
        raise AssertionError("class count")
    if frontier["classes"] != expected["classes"]:
        raise AssertionError("class catalog")
    if frontier["class_catalog_digest"] != digest(expected["classes"]):
        raise AssertionError("class digest")
    theorem = frontier["coverage_theorem"]
    if theorem["closure_only_edges_used"] is not False:
        raise AssertionError("closure-only witness")
    if (
        theorem["zero_envelope_directly_precedes_every_successful_output"]
        is not True
    ):
        raise AssertionError("direct coverage")

    if artifact["work_ledger"] != {
        "left_entries_read": 468,
        "right_entries_read": 36,
        "cartesian_child_pairs_materialized": 0,
        "fine_lattice_paths_enumerated": 0,
        "quotient_paths_enumerated": 13,
        "local_direct_witness_assignments_tested": expected[
            "assignment_tests"
        ],
        "naive_work_avoided": 9744432,
    }:
        raise AssertionError("work ledger")

    for mode in ("reversed", "seeded-shuffle"):
        replay = independently_replay(manifest, mode)
        if replay["left_forms"] != expected["left_forms"]:
            raise AssertionError("left input-order invariance")
        if replay["right_forms"] != expected["right_forms"]:
            raise AssertionError("right input-order invariance")
        if replay["classes"] != expected["classes"]:
            raise AssertionError("class input-order invariance")

    invariant_vector = artifact["invariant_vector"]
    if len(invariant_vector) != 10:
        raise AssertionError("invariant count")
    if set(invariant_vector.values()) != {"PASS"}:
        raise AssertionError("invariant vector")
    if artifact.get("admit") is not True:
        raise AssertionError("admission")

    strict = artifact["strict_boundary"]
    if not strict["node7_parent_generator_frontier_complete"]:
        raise AssertionError("frontier completeness")
    if not strict["node7_parent_refinement_complete"]:
        raise AssertionError("refinement completeness")
    if strict["node7_parent_up_k_complete"]:
        raise AssertionError("up_k overclaim")
    if strict["negative_root_reached"]:
        raise AssertionError("root overclaim")
    if strict["terminal_completeness_proved"]:
        raise AssertionError("terminal overclaim")
    if strict["found_layout_enabled"]:
        raise AssertionError("found-layout overclaim")
    if strict["no_layout_at_cap_enabled"]:
        raise AssertionError("no-layout overclaim")

    print(
        "JANUS_C049_1_B4_6_3_NODE7_FRONTIER_COMPRESSION_VERIFIER = PASS"
    )
    print("INVARIANTS = 10/10")
    print("QUOTIENT_CLASSES = 13")
    print(
        "LOCAL_DIRECT_WITNESS_ASSIGNMENTS =",
        expected["assignment_tests"],
    )
    print("ADMIT_NODE7_FRONTIER_COMPRESSION = TRUE")


def tamper_self_test(
    manifest_path: Path, artifact_path: Path
) -> None:
    original = json.loads(artifact_path.read_text(encoding="utf-8"))
    attacks = []

    def add(name: str, mutate) -> None:
        value = copy.deepcopy(original)
        mutate(value)
        value["semantic_digest"] = digest(
            {
                key: item
                for key, item in value.items()
                if key != "semantic_digest"
            }
        )
        attacks.append((name, value))

    add(
        "RUN_PATTERN",
        lambda value: value["child_normal_forms"]["left_forms"][0][
            "run_pattern_codes"
        ].__setitem__(0, "1"),
    )
    add(
        "TRANSPORT",
        lambda value: value["node7_geometry"].__setitem__(
            "right_basis_in_parent_coordinates", [1]
        ),
    )
    add(
        "JOIN_CORRECTION",
        lambda value: value["node7_geometry"]["join_correction_table"][
            0
        ].__setitem__("correction", 1),
    )
    add(
        "DELETE_CLASS",
        lambda value: value["quotient_frontier"]["classes"].pop(),
    )
    add(
        "ADD_CLASS",
        lambda value: value["quotient_frontier"]["classes"].append(
            copy.deepcopy(value["quotient_frontier"]["classes"][0])
        ),
    )
    add(
        "ZERO_TO_ONE",
        lambda value: value["quotient_frontier"]["classes"][0][
            "zero_envelope"
        ][0].__setitem__("value", 1),
    )

    def closure_only(value: dict) -> None:
        constructor = value["quotient_frontier"]["classes"][0][
            "direct_coverage_constructor"
        ]
        constructor["uses_direct_preorder_witness"] = False
        constructor["uses_transitive_closure"] = True

    add("CLOSURE_ONLY", closure_only)
    add(
        "ORDER_DEPENDENT",
        lambda value: value["child_normal_forms"]["left_forms"].reverse(),
    )

    root = Path("/tmp/node7-frontier-tamper")
    root.mkdir(exist_ok=True)
    rejected = 0
    for name, value in attacks:
        path = root / f"{name}.json"
        path.write_text(
            json.dumps(value, sort_keys=True), encoding="utf-8"
        )
        try:
            verify(manifest_path, path)
        except Exception:
            rejected += 1
        else:
            raise AssertionError(f"tamper accepted: {name}")
    if rejected != 8:
        raise AssertionError("tamper count")
    print("TAMPER_ATTACKS_REJECTED = 8/8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--tamper-self-test", action="store_true")
    parser.add_argument("--producer-source", type=Path)
    args = parser.parse_args()
    if args.producer_source is not None:
        verify_source_no_pair_enumeration(args.producer_source)
    verify(args.manifest, args.artifact)
    if args.tamper_self_test:
        tamper_self_test(args.manifest, args.artifact)


if __name__ == "__main__":
    main()
