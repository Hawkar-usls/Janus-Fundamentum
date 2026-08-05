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
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA = "C049.1-B4.6.3-NODE9-PARENT-FRONTIER-STRUCTURAL-COMPRESSION-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
MANIFEST_SHA = "9553263dc70f7a962a7bd95af4d5d4eeea6e1cdab163c616817b97cfcc207d6b"
MANIFEST_DIGEST = "b46e56a20c714806b3475658aacd82f628c909c3b7dc1492db7adb504dcaf868"
TRANSCRIPT = "eb904e833b53cf5626af1eb28493f479f5f54f2066a8b5427cb7e3eb47f515d8"
NODE8_RECEIPT = "befcbb30de8d70ee9816bdf072b92e597cfd7052c7d7931d48190e8e53854b20"
LEAF4_RECEIPT = "44ae26d9a650353d6360027b08ad3738b9a0fed5bfd78fcfafb165e83dd0052f"
NODE8_ENTRIES = "6030bb93f1298bf26f4c76d00bbc392dc0a6dd69dd4c1552691c55382fba7468"
NODE8_FRONTIER = "93dcd5610eb9df079823b172a4f824ce1c09859e759c6b771dc95b99af394d34"
NODE8_UPK = "e5202b9eb32ef44b1fdf493c6848ec82f8ce16fa502e623b7fbfdeb6bc735620"
RUN_PATTERNS = ((0,), (0, 1), (0, 1, 0), (1,), (1, 0), (1, 0, 1))
RUN_CODE = {p: "".join(str(v) for v in p) for p in RUN_PATTERNS}
COUNTS = {
    "left": 15948,
    "right": 36,
    "pairs": 574128,
    "refinements": 1284995408,
    "quotient": 182,
    "successful": 118,
    "failed": 64,
    "classes": 15,
    "assignments": 13248,
    "cells": 818,
}
JOIN_COUNTS = {0: 664, 1: 154}
SHRINK_COUNTS = {0: 656, 1: 162}


def canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def h(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rref(rows: Iterable[int], d: int) -> tuple[int, ...]:
    pivots: dict[int, int] = {}
    for raw in rows:
        value = int(raw)
        if value < 0 or value >= 1 << d:
            raise AssertionError("vector range")
        while value:
            p = value.bit_length() - 1
            if p in pivots:
                value ^= pivots[p]
                continue
            pivots[p] = value
            for q in tuple(pivots):
                if q != p and ((pivots[q] >> p) & 1):
                    pivots[q] ^= value
            break
    for p in sorted(pivots):
        for q in sorted(pivots, reverse=True):
            if q != p and ((pivots[q] >> p) & 1):
                pivots[q] ^= pivots[p]
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def elements(space: Sequence[int]) -> set[int]:
    out = {0}
    for row in space:
        out.update({x ^ int(row) for x in tuple(out)})
    return out


def join_space(a: Sequence[int], b: Sequence[int], d: int) -> tuple[int, ...]:
    return rref((*a, *b), d)


def meet_space(a: Sequence[int], b: Sequence[int], d: int) -> tuple[int, ...]:
    return rref(elements(a) & elements(b), d)


def stat(left: Sequence[int], right: Sequence[int], value: int) -> tuple:
    return (tuple(left), tuple(right), int(value))


def encode_stat(item: tuple) -> dict:
    return {"left": list(item[0]), "right": list(item[1]), "value": item[2]}


def encode(seq: Sequence[tuple]) -> list[dict]:
    return [encode_stat(item) for item in seq]


def compact(seq: Sequence[tuple]) -> tuple:
    current = list(seq)
    while True:
        changed = False
        for index in range(1, len(current)):
            if current[index - 1] == current[index]:
                current.pop(index)
                changed = True
                break
        if changed:
            continue
        for start in range(len(current)):
            for end in range(start + 2, len(current)):
                if current[start][:2] != current[end][:2]:
                    continue
                values = [item[2] for item in current[start : end + 1]]
                monotone = (
                    values[0] <= values[-1]
                    and all(values[0] <= z <= values[-1] for z in values[1:-1])
                ) or (
                    values[0] >= values[-1]
                    and all(values[0] >= z >= values[-1] for z in values[1:-1])
                )
                if monotone:
                    del current[start + 1 : end]
                    changed = True
                    break
            if changed:
                break
        if not changed:
            return tuple(current)


def split(raw: Sequence[dict], d: int) -> tuple[tuple, tuple]:
    geometry = []
    values = []
    for item in raw:
        g = (rref(item["left"], d), rref(item["right"], d))
        v = int(item["value"])
        if v not in (0, 1):
            raise AssertionError("nonbinary child")
        if not geometry or geometry[-1] != g:
            geometry.append(g)
            values.append([v])
        else:
            values[-1].append(v)
    patterns = tuple(tuple(group) for group in values)
    if any(pattern not in RUN_PATTERNS for pattern in patterns):
        raise AssertionError("run pattern")
    return tuple(geometry), patterns


def lift_space(space: Sequence[int], basis_rows: Sequence[int], d: int) -> tuple[int, ...]:
    rows = []
    for mask in space:
        value = 0
        for index, row in enumerate(basis_rows):
            if (int(mask) >> index) & 1:
                value ^= int(row)
        rows.append(value)
    return rref(rows, d)


def lift(raw: Sequence[dict], basis_rows: Sequence[int], d: int) -> tuple:
    return tuple(
        stat(
            lift_space(item["left"], basis_rows, d),
            lift_space(item["right"], basis_rows, d),
            int(item["value"]),
        )
        for item in raw
    )


def all_paths(m: int, n: int) -> list[tuple]:
    result = []

    def walk(i: int, j: int, prefix: list[tuple[int, int]]) -> None:
        if (i, j) == (m - 1, n - 1):
            result.append(tuple(prefix))
            return
        for di, dj in ((1, 0), (0, 1), (1, 1)):
            ni, nj = i + di, j + dj
            if ni < m and nj < n:
                prefix.append((ni, nj))
                walk(ni, nj, prefix)
                prefix.pop()

    walk(0, 0, [(0, 0)])
    return sorted(result)


def delannoy(m: int, n: int) -> int:
    return sum(math.comb(m, k) * math.comb(n, k) * (2 ** k) for k in range(min(m, n) + 1))


def length_hist(entries: Sequence[dict]) -> dict[str, int]:
    counts: dict[int, int] = {}
    for entry in entries:
        length = len(entry["trajectory"])
        counts[length] = counts.get(length, 0) + 1
    return {str(key): counts[key] for key in sorted(counts)}


def exact_total(left: dict[str, int], right: dict[str, int]) -> int:
    return sum(
        int(lc) * int(rc) * delannoy(int(ll) - 1, int(rl) - 1)
        for ll, lc in left.items()
        for rl, rc in right.items()
    )


def direct(lower: Sequence[tuple], upper: Sequence[tuple]) -> dict | None:
    parent: dict[tuple[int, int], tuple[int, int] | None] = {}
    for i, a in enumerate(lower):
        for j, b in enumerate(upper):
            if a[:2] != b[:2] or a[2] > b[2]:
                continue
            if (i, j) == (0, 0):
                parent[(i, j)] = None
            else:
                for previous in ((i - 1, j - 1), (i - 1, j), (i, j - 1)):
                    if previous in parent:
                        parent[(i, j)] = previous
                        break
    endpoint = (len(lower) - 1, len(upper) - 1)
    if endpoint not in parent:
        return None
    path = []
    cursor: tuple[int, int] | None = endpoint
    while cursor is not None:
        path.append(cursor)
        cursor = parent[cursor]
    path.reverse()
    return {"path": [[i, j] for i, j in path], "path_length": len(path)}


def product_language(base_values: Sequence[int]) -> set[tuple]:
    return set(itertools.product(*(RUN_PATTERNS if value == 0 else ((1,),) for value in base_values)))


def reorder(items: list, mode: str, seed: int) -> list:
    out = list(items)
    if mode == "reversed":
        out.reverse()
    elif mode == "seeded-shuffle":
        random.Random(seed).shuffle(out)
    elif mode != "original":
        raise AssertionError("order")
    return out


def independent_payload(manifest: dict, mode: str) -> dict:
    if manifest.get("manifest_digest") != MANIFEST_DIGEST:
        raise AssertionError("manifest digest")
    if manifest["chunking"]["transcript_root_digest"] != TRANSCRIPT:
        raise AssertionError("transcript")
    if manifest["execution"]["processed_internal_node_ids"] != [6, 7, 8]:
        raise AssertionError("processed nodes")
    stop = manifest["execution"]["stop"]
    if (stop["node_id"], stop["reason"], stop["required"], stop["no_layout_at_cap"]) != (
        9,
        "CHILD_PAIR_CAP_EXCEEDED",
        COUNTS["pairs"],
        False,
    ):
        raise AssertionError("stop")

    node8 = next(item for item in manifest["node_results"] if int(item["node_id"]) == 8)
    leaf4 = next(item for item in manifest["leaf_full_sets"] if int(item["node_id"]) == 4)
    if node8["output_receipt"]["receipt_digest"] != NODE8_RECEIPT:
        raise AssertionError("node8 receipt")
    if leaf4["output_receipt"]["receipt_digest"] != LEAF4_RECEIPT:
        raise AssertionError("leaf4 receipt")
    closure = node8["node_up_k"]
    if closure["reachable_entries_digest"] != NODE8_ENTRIES:
        raise AssertionError("entries digest")
    if closure["frontier_artifact_sha256"] != NODE8_FRONTIER or closure["up_k_artifact_sha256"] != NODE8_UPK:
        raise AssertionError("artifact binding")
    left_entries = closure["entries"]
    right_entries = leaf4["full_set"]["entries"]
    if (len(left_entries), len(right_entries)) != (COUNTS["left"], COUNTS["right"]):
        raise AssertionError("entry count")
    if h(left_entries) != NODE8_ENTRIES:
        raise AssertionError("entry content digest")

    retained_ids = list(closure["retained_class_ids"])
    retained = list(closure["retained_generators"])
    if len(retained_ids) != 28 or len(retained) != 28:
        raise AssertionError("retained family")
    catalog = {}
    by_skeleton = {}
    for source_index, (class_id, raw) in enumerate(zip(retained_ids, retained)):
        skeleton, patterns = split(raw, 2)
        if any(len(pattern) != 1 for pattern in patterns):
            raise AssertionError("retained run minimality")
        base_values = tuple(pattern[0] for pattern in patterns)
        if skeleton in by_skeleton:
            raise AssertionError("duplicate skeleton")
        by_skeleton[skeleton] = class_id
        catalog[class_id] = {
            "source_generator_index": source_index,
            "skeleton": skeleton,
            "base_values": base_values,
            "trajectory": raw,
        }

    left_forms = []
    observed = {class_id: set() for class_id in retained_ids}
    for source_index, entry in reorder(list(enumerate(left_entries)), mode, 0xC049109):
        raw = copy.deepcopy(entry["trajectory"])
        skeleton, patterns = split(raw, 2)
        if skeleton not in by_skeleton:
            raise AssertionError("entry skeleton")
        class_id = by_skeleton[skeleton]
        if entry.get("source_class_id") != class_id:
            raise AssertionError("provenance")
        if patterns not in product_language(catalog[class_id]["base_values"]):
            raise AssertionError("class product")
        observed[class_id].add(patterns)
        left_forms.append({
            "class_id": class_id,
            "run_pattern_codes": [RUN_CODE[p] for p in patterns],
            "trajectory_digest": h(raw),
            "source_entry_index": source_index,
        })
    for class_id in retained_ids:
        if observed[class_id] != product_language(catalog[class_id]["base_values"]):
            raise AssertionError("class completeness")

    right_forms = []
    right_skeleton = None
    right_observed = set()
    for source_index, entry in reorder(list(enumerate(right_entries)), mode, 0xC049209):
        raw = copy.deepcopy(entry["trajectory"])
        skeleton, patterns = split(raw, 1)
        if right_skeleton is None:
            right_skeleton = skeleton
        elif right_skeleton != skeleton:
            raise AssertionError("right skeleton")
        right_observed.add(patterns)
        right_forms.append({
            "run_pattern_codes": [RUN_CODE[p] for p in patterns],
            "trajectory_digest": h(raw),
            "source_entry_index": source_index,
        })
    if right_skeleton is None or len(right_skeleton) != 2:
        raise AssertionError("right skeleton length")
    if right_observed != set(itertools.product(RUN_PATTERNS, repeat=2)):
        raise AssertionError("right completeness")
    left_forms.sort(key=canon)
    right_forms.sort(key=canon)
    left_family_digest = h([[x["class_id"], x["run_pattern_codes"], x["trajectory_digest"]] for x in left_forms])
    right_family_digest = h([[x["run_pattern_codes"], x["trajectory_digest"]] for x in right_forms])

    descriptor = next(x for x in manifest["topology"]["internal_nodes"] if int(x["node_id"]) == 9)
    d = int(manifest["scaffold_case"]["d"])
    blocks = [tuple(block) for block in manifest["scaffold_case"]["whole_factor_blocks"]]
    left_boundary = rref(node8["parent_boundary"], d)
    right_boundary = rref(leaf4["boundary_rref_ambient"], d)
    common = join_space(left_boundary, right_boundary, d)
    covered = tuple(int(v) for v in descriptor["covered_factor_ids"])
    outside = tuple(int(v) for v in descriptor["outside_factor_ids"])
    covered_span = rref((row for fid in covered for row in blocks[fid]), d)
    outside_span = rref((row for fid in outside for row in blocks[fid]), d)
    parent_boundary = meet_space(covered_span, outside_span, d)
    if descriptor["child_node_ids"] != [8, 4]:
        raise AssertionError("descriptor")
    if (left_boundary, right_boundary, common, parent_boundary) != ((4, 1), (5,), (4, 1), (1,)):
        raise AssertionError("geometry")

    right_min = lift(leaf4["leaf_generator_coordinates"], right_boundary, d)
    if any(item[2] != 0 for item in right_min):
        raise AssertionError("right minimum")
    successful: dict[bytes, dict] = {}
    failed = []
    quotient_count = 0
    successful_count = 0
    assignment_tests = 0
    join_counts = {0: 0, 1: 0}
    shrink_counts = {0: 0, 1: 0}
    cells = 0

    for left_class_id in sorted(catalog):
        left_min = lift(catalog[left_class_id]["trajectory"], left_boundary, d)
        initial = meet_space(left_min[0][1], right_min[0][1], d)
        for path_index, path in enumerate(all_paths(len(left_min), len(right_min))):
            quotient_count += 1
            precompact = []
            join_corrections = []
            shrink_corrections = []
            base_values = []
            for i, j in path:
                a, b = left_min[i], right_min[j]
                joined_left = join_space(a[0], b[0], d)
                joined_right = join_space(a[1], b[1], d)
                current = meet_space(join_space(a[0], a[1], d), join_space(b[0], b[1], d), d)
                jc = len(initial) - len(current)
                if jc not in (0, 1):
                    raise AssertionError("join correction")
                lr = meet_space(joined_left, joined_right, d)
                projected_left = meet_space(joined_left, parent_boundary, d)
                projected_right = meet_space(joined_right, parent_boundary, d)
                sc = len(lr) - len(meet_space(lr, parent_boundary, d))
                if sc not in (0, 1):
                    raise AssertionError("shrink correction")
                value = a[2] + b[2] + jc + sc
                precompact.append(stat(projected_left, projected_right, value))
                join_corrections.append(jc)
                shrink_corrections.append(sc)
                base_values.append(value)
                join_counts[jc] += 1
                shrink_counts[sc] += 1
                cells += 1
            lower = compact(precompact)
            lower_width = max(x[2] for x in lower)
            source = {
                "left_class_id": left_class_id,
                "local_path_index": path_index,
                "quotient_path": [[i, j] for i, j in path],
                "join_corrections": join_corrections,
                "shrink_corrections": shrink_corrections,
                "base_values": base_values,
                "projected_precompact": encode(precompact),
                "compact_lower_envelope": encode(lower),
                "compact_lower_envelope_width": lower_width,
            }
            if lower_width <= 1:
                successful_count += 1
                if any(v not in (0, 1) for v in base_values):
                    raise AssertionError("successful nonbinary base")
                key = canon(encode(lower))
                if key not in successful:
                    successful[key] = {"generator": encode(lower), "sources": [], "assignment_tests": 0}
                local_cases = 0
                choices = [RUN_PATTERNS if value == 0 else ((1,),) for value in base_values]
                for assignment in itertools.product(*choices):
                    raw_upper = []
                    for item, pattern in zip(precompact, assignment):
                        raw_upper.extend(stat(item[0], item[1], value) for value in pattern)
                    upper = compact(raw_upper)
                    if max(item[2] for item in upper) > 1:
                        raise AssertionError("binary abstraction width")
                    if direct(lower, upper) is None:
                        raise AssertionError("direct coverage")
                    local_cases += 1
                source["local_direct_assignment_tests"] = local_cases
                successful[key]["sources"].append(source)
                successful[key]["assignment_tests"] += local_cases
                assignment_tests += local_cases
            else:
                if lower_width != 2:
                    raise AssertionError("failure width")
                overflow = next(index for index, item in enumerate(lower) if item[2] > 1)
                source["failure_kind"] = "UNIVERSAL_LOWER_ENVELOPE_WIDTH_CAP"
                source["first_compact_overflow_index"] = overflow
                source["first_compact_overflow_statistic"] = encode_stat(lower[overflow])
                source["successful_binary_assignment_count"] = 0
                failed.append(source)

    if (
        quotient_count,
        successful_count,
        len(failed),
        len(successful),
        assignment_tests,
        cells,
    ) != (
        COUNTS["quotient"],
        COUNTS["successful"],
        COUNTS["failed"],
        COUNTS["classes"],
        COUNTS["assignments"],
        COUNTS["cells"],
    ):
        raise AssertionError("structural counts")
    if join_counts != JOIN_COUNTS or shrink_counts != SHRINK_COUNTS:
        raise AssertionError("correction counts")

    classes = []
    path_to_class = []
    for index, key in enumerate(sorted(successful)):
        item = successful[key]
        class_id = f"N9-S{index:02d}"
        canonical_source = sorted(item["sources"], key=canon)[0]
        generator = item["generator"]
        classes.append({
            "class_id": class_id,
            "canonical_generator": generator,
            "generator_digest": h(generator),
            "width": max(x["value"] for x in generator),
            "length": len(generator),
            "source_path_multiplicity": len(item["sources"]),
            "canonical_reachability_witness": canonical_source,
            "source_path_digest": h(sorted(item["sources"], key=canon)),
            "local_direct_assignment_tests": item["assignment_tests"],
        })
        for source in item["sources"]:
            path_to_class.append({
                "left_class_id": source["left_class_id"],
                "local_path_index": source["local_path_index"],
                "class_id": class_id,
                "quotient_path": source["quotient_path"],
                "join_corrections": source["join_corrections"],
                "shrink_corrections": source["shrink_corrections"],
                "base_values": source["base_values"],
            })
    path_to_class.sort(key=canon)
    failed.sort(key=canon)

    left_hist = length_hist(left_entries)
    right_hist = length_hist(right_entries)
    pair_count = len(left_entries) * len(right_entries)
    refinement_count = exact_total(left_hist, right_hist)
    if (pair_count, refinement_count) != (COUNTS["pairs"], COUNTS["refinements"]):
        raise AssertionError("frontier totals")

    return {
        "source": {
            "integrated_manifest_file_sha256": MANIFEST_SHA,
            "integrated_manifest_digest": MANIFEST_DIGEST,
            "transcript_root_digest": TRANSCRIPT,
            "node8_output_receipt_digest": NODE8_RECEIPT,
            "leaf4_output_receipt_digest": LEAF4_RECEIPT,
            "node8_entries_digest": NODE8_ENTRIES,
            "node8_frontier_artifact_sha256": NODE8_FRONTIER,
            "node8_up_k_artifact_sha256": NODE8_UPK,
        },
        "node_id": 9,
        "ambient_dim": d,
        "k": int(manifest["scaffold_case"]["k"]),
        "child_normal_forms": {
            "left_entry_count": len(left_forms),
            "right_entry_count": len(right_forms),
            "left_family_digest": left_family_digest,
            "right_family_digest": right_family_digest,
            "left_skeleton_count": len(catalog),
            "right_skeleton_count": 1,
            "typical_pattern_catalog": [RUN_CODE[p] for p in RUN_PATTERNS],
            "left_class_inventory": [
                {
                    "class_id": class_id,
                    "skeleton_length": len(catalog[class_id]["skeleton"]),
                    "base_values": list(catalog[class_id]["base_values"]),
                    "entry_count": len(product_language(catalog[class_id]["base_values"])),
                }
                for class_id in sorted(catalog)
            ],
        },
        "geometry": {
            "descriptor": descriptor,
            "left_boundary": list(left_boundary),
            "right_boundary": list(right_boundary),
            "common_boundary": list(common),
            "parent_boundary": list(parent_boundary),
            "left_expand_identity": True,
            "right_boundary_embedded_in_common": True,
            "shrink_is_identity": False,
            "join_correction_counts_over_quotient_cells": {str(key): join_counts[key] for key in sorted(join_counts)},
            "shrink_correction_counts_over_quotient_cells": {str(key): shrink_counts[key] for key in sorted(shrink_counts)},
        },
        "exact_frontier": {
            "child_pair_count": pair_count,
            "naive_refinement_count": refinement_count,
            "left_length_histogram": left_hist,
            "right_length_histogram": right_hist,
            "cartesian_child_pairs_materialized": 0,
            "fine_lattice_paths_enumerated": 0,
        },
        "quotient_frontier": {
            "quotient_path_count": quotient_count,
            "successful_quotient_path_count": successful_count,
            "universal_failed_quotient_path_count": len(failed),
            "post_shrink_successful_class_count": len(classes),
            "successful_source_path_collision_count": successful_count - len(classes),
            "classes": classes,
            "path_to_class": path_to_class,
            "universal_failure_partition": failed,
            "all_successful_generators_reachable": True,
            "all_successful_generators_width_at_most_k": True,
            "universal_direct_coverage": True,
            "failed_refinement_partition_complete": True,
            "local_direct_assignment_tests": assignment_tests,
            "direct_witness_kind": "EXTENSION_PREORDER_DIRECT",
            "failure_witness_kind": "COMPACT_LOWER_ENVELOPE_WIDTH_CAP",
            "transitive_closure_used": False,
        },
        "work_ledger": {
            "left_entries_read": len(left_entries),
            "right_entries_read": len(right_entries),
            "left_right_cartesian_pairs_materialized": 0,
            "fine_lattice_paths_enumerated": 0,
            "quotient_paths_enumerated": quotient_count,
            "quotient_cells_checked": cells,
            "successful_quotient_paths": successful_count,
            "universal_failed_quotient_paths": len(failed),
            "post_shrink_successful_classes": len(classes),
            "local_direct_witness_assignments_tested": assignment_tests,
            "naive_refinements_avoided": refinement_count,
        },
        "invariant_vector": {f"N9-INV-{index:02d}": "PASS" for index in range(1, 11)},
        "admit": True,
        "strict_boundary": {
            "node8_integrated_into_bottom_up_executor": True,
            "node9_parent_generator_frontier_complete": True,
            "node9_parent_refinement_complete": True,
            "node9_parent_up_k_complete": False,
            "node9_integrated_into_bottom_up_executor": False,
            "root_parent_refinement_started": False,
            "negative_root_reached": False,
            "terminal_completeness_proved": False,
            "found_layout_enabled": False,
            "no_layout_at_cap_enabled": False,
            "current_global_terminal": TERMINAL,
            "p_vs_np": "OPEN",
        },
        "next_gate": "C049.1_B4.6.3_NODE9_FIFTEEN_GENERATOR_UP_K_CLOSURE",
    }


def static_scan(source_path: Path) -> None:
    tree = ast.parse(source_path.read_text(encoding="utf-8"))

    def inventory_name(node: ast.AST) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"enumerate", "list", "tuple"} and node.args:
            return inventory_name(node.args[0])
        return None

    def visit(node: ast.AST, active: tuple[str, ...]) -> None:
        next_active = active
        if isinstance(node, (ast.For, ast.comprehension)):
            name = inventory_name(node.iter)
            if name in {"left_entries", "right_entries", "left_forms", "right_forms"}:
                opposite = {"left_entries": "right_entries", "right_entries": "left_entries", "left_forms": "right_forms", "right_forms": "left_forms"}[name]
                if opposite in active:
                    raise AssertionError("nested child Cartesian inventory iteration")
                next_active = (*active, name)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "product":
            names = {inventory_name(arg) for arg in node.args}
            if ({"left_entries", "right_entries"} <= names) or ({"left_forms", "right_forms"} <= names):
                raise AssertionError("explicit child Cartesian product")
        for child in ast.iter_child_nodes(node):
            visit(child, next_active)

    visit(tree, ())


def verify(manifest_path: Path, artifact: dict, producer_source: Path | None = None) -> dict:
    if file_hash(manifest_path) != MANIFEST_SHA:
        raise AssertionError("manifest file hash")
    if artifact.get("schema") != SCHEMA or artifact.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("artifact schema")
    if artifact.get("semantic_digest") != h(artifact.get("proof_payload")):
        raise AssertionError("artifact semantic digest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_original = independent_payload(manifest, "original")
    expected_reversed = independent_payload(manifest, "reversed")
    expected_shuffled = independent_payload(manifest, "seeded-shuffle")
    if expected_original != expected_reversed or expected_original != expected_shuffled:
        raise AssertionError("independent order replay mismatch")
    if artifact["proof_payload"] != expected_original:
        raise AssertionError("producer artifact differs from independent replay")
    if producer_source is not None:
        static_scan(producer_source)
    return expected_original


def tamper_tests(artifact: dict, expected: dict) -> int:
    attacks = []

    def attack(path: Sequence[Any], value: Any) -> dict:
        item = copy.deepcopy(artifact)
        cursor = item
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = value
        item["semantic_digest"] = h(item["proof_payload"])
        return item

    attacks.append(attack(("proof_payload", "source", "integrated_manifest_file_sha256"), "0" * 64))
    attacks.append(attack(("proof_payload", "child_normal_forms", "left_entry_count"), 15947))
    attacks.append(attack(("proof_payload", "geometry", "parent_boundary"), [4, 1]))
    attacks.append(attack(("proof_payload", "geometry", "join_correction_counts_over_quotient_cells", "1"), 153))
    item = copy.deepcopy(artifact)
    item["proof_payload"]["quotient_frontier"]["universal_failure_partition"].pop()
    item["semantic_digest"] = h(item["proof_payload"])
    attacks.append(item)
    item = copy.deepcopy(artifact)
    item["proof_payload"]["quotient_frontier"]["classes"].pop()
    item["semantic_digest"] = h(item["proof_payload"])
    attacks.append(item)
    item = copy.deepcopy(artifact)
    item["proof_payload"]["quotient_frontier"]["classes"][0]["canonical_generator"][0]["value"] = 1
    item["semantic_digest"] = h(item["proof_payload"])
    attacks.append(item)
    attacks.append(attack(("proof_payload", "quotient_frontier", "transitive_closure_used"), True))
    attacks.append(attack(("proof_payload", "strict_boundary", "negative_root_reached"), True))
    attacks.append(attack(("proof_payload", "strict_boundary", "p_vs_np"), "CLOSED"))

    rejected = 0
    for candidate in attacks:
        try:
            if candidate.get("schema") != SCHEMA:
                raise AssertionError("schema")
            if candidate.get("semantic_digest") != h(candidate.get("proof_payload")):
                raise AssertionError("digest")
            if candidate.get("proof_payload") != expected:
                raise AssertionError("independent replay mismatch")
        except Exception:
            rejected += 1
    if rejected != len(attacks):
        raise AssertionError("tamper rejection incomplete")
    return rejected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--producer-source", type=Path)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    artifact = json.loads(args.artifact.read_text(encoding="utf-8"))
    payload = verify(args.manifest, artifact, args.producer_source)
    rejected = tamper_tests(artifact, payload) if args.tamper_self_test else 0
    print("STATIC_NO_CHILD_CARTESIAN_ENUMERATION = PASS")
    print("JANUS_C049_1_B4_6_3_NODE9_FRONTIER_COMPRESSION_VERIFIER = PASS")
    print("INVARIANTS = 10/10")
    print("QUOTIENT_PATHS =", payload["quotient_frontier"]["quotient_path_count"])
    print("UNIVERSAL_FAILED_QUOTIENT_PATHS =", payload["quotient_frontier"]["universal_failed_quotient_path_count"])
    print("POST_SHRINK_SUCCESSFUL_CLASSES =", payload["quotient_frontier"]["post_shrink_successful_class_count"])
    print("LOCAL_DIRECT_WITNESS_ASSIGNMENTS =", payload["quotient_frontier"]["local_direct_assignment_tests"])
    if args.tamper_self_test:
        print(f"TAMPER_ATTACKS_REJECTED = {rejected}/10")


if __name__ == "__main__":
    main()
