from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any, Sequence

import janus_c049_1_b3_expand_join_shrink_core as b3
import janus_c049_1_b5_2a_generic_algorithm2_provenance_carrier as base

AMENDMENT_SCHEMA = "janus.c049_1.b5_2a.generic_algorithm2_provenance_carrier_amendment.v1_1"
SCHEMA = "janus.c049_1.b5_2a.generic_algorithm2_provenance_carrier.v1_1"
BASE_SPEC_PATH = Path("experiments/direct/C049_1_B5_2A_GENERIC_ALGORITHM2_PROVENANCE_CARRIER_SPEC_V1.json")

_ORIGINAL_SAFE_UP_K = base.safe_up_k


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


def safe_up_k_v11(generators, boundary, ambient_dim, k, caps, stage):
    receipt, status = _ORIGINAL_SAFE_UP_K(generators, boundary, ambient_dim, k, caps, stage)
    if receipt is None:
        return receipt, status
    mapping, normalized = normalized_source_map(generators, boundary, ambient_dim, k)
    if receipt.get("generator_count", 0) != len(mapping):
        raise AssertionError("B5.1 normalized generator count/source-map mismatch")
    for entry in receipt.get("entries", []):
        normalized_index = int(entry["source_index"])
        if not 0 <= normalized_index < len(mapping):
            raise AssertionError("B5.1 source index outside normalized source map")
        original_index = mapping[normalized_index]
        entry["b5_1_source_index"] = normalized_index
        entry["original_source_index"] = original_index
        entry["source_trajectory"] = b3.encode_trajectory(normalized[normalized_index])
    receipt["normalized_source_to_original_generator_index"] = mapping
    return receipt, status


def normalized_entries_v11(receipt: dict) -> list[dict]:
    out = []
    for entry in receipt.get("entries", []):
        normalized_index = int(entry.get("b5_1_source_index", entry["source_index"]))
        original_index = int(entry.get("original_source_index", normalized_index))
        source_trajectory = entry.get("source_trajectory")
        if source_trajectory is None:
            raise AssertionError("missing normalized source trajectory in provenance-rich up_k receipt")
        out.append(
            {
                "trajectory": entry["trajectory"],
                "source_index": original_index,
                "b5_1_source_index": normalized_index,
                "original_source_index": original_index,
                "source_trajectory": source_trajectory,
                "witness": entry["witness"],
            }
        )
    return sorted(
        out,
        key=lambda e: (
            base.digest(e["trajectory"]),
            e["b5_1_source_index"],
            base.digest(e["witness"]),
        ),
    )


def up_label_v11(entry: dict) -> dict:
    witness = entry["witness"]
    path = witness.get("path")
    source = entry["source_trajectory"]
    target = entry["trajectory"]
    if not isinstance(path, list) or not path:
        raise AssertionError("empty canonical pair-list extension witness")
    if witness.get("path_length") != len(path):
        raise AssertionError("extension witness path length mismatch")

    native: list[list[int]] = []
    one_based: list[list[int]] = []
    slack: list[int] = []
    selected: list[int] = []
    previous_lower: int | None = None
    for position, point in enumerate(path):
        if not isinstance(point, list) or len(point) != 2:
            raise AssertionError("canonical extension witness point must be an integer pair")
        lower_index, upper_index = int(point[0]), int(point[1])
        if not (0 <= lower_index < len(source) and 0 <= upper_index < len(target)):
            raise AssertionError("extension witness point outside source/target trajectory")
        value = int(target[upper_index]["value"]) - int(source[lower_index]["value"])
        if value < 0:
            raise AssertionError("negative Algorithm2 slack")
        native.append([lower_index, upper_index])
        one_based.append([lower_index + 1, upper_index + 1])
        slack.append(value)
        if value == 0 and (position == 0 or lower_index != previous_lower):
            selected.append(lower_index)
        previous_lower = lower_index

    return {
        "native_zero_based_path": native,
        "paper_one_based_path": one_based,
        "slack_sequence": slack,
        "zero_slack_child_positions_zero_based": selected,
        "b5_1_source_index": int(entry["b5_1_source_index"]),
        "original_generator_index": int(entry["original_source_index"]),
        "source_trajectory_digest": base.digest(source),
        "witness_digest": base.digest(witness),
    }


def carrier_entries_v11(entries: Sequence[dict]) -> list[dict]:
    out = []
    for entry_index, entry in enumerate(entries):
        out.append(
            {
                "entry_index": entry_index,
                "trajectory": entry["trajectory"],
                "trajectory_digest": base.digest(entry["trajectory"]),
                "source_index": int(entry["original_source_index"]),
                "b5_1_source_index": int(entry["b5_1_source_index"]),
                "source_trajectory": entry["source_trajectory"],
                "extension_witness": entry["witness"],
                "algorithm2_up_label": up_label_v11(entry),
            }
        )
    return out


def install_v11_runtime() -> None:
    base.safe_up_k = safe_up_k_v11
    base.normalized_entries = normalized_entries_v11
    base.up_label = up_label_v11
    base.carrier_entries = carrier_entries_v11
    base.SCHEMA = SCHEMA


def build(raw: dict, subject: dict, amendment: dict) -> dict:
    if amendment.get("schema") != AMENDMENT_SCHEMA:
        raise AssertionError("wrong B5.2A v1.1 amendment schema")
    if amendment.get("status") != "AMENDMENT_FROZEN_SUPERSEDES_V1_RUNTIME_BINDING_DETAILS":
        raise AssertionError("B5.2A amendment not frozen")
    if git_blob(BASE_SPEC_PATH) != amendment["base_spec"]["git_blob"]:
        raise AssertionError("base B5.2A spec blob mismatch")
    base_spec = base.load(BASE_SPEC_PATH)
    install_v11_runtime()
    artifact = base.build(raw, subject, base_spec)
    artifact["schema"] = SCHEMA
    payload = artifact["proof_payload"]
    payload["carrier_amendment_v1_1"] = {
        "schema": AMENDMENT_SCHEMA,
        "base_spec_git_blob": amendment["base_spec"]["git_blob"],
        "runtime_up_k_authority": amendment["corrections"]["runtime_up_k_authority"],
        "canonical_extension_witness_schema": amendment["corrections"]["canonical_extension_witness_schema"],
        "source_index_dual_binding": amendment["corrections"]["source_index_dual_binding"],
        "negative_provenance": amendment["negative_provenance"],
        "factor_order_emitted": False,
        "found_layout": "FORBIDDEN",
    }
    artifact["semantic_digest"] = base.digest(payload)
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--b5-1-artifact", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifact = build(base.load(args.input), base.load(args.b5_1_artifact), base.load(args.spec))
    base.save(artifact, args.output)
    payload = artifact["proof_payload"]
    summary = payload["backtracking_summary"]
    projection = payload["semantic_projection"]
    print("JANUS_B5_2A_GENERIC_ALGORITHM2_PROVENANCE_CARRIER_V1_1 = PASS")
    print("CANONICAL_PAIR_LIST_WITNESS_ADAPTER = PASS")
    print("NORMALIZED_SOURCE_TO_ORIGINAL_GENERATOR_MAP = PASS")
    print("ROOT_ENTRIES =", summary["root_entries"])
    print("ROOT_ENTRIES_WITH_COMPLETE_BACKTRACK =", summary["root_entries_with_complete_backtrack"])
    print("DANGLING_REFERENCE_COUNT =", summary["dangling_reference_count"])
    print("SEMANTIC_PROJECTION_NODE_DIGESTS =", f"{projection['node_digest_count_matches']}/{projection['node_count']}")
    print("SEMANTIC_PROJECTION_NODE_COUNTS =", f"{projection['node_entry_count_matches']}/{projection['node_count']}")
    print("FACTOR_ORDER_EMITTED = FALSE")
    print("FOUND_LAYOUT = FORBIDDEN")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")
    print("SEMANTIC_DIGEST =", artifact["semantic_digest"])


if __name__ == "__main__":
    main()
