#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

SCHEMA = "C049.1-B4.6.3-NODE7-UP-K-INTEGRATION-NODE8-PARENT-REFINEMENT-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"

EXPECTED_FRONTIER_SHA256 = "6a0748219d829434feeb5de2c5488e1fa3aeb1fab16ecbfee0c5629be90130a9"
EXPECTED_UP_K_SHA256 = "c085a3bee4e0c92a01eb22715390079f9858c5704ebcbf8534f9de196087d189"
EXPECTED_UP_K_SEMANTIC_DIGEST = "23079901348590eb39d60d904d52dfd5004f8b287382a288ccbea688802b22f2"
EXPECTED_NODE6_RECEIPT_DIGEST = "88170c8f5ba5519908e88f1dba21bb2247218c0713dc6830e562a879edd3aad9"
EXPECTED_NODE7_ENTRIES = 9108
EXPECTED_NODE8_RIGHT_ENTRIES = 36
EXPECTED_NODE8_PAIRS = 327888
EXPECTED_NODE8_REFINEMENTS = 602017584
EXPECTED_TRANSCRIPT_ROOT = "eb904e833b53cf5626af1eb28493f479f5f54f2066a8b5427cb7e3eb47f515d8"


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def delannoy_path_count(m: int, n: int) -> int:
    if m <= 0 or n <= 0:
        raise ValueError("trajectory lengths must be positive")
    table = [[0] * n for _ in range(m)]
    table[0][0] = 1
    for i in range(m):
        for j in range(n):
            if i == 0 and j == 0:
                continue
            value = 0
            if i:
                value += table[i - 1][j]
            if j:
                value += table[i][j - 1]
            if i and j:
                value += table[i - 1][j - 1]
            table[i][j] = value
    return table[-1][-1]


def verify_static_source(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    if 'if int(descriptor["node_id"]) == NODE7_ID:' not in source:
        raise AssertionError("node-7 intercept is not visibly scoped to node 7")
    if '"executor_intercept_scope": "NODE_ID_7_ONLY"' not in source:
        raise AssertionError("node-7 intercept scope receipt missing")
    forbidden = (
        "DEFAULT_PAIR_CAP = 327888",
        "DEFAULT_REFINEMENT_CAP = 602017584",
        '"negative_root_reached": True',
        '"no_layout_at_cap_enabled": True',
    )
    for text in forbidden:
        if text in source:
            raise AssertionError(f"forbidden integration shortcut present: {text}")
    names = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }
    required = {
        "certified_node7_closure",
        "certified_node7_execute",
        "delannoy_path_count",
        "build",
    }
    if not required.issubset(names):
        raise AssertionError("integration source lacks required proof functions")


def verify(
    frontier_path: Path,
    up_k_path: Path,
    manifest_path: Path,
    summary_path: Path,
    producer_source: Path,
) -> dict:
    if file_sha256(frontier_path) != EXPECTED_FRONTIER_SHA256:
        raise AssertionError("frontier byte digest drift")
    if file_sha256(up_k_path) != EXPECTED_UP_K_SHA256:
        raise AssertionError("up_k byte digest drift")
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    up_k = json.loads(up_k_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    verify_static_source(producer_source)

    if summary.get("schema") != SCHEMA:
        raise AssertionError("summary schema drift")
    if frontier.get("admit") is not True or len(
        frontier.get("quotient_frontier", {}).get("classes", [])
    ) != 13:
        raise AssertionError("frontier source is not the admitted 13-class artifact")
    expected_source = {
        "prefix_manifest_digest": "6df541b6aa441f218a54acf9232184d00cd319701156673e543fca651dec94ed",
        "node6_hardening_sha256": "a68ea1957382bfa89386a09ab501a052057b1cc5de8db7191a6ab3a26e1d2af9",
        "node7_frontier_sha256": EXPECTED_FRONTIER_SHA256,
        "node7_frontier_semantic_digest": "ed6b59821aaef10ac6bdb6286a72ffcafd15e2bbd2619e0edffc7f711a2b1103",
        "node7_up_k_sha256": EXPECTED_UP_K_SHA256,
        "node7_up_k_semantic_digest": EXPECTED_UP_K_SEMANTIC_DIGEST,
    }
    if summary.get("source") != expected_source:
        raise AssertionError("summary source binding drift")
    unsigned_summary = copy.deepcopy(summary)
    claimed_summary_digest = unsigned_summary.pop("semantic_digest", None)
    if claimed_summary_digest != digest(unsigned_summary):
        raise AssertionError("summary semantic digest mismatch")

    proof = up_k["proof_payload"]
    source_closure = proof["exact_reachable_closure"]
    if up_k.get("semantic_digest") != EXPECTED_UP_K_SEMANTIC_DIGEST:
        raise AssertionError("up_k semantic digest drift")
    if proof.get("admit") is not True:
        raise AssertionError("up_k source is not admitted")
    if len(source_closure["reachable_entries"]) != EXPECTED_NODE7_ENTRIES:
        raise AssertionError("source reachable entry count drift")
    if digest(source_closure["reachable_entries"]) != source_closure[
        "reachable_entries_digest"
    ]:
        raise AssertionError("source reachable entries digest mismatch")

    unsigned_manifest = copy.deepcopy(manifest)
    claimed_manifest_digest = unsigned_manifest.pop("manifest_digest", None)
    if claimed_manifest_digest != digest(unsigned_manifest):
        raise AssertionError("integrated manifest digest mismatch")
    if manifest["execution"]["processed_internal_node_ids"] != [6, 7]:
        raise AssertionError("processed node vector drift")
    stop = manifest["execution"]["stop"]
    if (
        int(stop["node_id"]),
        stop["reason"],
        int(stop["required"]),
        bool(stop["no_layout_at_cap"]),
        stop["terminal"],
    ) != (
        8,
        "CHILD_PAIR_CAP_EXCEEDED",
        EXPECTED_NODE8_PAIRS,
        False,
        TERMINAL,
    ):
        raise AssertionError("node-8 honest stop drift")
    if manifest["chunking"]["transcript_root_digest"] != EXPECTED_TRANSCRIPT_ROOT:
        raise AssertionError("certified bridge unexpectedly changed raw transcript root")

    node6 = next(item for item in manifest["node_results"] if int(item["node_id"]) == 6)
    node7 = next(item for item in manifest["node_results"] if int(item["node_id"]) == 7)
    if node6["output_receipt"]["receipt_digest"] != EXPECTED_NODE6_RECEIPT_DIGEST:
        raise AssertionError("node-6 output receipt drift")
    unsigned_node7 = copy.deepcopy(node7)
    claimed_node7_digest = unsigned_node7.pop("node_execution_digest", None)
    if claimed_node7_digest != digest(unsigned_node7):
        raise AssertionError("node-7 execution digest mismatch")
    receipt_body = copy.deepcopy(node7["output_receipt"])
    claimed_receipt_digest = receipt_body.pop("receipt_digest", None)
    if claimed_receipt_digest != digest(receipt_body):
        raise AssertionError("node-7 output receipt digest mismatch")
    closure = node7["node_up_k"]
    if closure["closure_method"] != (
        "CERTIFIED_NODE7_THIRTEEN_GENERATOR_REACHABLE_CATALOG"
    ):
        raise AssertionError("node-7 certified closure method drift")
    if (
        len(closure["input_generators"]),
        len(closure["retained_generators"]),
        len(closure["removals"]),
        int(closure["entry_count"]),
    ) != (13, 13, 0, EXPECTED_NODE7_ENTRIES):
        raise AssertionError("node-7 integrated closure cardinality drift")
    if closure["entries"] != source_closure["reachable_entries"]:
        raise AssertionError("integrated closure differs from admitted closure artifact")
    if closure["reachable_entries_digest"] != source_closure[
        "reachable_entries_digest"
    ]:
        raise AssertionError("integrated reachable entries digest drift")
    if node7["input_full_set_receipts"][0]["receipt_digest"] != (
        node6["output_receipt"]["receipt_digest"]
    ):
        raise AssertionError("node-7 left receipt handoff drift")
    if node7["input_full_set_receipts"][1] != manifest["leaf_full_sets"][2][
        "output_receipt"
    ]:
        raise AssertionError("node-7 right leaf receipt handoff drift")
    if any(value["count"] != 0 for value in node7["record_ranges"].values()):
        raise AssertionError("certified node-7 bridge materialized raw transcript records")
    if node7["audit"]["child_pairs_processed"] != 0:
        raise AssertionError("node-7 bridge falsely reports pair enumeration")
    if node7["audit"]["lattice_paths_processed"] != 0:
        raise AssertionError("node-7 bridge falsely reports fine refinement enumeration")
    if node7["audit"]["certified_naive_child_pairs_covered"] != 16848:
        raise AssertionError("node-7 theorem-covered pair count drift")
    if node7["audit"]["certified_naive_refinements_covered"] != 9744432:
        raise AssertionError("node-7 theorem-covered refinement count drift")
    if node7["output_receipt"]["entry_count"] != EXPECTED_NODE7_ENTRIES:
        raise AssertionError("node-7 output receipt entry count drift")

    right_entries = manifest["leaf_full_sets"][3]["full_set"]["entries"]
    if len(right_entries) != EXPECTED_NODE8_RIGHT_ENTRIES:
        raise AssertionError("node-8 right leaf inventory drift")
    pair_count = len(closure["entries"]) * len(right_entries)
    refinement_count = sum(
        delannoy_path_count(
            len(left["trajectory"]),
            len(right["trajectory"]),
        )
        for left in closure["entries"]
        for right in right_entries
    )
    if pair_count != EXPECTED_NODE8_PAIRS:
        raise AssertionError("node-8 pair count drift")
    if refinement_count != EXPECTED_NODE8_REFINEMENTS:
        raise AssertionError("node-8 exact refinement count drift")

    preflight = summary["node8_preflight"]
    if (
        int(preflight["left_entries"]),
        int(preflight["right_entries"]),
        int(preflight["child_pairs_required"]),
        int(preflight["naive_refinements_required"]),
        bool(preflight["parent_refinement_started"]),
        bool(preflight["no_layout_at_cap"]),
    ) != (
        EXPECTED_NODE7_ENTRIES,
        EXPECTED_NODE8_RIGHT_ENTRIES,
        EXPECTED_NODE8_PAIRS,
        EXPECTED_NODE8_REFINEMENTS,
        False,
        False,
    ):
        raise AssertionError("summary node-8 preflight drift")
    strict = summary["strict_boundary"]
    expected_strict = {
        "node7_parent_up_k_complete": True,
        "node7_integrated_into_bottom_up_executor": True,
        "node8_reached": True,
        "node8_parent_preflight_complete": True,
        "node8_parent_refinement_started": False,
        "negative_root_reached": False,
        "terminal_completeness_proved": False,
        "found_layout_enabled": False,
        "no_layout_at_cap_enabled": False,
        "current_global_terminal": TERMINAL,
        "p_vs_np": "OPEN",
    }
    if strict != expected_strict:
        raise AssertionError("strict boundary drift")
    if summary["next_gate"] != (
        "C049.1_B4.6.3_NODE8_PARENT_FRONTIER_STRUCTURAL_COMPRESSION"
    ):
        raise AssertionError("next gate drift")

    return {
        "processed_internal_node_ids": [6, 7],
        "node7_up_k_entries": EXPECTED_NODE7_ENTRIES,
        "node8_child_pairs_required": pair_count,
        "node8_naive_refinements_required": refinement_count,
        "summary_semantic_digest": claimed_summary_digest,
        "manifest_digest": claimed_manifest_digest,
    }


def run_tamper_tests(
    frontier_path: Path,
    up_k_path: Path,
    manifest_path: Path,
    summary_path: Path,
    producer_source: Path,
) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    attacks = []

    def summary_attack(mutator):
        damaged = copy.deepcopy(summary)
        mutator(damaged)
        body = copy.deepcopy(damaged)
        body.pop("semantic_digest", None)
        damaged["semantic_digest"] = digest(body)
        return damaged

    damaged = copy.deepcopy(manifest)
    damaged["execution"]["stop"]["node_id"] = 7
    attacks.append(("stop-node", damaged, summary))
    damaged = copy.deepcopy(manifest)
    damaged["execution"]["stop"]["required"] -= 1
    attacks.append(("stop-pairs", damaged, summary))
    damaged = copy.deepcopy(manifest)
    damaged["node_results"][1]["node_up_k"]["entries"].pop()
    attacks.append(("node7-entry", damaged, summary))
    damaged = copy.deepcopy(manifest)
    damaged["node_results"][1]["record_ranges"]["pairs"]["count"] = 1
    attacks.append(("raw-record-range", damaged, summary))
    damaged = copy.deepcopy(manifest)
    damaged["chunking"]["transcript_root_digest"] = "0" * 64
    attacks.append(("transcript-root", damaged, summary))

    summary_variants = [
        (
            "refinement-count",
            summary_attack(
                lambda value: value["node8_preflight"].__setitem__(
                    "naive_refinements_required", EXPECTED_NODE8_REFINEMENTS - 1
                )
            ),
        ),
        (
            "false-root",
            summary_attack(
                lambda value: value["strict_boundary"].__setitem__(
                    "negative_root_reached", True
                )
            ),
        ),
        (
            "false-no-layout",
            summary_attack(
                lambda value: value["strict_boundary"].__setitem__(
                    "no_layout_at_cap_enabled", True
                )
            ),
        ),
        (
            "source-up-k",
            summary_attack(
                lambda value: value["source"].__setitem__(
                    "node7_up_k_sha256", "0" * 64
                )
            ),
        ),
        (
            "next-gate",
            summary_attack(lambda value: value.__setitem__("next_gate", "ROOT")),
        ),
    ]

    rejected = 0
    for name, damaged_manifest, damaged_summary in attacks:
        with tempfile.TemporaryDirectory() as root:
            root_path = Path(root)
            manifest_tmp = root_path / "manifest.json"
            summary_tmp = root_path / "summary.json"
            manifest_tmp.write_text(
                json.dumps(damaged_manifest, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            summary_tmp.write_text(
                json.dumps(damaged_summary, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            try:
                verify(
                    frontier_path,
                    up_k_path,
                    manifest_tmp,
                    summary_tmp,
                    producer_source,
                )
            except Exception:
                rejected += 1
            else:
                raise AssertionError(f"tamper attack was accepted: {name}")

    for name, damaged_summary in summary_variants:
        with tempfile.TemporaryDirectory() as root:
            summary_tmp = Path(root) / "summary.json"
            summary_tmp.write_text(
                json.dumps(damaged_summary, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            try:
                verify(
                    frontier_path,
                    up_k_path,
                    manifest_path,
                    summary_tmp,
                    producer_source,
                )
            except Exception:
                rejected += 1
            else:
                raise AssertionError(f"tamper attack was accepted: {name}")

    if rejected != 10:
        raise AssertionError("tamper rejection count drift")
    return rejected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("node7_frontier", type=Path)
    parser.add_argument("node7_up_k", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("summary", type=Path)
    parser.add_argument("--producer-source", type=Path, required=True)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    result = verify(
        args.node7_frontier,
        args.node7_up_k,
        args.manifest,
        args.summary,
        args.producer_source,
    )
    rejected = (
        run_tamper_tests(
            args.node7_frontier,
            args.node7_up_k,
            args.manifest,
            args.summary,
            args.producer_source,
        )
        if args.tamper_self_test
        else 0
    )
    print("STATIC_NODE7_EXECUTOR_INTERCEPT_SCOPE = PASS")
    print("JANUS_C049_1_B4_6_3_NODE7_INTEGRATION_VERIFIER = PASS")
    print("PROCESSED_INTERNAL_NODE_IDS =", result["processed_internal_node_ids"])
    print("NODE7_UP_K_ENTRIES =", result["node7_up_k_entries"])
    print("NODE8_CHILD_PAIRS_REQUIRED =", result["node8_child_pairs_required"])
    print("NODE8_NAIVE_REFINEMENTS_REQUIRED =", result["node8_naive_refinements_required"])
    print(
        "TAMPER_ATTACKS_REJECTED =",
        f"{rejected}/10" if args.tamper_self_test else "NOT_RUN",
    )
    print("GLOBAL_TERMINAL =", TERMINAL)


if __name__ == "__main__":
    main()
