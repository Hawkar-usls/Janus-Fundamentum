#!/usr/bin/env python3
"""Stage6B.4 non-scientific UNSAT proof-pipeline smoke.

Runs the exact frozen RoundingSat -> raw proof -> VeriPB chain on a fixed
trivial UNSAT PB24 fixture. This smoke has zero deletion-qHorn authority.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent


def fsha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run(cmd):
    p=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    return p.returncode,p.stdout,p.stderr


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("roundingsat")
    ap.add_argument("veripb")
    ap.add_argument("fixture")
    ap.add_argument("outdir")
    ap.add_argument("--cakepb")
    ns=ap.parse_args()

    outdir=Path(ns.outdir); outdir.mkdir(parents=True,exist_ok=True)
    fixture=Path(ns.fixture)
    runner=HERE/"trump_stage6b3_roundingsat_runner.py"
    vph=HERE/"trump_stage6b4_veripb_v2_harness.py"
    cph=HERE/"trump_stage6b3_cakepb_secondary_harness.py"

    failures=[]
    rsdir=outdir/"roundingsat"
    rc,so,se=run([sys.executable,str(runner),ns.roundingsat,str(fixture),str(rsdir),"--timeout-seconds","30"])
    (outdir/"runner.wrapper.stdout").write_text(so)
    (outdir/"runner.wrapper.stderr").write_text(se)
    if rc!=0: failures.append(f"ROUNDINGSAT_RUNNER_RC_{rc}")

    rs_receipt_path=rsdir/"roundingsat.receipt.json"
    rs=json.loads(rs_receipt_path.read_text()) if rs_receipt_path.exists() else {}
    if rs.get("proof_producer_status")!="UNSAT": failures.append("ROUNDINGSAT_NOT_UNSAT")
    proof_path=Path(rs.get("raw_proof_path") or "")
    if not proof_path.exists() or proof_path.stat().st_size<=0: failures.append("MISSING_RAW_PROOF")

    vpdir=outdir/"veripb"; kernel=vpdir/"kernel.pbp"
    vp={}
    if not failures:
        rc,so,se=run([sys.executable,str(vph),ns.veripb,str(fixture),str(proof_path),str(kernel),str(vpdir),"--timeout-seconds","60"])
        (outdir/"veripb.wrapper.stdout").write_text(so)
        (outdir/"veripb.wrapper.stderr").write_text(se)
        if rc!=0: failures.append(f"VERIPB_HARNESS_RC_{rc}")
        vp_path=vpdir/"veripb.receipt.json"
        vp=json.loads(vp_path.read_text()) if vp_path.exists() else {}
        if vp.get("VERIPB_PRIMARY_raw_proof_verified")!="YES": failures.append("VERIPB_RAW_PROOF_NOT_VERIFIED")
        if vp.get("VERIPB_CHECKER_REPORTED_CONCLUSION")!="UNSAT": failures.append("VERIPB_NO_UNSAT_CONCLUSION")
        if vp.get("VERIPB_CONCLUSION_SECTION_VALID") is not True: failures.append("VERIPB_CONCLUSION_INVALID")

    cake_status="NOT_REQUESTED"
    cp_receipt=None
    if not failures and ns.cakepb and Path(ns.cakepb).exists() and vp.get("elaboration_succeeded")=="YES" and kernel.exists():
        cpdir=outdir/"cakepb"
        rc,so,se=run([sys.executable,str(cph),ns.cakepb,str(fixture),str(kernel),str(cpdir),"--timeout-seconds","60"])
        (outdir/"cakepb.wrapper.stdout").write_text(so)
        (outdir/"cakepb.wrapper.stderr").write_text(se)
        cp_path=cpdir/"cakepb.receipt.json"
        cp_receipt=json.loads(cp_path.read_text()) if cp_path.exists() else {}
        if cp_receipt.get("cakepb_verified")=="YES": cake_status="CAKEPB_VERIFIED"
        elif cp_receipt.get("infrastructure_error")=="YES": cake_status="CAKEPB_INFRASTRUCTURE_FAILURE"
        else: cake_status="CAKEPB_NOT_VERIFIED"

    receipt={
      "schema":"janus.trump.stage6b4.unsat_proof_pipeline_smoke.v1",
      "authority":"NON_SCIENTIFIC_INFRASTRUCTURE_SMOKE_ONLY",
      "scientific_deletion_qhorn_authority":False,
      "fixture_sha256":fsha(fixture),
      "roundingsat_binary_sha256":fsha(ns.roundingsat),
      "veripb_binary_sha256":fsha(ns.veripb),
      "roundingsat_status":rs.get("proof_producer_status"),
      "roundingsat_receipt_sha256":fsha(rs_receipt_path) if rs_receipt_path.exists() else None,
      "raw_proof_sha256":fsha(proof_path) if proof_path.exists() else None,
      "veripb_receipt_sha256":fsha(vpdir/"veripb.receipt.json") if (vpdir/"veripb.receipt.json").exists() else None,
      "veripb_raw_proof_verified":vp.get("VERIPB_PRIMARY_raw_proof_verified"),
      "veripb_conclusion":vp.get("VERIPB_CHECKER_REPORTED_CONCLUSION"),
      "veripb_conclusion_section_valid":vp.get("VERIPB_CONCLUSION_SECTION_VALID"),
      "kernel_proof_sha256":fsha(kernel) if kernel.exists() else None,
      "cakepb_status":cake_status,
      "status":"UNSAT_PROOF_PIPELINE_SMOKE_PASS" if not failures else "INFRASTRUCTURE_ERROR",
      "failures":failures
    }
    Path(outdir/"smoke.receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps(receipt,sort_keys=True))
    if failures: raise SystemExit(2)


if __name__=="__main__": main()
