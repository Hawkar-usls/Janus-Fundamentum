from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import janus_c049_1_b2_up_k_core as b2
import janus_c049_1_b3_expand_join_shrink_core as b3

# The historical v1 verifier imported names from B2 that are not the runtime
# API used by admitted B5.1.  Install the exact B3 runtime functions before
# importing the historical replay scaffold; the v1.1 verifier replaces all
# up_k/witness-specific validation below.
b2.extension_witness = b3.extension_preorder_witness
b2.up_k = b3.up_k

import janus_c049_1_b5_2a_generic_algorithm2_provenance_carrier_verifier as basev

AMENDMENT_SCHEMA = "janus.c049_1.b5_2a.generic_algorithm2_provenance_carrier_amendment.v1_1"
SCHEMA = "janus.c049_1.b5_2a.generic_algorithm2_provenance_carrier.v1_1"
BASE_SPEC_PATH = Path("experiments/direct/C049_1_B5_2A_GENERIC_ALGORITHM2_PROVENANCE_CARRIER_SPEC_V1.json")


def cb(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def dg(value: Any) -> str:
    return hashlib.sha256(cb(value)).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def normalized_source_map(
    generators: Sequence[Sequence[b3.Statistic]], boundary: Sequence[int], ambient_dim: int, k: int
) -> tuple[list[int], list[tuple[b3.Statistic, ...]]]:
    mapping: list[int] = []
    normalized: list[tuple[b3.Statistic, ...]] = []
    B = b3.xor_basis(boundary, ambient_dim)
    for original_index, generator in enumerate(generators):
        compact, _ = b3.compactify(generator)
        b3.decode_trajectory(b3.encode_trajectory(compact), B, ambient_dim, require_compact=True)
        if b3.width(compact) <= k:
            mapping.append(original_index)
            normalized.append(compact)
    return mapping, normalized


def expected_up_label(
    witness: dict,
    normalized_source: Sequence[b3.Statistic],
    target: Sequence[b3.Statistic],
    b5_1_source_index: int,
    original_generator_index: int,
) -> dict:
    path = witness.get("path")
    if not isinstance(path, list) or not path:
        raise AssertionError("empty canonical pair-list extension witness")
    if witness.get("path_length") != len(path):
        raise AssertionError("canonical extension witness path length")
    if path[0] != [0, 0] or path[-1] != [len(normalized_source) - 1, len(target) - 1]:
        raise AssertionError("canonical extension witness endpoints")

    native: list[list[int]] = []
    one_based: list[list[int]] = []
    slack: list[int] = []
    selected: list[int] = []
    previous_lower: int | None = None
    previous_pair: tuple[int, int] | None = None

    for position, point in enumerate(path):
        if not isinstance(point, list) or len(point) != 2:
            raise AssertionError("extension witness point is not an integer pair")
        lower_index, upper_index = int(point[0]), int(point[1])
        if not (0 <= lower_index < len(normalized_source) and 0 <= upper_index < len(target)):
            raise AssertionError("extension witness point outside source/target")
        pair = (lower_index, upper_index)
        if previous_pair is not None:
            step = (pair[0] - previous_pair[0], pair[1] - previous_pair[1])
            if step not in {(1, 0), (0, 1), (1, 1)}:
                raise AssertionError("illegal extension-preorder step")
        lower_stat = normalized_source[lower_index]
        upper_stat = target[upper_index]
        if not b3.statistic_leq(lower_stat, upper_stat):
            raise AssertionError("extension-preorder statistic comparison failed")
        value = int(upper_stat.value) - int(lower_stat.value)
        if value < 0:
            raise AssertionError("negative Algorithm2 slack")
        native.append([lower_index, upper_index])
        one_based.append([lower_index + 1, upper_index + 1])
        slack.append(value)
        if value == 0 and (position == 0 or lower_index != previous_lower):
            selected.append(lower_index)
        previous_lower = lower_index
        previous_pair = pair

    replayed = b3.extension_preorder_witness(normalized_source, target)
    if replayed != witness:
        raise AssertionError("canonical B3 extension witness replay mismatch")

    return {
        "native_zero_based_path": native,
        "paper_one_based_path": one_based,
        "slack_sequence": slack,
        "zero_slack_child_positions_zero_based": selected,
        "b5_1_source_index": int(b5_1_source_index),
        "original_generator_index": int(original_generator_index),
        "source_trajectory_digest": dg(b3.encode_trajectory(normalized_source)),
        "witness_digest": dg(witness),
    }


def validate_carrier_entries_v11(c_entries, generators, boundary, d, k):
    if not generators:
        expected_entries: list[dict] = []
        mapping: list[int] = []
        normalized: list[tuple[b3.Statistic, ...]] = []
    else:
        receipt = b3.up_k(generators, boundary, d, k)
        expected_entries = basev.normalize_entries(receipt)
        mapping, normalized = normalized_source_map(generators, boundary, d, k)
        if receipt["generator_count"] != len(mapping):
            raise AssertionError("runtime normalized generator count/source map mismatch")

    if len(c_entries) != len(expected_entries):
        raise AssertionError("carrier up_k count")

    for entry_index, (carrier, expected) in enumerate(zip(c_entries, expected_entries)):
        normalized_index = int(expected["source_index"])
        if not 0 <= normalized_index < len(mapping):
            raise AssertionError("B5.1 source index outside independently rebuilt map")
        original_index = int(mapping[normalized_index])
        source = normalized[normalized_index]
        target = b3.decode_trajectory(expected["trajectory"], boundary, d, require_compact=True)

        if carrier.get("entry_index") != entry_index:
            raise AssertionError("carrier entry index")
        if carrier.get("trajectory") != expected["trajectory"] or carrier.get("trajectory_digest") != dg(expected["trajectory"]):
            raise AssertionError("carrier trajectory")
        if int(carrier.get("b5_1_source_index", -1)) != normalized_index:
            raise AssertionError("B5.1 normalized source index")
        if int(carrier.get("source_index", -1)) != original_index:
            raise AssertionError("original generator source index")
        if carrier.get("source_trajectory") != b3.encode_trajectory(source):
            raise AssertionError("normalized source trajectory")
        if carrier.get("extension_witness") != expected["witness"]:
            raise AssertionError("canonical extension witness bytes")

        label = expected_up_label(
            expected["witness"], source, target, normalized_index, original_index
        )
        if carrier.get("algorithm2_up_label") != label:
            raise AssertionError("Algorithm2 up label")

    return expected_entries


def expected_amendment_payload(amendment: dict) -> dict:
    return {
        "schema": AMENDMENT_SCHEMA,
        "base_spec_git_blob": amendment["base_spec"]["git_blob"],
        "runtime_up_k_authority": amendment["corrections"]["runtime_up_k_authority"],
        "canonical_extension_witness_schema": amendment["corrections"]["canonical_extension_witness_schema"],
        "source_index_dual_binding": amendment["corrections"]["source_index_dual_binding"],
        "negative_provenance": amendment["negative_provenance"],
        "factor_order_emitted": False,
        "found_layout": "FORBIDDEN",
    }


def install_v11_verifier() -> None:
    basev.SCHEMA = SCHEMA
    basev.validate_carrier_entries = validate_carrier_entries_v11


def verify_v11(candidate: dict, raw: dict, subject: dict, amendment: dict) -> int:
    if amendment.get("schema") != AMENDMENT_SCHEMA:
        raise AssertionError("wrong amendment schema")
    if amendment.get("status") != "AMENDMENT_FROZEN_SUPERSEDES_V1_RUNTIME_BINDING_DETAILS":
        raise AssertionError("amendment not frozen")
    if git_blob(BASE_SPEC_PATH) != amendment["base_spec"]["git_blob"]:
        raise AssertionError("base spec blob mismatch")
    if amendment["corrections"]["published_source_title"] != "The art of trellis decoding is fixed-parameter tractable":
        raise AssertionError("published source title correction missing")
    if amendment["corrections"]["runtime_up_k_authority"]["actual_b5_1_import"] != "janus_c049_1_b3_expand_join_shrink_core.up_k":
        raise AssertionError("wrong runtime up_k authority")

    base_spec = load(BASE_SPEC_PATH)
    install_v11_verifier()
    roots = basev.verify(candidate, raw, subject, base_spec)

    payload = candidate["proof_payload"]
    if payload.get("carrier_amendment_v1_1") != expected_amendment_payload(amendment):
        raise AssertionError("carrier v1.1 amendment binding")
    if payload["carrier_amendment_v1_1"]["factor_order_emitted"] is not False:
        raise AssertionError("factor order promotion")
    if payload["carrier_amendment_v1_1"]["found_layout"] != "FORBIDDEN":
        raise AssertionError("FOUND_LAYOUT promotion")
    return roots


def repair(candidate: dict) -> dict:
    candidate["semantic_digest"] = dg(candidate["proof_payload"])
    return candidate


def tamper_suite_v11(base: dict, raw: dict, subject: dict, amendment: dict) -> tuple[int, int]:
    attacks: list[tuple[str, dict]] = []

    def add(name, mutation):
        candidate = copy.deepcopy(base)
        mutation(candidate["proof_payload"])
        attacks.append((name, repair(candidate)))

    def first_entry(payload, stage="final_entries"):
        for node in payload["node_carriers"]:
            if node.get(stage):
                return node[stage][0]
        raise AssertionError("no carrier entry for tamper")

    def internal(payload):
        return next(node for node in payload["node_carriers"] if node["kind"] == "internal")

    add("T01_SUBJECT", lambda p: p["subject"].__setitem__("b5_1_root_entry_count", p["subject"]["b5_1_root_entry_count"] + 1))
    add("T02_REMOVE_FINAL_CERT", lambda p: next(n for n in p["node_carriers"] if n["final_entries"])["final_entries"].pop())
    add("T03_ORIGINAL_SOURCE", lambda p: first_entry(p).__setitem__("source_index", 999))

    def mutate_pair_path(payload):
        path = first_entry(payload)["extension_witness"]["path"]
        path[0][1] = 999
    add("T04_PAIR_LIST_EXTENSION_PATH", mutate_pair_path)

    add("T05_SLACK", lambda p: first_entry(p)["algorithm2_up_label"]["slack_sequence"].__setitem__(0, 999))
    add("T06_ZERO_SLACK", lambda p: first_entry(p)["algorithm2_up_label"].__setitem__("zero_slack_child_positions_zero_based", [999]))
    add("T07_SHRINK_REF", lambda p: internal(p)["shrink_generators"][0].__setitem__("joined_entry_index", 999))
    add("T08_SHRINK_OUTPUT", lambda p: internal(p)["shrink_generators"][0].__setitem__("shrunk_generator", []))
    add("T09_JOINED_SOURCE", lambda p: internal(p)["joined_entries"][0].__setitem__("source_index", 999))
    add("T10_JOIN_LEFT", lambda p: internal(p)["successful_join_generators"][0].__setitem__("left_expanded_entry_index", 999))
    add("T11_JOIN_RIGHT", lambda p: internal(p)["successful_join_generators"][0].__setitem__("right_expanded_entry_index", 999))

    def diagonal_join(payload):
        record = internal(payload)["successful_join_generators"][0]
        path = record["path"]
        if len(path) > 1:
            path[1] = [1, 1]
        else:
            path.append([1, 1])
    add("T12_DIAGONAL_JOIN", diagonal_join)

    add("T13_JOIN_TRAJECTORY", lambda p: internal(p)["successful_join_generators"][0].__setitem__("joined_generator", []))
    add("T14_EXPANDED_SOURCE", lambda p: internal(p)["left_expanded_entries"][0].__setitem__("source_index", 999))
    add("T15_TRANSPORT_REF", lambda p: internal(p)["left_transport_generators"][0].__setitem__("child_output_entry_index", 999))
    add("T16_TRANSPORT_OUTPUT", lambda p: internal(p)["left_transport_generators"][0].__setitem__("transported_generator", []))
    add("T17_BACKTRACK_CYCLE", lambda p: p["root_entry_backtracks"][0].__setitem__("left_child", copy.deepcopy(p["root_entry_backtracks"][0])))
    add("T18_OMIT_ROOT_ANCESTRY", lambda p: p["root_entry_backtracks"].pop())
    add("T19_AFFINE_IDENTITY", lambda p: p["canonical_factor_catalog"][0].__setitem__("affine_offset", {"tamper": True}))
    add("T20_FACTOR_ORDER", lambda p: p["algorithm2_boundary"].update({"factor_order_emitted": True, "factor_order": ["fake"], "found_layout": "TRUE"}))
    add("T21_PROMOTION", lambda p: p["strict_boundary"].update({"generic_no_layout_at_cap_enabled": True, "polynomial_runtime_claim": "TRUE", "b5_complete": True, "p_vs_np": "CLOSED"}))
    add("T22_SOURCE_MAP_DESYNC", lambda p: first_entry(p).__setitem__("b5_1_source_index", 999))

    rejected = 0
    for name, candidate in attacks:
        try:
            verify_v11(candidate, raw, subject, amendment)
        except Exception:
            rejected += 1
            continue
        raise AssertionError(name + " survived")
    return rejected, len(attacks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--b5-1-artifact", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--tamper-suite", action="store_true")
    args = parser.parse_args()

    amendment = load(args.spec)
    raw = load(args.input)
    subject = load(args.b5_1_artifact)
    candidate = load(args.candidate)
    roots = verify_v11(candidate, raw, subject, amendment)

    print("JANUS_B5_2A_GENERIC_ALGORITHM2_PROVENANCE_CARRIER_V1_1_INDEPENDENT_VERIFIER = PASS")
    print("CANONICAL_PAIR_LIST_EXTENSION_WITNESSES = PASS")
    print("NORMALIZED_SOURCE_TO_ORIGINAL_GENERATOR_MAP = PASS")
    print("ROOT_ENTRIES_WITH_COMPLETE_BACKTRACK =", roots)
    print("DANGLING_REFERENCE_COUNT = 0")
    print("CYCLE_COUNT = 0")
    print("ALGORITHM2_UP_LABELS = PASS")
    print("JOIN_HV_LABELS = PASS")
    print("SEMANTIC_PROJECTION_TO_B5_1 = PASS")
    print("FACTOR_ORDER_EMITTED = FALSE")
    print("FOUND_LAYOUT = FORBIDDEN")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")

    if args.tamper_suite:
        rejected, total = tamper_suite_v11(candidate, raw, subject, amendment)
        print(f"DIGEST_REPAIRED_TAMPERS_REJECTED = {rejected}/{total}")


if __name__ == "__main__":
    main()
