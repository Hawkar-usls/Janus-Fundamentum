#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Sequence

TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
FRONTIER_SHA = "93dcd5610eb9df079823b172a4f824ce1c09859e759c6b771dc95b99af394d34"
FRONTIER_SEM = "209f5a013ec492b67066abc3dcf08af183d2ec5ec0000f3d8d03a033cb32f9db"
UPK_SHA = "e5202b9eb32ef44b1fdf493c6848ec82f8ce16fa502e623b7fbfdeb6bc735620"
UPK_SEM = "cf4794e6ccc4591e9bf57ccb4256a42c20bca8fba86658350f762f21f1019090"
SOURCE_ENTRIES_DIGEST = "1f37d96c5c16684057253ad109db9488e726bb4aed65745c966af520d13ac609"
COORDINATE_ENTRIES_DIGEST = "6030bb93f1298bf26f4c76d00bbc392dc0a6dd69dd4c1552691c55382fba7468"
COORDINATE_STREAM_DIGEST = "ddfa4717bda8c177b2014ec22fed6882be985e1dfbfec46701f933b01d2232f4"
COORDINATE_INPUT_DIGEST = "b5653fad52b8ba2899c27000bf86a1b496ab9e3ec5cc858b283aa4c7156b841e"
COORDINATE_RETAINED_DIGEST = "2da701dffb5bad4872459d5c2ab21b370f04c92a8b9e01f5a06252bb68d5df39"
COORDINATE_REMOVALS_DIGEST = "70e7cf110e735d10dee3f3895e261ad45c53dd6ce4e79a5cae9ea38fdba41545"
TRANSCRIPT_ROOT = "eb904e833b53f5626af1eb28493f479f5f54f2066a8b5427cb7e3eb47f515d8"
NODE7_RECEIPT = "838e4dfde9740585928b5498e18a5b0836f44da1d822c060d5c59b7d52177011"
LEAF3_RECEIPT = "80f424b87fd39e80013e1bb96b3dcec47d281a322f9964472b2ca32bd039e086"
LEAF4_RECEIPT = "44ae26d9a650353d6360027b08ad3738b9a0fed5bfd78fcfafb165e83dd0052f"
LEFT_HIST = {"2": 4, "3": 64, "4": 324, "5": 936, "6": 1916, "7": 2880, "8": 3352, "9": 2984, "10": 2048, "11": 1024, "12": 352, "13": 64}
RIGHT_HIST = {"2": 4, "3": 8, "4": 12, "5": 8, "6": 4}
EXPECTED_PAIRS = 574128
EXPECTED_REFINEMENTS = 1284995408


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def xor_basis(rows: Sequence[int], dimension: int) -> tuple[int, ...]:
    table: dict[int, int] = {}
    for raw in rows:
        value = int(raw)
        if value < 0 or value >= (1 << dimension):
            raise AssertionError("coordinate vector outside space")
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


def ambient_basis(rows: Sequence[int]) -> tuple[int, ...]:
    table: dict[int, int] = {}
    for raw in rows:
        value = int(raw)
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


def ambient_to_coordinate(vector: int, parent_basis: Sequence[int]) -> int:
    theta = len(parent_basis)
    for coordinate in range(1 << theta):
        ambient = 0
        for index, basis_vector in enumerate(parent_basis):
            if coordinate & (1 << (theta - 1 - index)):
                ambient ^= int(basis_vector)
        if ambient == int(vector):
            return coordinate
    raise AssertionError("ambient vector outside parent boundary")


def coordinate_subspace(rows: Sequence[int], parent_basis: Sequence[int]) -> list[int]:
    return list(xor_basis([ambient_to_coordinate(int(row), parent_basis) for row in rows], len(parent_basis)))


def coordinate_trajectory(raw: Sequence[dict], parent_basis: Sequence[int]) -> list[dict]:
    return [{"left": coordinate_subspace(item["left"], parent_basis), "right": coordinate_subspace(item["right"], parent_basis), "value": int(item["value"])} for item in raw]


def coordinate_entry(entry: dict, parent_basis: Sequence[int]) -> dict:
    out = copy.deepcopy(entry)
    out["trajectory"] = coordinate_trajectory(entry["trajectory"], parent_basis)
    return out


def coordinate_removal(removal: dict, parent_basis: Sequence[int]) -> dict:
    out = copy.deepcopy(removal)
    out["removed_generator"] = coordinate_trajectory(removal["removed_generator"], parent_basis)
    out["retained_generator"] = coordinate_trajectory(removal["retained_generator"], parent_basis)
    return out


def stream_digest(entries: Sequence[dict]) -> str:
    hasher = hashlib.sha256()
    for entry in entries:
        hasher.update(canonical_json(entry["trajectory"]))
        hasher.update(b"\n")
    return hasher.hexdigest()


def histogram(entries: Sequence[dict]) -> dict[str, int]:
    result: dict[str, int] = {}
    for entry in entries:
        key = str(len(entry["trajectory"]))
        result[key] = result.get(key, 0) + 1
    return dict(sorted(result.items(), key=lambda item: int(item[0])))


def delannoy(left_length: int, right_length: int) -> int:
    left_steps = left_length - 1
    right_steps = right_length - 1
    return sum(math.comb(left_steps, diagonal) * math.comb(right_steps, diagonal) * (2**diagonal) for diagonal in range(min(left_steps, right_steps) + 1))


def refinement_count(left_hist: dict[str, int], right_hist: dict[str, int]) -> int:
    return sum(left_count * right_count * delannoy(int(left_length), int(right_length)) for left_length, left_count in left_hist.items() for right_length, right_count in right_hist.items())


def bind_receipt(receipt: dict) -> None:
    unsigned = copy.deepcopy(receipt)
    unsigned.pop("receipt_digest", None)
    receipt["receipt_digest"] = digest(unsigned)


def bind_node(node: dict) -> None:
    unsigned = copy.deepcopy(node)
    unsigned.pop("node_execution_digest", None)
    node["node_execution_digest"] = digest(unsigned)


def bind_manifest(manifest: dict) -> None:
    for node in manifest.get("node_results", []):
        bind_receipt(node["output_receipt"])
        bind_node(node)
    unsigned = copy.deepcopy(manifest)
    unsigned.pop("manifest_digest", None)
    manifest["manifest_digest"] = digest(unsigned)


def bind_summary(summary: dict) -> None:
    unsigned = copy.deepcopy(summary)
    unsigned.pop("semantic_digest", None)
    summary["semantic_digest"] = digest(unsigned)


def verify_data(frontier: dict, up_k: dict, manifest: dict, summary: dict, producer_text: str | None = None) -> dict:
    if frontier.get("semantic_digest") != FRONTIER_SEM or frontier.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("frontier semantic")
    frontier_proof = frontier["proof_payload"]
    if frontier_proof.get("admit") is not True or set(frontier_proof.get("invariant_vector", {}).values()) != {"PASS"}:
        raise AssertionError("frontier admission")
    if up_k.get("semantic_digest") != UPK_SEM or up_k.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("up_k semantic")
    proof = up_k["proof_payload"]
    if proof.get("admit") is not True or set(proof.get("invariant_vector", {}).values()) != {"PASS"}:
        raise AssertionError("up_k admission")
    if proof["source"]["artifact_sha256"] != FRONTIER_SHA:
        raise AssertionError("up_k source")

    reachable = proof["reachable_closure"]
    if len(reachable["entries"]) != 15948 or digest(reachable["entries"]) != SOURCE_ENTRIES_DIGEST:
        raise AssertionError("source ambient entries")
    parent_basis = (4, 1)
    coordinate_entries = [coordinate_entry(item, parent_basis) for item in reachable["entries"]]
    coordinate_inputs = [coordinate_trajectory(item["generator"], parent_basis) for item in proof["input_family"]["generators"]]
    coordinate_retained = [coordinate_trajectory(item["generator"], parent_basis) for item in proof["preorder_minimization"]["retained_generators"]]
    coordinate_removals = [coordinate_removal(item, parent_basis) for item in proof["preorder_minimization"]["removals"]]
    if digest(coordinate_entries) != COORDINATE_ENTRIES_DIGEST or stream_digest(coordinate_entries) != COORDINATE_STREAM_DIGEST:
        raise AssertionError("coordinate entries")
    if digest(coordinate_inputs) != COORDINATE_INPUT_DIGEST or digest(coordinate_retained) != COORDINATE_RETAINED_DIGEST or digest(coordinate_removals) != COORDINATE_REMOVALS_DIGEST:
        raise AssertionError("coordinate generator inventories")

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
    node9_descriptor = next(item for item in topology["internal_nodes"] if int(item["node_id"]) == 9)
    expected_node9 = {"node_id": 9, "kind": "SPINE_INTERNAL_JOIN", "edge_index": 3, "child_node_ids": [8, 4], "left_factor_ids": [0, 1, 2, 3], "right_factor_ids": [4], "covered_factor_ids": [0, 1, 2, 3, 4], "outside_factor_ids": [5]}
    if node9_descriptor != expected_node9:
        raise AssertionError("node9 descriptor")

    execution = manifest["execution"]
    stop = execution["stop"]
    if execution["processed_internal_node_ids"] != [6, 7, 8] or execution["root_node_id"] != 10:
        raise AssertionError("execution vector")
    if (execution["status"], int(stop["node_id"]), stop["reason"], int(stop["required"]), int(stop["cap"]), stop["no_layout_at_cap"], stop["terminal"]) != ("OPEN_AT_NODE_CAPACITY", 9, "CHILD_PAIR_CAP_EXCEEDED", EXPECTED_PAIRS, 10000, False, TERMINAL):
        raise AssertionError("node9 stop")
    if manifest["chunking"]["transcript_root_digest"] != TRANSCRIPT_ROOT or manifest["chunking"]["chunk_count"] != 61:
        raise AssertionError("transcript boundary")

    node8 = next(item for item in manifest["node_results"] if int(item["node_id"]) == 8)
    unsigned_node = copy.deepcopy(node8)
    node_digest = unsigned_node.pop("node_execution_digest", None)
    if node_digest != digest(unsigned_node):
        raise AssertionError("node8 execution digest")
    receipt = node8["output_receipt"]
    unsigned_receipt = copy.deepcopy(receipt)
    receipt_digest = unsigned_receipt.pop("receipt_digest", None)
    if receipt_digest != digest(unsigned_receipt):
        raise AssertionError("node8 receipt digest")
    if node8["input_full_set_receipts"][0]["receipt_digest"] != NODE7_RECEIPT or node8["input_full_set_receipts"][1]["receipt_digest"] != LEAF3_RECEIPT:
        raise AssertionError("node8 child receipts")

    closure = node8["node_up_k"]
    if closure["closure_method"] != "CERTIFIED_NODE8_TWENTY_EIGHT_GENERATOR_REACHABLE_CATALOG":
        raise AssertionError("closure method")
    if (closure["entry_count"], len(closure["input_generators"]), len(closure["retained_generators"]), len(closure["removals"])) != (15948, 61, 28, 33):
        raise AssertionError("closure cardinality")
    if closure["entries"] != coordinate_entries or closure["input_generators"] != coordinate_inputs or closure["retained_generators"] != coordinate_retained or closure["removals"] != coordinate_removals:
        raise AssertionError("coordinate handoff mismatch")
    if closure["reachable_entries_digest"] != COORDINATE_ENTRIES_DIGEST or closure["coordinate_parent_boundary_ambient"] != [4, 1]:
        raise AssertionError("coordinate closure binding")
    if receipt["entry_count"] != 15948 or receipt["entries_digest"] != COORDINATE_ENTRIES_DIGEST or receipt["full_set_digest"] != digest(closure):
        raise AssertionError("receipt content")
    if any(int(item["count"]) for item in node8["record_ranges"].values()):
        raise AssertionError("generic node8 transcript")
    bridge = node8["certified_structural_bridge"]
    if (bridge["frontier_classes"], bridge["retained_generators"], bridge["direct_removals"], bridge["naive_child_pairs_covered"], bridge["naive_refinements_covered"], bridge["generic_pair_records_materialized"], bridge["generic_refinement_records_materialized"], bridge["closure_entries_returned_to_executor"]) != (61, 28, 33, 327888, 602017584, 0, 0, 15948):
        raise AssertionError("bridge counters")

    leaf4 = manifest["leaf_full_sets"][4]
    if leaf4["output_receipt"]["receipt_digest"] != LEAF4_RECEIPT or leaf4["full_set"]["entry_count"] != 36:
        raise AssertionError("leaf4 receipt")
    left_hist = histogram(closure["entries"])
    right_hist = histogram(leaf4["full_set"]["entries"])
    if left_hist != LEFT_HIST or right_hist != RIGHT_HIST:
        raise AssertionError("length histograms")
    pairs = sum(left_hist.values()) * sum(right_hist.values())
    refinements = refinement_count(left_hist, right_hist)
    if (pairs, refinements) != (EXPECTED_PAIRS, EXPECTED_REFINEMENTS):
        raise AssertionError("node9 exact frontier")

    blocks = manifest["scaffold_case"]["whole_factor_blocks"]
    left_boundary = tuple(node8["parent_boundary"])
    right_boundary = tuple(leaf4["boundary_rref_ambient"])
    common = ambient_basis((*left_boundary, *right_boundary))
    covered_rows = [row for index in [0, 1, 2, 3, 4] for row in blocks[index]]
    outside_rows = list(blocks[5])
    parent = ambient_basis(tuple(span(ambient_basis(covered_rows)) & span(ambient_basis(outside_rows))))
    if (left_boundary, right_boundary, common, parent) != ((4, 1), (5,), (4, 1), (1,)):
        raise AssertionError("node9 geometry")

    preflight = summary["node9_preflight"]
    if (preflight["left_entry_count"], preflight["right_entry_count"], preflight["child_pair_count"], preflight["naive_refinement_count"], preflight["left_length_histogram"], preflight["right_length_histogram"], preflight["left_boundary"], preflight["right_boundary"], preflight["common_boundary"], preflight["parent_boundary"], preflight["left_expand_identity"], preflight["shrink_identity"], preflight["no_layout_at_cap"]) != (15948, 36, EXPECTED_PAIRS, EXPECTED_REFINEMENTS, LEFT_HIST, RIGHT_HIST, [4, 1], [5], [4, 1], [1], True, False, False):
        raise AssertionError("summary preflight")
    if summary["integrated_manifest_digest"] != manifest["manifest_digest"] or summary["integrated_transcript_root_digest"] != TRANSCRIPT_ROOT:
        raise AssertionError("summary binding")
    if summary["node8"]["node_execution_digest"] != node8["node_execution_digest"] or summary["node8"]["output_receipt_digest"] != receipt["receipt_digest"]:
        raise AssertionError("summary node8 binding")

    expected_strict = {"node8_up_k_admitted": True, "node8_integrated_into_bottom_up_executor": True, "node8_generic_cartesian_replay_required": False, "node9_parent_refinement_started": True, "node9_parent_refinement_complete": False, "node9_parent_up_k_complete": False, "negative_root_reached": False, "terminal_completeness_proved": False, "found_layout_enabled": False, "no_layout_at_cap_enabled": False, "current_global_terminal": TERMINAL, "p_vs_np": "OPEN"}
    if summary["strict_boundary"] != expected_strict or summary["next_gate"] != "C049.1_B4.6.3_NODE9_PARENT_FRONTIER_STRUCTURAL_COMPRESSION":
        raise AssertionError("strict boundary")

    if producer_text is not None:
        for token in ("engine.lattice_paths", "join_trajectory(", "shrink_trajectory("):
            if token in producer_text:
                raise AssertionError("producer contains generic node8 refinement enumeration")
    return {"pairs": pairs, "refinements": refinements, "node8_entries": len(closure["entries"]), "node8_receipt": receipt["receipt_digest"]}


def tamper_attacks(frontier: dict, up_k: dict, manifest: dict, summary: dict, producer_text: str | None) -> list[str]:
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
            return
        raise AssertionError("tamper accepted: " + name)

    run("DELETE_NODE8_ENTRY", lambda f, u, m, s: m["node_results"][2]["node_up_k"]["entries"].pop())
    run("CHANGE_COORDINATE_CONVERSION", lambda f, u, m, s: m["node_results"][2]["node_up_k"].__setitem__("coordinate_conversion", "IDENTITY"))
    run("MATERIALIZE_NODE8_PAIR_RANGE", lambda f, u, m, s: m["node_results"][2]["record_ranges"]["pairs"].__setitem__("count", 1))
    run("DROP_PROCESSED_NODE8", lambda f, u, m, s: m["execution"].__setitem__("processed_internal_node_ids", [6, 7]))
    run("MOVE_STOP_TO_ROOT", lambda f, u, m, s: m["execution"]["stop"].__setitem__("node_id", 10))
    run("CHANGE_NODE9_PAIR_COUNT", lambda f, u, m, s: m["execution"]["stop"].__setitem__("required", EXPECTED_PAIRS - 1))
    run("SUBSTITUTE_LEAF4_RECEIPT", lambda f, u, m, s: m["leaf_full_sets"][4]["output_receipt"].__setitem__("receipt_digest", "0" * 64))
    run("CHANGE_REFINEMENT_COUNT", lambda f, u, m, s: s["node9_preflight"].__setitem__("naive_refinement_count", EXPECTED_REFINEMENTS - 1))
    run("CLAIM_NEGATIVE_ROOT", lambda f, u, m, s: s["strict_boundary"].__setitem__("negative_root_reached", True))
    run("SKIP_NODE9_COMPRESSION_GATE", lambda f, u, m, s: s.__setitem__("next_gate", "ROOT"))
    return rejected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("node8_frontier", type=Path)
    parser.add_argument("node8_up_k", type=Path)
    parser.add_argument("integrated_dir", type=Path)
    parser.add_argument("--producer-source", type=Path)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    if file_sha256(args.node8_frontier) != FRONTIER_SHA or file_sha256(args.node8_up_k) != UPK_SHA:
        raise AssertionError("frozen source bytes")
    frontier = load(args.node8_frontier)
    up_k = load(args.node8_up_k)
    manifest = load(args.integrated_dir / "manifest.json")
    summary = load(args.integrated_dir / "node8-integration-node9-preflight-summary.json")
    producer_text = args.producer_source.read_text(encoding="utf-8") if args.producer_source is not None else None
    result = verify_data(frontier, up_k, manifest, summary, producer_text)
    rejected = tamper_attacks(frontier, up_k, manifest, summary, producer_text) if args.tamper_self_test else []
    print("STATIC_NO_GENERIC_NODE8_REFINEMENT_ENUMERATION = PASS")
    print("JANUS_C049_1_B4_6_3_NODE8_INTEGRATION_VERIFIER = PASS")
    print("INVARIANTS = 10/10")
    print("NODE8_UP_K_ENTRIES =", result["node8_entries"])
    print("NODE9_CHILD_PAIRS =", result["pairs"])
    print("NODE9_NAIVE_REFINEMENTS =", result["refinements"])
    print("TAMPER_ATTACKS_REJECTED =", f"{len(rejected)}/10" if args.tamper_self_test else "NOT_RUN")


if __name__ == "__main__":
    main()
