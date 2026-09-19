#!/usr/bin/env python3
"""Stage6B.4 adapter from frozen VeriPB/CakePB receipts to bracket authority."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path


def fsha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("opb"); ap.add_argument("proof"); ap.add_argument("veripb_receipt")
    ap.add_argument("output"); ap.add_argument("--cakepb-receipt")
    ns=ap.parse_args()

    vp=json.loads(Path(ns.veripb_receipt).read_text())
    cp=json.loads(Path(ns.cakepb_receipt).read_text()) if ns.cakepb_receipt and Path(ns.cakepb_receipt).exists() else None
    opb_sha=fsha(ns.opb); proof_sha=fsha(ns.proof); vp_sha=fsha(ns.veripb_receipt)
    failures=[]
    if vp.get("OPB_sha256")!=opb_sha: failures.append("VERIPB_OPB_HASH_MISMATCH")
    if vp.get("raw_proof_sha256")!=proof_sha: failures.append("VERIPB_PROOF_HASH_MISMATCH")
    if vp.get("VERIPB_PROCESS_COMPLETED_SUCCESSFULLY") is not True: failures.append("VERIPB_PROCESS_NOT_SUCCESS")
    if vp.get("VERIPB_PROOF_VERIFICATION_ERRORS")!=0: failures.append("VERIPB_VERIFICATION_ERRORS")
    if vp.get("VERIPB_CHECKER_REPORTED_CONCLUSION")!="UNSAT": failures.append("VERIPB_NO_EXPLICIT_UNSAT")
    if vp.get("VERIPB_CONCLUSION_SECTION_VALID") is not True: failures.append("VERIPB_CONCLUSION_SECTION_INVALID")
    if vp.get("VERIPB_PRIMARY_raw_proof_verified")!="YES": failures.append("VERIPB_RAW_PROOF_NOT_VERIFIED")

    cake_status="NOT_RUN"
    cake_receipt_sha=None
    if cp is not None:
        cake_receipt_sha=fsha(ns.cakepb_receipt)
        if cp.get("cakepb_verified")=="YES": cake_status="CAKEPB_VERIFIED"
        elif cp.get("infrastructure_error")=="YES": cake_status="CAKEPB_INFRASTRUCTURE_FAILURE"
        else: cake_status="CAKEPB_NOT_VERIFIED"

    out={
      "schema":"janus.trump.stage6b4.veripb_unsat_authority.v1",
      "status":"VERIPB_VERIFIED_BOUNDARY_UNSAT" if not failures else "NO_LOWER_BOUND_AUTHORITY",
      "OPB_sha256":opb_sha,
      "raw_proof_sha256":proof_sha,
      "veripb_source_receipt_sha256":vp_sha,
      "receipt_sha256":vp_sha,
      "VERIPB_PROCESS_COMPLETED_SUCCESSFULLY":vp.get("VERIPB_PROCESS_COMPLETED_SUCCESSFULLY"),
      "VERIPB_PROOF_VERIFICATION_ERRORS":vp.get("VERIPB_PROOF_VERIFICATION_ERRORS"),
      "VERIPB_CHECKER_REPORTED_CONCLUSION":vp.get("VERIPB_CHECKER_REPORTED_CONCLUSION"),
      "VERIPB_CONCLUSION_SECTION_VALID":vp.get("VERIPB_CONCLUSION_SECTION_VALID"),
      "VERIPB_PRIMARY_raw_proof_verified":vp.get("VERIPB_PRIMARY_raw_proof_verified"),
      "verification_runtime_seconds":vp.get("verification_runtime_seconds"),
      "kernel_proof_sha256":vp.get("kernel_proof_sha256"),
      "CakePB_status":cake_status,
      "CakePB_receipt_sha256":cake_receipt_sha,
      "failures":failures
    }
    Path(ns.output).parent.mkdir(parents=True,exist_ok=True)
    Path(ns.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":out["status"],"OPB_sha256":opb_sha,"raw_proof_sha256":proof_sha,
                      "VeriPB_conclusion":out["VERIPB_CHECKER_REPORTED_CONCLUSION"],
                      "CakePB_status":cake_status,"failures":failures},sort_keys=True))
    if failures: raise SystemExit(2)


if __name__=="__main__": main()
