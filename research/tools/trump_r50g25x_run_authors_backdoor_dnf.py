#!/usr/bin/env python3
"""Execute the acquired authors' Backdoor-DNF implementation on frozen R50G25X.

This is an orchestration harness, not a detector implementation. It:
  * converts each frozen residual to DIMACS,
  * invokes the authors' runner.py unchanged for Horn, dual-Horn and Krom,
  * enforces a per-run wall-clock timeout,
  * invokes JANUS' independent DNF verifier on every returned Result,
  * records success / timeout / error without interpreting timeout as no-DNF.

The authors' source tree and its git/Zenodo provenance are external inputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


BASES = {
    "HORN": [],
    "DUAL_HORN": ["-r"],
    "KROM": ["-w"],
}


def canonical_sha(clauses):
    raw=json.dumps(clauses,sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(raw).hexdigest()


def write_dimacs(path: Path, clauses):
    maxvar=max((abs(l) for c in clauses for l in c), default=0)
    with path.open("w",encoding="ascii") as f:
        f.write(f"p cnf {maxvar} {len(clauses)}\n")
        for c in clauses:
            f.write(" ".join(map(str,c))+" 0\n")


def has_result(log_path: Path):
    if not log_path.exists():
        return False
    return any(line.startswith("Result:") for line in log_path.read_text(
        encoding="utf-8",errors="replace").splitlines())


def run_one(python: str, runner: Path, verifier: Path, cnf: Path, base: str,
            temp_dir: Path, log: Path, verify_out: Path, timeout_s: float):
    cmd=[python,str(runner),str(cnf),"-e","1","-c","-t",str(temp_dir),*BASES[base]]
    temp_dir.mkdir(parents=True,exist_ok=True)
    started=time.monotonic()
    try:
        p=subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout_s,
            cwd=str(runner.parent),
        )
        elapsed=time.monotonic()-started
        log.write_text(p.stdout or "",encoding="utf-8")
        state="AUTHORS_EXIT_0" if p.returncode==0 else "AUTHORS_NONZERO_EXIT"
        row={
            "authors_status":state,
            "authors_returncode":p.returncode,
            "authors_runtime_seconds":elapsed,
            "result_line_present":has_result(log),
            "authors_command":[str(x) for x in cmd],
        }
    except subprocess.TimeoutExpired as e:
        elapsed=time.monotonic()-started
        stdout=e.stdout or ""
        if isinstance(stdout,bytes):
            stdout=stdout.decode("utf-8","replace")
        log.write_text(stdout,encoding="utf-8")
        return {
            "authors_status":"RESOURCE_LIMIT_TIMEOUT",
            "authors_returncode":None,
            "authors_runtime_seconds":elapsed,
            "result_line_present":has_result(log),
            "independent_verification":"NOT_RUN",
        }

    if not row["result_line_present"]:
        row["independent_verification"]="NOT_RUN"
        return row

    vcmd=[python,str(verifier),str(cnf),str(log),base,str(verify_out)]
    try:
        vp=subprocess.run(
            vcmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=max(30.0,timeout_s),
        )
        row["verifier_returncode"]=vp.returncode
        row["verifier_stdout"]=vp.stdout[-4000:]
        if verify_out.exists():
            v=json.loads(verify_out.read_text(encoding="utf-8"))
            row["independent_verification"]=v["verdict"]
            row["term_count"]=v["term_count"]
            row["max_term_size"]=v["max_term_size"]
            row["union_variable_count"]=v["union_variable_count"]
            row["dnf_tautology"]=v["dnf_tautology"]
            row["all_terms_base_membership"]=v["all_terms_base_membership"]
            row["tautology_dpll_nodes"]=v["tautology_dpll_nodes"]
        else:
            row["independent_verification"]="VERIFIER_NO_OUTPUT"
    except subprocess.TimeoutExpired:
        row["independent_verification"]="VERIFIER_RESOURCE_LIMIT_TIMEOUT"
    return row


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("frozen_json")
    ap.add_argument("authors_src")
    ap.add_argument("verifier")
    ap.add_argument("out_dir")
    ap.add_argument("--timeout",type=float,default=20.0)
    ns=ap.parse_args()

    frozen=Path(ns.frozen_json)
    authors=Path(ns.authors_src)
    verifier=Path(ns.verifier).resolve()
    out=Path(ns.out_dir)
    out.mkdir(parents=True,exist_ok=True)
    dimacs=out/"dimacs"; logs=out/"logs"; verify=out/"verify"; tmp=out/"tmp"
    for p in (dimacs,logs,verify,tmp): p.mkdir(parents=True,exist_ok=True)

    runner=(authors/"runner.py").resolve()
    if not runner.exists():
        raise SystemExit(f"AUTHORS_RUNNER_MISSING:{runner}")
    muser=authors/"bin"/"muser-2"
    if not muser.exists():
        raise SystemExit(f"AUTHORS_MUSER_MISSING:{muser}")
    os.chmod(muser,0o755)

    data=json.loads(frozen.read_text(encoding="utf-8"))
    rows=[]
    for i,src in enumerate(data["residuals"]):
        clauses=src["residual_formula"]
        cnf=dimacs/f"r50g25x_{i:02d}.cnf"
        write_dimacs(cnf,clauses)
        base_rows={}
        for base in BASES:
            log=logs/f"r50g25x_{i:02d}_{base.lower()}.log"
            vout=verify/f"r50g25x_{i:02d}_{base.lower()}.json"
            base_rows[base]=run_one(
                sys.executable,runner,verifier,cnf,base,
                tmp/f"r50g25x_{i:02d}_{base.lower()}",
                log,vout,ns.timeout
            )
            print(json.dumps({
                "index":i,"base":base,
                "status":base_rows[base]["authors_status"],
                "verify":base_rows[base].get("independent_verification"),
                "terms":base_rows[base].get("term_count"),
            },sort_keys=True),flush=True)
        rows.append({
            "index":i,
            "family":src["family"],
            "hash":src["residual_hash"],
            "CLV":src["residual_CLV"],
            "canonical_formula_sha256":canonical_sha(clauses),
            "bases":base_rows,
        })

    passed=[
        (r["index"],base,b)
        for r in rows for base,b in r["bases"].items()
        if b.get("independent_verification")=="PASS"
    ]
    result={
        "schema":"janus.trump.r50g25x.authors_backdoor_dnf_execution.v1",
        "authority":"AUTHORS_DETECTOR_EXECUTION_PLUS_INDEPENDENT_TAUTOLOGY_AND_BASE_REPLAY__FINITE_CORPUS_ONLY",
        "source_artifact_id":9992845123,
        "source_run_id":34044941068,
        "authors_runner":str(runner),
        "per_run_timeout_seconds":ns.timeout,
        "rows":rows,
        "sound_routes":[
            {
                "index":i,"base":base,
                "term_count":b.get("term_count"),
                "max_term_size":b.get("max_term_size"),
                "union_variable_count":b.get("union_variable_count"),
            } for i,base,b in passed
        ],
        "sound_route_count":len(passed),
        "residual_indices_with_any_sound_route":sorted({i for i,_,_ in passed}),
        "firewall":{
            "timeout_means_no_dnf":False,
            "nonzero_exit_means_no_dnf":False,
            "minimum_dnf_claimed":False,
            "parameter_optimum_claimed":False,
            "general_sat_in_p":"NOT_PROVED",
            "p_vs_np":"OPEN",
        },
    }
    (out/"TRUMP_R50G25X_AUTHORS_BACKDOOR_DNF_EXECUTION.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "sound_route_count":result["sound_route_count"],
        "residual_indices_with_any_sound_route":result["residual_indices_with_any_sound_route"],
    },sort_keys=True))


if __name__=="__main__":
    main()
