#!/usr/bin/env python3
"""Stage6B.3 frozen RoundingSat proof-producer runner.

This program records external proof-producer telemetry and artifacts only.
It grants no SAT/UNSAT scientific authority.
"""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess, time
from pathlib import Path

UNSAT_RE=re.compile(r"\bUNSAT(?:ISFIABLE)?\b",re.I)
SAT_RE=re.compile(r"\bSAT(?:ISFIABLE)?\b",re.I)


def sha(p:Path):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def classify(text):
    # Check UNSAT first because "UNSATISFIABLE" contains SATISFIABLE as substring.
    if UNSAT_RE.search(text):
        return "UNSAT"
    if SAT_RE.search(text):
        return "SAT"
    return "UNKNOWN"


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("roundingsat")
    ap.add_argument("opb")
    ap.add_argument("outdir")
    ap.add_argument("--timeout-seconds",type=int,default=300)
    ns=ap.parse_args()

    binary=Path(ns.roundingsat); opb=Path(ns.opb); outdir=Path(ns.outdir)
    outdir.mkdir(parents=True,exist_ok=True)
    proof_base=outdir/"roundingsat_raw"
    stdoutp=outdir/"roundingsat.stdout"
    stderrp=outdir/"roundingsat.stderr"

    cmd=[str(binary),"--print-sol=1","--lp=0",f"--proof-log={proof_base}",str(opb)]
    t0=time.perf_counter()
    try:
        p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                         text=True,timeout=ns.timeout_seconds,check=False)
        timed_out=False; code=p.returncode; out=p.stdout; err=p.stderr
    except subprocess.TimeoutExpired as e:
        timed_out=True; code=None
        out=e.stdout or ""; err=e.stderr or ""
        if isinstance(out,bytes): out=out.decode(errors="replace")
        if isinstance(err,bytes): err=err.decode(errors="replace")
    runtime=time.perf_counter()-t0
    stdoutp.write_text(out,encoding="utf-8")
    stderrp.write_text(err,encoding="utf-8")
    status="TIMEOUT" if timed_out else classify(out+"\n"+err)

    proof_candidates=[
      proof_base,
      Path(str(proof_base)+".proof"),
      Path(str(proof_base)+".pbp")
    ]
    proof=next((p for p in proof_candidates if p.exists() and p.stat().st_size>0),None)

    receipt={
      "schema":"janus.trump.stage6b3.roundingsat_execution_receipt.v1",
      "role":"EXTERNAL_PROOF_PRODUCER_ONLY__NO_SCIENTIFIC_AUTHORITY",
      "binary_sha256":sha(binary),
      "OPB_sha256":sha(opb),
      "execution_command":cmd,
      "runtime_limit_seconds":ns.timeout_seconds,
      "runtime_seconds":runtime,
      "exit_code":code,
      "timed_out":timed_out,
      "proof_producer_status":status,
      "stdout_sha256":sha(stdoutp),
      "stderr_sha256":sha(stderrp),
      "stdout_bytes":stdoutp.stat().st_size,
      "stderr_bytes":stderrp.stat().st_size,
      "raw_proof_path":str(proof) if proof else None,
      "raw_proof_sha256":sha(proof) if proof else None,
      "raw_proof_bytes":proof.stat().st_size if proof else None,
      "model_source_path":str(stdoutp) if status=="SAT" else None,
      "model_source_sha256":sha(stdoutp) if status=="SAT" else None,
      "bare_status_is_authority":False
    }
    rp=outdir/"roundingsat.receipt.json"
    rp.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "status":status,
      "runtime_seconds":runtime,
      "exit_code":code,
      "proof_sha256":receipt["raw_proof_sha256"],
      "proof_bytes":receipt["raw_proof_bytes"]
    },sort_keys=True))


if __name__=="__main__":
    main()
