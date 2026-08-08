from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import janus_c049_1_b3_expand_join_shrink_core as b3

SCHEMA = "janus.c049_1.b5_2b.generic_algorithm2_printorder_reconstruction_candidate.v1"
SPEC_SCHEMA = "janus.c049_1.b5_2b.generic_algorithm2_printorder_reconstruction_spec.v1"
CARRIER_SCHEMA = "janus.c049_1.b5_2a.generic_algorithm2_provenance_carrier.v1_1"
B5_1_SCHEMA = "janus.c049_1.b5_1.generic_corrected_runtime_trace.v1"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save(value: Any, path: Path) -> None:
    path.write_bytes(canonical_bytes(value) + b"\n")


def id_key(value: Any) -> str:
    return canonical_bytes(value).decode("utf-8")


def trajectory_width(raw: Sequence[dict]) -> int:
    if not raw:
        raise AssertionError("empty trajectory")
    return max(int(stat["value"]) for stat in raw)


def compactify_raw(raw: Sequence[dict], boundary: Sequence[int], ambient_dim: int) -> tuple[list[dict], list[dict]]:
    gamma = b3.decode_trajectory(raw, boundary, ambient_dim, require_compact=False)
    compact, trace = b3.compactify(gamma)
    return b3.encode_trajectory(compact), trace


def replay_preorder(lower_raw: Sequence[dict], upper_raw: Sequence[dict], boundary: Sequence[int], ambient_dim: int) -> dict:
    lower = b3.decode_trajectory(lower_raw, boundary, ambient_dim, require_compact=False)
    upper = b3.decode_trajectory(upper_raw, boundary, ambient_dim, require_compact=False)
    witness = b3.extension_preorder_witness(lower, upper)
    if witness is None:
        raise AssertionError("required extension-preorder lift does not exist")
    return witness


def validate_path(path: Sequence[Sequence[int]], lower_length: int, upper_length: int) -> list[list[int]]:
    parsed = [[int(p[0]), int(p[1])] for p in path]
    if not parsed or parsed[0] != [0, 0] or parsed[-1] != [lower_length - 1, upper_length - 1]:
        raise AssertionError("extension path endpoints")
    for left, right in zip(parsed, parsed[1:]):
        step = (right[0] - left[0], right[1] - left[1])
        if step not in {(1, 0), (0, 1), (1, 1)}:
            raise AssertionError("extension path step")
    return parsed


def derive_x_sequence(path: Sequence[Sequence[int]], lower_length: int, upper_length: int) -> list[int]:
    parsed = validate_path(path, lower_length, upper_length)
    xs: list[int] = []
    for upper_index in range(upper_length):
        available = [lower for lower, upper in parsed if upper == upper_index]
        if not available:
            raise AssertionError("extension path skips an upper trajectory index")
        if upper_index == 0:
            chosen = 0
        elif upper_index == upper_length - 1:
            chosen = lower_length - 1
        else:
            chosen = min(available)
        if [chosen, upper_index] not in parsed:
            raise AssertionError("chosen Algorithm-2 x coordinate not on path")
        xs.append(chosen)
    if xs[0] != 0 or xs[-1] != lower_length - 1:
        raise AssertionError("Algorithm-2 x endpoints")
    if any(a > b for a, b in zip(xs, xs[1:])):
        raise AssertionError("Algorithm-2 x sequence decreases")
    return xs


def exact_cut_certificates(catalog: list[dict], order: list[Any], ambient_dim: int) -> tuple[list[dict], int]:
    by_key = {id_key(item["id"]): item for item in catalog}
    expected = sorted(by_key)
    actual = [id_key(value) for value in order]
    if sorted(actual) != expected or len(actual) != len(expected) or len(set(actual)) != len(actual):
        raise AssertionError("output is not an exact whole-factor permutation")

    blocks = [tuple(int(v) for v in by_key[key]["normal_space"]) for key in actual]
    cuts: list[dict] = []
    maximum = 0
    for cut in range(len(blocks) + 1):
        left = b3.xor_basis(tuple(v for block in blocks[:cut] for v in block), ambient_dim)
        right = b3.xor_basis(tuple(v for block in blocks[cut:] for v in block), ambient_dim)
        boundary = b3.subspace_intersection(left, right, ambient_dim)
        width = len(boundary)
        maximum = max(maximum, width)
        cuts.append(
            {
                "cut": cut,
                "left_factor_ids": order[:cut],
                "right_factor_ids": order[cut:],
                "left_span_rref": list(left),
                "right_span_rref": list(right),
                "boundary_rref": list(boundary),
                "width": width,
            }
        )
    return cuts, maximum


def build(spec: dict, raw_input: dict, b5_1: dict, carrier: dict) -> dict:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_CANDIDATE_ONLY":
        raise AssertionError("B5.2B spec")
    if carrier.get("schema") != CARRIER_SCHEMA:
        raise AssertionError("B5.2A carrier schema")
    if b5_1.get("schema") != B5_1_SCHEMA:
        raise AssertionError("B5.1 artifact schema")

    c = carrier["proof_payload"]
    b = b5_1["proof_payload"]
    if b.get("capability_status") != "CLOSED_COMPLETE_TRACE":
        raise AssertionError("B5.2B requires a CLOSED B5.1 subject")
    if c["subject"]["b5_1_semantic_digest"] != b5_1["semantic_digest"]:
        raise AssertionError("carrier/B5.1 semantic subject mismatch")
    if c["subject"]["b5_1_root_full_set_digest"] != b["root_full_set_digest_if_closed"]:
        raise AssertionError("carrier/B5.1 root digest mismatch")
    if c["subject"]["b5_1_root_entry_count"] != b["root_entry_count_if_closed"]:
        raise AssertionError("carrier/B5.1 root count mismatch")
    if c["ambient_dim"] != b["ambient_dim"] or c["k"] != b["k"]:
        raise AssertionError("carrier/B5.1 parameter mismatch")

    ambient_dim = int(c["ambient_dim"])
    k = int(c["k"])
    nodes = {item["node_id"]: item for item in c["node_carriers"]}
    root_id = c["root_id"]
    if root_id not in nodes:
        raise AssertionError("carrier root missing")
    root_node = nodes[root_id]
    root_entries = root_node["final_entries"]

    base_payload: dict[str, Any] = {
        "gate": spec["gate"],
        "status": "CANDIDATE_PENDING_EXACT_HEAD_CI_AND_REVIEW",
        "ambient_dim": ambient_dim,
        "k": k,
        "carrier_semantic_digest": carrier["semantic_digest"],
        "b5_1_semantic_digest": b5_1["semantic_digest"],
        "root_id": root_id,
        "root_entry_count": len(root_entries),
        "canonical_factor_catalog": c["canonical_factor_catalog"],
        "compactification_lift_policy": {
            "join_node_trajectory": "RAW_NONCOMPACT_HV_JOIN",
            "shrink_node_trajectory": "PROJECTED_PRECOMPACT",
            "compact_runtime_sources_used_only_as_projection_bindings": True,
            "b5_2a_slack_metadata_used_by_printorder": False,
        },
    }

    if not root_entries:
        base_payload.update(
            {
                "reconstruction_status": "NOT_APPLICABLE_EMPTY_ROOT",
                "selected_root_entry_index": None,
                "selected_root_width": None,
                "factor_order_ids": None,
                "layout_records": None,
                "cut_certificates": None,
                "maximum_cut_width": None,
                "paper_faithful_lift_certificates": [],
                "printorder_event_trace": [],
                "candidate_found_layout": False,
                "found_layout_promotion": "FORBIDDEN",
                "generic_no_layout_at_cap": "FORBIDDEN_PENDING_B5_3",
                "strict_boundary": spec["strict_boundary"],
            }
        )
        result = {"schema": SCHEMA, "semantic_digest_scope": "proof_payload", "proof_payload": base_payload}
        result["semantic_digest"] = digest(base_payload)
        return result

    selected = min(
        range(len(root_entries)),
        key=lambda index: (
            trajectory_width(root_entries[index]["trajectory"]),
            digest(root_entries[index]["trajectory"]),
            index,
        ),
    )
    selected_root = root_entries[selected]
    selected_bt = c["root_entry_backtracks"][selected]
    if int(selected_bt["entry_index"]) != selected:
        raise AssertionError("root backtrack/index mismatch")

    lift_certificates: list[dict] = []
    events: list[dict] = []
    output_order: list[Any] = []
    cert_cache: dict[tuple, dict] = {}

    def add_event(kind: str, **payload: Any) -> None:
        events.append({"event_index": len(events), "kind": kind, **payload})

    def up_certificate(
        *, stage: str, node_id: Any, entry_index: int, lower_raw: Sequence[dict], upper_raw: Sequence[dict],
        boundary: Sequence[int], retained_witness: dict | None = None, compact_source_raw: Sequence[dict] | None = None,
        compactification_trace: list[dict] | None = None,
    ) -> dict:
        key = (id_key(node_id), stage, int(entry_index), digest(lower_raw), digest(upper_raw))
        if key in cert_cache:
            return cert_cache[key]
        replayed = replay_preorder(lower_raw, upper_raw, boundary, ambient_dim)
        if retained_witness is not None and replayed != retained_witness:
            raise AssertionError("retained up witness differs from deterministic B3 replay")
        xs = derive_x_sequence(replayed["path"], len(lower_raw), len(upper_raw))
        certificate: dict[str, Any] = {
            "certificate_index": len(lift_certificates),
            "stage": stage,
            "node_id": node_id,
            "entry_index": int(entry_index),
            "boundary_rref": list(boundary),
            "lower_trajectory_digest": digest(lower_raw),
            "upper_trajectory_digest": digest(upper_raw),
            "lower_length": len(lower_raw),
            "upper_length": len(upper_raw),
            "extension_preorder_witness": replayed,
            "algorithm2_x_sequence_zero_based": xs,
            "slack_metadata_used": False,
        }
        if compact_source_raw is not None:
            compacted, recomputed_trace = compactify_raw(lower_raw, boundary, ambient_dim)
            if compacted != list(compact_source_raw):
                raise AssertionError("precompact source does not compactify to runtime source")
            if compactification_trace is not None and recomputed_trace != compactification_trace:
                raise AssertionError("compactification trace mismatch")
            certificate["compactification_lift"] = {
                "runtime_compact_source_digest": digest(compact_source_raw),
                "compactification_identity": True,
                "compactification_trace": recomputed_trace,
            }
        lift_certificates.append(certificate)
        cert_cache[key] = certificate
        return certificate

    zero_boundary_leaves = sorted(
        [
            item
            for item in c["node_carriers"]
            if item["kind"] == "leaf" and item["B_v_rref"] == []
        ],
        key=lambda item: id_key(item["leaf_factor_id"]),
    )
    for leaf in zero_boundary_leaves:
        output_order.append(leaf["leaf_factor_id"])
        add_event(
            "ZERO_BOUNDARY_LEAF_PREPRINT",
            node_id=leaf["node_id"],
            factor_id=leaf["leaf_factor_id"],
        )

    def emit_final(backtrack: dict, interval_index: int) -> None:
        node = nodes[backtrack["node_id"]]
        entry_index = int(backtrack["entry_index"])
        entry = node["final_entries"][entry_index]
        upper = entry["trajectory"]
        if not 0 <= interval_index < len(upper) - 1:
            raise AssertionError("final interval outside target trajectory")

        if backtrack["kind"] == "leaf":
            if node["kind"] != "leaf" or node["leaf_factor_id"] != backtrack["factor_id"]:
                raise AssertionError("leaf backtrack identity")
            lower = entry["source_trajectory"]
            certificate = up_certificate(
                stage="LEAF_FINAL_UP",
                node_id=node["node_id"],
                entry_index=entry_index,
                lower_raw=lower,
                upper_raw=upper,
                boundary=node["B_v_rref"],
                retained_witness=entry["extension_witness"],
            )
            xs = certificate["algorithm2_x_sequence_zero_based"]
            for child_interval in range(xs[interval_index], xs[interval_index + 1]):
                if len(lower) == 2 and child_interval == 0:
                    output_order.append(backtrack["factor_id"])
                    add_event(
                        "LEAF_PRINT",
                        node_id=node["node_id"],
                        factor_id=backtrack["factor_id"],
                        parent_interval=interval_index,
                        leaf_interval=child_interval,
                    )
                elif len(lower) == 1:
                    continue
                else:
                    raise AssertionError("unexpected leaf source trajectory interval")
            return

        if node["kind"] != "internal":
            raise AssertionError("internal backtrack points to non-internal carrier node")
        shrink_index = int(backtrack["shrink_generator_index"])
        shrink_record = node["shrink_generators"][shrink_index]
        if int(entry["source_index"]) != shrink_index:
            raise AssertionError("final up original source index/shrink record mismatch")
        if entry["source_trajectory"] != shrink_record["shrunk_generator"]:
            raise AssertionError("final up compact source/shrink generator mismatch")
        lower = shrink_record["shrink_receipt"]["projected_precompact"]
        certificate = up_certificate(
            stage="FINAL_UP_FROM_PAPER_SHRINK",
            node_id=node["node_id"],
            entry_index=entry_index,
            lower_raw=lower,
            upper_raw=upper,
            boundary=node["B_v_rref"],
            compact_source_raw=entry["source_trajectory"],
            compactification_trace=shrink_record["shrink_receipt"]["compactification_trace"],
        )
        xs = certificate["algorithm2_x_sequence_zero_based"]
        add_event(
            "UP_DISPATCH",
            stage="FINAL_UP_FROM_PAPER_SHRINK",
            node_id=node["node_id"],
            parent_interval=interval_index,
            child_interval_start=xs[interval_index],
            child_interval_stop=xs[interval_index + 1],
        )
        for child_interval in range(xs[interval_index], xs[interval_index + 1]):
            emit_shrink(backtrack, node, child_interval)

    def emit_shrink(backtrack: dict, node: dict, interval_index: int) -> None:
        joined_index = int(backtrack["joined_entry_index"])
        joined_entry = node["joined_entries"][joined_index]
        shrink_record = node["shrink_generators"][int(backtrack["shrink_generator_index"])]
        projected = shrink_record["shrink_receipt"]["projected_precompact"]
        if int(shrink_record["joined_entry_index"]) != joined_index:
            raise AssertionError("shrink joined-entry reference")
        if len(projected) != len(joined_entry["trajectory"]):
            raise AssertionError("paper shrink must preserve trajectory length")
        if not 0 <= interval_index < len(joined_entry["trajectory"]) - 1:
            raise AssertionError("paper shrink interval outside joined child")
        add_event(
            "SHRINK_IDENTITY_DISPATCH",
            node_id=node["node_id"],
            shrink_interval=interval_index,
            joined_child_interval=interval_index,
        )
        emit_joined_up(backtrack, node, interval_index)

    def emit_joined_up(backtrack: dict, node: dict, interval_index: int) -> None:
        joined_index = int(backtrack["joined_entry_index"])
        joined_entry = node["joined_entries"][joined_index]
        join_index = int(backtrack["successful_join_generator_index"])
        join_record = node["successful_join_generators"][join_index]
        if int(joined_entry["source_index"]) != join_index:
            raise AssertionError("joined up original source index/join record mismatch")
        if joined_entry["source_trajectory"] != join_record["joined_generator"]:
            raise AssertionError("joined up compact source/join generator mismatch")
        raw_join = join_record["join_receipt"]["raw_join"]
        certificate = up_certificate(
            stage="JOINED_UP_FROM_RAW_HV_JOIN",
            node_id=node["node_id"],
            entry_index=joined_index,
            lower_raw=raw_join,
            upper_raw=joined_entry["trajectory"],
            boundary=node["Bprime_v_rref"],
            compact_source_raw=joined_entry["source_trajectory"],
            compactification_trace=join_record["join_receipt"]["compactification_trace"],
        )
        xs = certificate["algorithm2_x_sequence_zero_based"]
        if not 0 <= interval_index < len(joined_entry["trajectory"]) - 1:
            raise AssertionError("joined up parent interval")
        add_event(
            "UP_DISPATCH",
            stage="JOINED_UP_FROM_RAW_HV_JOIN",
            node_id=node["node_id"],
            parent_interval=interval_index,
            child_interval_start=xs[interval_index],
            child_interval_stop=xs[interval_index + 1],
        )
        for raw_interval in range(xs[interval_index], xs[interval_index + 1]):
            emit_join(backtrack, node, join_record, raw_interval)

    def emit_join(backtrack: dict, node: dict, join_record: dict, interval_index: int) -> None:
        path = [[int(v[0]), int(v[1])] for v in join_record["path"]]
        raw_join = join_record["join_receipt"]["raw_join"]
        if path != join_record["join_receipt"]["path"] or len(path) != len(raw_join):
            raise AssertionError("raw H/V join path/trajectory identity")
        if not 0 <= interval_index < len(path) - 1:
            raise AssertionError("raw join interval")
        current = path[interval_index]
        following = path[interval_index + 1]
        step = (following[0] - current[0], following[1] - current[1])
        if step == (1, 0):
            add_event(
                "JOIN_DISPATCH_LEFT",
                node_id=node["node_id"],
                join_interval=interval_index,
                child_interval=current[0],
            )
            emit_expanded(
                backtrack["left_child"],
                node,
                "left",
                int(backtrack["left_expanded_entry_index"]),
                current[0],
            )
        elif step == (0, 1):
            add_event(
                "JOIN_DISPATCH_RIGHT",
                node_id=node["node_id"],
                join_interval=interval_index,
                child_interval=current[1],
            )
            emit_expanded(
                backtrack["right_child"],
                node,
                "right",
                int(backtrack["right_expanded_entry_index"]),
                current[1],
            )
        else:
            raise AssertionError("ordinary join contains diagonal/non-HV dispatch")

    def emit_expanded(child_backtrack: dict, node: dict, side: str, entry_index: int, interval_index: int) -> None:
        expanded = node[f"{side}_expanded_entries"][entry_index]
        source_index = int(expanded["source_index"])
        transport = node[f"{side}_transport_generators"][source_index]
        if int(transport["generator_index"]) != source_index:
            raise AssertionError("transport generator index")
        if int(transport["child_output_entry_index"]) != int(child_backtrack["entry_index"]):
            raise AssertionError("transport/child output ancestry mismatch")
        if expanded["source_trajectory"] != transport["transported_generator"]:
            raise AssertionError("expanded up source/transported generator mismatch")
        certificate = up_certificate(
            stage=f"{side.upper()}_EXPANDED_CHILD_UP",
            node_id=node["node_id"],
            entry_index=entry_index,
            lower_raw=expanded["source_trajectory"],
            upper_raw=expanded["trajectory"],
            boundary=node["Bprime_v_rref"],
            retained_witness=expanded["extension_witness"],
        )
        xs = certificate["algorithm2_x_sequence_zero_based"]
        if not 0 <= interval_index < len(expanded["trajectory"]) - 1:
            raise AssertionError("expanded up parent interval")
        add_event(
            "UP_DISPATCH",
            stage=f"{side.upper()}_EXPANDED_CHILD_UP",
            node_id=node["node_id"],
            parent_interval=interval_index,
            child_interval_start=xs[interval_index],
            child_interval_stop=xs[interval_index + 1],
        )
        for child_interval in range(xs[interval_index], xs[interval_index + 1]):
            add_event(
                "TRANSPORT_IDENTITY_DISPATCH",
                node_id=node["node_id"],
                side=side,
                transported_interval=child_interval,
                child_output_interval=child_interval,
            )
            emit_final(child_backtrack, child_interval)

    for root_interval in range(len(selected_root["trajectory"]) - 1):
        emit_final(selected_bt, root_interval)

    expected_ids = sorted([id_key(item["id"]) for item in c["canonical_factor_catalog"]])
    actual_ids = [id_key(value) for value in output_order]
    if sorted(actual_ids) != expected_ids or len(set(actual_ids)) != len(actual_ids):
        raise AssertionError("Algorithm-2 output is not an exact factor permutation")

    cuts, maximum_width = exact_cut_certificates(c["canonical_factor_catalog"], output_order, ambient_dim)
    if maximum_width > k:
        raise AssertionError("reconstructed factor order exceeds k")

    catalog_by_key = {id_key(item["id"]): item for item in c["canonical_factor_catalog"]}
    layout_records = [
        {
            "position": position,
            "factor_id": factor_id,
            "normal_space": catalog_by_key[id_key(factor_id)]["normal_space"],
            "affine_offset": catalog_by_key[id_key(factor_id)]["affine_offset"],
        }
        for position, factor_id in enumerate(output_order)
    ]

    base_payload.update(
        {
            "reconstruction_status": "LAYOUT_CANDIDATE_RECONSTRUCTED_PENDING_REVIEW",
            "selected_root_entry_index": selected,
            "selected_root_trajectory_digest": digest(selected_root["trajectory"]),
            "selected_root_width": trajectory_width(selected_root["trajectory"]),
            "root_selection_key": [
                trajectory_width(selected_root["trajectory"]),
                digest(selected_root["trajectory"]),
                selected,
            ],
            "paper_faithful_lift_certificates": lift_certificates,
            "printorder_event_trace": events,
            "factor_order_ids": output_order,
            "layout_records": layout_records,
            "cut_certificates": cuts,
            "maximum_cut_width": maximum_width,
            "candidate_found_layout": True,
            "found_layout_promotion": "FORBIDDEN_PENDING_B5_2B_EXACT_HEAD_CI_AND_REVIEW",
            "generic_no_layout_at_cap": "FORBIDDEN_PENDING_B5_3",
            "strict_boundary": spec["strict_boundary"],
        }
    )
    result = {"schema": SCHEMA, "semantic_digest_scope": "proof_payload", "proof_payload": base_payload}
    result["semantic_digest"] = digest(base_payload)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--b5-1-artifact", type=Path, required=True)
    parser.add_argument("--carrier", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifact = build(load(args.spec), load(args.input), load(args.b5_1_artifact), load(args.carrier))
    save(artifact, args.output)
    payload = artifact["proof_payload"]
    print("JANUS_B5_2B_GENERIC_ALGORITHM2_PRINTORDER_RECONSTRUCTION = PASS")
    print("RECONSTRUCTION_STATUS =", payload["reconstruction_status"])
    print("SELECTED_ROOT_ENTRY_INDEX =", payload["selected_root_entry_index"])
    print("SELECTED_ROOT_WIDTH =", payload["selected_root_width"])
    print("FACTOR_ORDER_IDS =", json.dumps(payload["factor_order_ids"], sort_keys=True, separators=(",", ":")))
    print("MAXIMUM_CUT_WIDTH =", payload["maximum_cut_width"])
    print("COMPACTIFICATION_LIFT_CERTIFICATES =", len(payload["paper_faithful_lift_certificates"]))
    print("B5_2A_SLACK_METADATA_USED_BY_PRINTORDER = FALSE")
    print("GENERIC_FOUND_LAYOUT = FORBIDDEN_PENDING_REVIEW")
    print("GENERIC_NO_LAYOUT_AT_CAP = FORBIDDEN_PENDING_B5_3")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")
    print("SEMANTIC_DIGEST =", artifact["semantic_digest"])


if __name__ == "__main__":
    main()
