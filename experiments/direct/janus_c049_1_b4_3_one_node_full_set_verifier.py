#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import defaultdict
from typing import Any, Iterable, Sequence

import janus_c049_1_b2_full_transcript_verifier as b2v
import janus_c049_1_b3_expand_join_shrink_verifier as b3v


SCHEMA = "C049.1-B4.3-ONE-NODE-FULL-SET-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def trajectory_key(raw: Sequence[dict]) -> str:
    return canonical_json(raw).decode()


def span(blocks: Iterable[Sequence[int]], ambient_dim: int) -> tuple[int, ...]:
    return b3v.rref((row for block in blocks for row in block), ambient_dim)


def boundary(
    left: Sequence[Sequence[int]], right: Sequence[Sequence[int]], ambient_dim: int
) -> tuple[int, ...]:
    return b3v.inter(span(left, ambient_dim), span(right, ambient_dim), ambient_dim)


def independent_compactification(
    raw: Sequence[dict], boundary_basis: Sequence[int], ambient_dim: int
) -> tuple[list[dict], list[dict]]:
    sequence = list(b3v.parse(raw, boundary_basis, ambient_dim, False))
    trace: list[dict] = []
    while True:
        changed = False
        for index in range(1, len(sequence)):
            if sequence[index - 1] != sequence[index]:
                continue
            before = len(sequence)
            removed = [b3v.enc(sequence[index])]
            del sequence[index]
            trace.append(
                {
                    "rule": "duplicate",
                    "start": index - 1,
                    "end": index,
                    "removed": removed,
                    "before_length": before,
                    "after_length": len(sequence),
                }
            )
            changed = True
            break
        if changed:
            continue
        for start in range(len(sequence)):
            for end in range(start + 2, len(sequence)):
                if (
                    sequence[start].l,
                    sequence[start].r,
                ) != (
                    sequence[end].l,
                    sequence[end].r,
                ):
                    continue
                values = [item.v for item in sequence[start : end + 1]]
                increasing = values[0] <= values[-1] and all(
                    values[0] <= value <= values[-1]
                    for value in values[1:-1]
                )
                decreasing = values[0] >= values[-1] and all(
                    values[0] >= value >= values[-1]
                    for value in values[1:-1]
                )
                if not increasing and not decreasing:
                    continue
                before = len(sequence)
                removed = [b3v.enc(item) for item in sequence[start + 1 : end]]
                del sequence[start + 1 : end]
                trace.append(
                    {
                        "rule": "interval",
                        "start": start,
                        "end": end,
                        "removed": removed,
                        "before_length": before,
                        "after_length": len(sequence),
                    }
                )
                changed = True
                break
            if changed:
                break
        if not changed:
            return b3v.encg(sequence), trace


def compaction_removed(trace: Sequence[dict]) -> int:
    return sum(len(step["removed"]) for step in trace)


def expected_refinement_work(join_receipt: dict, shrink_receipt: dict) -> dict:
    join_trace = join_receipt["compactification_trace"]
    shrink_trace = shrink_receipt["compactification_trace"]
    return {
        "lattice_path_trials": 1,
        "join_stat_constructions": int(join_receipt["raw_length"]),
        "join_intersection_corrections": len(join_receipt["stat_receipts"]),
        "join_compaction_steps": len(join_trace),
        "join_compaction_removed_statistics": compaction_removed(join_trace),
        "shrink_projection_statistics": len(shrink_receipt["projection_receipts"]),
        "shrink_compaction_steps": len(shrink_trace),
        "shrink_compaction_removed_statistics": compaction_removed(shrink_trace),
        "width_tests": 1,
    }


def verify_b2_closure(closure: dict, expected_ledger_totals: tuple[int, int]) -> None:
    expected = b2v.expected_closure(closure)
    for field in (
        "retained_generators",
        "removals",
        "universe_size",
        "entries",
        "entry_count",
    ):
        if closure[field] != expected[field]:
            raise AssertionError(f"B2 closure mismatch: {field}")
    ledger = closure["ledger"]
    if any(not isinstance(value, int) or value < 0 for value in ledger.values()):
        raise AssertionError("invalid B2 ledger")
    if (ledger.get("discovery_work"), ledger.get("work")) != expected_ledger_totals:
        raise AssertionError("B2 ledger total drift")


def verify_scaffold(artifact: dict) -> tuple[int, list[tuple[int, ...]]]:
    scaffold = artifact["scaffold_case"]
    scaffold_body = {
        key: value for key, value in scaffold.items() if key != "semantic_digest"
    }
    if scaffold.get("semantic_digest") != digest(scaffold_body):
        raise AssertionError("scaffold semantic digest mismatch")
    ambient = int(scaffold["d"])
    if int(scaffold["k"]) != 1:
        raise AssertionError("wrong scaffold width cap")
    blocks = [b3v.rref(block, ambient) for block in scaffold["whole_factor_blocks"]]
    order = tuple(int(index) for index in scaffold["scaffold_order"])
    if blocks != [(1,), (2,), (4,)] or order != (1, 0, 2):
        raise AssertionError("wrong B4.2 scaffold case")
    work = 0
    expected_edges = []
    for cut in range(1, len(order)):
        left = [blocks[index] for index in order[:cut]]
        right = [blocks[index] for index in order[cut:]]
        cut_boundary = boundary(left, right, ambient)
        work += sum(len(block) for block in left + right) + len(cut_boundary) + 1
        expected_edges.append(
            {
                "edge_index": cut - 1,
                "left_leaf_ids": list(order[:cut]),
                "right_leaf_ids": list(order[cut:]),
                "boundary_rref": list(cut_boundary),
                "width": len(cut_boundary),
                "cumulative_work": work,
            }
        )
    if scaffold["candidate_edges"] != expected_edges:
        raise AssertionError("scaffold edge replay mismatch")
    if scaffold["charged_work"] != work:
        raise AssertionError("scaffold work mismatch")
    if scaffold["next_terminal"] != TERMINAL:
        raise AssertionError("scaffold terminal drift")
    return ambient, blocks


def verify_artifact(artifact: dict) -> None:
    body = dict(artifact)
    claimed_digest = body.pop("artifact_digest", None)
    if claimed_digest != digest(body):
        raise AssertionError("artifact digest mismatch")
    if artifact.get("schema") != SCHEMA:
        raise AssertionError("schema mismatch")

    ambient, blocks = verify_scaffold(artifact)
    node = artifact["node"]
    if node["node_id"] != 3 or node["kind"] != "SPINE_INTERNAL_JOIN":
        raise AssertionError("wrong internal node")
    if node["covered_factor_ids"] != [1, 0] or node["outside_factor_ids"] != [2]:
        raise AssertionError("node factor ownership mismatch")
    if [b3v.rref(block, ambient) for block in node["whole_factor_blocks"]] != blocks:
        raise AssertionError("grouped partition content mismatch")
    if not node["grouped_partition_preserved"] or len(blocks) != 3:
        raise AssertionError("grouped partition lost")
    if node["affine_offsets"] != artifact["scaffold_case"]["affine_offsets"]:
        raise AssertionError("affine offsets lost")
    if node["covered_affine_offsets"] != [1, 0]:
        raise AssertionError("covered offsets mismatch")

    expected_child_boundaries = {
        child: boundary(
            [blocks[child]],
            [blocks[index] for index in range(len(blocks)) if index != child],
            ambient,
        )
        for child in (1, 0)
    }
    expected_common = b3v.rref(
        (*expected_child_boundaries[1], *expected_child_boundaries[0]), ambient
    )
    expected_parent = boundary([blocks[1], blocks[0]], [blocks[2]], ambient)
    if node["child_boundaries"] != {
        str(key): list(value) for key, value in expected_child_boundaries.items()
    }:
        raise AssertionError("child boundary mismatch")
    if node["common_join_boundary"] != list(expected_common):
        raise AssertionError("common boundary mismatch")
    if node["parent_boundary"] != list(expected_parent):
        raise AssertionError("parent boundary mismatch")
    if expected_common or expected_parent or node["width_cap"] != 1:
        raise AssertionError("bounded node fixture drift")

    leaves = artifact["child_full_sets"]
    if [leaf["factor_id"] for leaf in leaves] != [1, 0]:
        raise AssertionError("leaf order mismatch")
    for leaf in leaves:
        if leaf["boundary_rref"] != []:
            raise AssertionError("leaf boundary mismatch")
        if leaf["leaf_generator"] != [{"left": [], "right": [], "value": 0}]:
            raise AssertionError("leaf generator mismatch")
        if leaf["provenance"]["factor_id"] != leaf["factor_id"]:
            raise AssertionError("leaf provenance mismatch")
        verify_b2_closure(leaf["full_set"], (29, 64))
        if leaf["full_set"]["entry_count"] != 6:
            raise AssertionError("leaf full-set cardinality mismatch")

    work_events_expected: list[dict] = []
    cumulative = 0

    def add_work(kind: str, reference: str, breakdown: dict[str, int]) -> None:
        nonlocal cumulative
        delta = sum(int(value) for value in breakdown.values())
        cumulative += delta
        work_events_expected.append(
            {
                "event_index": len(work_events_expected),
                "kind": kind,
                "reference": reference,
                "breakdown": dict(sorted(breakdown.items())),
                "work_delta": delta,
                "cumulative_work": cumulative,
            }
        )

    for leaf in leaves:
        ledger = leaf["full_set"]["ledger"]
        add_work(
            "CHILD_FULL_SET",
            f"factor:{leaf['factor_id']}",
            {
                "b2_discovery_work": ledger["discovery_work"],
                "b2_work": ledger["work"],
            },
        )

    attempts = artifact["refinement_attempts"]
    by_attempt_id = {item["attempt_id"]: item for item in attempts}
    if sorted(by_attempt_id) != list(range(len(attempts))):
        raise AssertionError("attempt IDs not contiguous")
    seen_attempt_ids: list[int] = []

    for pair_id, pair in enumerate(artifact["pairs"]):
        if pair["pair_id"] != pair_id:
            raise AssertionError("pair ID mismatch")
        left_entry = leaves[0]["full_set"]["entries"][pair["left_entry_index"]]
        right_entry = leaves[1]["full_set"]["entries"][pair["right_entry_index"]]
        left = b3v.parse(pair["left_input"], [], ambient, True)
        right = b3v.parse(pair["right_input"], [], ambient, True)
        if pair["left_input"] != left_entry["trajectory"]:
            raise AssertionError("left child provenance mismatch")
        if pair["right_input"] != right_entry["trajectory"]:
            raise AssertionError("right child provenance mismatch")

        for side, parsed in (("left", left), ("right", right)):
            expanded = pair[f"{side}_expand"]
            if expanded["output"] != b3v.encg(parsed):
                raise AssertionError("expand changed trajectory")
            transport = expanded["transport"]
            if transport != {
                "child_boundary": [],
                "parent_boundary": [],
                "child_basis_in_parent_coordinates": [],
            }:
                raise AssertionError("expand transport mismatch")

        expand_breakdown = {
            "pair_enumerations": 1,
            "expanded_statistics": len(left) + len(right),
            "boundary_coordinate_changes": 0,
        }
        if pair["expand_work_breakdown"] != dict(sorted(expand_breakdown.items())):
            raise AssertionError("expand work mismatch")
        add_work("PAIR_EXPAND", f"pair:{pair_id}", expand_breakdown)

        expected_paths = tuple(sorted(b3v.paths(len(left), len(right))))
        claimed_attempts = [by_attempt_id[index] for index in pair["attempt_ids"]]
        claimed_paths = tuple(
            sorted(tuple(tuple(cell) for cell in item["lattice_path"])
                   for item in claimed_attempts)
        )
        if claimed_paths != expected_paths:
            raise AssertionError("lattice-path coverage mismatch")
        if pair["lattice_path_count"] != len(expected_paths):
            raise AssertionError("lattice-path count mismatch")

        for attempt in claimed_attempts:
            if attempt["pair_id"] != pair_id:
                raise AssertionError("attempt attached to wrong pair")
            local_body = dict(attempt)
            local_digest = local_body.pop("transcript_digest", None)
            if local_digest != digest(local_body):
                raise AssertionError("attempt transcript digest mismatch")
            seen_attempt_ids.append(attempt["attempt_id"])

            expected_join = b3v.join(
                left, right, attempt["lattice_path"], [], ambient
            )
            for field in (
                "boundary",
                "path",
                "raw_join",
                "raw_length",
                "raw_width",
                "stat_receipts",
                "compact_join",
                "compact_length",
                "compact_width",
            ):
                if attempt["join"][field] != expected_join[field]:
                    raise AssertionError(f"B3 join mismatch: {field}")
            compact_join, join_trace = independent_compactification(
                attempt["join"]["raw_join"], [], ambient
            )
            if compact_join != attempt["join"]["compact_join"]:
                raise AssertionError("join compact output mismatch")
            if join_trace != attempt["join"]["compactification_trace"]:
                raise AssertionError("join compactification transcript mismatch")

            joined = b3v.parse(compact_join, [], ambient, True)
            projected, expected_shrink = b3v.projected(joined, [], ambient)
            for field in (
                "target_boundary",
                "projected_precompact",
                "projection_receipts",
                "output",
            ):
                if attempt["shrink"][field] != expected_shrink[field]:
                    raise AssertionError(f"B3 shrink mismatch: {field}")
            compact_shrink, shrink_trace = independent_compactification(
                attempt["shrink"]["projected_precompact"], [], ambient
            )
            if compact_shrink != attempt["shrink"]["output"]:
                raise AssertionError("shrink compact output mismatch")
            if shrink_trace != attempt["shrink"]["compactification_trace"]:
                raise AssertionError("shrink compactification transcript mismatch")
            if attempt["output"] != b3v.encg(projected):
                raise AssertionError("refinement output mismatch")

            output_width = max(stat.v for stat in projected)
            if attempt["output_width"] != output_width:
                raise AssertionError("output width mismatch")
            expected_status = "SUCCESS" if output_width <= 1 else "FAILED_WIDTH_CAP"
            if attempt["status"] != expected_status:
                raise AssertionError("refinement status mismatch")
            expected_reason = (
                None
                if expected_status == "SUCCESS"
                else f"output width {output_width} exceeds k=1"
            )
            if attempt["failure_reason"] != expected_reason:
                raise AssertionError("failed-refinement reason mismatch")

            breakdown = expected_refinement_work(
                attempt["join"], attempt["shrink"]
            )
            if attempt["work_breakdown"] != dict(sorted(breakdown.items())):
                raise AssertionError("refinement work mismatch")
            add_work("REFINEMENT", f"attempt:{attempt['attempt_id']}", breakdown)
            if attempt["cumulative_work"] != cumulative:
                raise AssertionError("attempt cumulative work mismatch")

    if sorted(seen_attempt_ids) != list(range(len(attempts))):
        raise AssertionError("attempt coverage mismatch")

    successful_groups: dict[str, list[int]] = defaultdict(list)
    for attempt in attempts:
        if attempt["status"] == "SUCCESS":
            successful_groups[trajectory_key(attempt["output"])].append(
                attempt["attempt_id"]
            )
    expected_generators = []
    expected_duplicates = []
    for key in sorted(successful_groups):
        raw = json.loads(key)
        ids = successful_groups[key]
        expected_generators.append(
            {
                "trajectory": raw,
                "provenance_attempt_ids": ids,
                "canonical_retained_attempt_id": ids[0],
            }
        )
        identity_path = [[index, index] for index in range(len(raw))]
        for removed_id in ids[1:]:
            expected_duplicates.append(
                {
                    "removed_attempt_id": removed_id,
                    "retained_attempt_id": ids[0],
                    "trajectory": raw,
                    "witness": {
                        "path": identity_path,
                        "path_length": len(identity_path),
                    },
                    "reason": "IDENTICAL_REFINEMENT_OUTPUT",
                }
            )
    if artifact["successful_output_generators"] != expected_generators:
        raise AssertionError("successful generator provenance mismatch")
    if artifact["duplicate_deletions"] != expected_duplicates:
        raise AssertionError("duplicate deletion transcript mismatch")

    node_closure = artifact["node_up_k"]
    verify_b2_closure(node_closure, (29, 503))
    final_ledger = node_closure["ledger"]
    add_work(
        "NODE_B2_UP_K",
        "node:3",
        {
            "b2_discovery_work": final_ledger["discovery_work"],
            "b2_work": final_ledger["work"],
        },
    )
    if artifact["work_events"] != work_events_expected:
        raise AssertionError("cumulative work ledger mismatch")
    if any(
        later["cumulative_work"] < earlier["cumulative_work"]
        for earlier, later in zip(work_events_expected, work_events_expected[1:])
    ):
        raise AssertionError("cumulative work decreased")

    provenance_by_key = {
        trajectory_key(item["trajectory"]): item["provenance_attempt_ids"]
        for item in expected_generators
    }
    expected_input_provenance = [
        {
            "trajectory": raw,
            "provenance_attempt_ids": provenance_by_key[trajectory_key(raw)],
        }
        for raw in node_closure["input_generators"]
    ]
    if artifact["input_generator_provenance"] != expected_input_provenance:
        raise AssertionError("input generator provenance mismatch")
    expected_retained_provenance = [
        {
            "retained_generator_index": index,
            "trajectory": raw,
            "provenance_attempt_ids": provenance_by_key[trajectory_key(raw)],
        }
        for index, raw in enumerate(node_closure["retained_generators"])
    ]
    if artifact["retained_generator_provenance"] != expected_retained_provenance:
        raise AssertionError("retained generator provenance mismatch")
    expected_entry_provenance = [
        {
            "entry_index": index,
            "source_generator_index": int(entry["source_generator_index"]),
            "source_provenance_attempt_ids": expected_retained_provenance[
                int(entry["source_generator_index"])
            ]["provenance_attempt_ids"],
        }
        for index, entry in enumerate(node_closure["entries"])
    ]
    if artifact["entry_provenance"] != expected_entry_provenance:
        raise AssertionError("full-set entry provenance mismatch")

    successful = sum(item["status"] == "SUCCESS" for item in attempts)
    failed = len(attempts) - successful
    audit = artifact["audit"]
    expected_audit = {
        "child_full_set_entries": [6, 6],
        "child_pairs_processed": 36,
        "lattice_paths_processed": len(attempts),
        "successful_refinements": successful,
        "failed_refinements": failed,
        "raw_precompact_join_statistics": sum(
            item["join"]["raw_length"] for item in attempts
        ),
        "unique_successful_generators": len(expected_generators),
        "duplicate_successful_outputs_deleted": len(expected_duplicates),
        "b2_dominance_deletions": len(node_closure["removals"]),
        "retained_generators": len(node_closure["retained_generators"]),
        "final_up_k_entries": node_closure["entry_count"],
        "cumulative_work": cumulative,
        "failures": 0,
    }
    if audit != expected_audit:
        raise AssertionError("frozen audit mismatch")
    if audit != {
        "child_full_set_entries": [6, 6],
        "child_pairs_processed": 36,
        "lattice_paths_processed": 124,
        "successful_refinements": 35,
        "failed_refinements": 89,
        "raw_precompact_join_statistics": 448,
        "unique_successful_generators": 6,
        "duplicate_successful_outputs_deleted": 29,
        "b2_dominance_deletions": 5,
        "retained_generators": 1,
        "final_up_k_entries": 6,
        "cumulative_work": 2584,
        "failures": 0,
    }:
        raise AssertionError("frozen audit constants drift")

    strict = artifact["strict_boundary"]
    if strict["scope"] != "one internal scaffold node only":
        raise AssertionError("scope drift")
    if strict["full_iterative_compression_cycle"] is not False:
        raise AssertionError("full-cycle overclaim")
    if strict["complete_branch_refinement"] is not False:
        raise AssertionError("complete-refinement overclaim")
    if strict["no_layout_at_cap_enabled"] is not False:
        raise AssertionError("NO_LAYOUT_AT_CAP enabled")
    if strict["empty_full_set_terminal"] != TERMINAL:
        raise AssertionError("empty-set terminal drift")
    if strict["current_global_terminal"] != TERMINAL:
        raise AssertionError("global terminal drift")
    if strict["p_vs_np"] != "OPEN":
        raise AssertionError("P/NP status drift")


def rebind(artifact: dict) -> None:
    artifact.pop("artifact_digest", None)
    artifact["artifact_digest"] = digest(artifact)


def tamper_self_test(artifact: dict) -> None:
    controls = []

    altered_raw = copy.deepcopy(artifact)
    altered_raw["refinement_attempts"][0]["join"]["raw_join"][0]["value"] += 1
    attempt = altered_raw["refinement_attempts"][0]
    attempt.pop("transcript_digest", None)
    attempt["transcript_digest"] = digest(attempt)
    rebind(altered_raw)
    controls.append(altered_raw)

    missing_failure = copy.deepcopy(artifact)
    failed_index = next(
        index
        for index, item in enumerate(missing_failure["refinement_attempts"])
        if item["status"] == "FAILED_WIDTH_CAP"
    )
    missing_failure["refinement_attempts"].pop(failed_index)
    rebind(missing_failure)
    controls.append(missing_failure)

    altered_deletion = copy.deepcopy(artifact)
    altered_deletion["node_up_k"]["removals"][0]["witness"]["path"][0] = [1, 1]
    rebind(altered_deletion)
    controls.append(altered_deletion)

    decreased_work = copy.deepcopy(artifact)
    decreased_work["work_events"][5]["cumulative_work"] -= 1
    rebind(decreased_work)
    controls.append(decreased_work)

    split_group = copy.deepcopy(artifact)
    split_group["node"]["whole_factor_blocks"] = [[1], [2], [2], [4]]
    rebind(split_group)
    controls.append(split_group)

    for control in controls:
        try:
            verify_artifact(control)
        except Exception:
            continue
        raise AssertionError("digest-repaired semantic tamper accepted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    with open(args.artifact, encoding="utf-8") as handle:
        artifact = json.load(handle)
    verify_artifact(artifact)
    if args.tamper_self_test:
        tamper_self_test(artifact)
    print("VERIFIED C049.1 B4.3 ONE INTERNAL NODE FULL SET")
    print("B3_REFINEMENTS_REPLAYED =", len(artifact["refinement_attempts"]))
    print("B2_FULL_SET_ENTRIES_REPLAYED =", artifact["node_up_k"]["entry_count"])
    print("TAMPER_CONTROLS =", 5 if args.tamper_self_test else 0)
    print("TERMINAL =", TERMINAL)


if __name__ == "__main__":
    main()
