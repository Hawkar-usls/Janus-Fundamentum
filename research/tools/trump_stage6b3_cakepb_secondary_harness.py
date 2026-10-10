#!/usr/bin/env python3
"""Stage6B.3 CakePB formally verified secondary checker harness.

A zero exit code is insufficient. Secondary acceptance requires an explicit
VERIFIED UNSAT/UNSATISFIABLE verdict in stdout and no rejection marker.
"""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess, time
from pathlib import Path

PASS=[
  re.compile(r"\bs\s+VERIFIED\s+UNSAT(?:ISFIABLE)?\b",re.I),
  re.compile(r"\bVERIFIED\s+UNSAT(?:ISFIABLE)?\b",re.I)
]
FAIL=[
  re.compile(r"\bREJECT",re.I),
  re.compile(r"\bINVALID\b",re.I),
  re.compile(r"\bVERIFICATION\s+FAILED\b",re.I),
  re.compile(r"\bERROR\b",re.I)
]


def sha(p:Path):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("cakepb")
    ap.add_argument("opb")
    ap.add_argument("kernel")
    ap.add_argument("outdir")
    ap.add_argument("--timeout-seconds",type=int,default=600)
    ns=ap.parse_args()

    outdir=Path(ns.outdir); outdir.mkdir(parents=True,exist_ok=True)
    binary=Path(ns.cakepb); opb=Path(ns.opb); kernel=Path(ns.kernel)
    receipt={
      "schema":"janus.trump.stage6b3.cakepb_secondary_receipt.v1",
      "cakepb_binary_path":str(binary),
      "OPB_sha256":sha(opb),
      "kernel_proof_sha256":sha(kernel),
      "elaboration_succeeded":"YES",
      "cakepb_verified":"NO",
      "infrastructure_error":"NO"
    }

    if not binary.exists():
        receipt.update({"infrastructure_error":"YES","failure":"CAKEPB_BINARY_NOT_FOUND"})
    else:
        receipt["cakepb_executable_sha256"]=sha(binary)
        cmd=[str(binary),str(opb),str(kernel)]
        receipt["cakepb_command"]=cmd
        t0=time.perf_counter()
        try:
            p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                             text=True,timeout=ns.timeout_seconds,check=False)
            timed_out=False; out=p.stdout; err=p.stderr; code=p.returncode
        except subprocess.TimeoutExpired as e:
            timed_out=True; code=None
            out=e.stdout or ""; err=e.stderr or ""
            if isinstance(out,bytes): out=out.decode(errors="replace")
            if isinstance(err,bytes): err=err.decode(errors="replace")
        runtime=time.perf_counter()-t0
        (outdir/"cakepb.stdout").write_text(out,encoding="utf-8")
        (outdir/"cakepb.stderr").write_text(err,encoding="utf-8")
        bad=[r.pattern for r in FAIL if r.search(out+"\n"+err)]
        explicit=any(r.search(out) for r in PASS)
        ok=(not timed_out and code==0 and not bad and explicit)
        receipt.update({
          "cakepb_exit_code":code,
          "cakepb_runtime_seconds":runtime,
          "cakepb_timed_out":timed_out,
          "cakepb_failure_markers":bad,
          "cakepb_reported_conclusion":"UNSAT" if explicit else None,
          "cakepb_verified":"YES" if ok else "NO",
          "infrastructure_error":"YES" if timed_out else "NO"
        })

    rp=outdir/"cakepb.receipt.json"
    rp.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "cakepb_verified":receipt["cakepb_verified"],
      "infrastructure_error":receipt["infrastructure_error"],
      "reported_conclusion":receipt.get("cakepb_reported_conclusion")
    },sort_keys=True))


if __name__=="__main__":
    main()
