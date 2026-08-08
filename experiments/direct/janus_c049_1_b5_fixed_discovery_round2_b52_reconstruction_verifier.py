from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SPEC_SCHEMA = "janus.c049_1.b5.fixed_discovery_round2_b52_reconstruction_spec.v1"
PLAN_SCHEMA = "janus.c049_1.b5.fixed_discovery_round_orchestration_binding_candidate.v1_1"
B51_SCHEMA = "janus.c049_1.b5_1.generic_corrected_runtime_trace.v1"
B52A_SCHEMA = "janus.c049_1.b5_2a.generic_algorithm2_provenance_carrier.v1_1"
B52B_SCHEMA = "janus.c049_1.b5_2b.generic_algorithm2_printorder_reconstruction_candidate.v1"


def cb(x: Any) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(",", ":")).encode("utf-8")


def dg(x: Any) -> str:
    return hashlib.sha256(cb(x)).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def id_key(value: Any) -> str:
    return cb(value).decode("utf-8")


def verify(spec: dict, pre: dict, plan: dict, round2_input: dict, b51: dict, carrier: dict, layout: dict) -> dict:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_CANDIDATE_ONLY":
        raise AssertionError("spec")
    if plan.get("schema") != PLAN_SCHEMA or plan.get("semantic_digest") != dg(plan.get("proof_payload")):
        raise AssertionError("plan")
    pp = pre.get("proof_payload")
    pl = plan["proof_payload"]
    if not isinstance(pp, dict) or pre.get("semantic_digest") != dg(pp):
        raise AssertionError("preprocessing")
    if pl.get("preprocessing_authority_version") != "V1_1_CANONICAL_RREF":
        raise AssertionError("preprocessing authority")
    if pl.get("preprocessing_semantic_digest") != pre.get("semantic_digest"):
        raise AssertionError("preprocessing subject")
    schedule = pl.get("schedule_occurrence_indices")
    rounds = pl.get("rounds")
    if not isinstance(schedule, list) or len(schedule) < 2 or not isinstance(rounds, list) or len(rounds) < 2:
        raise AssertionError("round plan")
    expected_prefix = schedule[:2]
    if expected_prefix != spec["subject_contract"]["round_prefix_occurrence_indices"]:
        raise AssertionError("round2 prefix spec binding")
    if rounds[1].get("prefix_occurrence_indices") != expected_prefix:
        raise AssertionError("round2 prefix plan binding")

    by_occ = {int(x["occurrence_index"]): x for x in pp["discovery_catalog"]}
    expected_records = [by_occ[i] for i in expected_prefix]
    expected_factor_ids = [x["factor_id"] for x in expected_records]
    expected_by_id = {id_key(x["factor_id"]): x for x in expected_records}

    input_factors = round2_input.get("factors")
    if not isinstance(input_factors, list) or len(input_factors) != 2:
        raise AssertionError("round2 input count")
    expected_input = [
        {"id": x["factor_id"], "normal_space": x["normal_space"], "affine_offset": x["affine_offset"]}
        for x in expected_records
    ]
    if input_factors != expected_input:
        raise AssertionError("round2 input exact fixed-prefix binding")

    if b51.get("schema") != B51_SCHEMA or b51.get("semantic_digest") != dg(b51.get("proof_payload")):
        raise AssertionError("B5.1 headers/digest")
    b = b51["proof_payload"]
    if b.get("capability_status") != "CLOSED_COMPLETE_TRACE":
        raise AssertionError("B5.1 not closed")
    if int(b.get("root_entry_count_if_closed") or 0) != spec["subject_contract"]["round2_root_entry_count"]:
        raise AssertionError("round2 root count")
    if int(b.get("root_entry_count_if_closed") or 0) <= 0:
        raise AssertionError("round2 root empty")

    if carrier.get("schema") != B52A_SCHEMA or carrier.get("semantic_digest") != dg(carrier.get("proof_payload")):
        raise AssertionError("B5.2A headers/digest")
    c = carrier["proof_payload"]
    if c.get("subject", {}).get("b5_1_semantic_digest") != b51["semantic_digest"]:
        raise AssertionError("B5.2A/B5.1 subject digest")
    if c.get("subject", {}).get("b5_1_root_full_set_digest") != b.get("root_full_set_digest_if_closed"):
        raise AssertionError("B5.2A/B5.1 root digest")
    if c.get("subject", {}).get("b5_1_root_entry_count") != b.get("root_entry_count_if_closed"):
        raise AssertionError("B5.2A/B5.1 root count")
    summary = c.get("backtracking_summary", {})
    if summary.get("root_entries") != b.get("root_entry_count_if_closed"):
        raise AssertionError("B5.2A root summary")
    if summary.get("root_entries_with_complete_backtrack") != b.get("root_entry_count_if_closed"):
        raise AssertionError("B5.2A incomplete root backtrack")
    if summary.get("dangling_reference_count") != 0:
        raise AssertionError("B5.2A dangling provenance")

    if layout.get("schema") != B52B_SCHEMA or layout.get("semantic_digest") != dg(layout.get("proof_payload")):
        raise AssertionError("B5.2B headers/digest")
    q = layout["proof_payload"]
    if q.get("b5_1_semantic_digest") != b51["semantic_digest"]:
        raise AssertionError("B5.2B/B5.1 subject")
    if q.get("carrier_semantic_digest") != carrier["semantic_digest"]:
        raise AssertionError("B5.2B/carrier subject")
    if q.get("reconstruction_status") != "LAYOUT_CANDIDATE_RECONSTRUCTED_PENDING_REVIEW":
        raise AssertionError("reconstruction status")
    if q.get("candidate_found_layout") is not True:
        raise AssertionError("candidate found layout")
    if q.get("found_layout_promotion") != "FORBIDDEN_PENDING_B5_2B_EXACT_HEAD_CI_AND_REVIEW":
        raise AssertionError("premature found-layout promotion")
    if q.get("generic_no_layout_at_cap") != "FORBIDDEN_PENDING_B5_3":
        raise AssertionError("negative promotion")

    order = q.get("factor_order_ids")
    if not isinstance(order, list) or len(order) != len(expected_factor_ids):
        raise AssertionError("factor order length")
    order_keys = [id_key(x) for x in order]
    expected_keys = [id_key(x) for x in expected_factor_ids]
    if sorted(order_keys) != sorted(expected_keys) or len(set(order_keys)) != len(order_keys):
        raise AssertionError("factor order not exact fixed-prefix permutation")

    layout_records = q.get("layout_records")
    if not isinstance(layout_records, list) or len(layout_records) != len(order):
        raise AssertionError("layout records")
    for pos, (fid, record) in enumerate(zip(order, layout_records)):
        source = expected_by_id[id_key(fid)]
        expected = {
            "position": pos,
            "factor_id": fid,
            "normal_space": source["normal_space"],
            "affine_offset": source["affine_offset"],
        }
        if record != expected:
            raise AssertionError("layout record fixed-discovery identity")

    max_width = q.get("maximum_cut_width")
    if not isinstance(max_width, int) or max_width > int(pp["k"]):
        raise AssertionError("maximum width")
    cuts = q.get("cut_certificates")
    if not isinstance(cuts, list) or len(cuts) != len(order) + 1:
        raise AssertionError("cut certificates")
    if max(int(x["width"]) for x in cuts) != max_width:
        raise AssertionError("cut/max width disagreement")

    sb = q.get("strict_boundary", {})
    if sb.get("b5_complete") is not False or sb.get("p_vs_np") != "OPEN":
        raise AssertionError("B5.2B global promotion")
    if spec["strict_boundary"].get("c047") != "NOT_INVOKED":
        raise AssertionError("spec C047 boundary")

    return {
        "status": "PASS",
        "round2_prefix_occurrence_indices": expected_prefix,
        "round2_factor_ids": expected_factor_ids,
        "verified_factor_order_ids": order,
        "maximum_cut_width": max_width,
        "k": int(pp["k"]),
        "root_entry_count": int(b["root_entry_count_if_closed"]),
        "next_gate": "C049.1_B5_FIXED_DISCOVERY_ROUND3_EXECUTION_FROM_VERIFIED_PREFIX_LAYOUT",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    for name in ("spec", "preprocessing", "plan", "round2-input", "b5-1-artifact", "carrier", "layout"):
        ap.add_argument("--" + name, type=Path, required=True)
    a = ap.parse_args()
    report = verify(
        load(a.spec), load(a.preprocessing), load(a.plan), load(a.round2_input),
        load(a.b5_1_artifact), load(a.carrier), load(a.layout)
    )
    print("JANUS_B5_FIXED_DISCOVERY_ROUND2_B52_RECONSTRUCTION_BINDER = PASS")
    print("ROUND2_PREFIX_OCCURRENCES =", report["round2_prefix_occurrence_indices"])
    print("ROUND2_ROOT_ENTRIES =", report["root_entry_count"])
    print("B5_2A_COMPLETE_ROOT_BACKTRACK = PASS")
    print("B5_2B_FIXED_PREFIX_PERMUTATION = PASS")
    print("B5_2B_AFFINE_IDENTITY = PASS")
    print("VERIFIED_FACTOR_ORDER_IDS =", json.dumps(report["verified_factor_order_ids"], sort_keys=True, separators=(",", ":")))
    print("MAXIMUM_CUT_WIDTH =", report["maximum_cut_width"])
    print("K =", report["k"])
    print("VERIFIED_WIDTH_K_PREFIX_LAYOUT = PASS")
    print("C047 = NOT_INVOKED")
    print("NEXT_GATE =", report["next_gate"])
    print("FULL_SCHEDULE_EXECUTION = NOT_ESTABLISHED")
    print("B5_COMPLETE = FALSE")
    print("C049_1_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
