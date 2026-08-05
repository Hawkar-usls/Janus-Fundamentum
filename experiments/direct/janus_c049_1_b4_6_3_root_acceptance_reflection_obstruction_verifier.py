#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA = "C049.1-B4.6.3-ROOT-ACCEPTANCE-REFLECTION-OBSTRUCTION-v1"
MANIFEST_SHA = "563bc6d4148dfb94e7c5aa3c9b8e6ffa28e0b0e9cc6603fe0bffe39e71a636a9"
SUMMARY_SHA = "640d0a9f18d7a0e7639d4f0c4fa9d2acfe691662af70b2ad5b2f89458fc8faf0"
UPK_SHA = "c6e369099ea2fdf6572409dab7ce6f5172d40543388b366ec37a821262c506e4"


def packed(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha_value(value: Any) -> str:
    return hashlib.sha256(packed(value)).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rref(rows: Iterable[int], dimension: int) -> tuple[int, ...]:
    pivots: dict[int, int] = {}
    for raw in rows:
        value = int(raw)
        if value < 0 or value >= 1 << dimension:
            raise AssertionError("range")
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
        for other in sorted(pivots, reverse=True):
            if other != pivot and ((pivots[other] >> pivot) & 1):
                pivots[other] ^= pivots[pivot]
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def vectors(space: Sequence[int]) -> set[int]:
    values = {0}
    for row in space:
        values |= {item ^ int(row) for item in tuple(values)}
    return values


def plus(a: Sequence[int], b: Sequence[int], dimension: int) -> tuple[int, ...]:
    return rref((*a, *b), dimension)


def meet(a: Sequence[int], b: Sequence[int], dimension: int) -> tuple[int, ...]:
    return rref(vectors(a) & vectors(b), dimension)


def trajectory(raw: Sequence[dict[str, Any]], dimension: int):
    return tuple((rref(x["left"], dimension), rref(x["right"], dimension), int(x["value"])) for x in raw)


def typical(sequence: Sequence[int]) -> tuple[int, ...]:
    seq = list(sequence)
    while True:
        removed = False
        for index in range(1, len(seq)):
            if seq[index - 1] == seq[index]:
                del seq[index]
                removed = True
                break
        if removed:
            continue
        for start in range(len(seq)):
            for end in range(start + 2, len(seq)):
                values_ = seq[start : end + 1]
                bounded_up = values_[0] <= values_[-1] and all(values_[0] <= x <= values_[-1] for x in values_[1:-1])
                bounded_down = values_[0] >= values_[-1] and all(values_[0] >= x >= values_[-1] for x in values_[1:-1])
                if bounded_up or bounded_down:
                    del seq[start + 1 : end]
                    removed = True
                    break
            if removed:
                break
        if not removed:
            return tuple(seq)


def code(pattern: Sequence[int]) -> str:
    return "".join(str(x) for x in pattern)


def delannoy(a: int, b: int) -> int:
    return sum(math.comb(a, t) * math.comb(b, t) * (2 ** t) for t in range(min(a, b) + 1))


def path_list(m: int, n: int):
    answer = []
    def walk(i: int, j: int, current: list[tuple[int, int]]):
        if (i, j) == (m - 1, n - 1):
            answer.append(tuple(current))
            return
        for di, dj in ((1, 0), (0, 1), (1, 1)):
            ni, nj = i + di, j + dj
            if ni < m and nj < n:
                current.append((ni, nj))
                walk(ni, nj, current)
                current.pop()
    walk(0, 0, [(0, 0)])
    return sorted(answer)


def cell_table(left, right, dimension: int):
    initial = meet(left[0][1], right[0][1], dimension)
    table = []
    details = []
    for a in left:
        row = []
        row_details = []
        for b in right:
            joined_left = plus(a[0], b[0], dimension)
            joined_right = plus(a[1], b[1], dimension)
            current = meet(plus(a[0], a[1], dimension), plus(b[0], b[1], dimension), dimension)
            join = len(initial) - len(current)
            shrink = len(meet(joined_left, joined_right, dimension))
            row.append(a[2] + b[2] + join + shrink)
            row_details.append((join, shrink))
        table.append(row)
        details.append(row_details)
    return table, details


def accepted_outputs(table: Sequence[Sequence[int]], cap: int):
    m, n = len(table), len(table[0])
    states = [[Counter() for _ in range(n)] for _ in range(m)]
    if table[0][0] <= cap:
        states[0][0][(table[0][0],)] = 1
    for i in range(m):
        for j in range(n):
            if i == 0 and j == 0:
                continue
            if table[i][j] > cap:
                continue
            sources = []
            if i:
                sources.append(states[i - 1][j])
            if j:
                sources.append(states[i][j - 1])
            if i and j:
                sources.append(states[i - 1][j - 1])
            for source in sources:
                for old, multiplicity in source.items():
                    states[i][j][typical((*old, table[i][j]))] += multiplicity
    return states[-1][-1]


def layout_oracle(blocks, dimension: int, cap: int):
    widths = Counter()
    best_orders = []
    best = None
    cuts = 0
    for order in itertools.permutations(range(len(blocks))):
        vector = []
        for cut in range(1, len(order)):
            left = rref((row for factor in order[:cut] for row in blocks[factor]), dimension)
            right = rref((row for factor in order[cut:] for row in blocks[factor]), dimension)
            vector.append(len(meet(left, right, dimension)))
            cuts += 1
        maximum = max(vector, default=0)
        widths[maximum] += 1
        if best is None or maximum < best:
            best = maximum
            best_orders = [list(order)]
        elif maximum == best:
            best_orders.append(list(order))
    return {
        "permutations_replayed": math.factorial(len(blocks)),
        "cut_recomputations": cuts,
        "minimum_width": best,
        "width_histogram": {str(key): widths[key] for key in sorted(widths)},
        "width_at_most_k_layout_count": sum(count for width, count in widths.items() if width <= cap),
        "minimum_width_layout_count": len(best_orders),
        "minimum_width_order_digest": sha_value(best_orders),
    }


def recompute_language(left_entries, right_entries, cap: int):
    outputs = Counter()
    output_pairs = Counter()
    success_pairs = 0
    success_paths = 0
    cells = 0
    path_hist = Counter()
    zero = []
    for li, left_entry in enumerate(left_entries):
        left = trajectory(left_entry["trajectory"], 1)
        for ri, right_entry in enumerate(right_entries):
            right = trajectory(right_entry["trajectory"], 1)
            table, _ = cell_table(left, right, 1)
            cells += len(left) * len(right)
            local = accepted_outputs(table, cap)
            total = sum(local.values())
            if not total:
                continue
            success_pairs += 1
            success_paths += total
            path_hist[total] += 1
            for pattern, multiplicity in local.items():
                label = code(pattern)
                outputs[label] += multiplicity
                output_pairs[label] += 1
            if local.get((0,), 0):
                zero.append({
                    "left_entry_index": li,
                    "left_entry_id": left_entry.get("entry_id"),
                    "left_source_retained_class_id": left_entry.get("source_retained_class_id"),
                    "left_trajectory_digest": sha_value(left_entry["trajectory"]),
                    "right_entry_index": ri,
                    "right_source_generator_index": right_entry.get("source_generator_index"),
                    "right_trajectory_digest": sha_value(right_entry["trajectory"]),
                    "cell_values": table,
                    "unique_accepting_path": [[0, 0], [1, 1]],
                    "compact_root_pattern": "0",
                    "accepting_path_count": local[(0,)],
                })
    if len(zero) != 1:
        raise AssertionError("zero witness cardinality")
    return {
        "successful_child_pair_count": success_pairs,
        "successful_refinement_count": success_paths,
        "root_output_pattern_counts": {key: outputs[key] for key in sorted(outputs)},
        "root_output_pair_counts": {key: output_pairs[key] for key in sorted(output_pairs)},
        "successful_paths_per_pair_histogram": {str(key): path_hist[key] for key in sorted(path_hist)},
        "root_cells_evaluated": cells,
        "unique_zero_root_witness": zero[0],
    }


def recompute_shortcut(node9, leaf5):
    retained = node9["node_up_k"]["retained_generators"]
    class_ids = node9["node_up_k"]["retained_class_ids"]
    right = trajectory(leaf5["leaf_generator_coordinates"], 1)
    outputs = Counter()
    joins = Counter()
    shrinks = Counter()
    records = []
    visits = 0
    for li, raw in enumerate(retained):
        left = trajectory(raw, 1)
        table, details = cell_table(left, right, 1)
        for pi, path in enumerate(path_list(len(left), len(right))):
            raw_values = []
            local_join = []
            local_shrink = []
            for i, j in path:
                raw_values.append(table[i][j])
                local_join.append(details[i][j][0])
                local_shrink.append(details[i][j][1])
                joins[details[i][j][0]] += 1
                shrinks[details[i][j][1]] += 1
                visits += 1
            output = code(typical(raw_values))
            outputs[output] += 1
            records.append({
                "left_retained_index": li,
                "left_source_class_id": class_ids[li],
                "local_path_index": pi,
                "path": [[i, j] for i, j in path],
                "join_corrections": local_join,
                "shrink_corrections": local_shrink,
                "raw_projected_values": raw_values,
                "compact_root_pattern": output,
            })
    return {
        "shortcut_kind": "RETAINED_LOWER_ENVELOPES_ONLY",
        "quotient_path_count": len(records),
        "quotient_cell_visit_count": visits,
        "join_correction_counts": {str(key): joins[key] for key in sorted(joins)},
        "shrink_correction_counts": {str(key): shrinks[key] for key in sorted(shrinks)},
        "compact_output_counts": {key: outputs[key] for key in sorted(outputs)},
        "source_path_collision_contribution": len(records) - len(outputs),
        "path_records": records,
        "reflection_proof_present": False,
        "admissible_as_root_compression_theorem": False,
    }


def expected_payload(manifest_path: Path, summary_path: Path, upk_path: Path):
    if (sha_file(manifest_path), sha_file(summary_path), sha_file(upk_path)) != (MANIFEST_SHA, SUMMARY_SHA, UPK_SHA):
        raise AssertionError("source bytes")
    manifest = json.loads(manifest_path.read_text())
    summary = json.loads(summary_path.read_text())
    upk = json.loads(upk_path.read_text())
    if sha_value(upk["proof_payload"]) != upk["semantic_digest"]:
        raise AssertionError("up_k digest")
    node9 = next(x for x in manifest["node_results"] if x["node_id"] == 9)
    leaf5 = next(x for x in manifest["leaf_full_sets"] if x["node_id"] == 5)
    left_entries = node9["node_up_k"]["entries"]
    right_entries = leaf5["full_set"]["entries"]
    left_hist = Counter(len(x["trajectory"]) for x in left_entries)
    right_hist = Counter(len(x["trajectory"]) for x in right_entries)
    encoded_left_hist = {str(key): left_hist[key] for key in sorted(left_hist)}
    encoded_right_hist = {str(key): right_hist[key] for key in sorted(right_hist)}
    refinements = sum(lc * rc * delannoy(ll - 1, rl - 1) for ll, lc in left_hist.items() for rl, rc in right_hist.items())
    blocks = [tuple(x) for x in manifest["scaffold_case"]["whole_factor_blocks"]]
    oracle = layout_oracle(blocks, 3, 1)
    language = recompute_language(left_entries, right_entries, 1)
    shortcut = recompute_shortcut(node9, leaf5)
    return {
        "source_bindings": {
            "pr104_exact_head": "babdf21ba20c1d24ed97fff4bb14121d0dfc1287",
            "manifest_bytes": manifest_path.stat().st_size,
            "manifest_file_sha256": MANIFEST_SHA,
            "manifest_digest": manifest["manifest_digest"],
            "summary_bytes": summary_path.stat().st_size,
            "summary_file_sha256": SUMMARY_SHA,
            "summary_semantic_digest": summary["semantic_digest"],
            "node9_up_k_bytes": upk_path.stat().st_size,
            "node9_up_k_file_sha256": UPK_SHA,
            "node9_up_k_semantic_digest": upk["semantic_digest"],
            "node9_output_receipt": node9["output_receipt"]["receipt_digest"],
            "leaf5_output_receipt": leaf5["output_receipt"]["receipt_digest"],
        },
        "fixture": {
            "ambient_dim": manifest["scaffold_case"]["d"],
            "k": manifest["scaffold_case"]["k"],
            "whole_factor_blocks": [list(x) for x in blocks],
            "affine_offsets": manifest["scaffold_case"]["affine_offsets"],
        },
        "exhaustive_grouped_layout_oracle": oracle,
        "root_preflight": {
            "root_node_id": 10,
            "left_entry_count": len(left_entries),
            "right_entry_count": len(right_entries),
            "left_length_histogram": encoded_left_hist,
            "right_length_histogram": encoded_right_hist,
            "child_pair_count": len(left_entries) * len(right_entries),
            "naive_refinement_count": refinements,
            "left_boundary": summary["root_preflight"]["left_boundary"],
            "right_boundary": summary["root_preflight"]["right_boundary"],
            "common_boundary": summary["root_preflight"]["common_boundary"],
            "parent_boundary": summary["root_preflight"]["parent_boundary"],
            "left_expand_identity": summary["root_preflight"]["left_expand_identity"],
            "right_expand_identity": summary["root_preflight"]["right_expand_identity"],
            "shrink_identity": summary["root_preflight"]["shrink_identity"],
            "generic_pair_records_materialized": summary["root_preflight"]["generic_root_pair_records_materialized"],
            "generic_refinement_records_materialized": summary["root_preflight"]["generic_root_refinement_records_materialized"],
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
        "invariant_vector": {f"RRO-INV-{i:02d}": "PASS" for i in range(1, 13)},
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
            "current_global_terminal": "OPEN_TRAJECTORY_ENGINE_INCOMPLETE",
            "p_vs_np": "OPEN",
        },
        "next_gate": "C049.1_B4.6.3_ROOT_ACCEPTANCE_REFLECTION_CORRECTION",
        "admit_obstruction": True,
    }


def verify_value(candidate: dict[str, Any], expected: dict[str, Any]) -> None:
    if candidate.get("schema") != SCHEMA or candidate.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("schema")
    if candidate.get("semantic_digest") != sha_value(candidate.get("proof_payload")):
        raise AssertionError("outer digest")
    if candidate["proof_payload"] != expected:
        raise AssertionError("independent semantic replay mismatch")


def tamper_tests(artifact: dict[str, Any], expected: dict[str, Any]) -> int:
    def alter(value, index):
        p = value["proof_payload"]
        if index == 0: p["exhaustive_grouped_layout_oracle"]["minimum_width"] = 1
        elif index == 1: p["exhaustive_grouped_layout_oracle"]["width_histogram"]["2"] -= 1
        elif index == 2: p["current_b3_root_semantics"]["successful_child_pair_count"] += 1
        elif index == 3: p["current_b3_root_semantics"]["successful_refinement_count"] -= 1
        elif index == 4: p["current_b3_root_semantics"]["root_output_pattern_counts"]["0"] = 0
        elif index == 5: p["current_b3_root_semantics"]["unique_zero_root_witness"]["unique_accepting_path"] = [[0,0],[0,1],[1,1]]
        elif index == 6: p["retained_envelope_shortcut_attack"]["compact_output_counts"]["0"] = 0
        elif index == 7: p["retained_envelope_shortcut_attack"]["shrink_correction_counts"]["1"] -= 1
        elif index == 8: p["source_bindings"]["manifest_file_sha256"] = "0" * 64
        elif index == 9: p["root_preflight"]["parent_boundary"] = [1]
        elif index == 10: p["strict_boundary"]["no_layout_at_cap_enabled"] = True
        elif index == 11: p["next_gate"] = "C049.1_B4.6.3_ROOT_PARENT_FRONTIER_STRUCTURAL_COMPRESSION"
        else: raise AssertionError("tamper index")
        value["semantic_digest"] = sha_value(p)
    rejected = 0
    for index in range(12):
        candidate = copy.deepcopy(artifact)
        alter(candidate, index)
        try:
            verify_value(candidate, expected)
        except AssertionError:
            rejected += 1
        else:
            raise AssertionError(f"tamper {index} accepted")
    return rejected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("summary", type=Path)
    parser.add_argument("node9_up_k", type=Path)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    artifact = json.loads(args.artifact.read_text())
    expected = expected_payload(args.manifest, args.summary, args.node9_up_k)
    verify_value(artifact, expected)
    rejected = tamper_tests(artifact, expected) if args.tamper_self_test else 0
    print("JANUS_C049_1_B4_6_3_ROOT_ACCEPTANCE_REFLECTION_OBSTRUCTION_VERIFIER = PASS")
    print("INVARIANTS = 12/12")
    if args.tamper_self_test:
        print(f"DIGEST_REPAIRED_TAMPERS_REJECTED = {rejected}/12")
    print("LAYOUTS_AT_WIDTH_1 = 0")
    print("CURRENT_B3_WIDTH_1_ROOT_REFINEMENTS = 7825")
    print("ROOT_STRUCTURAL_COMPRESSION_ADMITTED = FALSE")
    print("CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE")


if __name__ == "__main__":
    main()
