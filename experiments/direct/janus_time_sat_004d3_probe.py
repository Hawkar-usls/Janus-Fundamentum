#!/usr/bin/env python3
"""TIME-SAT-004D3: preregistered 9-new-SATComp-instance source-only challenge.

Two-runner replay of a FROZEN, PUBLIC-origin (NOT hidden) mixed-family cohort.
Strict source fetch and DIMACS validation, complete parity CNF recognition,
GF2 solution with independently replayed original SAT model if applicable,
or same-admin source-bound algebraic 0=1 receipt; otherwise ABSTAIN.
One child per source for strict CPU/memory budgets. NO CDCL in this stage.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
from time import perf_counter

from janus_time_sat_004b_acquire import retrieve, unpack_bounded, scan_dimacs
from janus_time_sat_004b_baselines import read_cnf, classify_nonzero_exit
from janus_time_sat_004d1_xor import (
    MAX_N,MAX_ROWS,MAX_LITERALS,MAX_WIDTH,solve_if_exact_xor
)
from janus_time_sat_004d_pilot import EXPECTED_PREREG_GIT_BLOB

HERE=Path(__file__).resolve().parent
MANIFEST=Path("experiments/time_sat_004_external/PREREGISTERED_004D3_SATCOMP2026_MULTIFAMILY_20261101.json")
FROZEN_GIT_BLOB="5fc4572e41b57a973c3a26559173a6f1a53e4cd5"
PRIOR=Path("experiments/time_sat_004_external/PREREGISTERED_SATCOMP2026_PILOT_20261101.json")
EXACT_LIMITS={"n":MAX_N,"rows":MAX_ROWS,"literals":MAX_LITERALS,"width":MAX_WIDTH}
CANDIDATE_COUNT=9
MAX_SECONDS_CHILD_CPU=15
MAX_SECONDS_PARENT_WALL=18
ADDRESS_SPACE=2_147_483_648

def git_blob(path:Path):
    return subprocess.run(["git","hash-object",str(path)],check=True,
                          capture_output=True,text=True).stdout.strip()

def verify_frozen_manifest():
    if git_blob(MANIFEST)!=FROZEN_GIT_BLOB:
        raise AssertionError("FROZEN_004D3_MANIFEST_BLOB_CHANGED")
    if git_blob(PRIOR)!=EXPECTED_PREREG_GIT_BLOB:
        raise AssertionError("PREVIOUS_004B_MANIFEST_CHANGED")
    data=json.loads(MANIFEST.read_text())
    cases=data["candidates"]
    if len(cases)!=CANDIDATE_COUNT or len({c["GBD_database_id_NOT_SHA256"] for c in cases})!=9:
        raise AssertionError("004D3_FROZEN_COHORT_COUNT_OR_IDS_CHANGED")
    earlier={x["hash"] for x in json.loads(PRIOR.read_text())["candidates"]}
    if any(c["GBD_database_id_NOT_SHA256"] in earlier for c in cases):
        raise AssertionError("REUSED_EARLIER_PUBLIC_SOURCE")
    expected=["lights-out","lights-out","linear-equations","xor-shifting",
              "minimum-disagreement-parity","binary-tree-parity",
              "graph-coloring","argumentation","boxfolding"]
    if [c["family"] for c in cases]!=expected:
        raise AssertionError("COHORT_FAMILY_ORDER_CHANGED")
    if [c["cohort_index"] for c in cases]!=list(range(1,10)):
        raise AssertionError("FROZEN_INDEX_CHANGED")
    for c in cases:
        if c["official_uri"]!="http://benchmark-database.de/file/"+c["GBD_database_id_NOT_SHA256"]:
            raise AssertionError("GBD_OFFICIAL_URI_CHANGED")
    return cases

def bounded_source_shape(dim):
    """Conservative pre-check to avoid huge Python clause allocations."""
    return (dim["n_variables"]<=MAX_N and dim["n_clauses"]<=MAX_ROWS
            and dim["n_literal_occurrences"]<=MAX_LITERALS
            and dim["max_clause_width"]<=MAX_WIDTH)

def evaluate_one(source,n,m):
    resource.setrlimit(resource.RLIMIT_AS,(ADDRESS_SPACE,ADDRESS_SPACE))
    resource.setrlimit(resource.RLIMIT_CPU,
                       (MAX_SECONDS_CHILD_CPU,MAX_SECONDS_CHILD_CPU+1))
    rows=read_cnf(source,n,m,max_literals=MAX_LITERALS)
    outcome=solve_if_exact_xor(rows,n)
    if outcome["verdict"] not in (
       "SAT_ORIGINAL_MODEL_VERIFIED","GF2_UNSAT_SAME_ADMIN_REPLAY_ONLY",
       "ABSTAIN_NO_SAT_CLAIM"):
        raise AssertionError("INVALID_EXACT_XOR_CHILD_VERDICT")
    return outcome

def execute(out):
    frozen=verify_frozen_manifest()
    out.mkdir(parents=True,exist_ok=True)
    results=[]
    for c in frozen:
        candidate={"hash":c["GBD_database_id_NOT_SHA256"],
                   "official_uri":c["official_uri"]}
        case={"cohort_index":c["cohort_index"],
              "GBD_id_NOT_SHA256":candidate["hash"],
              "family":c["family"],
              "author":c["upstream_author"],
              "catalog_label_UNVERIFIED":c["upstream_metadata_label_UNVERIFIED"],
              "original_bytes_sha256":None,"decoded_CNF_sha256":None,
              "source_status":"NOT_ATTEMPTED","structural_status":"NOT_RUN",
              "verdict":"NO_MATHEMATICAL_CLAIM"}
        begin=perf_counter()
        raw=None;decoded=None
        try:
            raw,meta=retrieve(candidate,out)
            case["original_bytes_sha256"]=meta["source_sha256"]
            case["original_transfer_bytes"]=meta["original_transfer_bytes"]
            decoded=out/(candidate["hash"]+".cnf")
            decoded_meta=unpack_bounded(raw,decoded)
            case["decoded_CNF_sha256"]=decoded_meta["uncompressed_sha256"]
            case["decoded_original_bytes"]=decoded_meta["uncompressed_bytes"]
            shape=scan_dimacs(decoded)
            case["dimensions"]=shape
            case["source_status"]="STRICT_DIMACS_ORIGINAL_PASS"
            if not bounded_source_shape(shape):
                case["structural_status"]="ABSTAIN_BEFORE_CHILD_BOUNDED_SOURCE_SHAPE"
                case["verdict"]="ABSTAIN_NO_SAT_CLAIM"
            else:
                cmd=[sys.executable,str(Path(__file__).resolve()),
                     "--child","--source",str(decoded),
                     "--n",str(shape["n_variables"]),"--m",str(shape["n_clauses"])]
                started=perf_counter()
                try:
                    child=subprocess.run(cmd,text=True,capture_output=True,
                                         timeout=MAX_SECONDS_PARENT_WALL,check=False)
                    if child.returncode:
                        result=classify_nonzero_exit(child.returncode)
                        result["return_code"]=child.returncode
                        result["stderr_tail"]=child.stderr[-800:]
                    else:
                        result=json.loads(child.stdout)
                except subprocess.TimeoutExpired:
                    result={"verdict":"UNKNOWN_WALL_TIMEOUT"}
                case["structural_child_wall_seconds"]=perf_counter()-started
                case["structural_result"]=result
                case["verdict"]=result["verdict"]
                case["structural_status"]=result.get("coverage_status","PROCESS_UNKNOWN_OR_ERROR")
                if result["verdict"]=="SAT_ORIGINAL_MODEL_VERIFIED":
                    model=result["model"]
                    if len(model)!=shape["n_variables"]:
                        raise AssertionError("incomplete source SAT model")
                    case["model_signed_literal_SHA256"]=sha256(
                        json.dumps(model,separators=(",",":")).encode("ascii")).hexdigest()
                if result["verdict"]=="GF2_UNSAT_SAME_ADMIN_REPLAY_ONLY":
                    case["unsat_portable_DRUP_LRAT"]="NOT_PRODUCED"
                    case["external_Witness"]="NOT_VERIFIED"
        except Exception as exc:
            case["source_status"]="ERROR_"+type(exc).__name__
            case["source_error"]=str(exc)[:250]
            case["verdict"]="NO_MATHEMATICAL_CLAIM"
        finally:
            if raw is not None:raw.unlink(missing_ok=True)
            if decoded is not None:decoded.unlink(missing_ok=True)
        case["acquisition_parse_and_structural_wall_seconds"]=perf_counter()-begin
        results.append(case)
        print("TIME_SAT_004D3",case["family"],candidate["hash"],
              case["source_status"],case["structural_status"],
              case["verdict"],flush=True)
    result={
      "schema":"JANUS-TIME-SAT-004D3-PUBLIC-MULTIFAMILY-SOURCE-ONLY-PILOT-V1",
      "status":"RESEARCH_PUBLIC_SOURCE_ONLY_NO_NEW_CLAIM_OF_SPEEDUP",
      "frozen_manifest_git_blob":FROZEN_GIT_BLOB,
      "frozen_source_count":CANDIDATE_COUNT,
      "run_head_SHA":os.getenv("GITHUB_SHA","LOCAL"),
      "run_id":os.getenv("GITHUB_RUN_ID","LOCAL"),
      "research_cohort_not_sealed":True,
      "source_only_no_CDCL_or_paid_AI":True,
      "exact_XOR_source_verification_not_family_name_inference":True,
      "max_download_bytes":52428800,
      "max_decoded_bytes":134217728,
      "child_CPU_limit_seconds":MAX_SECONDS_CHILD_CPU,
      "child_AS_limit_bytes":ADDRESS_SPACE,
      "individual_child_wall_limit_seconds":MAX_SECONDS_PARENT_WALL,
      "no_result_replacement_or_cherrypicking":True,
      "not_an_independently_administered_Witness":True,
      "production_C023":"UNCHANGED",
      "results":results
    }
    (out/"result.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    source_ok=sum(x["source_status"]=="STRICT_DIMACS_ORIGINAL_PASS" for x in results)
    exact=sum(x["structural_status"]=="EXACT_XOR_COVER_PASS" for x in results)
    print("004D3_SUMMARY",json.dumps({"sources":len(results),
           "dimacs_ok":source_ok,"exact_full_XOR":exact,
           "verdicts":{x["family"]+"-"+str(x["cohort_index"]):x["verdict"]
                       for x in results}},sort_keys=True),flush=True)
    incomplete=[x for x in results
                if x["source_status"]!="STRICT_DIMACS_ORIGINAL_PASS"
                or x["verdict"]=="NO_MATHEMATICAL_CLAIM"
                or x["structural_status"]=="PROCESS_UNKNOWN_OR_ERROR"]
    if incomplete:
        raise RuntimeError("Cohort incomplete or structurally unresolved: raw receipts preserved; no 9/9 PASS")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path)
    ap.add_argument("--child",action="store_true")
    ap.add_argument("--source",type=Path)
    ap.add_argument("--n",type=int)
    ap.add_argument("--m",type=int)
    args=ap.parse_args()
    if args.child:
        if args.source is None or args.n is None or args.m is None:
            raise SystemExit("child source and dimensions required")
        print(json.dumps(evaluate_one(args.source,args.n,args.m),sort_keys=True))
    else:
        if args.out is None:raise SystemExit("--out required")
        execute(args.out)
