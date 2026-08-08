from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from janus_c049_1_b3_expand_join_shrink_core import (
    Statistic,
    decode_trajectory,
    encode_trajectory,
    expand_trajectory,
    shrink_trajectory,
    subspace_sum,
    width,
)
from janus_c049_1_b3_join_path_domain_corrected import join_trajectory, ordinary_join_paths
from janus_c049_1_b5_1_generic_corrected_runtime_trace_executor import (
    CLOSED,
    caller_premises,
    compute_boundaries,
    compute_coverages,
    digest,
    entries_to_trajectories,
    full_set_digest,
    load,
    normalized_entries,
    safe_up_k,
    save,
    validate_input,
)

SCHEMA = "janus.c049_1.b5_2a.generic_algorithm2_provenance_carrier.v1"
SPEC_SCHEMA = "janus.c049_1.b5_2a.generic_algorithm2_provenance_carrier_spec.v1"


def up_label(entry: dict) -> dict:
    w = entry["witness"]
    pts = w["path"]
    if not pts:
        raise AssertionError("empty extension witness")
    native = []
    one_based = []
    slack = []
    selected = []
    prev_lower = None
    for idx, pt in enumerate(pts):
        li = int(pt["lower_index"])
        ui = int(pt["upper_index"])
        lo = pt["lower"]
        up = pt["upper"]
        s = int(up["lambda"]) - int(lo["lambda"])
        if s < 0:
            raise AssertionError("negative Algorithm2 slack")
        native.append([li, ui])
        one_based.append([li + 1, ui + 1])
        slack.append(s)
        if s == 0 and (idx == 0 or li != prev_lower):
            selected.append(li)
        prev_lower = li
    return {
        "native_zero_based_path": native,
        "paper_one_based_path": one_based,
        "slack_sequence": slack,
        "zero_slack_child_positions_zero_based": selected,
        "source_index": int(entry["source_index"]),
        "witness_digest": digest(w),
    }


def carrier_entries(entries: Sequence[dict]) -> list[dict]:
    out = []
    for i, e in enumerate(entries):
        out.append({
            "entry_index": i,
            "trajectory": e["trajectory"],
            "trajectory_digest": digest(e["trajectory"]),
            "source_index": int(e["source_index"]),
            "extension_witness": e["witness"],
            "algorithm2_up_label": up_label(e),
        })
    return out


def assert_subject(subject: dict, factor_list: list[dict], canonical_tree: dict, root: str, postorder: Sequence[str]) -> dict[str, dict]:
    if subject.get("schema") != "janus.c049_1.b5_1.generic_corrected_runtime_trace.v1":
        raise AssertionError("wrong B5.1 subject schema")
    if subject.get("semantic_digest_scope") != "proof_payload" or digest(subject["proof_payload"]) != subject.get("semantic_digest"):
        raise AssertionError("B5.1 subject digest")
    p = subject["proof_payload"]
    if p["capability_status"] != CLOSED:
        raise AssertionError("B5.2A requires CLOSED B5.1 subject")
    if p["canonical_factor_catalog"] != factor_list:
        raise AssertionError("factor catalog mismatch")
    if p["canonical_tree"] != canonical_tree or p["root_id"] != root or p["postorder"] != list(postorder):
        raise AssertionError("tree mismatch")
    if p["terminal_promotion"] != "NONE":
        raise AssertionError("unexpected upstream terminal promotion")
    return {n["node_id"]: n for n in p["node_receipts"]}


def backtrack_node(node_id: str, entry_index: int, carriers: dict[str, dict], seen: set[tuple[str, int]]) -> dict:
    key = (node_id, entry_index)
    if key in seen:
        raise AssertionError("cyclic backtrack")
    seen = set(seen)
    seen.add(key)
    node = carriers[node_id]
    finals = node["final_entries"]
    if not (0 <= entry_index < len(finals)):
        raise AssertionError("dangling final entry")
    f = finals[entry_index]
    if node["kind"] == "leaf":
        if f["source_index"] != 0:
            raise AssertionError("leaf final must source Delta_B")
        return {
            "node_id": node_id,
            "entry_index": entry_index,
            "kind": "leaf",
            "factor_id": node["leaf_factor_id"],
            "delta_generator_index": 0,
            "up_label_digest": digest(f["algorithm2_up_label"]),
        }

    si = f["source_index"]
    shrinks = node["shrink_generators"]
    if not (0 <= si < len(shrinks)):
        raise AssertionError("dangling final source")
    sr = shrinks[si]
    ji = sr["joined_entry_index"]
    joined = node["joined_entries"]
    if not (0 <= ji < len(joined)):
        raise AssertionError("dangling joined entry")
    je = joined[ji]
    jsi = je["source_index"]
    joins = node["successful_join_generators"]
    if not (0 <= jsi < len(joins)):
        raise AssertionError("dangling join generator")
    jr = joins[jsi]

    left_ei = jr["left_expanded_entry_index"]
    right_ei = jr["right_expanded_entry_index"]
    left_expanded = node["left_expanded_entries"]
    right_expanded = node["right_expanded_entries"]
    if not (0 <= left_ei < len(left_expanded)) or not (0 <= right_ei < len(right_expanded)):
        raise AssertionError("dangling expanded entry")
    le = left_expanded[left_ei]
    re = right_expanded[right_ei]
    ltsi = le["source_index"]
    rtsi = re["source_index"]
    lt = node["left_transport_generators"]
    rt = node["right_transport_generators"]
    if not (0 <= ltsi < len(lt)) or not (0 <= rtsi < len(rt)):
        raise AssertionError("dangling transport generator")
    lchild_ei = lt[ltsi]["child_output_entry_index"]
    rchild_ei = rt[rtsi]["child_output_entry_index"]

    return {
        "node_id": node_id,
        "entry_index": entry_index,
        "kind": "internal",
        "final_up_label_digest": digest(f["algorithm2_up_label"]),
        "shrink_generator_index": si,
        "joined_entry_index": ji,
        "joined_up_label_digest": digest(je["algorithm2_up_label"]),
        "successful_join_generator_index": jsi,
        "join_HV_path": jr["path"],
        "left_expanded_entry_index": left_ei,
        "right_expanded_entry_index": right_ei,
        "left_expand_up_label_digest": digest(le["algorithm2_up_label"]),
        "right_expand_up_label_digest": digest(re["algorithm2_up_label"]),
        "left_child": backtrack_node(node["left_child_id"], lchild_ei, carriers, seen),
        "right_child": backtrack_node(node["right_child_id"], rchild_ei, carriers, seen),
    }


def build(raw: dict, subject: dict, spec: dict) -> dict:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_NO_FOUND_LAYOUT_PROMOTION":
        raise AssertionError("wrong B5.2A spec")
    d, k, factor_list, nodes, caps, root, postorder, canonical_tree = validate_input(raw)
    factors = {f["id"]: f for f in factor_list}
    covers, V, _ = compute_coverages(postorder, nodes, factors, d)
    B = compute_boundaries(postorder, covers, V, factors, d)
    subject_nodes = assert_subject(subject, factor_list, canonical_tree, root, postorder)

    carriers: dict[str, dict] = {}
    node_entries: dict[str, list[dict]] = {}
    for nid in postorder:
        node = nodes[nid]
        upstream = subject_nodes[nid]
        if node["kind"] == "leaf":
            delta = (Statistic((), B[nid], 0), Statistic(B[nid], (), 0))
            final_up, err = safe_up_k([delta], B[nid], d, k, caps, f"{nid}:leaf_up_k")
            if final_up is None or err["status"] != CLOSED:
                raise AssertionError("closed B5.1 leaf failed carrier replay")
            final_entries = normalized_entries(final_up)
            if upstream["output_entry_count"] != len(final_entries) or upstream["output_full_set_digest"] != full_set_digest(final_entries):
                raise AssertionError("leaf projection mismatch")
            node_entries[nid] = final_entries
            carriers[nid] = {
                "node_id": nid,
                "kind": "leaf",
                "leaf_factor_id": node["factor_id"],
                "covered_factor_ids": list(covers[nid]),
                "B_v_rref": list(B[nid]),
                "delta_generators": [{"generator_index": 0, "trajectory": encode_trajectory(delta)}],
                "final_entries": carrier_entries(final_entries),
                "b5_1_projection": {
                    "output_entry_count": len(final_entries),
                    "output_full_set_digest": full_set_digest(final_entries),
                },
            }
            continue

        left, right = node["left"], node["right"]
        Bprime = subspace_sum(B[left], B[right], d)
        cp = caller_premises(V[left], V[right], B[left], B[right], B[nid], Bprime, d)
        if not cp["all_pass"]:
            raise AssertionError("caller premise")

        left_child = entries_to_trajectories(node_entries[left], B[left], d)
        right_child = entries_to_trajectories(node_entries[right], B[right], d)

        left_transport = []
        left_generators = []
        for i, gamma in enumerate(left_child):
            out, receipt = expand_trajectory(gamma, B[left], Bprime, d)
            left_generators.append(out)
            left_transport.append({
                "generator_index": i,
                "child_output_entry_index": i,
                "child_trajectory": encode_trajectory(gamma),
                "transported_generator": encode_trajectory(out),
                "expand_receipt": receipt,
            })
        right_transport = []
        right_generators = []
        for i, gamma in enumerate(right_child):
            out, receipt = expand_trajectory(gamma, B[right], Bprime, d)
            right_generators.append(out)
            right_transport.append({
                "generator_index": i,
                "child_output_entry_index": i,
                "child_trajectory": encode_trajectory(gamma),
                "transported_generator": encode_trajectory(out),
                "expand_receipt": receipt,
            })

        left_up, lerr = safe_up_k(left_generators, Bprime, d, k, caps, f"{nid}:expand_left_up_k")
        right_up, rerr = safe_up_k(right_generators, Bprime, d, k, caps, f"{nid}:expand_right_up_k")
        if left_up is None or right_up is None or lerr["status"] != CLOSED or rerr["status"] != CLOSED:
            raise AssertionError("closed B5.1 expand failed carrier replay")
        left_entries = normalized_entries(left_up)
        right_entries = normalized_entries(right_up)
        left_g = entries_to_trajectories(left_entries, Bprime, d)
        right_g = entries_to_trajectories(right_entries, Bprime, d)

        successful = []
        successful_generators = []
        for li, g1 in enumerate(left_g):
            for ri, g2 in enumerate(right_g):
                for path in ordinary_join_paths(len(g1), len(g2)):
                    joined, jrec = join_trajectory(g1, g2, path, Bprime, d)
                    if width(joined) <= k:
                        idx = len(successful)
                        successful_generators.append(joined)
                        successful.append({
                            "generator_index": idx,
                            "left_expanded_entry_index": li,
                            "right_expanded_entry_index": ri,
                            "path": [list(p) for p in path],
                            "joined_generator": encode_trajectory(joined),
                            "join_receipt": jrec,
                        })

        joined_up, jerr = safe_up_k(successful_generators, Bprime, d, k, caps, f"{nid}:joined_up_k")
        if joined_up is None or jerr["status"] != CLOSED:
            raise AssertionError("closed B5.1 join failed carrier replay")
        joined_entries = normalized_entries(joined_up)
        joined_g = entries_to_trajectories(joined_entries, Bprime, d)

        shrink_records = []
        shrunk_generators = []
        for ji, gamma in enumerate(joined_g):
            shrunk, srec = shrink_trajectory(gamma, B[nid], d)
            idx = len(shrink_records)
            shrunk_generators.append(shrunk)
            shrink_records.append({
                "generator_index": idx,
                "joined_entry_index": ji,
                "joined_full_set_trajectory": encode_trajectory(gamma),
                "shrunk_generator": encode_trajectory(shrunk),
                "shrink_receipt": srec,
            })

        final_up, ferr = safe_up_k(shrunk_generators, B[nid], d, k, caps, f"{nid}:final_up_k")
        if final_up is None or ferr["status"] != CLOSED:
            raise AssertionError("closed B5.1 final failed carrier replay")
        final_entries = normalized_entries(final_up)
        if upstream["output_entry_count"] != len(final_entries) or upstream["output_full_set_digest"] != full_set_digest(final_entries):
            raise AssertionError("internal projection mismatch")
        node_entries[nid] = final_entries
        carriers[nid] = {
            "node_id": nid,
            "kind": "internal",
            "left_child_id": left,
            "right_child_id": right,
            "covered_factor_ids": list(covers[nid]),
            "B_v_rref": list(B[nid]),
            "Bprime_v_rref": list(Bprime),
            "caller_premise_certificate": cp,
            "left_transport_generators": left_transport,
            "right_transport_generators": right_transport,
            "left_expanded_entries": carrier_entries(left_entries),
            "right_expanded_entries": carrier_entries(right_entries),
            "successful_join_generators": successful,
            "joined_entries": carrier_entries(joined_entries),
            "shrink_generators": shrink_records,
            "final_entries": carrier_entries(final_entries),
            "b5_1_projection": {
                "output_entry_count": len(final_entries),
                "output_full_set_digest": full_set_digest(final_entries),
            },
        }

    root_count = len(node_entries[root])
    root_backtracks = [backtrack_node(root, i, carriers, set()) for i in range(root_count)]
    subject_p = subject["proof_payload"]
    if subject_p["root_entry_count_if_closed"] != root_count or subject_p["root_full_set_digest_if_closed"] != full_set_digest(node_entries[root]):
        raise AssertionError("root projection mismatch")

    payload = {
        "subject": {
            "b5_1_semantic_digest": subject["semantic_digest"],
            "b5_1_root_full_set_digest": subject_p["root_full_set_digest_if_closed"],
            "b5_1_root_entry_count": subject_p["root_entry_count_if_closed"],
        },
        "ambient_dim": d,
        "k": k,
        "canonical_factor_catalog": factor_list,
        "canonical_tree": canonical_tree,
        "root_id": root,
        "postorder": list(postorder),
        "node_carriers": [carriers[n] for n in sorted(carriers)],
        "root_entry_backtracks": root_backtracks,
        "backtracking_summary": {
            "root_entries": root_count,
            "root_entries_with_complete_backtrack": len(root_backtracks),
            "dangling_reference_count": 0,
            "cycle_count": 0,
        },
        "semantic_projection": {
            "node_count": len(carriers),
            "node_digest_count_matches": sum(
                1 for n in carriers if carriers[n]["b5_1_projection"]["output_full_set_digest"] == subject_nodes[n]["output_full_set_digest"]
            ),
            "node_entry_count_matches": sum(
                1 for n in carriers if carriers[n]["b5_1_projection"]["output_entry_count"] == subject_nodes[n]["output_entry_count"]
            ),
            "root_full_set_digest_unchanged": True,
            "root_entry_count_unchanged": True,
            "new_semantic_entries_added": 0,
        },
        "algorithm2_boundary": {
            "labels_retained": ["leaf_delta", "up_path_and_slack", "join_HV_path", "shrink_relation"],
            "factor_order_emitted": False,
            "printorder_correctness_claimed": False,
            "found_layout": "FORBIDDEN",
        },
        "strict_boundary": {
            "generic_algorithm2_backtracking_certificate_candidate": True,
            "b5_2b_generic_printorder_reconstruction": False,
            "generic_found_layout_enabled": False,
            "generic_no_layout_at_cap_enabled": False,
            "polynomial_runtime_claim": "FORBIDDEN",
            "b5_complete": False,
            "p_vs_np": "OPEN",
            "formal_admission": "BLOCKED_PENDING_REVIEW",
        },
    }
    artifact = {"schema": SCHEMA, "semantic_digest_scope": "proof_payload", "proof_payload": payload}
    artifact["semantic_digest"] = digest(payload)
    return artifact


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--b5-1-artifact", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    art = build(load(a.input), load(a.b5_1_artifact), load(a.spec))
    save(art, a.output)
    q = art["proof_payload"]
    print("JANUS_B5_2A_GENERIC_ALGORITHM2_PROVENANCE_CARRIER = PASS")
    print("ROOT_ENTRIES =", q["backtracking_summary"]["root_entries"])
    print("ROOT_ENTRIES_WITH_COMPLETE_BACKTRACK =", q["backtracking_summary"]["root_entries_with_complete_backtrack"])
    print("DANGLING_REFERENCE_COUNT =", q["backtracking_summary"]["dangling_reference_count"])
    print("SEMANTIC_PROJECTION_NODE_DIGESTS =", f"{q['semantic_projection']['node_digest_count_matches']}/{q['semantic_projection']['node_count']}")
    print("SEMANTIC_PROJECTION_NODE_COUNTS =", f"{q['semantic_projection']['node_entry_count_matches']}/{q['semantic_projection']['node_count']}")
    print("FACTOR_ORDER_EMITTED = FALSE")
    print("FOUND_LAYOUT = FORBIDDEN")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")
    print("SEMANTIC_DIGEST =", art["semantic_digest"])

if __name__ == "__main__":
    main()
