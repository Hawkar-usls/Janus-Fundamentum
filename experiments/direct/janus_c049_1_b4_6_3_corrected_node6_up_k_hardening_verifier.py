#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import itertools
import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA = "C049.1-B4.6.3-CORRECTED-NODE6-UP-K-HARDENING-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
PARENT_HEAD = "243b841f1a3023f0acfb3d8b1e381798f369921b"
PARENT_CERTIFICATE_SHA256 = "bf4a55fe6c645f4a8d0cd0c10341a550c80c76a3464892712268ab20d1ffdee7"
PARENT_CERTIFICATE_SEMANTIC = "9f548aba75fd1d919f3f957174983ac4cf80ce2f32bfcb673946817014f199f8"
PARENT_MANIFEST_DIGEST = "0aab826a3ad35673e786c98fc8bc0dbcffaa698c402015e5958a3d633fe968ac"
PARENT_TRANSCRIPT_ROOT_DIGEST = "5300b299d295c13d9fe6a970bb22994202db35e521785330a97b5b798875381e"
NODE_ID = 6
MAX_COMPACT_LENGTH = 15


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True, order=True)
class Statistic:
    left: tuple[int, ...]
    right: tuple[int, ...]
    value: int


@dataclass
class Ledger:
    counters: dict[str, int] = field(default_factory=dict)

    def charge(self, name: str, amount: int = 1) -> None:
        self.counters[name] = self.counters.get(name, 0) + amount

    def snapshot(self) -> dict[str, int]:
        return dict(sorted(self.counters.items()))


def encode(gamma: Sequence[Statistic]) -> list[dict]:
    return [
        {"left": list(stat.left), "right": list(stat.right), "value": stat.value}
        for stat in gamma
    ]


def decode(raw: Sequence[dict]) -> tuple[Statistic, ...]:
    if not isinstance(raw, list) or not raw:
        raise AssertionError("invalid encoded trajectory")
    gamma = tuple(
        Statistic(
            tuple(int(value) for value in item["left"]),
            tuple(int(value) for value in item["right"]),
            int(item["value"]),
        )
        for item in raw
    )
    if any(stat.value not in (0, 1) for stat in gamma):
        raise AssertionError("trajectory width drift")
    if gamma[0].right != gamma[-1].left:
        raise AssertionError("trajectory endpoint drift")
    return gamma


def trajectory_key(gamma: Sequence[Statistic]) -> tuple:
    return tuple((stat.left, stat.right, stat.value) for stat in gamma)


def skeleton_signature(gamma: Sequence[Statistic]) -> tuple:
    result = []
    for stat in gamma:
        symbol = (stat.left, stat.right)
        if not result or result[-1] != symbol:
            result.append(symbol)
    return tuple(result)


def encode_signature(signature: Sequence[tuple]) -> list[dict]:
    return [{"left": list(left), "right": list(right)} for left, right in signature]


def scalar_compact(values: Sequence[int]) -> bool:
    original = tuple(int(value) for value in values)
    sequence = list(original)
    if not sequence:
        return False
    while True:
        changed = False
        for index in range(1, len(sequence)):
            if sequence[index - 1] == sequence[index]:
                del sequence[index]
                changed = True
                break
        if changed:
            continue
        for start_index in range(len(sequence)):
            for end_index in range(start_index + 2, len(sequence)):
                start = sequence[start_index]
                end = sequence[end_index]
                interior = sequence[start_index + 1 : end_index]
                monotone_interval = (
                    start <= end and all(start <= item <= end for item in interior)
                ) or (
                    start >= end and all(start >= item >= end for item in interior)
                )
                if monotone_interval:
                    del sequence[start_index + 1 : end_index]
                    changed = True
                    break
            if changed:
                break
        if not changed:
            return tuple(sequence) == original


def enumerate_patterns(ledger: Ledger) -> tuple[tuple[int, ...], ...]:
    patterns = set()
    for length in range(1, MAX_COMPACT_LENGTH + 1):
        for values in itertools.product((0, 1), repeat=length):
            ledger.charge("binary_scalar_sequences_tested")
            if scalar_compact(values):
                patterns.add(tuple(values))
    return tuple(sorted(patterns))


def statistic_leq(lower: Statistic, upper: Statistic) -> bool:
    return (
        lower.left == upper.left
        and lower.right == upper.right
        and lower.value <= upper.value
    )


def deterministic_witness(
    lower: Sequence[Statistic], upper: Sequence[Statistic], ledger: Ledger
) -> dict | None:
    ledger.charge("relation_calls")
    parent: dict[tuple[int, int], tuple[int, int] | None] = {}
    for i in range(len(lower)):
        for j in range(len(upper)):
            ledger.charge("lattice_cells")
            if not statistic_leq(lower[i], upper[j]):
                continue
            if i == 0 and j == 0:
                parent[(i, j)] = None
                continue
            for previous in ((i - 1, j - 1), (i - 1, j), (i, j - 1)):
                ledger.charge("lattice_predecessor_tests")
                if previous in parent:
                    parent[(i, j)] = previous
                    break
    terminal = (len(lower) - 1, len(upper) - 1)
    if terminal not in parent:
        return None
    path = []
    cursor: tuple[int, int] | None = terminal
    while cursor is not None:
        path.append(cursor)
        cursor = parent[cursor]
    path.reverse()
    ledger.charge("lattice_path_vertices", len(path))
    ledger.charge("dominance_witnesses")
    return {"path": [[i, j] for i, j in path], "path_length": len(path)}


def witness_valid(
    lower: Sequence[Statistic], upper: Sequence[Statistic], witness: dict
) -> bool:
    path = witness.get("path")
    if not isinstance(path, list) or not path:
        return False
    parsed = []
    for cell in path:
        if not isinstance(cell, list) or len(cell) != 2:
            return False
        i, j = cell
        if not isinstance(i, int) or not isinstance(j, int):
            return False
        if not (0 <= i < len(lower) and 0 <= j < len(upper)):
            return False
        parsed.append((i, j))
    if parsed[0] != (0, 0) or parsed[-1] != (len(lower) - 1, len(upper) - 1):
        return False
    if any(
        (following[0] - current[0], following[1] - current[1])
        not in ((1, 0), (0, 1), (1, 1))
        for current, following in zip(parsed, parsed[1:])
    ):
        return False
    if any(not statistic_leq(lower[i], upper[j]) for i, j in parsed):
        return False
    return witness.get("path_length") == len(parsed)


def verify_chunk(root: Path, metadata: dict) -> dict:
    path = root / metadata["filename"]
    compressed = path.read_bytes()
    if len(compressed) != int(metadata["compressed_bytes"]):
        raise AssertionError("compressed chunk byte mismatch")
    if hashlib.sha256(compressed).hexdigest() != metadata["compressed_sha256"]:
        raise AssertionError("compressed chunk digest mismatch")
    raw = gzip.decompress(compressed)
    if len(raw) != int(metadata["uncompressed_bytes"]):
        raise AssertionError("uncompressed chunk byte mismatch")
    payload = json.loads(raw)
    unsigned = dict(payload)
    claimed = unsigned.pop("chunk_payload_digest", None)
    if claimed != metadata["chunk_payload_digest"] or digest(unsigned) != claimed:
        raise AssertionError("chunk payload digest mismatch")
    if payload["kind"] != metadata["kind"]:
        raise AssertionError("chunk kind mismatch")
    return payload


def load_source(
    transcript_root: Path, parent_certificate_path: Path, ledger: Ledger
) -> tuple[dict, dict, list[dict]]:
    if file_sha256(parent_certificate_path) != PARENT_CERTIFICATE_SHA256:
        raise AssertionError("parent certificate byte digest mismatch")
    parent = json.loads(parent_certificate_path.read_text())
    if parent.get("semantic_digest") != PARENT_CERTIFICATE_SEMANTIC:
        raise AssertionError("parent certificate semantic mismatch")
    parent_proof = parent.get("proof_payload", {})
    if parent_proof.get("result") != "HONEST_OPEN_AT_CORRECTED_NODE6_B2_CAPABILITY":
        raise AssertionError("parent result mismatch")
    if parent_proof.get("next_gate") != "C049.1_B4.6.3_CORRECTED_NODE6_UP_K_HARDENING":
        raise AssertionError("parent next gate mismatch")

    manifest = json.loads((transcript_root / "manifest.json").read_text())
    unsigned = dict(manifest)
    claimed = unsigned.pop("manifest_digest", None)
    if claimed != PARENT_MANIFEST_DIGEST or digest(unsigned) != claimed:
        raise AssertionError("parent manifest mismatch")
    if manifest["chunking"]["transcript_root_digest"] != PARENT_TRANSCRIPT_ROOT_DIGEST:
        raise AssertionError("parent transcript root mismatch")

    records = []
    expected_id = 0
    for metadata in manifest["chunking"]["chunk_groups"]["GENERATORS"]:
        payload = verify_chunk(transcript_root, metadata)
        ledger.charge("generator_chunks_replayed")
        for record in payload["records"]:
            ledger.charge("generator_records_replayed")
            if int(record["generator_id"]) != expected_id:
                raise AssertionError("generator id continuity mismatch")
            expected_id += 1
            body = dict(record)
            claimed_record = body.pop("record_digest", None)
            if digest(body) != claimed_record:
                raise AssertionError("generator record digest mismatch")
            if int(record["node_id"]) == NODE_ID:
                records.append(record)
    if len(records) != 414:
        raise AssertionError("source generator count mismatch")
    return parent, manifest, records


def reachable_catalog(
    signatures: Sequence[tuple], patterns: Sequence[tuple[int, ...]]
) -> tuple[tuple[Statistic, ...], ...]:
    result = set()
    for signature in signatures:
        for choice in itertools.product(patterns, repeat=len(signature)):
            gamma = []
            for (left, right), pattern in zip(signature, choice):
                gamma.extend(Statistic(left, right, value) for value in pattern)
            result.add(tuple(gamma))
    return tuple(sorted(result, key=trajectory_key))


def stream_digest(trajectories: Iterable[Sequence[Statistic]]) -> str:
    hasher = hashlib.sha256()
    for gamma in trajectories:
        hasher.update(canonical_json(encode(gamma)))
        hasher.update(b"\n")
    return hasher.hexdigest()


def verify_artifact(
    transcript_root: Path,
    parent_certificate_path: Path,
    artifact: dict,
    producer_source: Path | None = None,
) -> dict:
    if artifact.get("schema") != SCHEMA:
        raise AssertionError("artifact schema mismatch")
    proof = artifact.get("proof_payload")
    if not isinstance(proof, dict):
        raise AssertionError("proof payload missing")
    if artifact.get("semantic_digest") != digest(proof):
        raise AssertionError("semantic digest mismatch")
    if int(proof.get("certificate_bytes", -1)) <= 0:
        raise AssertionError("certificate accounting missing")

    if producer_source is not None:
        source_text = producer_source.read_text()
        forbidden = (
            "dimension_two_preorder_hardening",
            "node6_up_k_integration_parent_refinement",
            "node7_frontier_compression",
            "node7_thirteen_generator",
            "node8_",
            "node9_",
        )
        if any(token in source_text for token in forbidden):
            raise AssertionError("producer imports or embeds a legacy downstream theorem")

    ledger = Ledger()
    _, _, records = load_source(transcript_root, parent_certificate_path, ledger)
    source = proof.get("source", {})
    expected_source = {
        "parent_pr": 109,
        "parent_exact_head": PARENT_HEAD,
        "parent_certificate_sha256": PARENT_CERTIFICATE_SHA256,
        "parent_certificate_semantic_digest": PARENT_CERTIFICATE_SEMANTIC,
        "parent_manifest_digest": PARENT_MANIFEST_DIGEST,
        "parent_transcript_root_digest": PARENT_TRANSCRIPT_ROOT_DIGEST,
        "parent_result": "HONEST_OPEN_AT_CORRECTED_NODE6_B2_CAPABILITY",
    }
    if source != expected_source:
        raise AssertionError("source binding mismatch")
    if (proof.get("node_id"), proof.get("ambient_dim"), proof.get("k")) != (6, 2, 1):
        raise AssertionError("node parameters mismatch")
    if proof.get("input_generator_count") != 414:
        raise AssertionError("input generator count mismatch")

    trajectories = {}
    trajectory_digests = {}
    for record in records:
        identifier = int(record["generator_id"])
        gamma = decode(record["trajectory_parent_coordinates"])
        if record["trajectory_digest"] != digest(record["trajectory_parent_coordinates"]):
            raise AssertionError("trajectory digest mismatch")
        trajectories[identifier] = gamma
        trajectory_digests[identifier] = record["trajectory_digest"]
        ledger.charge("trajectory_statistics_replayed", len(gamma))
    expected_family_digest = digest(
        sorted(
            (record["trajectory_parent_coordinates"] for record in records),
            key=canonical_json,
        )
    )
    if proof.get("input_generator_family_digest") != expected_family_digest:
        raise AssertionError("input family digest mismatch")

    groups = defaultdict(list)
    for identifier, gamma in trajectories.items():
        groups[skeleton_signature(gamma)].append(identifier)
        ledger.charge("signature_bucket_insertions")
    signatures = tuple(sorted(groups))
    if len(signatures) != 2 or sorted(len(groups[item]) for item in signatures) != [207, 207]:
        raise AssertionError("skeleton partition mismatch")

    partition = proof.get("preorder_partition", {})
    if partition.get("rule") != "COLLAPSED_LEFT_RIGHT_SKELETON_STUTTER_SIGNATURE":
        raise AssertionError("partition rule mismatch")
    if partition.get("bucket_count") != 2 or partition.get("bucket_sizes") != [207, 207]:
        raise AssertionError("partition cardinality mismatch")
    if partition.get("cross_signature_relation_possible") is not False:
        raise AssertionError("cross-signature theorem mismatch")
    buckets = partition.get("buckets")
    if not isinstance(buckets, list) or len(buckets) != 2:
        raise AssertionError("bucket transcript mismatch")

    retained_ids = []
    expected_removal_pairs = set()
    for bucket_index, signature in enumerate(signatures):
        ids = sorted(groups[signature], key=lambda item: trajectory_key(trajectories[item]))
        zero_ids = [
            identifier
            for identifier in ids
            if all(stat.value == 0 for stat in trajectories[identifier])
        ]
        ledger.charge("zero_envelope_tests", len(ids))
        if len(zero_ids) != 1:
            raise AssertionError("unique zero envelope mismatch")
        retained_id = zero_ids[0]
        retained_ids.append(retained_id)
        bucket = buckets[bucket_index]
        if bucket.get("bucket_index") != bucket_index:
            raise AssertionError("bucket index mismatch")
        if bucket.get("collapsed_skeleton_signature") != encode_signature(signature):
            raise AssertionError("bucket signature mismatch")
        if bucket.get("signature_digest") != digest(encode_signature(signature)):
            raise AssertionError("bucket signature digest mismatch")
        if bucket.get("input_generator_count") != 207:
            raise AssertionError("bucket size mismatch")
        if bucket.get("retained_generator_id") != retained_id:
            raise AssertionError("retained generator id mismatch")
        if bucket.get("retained_trajectory") != encode(trajectories[retained_id]):
            raise AssertionError("retained trajectory mismatch")
        if bucket.get("retained_trajectory_digest") != trajectory_digests[retained_id]:
            raise AssertionError("retained digest mismatch")
        if bucket.get("zero_envelope_unique") is not True:
            raise AssertionError("zero-envelope flag mismatch")
        if bucket.get("distinct_skeleton_runs") is not True:
            raise AssertionError("skeleton distinctness mismatch")
        for removed_id in ids:
            if removed_id != retained_id:
                expected_removal_pairs.add((bucket_index, removed_id, retained_id))

    if proof.get("retained_generator_ids") != retained_ids:
        raise AssertionError("retained id list mismatch")
    if proof.get("retained_generators") != [encode(trajectories[item]) for item in retained_ids]:
        raise AssertionError("retained generator transcript mismatch")
    if proof.get("retained_generator_count") != 2:
        raise AssertionError("retained count mismatch")

    removals = proof.get("removals")
    if not isinstance(removals, list) or len(removals) != 412:
        raise AssertionError("removal transcript cardinality mismatch")
    seen_pairs = set()
    for removal_id, removal in enumerate(removals):
        if removal.get("removal_id") != removal_id:
            raise AssertionError("removal id mismatch")
        unsigned = dict(removal)
        claimed = unsigned.pop("removal_digest", None)
        if digest(unsigned) != claimed:
            raise AssertionError("removal digest mismatch")
        pair = (
            int(removal["bucket_index"]),
            int(removal["removed_generator_id"]),
            int(removal["retained_generator_id"]),
        )
        if pair not in expected_removal_pairs or pair in seen_pairs:
            raise AssertionError("removal provenance mismatch")
        seen_pairs.add(pair)
        _, removed_id, retained_id = pair
        lower = trajectories[retained_id]
        upper = trajectories[removed_id]
        witness = removal.get("direct_witness", {})
        if not witness_valid(lower, upper, witness):
            raise AssertionError("supplied removal witness invalid")
        recomputed = deterministic_witness(lower, upper, ledger)
        reverse = deterministic_witness(upper, lower, ledger)
        if witness != recomputed or reverse is not None:
            raise AssertionError("removal relation replay mismatch")
        if removal.get("reverse_relation") is not False:
            raise AssertionError("reverse relation flag mismatch")
        if removal.get("removed_trajectory_digest") != trajectory_digests[removed_id]:
            raise AssertionError("removed trajectory digest mismatch")
        if removal.get("retained_trajectory_digest") != trajectory_digests[retained_id]:
            raise AssertionError("retained trajectory digest mismatch")
    if seen_pairs != expected_removal_pairs or proof.get("removal_count") != 412:
        raise AssertionError("removal completeness mismatch")

    cross_tests = 0
    cross_relations = 0
    for left_id in groups[signatures[0]]:
        for right_id in groups[signatures[1]]:
            for lower_id, upper_id in ((left_id, right_id), (right_id, left_id)):
                cross_tests += 1
                if deterministic_witness(
                    trajectories[lower_id], trajectories[upper_id], ledger
                ) is not None:
                    cross_relations += 1
    if (cross_tests, cross_relations) != (85698, 0):
        raise AssertionError("cross-signature exhaustive replay mismatch")
    if partition.get("ordered_cross_signature_tests") != cross_tests:
        raise AssertionError("cross-signature work receipt mismatch")
    if partition.get("cross_signature_relations_found") != 0:
        raise AssertionError("cross-signature result receipt mismatch")

    patterns = enumerate_patterns(ledger)
    expected_patterns = ((0,), (0, 1), (0, 1, 0), (1,), (1, 0), (1, 0, 1))
    if patterns != expected_patterns:
        raise AssertionError("independent scalar typical catalog mismatch")
    closure = proof.get("exact_reachable_closure", {})
    if closure.get("binary_typical_run_patterns") != [list(item) for item in patterns]:
        raise AssertionError("scalar pattern transcript mismatch")
    if closure.get("binary_typical_run_pattern_count") != 6:
        raise AssertionError("scalar pattern count mismatch")
    if closure.get("binary_scalar_sequences_exhaustively_tested") != 65534:
        raise AssertionError("scalar exhaustive work mismatch")

    catalog = reachable_catalog(signatures, patterns)
    if len(catalog) != 432:
        raise AssertionError("independent reachable catalog size mismatch")
    if closure.get("complete_reachable_catalog_size") != 432:
        raise AssertionError("reachable catalog receipt mismatch")
    if closure.get("complete_reachable_catalog_stream_sha256") != stream_digest(catalog):
        raise AssertionError("reachable catalog stream mismatch")

    entries = closure.get("reachable_entries")
    if not isinstance(entries, list) or len(entries) != 432:
        raise AssertionError("reachable entry transcript mismatch")
    if closure.get("reachable_entries_digest") != digest(entries):
        raise AssertionError("reachable entry digest mismatch")
    source_by_signature = {
        skeleton_signature(trajectories[identifier]): index
        for index, identifier in enumerate(retained_ids)
    }
    for index, candidate in enumerate(catalog):
        entry = entries[index]
        if entry.get("trajectory") != encode(candidate):
            raise AssertionError("reachable trajectory ordering mismatch")
        source_index = source_by_signature[skeleton_signature(candidate)]
        if entry.get("source_generator_index") != source_index:
            raise AssertionError("reachable source index mismatch")
        lower = trajectories[retained_ids[source_index]]
        witness = entry.get("witness", {})
        if not witness_valid(lower, candidate, witness):
            raise AssertionError("reachable witness invalid")
        if witness != deterministic_witness(lower, candidate, ledger):
            raise AssertionError("reachable witness deterministic replay mismatch")

    original_set = {trajectory_key(gamma) for gamma in trajectories.values()}
    catalog_set = {trajectory_key(gamma) for gamma in catalog}
    if not original_set < catalog_set:
        raise AssertionError("input strict-subset theorem mismatch")
    missing = catalog_set - original_set
    missing_by_signature = defaultdict(int)
    for key in missing:
        gamma = tuple(Statistic(left, right, value) for left, right, value in key)
        missing_by_signature[skeleton_signature(gamma)] += 1
    if len(missing) != 18 or sorted(missing_by_signature.values()) != [9, 9]:
        raise AssertionError("new reachable entries mismatch")
    if closure.get("input_generator_set_size") != 414:
        raise AssertionError("input set size receipt mismatch")
    if closure.get("input_generator_set_is_strict_subset") is not True:
        raise AssertionError("strict-subset receipt mismatch")
    if closure.get("new_reachable_entries_beyond_input") != 18:
        raise AssertionError("new entry count receipt mismatch")
    if closure.get("new_reachable_entries_per_bucket") != [9, 9]:
        raise AssertionError("new entry bucket receipt mismatch")
    if closure.get("up_k_original_equals_up_k_retained") is not True:
        raise AssertionError("up_k equality receipt mismatch")
    if closure.get("closure_complete") is not True:
        raise AssertionError("closure completeness receipt mismatch")

    work = proof.get("work_ledger", {})
    if work.get("counters") != ledger.snapshot():
        raise AssertionError("work ledger mismatch")
    if work.get("total_charged_operations") != sum(ledger.counters.values()):
        raise AssertionError("total work mismatch")
    if work.get("monotone") is not True:
        raise AssertionError("work monotonicity mismatch")

    expected_invariants = {
        f"CNUK-INV-{index:02d}": "PASS" for index in range(1, 15)
    }
    if proof.get("invariant_vector") != expected_invariants:
        raise AssertionError("invariant vector mismatch")
    legacy = proof.get("legacy_inputs", {})
    if set(legacy) != {
        "legacy_node6_generator_family_consumed",
        "legacy_node6_up_k_closure_consumed",
        "legacy_node7_full_set_consumed",
        "legacy_downstream_counts_promoted",
    } or any(legacy.values()):
        raise AssertionError("legacy input boundary mismatch")

    strict = proof.get("strict_boundary", {})
    expected_strict = {
        "pr109_corrected_first_join_admitted": True,
        "corrected_node6_parent_refinement_complete": True,
        "corrected_node6_parent_up_k_complete": True,
        "corrected_node6_full_set_entry_count": 432,
        "corrected_bottom_up_replay_complete": False,
        "corrected_node7_parent_refinement_complete": False,
        "root_structural_compression_admitted": False,
        "root_parent_refinement_complete": False,
        "root_full_set_computed": False,
        "root_empty_proved": False,
        "found_layout": "FORBIDDEN",
        "no_layout_at_cap": "FORBIDDEN",
        "current_global_terminal": TERMINAL,
        "p_vs_np": "OPEN",
    }
    if strict != expected_strict:
        raise AssertionError("strict boundary mismatch")
    if proof.get("result") != "CORRECTED_NODE6_UP_K_CLOSURE_COMPUTED":
        raise AssertionError("result mismatch")
    if proof.get("next_gate") != (
        "C049.1_B4.6.3_CORRECTED_NODE6_INTEGRATION_AND_NODE7_PARENT_REFINEMENT"
    ):
        raise AssertionError("next gate mismatch")

    return {
        "input_generators": 414,
        "retained_generators": 2,
        "removals": 412,
        "reachable_entries": 432,
        "new_reachable_entries": 18,
        "cross_signature_tests": 85698,
        "invariants": "14/14",
    }


def repair_artifact(artifact: dict) -> dict:
    value = copy.deepcopy(artifact)
    proof = value["proof_payload"]
    proof["certificate_bytes"] = 0
    while True:
        value["semantic_digest"] = digest(proof)
        raw = json.dumps(value, indent=2, sort_keys=True).encode() + b"\n"
        size = len(raw)
        if proof["certificate_bytes"] == size:
            return value
        proof["certificate_bytes"] = size


def tamper_self_test(
    transcript_root: Path,
    parent_certificate: Path,
    artifact: dict,
    producer_source: Path | None,
) -> int:
    mutations = []

    def add(name, mutate):
        candidate = copy.deepcopy(artifact)
        mutate(candidate["proof_payload"])
        mutations.append((name, repair_artifact(candidate)))

    add("parent-head", lambda p: p["source"].__setitem__("parent_exact_head", "0" * 40))
    add("input-count", lambda p: p.__setitem__("input_generator_count", 413))
    add("bucket-count", lambda p: p["preorder_partition"].__setitem__("bucket_count", 3))
    add("retained-count", lambda p: p.__setitem__("retained_generator_count", 3))
    add("removal-count", lambda p: p.__setitem__("removal_count", 411))
    add(
        "cross-relation",
        lambda p: p["preorder_partition"].__setitem__(
            "cross_signature_relations_found", 1
        ),
    )
    add(
        "pattern-count",
        lambda p: p["exact_reachable_closure"].__setitem__(
            "binary_typical_run_pattern_count", 5
        ),
    )
    add(
        "catalog-size",
        lambda p: p["exact_reachable_closure"].__setitem__(
            "complete_reachable_catalog_size", 431
        ),
    )
    add(
        "new-entry-count",
        lambda p: p["exact_reachable_closure"].__setitem__(
            "new_reachable_entries_beyond_input", 17
        ),
    )
    add(
        "entry-witness",
        lambda p: p["exact_reachable_closure"]["reachable_entries"][0][
            "witness"
        ].__setitem__("path", [[0, 0]]),
    )
    add(
        "up-k-boundary",
        lambda p: p["strict_boundary"].__setitem__(
            "corrected_node6_parent_up_k_complete", False
        ),
    )
    add("p-vs-np", lambda p: p["strict_boundary"].__setitem__("p_vs_np", "CLOSED"))

    rejected = 0
    for name, candidate in mutations:
        try:
            verify_artifact(
                transcript_root,
                parent_certificate,
                candidate,
                producer_source,
            )
        except Exception:
            rejected += 1
        else:
            raise AssertionError(f"digest-repaired tamper accepted: {name}")
    return rejected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("transcript_root", type=Path)
    parser.add_argument("parent_certificate", type=Path)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--producer-source", type=Path)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()

    raw = args.artifact.read_bytes()
    artifact = json.loads(raw)
    if int(artifact["proof_payload"].get("certificate_bytes", -1)) != len(raw):
        raise AssertionError("certificate byte fixed point mismatch")
    summary = verify_artifact(
        args.transcript_root,
        args.parent_certificate,
        artifact,
        args.producer_source,
    )
    rejected = 0
    if args.tamper_self_test:
        rejected = tamper_self_test(
            args.transcript_root,
            args.parent_certificate,
            artifact,
            args.producer_source,
        )
        if rejected != 12:
            raise AssertionError("tamper rejection count mismatch")

    print("JANUS_C049_1_B4_6_3_CORRECTED_NODE6_UP_K_HARDENING_VERIFIER = PASS")
    print("INPUT_GENERATORS =", summary["input_generators"])
    print("RETAINED_GENERATORS =", summary["retained_generators"])
    print("DIRECT_REMOVALS =", summary["removals"])
    print("REACHABLE_ENTRIES =", summary["reachable_entries"])
    print("NEW_REACHABLE_ENTRIES =", summary["new_reachable_entries"])
    print("CROSS_SIGNATURE_TESTS =", summary["cross_signature_tests"])
    print("INVARIANTS =", summary["invariants"])
    print("DIGEST_REPAIRED_TAMPERS_REJECTED =", f"{rejected}/12")
    print(
        "NEXT_GATE = C049.1_B4.6.3_CORRECTED_NODE6_INTEGRATION_AND_NODE7_PARENT_REFINEMENT"
    )
    print("CURRENT_GLOBAL_TERMINAL =", TERMINAL)


if __name__ == "__main__":
    main()
