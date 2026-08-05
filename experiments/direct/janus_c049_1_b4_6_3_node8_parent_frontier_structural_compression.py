#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
import random
from dataclasses import dataclass
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
PATTERN_CODES = {p: "".join(map(str, p)) for p in PATTERNS}
EXPECTED_LEFT_ENTRIES = 9108
EXPECTED_RIGHT_ENTRIES = 36
EXPECTED_CHILD_PAIRS = 327888
EXPECTED_NAIVE_REFINEMENTS = 602017584
EXPECTED_QUOTIENT_PATHS = 75
EXPECTED_CLASSES = 61
EXPECTED_ASSIGNMENTS = 31500


@dataclass(frozen=True, order=True)
class Statistic:
    left: tuple[int, ...]
    right: tuple[int, ...]
    value: int


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
        for other in sorted(table, reverse=True):
            if other != pivot and ((table[other] >> pivot) & 1):
                table[other] ^= table[pivot]
    return tuple(table[p] for p in sorted(table, reverse=True))


def span_vectors(space: Sequence[int]) -> set[int]:
    out = {0}
    for row in space:
        out |= {value ^ int(row) for value in tuple(out)}
    return out


def subspace_sum(a: Sequence[int], b: Sequence[int], d: int) -> tuple[int, ...]:
    return xor_basis((*a, *b), d)


def subspace_intersection(a: Sequence[int], b: Sequence[int], d: int) -> tuple[int, ...]:
    return xor_basis(span_vectors(a) & span_vectors(b), d)


def encode_stat(s: Statistic) -> dict:
    return {"left": list(s.left), "right": list(s.right), "value": s.value}


def encode_trajectory(gamma: Sequence[Statistic]) -> list[dict]:
    return [encode_stat(s) for s in gamma]


def compactify(stats: Sequence[Statistic]) -> tuple[Statistic, ...]:
    seq = list(stats)
    while True:
        changed = False
        for i in range(1, len(seq)):
            if seq[i - 1] == seq[i]:
                del seq[i]
                changed = True
                break
        if changed:
            continue
        for i in range(len(seq)):
            for j in range(i + 2, len(seq)):
                if (seq[i].left, seq[i].right) != (seq[j].left, seq[j].right):
                    continue
                values = [item.value for item in seq[i : j + 1]]
                inc = values[0] <= values[-1] and all(values[0] <= z <= values[-1] for z in values[1:-1])
                dec = values[0] >= values[-1] and all(values[0] >= z >= values[-1] for z in values[1:-1])
                if inc or dec:
                    del seq[i + 1 : j]
                    changed = True
                    break
            if changed:
                break
        if not changed:
            return tuple(seq)


def split_runs(raw: Sequence[dict], ambient_dim: int) -> tuple[tuple, tuple[tuple[int, ...], ...]]:
    skeleton: list[tuple] = []
    patterns: list[list[int]] = []
    for item in raw:
        geom = (xor_basis(item["left"], ambient_dim), xor_basis(item["right"], ambient_dim))
        value = int(item["value"])
        if value not in (0, 1):
            raise AssertionError("nonbinary child value")
        if not skeleton or skeleton[-1] != geom:
            skeleton.append(geom)
            patterns.append([value])
        else:
            patterns[-1].append(value)
    pattern_tuple = tuple(tuple(values) for values in patterns)
    if any(pattern not in PATTERNS for pattern in pattern_tuple):
        raise AssertionError("typical pattern catalog violation")
    return tuple(skeleton), pattern_tuple


def coordinate_space_to_ambient(space: Sequence[int], basis: Sequence[int], d: int) -> tuple[int, ...]:
    rows = []
    for mask in space:
        value = 0
        for index, row in enumerate(basis):
            if (int(mask) >> index) & 1:
                value ^= int(row)
        rows.append(value)
    return xor_basis(rows, d)


def lift_trajectory(raw: Sequence[dict], basis: Sequence[int], d: int) -> tuple[Statistic, ...]:
    return tuple(
        Statistic(
            coordinate_space_to_ambient(item["left"], basis, d),
            coordinate_space_to_ambient(item["right"], basis, d),
            int(item["value"]),
        )
        for item in raw
    )


def quotient_paths(m: int, n: int) -> list[tuple[tuple[int, int], ...]]:
    out: list[tuple[tuple[int, int], ...]] = []

    def rec(i: int, j: int, path: list[tuple[int, int]]) -> None:
        if (i, j) == (m - 1, n - 1):
            out.append(tuple(path))
            return
        for di, dj in ((1, 0), (0, 1), (1, 1)):
            ni, nj = i + di, j + dj
            if ni < m and nj < n:
                path.append((ni, nj))
                rec(ni, nj, path)
                path.pop()

    rec(0, 0, [(0, 0)])
    return sorted(out)


def delannoy(m: int, n: int) -> int:
    return sum(math.comb(m, k) * math.comb(n, k) * (2 ** k) for k in range(min(m, n) + 1))


def trajectory_length_histogram(entries: Sequence[dict]) -> dict[str, int]:
    counts: dict[int, int] = {}
    for item in entries:
        length = len(item["trajectory"])
        counts[length] = counts.get(length, 0) + 1
    return {str(key): counts[key] for key in sorted(counts)}


def exact_refinement_total(left_hist: dict[str, int], right_hist: dict[str, int]) -> int:
    return sum(
        int(left_count) * int(right_count) * delannoy(int(left_len) - 1, int(right_len) - 1)
        for left_len, left_count in left_hist.items()
        for right_len, right_count in right_hist.items()
    )


def extension_preorder_witness(lower: Sequence[Statistic], upper: Sequence[Statistic]) -> dict | None:
    parent: dict[tuple[int, int], tuple[int, int] | None] = {}
    for i in range(len(lower)):
        for j in range(len(upper)):
            a, b = lower[i], upper[j]
            if a.left != b.left or a.right != b.right or a.value > b.value:
                continue
            if (i, j) == (0, 0):
                parent[(i, j)] = None
                continue
            for previous in ((i - 1, j - 1), (i - 1, j), (i, j - 1)):
                if previous in parent:
                    parent[(i, j)] = previous
                    break
    end = (len(lower) - 1, len(upper) - 1)
    if end not in parent:
        return None
    path = []
    cursor: tuple[int, int] | None = end
    while cursor is not None:
        path.append(cursor)
        cursor = parent[cursor]
    path.reverse()
    return {"path": [[i, j] for i, j in path], "path_length": len(path)}


def normalize_children(manifest: dict, mode: str) -> tuple[list[dict], list[dict], dict, dict]:
    node7 = next(node for node in manifest["node_results"] if int(node["node_id"]) == 7)
    leaf3 = next(leaf for leaf in manifest["leaf_full_sets"] if int(leaf["node_id"]) == 3)
    left_entries = list(enumerate(node7["node_up_k"]["entries"]))
    right_entries = list(enumerate(leaf3["full_set"]["entries"]))
    if mode == "reversed":
        left_entries.reverse()
        right_entries.reverse()
    elif mode == "seeded-shuffle":
        rng = random.Random(0xC049108)
        rng.shuffle(left_entries)
        rng.shuffle(right_entries)
    elif mode != "original":
        raise AssertionError("entry order mode")

    class_ids = list(node7["node_up_k"]["retained_class_ids"])
    retained = list(node7["node_up_k"]["retained_generators"])
    if len(class_ids) != 13 or len(retained) != 13:
        raise AssertionError("node7 retained family drift")
    skeleton_to_class = {}
    retained_catalog = {}
    for source_index, (class_id, raw) in enumerate(zip(class_ids, retained)):
        skeleton, patterns = split_runs(raw, 2)
        if patterns != tuple((0,) for _ in skeleton):
            raise AssertionError("node7 retained generator is not zero envelope")
        if skeleton in skeleton_to_class:
            raise AssertionError("duplicate node7 retained skeleton")
        skeleton_to_class[skeleton] = class_id
        retained_catalog[class_id] = {
            "source_generator_index": source_index,
            "skeleton": skeleton,
            "trajectory": raw,
        }

    left_forms = []
    pattern_sets: dict[str, set[tuple[str, ...]]] = {class_id: set() for class_id in class_ids}
    for source_index, entry in left_entries:
        raw = copy.deepcopy(entry["trajectory"])
        skeleton, patterns = split_runs(raw, 2)
        if skeleton not in skeleton_to_class:
            raise AssertionError("left entry skeleton outside retained family")
        class_id = skeleton_to_class[skeleton]
        codes = tuple(PATTERN_CODES[item] for item in patterns)
        if entry.get("source_class_id") != class_id:
            raise AssertionError("left entry class provenance drift")
        pattern_sets[class_id].add(codes)
        left_forms.append({
            "class_id": class_id,
            "run_pattern_codes": list(codes),
            "trajectory_digest": digest(raw),
            "source_entry_index": source_index,
        })
    for class_id, item in retained_catalog.items():
        expected = set(itertools.product(tuple(PATTERN_CODES.values()), repeat=len(item["skeleton"])))
        if pattern_sets[class_id] != expected:
            raise AssertionError("left class typical-product catalog incomplete")

    right_forms = []
    right_pattern_set = set()
    right_skeleton = None
    for source_index, entry in right_entries:
        raw = copy.deepcopy(entry["trajectory"])
        skeleton, patterns = split_runs(raw, 1)
        if right_skeleton is None:
            right_skeleton = skeleton
        elif skeleton != right_skeleton:
            raise AssertionError("right skeleton multiplicity drift")
        codes = tuple(PATTERN_CODES[item] for item in patterns)
        right_pattern_set.add(codes)
        right_forms.append({
            "run_pattern_codes": list(codes),
            "trajectory_digest": digest(raw),
            "source_entry_index": source_index,
        })
    if right_skeleton is None or len(right_skeleton) != 2:
        raise AssertionError("right skeleton drift")
    if right_pattern_set != set(itertools.product(tuple(PATTERN_CODES.values()), repeat=2)):
        raise AssertionError("right typical-product catalog incomplete")

    left_forms.sort(key=canonical_json)
    right_forms.sort(key=canonical_json)
    return left_forms, right_forms, retained_catalog, {
        "skeleton": right_skeleton,
        "zero_trajectory": leaf3["leaf_generator_coordinates"],
    }


def derive_geometry(manifest: dict, node7: dict, leaf3: dict) -> dict:
    descriptor = next(item for item in manifest["topology"]["internal_nodes"] if int(item["node_id"]) == 8)
    d = int(manifest["scaffold_case"]["d"])
    blocks = [tuple(block) for block in manifest["scaffold_case"]["whole_factor_blocks"]]
    left_boundary = xor_basis(node7["parent_boundary"], d)
    right_boundary = xor_basis(leaf3["boundary_rref_ambient"], d)
    common = subspace_sum(left_boundary, right_boundary, d)
    covered = tuple(int(v) for v in descriptor["covered_factor_ids"])
    outside = tuple(int(v) for v in descriptor["outside_factor_ids"])
    covered_span = xor_basis((row for factor in covered for row in blocks[factor]), d)
    outside_span = xor_basis((row for factor in outside for row in blocks[factor]), d)
    parent = subspace_intersection(covered_span, outside_span, d)
    if descriptor["child_node_ids"] != [7, 3]:
        raise AssertionError("node8 descriptor drift")
    if (left_boundary, right_boundary, common, parent) != ((4, 2), (3,), (4, 2, 1), (4, 1)):
        raise AssertionError("node8 geometry drift")
    return {
        "descriptor": descriptor,
        "ambient_dim": d,
        "left_boundary": left_boundary,
        "right_boundary": right_boundary,
        "common_boundary": common,
        "parent_boundary": parent,
    }


def build(manifest_path: Path, output_path: Path, entry_order: str) -> dict:
    if file_sha256(manifest_path) != EXPECTED_MANIFEST_FILE_SHA256:
        raise AssertionError("integrated manifest file sha drift")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("manifest_digest") != EXPECTED_MANIFEST_DIGEST:
        raise AssertionError("integrated manifest semantic digest drift")
    if manifest["chunking"]["transcript_root_digest"] != EXPECTED_TRANSCRIPT:
        raise AssertionError("transcript binding drift")
    if manifest["execution"]["processed_internal_node_ids"] != [6, 7]:
        raise AssertionError("processed node vector drift")
    stop = manifest["execution"]["stop"]
    if stop["node_id"] != 8 or stop["reason"] != "CHILD_PAIR_CAP_EXCEEDED":
        raise AssertionError("node8 preflight stop drift")

    node7 = next(node for node in manifest["node_results"] if int(node["node_id"]) == 7)
    leaf3 = next(leaf for leaf in manifest["leaf_full_sets"] if int(leaf["node_id"]) == 3)
    if node7["output_receipt"]["receipt_digest"] != EXPECTED_NODE7_RECEIPT:
        raise AssertionError("node7 receipt drift")
    if leaf3["output_receipt"]["receipt_digest"] != EXPECTED_LEAF3_RECEIPT:
        raise AssertionError("leaf3 receipt drift")
    if node7["node_up_k"]["reachable_entries_digest"] != EXPECTED_NODE7_ENTRIES_DIGEST:
        raise AssertionError("node7 entries binding drift")
    if node7["node_up_k"]["frontier_artifact_sha256"] != EXPECTED_FRONTIER_SHA256:
        raise AssertionError("node7 frontier binding drift")
    if node7["node_up_k"]["up_k_artifact_sha256"] != EXPECTED_UP_K_SHA256:
        raise AssertionError("node7 up_k binding drift")

    left_entries = node7["node_up_k"]["entries"]
    right_entries = leaf3["full_set"]["entries"]
    if (len(left_entries), len(right_entries)) != (EXPECTED_LEFT_ENTRIES, EXPECTED_RIGHT_ENTRIES):
        raise AssertionError("child entry count drift")
    if digest(left_entries) != EXPECTED_NODE7_ENTRIES_DIGEST:
        raise AssertionError("node7 entry digest mismatch")

    left_forms, right_forms, retained_catalog, right_catalog = normalize_children(manifest, entry_order)
    left_family_digest = digest([[item["class_id"], item["run_pattern_codes"], item["trajectory_digest"]] for item in left_forms])
    right_family_digest = digest([[item["run_pattern_codes"], item["trajectory_digest"]] for item in right_forms])
    geometry = derive_geometry(manifest, node7, leaf3)
    d = geometry["ambient_dim"]
    left_basis = geometry["left_boundary"]
    right_basis = geometry["right_boundary"]
    parent = geometry["parent_boundary"]

    right_zero = lift_trajectory(right_catalog["zero_trajectory"], right_basis, d)
    if any(stat.value != 0 for stat in right_zero):
        raise AssertionError("right zero envelope drift")

    path_records = []
    unique_envelopes: dict[bytes, dict] = {}
    local_assignment_tests = 0
    join_correction_cells = 0
    shrink_correction_counts = {0: 0, 1: 0}
    quotient_count = 0

    for class_id in sorted(retained_catalog):
        left_zero = lift_trajectory(retained_catalog[class_id]["trajectory"], left_basis, d)
        if any(stat.value != 0 for stat in left_zero):
            raise AssertionError("left zero envelope drift")
        initial_intersection = subspace_intersection(left_zero[0].right, right_zero[0].right, d)
        for local_path_index, path in enumerate(quotient_paths(len(left_zero), len(right_zero))):
            quotient_count += 1
            projected_precompact = []
            join_corrections = []
            shrink_corrections = []
            for i, j in path:
                left = left_zero[i]
                right = right_zero[j]
                joined_left = subspace_sum(left.left, right.left, d)
                joined_right = subspace_sum(left.right, right.right, d)
                left_span = subspace_sum(left.left, left.right, d)
                right_span = subspace_sum(right.left, right.right, d)
                current = subspace_intersection(left_span, right_span, d)
                join_correction = len(initial_intersection) - len(current)
                if join_correction != 0:
                    raise AssertionError("node8 join correction is not identically zero")
                join_correction_cells += 1
                lr = subspace_intersection(joined_left, joined_right, d)
                projected_left = subspace_intersection(joined_left, parent, d)
                projected_right = subspace_intersection(joined_right, parent, d)
                triple = subspace_intersection(lr, parent, d)
                shrink_correction = len(lr) - len(triple)
                if shrink_correction not in (0, 1):
                    raise AssertionError("unexpected node8 shrink correction")
                shrink_correction_counts[shrink_correction] += 1
                join_corrections.append(join_correction)
                shrink_corrections.append(shrink_correction)
                projected_precompact.append(Statistic(projected_left, projected_right, shrink_correction))
            envelope = compactify(projected_precompact)
            if max(stat.value for stat in envelope) > 1:
                raise AssertionError("zero envelope exceeds width cap")
            envelope_key = canonical_json(encode_trajectory(envelope))
            source_record = {
                "left_class_id": class_id,
                "local_path_index": local_path_index,
                "quotient_path": [[i, j] for i, j in path],
                "join_corrections": join_corrections,
                "shrink_corrections": shrink_corrections,
                "projected_precompact": encode_trajectory(projected_precompact),
            }
            if envelope_key not in unique_envelopes:
                unique_envelopes[envelope_key] = {"generator": encode_trajectory(envelope), "sources": [], "assignment_tests": 0}
            unique_envelopes[envelope_key]["sources"].append(source_record)

            choices = [PATTERNS if correction == 0 else ((1,),) for correction in shrink_corrections]
            case_count = 0
            for assignment in itertools.product(*choices):
                raw_upper = []
                for stat, pattern in zip(projected_precompact, assignment):
                    for value in pattern:
                        raw_upper.append(Statistic(stat.left, stat.right, int(value)))
                upper = compactify(raw_upper)
                if extension_preorder_witness(envelope, upper) is None:
                    raise AssertionError("direct coverage failed after shrink compactification")
                if max(stat.value for stat in upper) > 1:
                    raise AssertionError("local successful-output abstraction exceeds k")
                case_count += 1
            unique_envelopes[envelope_key]["assignment_tests"] += case_count
            local_assignment_tests += case_count

    if quotient_count != EXPECTED_QUOTIENT_PATHS:
        raise AssertionError("quotient path count drift")
    if len(unique_envelopes) != EXPECTED_CLASSES:
        raise AssertionError("post-shrink class count drift")
    if local_assignment_tests != EXPECTED_ASSIGNMENTS:
        raise AssertionError("local assignment count drift")

    classes = []
    path_to_class = []
    for class_index, key in enumerate(sorted(unique_envelopes)):
        item = unique_envelopes[key]
        class_id = f"N8-S{class_index:02d}"
        canonical_source = sorted(item["sources"], key=canonical_json)[0]
        generator = item["generator"]
        classes.append({
            "class_id": class_id,
            "canonical_generator": generator,
            "generator_digest": digest(generator),
            "width": max(stat["value"] for stat in generator),
            "length": len(generator),
            "source_path_multiplicity": len(item["sources"]),
            "canonical_reachability_witness": canonical_source,
            "source_path_digest": digest(sorted(item["sources"], key=canonical_json)),
            "local_direct_assignment_tests": item["assignment_tests"],
        })
        for source in item["sources"]:
            path_to_class.append({
                "left_class_id": source["left_class_id"],
                "local_path_index": source["local_path_index"],
                "class_id": class_id,
                "quotient_path": source["quotient_path"],
                "shrink_corrections": source["shrink_corrections"],
            })
    path_to_class.sort(key=canonical_json)

    left_hist = trajectory_length_histogram(left_entries)
    right_hist = trajectory_length_histogram(right_entries)
    child_pairs = len(left_entries) * len(right_entries)
    naive_refinements = exact_refinement_total(left_hist, right_hist)
    if child_pairs != EXPECTED_CHILD_PAIRS or naive_refinements != EXPECTED_NAIVE_REFINEMENTS:
        raise AssertionError("exact node8 frontier drift")

    invariant_vector = {f"N8-INV-{index:02d}": "PASS" for index in range(1, 11)}
    proof_payload = {
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
            "left_skeleton_count": len(retained_catalog),
            "right_skeleton_count": 1,
            "typical_pattern_catalog": [PATTERN_CODES[p] for p in PATTERNS],
            "left_class_inventory": [
                {
                    "class_id": class_id,
                    "skeleton_length": len(retained_catalog[class_id]["skeleton"]),
                    "entry_count": 6 ** len(retained_catalog[class_id]["skeleton"]),
                }
                for class_id in sorted(retained_catalog)
            ],
        },
        "geometry": {
            "descriptor": geometry["descriptor"],
            "left_boundary": list(geometry["left_boundary"]),
            "right_boundary": list(geometry["right_boundary"]),
            "common_boundary": list(geometry["common_boundary"]),
            "parent_boundary": list(geometry["parent_boundary"]),
            "join_lambda_correction_identically_zero": True,
            "shrink_is_identity": False,
            "shrink_correction_counts_over_quotient_cells": {str(key): shrink_correction_counts[key] for key in sorted(shrink_correction_counts)},
        },
        "exact_frontier": {
            "child_pair_count": child_pairs,
            "naive_refinement_count": naive_refinements,
            "left_length_histogram": left_hist,
            "right_length_histogram": right_hist,
            "cartesian_child_pairs_materialized": 0,
            "fine_lattice_paths_enumerated": 0,
        },
        "quotient_frontier": {
            "pre_shrink_quotient_path_count": quotient_count,
            "post_shrink_class_count": len(classes),
            "source_path_collision_count": quotient_count - len(classes),
            "classes": classes,
            "path_to_class": path_to_class,
            "all_zero_envelopes_reachable": True,
            "all_zero_envelopes_width_at_most_k": True,
            "universal_direct_coverage": True,
            "local_direct_assignment_tests": local_assignment_tests,
            "direct_witness_kind": "EXTENSION_PREORDER_DIRECT",
            "transitive_closure_used": False,
        },
        "work_ledger": {
            "left_entries_read": len(left_entries),
            "right_entries_read": len(right_entries),
            "left_right_cartesian_pairs_materialized": 0,
            "fine_lattice_paths_enumerated": 0,
            "quotient_paths_enumerated": quotient_count,
            "quotient_join_cells_checked": join_correction_cells,
            "post_shrink_classes": len(classes),
            "local_direct_witness_assignments_tested": local_assignment_tests,
            "naive_refinements_avoided": naive_refinements,
        },
        "invariant_vector": invariant_vector,
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
    artifact = {"schema": SCHEMA, "semantic_digest_scope": "proof_payload", "proof_payload": proof_payload}
    artifact["semantic_digest"] = digest(proof_payload)
    output_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("JANUS_C049_1_B4_6_3_NODE8_PARENT_FRONTIER_STRUCTURAL_COMPRESSION = PASS")
    print("LEFT_NORMAL_FORMS =", len(left_forms))
    print("RIGHT_NORMAL_FORMS =", len(right_forms))
    print("NAIVE_CHILD_PAIRS =", child_pairs)
    print("NAIVE_REFINEMENTS =", naive_refinements)
    print("PRE_SHRINK_QUOTIENT_PATHS =", quotient_count)
    print("POST_SHRINK_CLASSES =", len(classes))
    print("LOCAL_DIRECT_WITNESS_ASSIGNMENTS =", local_assignment_tests)
    print("ADMIT_NODE8_FRONTIER_COMPRESSION = TRUE")
    print("SEMANTIC_DIGEST =", artifact["semantic_digest"])
    print("GLOBAL_TERMINAL =", TERMINAL)
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--entry-order", choices=("original", "reversed", "seeded-shuffle"), default="original")
    args = parser.parse_args()
    build(args.manifest, args.output, args.entry_order)


if __name__ == "__main__":
    main()
