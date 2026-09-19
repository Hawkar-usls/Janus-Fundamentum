#!/usr/bin/env python3
"""Stage6B.4 VeriPB v2 primary verification + optional elaboration harness.

Infrastructure repair scope is frozen by commit
4aa65af4c9f0745ef273ca8265b2b00b4235504b.

For pinned proof version 2.0, the terminal section is independently parsed as
the final three meaningful lines:
  output ...
  conclusion UNSAT [: ConstraintID]
  end pseudo-Boolean proof
with optional trailing semicolons.

Scientific UNSAT authority requires BOTH this terminal parser and successful
VeriPB verification with an explicit VERIFIED UNSATISFIABLE report.
"""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess, time
from pathlib import Path

FAIL_PATTERNS=[
    re.compile(r"verification\s+failed",re.I),
    re.compile(r"proof\s+verification\s+error",re.I),
    re.compile(r"invalid\s+proof",re.I),
]
VERIFIED_UNSAT_PATTERNS=[
    re.compile(r"\bs\s+VERIFIED\s+UNSAT(?:ISFIABLE)?\b",re.I),
    re.compile(r"\bVERIFIED\s+UNSAT(?:ISFIABLE)?\b",re.I),
    re.compile(r"\bUNSAT(?:ISFIABLE)?\s+VERIFIED\b",re.I),
]
HEADER_RE=re.compile(r"^pseudo-Boolean\s+proof\s+version\s+2\.0\s*$",re.I)
OUTPUT_RE=re.compile(r"^output\s+.+?\s*;?$",re.I)
CONCLUSION_RE=re.compile(r"^conclusion\s+UNSAT(?:\s*:\s*(\d+))?\s*;?$",re.I)
END_RE=re.compile(r"^end\s+pseudo-Boolean\s+proof\s*;?$",re.I)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def parse_terminal(proof_text):
    meaningful=[]
    for raw in proof_text.splitlines():
        s=raw.strip()
        if not s or s.startswith("%"): continue
        meaningful.append(s)
    receipt={
      "proof_version_2_header_valid":False,
      "terminal_section_valid":False,
      "output_line":None,
      "conclusion_line":None,
      "conclusion_type":None,
      "contradiction_constraint_id":None,
      "end_line":None,
      "noncomment_line_count":len(meaningful)
    }
    if not meaningful or not HEADER_RE.fullmatch(meaningful[0]):
        receipt["failure"]="MISSING_OR_INVALID_PROOF_V2_HEADER"
        return receipt
    receipt["proof_version_2_header_valid"]=True
    if len(meaningful)<4:
        receipt["failure"]="PROOF_TOO_SHORT_FOR_TERMINAL_SECTION"
        return receipt
    output_line,conclusion_line,end_line=meaningful[-3:]
    receipt["output_line"]=output_line
    receipt["conclusion_line"]=conclusion_line
    receipt["end_line"]=end_line
    om=OUTPUT_RE.fullmatch(output_line)
    cm=CONCLUSION_RE.fullmatch(conclusion_line)
    em=END_RE.fullmatch(end_line)
    if not om:
        receipt["failure"]="INVALID_OUTPUT_TERMINAL_LINE"; return receipt
    if not cm:
        receipt["failure"]="INVALID_UNSAT_CONCLUSION_TERMINAL_LINE"; return receipt
    if not em:
        receipt["failure"]="INVALID_END_TERMINAL_LINE"; return receipt
    receipt["conclusion_type"]="UNSAT"
    receipt["contradiction_constraint_id"]=int(cm.group(1)) if cm.group(1) is not None else None
    receipt["terminal_section_valid"]=True
    return receipt


def run(cmd,timeout,stdout_path,stderr_path):
    t0=time.perf_counter()
    try:
        p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=timeout,check=False)
        timed_out=False; out=p.stdout; err=p.stderr; code=p.returncode
    except subprocess.TimeoutExpired as e:
        timed_out=True; code=None; out=e.stdout or ""; err=e.stderr or ""
        if isinstance(out,bytes): out=out.decode(errors="replace")
        if isinstance(err,bytes): err=err.decode(errors="replace")
    runtime=time.perf_counter()-t0
    Path(stdout_path).write_text(out); Path(stderr_path).write_text(err)
    return code,runtime,timed_out,out,err


def explicit_unsat(text):
    return any(p.search(text) for p in VERIFIED_UNSAT_PATTERNS)


def fail_markers(text):
    return [p.pattern for p in FAIL_PATTERNS if p.search(text)]


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("veripb"); ap.add_argument("opb"); ap.add_argument("proof")
    ap.add_argument("kernel"); ap.add_argument("outdir"); ap.add_argument("--timeout-seconds",type=int,default=600)
    ns=ap.parse_args()
    outdir=Path(ns.outdir); outdir.mkdir(parents=True,exist_ok=True)
    vp=Path(ns.veripb); opb=Path(ns.opb); proof=Path(ns.proof); kernel=Path(ns.kernel); kernel.parent.mkdir(parents=True,exist_ok=True)

    terminal=parse_terminal(proof.read_text(errors="replace"))

    verify_stdout=outdir/"veripb.verify.stdout"; verify_stderr=outdir/"veripb.verify.stderr"
    verify_cmd=[str(vp),str(opb),str(proof)]
    vc,vt,vto,vout,verr=run(verify_cmd,ns.timeout_seconds,verify_stdout,verify_stderr)
    combined=vout+"\n"+verr; markers=fail_markers(combined); reported=explicit_unsat(combined)
    primary_ok=(terminal["terminal_section_valid"] and not vto and vc==0 and not markers and reported)

    ec=et=None; eto=False; eout=eerr=""; emarkers=[]; kernel_ok=False; used=None
    if primary_ok:
        elab_stdout=outdir/"veripb.elaborate.stdout"; elab_stderr=outdir/"veripb.elaborate.stderr"
        candidates=[
          [str(vp),"--elaborate",str(kernel),str(opb),str(proof)],
          [str(vp),"--proofOutput",str(kernel),str(opb),str(proof)]
        ]
        for cmd in candidates:
            if kernel.exists(): kernel.unlink()
            ec,et,eto,eout,eerr=run(cmd,ns.timeout_seconds,elab_stdout,elab_stderr)
            emarkers=fail_markers(eout+"\n"+eerr)
            if not eto and ec==0 and not emarkers and kernel.exists() and kernel.stat().st_size>0:
                kernel_ok=True; used=cmd; break
        if used is None: used=candidates[-1]

    receipt={
      "schema":"janus.trump.stage6b4.veripb_v2_primary_and_elaboration_receipt.v1",
      "repair_prereg_commit":"4aa65af4c9f0745ef273ca8265b2b00b4235504b",
      "veripb_binary_sha256":sha(vp),
      "OPB_sha256":sha(opb),
      "raw_proof_sha256":sha(proof),
      "raw_proof_bytes":proof.stat().st_size,
      "terminal_parser":terminal,
      "raw_proof_has_conclusion_UNSAT":terminal["terminal_section_valid"] and terminal["conclusion_type"]=="UNSAT",
      "verification_command":verify_cmd,
      "verification_exit_code":vc,
      "verification_runtime_seconds":vt,
      "verification_timed_out":vto,
      "verification_failure_markers":markers,
      "VERIPB_CHECKER_REPORTED_CONCLUSION":"UNSAT" if reported else None,
      "VERIPB_PROCESS_COMPLETED_SUCCESSFULLY":not vto and vc==0,
      "VERIPB_PROOF_VERIFICATION_ERRORS":0 if not markers and not vto and vc==0 else None,
      "VERIPB_CONCLUSION_SECTION_VALID":terminal["terminal_section_valid"],
      "VERIPB_PRIMARY_raw_proof_verified":"YES" if primary_ok else "NO",
      "elaboration_attempted":primary_ok,
      "elaboration_command":used,
      "elaboration_exit_code":ec,
      "elaboration_runtime_seconds":et,
      "elaboration_timed_out":eto,
      "elaboration_failure_markers":emarkers,
      "elaboration_succeeded":"YES" if kernel_ok else "NO",
      "kernel_proof_sha256":sha(kernel) if kernel_ok else None,
      "kernel_proof_bytes":kernel.stat().st_size if kernel_ok else None
    }
    rp=outdir/"veripb.receipt.json"; rp.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"raw_proof_verified":receipt["VERIPB_PRIMARY_raw_proof_verified"],
                      "conclusion":receipt["VERIPB_CHECKER_REPORTED_CONCLUSION"],
                      "terminal_section_valid":receipt["VERIPB_CONCLUSION_SECTION_VALID"],
                      "constraint_id":terminal.get("contradiction_constraint_id"),
                      "elaboration_succeeded":receipt["elaboration_succeeded"]},sort_keys=True))
    if not primary_ok: raise SystemExit(2)


if __name__=="__main__": main()
