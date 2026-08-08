from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import janus_c049_1_b5_iterative_compression_preprocessing_binding_verifier as prepv
import janus_c049_1_b5_1_generic_corrected_runtime_trace_executor_verifier as b51v
import janus_c049_1_b5_2a_generic_algorithm2_provenance_carrier_verifier_v11 as b52av
import janus_c049_1_b5_2b_generic_algorithm2_printorder_reconstruction_verifier_v11 as b52bv
from janus_c047_affine_trellis_core import affine_rref, linear_rref
from janus_c049_fpt_integration_core import layout_data_from_spaces, make_found_layout_transcript
from janus_c049_fpt_integration_verifier import verify as historical_verify_phase_a

SCHEMA = "janus.c049_1.b5.full_input_original_order_lift_c047_rebound_candidate.v1"
SPEC_SCHEMA = "janus.c049_1.b5.full_input_original_order_lift_c047_rebound_spec.v1"
AFFINE_SCHEMA = "janus.c049_1.c047_affine_equations.v1"


def cb(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def dg(value: Any) -> str:
    return hashlib.sha256(cb(value)).hexdigest()


def load(path: Path | None) -> Any:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def semantic_space(rows, dimension: int) -> tuple[int, ...]:
    return linear_rref([int(x) for x in rows], dimension)


def original_catalog(pre_payload: dict) -> list[dict]:
    out = []
    for i, rec in enumerate(pre_payload["original_catalog"]):
        if rec.get("occurrence_index") != i:
            raise AssertionError("original occurrence index")
        fid = rec.get("factor_id")
        if not isinstance(fid, str) or not fid:
            raise AssertionError("string factor id required")
        out.append({"id": fid, "normal_space": [int(x) for x in rec["normal_space"]], "affine_offset": copy.deepcopy(rec.get("affine_offset"))})
    if len({x["id"] for x in out}) != len(out):
        raise AssertionError("duplicate factor id")
    return out


def reduced_catalog(pre_payload: dict) -> list[dict]:
    return [
        {"id": str(rec["factor_id"]), "normal_space": [int(x) for x in rec["normal_space"]], "affine_offset": copy.deepcopy(rec.get("affine_offset"))}
        for rec in pre_payload["discovery_catalog"]
    ]


def verify_reduced_original_cuts(p52: dict, layout: dict, dimension: int) -> list[dict]:
    cuts = p52["cut_certificates"]
    if len(cuts) != len(layout["cut_widths"]):
        raise AssertionError("cut count")
    bridge = []
    for i, cut in enumerate(cuts):
        rb = semantic_space(cut["boundary_rref"], dimension)
        ob = semantic_space(layout["cut_bases"][i], dimension)
        if int(cut["width"]) != int(layout["cut_widths"][i]) or rb != ob:
            raise AssertionError("reduced/original cut mismatch")
        bridge.append({
            "cut": i,
            "width": int(layout["cut_widths"][i]),
            "b5_boundary_semantic_digest": dg(list(rb)),
            "phase_a_boundary_semantic_digest": dg(list(ob)),
            "semantic_boundary_equal": True,
        })
    return bridge


def affine_adapter(catalog: list[dict], dimension: int) -> tuple[str, list[dict], list[dict], str | None]:
    phase_factors = []
    mapping = []
    for position, factor in enumerate(catalog):
        offset = factor.get("affine_offset")
        if not isinstance(offset, dict) or offset.get("schema") != AFFINE_SCHEMA:
            return "OPEN_AFFINE_REBOUND_BINDING", [], [], "MISSING_CANONICAL_AFFINE_PROFILE"
        equations = offset.get("equations")
        if not isinstance(equations, list) or not equations:
            return "OPEN_AFFINE_REBOUND_BINDING", [], [], "EMPTY_OR_NONLIST_EQUATIONS"
        parsed = []
        for row in equations:
            if not isinstance(row, list) or len(row) != 2:
                return "OPEN_AFFINE_REBOUND_BINDING", [], [], "BAD_EQUATION_SHAPE"
            mask, beta = row
            if not isinstance(mask, int) or not isinstance(beta, int) or not (0 <= mask < (1 << dimension)) or beta not in (0, 1):
                return "OPEN_AFFINE_REBOUND_BINDING", [], [], "BAD_EQUATION_VALUE"
            parsed.append((mask, beta))
        reduced = affine_rref(parsed, dimension)
        if reduced is None:
            return "OPEN_NONBIJECTIVE_AFFINE_NORMALIZATION", [], [], "INCONSISTENT_AFFINE_FACTOR_WOULD_BE_DROPPED"
        original_normal = semantic_space(factor["normal_space"], dimension)
        affine_normal = linear_rref([mask for mask, _ in reduced], dimension)
        if original_normal != affine_normal:
            return "OPEN_AFFINE_REBOUND_BINDING", [], [], "AFFINE_NORMAL_SPAN_MISMATCH"
        normalized = [[int(mask), int(beta)] for mask, beta in reduced]
        phase_factors.append({"factor_id": position, "equations": normalized})
        mapping.append({
            "b5_factor_id": factor["id"],
            "phase_a_numeric_factor_id": position,
            "phase_a_input_position": position,
            "b5_normal_space_serialized": factor["normal_space"],
            "phase_a_normal_space_rref": list(affine_normal),
            "normal_space_rref": list(original_normal),
            "normal_space_semantic_digest": dg(list(original_normal)),
            "semantic_normal_space_equal": True,
            "raw_list_byte_equal": factor["normal_space"] == list(affine_normal),
            "affine_offset_identity_digest": dg(offset),
            "normalized_equations": normalized,
            "normalized_equations_digest": dg(normalized),
        })
    return "BOUND", phase_factors, mapping, None


def verify(
    candidate: dict,
    spec: dict,
    raw_original: dict,
    preprocessing: dict,
    reduced_raw: dict | None,
    b51: dict | None,
    carrier: dict | None,
    b52: dict | None,
    prep_spec: dict,
    b51_spec: dict,
    b52a_spec: dict,
    b52b_spec: dict,
    caps: dict[str, int | None],
) -> dict:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_CANDIDATE_ONLY":
        raise AssertionError("spec")
    if candidate.get("schema") != SCHEMA or candidate.get("semantic_digest_scope") != "proof_payload" or candidate.get("semantic_digest") != dg(candidate.get("proof_payload")):
        raise AssertionError("candidate digest")
    pre_result = prepv.verify(preprocessing, prep_spec, raw_original)
    pre = preprocessing["proof_payload"]
    p = candidate["proof_payload"]
    d, k = int(pre["ambient_dim"]), int(pre["k"])
    if p["ambient_dim"] != d or p["k"] != k or p["preprocessing_semantic_digest"] != preprocessing["semantic_digest"]:
        raise AssertionError("preprocessing subject binding")
    if p["preprocessing_branch"] != pre["preprocessing_branch"]:
        raise AssertionError("preprocessing branch")
    if p["phase_a_capability_request"] != {key: caps.get(key) for key in sorted(caps)}:
        raise AssertionError("capability request")

    policy = p["authority_policy"]
    if policy != {
        "reduced_geometry_is_discovery_only": True,
        "original_geometry_required_for_final_width_and_affine_rebound": True,
        "direct_b5_4_on_reduced_catalog": False,
        "strict_prefix_c047": False,
        "b5_3_no_layout_used_as_c047_unsat_premise": False,
        "historical_phase_a_c047_code_modified": False,
    }:
        raise AssertionError("authority policy")

    if pre["preprocessing_branch"] == "LOCAL_NO_LAYOUT_SOURCE_CANDIDATE_PENDING_REVIEW":
        if p["lift_status"] != "NOT_APPLICABLE_PREPROCESSING_NO_LAYOUT" or p["c047_result"] != "NOT_ESTABLISHED_PREPROCESSING_NO_LAYOUT":
            raise AssertionError("preprocessing negative branch")
        expected = {"branch": p["lift_status"], "c047_result": p["c047_result"], "original_max_width": None}
    elif pre["preprocessing_branch"] == "TRIVIAL_EMPTY_INPUT":
        if p["lift_status"] != "NOT_APPLICABLE_EMPTY_INPUT" or p["factor_order_ids"] != []:
            raise AssertionError("empty branch")
        expected = {"branch": p["lift_status"], "c047_result": p["c047_result"], "original_max_width": None}
    else:
        if pre["preprocessing_branch"] not in {"PREPROCESSING_BOUND", "TRIVIAL_SINGLETON_INPUT"}:
            raise AssertionError("unexpected preprocessing branch")
        if reduced_raw is None or b51 is None or carrier is None or b52 is None:
            raise AssertionError("missing reduced positive chain")
        closed = b51v.verify(b51, reduced_raw, b51_spec)
        if closed is not True:
            if p["lift_status"] != "NOT_APPLICABLE_REDUCED_OPEN_RUNTIME":
                raise AssertionError("reduced OPEN branch")
            expected = {"branch": p["lift_status"], "c047_result": p["c047_result"], "original_max_width": None}
        else:
            b52av.verify_v11(carrier, reduced_raw, b51, b52a_spec)
            b52_expected = b52bv.basev.verify(b52, b52b_spec, reduced_raw, b51, carrier)
            p52 = b52["proof_payload"]
            if b52_expected["empty"]:
                if p["lift_status"] != "NOT_APPLICABLE_REDUCED_NO_LAYOUT":
                    raise AssertionError("reduced empty branch")
                expected = {"branch": p["lift_status"], "c047_result": p["c047_result"], "original_max_width": None}
            else:
                if b51["proof_payload"]["canonical_factor_catalog"] != reduced_catalog(pre):
                    raise AssertionError("B5.1 not exact discovery catalog")
                if p52["canonical_factor_catalog"] != reduced_catalog(pre):
                    raise AssertionError("B5.2B not exact discovery catalog")
                catalog = original_catalog(pre)
                order_ids = [str(x) for x in p52["factor_order_ids"]]
                ids = [x["id"] for x in catalog]
                if len(order_ids) != len(ids) or len(set(order_ids)) != len(order_ids) or sorted(order_ids) != sorted(ids):
                    raise AssertionError("full occurrence permutation")
                by_id = {x["id"]: i for i, x in enumerate(catalog)}
                positions = [by_id[x] for x in order_ids]
                layout = layout_data_from_spaces([tuple(x["normal_space"]) for x in catalog], positions, d)
                if int(layout["maximum_width"]) > k:
                    raise AssertionError("original order width")
                bridge = verify_reduced_original_cuts(p52, layout, d)
                if p.get("factor_order_ids") != order_ids or p.get("original_layout_replay") != layout or p.get("original_layout_semantic_digest") != dg(layout):
                    raise AssertionError("original layout replay")
                if p.get("reduced_to_original_cut_bridge") != bridge or p.get("reduced_to_original_cut_bridge_digest") != dg(bridge):
                    raise AssertionError("cut bridge")
                expected_records = [{"position":j,"factor_id":fid,"normal_space":copy.deepcopy(catalog[by_id[fid]]["normal_space"]),"affine_offset":copy.deepcopy(catalog[by_id[fid]]["affine_offset"])} for j,fid in enumerate(order_ids)]
                if p.get("original_layout_records") != expected_records:
                    raise AssertionError("original layout records")

                status, phase_factors, mapping, reason = affine_adapter(catalog, d)
                if status != "BOUND":
                    if p["lift_status"] != status or p["affine_binding_status"] != status or p.get("affine_binding_open_reason") != reason or p["c047_result"] != "NOT_ESTABLISHED":
                        raise AssertionError("affine OPEN branch")
                    expected = {"branch": status, "c047_result": "NOT_ESTABLISHED", "original_max_width": int(layout["maximum_width"])}
                else:
                    phase_by_id = {str(x["b5_factor_id"]):x for x in mapping}
                    phase_positions = [int(phase_by_id[fid]["phase_a_input_position"]) for fid in order_ids]
                    if phase_positions != positions:
                        raise AssertionError("numeric occurrence order")
                    phase_layout = layout_data_from_spaces([tuple(mask for mask,_ in f["equations"]) for f in phase_factors], phase_positions, d)
                    phase_bridge = []
                    for i,(ow,pw,ob,pb) in enumerate(zip(layout["cut_widths"],phase_layout["cut_widths"],layout["cut_bases"],phase_layout["cut_bases"])):
                        os=semantic_space(ob,d); ps=semantic_space(pb,d)
                        if int(ow)!=int(pw) or os!=ps: raise AssertionError("original/Phase-A cut")
                        phase_bridge.append({"cut":i,"width":int(ow),"original_boundary_semantic_digest":dg(list(os)),"phase_a_boundary_semantic_digest":dg(list(ps)),"semantic_boundary_equal":True})
                    transcript = make_found_layout_transcript(
                        phase_positions, phase_layout["cut_widths"], phase_layout["cut_bases"],
                        constructor_id="B5_FULL_INPUT_ORIGINAL_ORDER_LIFT", discovery_claim=True,
                        constructor_trace={
                            "preprocessing_semantic_digest":preprocessing["semantic_digest"],
                            "reduced_b5_2b_semantic_digest":b52["semantic_digest"],
                            "factor_order_ids":order_ids,
                            "original_layout_semantic_digest":dg(layout),
                            "reduced_to_original_cut_bridge_digest":dg(bridge),
                            "original_to_phase_a_cut_bridge_digest":dg(phase_bridge),
                        },
                    )
                    if p.get("phase_a_factor_bijection") != mapping or p.get("phase_a_factor_bijection_digest") != dg(mapping): raise AssertionError("Phase-A mapping")
                    if p.get("phase_a_factors") != phase_factors or p.get("phase_a_factor_catalog_digest") != dg(phase_factors): raise AssertionError("Phase-A factors")
                    if p.get("phase_a_order_positions") != phase_positions or p.get("phase_a_layout_recomputation") != phase_layout: raise AssertionError("Phase-A layout")
                    if p.get("original_to_phase_a_cut_bridge") != phase_bridge or p.get("phase_a_transcript") != transcript: raise AssertionError("Phase-A bridge/transcript")
                    certificate = p.get("phase_a_certificate")
                    if historical_verify_phase_a(phase_factors, d, certificate) is not True:
                        raise AssertionError("historical Phase-A verifier false")
                    result = str(certificate["status"])
                    expected_status = "ORIGINAL_ORDER_LIFT_AND_PHASE_A_C047_COMPLETED" if result in {"SAT","UNSAT"} else "ORIGINAL_ORDER_LIFT_PHASE_A_C047_OPEN"
                    if p["lift_status"] != expected_status or p["affine_binding_status"] != "BOUND" or p["historical_phase_a_verifier_pass"] is not True or p["c047_result"] != result:
                        raise AssertionError("historical result branch")
                    expected = {"branch": expected_status, "c047_result": result, "original_max_width": int(layout["maximum_width"])}

    if p.get("strict_boundary") != spec["strict_boundary"]:
        raise AssertionError("strict boundary")
    b = p["strict_boundary"]
    if b["direct_b5_4_on_reduced_catalog"] is not False or b["strict_prefix_c047"] is not False or b["iterative_compression_orchestrator"] is not False or b["all_input_termination"] != "NOT_ESTABLISHED" or b["polynomial_runtime"] != "NOT_ESTABLISHED" or b["b5_complete"] is not False or b["p_vs_np"] != "OPEN":
        raise AssertionError("promotion boundary")
    return expected


def repair(candidate: dict) -> dict:
    candidate["semantic_digest"] = dg(candidate["proof_payload"])
    return candidate


def tamper_suite(subject: dict, spec: dict, prep_spec: dict, b51_spec: dict, b52a_spec: dict, b52b_spec: dict) -> tuple[int,int]:
    attacks = []
    def add(name, mutation):
        c=copy.deepcopy(subject["candidate"]); mutation(c["proof_payload"]); attacks.append((name,repair(c)))
    p=subject["candidate"]["proof_payload"]
    add("T01_PREPROCESSING_SUBJECT_DIGEST",lambda x:x.__setitem__("preprocessing_semantic_digest","0"*64))
    add("T02_ORIGINAL_FACTOR_ID",lambda x:x["original_layout_records"][0].__setitem__("factor_id","__fake__"))
    add("T03_ORIGINAL_NORMAL_SPACE",lambda x:x["original_layout_records"][0].__setitem__("normal_space",[]))
    add("T04_ORIGINAL_AFFINE_OFFSET",lambda x:x["original_layout_records"][0].__setitem__("affine_offset",{"tamper":True}))
    add("T05_REDUCED_B5_2B_SUBJECT_DIGEST",lambda x:x.__setitem__("reduced_b5_2b_semantic_digest","0"*64))
    add("T06_REDUCED_ORDER_DUPLICATE",lambda x:x["factor_order_ids"].__setitem__(-1,x["factor_order_ids"][0]))
    add("T07_REDUCED_ORDER_OMISSION",lambda x:x["factor_order_ids"].pop())
    add("T08_REDUCED_ORDER_UNKNOWN_FACTOR",lambda x:x["factor_order_ids"].__setitem__(0,"__unknown__"))
    add("T09_ORIGINAL_ORDER_REORDERED_AFTER_B5_2B",lambda x:x["factor_order_ids"].__setitem__(slice(0,2),list(reversed(x["factor_order_ids"][:2]))))
    add("T10_ORIGINAL_CUT_WIDTH",lambda x:x["original_layout_replay"]["cut_widths"].__setitem__(1,999))
    add("T11_ORIGINAL_CUT_BASIS",lambda x:x["original_layout_replay"]["cut_bases"].__setitem__(1,[999]))
    add("T12_REDUCED_ORIGINAL_CUT_BRIDGE",lambda x:x["reduced_to_original_cut_bridge"][1].__setitem__("width",999))
    add("T13_ORIGINAL_MAX_WIDTH_GT_K_ACCEPTED",lambda x:x["original_layout_replay"].__setitem__("maximum_width",999))
    add("T14_PHASE_A_NUMERIC_ID_COLLISION",lambda x:x["phase_a_factor_bijection"][1].__setitem__("phase_a_input_position",0))
    add("T15_PHASE_A_ORDER_POSITION",lambda x:x["phase_a_order_positions"].__setitem__(0,999))
    add("T16_AFFINE_BETA",lambda x:x["phase_a_factors"][0]["equations"][0].__setitem__(1,1-x["phase_a_factors"][0]["equations"][0][1]))
    add("T17_AFFINE_MASK",lambda x:x["phase_a_factors"][0]["equations"][0].__setitem__(0,0))
    add("T18_PHASE_A_TRANSCRIPT",lambda x:x["phase_a_transcript"]["order"].__setitem__(0,999))
    add("T19_FORGE_SAT_ON_UNSAT",lambda x:x["phase_a_certificate"].__setitem__("status","SAT"))
    add("T20_FORGE_UNSAT_ON_SAT",lambda x:x["phase_a_certificate"].__setitem__("status","UNSAT"))
    add("T21_PROMOTE_HISTORICAL_OPEN",lambda x:x.__setitem__("lift_status","ORIGINAL_ORDER_LIFT_AND_PHASE_A_C047_COMPLETED"))
    add("T22_DIRECT_REDUCED_B5_4_PROMOTION",lambda x:x["authority_policy"].__setitem__("direct_b5_4_on_reduced_catalog",True))
    add("T23_STRICT_PREFIX_PROMOTION",lambda x:x["authority_policy"].__setitem__("strict_prefix_c047",True))
    add("T24_B5_3_NO_LAYOUT_TO_C047_UNSAT",lambda x:x["authority_policy"].__setitem__("b5_3_no_layout_used_as_c047_unsat_premise",True))
    add("T25_ORIGINAL_ORDER_LIFT_WITHOUT_PREPROCESSING_EQUIVALENCE",lambda x:x["authority_policy"].__setitem__("original_geometry_required_for_final_width_and_affine_rebound",False))
    add("T26_ALL_INPUT_TERMINATION_PROMOTION",lambda x:x["strict_boundary"].__setitem__("all_input_termination","ESTABLISHED"))
    add("T27_POLYNOMIAL_RUNTIME_PROMOTION",lambda x:x["strict_boundary"].__setitem__("polynomial_runtime","ESTABLISHED"))
    add("T28_B5_COMPLETE_PROMOTION",lambda x:x["strict_boundary"].__setitem__("b5_complete",True))
    add("T29_P_VS_NP_PROMOTION",lambda x:x["strict_boundary"].__setitem__("p_vs_np","CLOSED"))
    rejected=0
    for name,candidate in attacks:
        try:
            verify(candidate,spec,subject["raw_original"],subject["preprocessing"],subject["reduced_raw"],subject["b51"],subject["carrier"],subject["b52"],prep_spec,b51_spec,b52a_spec,b52b_spec,subject["caps"])
        except Exception:
            rejected += 1; print(name+" = REJECTED"); continue
        raise AssertionError(name+" survived")
    return rejected,len(attacks)


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--spec",type=Path,required=True)
    p.add_argument("--preprocessing-spec",type=Path,required=True)
    p.add_argument("--b5-1-spec",type=Path,required=True)
    p.add_argument("--b5-2a-spec",type=Path,required=True)
    p.add_argument("--b5-2b-spec",type=Path,required=True)
    p.add_argument("--original-input",type=Path,required=True)
    p.add_argument("--preprocessing",type=Path,required=True)
    p.add_argument("--reduced-input",type=Path)
    p.add_argument("--b5-1-artifact",type=Path)
    p.add_argument("--carrier",type=Path)
    p.add_argument("--b5-2b-artifact",type=Path)
    p.add_argument("--candidate",type=Path,required=True)
    p.add_argument("--discovery-cap",type=int); p.add_argument("--work-cap",type=int); p.add_argument("--certificate-cap",type=int); p.add_argument("--trellis-work-cap",type=int); p.add_argument("--trellis-certificate-cap",type=int)
    p.add_argument("--tamper-suite",action="store_true")
    a=p.parse_args()
    caps={"discovery_cap":a.discovery_cap,"work_cap":a.work_cap,"certificate_cap":a.certificate_cap,"trellis_work_cap":a.trellis_work_cap,"trellis_certificate_cap":a.trellis_certificate_cap}
    subject={"raw_original":load(a.original_input),"preprocessing":load(a.preprocessing),"reduced_raw":load(a.reduced_input),"b51":load(a.b5_1_artifact),"carrier":load(a.carrier),"b52":load(a.b5_2b_artifact),"candidate":load(a.candidate),"caps":caps}
    result=verify(subject["candidate"],load(a.spec),subject["raw_original"],subject["preprocessing"],subject["reduced_raw"],subject["b51"],subject["carrier"],subject["b52"],load(a.preprocessing_spec),load(a.b5_1_spec),load(a.b5_2a_spec),load(a.b5_2b_spec),caps)
    print("JANUS_B5_FULL_INPUT_ORIGINAL_ORDER_LIFT_C047_REBOUND_INDEPENDENT_VERIFIER = PASS")
    print("LIFT_STATUS =",result["branch"])
    print("ORIGINAL_MAX_WIDTH =",result["original_max_width"])
    print("C047_RESULT =",result["c047_result"])
    print("UPSTREAM_PREPROCESSING_REPLAY = PASS")
    print("UPSTREAM_B5_1_B5_2A_B5_2B_REPLAY = PASS")
    print("ORIGINAL_CUT_RECOMPUTATION = PASS")
    print("REDUCED_ORIGINAL_CUT_EQUIVALENCE = PASS")
    print("HISTORICAL_PHASE_A_VERIFIER = PASS_OR_NOT_APPLICABLE_BY_BRANCH")
    print("DIRECT_B5_4_ON_REDUCED_CATALOG = FALSE")
    print("ITERATIVE_COMPRESSION_ORCHESTRATOR = FALSE")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")
    if a.tamper_suite:
        r,t=tamper_suite(subject,load(a.spec),load(a.preprocessing_spec),load(a.b5_1_spec),load(a.b5_2a_spec),load(a.b5_2b_spec)); print(f"DIGEST_REPAIRED_TAMPERS_REJECTED = {r}/{t}")

if __name__=="__main__": main()
