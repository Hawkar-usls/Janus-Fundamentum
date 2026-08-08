from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from janus_c047_affine_trellis_core import affine_rref, input_length, linear_rref
from janus_c049_fpt_integration_core import IntegrationCapability, layout_data_from_spaces, make_found_layout_transcript
from janus_c049_fpt_integration_verifier import verify as verify_phase_a
import janus_c049_1_b5_2a_generic_algorithm2_provenance_carrier_verifier_v11 as b52a_verifier
import janus_c049_1_b5_2b_generic_algorithm2_printorder_reconstruction_verifier as b52b_verifier

SCHEMA = "janus.c049_1.b5_4.corrected_discovery_c047_rebound_candidate.v1"
SPEC_SCHEMA = "janus.c049_1.b5_4.corrected_discovery_c047_rebound_spec.v1"
B5_1_SCHEMA = "janus.c049_1.b5_1.generic_corrected_runtime_trace.v1"
B5_2B_SCHEMA = "janus.c049_1.b5_2b.generic_algorithm2_printorder_reconstruction_candidate.v1"
AFFINE_SCHEMA = "janus.c049_1.c047_affine_equations.v1"


def cb(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def dg(value: Any) -> str:
    return hashlib.sha256(cb(value)).hexdigest()


def load(path: Path | None) -> Any:
    return None if path is None else json.loads(path.read_text(encoding="utf-8"))


def semantic_space(rows, dimension: int) -> tuple[int, ...]:
    return linear_rref([int(x) for x in rows], dimension)


def verify_admission_receipts(spec: dict, b52_receipt: dict, b53_receipt: dict) -> dict:
    a52 = spec["authority_inputs"]["b5_2b_positive_terminal_admission"]
    if b52_receipt.get("schema") != "janus.c049_1.b5_2b.generic_algorithm2_printorder_reconstruction_admission_receipt.v1":
        raise AssertionError("B5.2B admission schema")
    if b52_receipt.get("semantic_digest") != a52["receipt_semantic_digest"] or dg(b52_receipt["audit_payload"]) != a52["receipt_semantic_digest"]:
        raise AssertionError("B5.2B admission digest")
    p52 = b52_receipt["audit_payload"]
    if p52.get("admission_review_id") != a52["review_id"] or p52.get("exact_proof_head") != a52["proof_head"]:
        raise AssertionError("B5.2B admission authority")
    if p52["semantic_conclusion"].get("generic_found_layout") != "TRUE_WHEN_B5_1_CLOSED_ROOT_NONEMPTY_AND_B5_2A_B5_2B_VERIFY":
        raise AssertionError("B5.2B admitted statement")

    a53 = spec["authority_inputs"]["b5_3_negative_terminal_admission"]
    if b53_receipt.get("schema") != "janus.c049_1.b5_3.generic_empty_root_terminal_composition_admission_receipt.v1_1":
        raise AssertionError("B5.3 admission schema")
    if b53_receipt.get("semantic_digest") != a53["receipt_semantic_digest"] or dg(b53_receipt["audit_payload"]) != a53["receipt_semantic_digest"]:
        raise AssertionError("B5.3 admission digest")
    p53 = b53_receipt["audit_payload"]
    if p53.get("admission_review_id") != a53["review_id"] or p53.get("exact_proof_head") != a53["proof_head"]:
        raise AssertionError("B5.3 admission authority")
    if p53["admitted_statement"].get("generic_no_layout_at_cap") != "TRUE_WHEN_B5_1_VERIFIED_CLOSED_ROOT_EMPTY_AND_B5_3_AUTHORITY_BRIDGE_PASSES":
        raise AssertionError("B5.3 admitted statement")
    return {
        "b5_2b_proof_head": a52["proof_head"],
        "b5_2b_review_id": a52["review_id"],
        "b5_2b_admission_semantic_digest": a52["receipt_semantic_digest"],
        "b5_3_proof_head": a53["proof_head"],
        "b5_3_review_id": a53["review_id"],
        "b5_3_admission_semantic_digest": a53["receipt_semantic_digest"],
        "historical_phase_a_subject": spec["authority_inputs"]["historical_phase_a"]["proof_subject"],
    }


def parse_profile(offset: Any, dimension: int) -> tuple[str, tuple[tuple[int, int], ...] | None, str | None]:
    if not isinstance(offset, dict) or offset.get("schema") != AFFINE_SCHEMA:
        return "OPEN_AFFINE_REBOUND_BINDING", None, "MISSING_CANONICAL_AFFINE_PROFILE"
    eqs = offset.get("equations")
    if not isinstance(eqs, list) or not eqs:
        return "OPEN_AFFINE_REBOUND_BINDING", None, "EMPTY_OR_NONLIST_EQUATIONS"
    parsed = []
    limit = 1 << dimension
    for row in eqs:
        if not isinstance(row, list) or len(row) != 2:
            return "OPEN_AFFINE_REBOUND_BINDING", None, "BAD_EQUATION_SHAPE"
        mask, beta = row
        if not isinstance(mask, int) or not isinstance(beta, int) or not (0 <= mask < limit) or beta not in (0, 1):
            return "OPEN_AFFINE_REBOUND_BINDING", None, "BAD_EQUATION_VALUE"
        parsed.append((mask, beta))
    rr = affine_rref(parsed, dimension)
    if rr is None:
        return "OPEN_NONBIJECTIVE_AFFINE_NORMALIZATION", None, "INCONSISTENT_AFFINE_FACTOR_WOULD_BE_DROPPED"
    return "BOUND", rr, None


def independent_adapter(catalog: list[dict], dimension: int) -> tuple[str, list[dict], list[dict], str | None]:
    factors = []
    mapping = []
    seen = set()
    for pos, factor in enumerate(catalog):
        key = cb(factor["id"]).decode("utf-8")
        if key in seen:
            return "OPEN_AFFINE_REBOUND_BINDING", [], [], "DUPLICATE_B5_FACTOR_ID"
        seen.add(key)
        status, rr, reason = parse_profile(factor.get("affine_offset"), dimension)
        if status != "BOUND" or rr is None:
            return status, [], [], reason
        b5space = semantic_space(factor["normal_space"], dimension)
        phase_space = linear_rref([mask for mask, _ in rr], dimension)
        if b5space != phase_space:
            return "OPEN_AFFINE_REBOUND_BINDING", [], [], "AFFINE_NORMAL_SPAN_MISMATCH"
        equations = [[int(mask), int(beta)] for mask, beta in rr]
        factors.append({"factor_id": pos, "equations": equations})
        mapping.append({
            "b5_factor_id": factor["id"],
            "phase_a_numeric_factor_id": pos,
            "phase_a_input_position": pos,
            "b5_normal_space_serialized": factor["normal_space"],
            "phase_a_normal_space_rref": list(phase_space),
            "normal_space_rref": list(b5space),
            "normal_space_semantic_digest": dg(list(b5space)),
            "semantic_normal_space_equal": True,
            "raw_list_byte_equal": factor["normal_space"] == list(phase_space),
            "affine_offset_identity_digest": dg(factor.get("affine_offset")),
            "normalized_equations": equations,
            "normalized_equations_digest": dg(equations),
        })
    return "BOUND", factors, mapping, None


def phase_capability(dimension: int, factors: list[dict], k: int, caps: dict) -> IntegrationCapability:
    return IntegrationCapability(
        input_length(factors, dimension), k,
        discovery_cap=caps.get("discovery_cap"),
        work_cap=caps.get("work_cap"),
        certificate_cap=caps.get("certificate_cap"),
        trellis_work_cap=caps.get("trellis_work_cap"),
        trellis_certificate_cap=caps.get("trellis_certificate_cap"),
    )


def expected_cut_bridge(b52: dict, layout: dict, dimension: int) -> list[dict]:
    cuts = b52["proof_payload"]["cut_certificates"]
    if len(cuts) != len(layout["cut_widths"]):
        raise AssertionError("cut count")
    out = []
    for i, cut in enumerate(cuts):
        b5basis = semantic_space(cut["boundary_rref"], dimension)
        phasebasis = semantic_space(layout["cut_bases"][i], dimension)
        if int(cut["width"]) != int(layout["cut_widths"][i]) or b5basis != phasebasis:
            raise AssertionError("cut bridge")
        out.append({"cut": i, "width": int(layout["cut_widths"][i]), "b5_boundary_semantic_digest": dg(list(b5basis)), "phase_a_boundary_semantic_digest": dg(list(phasebasis)), "semantic_boundary_equal": True})
    return out


def fixed_base(spec: dict, raw: dict, b51: dict, carrier: dict | None, b52: dict | None, caps: dict, authority: dict) -> dict:
    q = b51["proof_payload"]
    return {
        "gate": spec["gate"],
        "status": "CANDIDATE_PENDING_EXACT_HEAD_CI_AND_REVIEW",
        "subject": {
            "b5_1_semantic_digest": b51["semantic_digest"],
            "b5_2a_carrier_semantic_digest": None if carrier is None else carrier.get("semantic_digest"),
            "b5_2b_semantic_digest": None if b52 is None else b52.get("semantic_digest"),
            "b5_1_capability_status": q["capability_status"],
            "root_entry_count_if_closed": q.get("root_entry_count_if_closed"),
        },
        "ambient_dim": int(q["ambient_dim"]),
        "k": int(q["k"]),
        "canonical_factor_catalog": q["canonical_factor_catalog"],
        "phase_a_capability_request": {key: caps.get(key) for key in sorted(caps)},
        "authority_bindings": authority,
        "authority_policy": {
            "b5_2b_positive_terminal_required_for_found_layout_rebound": True,
            "b5_3_negative_terminal_is_branch_separation_only": True,
            "b5_3_no_layout_used_as_c047_unsat_premise": False,
            "historical_phase_a_c047_code_modified": False,
        },
    }


def add_ceiling(spec: dict, payload: dict) -> dict:
    payload["strict_boundary"] = spec["strict_boundary"]
    payload["scope_ceiling"] = {
        "c047_result_admitted": False,
        "affine_instance_sat_or_unsat_admitted": False,
        "all_input_termination": "NOT_ESTABLISHED",
        "polynomial_runtime": "NOT_ESTABLISHED",
        "b5_complete": False,
        "arbitrary_input_global_engine_theorem": False,
        "p_vs_np": "OPEN",
        "formal_admission": "BLOCKED_PENDING_REVIEW",
    }
    return payload


def verify(candidate: dict, spec: dict, raw: dict, b51: dict, carrier: dict | None, b52: dict | None, carrier_spec: dict, b52_spec: dict, b52_receipt: dict, b53_receipt: dict, caps: dict) -> dict:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_CANDIDATE_ONLY": raise AssertionError("spec")
    if b51.get("schema") != B5_1_SCHEMA or b51.get("semantic_digest_scope") != "proof_payload" or b51.get("semantic_digest") != dg(b51["proof_payload"]): raise AssertionError("B5.1")
    if candidate.get("schema") != SCHEMA or candidate.get("semantic_digest_scope") != "proof_payload" or candidate.get("semantic_digest") != dg(candidate["proof_payload"]): raise AssertionError("candidate")
    authority = verify_admission_receipts(spec,b52_receipt,b53_receipt)
    q=b51["proof_payload"]; d=int(q["ambient_dim"]); k=int(q["k"])
    if int(raw["ambient_dim"])!=d or int(raw["k"])!=k: raise AssertionError("raw/B5 params")
    base=fixed_base(spec,raw,b51,carrier,b52,caps,authority)

    if q["capability_status"]=="OPEN_RUNTIME_CAPABILITY":
        expected=add_ceiling(spec,{**base,"rebound_status":"NOT_APPLICABLE_OPEN_RUNTIME","affine_binding_status":"NOT_ATTEMPTED","phase_a_factor_bijection":None,"phase_a_factors":None,"phase_a_order_positions":None,"phase_a_transcript":None,"phase_a_certificate":None,"historical_phase_a_verifier_pass":False,"c047_result":"NOT_ESTABLISHED"})
        if candidate["proof_payload"]!=expected: raise AssertionError("OPEN branch")
        return expected
    if q["capability_status"]!="CLOSED_COMPLETE_TRACE": raise AssertionError("B5.1 status")
    if carrier is None or b52 is None: raise AssertionError("closed upstream missing")

    # Independently re-verify the admitted positive discovery chain before rebound interpretation.
    b52a_verifier.verify_v11(carrier,raw,b51,carrier_spec)
    b52b_verifier.verify(b52,b52_spec,raw,b51,carrier)
    if b52.get("schema")!=B5_2B_SCHEMA: raise AssertionError("B5.2B schema")
    p52=b52["proof_payload"]
    if p52["canonical_factor_catalog"]!=q["canonical_factor_catalog"]: raise AssertionError("catalog")

    if p52["reconstruction_status"]=="NOT_APPLICABLE_EMPTY_ROOT":
        expected=add_ceiling(spec,{**base,"rebound_status":"NOT_APPLICABLE_NO_FOUND_LAYOUT","affine_binding_status":"NOT_ATTEMPTED","phase_a_factor_bijection":None,"phase_a_factors":None,"phase_a_order_positions":None,"phase_a_transcript":None,"phase_a_certificate":None,"historical_phase_a_verifier_pass":False,"c047_result":"NOT_ESTABLISHED_DEFER_TO_B5_3"})
        if candidate["proof_payload"]!=expected: raise AssertionError("empty-root branch")
        return expected
    if p52["reconstruction_status"]!="LAYOUT_CANDIDATE_RECONSTRUCTED_PENDING_REVIEW" or p52["candidate_found_layout"] is not True: raise AssertionError("B5.2B positive")

    status,factors,mapping,reason=independent_adapter(q["canonical_factor_catalog"],d)
    if status!="BOUND":
        expected=add_ceiling(spec,{**base,"rebound_status":status,"affine_binding_status":status,"affine_binding_open_reason":reason,"phase_a_factor_bijection":None,"phase_a_factors":None,"phase_a_order_positions":None,"phase_a_transcript":None,"phase_a_certificate":None,"historical_phase_a_verifier_pass":False,"c047_result":"NOT_ESTABLISHED"})
        if candidate["proof_payload"]!=expected: raise AssertionError("affine OPEN branch")
        return expected

    by={cb(x["b5_factor_id"]).decode("utf-8"):x for x in mapping}
    order=[]
    for fid in p52["factor_order_ids"]:
        key=cb(fid).decode("utf-8")
        if key not in by: raise AssertionError("unmapped order")
        order.append(int(by[key]["phase_a_input_position"]))
    if sorted(order)!=list(range(len(factors))): raise AssertionError("order permutation")
    spaces=[tuple(mask for mask,_ in f["equations"]) for f in factors]
    layout=layout_data_from_spaces(spaces,order,d)
    if int(layout["maximum_width"])!=int(p52["maximum_cut_width"]): raise AssertionError("max width")
    bridge=expected_cut_bridge(b52,layout,d)
    transcript=make_found_layout_transcript(order,layout["cut_widths"],layout["cut_bases"],constructor_id="B5_2B_CORRECTED_GENERIC_DISCOVERY_REBOUND",discovery_claim=True,constructor_trace={"b5_2b_semantic_digest":b52["semantic_digest"],"b5_factor_order_ids":p52["factor_order_ids"],"factor_bijection_digest":dg(mapping),"cut_bridge_digest":dg(bridge),"affine_rebound_profile":AFFINE_SCHEMA})

    p=candidate["proof_payload"]
    fields={"phase_a_factor_bijection":mapping,"phase_a_factor_bijection_digest":dg(mapping),"phase_a_factors":factors,"phase_a_factor_catalog_digest":dg(factors),"phase_a_order_positions":order,"phase_a_layout_recomputation":layout,"b5_to_phase_a_cut_bridge":bridge,"phase_a_transcript":transcript}
    for key,value in fields.items():
        if p.get(key)!=value: raise AssertionError("rebound field "+key)
    cert=p.get("phase_a_certificate")
    if not isinstance(cert,dict): raise AssertionError("missing Phase-A certificate")
    verify_phase_a(factors,d,cert)
    expected={**base,"rebound_status":"PHASE_A_C047_REPLAY_COMPLETED" if cert["status"] in ("SAT","UNSAT") else "PHASE_A_C047_REPLAY_OPEN","affine_binding_status":"BOUND","affine_binding_open_reason":None,**fields,"phase_a_certificate":cert,"historical_phase_a_verifier_pass":True,"c047_result":cert["status"],"c047_reason":cert.get("reason")}
    expected=add_ceiling(spec,expected)
    if p!=expected: raise AssertionError("completed rebound payload")
    return expected


def repair(candidate: dict) -> dict:
    candidate["semantic_digest"]=dg(candidate["proof_payload"]); return candidate


def tamper_suite(subjects: dict, spec: dict, carrier_spec: dict, b52_spec: dict, r52: dict, r53: dict, caps: dict) -> tuple[int,int]:
    attacks=[]
    def add(name, key, mutate):
        s=subjects[key]; c=copy.deepcopy(s["candidate"]); mutate(c["proof_payload"]); attacks.append((name,key,repair(c)))
    sat=subjects["sat"]["candidate"]["proof_payload"]
    if sat["c047_result"]!="SAT": raise AssertionError("SAT control missing")
    if subjects["unsat"]["candidate"]["proof_payload"]["c047_result"]!="UNSAT": raise AssertionError("UNSAT control missing")
    if not str(subjects["hist_open"]["candidate"]["proof_payload"]["c047_result"]).startswith("OPEN_"): raise AssertionError("historical OPEN control missing")
    add("T01_B52_AUTHORITY","sat",lambda p:p["authority_bindings"].__setitem__("b5_2b_review_id",0))
    add("T02_B53_AS_UNSAT","empty",lambda p:p.update({"rebound_status":"PHASE_A_C047_REPLAY_COMPLETED","c047_result":"UNSAT"}))
    add("T03_OPAQUE_PROMOTION","opaque",lambda p:p.update({"affine_binding_status":"BOUND","rebound_status":"PHASE_A_C047_REPLAY_COMPLETED","c047_result":"SAT"}))
    add("T04_BETA","sat",lambda p:p["phase_a_factors"][0]["equations"][0].__setitem__(1,1-p["phase_a_factors"][0]["equations"][0][1]))
    add("T05_MASK","sat",lambda p:p["phase_a_factors"][0]["equations"][0].__setitem__(0,p["phase_a_factors"][0]["equations"][0][0]^1))
    add("T06_GEOMETRY_DEDUP","unsat",lambda p:p["phase_a_factor_bijection"].pop())
    add("T07_POSITION_COLLISION","sat",lambda p:p["phase_a_factor_bijection"][1].__setitem__("phase_a_input_position",0))
    add("T08_ID_CONFUSION","sat",lambda p:p["phase_a_factor_bijection"][0].__setitem__("phase_a_numeric_factor_id",p["phase_a_factor_bijection"][0]["b5_factor_id"]))
    add("T09_OMIT_FACTOR","sat",lambda p:p["phase_a_factors"].pop())
    add("T10_ORDER","sat",lambda p:p.__setitem__("phase_a_order_positions",list(reversed(p["phase_a_order_positions"]))))
    add("T11_CUT_WIDTH","sat",lambda p:p["phase_a_layout_recomputation"]["cut_widths"].__setitem__(0,999))
    add("T12_CUT_BASIS","sat",lambda p:p["phase_a_layout_recomputation"]["cut_bases"].__setitem__(0,[999]))
    add("T13_TRANSCRIPT_DIGEST","sat",lambda p:p["phase_a_transcript"].__setitem__("transcript_digest","0"*64))
    add("T14_FORGE_SAT","unsat",lambda p:p.update({"c047_result":"SAT","rebound_status":"PHASE_A_C047_REPLAY_COMPLETED"}))
    add("T15_FORGE_UNSAT","sat",lambda p:p.update({"c047_result":"UNSAT","rebound_status":"PHASE_A_C047_REPLAY_COMPLETED"}))
    add("T16_OPEN_PROMOTION","hist_open",lambda p:p.update({"c047_result":"SAT","rebound_status":"PHASE_A_C047_REPLAY_COMPLETED"}))
    add("T17_INCONSISTENT_DROP","inconsistent",lambda p:p.update({"affine_binding_status":"BOUND","rebound_status":"PHASE_A_C047_REPLAY_COMPLETED","c047_result":"SAT"}))
    add("T18_EMPTY_C047","empty",lambda p:p.__setitem__("c047_result","UNSAT"))
    add("T19_B51_OPEN_C047","b5_open",lambda p:p.__setitem__("c047_result","SAT"))
    add("T20_NO_HIST_VERIFIER","sat",lambda p:p.__setitem__("historical_phase_a_verifier_pass",False))
    add("T21_RUNTIME_CLAIM","sat",lambda p:p["scope_ceiling"].update({"all_input_termination":"ESTABLISHED","polynomial_runtime":"ESTABLISHED"}))
    add("T22_GLOBAL_CLAIM","sat",lambda p:p["scope_ceiling"].update({"b5_complete":True,"arbitrary_input_global_engine_theorem":True,"p_vs_np":"CLOSED"}))
    add("T23_OFFSET_IDENTITY","sat",lambda p:p["phase_a_factor_bijection"][0].__setitem__("affine_offset_identity_digest","0"*64))
    add("T24_RAW_BYTE_EQUALITY","basis_order",lambda p:p["phase_a_factor_bijection"][0].update({"semantic_normal_space_equal":False,"raw_list_byte_equal":True}))
    rejected=0
    for name,key,candidate in attacks:
        s=subjects[key]
        try: verify(candidate,spec,s["raw"],s["b51"],s.get("carrier"),s.get("b52"),carrier_spec,b52_spec,r52,r53,s.get("caps",caps))
        except Exception: rejected+=1; continue
        raise AssertionError(name+" survived")
    return rejected,len(attacks)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--spec",type=Path,required=True); p.add_argument("--carrier-spec",type=Path,required=True); p.add_argument("--b5-2b-spec",type=Path,required=True)
    p.add_argument("--b5-2b-admission",type=Path,required=True); p.add_argument("--b5-3-admission",type=Path,required=True)
    p.add_argument("--input",type=Path,required=True); p.add_argument("--b5-1-artifact",type=Path,required=True); p.add_argument("--carrier",type=Path); p.add_argument("--b5-2b-artifact",type=Path); p.add_argument("--candidate",type=Path,required=True)
    p.add_argument("--discovery-cap",type=int); p.add_argument("--work-cap",type=int); p.add_argument("--certificate-cap",type=int); p.add_argument("--trellis-work-cap",type=int); p.add_argument("--trellis-certificate-cap",type=int)
    a=p.parse_args(); caps={"discovery_cap":a.discovery_cap,"work_cap":a.work_cap,"certificate_cap":a.certificate_cap,"trellis_work_cap":a.trellis_work_cap,"trellis_certificate_cap":a.trellis_certificate_cap}
    out=verify(load(a.candidate),load(a.spec),load(a.input),load(a.b5_1_artifact),load(a.carrier),load(a.b5_2b_artifact),load(a.carrier_spec),load(a.b5_2b_spec),load(a.b5_2b_admission),load(a.b5_3_admission),caps)
    print("JANUS_B5_4_CORRECTED_DISCOVERY_C047_REBOUND_INDEPENDENT_VERIFIER = PASS")
    print("REBOUND_STATUS =",out["rebound_status"]); print("AFFINE_BINDING_STATUS =",out["affine_binding_status"]); print("C047_RESULT =",out["c047_result"])
    print("B5_2A_B5_2B_REVERIFICATION = PASS" if out["subject"]["b5_1_capability_status"]=="CLOSED_COMPLETE_TRACE" else "B5_2A_B5_2B_REVERIFICATION = NOT_APPLICABLE_OPEN")
    print("SEMANTIC_NORMAL_SPACE_REBOUND = PASS" if out["affine_binding_status"]=="BOUND" else "SEMANTIC_NORMAL_SPACE_REBOUND = NOT_BOUND")
    print("HISTORICAL_PHASE_A_VERIFIER_PASS =",str(out["historical_phase_a_verifier_pass"]).upper())
    print("B5_3_NO_LAYOUT_USED_AS_C047_UNSAT_PREMISE = FALSE"); print("AFFINE_INSTANCE_SAT_OR_UNSAT_ADMITTED = FALSE"); print("B5_COMPLETE = FALSE"); print("P_VS_NP = OPEN")

if __name__=="__main__": main()
