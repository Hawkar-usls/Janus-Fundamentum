#!/usr/bin/env python3
"""Stage6B.3 scientific result assembler.

Promotion rules are intentionally asymmetric:
SAT -> requires exact OPB model replay AND independent q-Horn witness replay.
UNSAT -> requires exact raw proof and VeriPB verified UNSAT conclusion.

CakePB is a stronger secondary line but is not required for the primary exact
distance promotion frozen in the preregistration.
"""
from __future__ import annotations
import argparse, collections, hashlib, json
from pathlib import Path

TARGETS=[1,2,3,4,5,6,7,9,10,11,12,13,14]
BOUNDARY={1:24,2:31,3:25,4:28,5:22,6:27,7:22,9:31,10:31,11:31,12:31,13:31,14:31}


def load(p):
    p=Path(p)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def sha(p):
    p=Path(p)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def row_for_b2(b2,index):
    return next(r for r in b2["rows"] if int(r["target_index"])==index)


def classify(index,b2row,base):
    ca=base["canonical"]
    oa=base["opb_audit"]
    sr=base["solver"]
    sat=base["sat"]
    vp=base["veripb"]
    cp=base["cakepb"]
    m=int(b2row["final_B_star_size"])
    k=BOUNDARY[index]

    row={
      "index":index,
      "Stage6B2_m":m,
      "boundary_k":k,
      "raw_cnf_sha256":ca.get("raw_cnf_sha256") if ca else None,
      "canonical_cnf_sha256":ca.get("canonical_cnf_sha256") if ca else None,
      "duplicate_count":ca.get("duplicate_literal_occurrence_count") if ca else None,
      "complementary_pair_count":ca.get("complementary_pair_clause_count") if ca else None,
      "Stage6B2_B_star_sha256":b2row.get("final_B_star_sha256"),
      "Stage6B2_positive_qhorn_certificate_sha256":b2row.get("fresh_qhorn_certificate_sha256"),
      "Stage6B2_full_terminal_object_sha256":b2row.get("full_terminal_object_sha256"),
      "OPB_sha256":oa.get("OPB_sha256") if oa else None,
      "OPB_constraint_count":oa.get("constraint_count") if oa else None,
      "PB_variable_count":oa.get("PB_variable_count") if oa else None,
      "proof_producer_status":sr.get("proof_producer_status") if sr else None,
      "proof_producer_runtime":sr.get("runtime_seconds") if sr else None,
      "model_sha256_if_SAT":sr.get("model_source_sha256") if sr else None,
      "proof_size_if_UNSAT":sr.get("raw_proof_bytes") if sr else None,
      "proof_sha256":sr.get("raw_proof_sha256") if sr else None,
      "PB_MODEL_REPLAY_VERIFIED":sat.get("PB_MODEL_REPLAY_VERIFIED") if sat else False,
      "QHORN_WITNESS_REPLAY_VERIFIED":sat.get("QHORN_WITNESS_REPLAY_VERIFIED") if sat else False,
      "decoded_candidate_B":sat.get("decoded_B") if sat else None,
      "decoded_candidate_B_size":sat.get("decoded_B_size") if sat else None,
      "VeriPB_raw_proof_status":vp.get("VERIPB_PRIMARY_raw_proof_verified") if vp else None,
      "VeriPB_checker_reported_conclusion":vp.get("VERIPB_CHECKER_REPORTED_CONCLUSION") if vp else None,
      "VeriPB_runtime":vp.get("verification_runtime_seconds") if vp else None,
      "VeriPB_receipt_sha256":base.get("veripb_receipt_sha256"),
      "elaboration_status":vp.get("elaboration_succeeded") if vp else None,
      "kernel_proof_sha256":vp.get("kernel_proof_sha256") if vp else None,
      "CakePB_verification_status":cp.get("cakepb_verified") if cp else None,
      "CakePB_infrastructure_error":cp.get("infrastructure_error") if cp else None,
      "exact_distance":None
    }

    if m-1!=k:
        row["final_B3_verdict"]="INFRASTRUCTURE_ERROR"
        row["failure"]="FROZEN_BOUNDARY_DOES_NOT_EQUAL_M_MINUS_1"
        return row

    if ca is None:
        row["final_B3_verdict"]="INFRASTRUCTURE_ERROR"; row["failure"]="MISSING_CANONICAL_AUDIT"; return row
    if ca.get("status")=="CANONICALIZATION_REQUIRES_SEPARATE_PREREG":
        row["final_B3_verdict"]="CANONICALIZATION_REQUIRES_SEPARATE_PREREG"; return row
    if ca.get("status")!="CANONICALIZATION_AUDIT_PASS":
        row["final_B3_verdict"]="INFRASTRUCTURE_ERROR"; row["failure"]="CANONICAL_AUDIT_NOT_PASS"; return row
    if oa is None or oa.get("status")!="OPB_SEMANTIC_AUDIT_PASS":
        row["final_B3_verdict"]="INFRASTRUCTURE_ERROR"; row["failure"]="OPB_AUDIT_NOT_PASS"; return row
    if sr is None:
        row["final_B3_verdict"]="INFRASTRUCTURE_ERROR"; row["failure"]="MISSING_SOLVER_RECEIPT"; return row

    status=sr.get("proof_producer_status")
    if status=="TIMEOUT":
        row["final_B3_verdict"]="UNKNOWN_RESOURCE_LIMIT"; return row
    if status in ("PARSER_ERROR","ERROR","UNKNOWN"):
        row["final_B3_verdict"]="INFRASTRUCTURE_ERROR"
        row["failure"]=f"PROOF_PRODUCER_NON_RESOURCE_FAILURE:{status}"
        return row

    if status=="SAT":
        if sat and sat.get("PB_MODEL_REPLAY_VERIFIED") is True and sat.get("QHORN_WITNESS_REPLAY_VERIFIED") is True:
            row["final_B3_verdict"]="VERIFIED_SMALLER_DELETION_QHORN_WITNESS"
            row["verified_upper_bound"]=sat.get("decoded_B_size")
            row["Stage6B2_B_star_proven_not_minimum_cardinality"]=sat.get("decoded_B_size",m)<m
        else:
            row["final_B3_verdict"]="INFRASTRUCTURE_ERROR"
            row["failure"]="SAT_WITHOUT_DUAL_REPLAY_AUTHORITY"
        return row

    if status=="UNSAT":
        if not sr.get("raw_proof_sha256"):
            row["final_B3_verdict"]="UNVERIFIED_UNSAT_NO_AUTHORITY"; return row
        if vp is None:
            row["final_B3_verdict"]="UNVERIFIED_UNSAT_NO_AUTHORITY"; return row
        if vp.get("verification_timed_out"):
            row["final_B3_verdict"]="UNKNOWN_PROOF_CHECK_RESOURCE_LIMIT"; return row
        if vp.get("VERIPB_PRIMARY_raw_proof_verified")!="YES" or vp.get("VERIPB_CHECKER_REPORTED_CONCLUSION")!="UNSAT":
            row["final_B3_verdict"]="FAIL_UNSAT_CERTIFICATE"; return row

        row["final_B3_verdict"]="EXACT_DELETION_QHORN_DISTANCE_VERIFIED"
        row["exact_distance"]=m
        row["verified_lower_bound"]=m
        row["verified_upper_bound"]=m
        if cp and cp.get("cakepb_verified")=="YES":
            row["PB_UNSAT_authority"]="DUAL_CHECKED_PB_UNSAT"
        elif cp and cp.get("infrastructure_error")=="YES":
            row["PB_UNSAT_authority"]="VERIPB_VERIFIED_UNSAT__CAKEPB_INFRA_FAILURE"
        else:
            row["PB_UNSAT_authority"]="VERIPB_VERIFIED_UNSAT"
        return row

    row["final_B3_verdict"]="INFRASTRUCTURE_ERROR"
    row["failure"]=f"UNRECOGNIZED_PROOF_PRODUCER_STATUS:{status}"
    return row


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("stage6b2_result")
    ap.add_argument("root")
    ap.add_argument("output")
    ap.add_argument("--prereg-commit",required=True)
    ap.add_argument("--implementation-head",required=True)
    ns=ap.parse_args()

    b2=load(ns.stage6b2_result); root=Path(ns.root)
    rows=[]
    for i in TARGETS:
        d=root/f"r50g25x_{i:02d}"
        vp_path=d/"veripb"/"veripb.receipt.json"
        base={
          "canonical":load(d/"canonical.json"),
          "opb_audit":load(d/"opb.audit.json"),
          "solver":load(d/"roundingsat"/"roundingsat.receipt.json"),
          "sat":load(d/"sat_replay.json"),
          "veripb":load(vp_path),
          "veripb_receipt_sha256":sha(vp_path),
          "cakepb":load(d/"cakepb"/"cakepb.receipt.json")
        }
        rows.append(classify(i,row_for_b2(b2,i),base))

    counts=dict(collections.Counter(r["final_B3_verdict"] for r in rows))
    out={
      "schema":"janus.trump.stage6b3.exact_deletion_qhorn_boundary_proof_gate.result.v1",
      "gate":"TRUMP_STAGE6B3_EXACT_DELETION_QHORN_BOUNDARY_PROOF_GATE",
      "prereg_commit":ns.prereg_commit,
      "implementation_head":ns.implementation_head,
      "rows":rows,
      "verdict_counts":counts,
      "claim_ceiling":{
        "NEW_JANUS_CONTROLLER":"BLOCKED",
        "GENERAL_SAT_IN_P":"NOT_PROVED",
        "P_EQ_NP":"NOT_PROVED",
        "P_VS_NP":"OPEN",
        "FINITE_EXACT_DISTANCES_IMPLY_ASYMPTOTIC_RESULT":False
      },
      "stage6C_stage6D_executed":False
    }
    Path(ns.output).parent.mkdir(parents=True,exist_ok=True)
    Path(ns.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"verdict_counts":counts,"rows":[{"index":r["index"],"verdict":r["final_B3_verdict"],"exact_distance":r.get("exact_distance"),"candidate_B_size":r.get("decoded_candidate_B_size")} for r in rows]},sort_keys=True))


if __name__=="__main__":
    main()
