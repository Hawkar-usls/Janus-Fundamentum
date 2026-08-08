from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import janus_c049_1_b4_2_3k_scaffold as b42
import janus_c049_1_b5_1_generic_corrected_runtime_trace_executor as b51
import janus_c049_1_b5_2a_generic_algorithm2_provenance_carrier_v11 as b52a
import janus_c049_1_b5_2b_generic_algorithm2_printorder_reconstruction as b52b
import janus_c049_1_b5_3_generic_empty_root_terminal_composition as b53
import janus_c049_1_b5_4_corrected_discovery_c047_rebound_v11 as b54
from janus_c049_1_b3_expand_join_shrink_core import subspace_intersection, xor_basis

SCHEMA = "janus.c049_1.b5.iterative_compression_orchestrator_candidate.v1"
SPEC_SCHEMA = "janus.c049_1.b5.iterative_compression_orchestrator_spec.v1"
BASE = Path("experiments/direct")

B51_SPEC = BASE / "C049_1_B5_1_GENERIC_CORRECTED_RUNTIME_TRACE_EXECUTOR_SPEC_V1.json"
B52A_AMENDMENT = BASE / "C049_1_B5_2A_GENERIC_ALGORITHM2_PROVENANCE_CARRIER_AMENDMENT_V1_1.json"
B52B_SPEC = BASE / "C049_1_B5_2B_GENERIC_ALGORITHM2_PRINTORDER_RECONSTRUCTION_SPEC_V1.json"
B53_SPEC = BASE / "C049_1_B5_3_GENERIC_EMPTY_ROOT_TERMINAL_COMPOSITION_SPEC_V1.json"
B54_SPEC = BASE / "C049_1_B5_4_CORRECTED_DISCOVERY_C047_REBOUND_SPEC_V1.json"

B5_CONTRACT_RECEIPT = BASE / "audits/C049_1_B5_GENERAL_RUNTIME_TERMINAL_CONTRACT_ADMISSION_CEBBCFF9.json"
B51_RECEIPT = BASE / "audits/C049_1_B5_1_GENERIC_CORRECTED_RUNTIME_TRACE_EXECUTOR_ADMISSION_DDA63620.json"
B52B_RECEIPT = BASE / "audits/C049_1_B5_2B_GENERIC_ALGORITHM2_PRINTORDER_RECONSTRUCTION_ADMISSION_F057B7AF.json"
COMPOSITION_AUDIT = BASE / "audits/C049_1_B4_6_3_GENERAL_STRUCTURAL_INDUCTION_COMPOSITION_INDEPENDENT_SOURCE_AUDIT_4F8F9424.json"
O7_AUDIT = BASE / "audits/C049_1_B4_6_3_GENERAL_EMPTY_ROOT_SPECIALIZATION_AUTHORITY_CLOSURE_AUDIT_7F9DF43C.json"


def cb(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def dg(value: Any) -> str:
    return hashlib.sha256(cb(value)).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save(value: Any, path: Path) -> None:
    path.write_bytes(cb(value) + b"\n")


def artifact_bytes(value: Any | None) -> int:
    return 0 if value is None else len(cb(value)) + 1


def canonical_input(raw: dict) -> tuple[int, int, list[dict], list[str], dict, dict, int | None]:
    d = int(raw["ambient_dim"])
    k = int(raw["k"])
    if d <= 0 or k < 0:
        raise ValueError("ambient_dim must be positive and k nonnegative")
    factors_raw = raw.get("factors")
    if not isinstance(factors_raw, list) or not factors_raw:
        raise ValueError("nonempty factor catalog required")
    factors: list[dict] = []
    seen: set[str] = set()
    for item in factors_raw:
        fid = str(item["id"])
        if not fid or fid in seen:
            raise ValueError("factor IDs must be unique nonempty strings")
        seen.add(fid)
        factors.append({
            "id": fid,
            "normal_space": list(xor_basis(item.get("normal_space", []), d)),
            "affine_offset": item.get("affine_offset"),
        })
    factors.sort(key=lambda item: item["id"])
    by_id = {item["id"]: item for item in factors}

    order = [str(x) for x in raw.get("input_order", [])]
    if len(order) != len(factors) or len(set(order)) != len(order) or sorted(order) != sorted(by_id):
        raise ValueError("input_order must be an exact permutation of factor IDs")

    runtime_caps = dict(raw.get("runtime_caps", {}))
    phase_a_caps = dict(raw.get("phase_a_caps", {}))
    max_rounds_raw = raw.get("max_rounds")
    max_rounds = None if max_rounds_raw is None else int(max_rounds_raw)
    if max_rounds is not None and max_rounds < 0:
        raise ValueError("max_rounds must be nonnegative")
    return d, k, factors, order, runtime_caps, phase_a_caps, max_rounds


def factor_map(factors: Sequence[dict]) -> dict[str, dict]:
    return {str(item["id"]): item for item in factors}


def prefix_factors(factors: Sequence[dict], prefix_ids: Sequence[str]) -> list[dict]:
    by = factor_map(factors)
    return [dict(by[fid]) for fid in sorted(prefix_ids)]


def left_deep_tree(order_ids: Sequence[str], round_index: int) -> dict:
    if not order_ids:
        raise ValueError("empty tree order")
    leaves = [
        {"id": f"r{round_index:04d}:leaf:{position:04d}", "factor_id": str(fid)}
        for position, fid in enumerate(order_ids)
    ]
    if len(leaves) == 1:
        return {"root": leaves[0]["id"], "nodes": leaves}
    nodes: list[dict] = list(leaves)
    left = leaves[0]["id"]
    for position in range(1, len(leaves)):
        nid = f"r{round_index:04d}:join:{position:04d}"
        nodes.append({"id": nid, "left": left, "right": leaves[position]["id"]})
        left = nid
    return {"root": left, "nodes": nodes}


def tree_boundary_certificate(tree: dict, factors: Sequence[dict], d: int, k: int) -> dict:
    by_factor = factor_map(factors)
    nodes = {str(item["id"]): item for item in tree["nodes"]}
    root = str(tree["root"])
    all_ids = set(by_factor)
    state: dict[str, int] = {}
    covers: dict[str, tuple[str, ...]] = {}

    def walk(nid: str) -> tuple[str, ...]:
        if nid not in nodes or state.get(nid) == 1:
            raise AssertionError("tree cycle or missing node")
        if state.get(nid) == 2:
            raise AssertionError("tree node has multiple parents")
        state[nid] = 1
        node = nodes[nid]
        if "factor_id" in node:
            fid = str(node["factor_id"])
            if fid not in by_factor:
                raise AssertionError("tree references unknown factor")
            cover = (fid,)
        else:
            cover = tuple(sorted((*walk(str(node["left"])), *walk(str(node["right"])))))
        covers[nid] = cover
        state[nid] = 2
        return cover

    root_cover = walk(root)
    if len(state) != len(nodes) or sorted(root_cover) != sorted(all_ids) or len(root_cover) != len(set(root_cover)):
        raise AssertionError("tree leaf coverage")

    edges: list[dict] = []
    maximum = 0
    for nid in sorted(nodes):
        if nid == root:
            continue
        covered = covers[nid]
        outside = tuple(sorted(all_ids - set(covered)))
        left_span = xor_basis([v for fid in covered for v in by_factor[fid]["normal_space"]], d)
        right_span = xor_basis([v for fid in outside for v in by_factor[fid]["normal_space"]], d)
        boundary = subspace_intersection(left_span, right_span, d)
        maximum = max(maximum, len(boundary))
        edges.append({
            "node_id": nid,
            "covered_factor_ids": list(covered),
            "outside_factor_ids": list(outside),
            "covered_span_rref": list(left_span),
            "outside_span_rref": list(right_span),
            "boundary_rref": list(boundary),
            "width": len(boundary),
        })
    return {
        "tree_digest": dg(tree),
        "edge_certificates": edges,
        "maximum_nonroot_edge_boundary_dimension": maximum,
        "three_k_cap": 3 * k,
        "all_nonroot_edges_width_le_3k": maximum <= 3 * k,
    }


def scaffold_round(
    prefix: Sequence[dict],
    previous_order_ids: Sequence[str],
    new_factor_id: str,
    d: int,
    k: int,
    round_index: int,
) -> tuple[dict, dict, dict]:
    schedule_ids = [str(x["id"]) for x in prefix]
    local = {fid: i for i, fid in enumerate(schedule_ids)}
    if new_factor_id != schedule_ids[-1]:
        raise AssertionError("new factor must be final prefix occurrence")
    old_order = [local[str(fid)] for fid in previous_order_ids]
    blocks = [tuple(int(v) for v in item["normal_space"]) for item in prefix]
    betas = [item.get("affine_offset") for item in prefix]
    witness = b42.scaffold(blocks, old_order, len(prefix) - 1, d, k, betas)
    if witness.get("terminal") == "NO_LAYOUT_AT_CAP_LOCAL_DIMENSION":
        raise AssertionError("local 2k precheck must intercept B4.2 negative shortcut")
    scaffold_order_ids = [schedule_ids[int(index)] for index in witness["scaffold_order"]]
    tree = left_deep_tree(scaffold_order_ids, round_index)
    cert = tree_boundary_certificate(tree, prefix, d, k)
    candidate_by_left = {
        tuple(schedule_ids[int(index)] for index in edge["left_leaf_ids"]): edge
        for edge in witness.get("candidate_edges", [])
    }
    matched = 0
    for edge in cert["edge_certificates"]:
        key = tuple(scaffold_order_ids[: len(edge["covered_factor_ids"])])
        if tuple(edge["covered_factor_ids"]) == tuple(sorted(key)) and key in candidate_by_left:
            old = candidate_by_left[key]
            if int(old["width"]) != int(edge["width"]):
                raise AssertionError("B4.2/internal tree boundary mismatch")
            matched += 1
    cert["b4_2_prefix_edge_matches"] = matched
    cert["b4_2_candidate_edge_count"] = len(witness.get("candidate_edges", []))
    return witness, tree, cert


def b51_raw(prefix: Sequence[dict], tree: dict, d: int, k: int, runtime_caps: dict) -> dict:
    out = {
        "ambient_dim": d,
        "k": k,
        "factors": [dict(item) for item in prefix],
        "tree": tree,
    }
    if runtime_caps:
        out["caps"] = dict(runtime_caps)
    return out


def run_b53(b51_artifact: dict) -> dict:
    return b53.build(
        load(B53_SPEC),
        b51_artifact,
        load(B5_CONTRACT_RECEIPT),
        load(B51_RECEIPT),
        load(COMPOSITION_AUDIT),
        load(O7_AUDIT),
        load(B52B_RECEIPT),
    )


def run_positive_chain(raw_round: dict, b51_artifact: dict) -> tuple[dict, dict]:
    carrier = b52a.build(raw_round, b51_artifact, load(B52A_AMENDMENT))
    layout = b52b.build(load(B52B_SPEC), raw_round, b51_artifact, carrier)
    return carrier, layout


def deletion_monotonicity_certificate(prefix_ids: Sequence[str], all_ids: Sequence[str], k: int) -> dict:
    prefix = [str(x) for x in prefix_ids]
    whole = [str(x) for x in all_ids]
    if not prefix or prefix == whole or whole[: len(prefix)] != prefix:
        raise AssertionError("strict-prefix monotonicity requires a proper schedule prefix")
    omitted = whole[len(prefix) :]
    return {
        "lemma": "SUBARRANGEMENT_DELETION_MONOTONICITY",
        "prefix_factor_ids": prefix,
        "omitted_factor_ids": omitted,
        "full_factor_ids": whole,
        "prefix_is_strict_schedule_prefix": True,
        "indexed_occurrence_partition": sorted(prefix + omitted) == sorted(whole) and len(set(whole)) == len(whole),
        "hypothetical_full_layout_to_prefix_layout_map": "DELETE_ALL_NONPREFIX_OCCURRENCES_PRESERVING_RELATIVE_ORDER",
        "cut_map": "AFTER_r_PREFIX_OCCURRENCES_IN_THE_INDUCED_ORDER_USE_THE_FULL_LAYOUT_CUT_IMMEDIATELY_AFTER_THE_r_TH_PREFIX_OCCURRENCE",
        "left_span_inclusion": "PREFIX_LEFT_SPAN_LE_FULL_LEFT_SPAN",
        "right_span_inclusion": "PREFIX_RIGHT_SPAN_LE_FULL_RIGHT_SPAN",
        "intersection_inclusion": "PREFIX_LEFT_INTER_PREFIX_RIGHT_LE_FULL_LEFT_INTER_FULL_RIGHT",
        "width_conclusion": "INDUCED_PREFIX_LAYOUT_WIDTH_LE_FULL_LAYOUT_WIDTH",
        "contrapositive": "PREFIX_NO_LAYOUT_AT_WIDTH_LE_K_IMPLIES_FULL_NO_LAYOUT_AT_WIDTH_LE_K",
        "k": int(k),
        "affine_unsat_claimed": False,
    }


def sum_work(total: dict[str, int], work: dict[str, Any]) -> None:
    for key, value in work.items():
        if isinstance(value, int):
            total[key] = int(total.get(key, 0)) + int(value)


def make_round_record(
    round_index: int,
    prefix_ids: Sequence[str],
    new_factor_id: str | None,
    previous_layout_digest: str | None,
    scaffold_witness: dict | None,
    tree: dict,
    tree_cert: dict,
    b51_artifact: dict,
    carrier: dict | None,
    layout: dict | None,
    b53_artifact: dict | None,
    terminal_class: str,
) -> dict:
    nested = {
        "scaffold_witness": scaffold_witness,
        "b5_1": b51_artifact,
        "b5_2a": carrier,
        "b5_2b": layout,
        "b5_3": b53_artifact,
    }
    byte_counts = {key: artifact_bytes(value) for key, value in nested.items()}
    return {
        "round_index": round_index,
        "prefix_factor_ids": list(prefix_ids),
        "new_factor_id_or_base": "BASE" if new_factor_id is None else new_factor_id,
        "previous_verified_layout_digest": previous_layout_digest,
        "tree": tree,
        "tree_boundary_certificate": tree_cert,
        "scaffold_witness": scaffold_witness,
        "b5_1_artifact": b51_artifact,
        "b5_2a_artifact": carrier,
        "b5_2b_artifact": layout,
        "b5_3_artifact": b53_artifact,
        "verified_next_layout": None if layout is None else {
            "factor_order_ids": layout["proof_payload"].get("factor_order_ids"),
            "maximum_cut_width": layout["proof_payload"].get("maximum_cut_width"),
            "semantic_digest": layout.get("semantic_digest"),
        },
        "artifact_byte_counts": byte_counts,
        "round_certificate_bytes": sum(byte_counts.values()),
        "round_terminal_class": terminal_class,
    }


def wrap(spec: dict, payload: dict) -> dict:
    payload["strict_boundary"] = spec["strict_boundary"]
    artifact = {"schema": SCHEMA, "semantic_digest_scope": "proof_payload", "proof_payload": payload}
    artifact["semantic_digest"] = dg(payload)
    return artifact


def execute(raw: dict, spec: dict) -> dict:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_IMPLEMENTATION_CANDIDATE_NOT_ADMITTED":
        raise AssertionError("orchestrator spec")
    d, k, factors, order, runtime_caps, phase_a_caps, max_rounds = canonical_input(raw)
    by = factor_map(factors)
    global_work: dict[str, int] = {}
    rounds: list[dict] = []
    previous_layout_ids: list[str] | None = None
    previous_layout_digest: str | None = None
    terminal: dict[str, Any] | None = None

    base_payload = {
        "gate": spec["gate"],
        "status": "CANDIDATE_PENDING_EXACT_HEAD_CI_AND_REVIEW",
        "ambient_dim": d,
        "k": k,
        "canonical_factor_catalog": factors,
        "input_order": order,
        "runtime_caps": runtime_caps,
        "phase_a_caps": phase_a_caps,
        "max_rounds": max_rounds,
        "normal_space_role": spec["input_contract"]["normal_space_role"],
        "preprocessing_implemented": False,
        "local_2k_negative_certificate_implemented": False,
        "authority_policy": {
            "b4_2_scaffold_is_construction_witness_only": True,
            "tree_boundaries_independently_recomputed": True,
            "b5_3_no_layout_used_as_c047_unsat_premise": False,
            "strict_prefix_negative_requires_deletion_monotonicity": True,
            "capability_open_never_promotes": True,
        },
    }

    for round_index in range(1, len(order) + 1):
        if max_rounds is not None and len(rounds) >= max_rounds:
            terminal = {
                "terminal_class": "OPEN_ORCHESTRATOR_ROUND_CAP",
                "terminal_round_index": round_index,
                "open_reason": {"observed_next_round": round_index, "max_rounds": max_rounds},
                "full_discovery_no_layout_at_cap": False,
                "c047_result": "NOT_ESTABLISHED",
            }
            break

        prefix_ids = order[:round_index]
        prefix_schedule = [dict(by[fid]) for fid in prefix_ids]
        new_factor_id = None if round_index == 1 else prefix_ids[-1]
        scaffold_witness = None

        if round_index == 1:
            tree = left_deep_tree(prefix_ids, round_index)
            tree_cert = tree_boundary_certificate(tree, prefix_schedule, d, k)
        else:
            if previous_layout_ids is None or previous_layout_digest is None:
                raise AssertionError("nonbase round requires previous verified layout candidate")
            if sorted(previous_layout_ids) != sorted(prefix_ids[:-1]) or len(set(previous_layout_ids)) != len(previous_layout_ids):
                raise AssertionError("previous layout is not exact previous prefix permutation")
            new_dim = len(xor_basis(by[new_factor_id]["normal_space"], d))
            if new_dim > 2 * k:
                terminal = {
                    "terminal_class": "OPEN_LOCAL_2K_CERTIFICATE_REQUIRED",
                    "terminal_round_index": round_index,
                    "open_reason": {
                        "new_factor_id": new_factor_id,
                        "observed_discovery_dimension": new_dim,
                        "two_k_cap": 2 * k,
                        "local_negative_certificate_implemented": False,
                    },
                    "full_discovery_no_layout_at_cap": False,
                    "c047_result": "NOT_ESTABLISHED",
                }
                break
            scaffold_witness, tree, tree_cert = scaffold_round(
                prefix_schedule, previous_layout_ids, new_factor_id, d, k, round_index
            )
            if not tree_cert["all_nonroot_edges_width_le_3k"]:
                terminal = {
                    "terminal_class": "OPEN_3K_SCAFFOLD_OR_VERIFICATION",
                    "terminal_round_index": round_index,
                    "open_reason": {
                        "maximum_nonroot_edge_boundary_dimension": tree_cert["maximum_nonroot_edge_boundary_dimension"],
                        "three_k_cap": 3 * k,
                        "scaffold_semantic_digest": scaffold_witness.get("semantic_digest"),
                    },
                    "full_discovery_no_layout_at_cap": False,
                    "c047_result": "NOT_ESTABLISHED",
                }
                break

        round_raw = b51_raw(prefix_schedule, tree, d, k, runtime_caps)
        b51_artifact = b51.execute(round_raw, load(B51_SPEC))
        q51 = b51_artifact["proof_payload"]
        sum_work(global_work, q51.get("global_work_ledger", {}))

        if q51["capability_status"] == b51.OPEN:
            record = make_round_record(
                round_index, prefix_ids, new_factor_id, previous_layout_digest,
                scaffold_witness, tree, tree_cert, b51_artifact, None, None, None,
                "OPEN_B5_1_RUNTIME_CAPABILITY",
            )
            rounds.append(record)
            terminal = {
                "terminal_class": "OPEN_B5_1_RUNTIME_CAPABILITY",
                "terminal_round_index": round_index,
                "open_reason": q51["open_reason"],
                "full_discovery_no_layout_at_cap": False,
                "c047_result": "NOT_ESTABLISHED",
            }
            break
        if q51["capability_status"] != b51.CLOSED:
            raise AssertionError("unknown B5.1 capability status")

        if int(q51["root_entry_count_if_closed"]) == 0:
            neg = run_b53(b51_artifact)
            p53 = neg["proof_payload"]
            if p53.get("candidate_no_layout_at_cap") is not True:
                raise AssertionError("empty B5.1 root did not produce B5.3 negative candidate")
            is_full = round_index == len(order)
            bridge = None if is_full else deletion_monotonicity_certificate(prefix_ids, order, k)
            record = make_round_record(
                round_index, prefix_ids, new_factor_id, previous_layout_digest,
                scaffold_witness, tree, tree_cert, b51_artifact, None, None, neg,
                "FULL_INPUT_NO_LAYOUT_AT_CAP" if is_full else "STRICT_PREFIX_NO_LAYOUT_AT_CAP_WITH_DELETION_MONOTONICITY",
            )
            record["strict_prefix_deletion_monotonicity"] = bridge
            rounds.append(record)
            terminal = {
                "terminal_class": record["round_terminal_class"],
                "terminal_round_index": round_index,
                "b5_3_semantic_digest": neg["semantic_digest"],
                "strict_prefix_deletion_monotonicity": bridge,
                "full_discovery_no_layout_at_cap": True,
                "affine_instance_unsat": "NOT_ESTABLISHED",
                "c047_result": "NOT_ESTABLISHED",
            }
            break

        carrier, layout = run_positive_chain(round_raw, b51_artifact)
        p52 = layout["proof_payload"]
        if p52.get("candidate_found_layout") is not True or p52.get("factor_order_ids") is None:
            raise AssertionError("nonempty B5.1 root did not reconstruct layout")
        next_order = [str(fid) for fid in p52["factor_order_ids"]]
        if sorted(next_order) != sorted(prefix_ids) or len(set(next_order)) != len(next_order):
            raise AssertionError("B5.2B layout is not exact prefix permutation")
        if int(p52["maximum_cut_width"]) > k:
            raise AssertionError("B5.2B layout exceeds k")

        record = make_round_record(
            round_index, prefix_ids, new_factor_id, previous_layout_digest,
            scaffold_witness, tree, tree_cert, b51_artifact, carrier, layout, None,
            "POSITIVE_PREFIX_LAYOUT" if round_index < len(order) else "FULL_INPUT_POSITIVE_LAYOUT",
        )
        rounds.append(record)
        previous_layout_ids = next_order
        previous_layout_digest = layout["semantic_digest"]

        if round_index == len(order):
            c047 = b54.build(load(B54_SPEC), round_raw, b51_artifact, carrier, layout, phase_a_caps)
            p54 = c047["proof_payload"]
            record["b5_4_artifact"] = c047
            record["artifact_byte_counts"]["b5_4"] = artifact_bytes(c047)
            record["round_certificate_bytes"] += artifact_bytes(c047)
            rebound = str(p54["rebound_status"])
            c047_result = str(p54["c047_result"])
            if rebound == "PHASE_A_C047_REPLAY_COMPLETED" and c047_result in {"SAT", "UNSAT"}:
                tclass = "FULL_INPUT_C047_" + c047_result
            else:
                tclass = rebound if rebound.startswith("OPEN_") else "OPEN_FINAL_B5_4_" + rebound
            record["round_terminal_class"] = tclass
            terminal = {
                "terminal_class": tclass,
                "terminal_round_index": round_index,
                "b5_4_semantic_digest": c047["semantic_digest"],
                "verified_full_input_layout_digest": layout["semantic_digest"],
                "full_discovery_no_layout_at_cap": False,
                "c047_result": c047_result,
                "historical_phase_a_verifier_pass": p54.get("historical_phase_a_verifier_pass", False),
            }
            break

    if terminal is None:
        raise AssertionError("orchestrator did not produce a terminal or OPEN")

    certificate_bytes = sum(int(r["round_certificate_bytes"]) for r in rounds)
    payload = dict(base_payload)
    payload.update({
        "rounds": rounds,
        "global_ledger": {
            "attempted_round_count": len(rounds) + (1 if terminal["terminal_class"] in {"OPEN_LOCAL_2K_CERTIFICATE_REQUIRED", "OPEN_3K_SCAFFOLD_OR_VERIFICATION", "OPEN_ORCHESTRATOR_ROUND_CAP"} else 0),
            "completed_round_count": len(rounds),
            "round_indices": [int(r["round_index"]) for r in rounds],
            "sum_b5_1_global_work_ledger": global_work,
            "sum_serialized_round_certificate_bytes": certificate_bytes,
            "failed_join_refinement_work_preserved_inside_b5_1_ledgers": True,
            "work_counter_reset_between_rounds": False,
        },
        "terminal": terminal,
        "terminal_promotion_policy": {
            "open_promoted": False,
            "b5_3_no_layout_used_as_c047_unsat_premise": False,
            "strict_prefix_negative_requires_deletion_monotonicity": True,
        },
    })
    return wrap(spec, payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifact = execute(load(args.input), load(args.spec))
    save(artifact, args.output)
    p = artifact["proof_payload"]
    print("JANUS_B5_ITERATIVE_COMPRESSION_ORCHESTRATOR = PASS")
    print("ROUND_COUNT =", len(p["rounds"]))
    print("TERMINAL_CLASS =", p["terminal"]["terminal_class"])
    print("FULL_DISCOVERY_NO_LAYOUT_AT_CAP =", str(p["terminal"].get("full_discovery_no_layout_at_cap", False)).upper())
    print("C047_RESULT =", p["terminal"].get("c047_result", "NOT_ESTABLISHED"))
    print("PREPROCESSING_IMPLEMENTED = FALSE")
    print("LOCAL_2K_NEGATIVE_CERTIFICATE_IMPLEMENTED = FALSE")
    print("ALL_INPUT_TERMINATION = NOT_ESTABLISHED")
    print("POLYNOMIAL_RUNTIME = NOT_ESTABLISHED")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")
    print("SEMANTIC_DIGEST =", artifact["semantic_digest"])


if __name__ == "__main__":
    main()
