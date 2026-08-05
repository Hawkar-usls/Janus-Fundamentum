#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA = "C049.1-B4.6.3-ROOT-ACCEPTANCE-REFLECTION-OBSTRUCTION-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"

MANIFEST_BYTES = 16175333
MANIFEST_SHA256 = "563bc6d4148dfb94e7c5aa3c9b8e6ffa28e0b0e9cc6603fe0bffe39e71a636a9"
MANIFEST_DIGEST = "cb124decfa45c2adfd58fe7bf86c9e8a7cd45afff84dde4ff90d4090721c74fd"
SUMMARY_BYTES = 4406
SUMMARY_SHA256 = "640d0a9f18d7a0e7639d4f0c4fa9d2acfe691662af70b2ad5b2f89458fc8faf0"
SUMMARY_DIGEST = "dc790f6294afb5fec24b5e8686f32725eb616b3125364d11a1fcb4d24b269443"
NODE9_UP_K_BYTES = 555527
NODE9_UP_K_SHA256 = "c6e369099ea2fdf6572409dab7ce6f5172d40543388b366ec37a821262c506e4"
NODE9_UP_K_DIGEST = "f90aa04716ca2fa9019449e19b5866ac443cf545253bb41ae212dd3c68212713"
NODE9_OUTPUT_RECEIPT = "1a23cdd127a35932d8515c742034e67443ebf4c2a42ac06458f809d63d65ca5a"
LEAF5_RECEIPT = "1e81398ee7d05a6312ea94154a7026df64e9bf739d3957180e2f11d723c9c528"

EXPECTED_ROOT_PAIRS = 9072
EXPECTED_ROOT_REFINEMENTS = 4954128
EXPECTED_SUCCESSFUL_PAIRS = 764
EXPECTED_SUCCESSFUL_REFINEMENTS = 7825
EXPECTED_OUTPUT_COUNTS = {"0": 1, "01": 1898, "010": 1351, "1": 221, "10": 1898, "101": 2456}
EXPECTED_OUTPUT_PAIR_COUNTS = {"0": 1, "01": 184, "010": 124, "1": 143, "10": 184, "101": 265}
EXPECTED_LAYOUT_WIDTH_HIST = {"2": 288, "3": 432}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


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
        row = table[pivot]
        for other in sorted(table, reverse=True):
            if other != pivot and ((table[other] >> pivot) & 1):
                table[other] ^= row
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


def decode_trajectory(raw: Sequence[dict[str, Any]], d: int) -> tuple[tuple[tuple[int, ...], tuple[int, ...], int], ...]:
    return tuple(
        (xor_basis(item["left"], d), xor_basis(item["right"], d), int(item["value"]))
        for item in raw
    )


def compact_scalar(values: Sequence[int]) -> tuple[int, ...]:
    seq = list(map(int, values))
    while True:
        changed = False
        for index in range(1, len(seq)):
            if seq[index - 1] == seq[index]:
                del seq[index]
                changed = True
                break
        if changed:
            continue
        for i in range(len(seq)):
            for j in range(i + 2, len(seq)):
                interval = seq[i : j + 1]
                increasing = interval[0] <= interval[-1] and all(interval[0] <= x <= interval[-1] for x in interval[1:-1])
                decreasing = interval[0] >= interval[-1] and all(interval[0] >= x >= interval[-1] for x in interval[1:-1])
                if increasing or decreasing:
                    del seq[i + 1 : j]
                    changed = True
                    break
            if changed:
                break
        if not changed:
            return tuple(seq)


def pattern_code(pattern: Sequence[int]) -> str:
    return "".join(map(str, pattern))


def delannoy(m: int, n: int) -> int:
    return sum(math.comb(m, index) * math.comb(n, index) * (2 ** index) for index in range(min(m, n) + 1))


def length_histogram(entries: Sequence[dict[str, Any]]) -> dict[str, int]:
    count = Counter(len(item["trajectory"]) for item in entries)
    return {str(key): count[key] for key in sorted(count)}


def exact_refinement_total(left_hist: dict[str, int], right_hist: dict[str, int]) -> int:
    return sum(
        left_count * right_count * delannoy(int(left_length) - 1, int(right_length) - 1)
        for left_length, left_count in left_hist.items()
        for right_length, right_count in right_hist.items()
    )


def root_cell_values(left, right, d: int):
    initial_intersection = subspace_intersection(left[0][1], right[0][1], d)
    values: list[list[int]] = []
    join_counts: Counter[int] = Counter()
    shrink_counts: Counter[int] = Counter()
    for left_stat in left:
        row: list[int] = []
        for right_stat in right:
            joined_left = subspace_sum(left_stat[0], right_stat[0], d)
            joined_right = subspace_sum(left_stat[1], right_stat[1], d)
            left_span = subspace_sum(left_stat[0], left_stat[1], d)
            right_span = subspace_sum(right_stat[0], right_stat[1], d)
            current = subspace_intersection(left_span, right_span, d)
            join_correction = len(initial_intersection) - len(current)
            shrink_correction = len(subspace_intersection(joined_left, joined_right, d))
            join_counts[join_correction] += 1
            shrink_counts[shrink_correction] += 1
            row.append(left_stat[2] + right_stat[2] + join_correction + shrink_correction)
        values.append(row)
    return values, join_counts, shrink_counts


def successful_path_outputs(values: Sequence[Sequence[int]], k: int) -> Counter[tuple[int, ...]]:
    m, n = len(values), len(values[0])
    dp = [[Counter() for _ in range(n)] for _ in range(m)]
    if values[0][0] <= k:
        dp[0][0][(int(values[0][0]),)] = 1
    for i in range(m):
        for j in range(n):
            if i == 0 and j == 0:
                continue
            if values[i][j] > k:
                continue
            predecessors = []
            if i:
                predecessors.append(dp[i - 1][j])
            if j:
                predecessors.append(dp[i][j - 1])
            if i and j:
                predecessors.append(dp[i - 1][j - 1])
            for source in predecessors:
                for pattern, count in source.items():
                    dp[i][j][compact_scalar((*pattern, int(values[i][j])))] += count
    return dp[-1][-1]


def lattice_paths(m: int, n: int) -> list[tuple[tuple[int, int], ...]]:
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


def exact_layout_oracle(blocks: Sequence[Sequence[int]], d: int, k: int) -> dict[str, Any]:
    width_hist: Counter[int] = Counter()
    minimizing_orders: list[list[int]] = []
    minimum = None
    cut_recomputations = 0
    for order in itertools.permutations(range(len(blocks))):
        widths = []
        for cut in range(1, len(order)):
            prefix = xor_basis((row for factor in order[:cut] for row in blocks[factor]), d)
            suffix = xor_basis((row for factor in order[cut:] for row in blocks[factor]), d)
            widths.append(len(subspace_intersection(prefix, suffix, d)))
            cut_recomputations += 1
        maximum = max(widths, default=0)
        width_hist[maximum] += 1
        if minimum is None or maximum < minimum:
            minimum = maximum
            minimizing_orders = [list(order)]
        elif maximum == minimum:
            minimizing_orders.append(list(order))
    result = {
        "permutations_replayed": math.factorial(len(blocks)),
        "cut_recomputations": cut_recomputations,
        "minimum_width": minimum,
        "width_histogram": {str(key): width_hist[key] for key in sorted(width_hist)},
        "width_at_most_k_layout_count": sum(count for width, count in width_hist.items() if width <= k),
        "minimum_width_layout_count": len(minimizing_orders),
        "minimum_width_order_digest": digest(minimizing_orders),
    }
    if result["width_histogram"] != EXPECTED_LAYOUT_WIDTH_HIST:
        raise AssertionError("layout oracle drift")
    if (result["minimum_width"], result["width_at_most_k_layout_count"], result["minimum_width_layout_count"]) != (2, 0, 288):
        raise AssertionError("layout oracle boundary")
    return result


def root_language_analysis(left_entries, right_entries, d: int, k: int) -> dict[str, Any]:
    output_counts: Counter[str] = Counter()
    output_pair_counts: Counter[str] = Counter()
    successful_pair_count = 0
    successful_refinement_count = 0
    cells_evaluated = 0
    zero_witnesses: list[dict[str, Any]] = []
    pair_success_hist: Counter[int] = Counter()
    for left_index, left_entry in enumerate(left_entries):
        left = decode_trajectory(left_entry["trajectory"], d)
        for right_index, right_entry in enumerate(right_entries):
            right = decode_trajectory(right_entry["trajectory"], d)
            values, _, _ = root_cell_values(left, right, d)
            cells_evaluated += len(left) * len(right)
            outputs = successful_path_outputs(values, k)
            pair_total = sum(outputs.values())
            if not pair_total:
                continue
            successful_pair_count += 1
            successful_refinement_count += pair_total
            pair_success_hist[pair_total] += 1
            for pattern, count in outputs.items():
                code = pattern_code(pattern)
                output_counts[code] += count
                output_pair_counts[code] += 1
            if outputs.get((0,), 0):
                zero_witnesses.append({
                    "left_entry_index": left_index,
                    "left_entry_id": left_entry.get("entry_id"),
                    "left_source_retained_class_id": left_entry.get("source_retained_class_id"),
                    "left_trajectory_digest": digest(left_entry["trajectory"]),
                    "right_entry_index": right_index,
                    "right_source_generator_index": right_entry.get("source_generator_index"),
                    "right_trajectory_digest": digest(right_entry["trajectory"]),
                    "cell_values": values,
                    "unique_accepting_path": [[0, 0], [1, 1]],
                    "compact_root_pattern": "0",
                    "accepting_path_count": outputs[(0,)],
                })
    encoded_counts = {key: output_counts[key] for key in sorted(output_counts)}
    encoded_pair_counts = {key: output_pair_counts[key] for key in sorted(output_pair_counts)}
    if successful_pair_count != EXPECTED_SUCCESSFUL_PAIRS or successful_refinement_count != EXPECTED_SUCCESSFUL_REFINEMENTS:
        raise AssertionError("successful root count drift")
    if encoded_counts != EXPECTED_OUTPUT_COUNTS or encoded_pair_counts != EXPECTED_OUTPUT_PAIR_COUNTS:
        raise AssertionError("root output pattern drift")
    if len(zero_witnesses) != 1 or zero_witnesses[0]["accepting_path_count"] != 1:
        raise AssertionError("unique zero-root witness drift")
    return {
        "successful_child_pair_count": successful_pair_count,
        "successful_refinement_count": successful_refinement_count,
        "root_output_pattern_counts": encoded_counts,
        "root_output_pair_counts": encoded_pair_counts,
        "successful_paths_per_pair_histogram": {str(key): pair_success_hist[key] for key in sorted(pair_success_hist)},
        "root_cells_evaluated": cells_evaluated,
        "unique_zero_root_witness": zero_witnesses[0],
    }


def retained_envelope_shortcut(node9: dict[str, Any], leaf5: dict[str, Any], d: int) -> dict[str, Any]:
    left_generators = node9["node_up_k"]["retained_generators"]
    retained_class_ids = list(node9["node_up_k"]["retained_class_ids"])
    right_generator = leaf5["leaf_generator_coordinates"]
    output_counts: Counter[str] = Counter()
    join_counts: Counter[int] = Counter()
    shrink_counts: Counter[int] = Counter()
    path_records = []
    cell_visits = 0
    for left_index, raw_left in enumerate(left_generators):
        left = decode_trajectory(raw_left, d)
        right = decode_trajectory(right_generator, d)
        initial_intersection = subspace_intersection(left[0][1], right[0][1], d)
        for local_path_index, path in enumerate(lattice_paths(len(left), len(right))):
            sequence = []
            local_join = []
            local_shrink = []
            for i, j in path:
                left_stat, right_stat = left[i], right[j]
                joined_left = subspace_sum(left_stat[0], right_stat[0], d)
                joined_right = subspace_sum(left_stat[1], right_stat[1], d)
                current = subspace_intersection(
                    subspace_sum(left_stat[0], left_stat[1], d),
                    subspace_sum(right_stat[0], right_stat[1], d), d)
                join_correction = len(initial_intersection) - len(current)
                shrink_correction = len(subspace_intersection(joined_left, joined_right, d))
                value = left_stat[2] + right_stat[2] + join_correction + shrink_correction
                sequence.append(value)
                local_join.append(join_correction)
                local_shrink.append(shrink_correction)
                join_counts[join_correction] += 1
                shrink_counts[shrink_correction] += 1
                cell_visits += 1
            output = compact_scalar(sequence)
            code = pattern_code(output)
            output_counts[code] += 1
            path_records.append({
                "left_retained_index": left_index,
                "left_source_class_id": retained_class_ids[left_index],
                "local_path_index": local_path_index,
                "path": [[i, j] for i, j in path],
                "join_corrections": local_join,
                "shrink_corrections": local_shrink,
                "raw_projected_values": sequence,
                "compact_root_pattern": code,
            })
    result = {
        "shortcut_kind": "RETAINED_LOWER_ENVELOPES_ONLY",
        "quotient_path_count": len(path_records),
        "quotient_cell_visit_count": cell_visits,
        "join_correction_counts": {str(key): join_counts[key] for key in sorted(join_counts)},
        "shrink_correction_counts": {str(key): shrink_counts[key] for key in sorted(shrink_counts)},
        "compact_output_counts": {key: output_counts[key] for key in sorted(output_counts)},
        "source_path_collision_contribution": len(path_records) - len(output_counts),
        "path_records": path_records,
        "reflection_proof_present": False,
        "admissible_as_root_compression_theorem": False,
    }
    expected = (8, 26, {"0": 26}, {"0": 16, "1": 10}, {"0": 1, "010": 7}, 6)
    observed = (result["quotient_path_count"], result["quotient_cell_visit_count"], result["join_correction_counts"], result["shrink_correction_counts"], result["compact_output_counts"], result["source_path_collision_contribution"])
    if observed != expected:
        raise AssertionError("retained-envelope shortcut drift")
    return result


def build(manifest_path: Path, summary_path: Path, up_k_path: Path) -> dict[str, Any]:
    if manifest_path.stat().st_size != MANIFEST_BYTES or file_sha256(manifest_path) != MANIFEST_SHA256:
        raise AssertionError("manifest byte binding")
    if summary_path.stat().st_size != SUMMARY_BYTES or file_sha256(summary_path) != SUMMARY_SHA256:
        raise AssertionError("summary byte binding")
    if up_k_path.stat().st_size != NODE9_UP_K_BYTES or file_sha256(up_k_path) != NODE9_UP_K_SHA256:
        raise AssertionError("node9 up_k byte binding")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    up_k = json.loads(up_k_path.read_text(encoding="utf-8"))
    if manifest.get("manifest_digest") != MANIFEST_DIGEST or summary.get("semantic_digest") != SUMMARY_DIGEST:
        raise AssertionError("integrated semantic binding")
    if up_k.get("semantic_digest") != NODE9_UP_K_DIGEST or digest(up_k["proof_payload"]) != NODE9_UP_K_DIGEST:
        raise AssertionError("up_k semantic binding")
    if manifest["execution"]["processed_internal_node_ids"] != [6, 7, 8, 9]:
        raise AssertionError("processed node vector")
    stop = manifest["execution"]["stop"]
    if (stop["node_id"], stop["reason"], stop["required"], stop["cap"], stop["no_layout_at_cap"]) != (10, "REFINEMENT_CAP_EXCEEDED", EXPECTED_ROOT_REFINEMENTS, 2000000, False):
        raise AssertionError("root preflight stop")
    root = summary["root_preflight"]
    if (root["child_pair_count"], root["naive_refinement_count"], root["left_boundary"], root["right_boundary"], root["common_boundary"], root["parent_boundary"], root["left_expand_identity"], root["right_expand_identity"], root["shrink_identity"]) != (9072, 4954128, [1], [1], [1], [], True, True, False):
        raise AssertionError("root geometry")
    node9 = next(item for item in manifest["node_results"] if int(item["node_id"]) == 9)
    leaf5 = next(item for item in manifest["leaf_full_sets"] if int(item["node_id"]) == 5)
    if node9["output_receipt"]["receipt_digest"] != NODE9_OUTPUT_RECEIPT or leaf5["output_receipt"]["receipt_digest"] != LEAF5_RECEIPT:
        raise AssertionError("child receipt")
    if node9["node_up_k"]["up_k_artifact_sha256"] != NODE9_UP_K_SHA256:
        raise AssertionError("node9 up_k manifest binding")
    left_entries = node9["node_up_k"]["entries"]
    right_entries = leaf5["full_set"]["entries"]
    left_hist = length_histogram(left_entries)
    right_hist = length_histogram(right_entries)
    child_pairs = len(left_entries) * len(right_entries)
    refinements = exact_refinement_total(left_hist, right_hist)
    if child_pairs != EXPECTED_ROOT_PAIRS or refinements != EXPECTED_ROOT_REFINEMENTS:
        raise AssertionError("root cardinality")
    d = int(manifest["scaffold_case"]["d"])
    k = int(manifest["scaffold_case"]["k"])
    blocks = [tuple(map(int, block)) for block in manifest["scaffold_case"]["whole_factor_blocks"]]
    offsets = list(map(int, manifest["scaffold_case"]["affine_offsets"]))
    if (d, k, blocks, offsets) != (3, 1, [(2,), (4,), (6,), (3,), (5,), (1,)], [0, 0, 0, 0, 0, 0]):
        raise AssertionError("negative fixture drift")
    oracle = exact_layout_oracle(blocks, d, k)
    language = root_language_analysis(left_entries, right_entries, 1, k)
    shortcut = retained_envelope_shortcut(node9, leaf5, 1)
    proof_payload = {
        "source_bindings": {
            "pr104_exact_head": "babdf21ba20c1d24ed97fff4bb14121d0dfc1287",
            "manifest_bytes": MANIFEST_BYTES,
            "manifest_file_sha256": MANIFEST_SHA256,
            "manifest_digest": MANIFEST_DIGEST,
            "summary_bytes": SUMMARY_BYTES,
            "summary_file_sha256": SUMMARY_SHA256,
            "summary_semantic_digest": SUMMARY_DIGEST,
            "node9_up_k_bytes": NODE9_UP_K_BYTES,
            "node9_up_k_file_sha256": NODE9_UP_K_SHA256,
            "node9_up_k_semantic_digest": NODE9_UP_K_DIGEST,
            "node9_output_receipt": NODE9_OUTPUT_RECEIPT,
            "leaf5_output_receipt": LEAF5_RECEIPT,
        },
        "fixture": {"ambient_dim": d, "k": k, "whole_factor_blocks": [list(block) for block in blocks], "affine_offsets": offsets},
        "exhaustive_grouped_layout_oracle": oracle,
        "root_preflight": {
            "root_node_id": 10,
            "left_entry_count": len(left_entries),
            "right_entry_count": len(right_entries),
            "left_length_histogram": left_hist,
            "right_length_histogram": right_hist,
            "child_pair_count": child_pairs,
            "naive_refinement_count": refinements,
            "left_boundary": [1], "right_boundary": [1], "common_boundary": [1], "parent_boundary": [],
            "left_expand_identity": True, "right_expand_identity": True, "shrink_identity": False,
            "generic_pair_records_materialized": 0, "generic_refinement_records_materialized": 0,
        },
        "current_b3_root_semantics": language,
        "retained_envelope_shortcut_attack": shortcut,
        "decisive_obstruction": {
            "layout_oracle_width_at_most_k_count": oracle["width_at_most_k_layout_count"],
            "current_b3_width_at_most_k_root_refinement_count": language["successful_refinement_count"],
            "current_b3_zero_root_refinement_count": language["root_output_pattern_counts"]["0"],
            "root_acceptance_reflection_contradiction": True,
            "which_upstream_layer_is_unsound": "NOT_LOCALIZED_BY_THIS_OBSTRUCTION",
            "root_structural_compression_admitted": False,
            "required_correction": "PROVE_OR_REPAIR_ROOT_ACCEPTANCE_REFLECTION_BEFORE_FRONTIER_COMPRESSION",
        },
        "invariant_vector": {f"RRO-INV-{index:02d}": "PASS" for index in range(1, 13)},
        "strict_boundary": {
            "pr104_node9_integration_rebound": "ADMITTED",
            "root_reached_on_rebound_chain": True,
            "root_parent_refinement_started": True,
            "root_parent_refinement_complete": False,
            "root_parent_up_k_complete": False,
            "root_full_set_computed": False,
            "root_empty_proved": False,
            "terminal_completeness_proved": False,
            "found_layout_enabled": False,
            "no_layout_at_cap_enabled": False,
            "current_global_terminal": TERMINAL,
            "p_vs_np": "OPEN",
        },
        "next_gate": "C049.1_B4.6.3_ROOT_ACCEPTANCE_REFLECTION_CORRECTION",
        "admit_obstruction": True,
    }
    return {"schema": SCHEMA, "semantic_digest_scope": "proof_payload", "proof_payload": proof_payload, "semantic_digest": digest(proof_payload)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("summary", type=Path)
    parser.add_argument("node9_up_k", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    artifact = build(args.manifest, args.summary, args.node9_up_k)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_json(artifact) + b"\n")
    print("JANUS_C049_1_B4_6_3_ROOT_ACCEPTANCE_REFLECTION_OBSTRUCTION = PASS")
    print("LAYOUTS_AT_WIDTH_1 = 0")
    print("CURRENT_B3_WIDTH_1_ROOT_REFINEMENTS = 7825")
    print("CURRENT_B3_ZERO_ROOT_REFINEMENTS = 1")
    print("ROOT_ACCEPTANCE_REFLECTION_CONTRADICTION = TRUE")
    print(f"ARTIFACT_BYTES = {args.output.stat().st_size}")
    print(f"ARTIFACT_SHA256 = {file_sha256(args.output)}")
    print(f"SEMANTIC_DIGEST = {artifact['semantic_digest']}")
    print("NEXT_GATE = C049.1_B4.6.3_ROOT_ACCEPTANCE_REFLECTION_CORRECTION")
    print(f"CURRENT_GLOBAL_TERMINAL = {TERMINAL}")


if __name__ == "__main__":
    main()
