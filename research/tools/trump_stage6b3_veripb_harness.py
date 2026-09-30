#!/usr/bin/env python3
"""Stage6B.3 VeriPB primary verification + elaboration harness.

This harness is deliberately conservative:
* raw proof must contain a valid-looking "conclusion UNSAT" section;
* VeriPB process must exit successfully;
* stdout/stderr must not contain verification-failure markers;
* checker output must explicitly report verified UNSAT/UNSATISFIABLE;
* elaboration is a separate invocation producing a persisted kernel proof.

Exit code alone is never scientific authority.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, time
from pathlib import Path


FAIL_PATTERNS=[
    re.compile(r"verification\s+failed",re.I),
    re.compile(r"proof\s+verification\s+error",re.I),
    re.compile(r"\berror\b",re.I),
    re.compile(r"invalid\s+proof",re.I)
]
VERIFIED_UNSAT_PATTERNS=[
    re.compile(r"\bs\s+VERIFIED\s+UNSAT(?:ISFIABLE)?\b",re.I),
    re.compile(r"\bVERIFIED\s+UNSAT(?:ISFIABLE)?\b",re.I),
    re.compile(r"\bUNSAT(?:ISFIABLE)?\s+VERIFIED\b",re.I)
]
RAW_CONCLUSION_RE=re.compile(r"^\s*conclusion\s+UNSAT(?:\s*:\s*[^;]+)?\s*;\s*$",re.I|re.M)


def sha(path:Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(cmd,timeout,stdout_path,stderr_path):
    t0=time.perf_counter()
    try:
        p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                         text=True,timeout=timeout,check=False)
        timed_out=False
    except subprocess.TimeoutExpired as e:
        p=None; timed_out=True
        out=(e.stdout or "")
        err=(e.stderr or "")
        if isinstance(out,bytes): out=out.decode(errors="replace")
        if isinstance(err,bytes): err=err.decode(errors="replace")
    runtime=time.perf_counter()-t0
    if p is not None:
        out=p.stdout; err=p.stderr; code=p.returncode
    else:
        code=None
    stdout_path.write_text(out,encoding="utf-8")
    stderr_path.write_text(err,encoding="utf-8")
    return code,runtime,timed_out,out,err


def explicit_unsat(text):
    return any(p.search(text) for p in VERIFIED_UNSAT_PATTERNS)


def fail_markers(text):
    return [p.pattern for p in FAIL_PATTERNS if p.search(text)]


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("veripb")
    ap.add_argument("opb")
    ap.add_argument("proof")
    ap.add_argument("kernel")
    ap.add_argument("outdir")
    ap.add_argument("--timeout-seconds",type=int,default=600)
    ns=ap.parse_args()

    vp=Path(ns.veripb); opb=Path(ns.opb); proof=Path(ns.proof)
    kernel=Path(ns.kernel); outdir=Path(ns.outdir)
    outdir.mkdir(parents=True,exist_ok=True); kernel.parent.mkdir(parents=True,exist_ok=True)

    raw_text=proof.read_text(encoding="utf-8",errors="replace")
    raw_conclusion=bool(RAW_CONCLUSION_RE.search(raw_text))

    verify_stdout=outdir/"veripb.verify.stdout"
    verify_stderr=outdir/"veripb.verify.stderr"
    verify_cmd=[str(vp),str(opb),str(proof)]
    vc,vt,vto,vout,verr=run(verify_cmd,ns.timeout_seconds,verify_stdout,verify_stderr)
    combined=vout+"\n"+verr
    vfail=fail_markers(combined)
    reported_unsat=explicit_unsat(combined)

    primary_ok=(raw_conclusion and not vto and vc==0 and not vfail and reported_unsat)

    # Elaboration is attempted only after primary acceptance.
    ec=et=None; eto=False; eout=eerr=""; efail=[]; kernel_ok=False; used_cmd=None
    if primary_ok:
        elab_stdout=outdir/"veripb.elaborate.stdout"
        elab_stderr=outdir/"veripb.elaborate.stderr"
        # Pinned CP2025 VeriPB accepts proof-output/elaboration mode.
        candidates=[
          [str(vp),"--elaborate",str(kernel),str(opb),str(proof)],
          [str(vp),"--proofOutput",str(kernel),str(opb),str(proof)]
        ]
        for cmd in candidates:
            if kernel.exists(): kernel.unlink()
            ec,et,eto,eout,eerr=run(cmd,ns.timeout_seconds,elab_stdout,elab_stderr)
            efail=fail_markers(eout+"\n"+eerr)
            if not eto and ec==0 and not efail and kernel.exists() and kernel.stat().st_size>0:
                kernel_ok=True; used_cmd=cmd; break
            # Only the exact frozen alternatives above are allowed. No other fallback.
        if not kernel_ok and used_cmd is None:
            used_cmd=candidates[-1]

    receipt={
      "schema":"janus.trump.stage6b3.veripb_primary_and_elaboration_receipt.v1",
      "veripb_binary_sha256":sha(vp),
      "OPB_sha256":sha(opb),
      "raw_proof_sha256":sha(proof),
      "raw_proof_bytes":proof.stat().st_size,
      "raw_proof_has_conclusion_UNSAT":raw_conclusion,
      "verification_command":verify_cmd,
      "verification_exit_code":vc,
      "verification_runtime_seconds":vt,
      "verification_timed_out":vto,
      "verification_failure_markers":vfail,
      "VERIPB_CHECKER_REPORTED_CONCLUSION":"UNSAT" if reported_unsat else None,
      "VERIPB_PROCESS_COMPLETED_SUCCESSFULLY":(not vto and vc==0),
      "VERIPB_PROOF_VERIFICATION_ERRORS":0 if (not vfail and not vto and vc==0) else None,
      "VERIPB_CONCLUSION_SECTION_VALID":raw_conclusion,
      "VERIPB_PRIMARY_raw_proof_verified":"YES" if primary_ok else "NO",
      "elaboration_attempted":primary_ok,
      "elaboration_command":used_cmd,
      "elaboration_exit_code":ec,
      "elaboration_runtime_seconds":et,
      "elaboration_timed_out":eto,
      "elaboration_failure_markers":efail,
      "elaboration_succeeded":"YES" if kernel_ok else "NO",
      "kernel_proof_sha256":sha(kernel) if kernel_ok else None,
      "kernel_proof_bytes":kernel.stat().st_size if kernel_ok else None
    }
    rp=outdir/"veripb.receipt.json"
    rp.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "VERIPB_PRIMARY_raw_proof_verified":receipt["VERIPB_PRIMARY_raw_proof_verified"],
      "reported_conclusion":receipt["VERIPB_CHECKER_REPORTED_CONCLUSION"],
      "elaboration_succeeded":receipt["elaboration_succeeded"],
      "kernel_proof_sha256":receipt["kernel_proof_sha256"]
    },sort_keys=True))


if __name__=="__main__":
    main()
