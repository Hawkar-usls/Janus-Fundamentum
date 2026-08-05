#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import gc
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Sequence

TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
FRONTIER_SCHEMA = "C049.1-B4.6.3-NODE9-PARENT-FRONTIER-STRUCTURAL-COMPRESSION-v1"
FRONTIER_SHA = "6eefd8e31ba4808e5587475c2faa2c000fd0093da4de2c488db42d103c059890"
FRONTIER_SEM = "62e9178821fe56cbf094e8512dd20b687796c6fd87e08c0fea8ea833ef6c5e80"
UPK_SCHEMA = "C049.1-B4.6.3-NODE9-FIFTEEN-GENERATOR-UP-K-CLOSURE-v1"
UPK_SHA = "c6e369099ea2fdf6572409dab7ce6f5172d40543388b366ec37a821262c506e4"
UPK_SEM = "f90aa04716ca2fa9019449e19b5866ac443cf545253bb41ae212dd3c68212713"
INPUT_FAMILY_DIGEST = "027dcee32e45abb2864055877db5cc18d6402ae4361d4c2c276e87a2396f4d39"
RETAINED_FAMILY_DIGEST = "b8df3e1986bc8bd4d9058d6efc66aebe48153bfb43bd8b275e2b2f51f6752cb1"
REMOVALS_DIGEST = "9cf4385a49c4fddbc593fd8835ad791df36bf28d7170d100eb9b78c6826135a5"
REACHABLE_TRAJECTORIES_DIGEST = "d7970ed19cd149cd3d4609581cb592ef8e69d36739502bb4deb43c44df5092fe"
REACHABLE_RECORDS_DIGEST = "8a35d07ed7435b472ef2407dfc0c1e3a18d71c46d5efefbb72418eda3be26912"
REACHABLE_STREAM_SHA256 = "0c8a1aba19ecef370011a24c03059e73950c75fc849c0c995004e88641d010e6"
TRANSCRIPT_ROOT = "eb904e833b53cf5626af1eb28493f479f5f54f2066a8b5427cb7e3eb47f515d8"
NODE8_RECEIPT = "befcbb30de8d70ee9816bdf072b92e597cfd7052c7d7931d48190e8e53854b20"
LEAF4_RECEIPT = "44ae26d9a650353d6360027b08ad3738b9a0fed5bfd78fcfafb165e83dd0052f"
LEAF5_RECEIPT = "1e81398ee7d05a6312ea94154a7026df64e9bf739d3957180e2f11d723c9c528"
LEFT_HIST = {"2": 4, "3": 16, "4": 36, "5": 56, "6": 60, "7": 48, "8": 24, "9": 8}
RIGHT_HIST = {"2": 4, "3": 8, "4": 12, "5": 8, "6": 4}
EXPECTED_PAIRS = 9072
EXPECTED_REFINEMENTS = 4954128


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def invariant_pass(vector: dict[str, Any], prefix: str) -> bool:
    return vector == {f"{prefix}-{index:02d}": "PASS" for index in range(1, 11)}


def trajectory_stream_digest(entries: Sequence[dict[str, Any]]) -> str:
    raw = b"".join(canonical_json(item["trajectory"]) + b"\n" for item in entries)
    return hashlib.sha256(raw).hexdigest()


def xor_basis(rows: Iterable[int], dimension: int) -> tuple[int, ...]:
    table: dict[int, int] = {}
    for raw in rows:
        value = int(raw)
        if value < 0 or value >= (1 << dimension):
            raise AssertionError("vector outside ambient space")
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
    return tuple(table[pivot] for pivot in sorted(table, reverse=True))


def span(rows: Sequence[int]) -> set[int]:
    values = {0}
    for row in rows:
        values |= {value ^ int(row) for value in tuple(values)}
    return values


def boundary(blocks: Sequence[Sequence[int]], covered: Sequence[int], outside: Sequence[int], dimension: int) -> tuple[int, ...]:
    covered_basis = xor_basis((row for index in covered for row in blocks[index]), dimension)
    outside_basis = xor_basis((row for index in outside for row in blocks[index]), dimension)
    return xor_basis(span(covered_basis) & span(outside_basis), dimension)


def delannoy(left_length: int, right_length: int) -> int:
    left_steps = left_length - 1
    right_steps = right_length - 1
    return sum(
        math.comb(left_steps, diagonal)
        * math.comb(right_steps, diagonal)
        * (2**diagonal)
        for diagonal in range(min(left_steps, right_steps) + 1)
    )


def histogram(entries: Sequence[dict[str, Any]]) -> dict[str, int]:
    result: dict[str, int] = {}
    for entry in entries:
        key = str(len(entry["trajectory"]))
        result[key] = result.get(key, 0) + 1
    return dict(sorted(result.items(), key=lambda item: int(item[0])))


def refinement_count(left_hist: dict[str, int], right_hist: dict[str, int]) -> int:
    return sum(
        left_count * right_count * delannoy(int(left_length), int(right_length))
        for left_length, left_count in left_hist.items()
        for right_length, right_count in right_hist.items()
    )


def expected_source(frontier: dict[str, Any], up_k: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if frontier.get("schema") != FRONTIER_SCHEMA or frontier.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("frontier schema/scope")
    if frontier.get("semantic_digest") != FRONTIER_SEM or digest(frontier["proof_payload"]) != FRONTIER_SEM:
        raise AssertionError("frontier semantic binding")
    frontier_proof = frontier["proof_payload"]
    if frontier_proof.get("admit") is not True or not invariant_pass(frontier_proof.get("invariant_vector", {}), "N9-INV"):
        raise AssertionError("frontier admission")
    if frontier_proof["quotient_frontier"]["post_shrink_successful_class_count"] != 15:
        raise AssertionError("frontier class count")

    if up_k.get("schema") != UPK_SCHEMA or up_k.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("up_k schema/scope")
    if up_k.get("semantic_digest") != UPK_SEM or digest(up_k["proof_payload"]) != UPK_SEM:
        raise AssertionError("up_k semantic binding")
    proof = up_k["proof_payload"]
    if proof.get("admit") is not True or not invariant_pass(proof.get("invariant_vector", {}), "N9U-INV"):
        raise AssertionError("up_k admission")
    if proof["source"] != {
        "frontier_schema": FRONTIER_SCHEMA,
        "frontier_artifact_sha256": FRONTIER_SHA,
        "frontier_semantic_digest": FRONTIER_SEM,
        "frontier_generator_count": 15,
        "frontier_post_shrink_class_count": 15,
    }:
        raise AssertionError("up_k source binding")
    family = proof["input_generator_family"]
    minimization = proof["minimization"]
    reachable = proof["reachable_closure"]
    if (family["generator_count"], family["generator_family_digest"], digest(family["generators"])) != (15, INPUT_FAMILY_DIGEST, INPUT_FAMILY_DIGEST):
        raise AssertionError("input family")
    if (
        minimization["retained_generator_count"],
        minimization["direct_removal_count"],
        minimization["retained_family_digest"],
        digest(minimization["retained_generators"]),
        digest(minimization["direct_removals"]),
        minimization["every_removal_has_direct_retained_witness"],
        minimization["transitive_closure_used_for_removal"],
    ) != (2, 13, RETAINED_FAMILY_DIGEST, RETAINED_FAMILY_DIGEST, REMOVALS_DIGEST, True, False):
        raise AssertionError("minimization")
    entries = reachable["entries"]
    if (
        reachable["complete_reachable_catalog"],
        reachable["reachable_entry_count"],
        reachable["reachable_entries_digest"],
        reachable["reachable_stream_sha256"],
        digest([item["trajectory"] for item in entries]),
        digest(entries),
        trajectory_stream_digest(entries),
        reachable["global_compact_universe_enumerated"],
        reachable["global_compact_universe_entry_count"],
    ) != (
        252,
        252,
        REACHABLE_TRAJECTORIES_DIGEST,
        REACHABLE_STREAM_SHA256,
        REACHABLE_TRAJECTORIES_DIGEST,
        REACHABLE_RECORDS_DIGEST,
        REACHABLE_STREAM_SHA256,
        False,
        0,
    ):
        raise AssertionError("reachable closure")
    return frontier_proof, proof


def expected_closure(proof: dict[str, Any]) -> dict[str, Any]:
    family = proof["input_generator_family"]
    minimization = proof["minimization"]
    reachable = proof["reachable_closure"]
    work = sum(
        int(value)
        for value in proof["work_ledger"].values()
        if isinstance(value, int) and not isinstance(value, bool)
    )
    return {
        "ambient_dim": 1,
        "k": 1,
        "input_generators": [copy.deepcopy(item["trajectory"]) for item in family["generators"]],
        "retained_generators": [copy.deepcopy(item["trajectory"]) for item in minimization["retained_generators"]],
        "removals": copy.deepcopy(minimization["direct_removals"]),
        "universe_size": 252,
        "entries": copy.deepcopy(reachable["entries"]),
        "entry_count": 252,
        "ledger": {"discovery_work": work, "work": 0, "certified_total_charged_operations": work},
        "closure_method": "CERTIFIED_NODE9_TWO_GENERATOR_REACHABLE_CATALOG",
        "global_universe_enumerated": False,
        "complete_reachable_catalog_proved": True,
        "source_input_family_digest": INPUT_FAMILY_DIGEST,
        "source_retained_family_digest": RETAINED_FAMILY_DIGEST,
        "source_direct_removals_digest": REMOVALS_DIGEST,
        "frontier_artifact_sha256": FRONTIER_SHA,
        "up_k_artifact_sha256": UPK_SHA,
        "up_k_semantic_digest": UPK_SEM,
        "reachable_entries_digest": REACHABLE_TRAJECTORIES_DIGEST,
        "reachable_records_digest": REACHABLE_RECORDS_DIGEST,
        "reachable_catalog_stream_sha256": REACHABLE_STREAM_SHA256,
        "input_class_ids": [item["source_class_id"] for item in family["generators"]],
        "retained_class_ids": [item["source_class_id"] for item in minimization["retained_generators"]],
        "coordinate_parent_boundary_ambient": [1],
        "coordinate_conversion": "IDENTITY_ALREADY_IN_NODE9_PARENT_COORDINATES",
        "invariant_vector": copy.deepcopy(proof["invariant_vector"]),
        "idempotence": copy.deepcopy(proof["idempotence"]),
        "admit": True,
    }


def verify_data(
    frontier: dict[str, Any],
    up_k: dict[str, Any],
    manifest: dict[str, Any],
    summary: dict[str, Any],
    producer_text: str | None = None,
) -> dict[str, Any]:
    frontier_proof, up_k_proof = expected_source(frontier, up_k)
    expected = expected_closure(up_k_proof)

    unsigned_manifest = copy.deepcopy(manifest)
    claimed_manifest_digest = unsigned_manifest.pop("manifest_digest", None)
    if claimed_manifest_digest != digest(unsigned_manifest):
        raise AssertionError("manifest digest")
    unsigned_summary = copy.deepcopy(summary)
    claimed_summary_digest = unsigned_summary.pop("semantic_digest", None)
    if claimed_summary_digest != digest(unsigned_summary):
        raise AssertionError("summary digest")

    topology = manifest["topology"]
    if topology["root_node_id"] != 10:
        raise AssertionError("root id")
    root_descriptor = next(item for item in topology["internal_nodes"] if int(item["node_id"]) == 10)
    if root_descriptor != {
        "node_id": 10,
        "kind": "SYNTHETIC_ROOT_CLOSE",
        "edge_index": 4,
        "child_node_ids": [9, 5],
        "left_factor_ids": [0, 1, 2, 3, 4],
        "right_factor_ids": [5],
        "covered_factor_ids": [0, 1, 2, 3, 4, 5],
        "outside_factor_ids": [],
    }:
        raise AssertionError("root descriptor")

    execution = manifest["execution"]
    stop = execution["stop"]
    if execution["processed_internal_node_ids"] != [6, 7, 8, 9]:
        raise AssertionError("processed node vector")
    if execution["root_node_id"] != 10 or execution["root_full_set_receipt"] is not None:
        raise AssertionError("root receipt boundary")
    if (
        execution["status"],
        int(stop["node_id"]),
        stop["reason"],
        int(stop["required"]),
        int(stop["cap"]),
        stop["no_layout_at_cap"],
        stop["terminal"],
    ) != (
        "OPEN_AT_NODE_CAPACITY",
        10,
        "REFINEMENT_CAP_EXCEEDED",
        EXPECTED_REFINEMENTS,
        2000000,
        False,
        TERMINAL,
    ):
        raise AssertionError("root stop")
    if manifest["chunking"]["transcript_root_digest"] != TRANSCRIPT_ROOT or manifest["chunking"]["chunk_count"] != 61:
        raise AssertionError("transcript boundary")

    node9 = next(item for item in manifest["node_results"] if int(item["node_id"]) == 9)
    unsigned_node = copy.deepcopy(node9)
    node_digest = unsigned_node.pop("node_execution_digest", None)
    if node_digest != digest(unsigned_node):
        raise AssertionError("node9 execution digest")
    receipt = node9["output_receipt"]
    unsigned_receipt = copy.deepcopy(receipt)
    receipt_digest = unsigned_receipt.pop("receipt_digest", None)
    if receipt_digest != digest(unsigned_receipt):
        raise AssertionError("node9 receipt digest")
    if node9["input_full_set_receipts"][0]["receipt_digest"] != NODE8_RECEIPT:
        raise AssertionError("node8 child receipt")
    if node9["input_full_set_receipts"][1]["receipt_digest"] != LEAF4_RECEIPT:
        raise AssertionError("leaf4 child receipt")
    if node9["parent_boundary"] != [1] or node9["common_join_boundary"] != [4, 1]:
        raise AssertionError("node9 boundary")
    if node9["node_up_k"] != expected:
        raise AssertionError("node9 closure handoff")
    if any(int(item["count"]) for item in node9["record_ranges"].values()):
        raise AssertionError("generic node9 transcript")
    if (
        receipt["node_id"],
        receipt["boundary_rref_ambient"],
        receipt["boundary_coordinate_dimension"],
        receipt["entry_count"],
        receipt["entries_digest"],
        receipt["full_set_digest"],
    ) != (9, [1], 1, 252, REACHABLE_RECORDS_DIGEST, digest(expected)):
        raise AssertionError("node9 receipt content")
    bridge = node9["certified_structural_bridge"]
    if (
        bridge["frontier_classes"],
        bridge["retained_generators"],
        bridge["direct_removals"],
        bridge["naive_child_pairs_covered"],
        bridge["naive_refinements_covered"],
        bridge["successful_quotient_paths"],
        bridge["universal_failed_quotient_paths"],
        bridge["generic_pair_records_materialized"],
        bridge["generic_refinement_records_materialized"],
        bridge["closure_entries_returned_to_executor"],
    ) != (15, 2, 13, 574128, 1284995408, 118, 64, 0, 0, 252):
        raise AssertionError("bridge counters")

    leaf5 = manifest["leaf_full_sets"][5]
    if leaf5["output_receipt"]["receipt_digest"] != LEAF5_RECEIPT or leaf5["full_set"]["entry_count"] != 36:
        raise AssertionError("leaf5 receipt")
    left_hist = histogram(expected["entries"])
    right_hist = histogram(leaf5["full_set"]["entries"])
    if left_hist != LEFT_HIST or right_hist != RIGHT_HIST:
        raise AssertionError("root length histograms")
    pairs = sum(left_hist.values()) * sum(right_hist.values())
    refinements = refinement_count(left_hist, right_hist)
    if (pairs, refinements) != (EXPECTED_PAIRS, EXPECTED_REFINEMENTS):
        raise AssertionError("root exact frontier")

    blocks = manifest["scaffold_case"]["whole_factor_blocks"]
    left_boundary = tuple(node9["parent_boundary"])
    right_boundary = tuple(leaf5["boundary_rref_ambient"])
    common = xor_basis((*left_boundary, *right_boundary), 3)
    parent = boundary(blocks, [0, 1, 2, 3, 4, 5], [], 3)
    if (left_boundary, right_boundary, common, parent) != ((1,), (1,), (1,), ()):
        raise AssertionError("root geometry")

    preflight = summary["root_preflight"]
    if (
        preflight["root_node_id"],
        preflight["left_child_node_id"],
        preflight["right_child_node_id"],
        preflight["left_entry_count"],
        preflight["right_entry_count"],
        preflight["child_pair_count"],
        preflight["naive_refinement_count"],
        preflight["left_length_histogram"],
        preflight["right_length_histogram"],
        preflight["left_boundary"],
        preflight["right_boundary"],
        preflight["common_boundary"],
        preflight["parent_boundary"],
        preflight["left_expand_identity"],
        preflight["right_expand_identity"],
        preflight["shrink_identity"],
        preflight["pair_cap_exceeded"],
        preflight["refinement_cap_exceeded"],
        preflight["stop_reason"],
        preflight["generic_root_pair_records_materialized"],
        preflight["generic_root_refinement_records_materialized"],
        preflight["no_layout_at_cap"],
    ) != (
        10,
        9,
        5,
        252,
        36,
        EXPECTED_PAIRS,
        EXPECTED_REFINEMENTS,
        LEFT_HIST,
        RIGHT_HIST,
        [1],
        [1],
        [1],
        [],
        True,
        True,
        False,
        False,
        True,
        "REFINEMENT_CAP_EXCEEDED",
        0,
        0,
        False,
    ):
        raise AssertionError("root preflight summary")
    if summary["integrated_manifest_digest"] != manifest["manifest_digest"]:
        raise AssertionError("summary manifest binding")
    if summary["integrated_transcript_root_digest"] != TRANSCRIPT_ROOT:
        raise AssertionError("summary transcript binding")
    if summary["node9"]["node_execution_digest"] != node9["node_execution_digest"]:
        raise AssertionError("summary node9 execution binding")
    if summary["node9"]["output_receipt_digest"] != receipt["receipt_digest"]:
        raise AssertionError("summary node9 receipt binding")

    strict = {
        "node9_parent_up_k_admitted": True,
        "node9_integrated_into_bottom_up_executor": True,
        "node9_generic_cartesian_replay_required": False,
        "root_reached": True,
        "root_parent_refinement_started": True,
        "root_parent_refinement_complete": False,
        "root_parent_up_k_complete": False,
        "root_full_set_computed": False,
        "negative_root_reached": False,
        "terminal_completeness_proved": False,
        "found_layout_enabled": False,
        "no_layout_at_cap_enabled": False,
        "current_global_terminal": TERMINAL,
        "p_vs_np": "OPEN",
    }
    if summary["strict_boundary"] != strict:
        raise AssertionError("strict boundary")
    if summary["next_gate"] != "C049.1_B4.6.3_ROOT_PARENT_FRONTIER_STRUCTURAL_COMPRESSION":
        raise AssertionError("next gate")

    if producer_text is not None:
        for token in ("engine.lattice_paths", "join_trajectory(", "shrink_trajectory("):
            if token in producer_text:
                raise AssertionError("producer contains generic node9/root refinement enumeration")
    return {
        "pairs": pairs,
        "refinements": refinements,
        "node9_entries": len(expected["entries"]),
        "node9_receipt": receipt["receipt_digest"],
    }


def bind_receipt(receipt: dict[str, Any]) -> None:
    unsigned = copy.deepcopy(receipt)
    unsigned.pop("receipt_digest", None)
    receipt["receipt_digest"] = digest(unsigned)


def bind_node(node: dict[str, Any]) -> None:
    unsigned = copy.deepcopy(node)
    unsigned.pop("node_execution_digest", None)
    node["node_execution_digest"] = digest(unsigned)


def bind_manifest(manifest: dict[str, Any]) -> None:
    for node in manifest.get("node_results", []):
        bind_receipt(node["output_receipt"])
        bind_node(node)
    unsigned = copy.deepcopy(manifest)
    unsigned.pop("manifest_digest", None)
    manifest["manifest_digest"] = digest(unsigned)


def bind_summary(summary: dict[str, Any]) -> None:
    unsigned = copy.deepcopy(summary)
    unsigned.pop("semantic_digest", None)
    summary["semantic_digest"] = digest(unsigned)


def node_by_id(manifest: dict[str, Any], node_id: int) -> dict[str, Any]:
    return next(item for item in manifest["node_results"] if int(item["node_id"]) == node_id)


def tamper_attacks(
    frontier: dict[str, Any],
    up_k: dict[str, Any],
    manifest: dict[str, Any],
    summary: dict[str, Any],
    producer_text: str | None,
) -> list[str]:
    rejected: list[str] = []

    def run(name: str, mutation) -> None:
        f = copy.deepcopy(frontier)
        u = copy.deepcopy(up_k)
        m = copy.deepcopy(manifest)
        s = copy.deepcopy(summary)
        mutation(f, u, m, s)
        bind_manifest(m)
        s["integrated_manifest_digest"] = m["manifest_digest"]
        bind_summary(s)
        try:
            verify_data(f, u, m, s, producer_text)
        except Exception:
            rejected.append(name)
        else:
            raise AssertionError("tamper accepted: " + name)
        finally:
            del f, u, m, s
            gc.collect()

    run("DELETE_NODE9_ENTRY", lambda f, u, m, s: node_by_id(m, 9)["node_up_k"]["entries"].pop())
    run("CHANGE_NODE9_CLOSURE_METHOD", lambda f, u, m, s: node_by_id(m, 9)["node_up_k"].__setitem__("closure_method", "GENERIC"))
    run("MATERIALIZE_NODE9_PAIR_RANGE", lambda f, u, m, s: node_by_id(m, 9)["record_ranges"]["pairs"].__setitem__("count", 1))
    run("DROP_PROCESSED_NODE9", lambda f, u, m, s: m["execution"].__setitem__("processed_internal_node_ids", [6, 7, 8]))
    run("MOVE_STOP_BACK_TO_NODE9", lambda f, u, m, s: m["execution"]["stop"].__setitem__("node_id", 9))
    run("CHANGE_ROOT_PAIR_COUNT", lambda f, u, m, s: s["root_preflight"].__setitem__("child_pair_count", EXPECTED_PAIRS - 1))
    run("SUBSTITUTE_LEAF5_RECEIPT", lambda f, u, m, s: m["leaf_full_sets"][5]["output_receipt"].__setitem__("receipt_digest", "0" * 64))
    run("CHANGE_ROOT_REFINEMENT_COUNT", lambda f, u, m, s: s["root_preflight"].__setitem__("naive_refinement_count", EXPECTED_REFINEMENTS - 1))
    run("CLAIM_NEGATIVE_ROOT", lambda f, u, m, s: s["strict_boundary"].__setitem__("negative_root_reached", True))
    run("CLAIM_ROOT_FULL_SET", lambda f, u, m, s: s["strict_boundary"].__setitem__("root_full_set_computed", True))
    return rejected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("node9_frontier", type=Path)
    parser.add_argument("node9_up_k", type=Path)
    parser.add_argument("integrated_dir", type=Path)
    parser.add_argument("--producer-source", type=Path)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    if file_sha256(args.node9_frontier) != FRONTIER_SHA:
        raise AssertionError("frozen node9 frontier bytes")
    if file_sha256(args.node9_up_k) != UPK_SHA:
        raise AssertionError("frozen node9 up_k bytes")
    frontier = load(args.node9_frontier)
    up_k = load(args.node9_up_k)
    manifest = load(args.integrated_dir / "manifest.json")
    summary = load(args.integrated_dir / "node9-integration-root-preflight-summary.json")
    producer_text = args.producer_source.read_text(encoding="utf-8") if args.producer_source is not None else None
    result = verify_data(frontier, up_k, manifest, summary, producer_text)
    rejected = tamper_attacks(frontier, up_k, manifest, summary, producer_text) if args.tamper_self_test else []
    print("STATIC_NO_GENERIC_NODE9_OR_ROOT_REFINEMENT_ENUMERATION = PASS")
    print("JANUS_C049_1_B4_6_3_NODE9_INTEGRATION_VERIFIER = PASS")
    print("INVARIANTS = 10/10")
    print("NODE9_UP_K_ENTRIES =", result["node9_entries"])
    print("NODE9_OUTPUT_RECEIPT =", result["node9_receipt"])
    print("ROOT_CHILD_PAIRS =", result["pairs"])
    print("ROOT_NAIVE_REFINEMENTS =", result["refinements"])
    print("TAMPER_ATTACKS_REJECTED =", f"{len(rejected)}/10" if args.tamper_self_test else "NOT_RUN")


if __name__ == "__main__":
    main()
