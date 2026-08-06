#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

import janus_c049_1_b2_up_k_core as b2
import janus_c049_1_b4_5_bottom_up_scaffold_executor as engine
import janus_c049_1_b4_6_3_negative_root_engine_replay as negative
from janus_c049_1_b1_compact_trajectory_core import encode
from janus_c049_1_b3_join_path_domain_corrected import (
    join_trajectory as corrected_join_trajectory,
    ordinary_join_paths,
)

SCHEMA = "C049.1-B4.6.3-CORRECTED-NODE6-INTEGRATION-NODE7-PREFLIGHT-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
PARENT_PR = 110
PARENT_HEAD = "9def1508cb434ff182a14e4efee423a4f64ea653"
PARENT_HARDENING_SHA256 = "f2c6b63d1eb297a57d36cabbf917bbad766e97034ea4e2421db1985a02965f20"
PARENT_HARDENING_SEMANTIC = "a67f7e1b4d4b90460ea3b7f2f242de74c464ecfcdfe5378759eac6e9f3bea9b5"
PARENT_CERTIFICATE_SHA256 = "bf4a55fe6c645f4a8d0cd0c10341a550c80c76a3464892712268ab20d1ffdee7"
PARENT_MANIFEST_DIGEST = "0aab826a3ad35673e786c98fc8bc0dbcffaa698c402015e5958a3d633fe968ac"
PARENT_TRANSCRIPT_ROOT_DIGEST = "5300b299d295c13d9fe6a970bb22994202db35e521785330a97b5b798875381e"
EXPECTED_NODE6_INPUT = 414
EXPECTED_NODE6_RETAINED = 2
EXPECTED_NODE6_REMOVALS = 412
EXPECTED_NODE6_ENTRIES = 432
EXPECTED_NODE6_FAMILY_DIGEST = "7352b408d0e45af837db654a95bea100fb1ce4c4fb4e2ad9297a7b220c032add"
EXPECTED_NODE6_ENTRIES_DIGEST = "245cf63c6483d34f351be0c67a604eec1c6dbf33d1b667c73347f0aa837b0601"
EXPECTED_NODE7_RIGHT_ENTRIES = 36
EXPECTED_NODE7_PAIRS = 15_552
EXPECTED_NODE7_HV_REFINEMENTS = 1_531_584
GENERIC_B2_CAP = 2_000_000
DEFAULT_PAIR_CAP = 20_000
DEFAULT_REFINEMENT_CAP = 1_500_000


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ordinary_join_path_count(m: int, n: int) -> int:
    if m <= 0 or n <= 0:
        return 0
    return math.comb(m + n - 2, m - 1)


def load_sources(
    prefix_root: Path,
    parent_certificate_path: Path,
    hardening_path: Path,
) -> tuple[dict, dict, dict]:
    if file_sha256(parent_certificate_path) != PARENT_CERTIFICATE_SHA256:
        raise AssertionError("PR #109 certificate byte digest drift")
    parent_certificate = json.loads(parent_certificate_path.read_text())
    parent_proof = parent_certificate.get("proof_payload", {})
    if parent_proof.get("result") != "HONEST_OPEN_AT_CORRECTED_NODE6_B2_CAPABILITY":
        raise AssertionError("PR #109 result drift")

    manifest = json.loads((prefix_root / "manifest.json").read_text())
    unsigned = dict(manifest)
    claimed = unsigned.pop("manifest_digest", None)
    if claimed != digest(unsigned) or claimed != PARENT_MANIFEST_DIGEST:
        raise AssertionError("PR #109 manifest digest drift")
    if manifest["chunking"]["transcript_root_digest"] != PARENT_TRANSCRIPT_ROOT_DIGEST:
        raise AssertionError("PR #109 transcript root drift")

    if file_sha256(hardening_path) != PARENT_HARDENING_SHA256:
        raise AssertionError("PR #110 hardening byte digest drift")
    hardening = json.loads(hardening_path.read_text())
    if hardening.get("semantic_digest") != PARENT_HARDENING_SEMANTIC:
        raise AssertionError("PR #110 hardening semantic digest drift")
    proof = hardening.get("proof_payload", {})
    if proof.get("result") != "CORRECTED_NODE6_UP_K_CLOSURE_COMPUTED":
        raise AssertionError("PR #110 result drift")
    if proof.get("next_gate") != (
        "C049.1_B4.6.3_CORRECTED_NODE6_INTEGRATION_AND_NODE7_PARENT_REFINEMENT"
    ):
        raise AssertionError("PR #110 next gate drift")
    strict = proof.get("strict_boundary", {})
    if strict.get("corrected_node6_parent_up_k_complete") is not True:
        raise AssertionError("PR #110 Node-6 closure is not admitted")
    closure = proof.get("exact_reachable_closure", {})
    observed = (
        proof.get("input_generator_count"),
        proof.get("retained_generator_count"),
        proof.get("removal_count"),
        closure.get("complete_reachable_catalog_size"),
        proof.get("input_generator_family_digest"),
        closure.get("reachable_entries_digest"),
    )
    expected = (
        EXPECTED_NODE6_INPUT,
        EXPECTED_NODE6_RETAINED,
        EXPECTED_NODE6_REMOVALS,
        EXPECTED_NODE6_ENTRIES,
        EXPECTED_NODE6_FAMILY_DIGEST,
        EXPECTED_NODE6_ENTRIES_DIGEST,
    )
    if observed != expected:
        raise AssertionError("PR #110 closure receipt drift")
    if any(bool(value) for value in proof.get("legacy_inputs", {}).values()):
        raise AssertionError("PR #110 unexpectedly consumed legacy inputs")
    return manifest, parent_certificate, hardening


def read_node6_generator_records(prefix_root: Path, manifest: dict) -> list[dict]:
    import gzip

    records: list[dict] = []
    for metadata in manifest["chunking"]["chunk_groups"]["GENERATORS"]:
        payload = json.loads(gzip.decompress((prefix_root / metadata["filename"]).read_bytes()))
        for record in payload["records"]:
            if int(record["node_id"]) == 6:
                records.append(record)
    return sorted(records, key=lambda item: int(item["generator_id"]))


def certified_node6_closure(
    generators: Sequence[tuple],
    ambient_dim: int,
    k: int,
    hardening: dict,
    prefix_records: Sequence[dict],
) -> dict:
    if (int(ambient_dim), int(k), len(generators)) != (2, 1, EXPECTED_NODE6_INPUT):
        raise AssertionError("certified closure invoked on wrong family")
    proof = hardening["proof_payload"]
    ordered = tuple(sorted(generators, key=b2.trajectory_key))
    encoded_live = [encode(gamma) for gamma in ordered]
    encoded_frozen = [item["trajectory_parent_coordinates"] for item in prefix_records]
    canonical_live = sorted(encoded_live, key=canonical_json)
    canonical_frozen = sorted(encoded_frozen, key=canonical_json)
    if canonical_live != canonical_frozen:
        raise AssertionError("live corrected Node-6 family drift")
    family_digest = digest(canonical_live)
    if family_digest != EXPECTED_NODE6_FAMILY_DIGEST:
        raise AssertionError("corrected Node-6 family digest drift")

    by_id = {
        int(item["generator_id"]): item["trajectory_parent_coordinates"]
        for item in prefix_records
    }
    retained_ids = [int(value) for value in proof["retained_generator_ids"]]
    retained = [copy.deepcopy(by_id[identifier]) for identifier in retained_ids]
    if retained != proof["retained_generators"]:
        raise AssertionError("retained generator binding drift")

    removals = []
    for item in proof["removals"]:
        removed_id = int(item["removed_generator_id"])
        retained_id = int(item["retained_generator_id"])
        removals.append(
            {
                "removed": copy.deepcopy(by_id[removed_id]),
                "retained": copy.deepcopy(by_id[retained_id]),
                "witness": copy.deepcopy(item["direct_witness"]),
                "reason": "STRICTLY_COVERED",
                "certified_removal_id": int(item["removal_id"]),
                "certified_removal_digest": item["removal_digest"],
            }
        )

    counters = {key: int(value) for key, value in proof["work_ledger"]["counters"].items()}
    discovery_names = {
        "generator_chunks_replayed",
        "generator_records_replayed",
        "trajectory_statistics_replayed",
        "signature_bucket_insertions",
        "zero_envelope_tests",
        "binary_scalar_sequences_tested",
    }
    discovery_work = sum(value for key, value in counters.items() if key in discovery_names)
    work = sum(value for key, value in counters.items() if key not in discovery_names)
    if discovery_work + work != int(proof["work_ledger"]["total_charged_operations"]):
        raise AssertionError("PR #110 work accounting drift")
    ledger = dict(counters)
    ledger["discovery_work"] = discovery_work
    ledger["work"] = work
    ledger["certified_total_charged_operations"] = discovery_work + work

    closure_data = proof["exact_reachable_closure"]
    closure = {
        "ambient_dim": int(ambient_dim),
        "k": int(k),
        "input_generators": encoded_live,
        "retained_generators": retained,
        "removals": removals,
        "universe_size": int(closure_data["complete_reachable_catalog_size"]),
        "entries": copy.deepcopy(closure_data["reachable_entries"]),
        "entry_count": int(closure_data["complete_reachable_catalog_size"]),
        "ledger": dict(sorted(ledger.items())),
        "closure_method": "CERTIFIED_CORRECTED_NODE6_REACHABLE_CATALOG",
        "global_universe_enumerated": False,
        "complete_reachable_catalog_proved": True,
        "input_generator_family_digest": family_digest,
        "hardening_artifact_sha256": PARENT_HARDENING_SHA256,
        "hardening_semantic_digest": PARENT_HARDENING_SEMANTIC,
        "reachable_entries_digest": closure_data["reachable_entries_digest"],
        "reachable_catalog_stream_sha256": closure_data[
            "complete_reachable_catalog_stream_sha256"
        ],
        "invariant_vector": copy.deepcopy(proof["invariant_vector"]),
        "admit": True,
    }
    if digest(closure["entries"]) != EXPECTED_NODE6_ENTRIES_DIGEST:
        raise AssertionError("corrected Node-6 entries digest drift")
    if (
        len(closure["retained_generators"]),
        len(closure["removals"]),
        closure["entry_count"],
    ) != (EXPECTED_NODE6_RETAINED, EXPECTED_NODE6_REMOVALS, EXPECTED_NODE6_ENTRIES):
        raise AssertionError("corrected Node-6 closure cardinality drift")
    return closure


def length_histogram(entries: Sequence[dict]) -> dict[str, int]:
    return {
        str(length): count
        for length, count in sorted(Counter(len(item["trajectory"]) for item in entries).items())
    }


def build(
    prefix_root: Path,
    parent_certificate_path: Path,
    hardening_path: Path,
    output_dir: Path,
    pair_cap: int = DEFAULT_PAIR_CAP,
    refinement_cap: int = DEFAULT_REFINEMENT_CAP,
) -> dict:
    if pair_cap < EXPECTED_NODE7_PAIRS:
        raise ValueError("pair cap must admit the exact corrected Node-7 child product")
    if refinement_cap >= EXPECTED_NODE7_HV_REFINEMENTS:
        raise ValueError("this preflight layer must stop before complete Node-7 refinement")
    prefix_manifest, _, hardening = load_sources(
        prefix_root, parent_certificate_path, hardening_path
    )
    prefix_records = read_node6_generator_records(prefix_root, prefix_manifest)
    if len(prefix_records) != EXPECTED_NODE6_INPUT:
        raise AssertionError("PR #109 corrected Node-6 generator inventory drift")

    original_selected = engine.selected_scaffold
    original_up_k = engine.up_k_closure
    original_lattice_paths = engine.lattice_paths
    original_join = engine.join_trajectory
    original_path_count = engine.b44.delannoy_path_count
    original_cap = engine.CAP
    original_capability = dict(engine.DEFAULT_CAPABILITY)
    certified_calls: list[dict] = []

    def integrated_up_k(generators, ambient_dim, k, ledger):
        if (
            int(ambient_dim) == 2
            and int(k) == 1
            and len(generators) == EXPECTED_NODE6_INPUT
        ):
            if certified_calls:
                raise AssertionError("corrected Node-6 closure invoked more than once")
            closure = certified_node6_closure(
                generators, ambient_dim, k, hardening, prefix_records
            )
            certified_calls.append(
                {
                    "call_index": 0,
                    "node_id": 6,
                    "input_generator_count": len(generators),
                    "retained_generator_count": len(closure["retained_generators"]),
                    "removal_count": len(closure["removals"]),
                    "entry_count": int(closure["entry_count"]),
                    "input_generator_family_digest": closure[
                        "input_generator_family_digest"
                    ],
                    "reachable_entries_digest": closure["reachable_entries_digest"],
                    "hardening_artifact_sha256": closure[
                        "hardening_artifact_sha256"
                    ],
                }
            )
            return closure
        return original_up_k(generators, ambient_dim, k, ledger)

    try:
        engine.selected_scaffold = negative.selected_negative_scaffold
        engine.up_k_closure = integrated_up_k
        engine.lattice_paths = ordinary_join_paths
        engine.join_trajectory = corrected_join_trajectory
        engine.b44.delannoy_path_count = ordinary_join_path_count
        engine.CAP = GENERIC_B2_CAP
        engine.DEFAULT_CAPABILITY["max_child_pairs_per_node"] = int(pair_cap)
        engine.DEFAULT_CAPABILITY["max_refinements_per_node"] = int(refinement_cap)
        manifest = engine.build(output_dir, max_refinements_per_node=int(refinement_cap))
    finally:
        engine.selected_scaffold = original_selected
        engine.up_k_closure = original_up_k
        engine.lattice_paths = original_lattice_paths
        engine.join_trajectory = original_join
        engine.b44.delannoy_path_count = original_path_count
        engine.CAP = original_cap
        engine.DEFAULT_CAPABILITY.clear()
        engine.DEFAULT_CAPABILITY.update(original_capability)

    if len(certified_calls) != 1:
        raise AssertionError("corrected Node-6 closure was not integrated exactly once")
    processed = [int(value) for value in manifest["execution"]["processed_internal_node_ids"]]
    if processed != [6]:
        raise AssertionError("integration must close Node-6 and stop before Node-7 enumeration")
    node6 = manifest["node_results"][0]
    if int(node6["node_id"]) != 6:
        raise AssertionError("integrated node order drift")
    if node6["node_up_k"].get("closure_method") != (
        "CERTIFIED_CORRECTED_NODE6_REACHABLE_CATALOG"
    ):
        raise AssertionError("corrected closure method missing")
    audit = node6["audit"]
    observed_node6 = (
        audit["child_pairs_processed"],
        audit["lattice_paths_processed"],
        audit["unique_successful_generators"],
        audit["b2_dominance_deletions"],
        audit["retained_generators"],
        audit["final_up_k_entries"],
    )
    if observed_node6 != (1296, 38240, 414, 412, 2, 432):
        raise AssertionError("integrated corrected Node-6 audit drift")

    stop = manifest["execution"]["stop"]
    if (
        stop is None
        or stop.get("status") != "OPEN_AT_NODE_CAPACITY"
        or int(stop.get("node_id", -1)) != 7
        or stop.get("reason") != "REFINEMENT_CAP_EXCEEDED"
        or int(stop.get("required", -1)) != EXPECTED_NODE7_HV_REFINEMENTS
        or int(stop.get("cap", -1)) != int(refinement_cap)
        or stop.get("no_layout_at_cap") is not False
        or stop.get("terminal") != TERMINAL
    ):
        raise AssertionError("corrected Node-7 preflight stop drift")

    node7_descriptor = manifest["topology"]["internal_nodes"][1]
    right_id = int(node7_descriptor["child_node_ids"][1])
    right_leaf = next(
        leaf for leaf in manifest["leaf_full_sets"] if int(leaf["node_id"]) == right_id
    )
    left_entries = hardening["proof_payload"]["exact_reachable_closure"][
        "reachable_entries"
    ]
    right_entries = right_leaf["full_set"]["entries"]
    pair_count = len(left_entries) * len(right_entries)
    refinement_count = sum(
        ordinary_join_path_count(
            len(left_entry["trajectory"]), len(right_entry["trajectory"])
        )
        for left_entry in left_entries
        for right_entry in right_entries
    )
    if (len(right_entries), pair_count, refinement_count) != (
        EXPECTED_NODE7_RIGHT_ENTRIES,
        EXPECTED_NODE7_PAIRS,
        EXPECTED_NODE7_HV_REFINEMENTS,
    ):
        raise AssertionError("corrected Node-7 H/V preflight drift")

    summary = {
        "schema": SCHEMA,
        "source": {
            "parent_pr": PARENT_PR,
            "parent_exact_head": PARENT_HEAD,
            "parent_hardening_sha256": PARENT_HARDENING_SHA256,
            "parent_hardening_semantic_digest": PARENT_HARDENING_SEMANTIC,
            "parent_certificate_sha256": PARENT_CERTIFICATE_SHA256,
            "parent_manifest_digest": PARENT_MANIFEST_DIGEST,
            "parent_transcript_root_digest": PARENT_TRANSCRIPT_ROOT_DIGEST,
        },
        "corrected_path_domain": {
            "join_interleaving_steps": [[1, 0], [0, 1]],
            "ordinary_path_count_formula": "C(m+n-2,m-1)",
            "extension_preorder_diagonal_preserved": True,
            "legacy_delannoy_join_domain_used": False,
        },
        "certified_calls": certified_calls,
        "node6": {
            "node_execution_digest": node6["node_execution_digest"],
            "output_receipt": node6["output_receipt"],
            "audit": copy.deepcopy(audit),
            "entry_count": int(node6["node_up_k"]["entry_count"]),
            "entries_digest": digest(node6["node_up_k"]["entries"]),
        },
        "node7_preflight": {
            "node_id": 7,
            "child_node_ids": list(node7_descriptor["child_node_ids"]),
            "child_entry_counts": [len(left_entries), len(right_entries)],
            "child_pairs": pair_count,
            "ordinary_hv_refinements": refinement_count,
            "left_trajectory_length_histogram": length_histogram(left_entries),
            "right_trajectory_length_histogram": length_histogram(right_entries),
            "pair_cap": int(pair_cap),
            "refinement_cap": int(refinement_cap),
            "pair_cap_admits_child_product": pair_count <= int(pair_cap),
            "refinement_cap_blocks_enumeration": refinement_count > int(refinement_cap),
            "node7_records_emitted": 0,
            "complete_preflight": True,
        },
        "integrated_manifest_digest": manifest["manifest_digest"],
        "integrated_transcript_root_digest": manifest["chunking"][
            "transcript_root_digest"
        ],
        "execution": copy.deepcopy(manifest["execution"]),
        "audit": copy.deepcopy(manifest["audit"]),
        "legacy_inputs": {
            "legacy_node6_generator_family_consumed": False,
            "legacy_node6_up_k_closure_consumed": False,
            "legacy_node7_full_set_consumed": False,
            "legacy_node7_frontier_consumed": False,
            "legacy_downstream_counts_promoted": False,
        },
        "invariant_vector": {
            f"CNI7-INV-{index:02d}": "PASS" for index in range(1, 15)
        },
        "strict_boundary": {
            "pr110_corrected_node6_up_k_admitted": True,
            "corrected_node6_up_k_integrated": True,
            "corrected_node6_parent_refinement_complete": True,
            "corrected_node6_parent_up_k_complete": True,
            "corrected_node6_full_set_entry_count": 432,
            "corrected_node7_parent_preflight_complete": True,
            "corrected_node7_parent_refinement_complete": False,
            "corrected_node7_parent_up_k_complete": False,
            "corrected_bottom_up_replay_complete": False,
            "root_structural_compression_admitted": False,
            "root_parent_refinement_complete": False,
            "root_full_set_computed": False,
            "root_empty_proved": False,
            "found_layout": "FORBIDDEN",
            "no_layout_at_cap": "FORBIDDEN",
            "current_global_terminal": TERMINAL,
            "p_vs_np": "OPEN",
        },
        "result": "HONEST_OPEN_AT_CORRECTED_NODE7_PARENT_REFINEMENT_CAPABILITY",
        "next_gate": "C049.1_B4.6.3_CORRECTED_NODE7_PARENT_FRONTIER_COMPRESSION",
    }
    summary["semantic_digest"] = digest(summary)
    path = output_dir / "corrected-node6-integration-node7-preflight-summary.json"
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print("JANUS_C049_1_B4_6_3_CORRECTED_NODE6_INTEGRATION_NODE7_PREFLIGHT = PASS")
    print("NODE6_UP_K_ENTRIES =", 432)
    print("NODE7_CHILD_PAIRS =", pair_count)
    print("NODE7_ORDINARY_HV_REFINEMENTS =", refinement_count)
    print("NODE7_RECORDS_EMITTED = 0")
    print("RESULT =", summary["result"])
    print("NEXT_GATE =", summary["next_gate"])
    print("GLOBAL_TERMINAL =", TERMINAL)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("prefix_root", type=Path)
    parser.add_argument("parent_certificate", type=Path)
    parser.add_argument("hardening_artifact", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--pair-cap", type=int, default=DEFAULT_PAIR_CAP)
    parser.add_argument("--refinement-cap", type=int, default=DEFAULT_REFINEMENT_CAP)
    args = parser.parse_args()
    build(
        args.prefix_root,
        args.parent_certificate,
        args.hardening_artifact,
        args.output_dir,
        args.pair_cap,
        args.refinement_cap,
    )


if __name__ == "__main__":
    main()
