#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Iterator, Sequence

TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
PARENT_HEAD = "9def1508cb434ff182a14e4efee423a4f64ea653"
PARENT_HARDENING_SHA256 = "f2c6b63d1eb297a57d36cabbf917bbad766e97034ea4e2421db1985a02965f20"
PARENT_HARDENING_SEMANTIC = "a67f7e1b4d4b90460ea3b7f2f242de74c464ecfcdfe5378759eac6e9f3bea9b5"
PARENT_CERTIFICATE_SHA256 = "bf4a55fe6c645f4a8d0cd0c10341a550c80c76a3464892712268ab20d1ffdee7"
PARENT_MANIFEST_DIGEST = "0aab826a3ad35673e786c98fc8bc0dbcffaa698c402015e5958a3d633fe968ac"
PARENT_TRANSCRIPT_ROOT_DIGEST = "5300b299d295c13d9fe6a970bb22994202db35e521785330a97b5b798875381e"
NODE6_ENTRIES_DIGEST = "245cf63c6483d34f351be0c67a604eec1c6dbf33d1b667c73347f0aa837b0601"
NODE7_PAIRS = 15_552
NODE7_HV_REFINEMENTS = 1_531_584
NEXT_GATE = "C049.1_B4.6.3_CORRECTED_NODE7_PARENT_FRONTIER_COMPRESSION"


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


def path_steps(path: Sequence[Sequence[int]]) -> tuple[tuple[int, int], ...]:
    parsed = tuple((int(item[0]), int(item[1])) for item in path)
    return tuple(
        (following[0] - current[0], following[1] - current[1])
        for current, following in zip(parsed, parsed[1:])
    )


def verify_bound_json(path: Path, expected_sha: str | None = None) -> dict:
    if expected_sha is not None and file_sha256(path) != expected_sha:
        raise AssertionError("artifact byte digest drift")
    value = json.loads(path.read_text())
    if "proof_payload" in value:
        if value.get("semantic_digest") != digest(value["proof_payload"]):
            raise AssertionError("proof semantic digest drift")
        if int(value["proof_payload"].get("certificate_bytes", -1)) != len(path.read_bytes()):
            raise AssertionError("proof fixed-point byte count drift")
    return value


def verify_manifest(root: Path) -> dict:
    manifest = json.loads((root / "manifest.json").read_text())
    unsigned = dict(manifest)
    claimed = unsigned.pop("manifest_digest", None)
    if claimed != digest(unsigned):
        raise AssertionError("integrated manifest digest drift")
    groups = manifest["chunking"]["chunk_groups"]
    if manifest["chunking"]["transcript_root_digest"] != digest(groups):
        raise AssertionError("integrated transcript root drift")
    return manifest


def verified_records(root: Path, manifest: dict, kind: str) -> Iterator[dict]:
    expected_global_id = 0
    previous_digest = None
    id_field = {
        "PAIRS": "pair_id",
        "REFINEMENTS": "attempt_id",
        "GENERATORS": "generator_id",
        "DELETIONS": "deletion_id",
    }[kind]
    metadata_group = manifest["chunking"]["chunk_groups"][kind]
    for index, metadata in enumerate(metadata_group):
        if int(metadata["chunk_index"]) != index:
            raise AssertionError("chunk index drift")
        if metadata["previous_chunk_digest"] != previous_digest:
            raise AssertionError("chunk backward link drift")
        compressed = (root / metadata["filename"]).read_bytes()
        if len(compressed) != int(metadata["compressed_bytes"]):
            raise AssertionError("compressed chunk byte drift")
        compressed_digest = hashlib.sha256(compressed).hexdigest()
        if compressed_digest != metadata["compressed_sha256"]:
            raise AssertionError("compressed chunk digest drift")
        raw = gzip.decompress(compressed)
        if len(raw) != int(metadata["uncompressed_bytes"]):
            raise AssertionError("uncompressed chunk byte drift")
        payload = json.loads(raw)
        unsigned = dict(payload)
        claimed = unsigned.pop("chunk_payload_digest", None)
        if claimed != digest(unsigned) or claimed != metadata["chunk_payload_digest"]:
            raise AssertionError("chunk payload digest drift")
        if payload["kind"] != kind or int(payload["chunk_index"]) != index:
            raise AssertionError("chunk identity drift")
        if int(payload["record_count"]) != len(payload["records"]):
            raise AssertionError("chunk record count drift")
        for record in payload["records"]:
            if int(record[id_field]) != expected_global_id:
                raise AssertionError("global record id continuity drift")
            expected_global_id += 1
            body = dict(record)
            record_digest = body.pop("record_digest", None)
            if record_digest != digest(body):
                raise AssertionError("record digest drift")
            yield record
        previous_digest = compressed_digest
    expected_total = sum(int(item["record_count"]) for item in metadata_group)
    if expected_global_id != expected_total:
        raise AssertionError("record inventory drift")


def length_histogram(entries: Sequence[dict]) -> dict[str, int]:
    return {
        str(length): count
        for length, count in sorted(Counter(len(item["trajectory"]) for item in entries).items())
    }


def verify_static_producer(source_path: Path) -> None:
    source = source_path.read_text()
    forbidden = (
        "dimension_two_preorder_hardening",
        "node6_up_k_integration_parent_refinement",
        "node7_parent_frontier_structural_compression",
        "node7_thirteen_generator_up_k_closure",
        "node7_up_k_integration",
        "node8_",
        "node9_",
        "root_parent_frontier",
    )
    for token in forbidden:
        if token in source:
            raise AssertionError(f"producer references historical downstream layer: {token}")
    if "ordinary_join_paths" not in source or "corrected_join_trajectory" not in source:
        raise AssertionError("producer does not bind corrected H/V join API")


def verify_summary_semantics(
    summary: dict,
    manifest: dict,
    hardening: dict,
    pair_records: Sequence[dict],
    refinement_records: Sequence[dict],
    generator_records: Sequence[dict],
    deletion_records: Sequence[dict],
) -> None:
    unsigned = dict(summary)
    claimed = unsigned.pop("semantic_digest", None)
    if claimed != digest(unsigned):
        raise AssertionError("summary semantic digest drift")
    source = summary["source"]
    if source != {
        "parent_pr": 110,
        "parent_exact_head": PARENT_HEAD,
        "parent_hardening_sha256": PARENT_HARDENING_SHA256,
        "parent_hardening_semantic_digest": PARENT_HARDENING_SEMANTIC,
        "parent_certificate_sha256": PARENT_CERTIFICATE_SHA256,
        "parent_manifest_digest": PARENT_MANIFEST_DIGEST,
        "parent_transcript_root_digest": PARENT_TRANSCRIPT_ROOT_DIGEST,
    }:
        raise AssertionError("source binding drift")

    domain = summary["corrected_path_domain"]
    if domain["join_interleaving_steps"] != [[1, 0], [0, 1]]:
        raise AssertionError("ordinary join domain drift")
    if domain["extension_preorder_diagonal_preserved"] is not True:
        raise AssertionError("extension diagonal preservation drift")
    if domain["legacy_delannoy_join_domain_used"] is not False:
        raise AssertionError("legacy Delannoy domain re-entered integration")

    proof = hardening["proof_payload"]
    closure = proof["exact_reachable_closure"]
    if (
        proof["input_generator_count"],
        proof["retained_generator_count"],
        proof["removal_count"],
        closure["complete_reachable_catalog_size"],
        closure["reachable_entries_digest"],
    ) != (414, 2, 412, 432, NODE6_ENTRIES_DIGEST):
        raise AssertionError("hardening closure drift")
    if digest(closure["reachable_entries"]) != NODE6_ENTRIES_DIGEST:
        raise AssertionError("hardening entries digest drift")

    calls = summary["certified_calls"]
    if len(calls) != 1:
        raise AssertionError("certified call cardinality drift")
    call = calls[0]
    if (
        call["node_id"],
        call["input_generator_count"],
        call["retained_generator_count"],
        call["removal_count"],
        call["entry_count"],
        call["reachable_entries_digest"],
        call["hardening_artifact_sha256"],
    ) != (6, 414, 2, 412, 432, NODE6_ENTRIES_DIGEST, PARENT_HARDENING_SHA256):
        raise AssertionError("certified integration call drift")

    if len(manifest["node_results"]) != 1:
        raise AssertionError("integrated node inventory drift")
    node6 = manifest["node_results"][0]
    if int(node6["node_id"]) != 6:
        raise AssertionError("integrated node order drift")
    if node6["node_up_k"]["closure_method"] != (
        "CERTIFIED_CORRECTED_NODE6_REACHABLE_CATALOG"
    ):
        raise AssertionError("certified closure method drift")
    if digest(node6["node_up_k"]["entries"]) != NODE6_ENTRIES_DIGEST:
        raise AssertionError("integrated closure entries drift")
    audit = node6["audit"]
    expected_audit = (1296, 38240, 2684, 35556, 414, 2270, 412, 2, 432)
    observed_audit = (
        audit["child_pairs_processed"],
        audit["lattice_paths_processed"],
        audit["successful_refinements"],
        audit["failed_refinements"],
        audit["unique_successful_generators"],
        audit["duplicate_successful_outputs_deleted"],
        audit["b2_dominance_deletions"],
        audit["retained_generators"],
        audit["final_up_k_entries"],
    )
    if observed_audit != expected_audit:
        raise AssertionError("integrated Node-6 audit drift")
    if summary["node6"]["entry_count"] != 432:
        raise AssertionError("summary Node-6 entry count drift")
    if summary["node6"]["entries_digest"] != NODE6_ENTRIES_DIGEST:
        raise AssertionError("summary Node-6 entries digest drift")

    if len(pair_records) != 1296 or any(int(item["node_id"]) != 6 for item in pair_records):
        raise AssertionError("Node-6 pair transcript drift")
    expected_paths = 0
    for pair in pair_records:
        m = len(pair["left_expand"]["output_ambient"])
        n = len(pair["right_expand"]["output_ambient"])
        expected = ordinary_join_path_count(m, n)
        if int(pair["lattice_path_count"]) != expected:
            raise AssertionError("pair H/V path count drift")
        first = int(pair["first_attempt_id"])
        last = int(pair["last_attempt_id"])
        if last - first + 1 != expected:
            raise AssertionError("pair attempt range drift")
        expected_paths += expected
    if expected_paths != 38240 or len(refinement_records) != expected_paths:
        raise AssertionError("complete corrected Node-6 refinement replay drift")

    success_ids: set[int] = set()
    failure_ids: set[int] = set()
    for item in refinement_records:
        if int(item["node_id"]) != 6:
            raise AssertionError("Node-7 record emitted before admitted enumeration")
        steps = path_steps(item["lattice_path"])
        if any(step not in ((1, 0), (0, 1)) for step in steps):
            raise AssertionError("diagonal or invalid join step in integrated transcript")
        identifier = int(item["attempt_id"])
        if item["status"] == "SUCCESS":
            success_ids.add(identifier)
        elif item["status"] == "FAILED_WIDTH_CAP":
            failure_ids.add(identifier)
        else:
            raise AssertionError("unknown refinement status")
    if len(success_ids) != 2684 or len(failure_ids) != 35556 or success_ids & failure_ids:
        raise AssertionError("refinement partition drift")

    provenance: list[int] = []
    if len(generator_records) != 414 or any(int(item["node_id"]) != 6 for item in generator_records):
        raise AssertionError("generator transcript drift")
    for item in generator_records:
        provenance.extend(int(value) for value in item["provenance_attempt_ids"])
    if set(provenance) != success_ids or len(provenance) != len(success_ids):
        raise AssertionError("successful refinement provenance drift")
    if len(deletion_records) != 2270 or any(int(item["node_id"]) != 6 for item in deletion_records):
        raise AssertionError("duplicate-deletion transcript drift")
    if len({int(item["removed_attempt_id"]) for item in deletion_records}) != 2270:
        raise AssertionError("duplicate deletion conservation drift")

    preflight = summary["node7_preflight"]
    topology_node7 = manifest["topology"]["internal_nodes"][1]
    right_id = int(topology_node7["child_node_ids"][1])
    right_leaf = next(
        leaf for leaf in manifest["leaf_full_sets"] if int(leaf["node_id"]) == right_id
    )
    left_entries = closure["reachable_entries"]
    right_entries = right_leaf["full_set"]["entries"]
    pair_count = len(left_entries) * len(right_entries)
    refinement_count = sum(
        ordinary_join_path_count(
            len(left["trajectory"]), len(right["trajectory"])
        )
        for left in left_entries
        for right in right_entries
    )
    if (len(left_entries), len(right_entries), pair_count, refinement_count) != (
        432,
        36,
        NODE7_PAIRS,
        NODE7_HV_REFINEMENTS,
    ):
        raise AssertionError("independent Node-7 workload computation drift")
    if preflight["child_node_ids"] != [6, right_id]:
        raise AssertionError("Node-7 child handoff drift")
    if preflight["child_entry_counts"] != [432, 36]:
        raise AssertionError("Node-7 child entry count drift")
    if preflight["child_pairs"] != pair_count:
        raise AssertionError("Node-7 pair preflight drift")
    if preflight["ordinary_hv_refinements"] != refinement_count:
        raise AssertionError("Node-7 refinement preflight drift")
    if preflight["left_trajectory_length_histogram"] != length_histogram(left_entries):
        raise AssertionError("left trajectory histogram drift")
    if preflight["right_trajectory_length_histogram"] != length_histogram(right_entries):
        raise AssertionError("right trajectory histogram drift")
    if preflight["node7_records_emitted"] != 0 or preflight["complete_preflight"] is not True:
        raise AssertionError("Node-7 preflight boundary drift")

    stop = manifest["execution"]["stop"]
    if (
        manifest["execution"]["processed_internal_node_ids"] != [6]
        or stop["status"] != "OPEN_AT_NODE_CAPACITY"
        or int(stop["node_id"]) != 7
        or stop["reason"] != "REFINEMENT_CAP_EXCEEDED"
        or int(stop["required"]) != NODE7_HV_REFINEMENTS
        or int(stop["cap"]) != int(preflight["refinement_cap"])
        or stop["no_layout_at_cap"] is not False
        or stop["terminal"] != TERMINAL
    ):
        raise AssertionError("honest Node-7 capability stop drift")
    if not (preflight["pair_cap"] >= NODE7_PAIRS):
        raise AssertionError("pair cap did not admit exact child product")
    if not (preflight["refinement_cap"] < NODE7_HV_REFINEMENTS):
        raise AssertionError("refinement cap did not enforce preflight boundary")

    if summary["integrated_manifest_digest"] != manifest["manifest_digest"]:
        raise AssertionError("summary/manifest binding drift")
    if summary["integrated_transcript_root_digest"] != manifest["chunking"]["transcript_root_digest"]:
        raise AssertionError("summary/transcript binding drift")
    if any(bool(value) for value in summary["legacy_inputs"].values()):
        raise AssertionError("legacy input entered corrected integration")
    if summary["invariant_vector"] != {f"CNI7-INV-{i:02d}": "PASS" for i in range(1, 15)}:
        raise AssertionError("invariant vector drift")

    strict = summary["strict_boundary"]
    expected_true = (
        "pr110_corrected_node6_up_k_admitted",
        "corrected_node6_up_k_integrated",
        "corrected_node6_parent_refinement_complete",
        "corrected_node6_parent_up_k_complete",
        "corrected_node7_parent_preflight_complete",
    )
    if any(strict[key] is not True for key in expected_true):
        raise AssertionError("admitted integration boundary drift")
    expected_false = (
        "corrected_node7_parent_refinement_complete",
        "corrected_node7_parent_up_k_complete",
        "corrected_bottom_up_replay_complete",
        "root_structural_compression_admitted",
        "root_parent_refinement_complete",
        "root_full_set_computed",
        "root_empty_proved",
    )
    if any(strict[key] is not False for key in expected_false):
        raise AssertionError("incomplete downstream boundary drift")
    if strict["corrected_node6_full_set_entry_count"] != 432:
        raise AssertionError("strict Node-6 entry count drift")
    if strict["found_layout"] != "FORBIDDEN" or strict["no_layout_at_cap"] != "FORBIDDEN":
        raise AssertionError("forbidden terminal enabled")
    if strict["current_global_terminal"] != TERMINAL or strict["p_vs_np"] != "OPEN":
        raise AssertionError("global terminal drift")
    if summary["result"] != "HONEST_OPEN_AT_CORRECTED_NODE7_PARENT_REFINEMENT_CAPABILITY":
        raise AssertionError("result drift")
    if summary["next_gate"] != NEXT_GATE:
        raise AssertionError("next gate drift")


def repaired_summary(summary: dict) -> dict:
    value = copy.deepcopy(summary)
    value.pop("semantic_digest", None)
    value["semantic_digest"] = digest(value)
    return value


def run_tamper_self_test(
    summary: dict,
    manifest: dict,
    hardening: dict,
    pairs: Sequence[dict],
    refinements: Sequence[dict],
    generators: Sequence[dict],
    deletions: Sequence[dict],
) -> None:
    mutations = []

    def add(name, mutate):
        mutations.append((name, mutate))

    add("parent_head", lambda x: x["source"].__setitem__("parent_exact_head", "0" * 40))
    add("node6_entry_count", lambda x: x["node6"].__setitem__("entry_count", 431))
    add("node6_entries_digest", lambda x: x["node6"].__setitem__("entries_digest", "0" * 64))
    add("node7_pairs", lambda x: x["node7_preflight"].__setitem__("child_pairs", NODE7_PAIRS - 1))
    add("node7_refinements", lambda x: x["node7_preflight"].__setitem__("ordinary_hv_refinements", NODE7_HV_REFINEMENTS - 1))
    add("diagonal_domain", lambda x: x["corrected_path_domain"].__setitem__("join_interleaving_steps", [[1, 0], [0, 1], [1, 1]]))
    add("node7_complete", lambda x: x["strict_boundary"].__setitem__("corrected_node7_parent_refinement_complete", True))
    add("legacy_consumed", lambda x: x["legacy_inputs"].__setitem__("legacy_node7_full_set_consumed", True))
    add("found_layout", lambda x: x["strict_boundary"].__setitem__("found_layout", "TRUE"))
    add("no_layout", lambda x: x["strict_boundary"].__setitem__("no_layout_at_cap", "TRUE"))
    add("root_full_set", lambda x: x["strict_boundary"].__setitem__("root_full_set_computed", True))
    add("next_gate", lambda x: x.__setitem__("next_gate", "WRONG_GATE"))

    rejected = 0
    for name, mutate in mutations:
        candidate = copy.deepcopy(summary)
        mutate(candidate)
        candidate = repaired_summary(candidate)
        try:
            verify_summary_semantics(
                candidate, manifest, hardening, pairs, refinements, generators, deletions
            )
        except AssertionError:
            rejected += 1
        else:
            raise AssertionError(f"digest-repaired tamper survived: {name}")
    if rejected != 12:
        raise AssertionError("tamper rejection count drift")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("integration_root", type=Path)
    parser.add_argument("hardening_artifact", type=Path)
    parser.add_argument("summary", type=Path)
    parser.add_argument("--producer-source", type=Path, required=True)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()

    verify_static_producer(args.producer_source)
    hardening = verify_bound_json(args.hardening_artifact, PARENT_HARDENING_SHA256)
    if hardening.get("semantic_digest") != PARENT_HARDENING_SEMANTIC:
        raise AssertionError("hardening semantic digest drift")
    manifest = verify_manifest(args.integration_root)
    summary = json.loads(args.summary.read_text())
    pairs = list(verified_records(args.integration_root, manifest, "PAIRS"))
    refinements = list(verified_records(args.integration_root, manifest, "REFINEMENTS"))
    generators = list(verified_records(args.integration_root, manifest, "GENERATORS"))
    deletions = list(verified_records(args.integration_root, manifest, "DELETIONS"))
    verify_summary_semantics(
        summary, manifest, hardening, pairs, refinements, generators, deletions
    )
    if args.tamper_self_test:
        run_tamper_self_test(
            summary, manifest, hardening, pairs, refinements, generators, deletions
        )
    print("JANUS_C049_1_B4_6_3_CORRECTED_NODE6_INTEGRATION_NODE7_PREFLIGHT_VERIFIER = PASS")
    print("NODE6_PAIRS =", len(pairs))
    print("NODE6_REFINEMENTS =", len(refinements))
    print("NODE6_GENERATORS =", len(generators))
    print("NODE7_CHILD_PAIRS =", NODE7_PAIRS)
    print("NODE7_ORDINARY_HV_REFINEMENTS =", NODE7_HV_REFINEMENTS)
    print("INVARIANTS = 14/14")
    print("DIGEST_REPAIRED_TAMPERS_REJECTED = 12/12")
    print("NEXT_GATE =", NEXT_GATE)
    print("CURRENT_GLOBAL_TERMINAL =", TERMINAL)


if __name__ == "__main__":
    main()
