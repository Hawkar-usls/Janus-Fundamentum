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

SCHEMA = "C049.1-B4.6.3-NODE8-PARENT-FRONTIER-STRUCTURAL-COMPRESSION-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
EXPECTED_MANIFEST_FILE_SHA256 = "05a4269be3b15bee40c254f81cc5e668c4903e90777576a9f0d226093892122b"
EXPECTED_MANIFEST_DIGEST = "c1b34fe2e47a1566b9cde045dd28fbdafdd30780de834b6d0bdb8731b11a00d6"
EXPECTED_TRANSCRIPT = "eb904e833b53cf5626af1eb28493f479f5f54f2066a8b5427cb7e3eb47f515d8"
EXPECTED_NODE7_RECEIPT = "838e4dfde9740585928b5498e18a5b0836f44da1d822c060d5c59b7d52177011"
EXPECTED_LEAF3_RECEIPT = "80f424b87fd39e80013e1bb96b3dcec47d281a322f9964472b2ca32bd039e086"
EXPECTED_NODE7_ENTRIES_DIGEST = "269d5cd926d3be3df5641066a7986dfb1df049abab68b4202f6bc9a39e27a46e"
EXPECTED_FRONTIER_SHA256 = "6a0748219d829434feeb5de2c5488e1fa3aeb1fab16ecbfee0c5629be90130a9"
EXPECTED_UP_K_SHA256 = "c085a3bee4e0c92a01eb22715390079f9858c5704ebcbf8534f9de196087d189"
PATTERNS = ((0,), (0, 1), (0, 1, 0), (1,), (1, 0), (1, 0, 1))
CODES = {p: "".join(str(v) for v in p) for p in PATTERNS}
EXPECTED_COUNTS = {
    "left": 9108,
    "right": 36,
    "pairs": 327888,
    "refinements": 602017584,
    "paths": 75,
    "classes": 61,
    "assignments": 31500,
}


def canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def hash_value(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def basis(rows: Iterable[int], d: int) -> tuple[int, ...]:
    pivots: dict[int, int] = {}
    for raw in rows:
        value = int(raw)
        if not 0 <= value < (1 << d):
            raise AssertionError("vector range")
        while value:
            p = value.bit_length() - 1
            if p in pivots:
                value ^= pivots[p]
            else:
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


def vectors(space: Sequence[int]) -> set[int]:
    result = {0}
    for row in space:
        result.update({value ^ int(row) for value in tuple(result)})
    return result


def plus(a: Sequence[int], b: Sequence[int], d: int) -> tuple[int, ...]:
    return basis((*a, *b), d)


def meet(a: Sequence[int], b: Sequence[int], d: int) -> tuple[int, ...]:
    return basis(vectors(a) & vectors(b), d)


def encode_stat(stat: tuple) -> dict:
    return {"left": list(stat[0]), "right": list(stat[1]), "value": int(stat[2])}


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
                values0 = [item[2] for item in current[start : end + 1]]
                monotone_interval = (
                    values0[0] <= values0[-1]
                    and all(values0[0] <= z <= values0[-1] for z in values0[1:-1])
                ) or (
                    values0[0] >= values0[-1]
                    and all(values0[0] >= z >= values0[-1] for z in values0[1:-1])
                )
                if monotone_interval:
                    del current[start + 1 : end]
                    changed = True
                    break
            if changed:
                break
        if not changed:
            return tuple(current)


def runs(raw: Sequence[dict], d: int) -> tuple[tuple, tuple]:
    skeleton = []
    values = []
    for item in raw:
        geom = (basis(item["left"], d), basis(item["right"], d))
        value = int(item["value"])
        if value not in (0, 1):
            raise AssertionError("nonbinary")
        if not skeleton or skeleton[-1] != geom:
            skeleton.append(geom)
            values.append([value])
        else:
            values[-1].append(value)
    patterns = tuple(tuple(group) for group in values)
    if any(item not in PATTERNS for item in patterns):
        raise AssertionError("pattern catalog")
    return tuple(skeleton), patterns


def lift_space(space: Sequence[int], coordinate_basis: Sequence[int], d: int) -> tuple[int, ...]:
    rows = []
    for mask0 in space:
        value = 0
        for index, row in enumerate(coordinate_basis):
            if (int(mask0) >> index) & 1:
                value ^= int(row)
        rows.append(value)
    return basis(rows, d)


def lift(raw: Sequence[dict], coordinate_basis: Sequence[int], d: int) -> tuple:
    return tuple(
        (
            lift_space(item["left"], coordinate_basis, d),
            lift_space(item["right"], coordinate_basis, d),
            int(item["value"]),
        )
        for item in raw
    )


def paths(m: int, n: int) -> list[tuple]:
    result = []

    def visit(i: int, j: int, prefix: list[tuple[int, int]]) -> None:
        if i == m - 1 and j == n - 1:
            result.append(tuple(prefix))
            return
        for step in ((1, 0), (0, 1), (1, 1)):
            ni, nj = i + step[0], j + step[1]
            if ni < m and nj < n:
                prefix.append((ni, nj))
                visit(ni, nj, prefix)
                prefix.pop()

    visit(0, 0, [(0, 0)])
    return sorted(result)


def delannoy(m: int, n: int) -> int:
    total = 0
    for k in range(min(m, n) + 1):
        total += math.comb(m, k) * math.comb(n, k) * (2 ** k)
    return total


def histogram(entries: Sequence[dict]) -> dict[str, int]:
    out: dict[int, int] = {}
    for entry in entries:
        out[len(entry["trajectory"])] = out.get(len(entry["trajectory"]), 0) + 1
    return {str(key): out[key] for key in sorted(out)}


def refinement_total(left: dict[str, int], right: dict[str, int]) -> int:
    total = 0
    for lm, lc in left.items():
        for rn, rc in right.items():
            total += int(lc) * int(rc) * delannoy(int(lm) - 1, int(rn) - 1)
    return total


def direct_witness(lower: Sequence[tuple], upper: Sequence[tuple]) -> dict | None:
    seen: dict[tuple[int, int], tuple[int, int] | None] = {}
    for i, low in enumerate(lower):
        for j, high in enumerate(upper):
            if low[:2] != high[:2] or low[2] > high[2]:
                continue
            if (i, j) == (0, 0):
                seen[(i, j)] = None
            else:
                for previous in ((i - 1, j - 1), (i - 1, j), (i, j - 1)):
                    if previous in seen:
                        seen[(i, j)] = previous
                        break
    endpoint = (len(lower) - 1, len(upper) - 1)
    if endpoint not in seen:
        return None
    path = []
    cursor: tuple[int, int] | None = endpoint
    while cursor is not None:
        path.append(cursor)
        cursor = seen[cursor]
    path.reverse()
    return {"path": [[i, j] for i, j in path], "path_length": len(path)}


def order_items(items: list, mode: str, seed: int) -> list:
    result = list(items)
    if mode == "reversed":
        result.reverse()
    elif mode == "seeded-shuffle":
        random.Random(seed).shuffle(result)
    elif mode != "original":
        raise AssertionError("order mode")
    return result


def independent_payload(manifest: dict, mode: str) -> dict:
    if manifest.get("manifest_digest") != EXPECTED_MANIFEST_DIGEST:
        raise AssertionError("manifest digest")
    if manifest["chunking"]["transcript_root_digest"] != EXPECTED_TRANSCRIPT:
        raise AssertionError("transcript digest")
    if manifest["execution"]["processed_internal_node_ids"] != [6, 7]:
        raise AssertionError("processed vector")
    stop = manifest["execution"]["stop"]
    if (stop["node_id"], stop["reason"], stop["required"], stop["no_layout_at_cap"]) != (
        8,
        "CHILD_PAIR_CAP_EXCEEDED",
        EXPECTED_COUNTS["pairs"],
        False,
    ):
        raise AssertionError("stop boundary")

    node7 = next(node for node in manifest["node_results"] if int(node["node_id"]) == 7)
    leaf3 = next(leaf for leaf in manifest["leaf_full_sets"] if int(leaf["node_id"]) == 3)
    if node7["output_receipt"]["receipt_digest"] != EXPECTED_NODE7_RECEIPT:
        raise AssertionError("node7 receipt")
    if leaf3["output_receipt"]["receipt_digest"] != EXPECTED_LEAF3_RECEIPT:
        raise AssertionError("leaf3 receipt")
    closure = node7["node_up_k"]
    if closure["reachable_entries_digest"] != EXPECTED_NODE7_ENTRIES_DIGEST:
        raise AssertionError("entry receipt")
    if closure["frontier_artifact_sha256"] != EXPECTED_FRONTIER_SHA256:
        raise AssertionError("frontier source")
    if closure["up_k_artifact_sha256"] != EXPECTED_UP_K_SHA256:
        raise AssertionError("up_k source")
    left_entries = closure["entries"]
    right_entries = leaf3["full_set"]["entries"]
    if len(left_entries) != EXPECTED_COUNTS["left"] or len(right_entries) != EXPECTED_COUNTS["right"]:
        raise AssertionError("entry counts")
    if hash_value(left_entries) != EXPECTED_NODE7_ENTRIES_DIGEST:
        raise AssertionError("entry content")

    class_ids = list(closure["retained_class_ids"])
    retained = list(closure["retained_generators"])
    skeleton_map = {}
    retained_info = {}
    for index, (class_id, generator) in enumerate(zip(class_ids, retained)):
        skeleton, pattern_values = runs(generator, 2)
        if pattern_values != tuple((0,) for _ in skeleton):
            raise AssertionError("retained zero envelope")
        if skeleton in skeleton_map:
            raise AssertionError("retained skeleton collision")
        skeleton_map[skeleton] = class_id
        retained_info[class_id] = {
            "source_generator_index": index,
            "skeleton": skeleton,
            "trajectory": generator,
        }
    if len(retained_info) != 13:
        raise AssertionError("retained inventory")

    left_forms = []
    left_products = {class_id: set() for class_id in class_ids}
    indexed_left = order_items(list(enumerate(left_entries)), mode, 0xC049108)
    for original_index, entry in indexed_left:
        skeleton, pattern_values = runs(entry["trajectory"], 2)
        class_id = skeleton_map.get(skeleton)
        if class_id is None or entry.get("source_class_id") != class_id:
            raise AssertionError("left provenance")
        codes0 = tuple(CODES[value] for value in pattern_values)
        left_products[class_id].add(codes0)
        left_forms.append({
            "class_id": class_id,
            "run_pattern_codes": list(codes0),
            "trajectory_digest": hash_value(entry["trajectory"]),
            "source_entry_index": original_index,
        })
    code_values = tuple(CODES[p] for p in PATTERNS)
    for class_id, item in retained_info.items():
        if left_products[class_id] != set(itertools.product(code_values, repeat=len(item["skeleton"]))):
            raise AssertionError("left product completeness")

    right_forms = []
    right_product = set()
    right_skeleton = None
    indexed_right = order_items(list(enumerate(right_entries)), mode, 0xC049109)
    for original_index, entry in indexed_right:
        skeleton, pattern_values = runs(entry["trajectory"], 1)
        if right_skeleton is None:
            right_skeleton = skeleton
        elif right_skeleton != skeleton:
            raise AssertionError("right skeleton")
        codes0 = tuple(CODES[value] for value in pattern_values)
        right_product.add(codes0)
        right_forms.append({
            "run_pattern_codes": list(codes0),
            "trajectory_digest": hash_value(entry["trajectory"]),
            "source_entry_index": original_index,
        })
    if right_skeleton is None or len(right_skeleton) != 2:
        raise AssertionError("right skeleton shape")
    if right_product != set(itertools.product(code_values, repeat=2)):
        raise AssertionError("right product completeness")
    left_forms.sort(key=canon)
    right_forms.sort(key=canon)
    left_family_digest = hash_value([[item["class_id"], item["run_pattern_codes"], item["trajectory_digest"]] for item in left_forms])
    right_family_digest = hash_value([[item["run_pattern_codes"], item["trajectory_digest"]] for item in right_forms])

    descriptor = next(item for item in manifest["topology"]["internal_nodes"] if int(item["node_id"]) == 8)
    if descriptor["child_node_ids"] != [7, 3]:
        raise AssertionError("descriptor")
    d = int(manifest["scaffold_case"]["d"])
    blocks = [tuple(block) for block in manifest["scaffold_case"]["whole_factor_blocks"]]
    left_boundary = basis(node7["parent_boundary"], d)
    right_boundary = basis(leaf3["boundary_rref_ambient"], d)
    common = plus(left_boundary, right_boundary, d)
    covered_span = basis((row for factor in descriptor["covered_factor_ids"] for row in blocks[int(factor)]), d)
    outside_span = basis((row for factor in descriptor["outside_factor_ids"] for row in blocks[int(factor)]), d)
    parent = meet(covered_span, outside_span, d)
    if (left_boundary, right_boundary, common, parent) != ((4, 2), (3,), (4, 2, 1), (4, 1)):
        raise AssertionError("geometry")

    right_zero = lift(leaf3["leaf_generator_coordinates"], right_boundary, d)
    unique: dict[bytes, dict] = {}
    path_count = 0
    join_cells = 0
    correction_counts = {0: 0, 1: 0}
    assignment_count = 0

    for class_id in sorted(retained_info):
        left_zero = lift(retained_info[class_id]["trajectory"], left_boundary, d)
        initial = meet(left_zero[0][1], right_zero[0][1], d)
        for local_path_index, path0 in enumerate(paths(len(left_zero), len(right_zero))):
            path_count += 1
            projected = []
            join_corrections = []
            shrink_corrections = []
            for i, j in path0:
                a, b = left_zero[i], right_zero[j]
                joined_left = plus(a[0], b[0], d)
                joined_right = plus(a[1], b[1], d)
                current = meet(plus(a[0], a[1], d), plus(b[0], b[1], d), d)
                join_corr = len(initial) - len(current)
                if join_corr != 0:
                    raise AssertionError("join correction")
                join_cells += 1
                lr = meet(joined_left, joined_right, d)
                projected_left = meet(joined_left, parent, d)
                projected_right = meet(joined_right, parent, d)
                triple = meet(lr, parent, d)
                shrink_corr = len(lr) - len(triple)
                if shrink_corr not in correction_counts:
                    raise AssertionError("shrink correction")
                correction_counts[shrink_corr] += 1
                join_corrections.append(join_corr)
                shrink_corrections.append(shrink_corr)
                projected.append((projected_left, projected_right, shrink_corr))
            envelope = compact(projected)
            if max(item[2] for item in envelope) > 1:
                raise AssertionError("width")
            key = canon(encode(envelope))
            source = {
                "left_class_id": class_id,
                "local_path_index": local_path_index,
                "quotient_path": [[i, j] for i, j in path0],
                "join_corrections": join_corrections,
                "shrink_corrections": shrink_corrections,
                "projected_precompact": encode(projected),
            }
            bucket = unique.setdefault(key, {"generator": encode(envelope), "sources": [], "assignment_tests": 0})
            bucket["sources"].append(source)

            choices = [PATTERNS if corr == 0 else ((1,),) for corr in shrink_corrections]
            local_cases = 0
            for assignment in itertools.product(*choices):
                upper_raw = []
                for stat, pattern in zip(projected, assignment):
                    upper_raw.extend((stat[0], stat[1], int(value)) for value in pattern)
                upper = compact(upper_raw)
                if direct_witness(envelope, upper) is None:
                    raise AssertionError("direct witness")
                if max(item[2] for item in upper) > 1:
                    raise AssertionError("abstract success width")
                local_cases += 1
            bucket["assignment_tests"] += local_cases
            assignment_count += local_cases

    if (path_count, len(unique), assignment_count) != (
        EXPECTED_COUNTS["paths"],
        EXPECTED_COUNTS["classes"],
        EXPECTED_COUNTS["assignments"],
    ):
        raise AssertionError("quotient totals")

    classes = []
    path_map = []
    for class_index, key in enumerate(sorted(unique)):
        item = unique[key]
        class_id = f"N8-S{class_index:02d}"
        sources = sorted(item["sources"], key=canon)
        generator = item["generator"]
        classes.append({
            "class_id": class_id,
            "canonical_generator": generator,
            "generator_digest": hash_value(generator),
            "width": max(stat["value"] for stat in generator),
            "length": len(generator),
            "source_path_multiplicity": len(sources),
            "canonical_reachability_witness": sources[0],
            "source_path_digest": hash_value(sources),
            "local_direct_assignment_tests": item["assignment_tests"],
        })
        for source in item["sources"]:
            path_map.append({
                "left_class_id": source["left_class_id"],
                "local_path_index": source["local_path_index"],
                "class_id": class_id,
                "quotient_path": source["quotient_path"],
                "shrink_corrections": source["shrink_corrections"],
            })
    path_map.sort(key=canon)

    left_hist = histogram(left_entries)
    right_hist = histogram(right_entries)
    pairs0 = len(left_entries) * len(right_entries)
    refs0 = refinement_total(left_hist, right_hist)
    if pairs0 != EXPECTED_COUNTS["pairs"] or refs0 != EXPECTED_COUNTS["refinements"]:
        raise AssertionError("frontier totals")

    return {
        "source": {
            "integrated_manifest_file_sha256": EXPECTED_MANIFEST_FILE_SHA256,
            "integrated_manifest_digest": EXPECTED_MANIFEST_DIGEST,
            "transcript_root_digest": EXPECTED_TRANSCRIPT,
            "node7_output_receipt_digest": EXPECTED_NODE7_RECEIPT,
            "leaf3_output_receipt_digest": EXPECTED_LEAF3_RECEIPT,
            "node7_entries_digest": EXPECTED_NODE7_ENTRIES_DIGEST,
            "node7_frontier_artifact_sha256": EXPECTED_FRONTIER_SHA256,
            "node7_up_k_artifact_sha256": EXPECTED_UP_K_SHA256,
        },
        "node_id": 8,
        "ambient_dim": d,
        "k": int(manifest["scaffold_case"]["k"]),
        "child_normal_forms": {
            "left_entry_count": len(left_forms),
            "right_entry_count": len(right_forms),
            "left_family_digest": left_family_digest,
            "right_family_digest": right_family_digest,
            "left_skeleton_count": len(retained_info),
            "right_skeleton_count": 1,
            "typical_pattern_catalog": [CODES[p] for p in PATTERNS],
            "left_class_inventory": [
                {
                    "class_id": class_id,
                    "skeleton_length": len(retained_info[class_id]["skeleton"]),
                    "entry_count": 6 ** len(retained_info[class_id]["skeleton"]),
                }
                for class_id in sorted(retained_info)
            ],
        },
        "geometry": {
            "descriptor": descriptor,
            "left_boundary": list(left_boundary),
            "right_boundary": list(right_boundary),
            "common_boundary": list(common),
            "parent_boundary": list(parent),
            "join_lambda_correction_identically_zero": True,
            "shrink_is_identity": False,
            "shrink_correction_counts_over_quotient_cells": {str(key): correction_counts[key] for key in sorted(correction_counts)},
        },
        "exact_frontier": {
            "child_pair_count": pairs0,
            "naive_refinement_count": refs0,
            "left_length_histogram": left_hist,
            "right_length_histogram": right_hist,
            "cartesian_child_pairs_materialized": 0,
            "fine_lattice_paths_enumerated": 0,
        },
        "quotient_frontier": {
            "pre_shrink_quotient_path_count": path_count,
            "post_shrink_class_count": len(classes),
            "source_path_collision_count": path_count - len(classes),
            "classes": classes,
            "path_to_class": path_map,
            "all_zero_envelopes_reachable": True,
            "all_zero_envelopes_width_at_most_k": True,
            "universal_direct_coverage": True,
            "local_direct_assignment_tests": assignment_count,
            "direct_witness_kind": "EXTENSION_PREORDER_DIRECT",
            "transitive_closure_used": False,
        },
        "work_ledger": {
            "left_entries_read": len(left_entries),
            "right_entries_read": len(right_entries),
            "left_right_cartesian_pairs_materialized": 0,
            "fine_lattice_paths_enumerated": 0,
            "quotient_paths_enumerated": path_count,
            "quotient_join_cells_checked": join_cells,
            "post_shrink_classes": len(classes),
            "local_direct_witness_assignments_tested": assignment_count,
            "naive_refinements_avoided": refs0,
        },
        "invariant_vector": {f"N8-INV-{index:02d}": "PASS" for index in range(1, 11)},
        "admit": True,
        "strict_boundary": {
            "node7_integrated_into_bottom_up_executor": True,
            "node8_parent_generator_frontier_complete": True,
            "node8_parent_refinement_complete": True,
            "node8_parent_up_k_complete": False,
            "node8_integrated_into_bottom_up_executor": False,
            "node9_parent_refinement_started": False,
            "negative_root_reached": False,
            "terminal_completeness_proved": False,
            "found_layout_enabled": False,
            "no_layout_at_cap_enabled": False,
            "current_global_terminal": TERMINAL,
            "p_vs_np": "OPEN",
        },
        "next_gate": "C049.1_B4.6.3_NODE8_SIXTY_ONE_GENERATOR_UP_K_CLOSURE",
    }


def reject_if_invalid(manifest: dict, artifact: dict, expected: dict) -> None:
    if artifact.get("schema") != SCHEMA:
        raise AssertionError("schema")
    if artifact.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("semantic scope")
    if artifact.get("proof_payload") != expected:
        raise AssertionError("independent replay mismatch")
    if artifact.get("semantic_digest") != hash_value(expected):
        raise AssertionError("semantic digest")
    if expected["admit"] is not True or set(expected["invariant_vector"].values()) != {"PASS"}:
        raise AssertionError("admission vector")


def verify_source_no_cartesian(source_path: Path) -> None:
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    if "lattice_paths(" in source:
        raise AssertionError("fine lattice enumerator referenced")
    forbidden_names = {"left_entries", "right_entries"}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.For, ast.AsyncFor)):
            continue
        outer_text = ast.get_source_segment(source, node.iter) or ""
        outer_side = next((name for name in forbidden_names if name in outer_text), None)
        if outer_side is None:
            continue
        for child in ast.walk(ast.Module(body=node.body, type_ignores=[])):
            if child is node or not isinstance(child, (ast.For, ast.AsyncFor)):
                continue
            inner_text = ast.get_source_segment(source, child.iter) or ""
            other = (forbidden_names - {outer_side}).pop()
            if other in inner_text:
                raise AssertionError("child Cartesian product in producer")
    print("STATIC_NO_CHILD_CARTESIAN_OR_FINE_PATH_ENUMERATION = PASS")


def tamper_self_test(manifest: dict, artifact: dict, expected: dict) -> None:
    attacks = []

    def add(name: str, mutation) -> None:
        candidate = copy.deepcopy(artifact)
        mutation(candidate)
        candidate["semantic_digest"] = hash_value(candidate["proof_payload"])
        attacks.append((name, candidate))

    add("source_manifest_substitution", lambda a: a["proof_payload"]["source"].__setitem__("integrated_manifest_digest", "0" * 64))
    add("left_inventory_deletion", lambda a: a["proof_payload"]["child_normal_forms"].__setitem__("left_entry_count", 9107))
    add("parent_boundary_substitution", lambda a: a["proof_payload"]["geometry"].__setitem__("parent_boundary", [4, 2]))
    add("join_correction_tamper", lambda a: a["proof_payload"]["geometry"].__setitem__("join_lambda_correction_identically_zero", False))
    add("shrink_correction_tamper", lambda a: a["proof_payload"]["geometry"]["shrink_correction_counts_over_quotient_cells"].__setitem__("1", 0))
    add("quotient_path_deletion", lambda a: a["proof_payload"]["quotient_frontier"].__setitem__("pre_shrink_quotient_path_count", 74))
    add("fake_sixty_second_class", lambda a: a["proof_payload"]["quotient_frontier"]["classes"].append(copy.deepcopy(a["proof_payload"]["quotient_frontier"]["classes"][0])))
    add("zero_envelope_value_tamper", lambda a: a["proof_payload"]["quotient_frontier"]["classes"][0]["canonical_generator"][0].__setitem__("value", 1))
    add("closure_only_witness", lambda a: a["proof_payload"]["quotient_frontier"].__setitem__("direct_witness_kind", "TRANSITIVE_CLOSURE"))
    add("false_root_claim", lambda a: a["proof_payload"]["strict_boundary"].__setitem__("negative_root_reached", True))

    rejected = 0
    for name, candidate in attacks:
        try:
            reject_if_invalid(manifest, candidate, expected)
        except AssertionError:
            rejected += 1
        else:
            raise AssertionError(f"tamper accepted: {name}")
    if rejected != 10:
        raise AssertionError("tamper rejection count")
    print("TAMPER_ATTACKS_REJECTED = 10/10")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--producer-source", type=Path, required=True)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()

    if hash_file(args.manifest) != EXPECTED_MANIFEST_FILE_SHA256:
        raise AssertionError("manifest file sha")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    artifact = json.loads(args.artifact.read_text(encoding="utf-8"))
    original = independent_payload(manifest, "original")
    reversed_payload = independent_payload(manifest, "reversed")
    shuffled = independent_payload(manifest, "seeded-shuffle")
    if original != reversed_payload or original != shuffled:
        raise AssertionError("input-order replay drift")
    reject_if_invalid(manifest, artifact, original)
    verify_source_no_cartesian(args.producer_source)
    if args.tamper_self_test:
        tamper_self_test(manifest, artifact, original)
    print("JANUS_C049_1_B4_6_3_NODE8_FRONTIER_COMPRESSION_VERIFIER = PASS")
    print("INVARIANTS = 10/10")
    print("PRE_SHRINK_QUOTIENT_PATHS = 75")
    print("POST_SHRINK_CLASSES = 61")
    print("LOCAL_DIRECT_WITNESS_ASSIGNMENTS = 31500")
    print("ADMIT_NODE8_FRONTIER_COMPRESSION = TRUE")


if __name__ == "__main__":
    main()
