#!/usr/bin/env python3
"""TIME-SAT-004D7 exact-original public 004B three-case independent GF2 rank.

Strict research-only, source-only. Uses pre-frozen original GBD transfer and
decoded SHA256. The full existing 004D6 proof operator is reused UNMODIFIED.
Every derived resolvent and XOR-mask group is separately replay-verified.
New GF2 augmented/coefficient rank measured vs all ORIGINAL exact XOR masks.
No SAT engines, no speedups, no concealed holdout, no production writes.
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

from janus_time_sat_004b_acquire import retrieve,unpack_bounded,scan_dimacs
from janus_time_sat_004b_baselines import read_cnf,classify_nonzero_exit
from janus_time_sat_004d7_rank_gate import source_rank_experiment

ROOT=Path("experiments/time_sat_004_external")
FROZEN=ROOT/"PREREGISTERED_004D7_NEW_SOURCE_RANK_GATE_20261102.json"
FROZEN_BLOB="2b54d42df0e3f19b1da8a566c17cb2e81bb279d8"
OLD=ROOT/"PREREGISTERED_SATCOMP2026_PILOT_20261101.json"
OLD_BLOB="dc658d57453813bb306aa20f45b3385571f1fe3d"
EXPECTED=("or_randxor","greentao","p-center")
CPU=18
WALL=24
RLIMIT=2_147_483_648

def sha(p):
    h=sha256()
    with p.open("rb") as fd:
        for chunk in iter(lambda:fd.read(65536),b""):h.update(chunk)
    return h.hexdigest()

def verify_freeze():
    for file,wanted in ((FROZEN,FROZEN_BLOB),(OLD,OLD_BLOB)):
        found=subprocess.run(["git","hash-object",str(file)],
            text=True,capture_output=True,check=True).stdout.strip()
        if found!=wanted:raise AssertionError("004D7 frozen source manifest changed "+str(file))
    data=json.loads(FROZEN.read_text())
    cases=data["original_cases"]
    old=json.loads(OLD.read_text())["candidates"]
    old_by_id={x["hash"]:x for x in old}
    if [x["family"] for x in cases]!=list(EXPECTED):
        raise AssertionError("04D7 exact selected families modified")
    for c in cases:
        original=old_by_id.get(c["GBD_id_NOT_SHA256"])
        if original is None or original["family"]!=c["family"] or original["result"]!=c["catalog_label"]:
            raise AssertionError("original 004B selection record mismatch")
        if c["n_variables"]>5000 or c["n_clauses"]>30000 or c["n_literal_occurrences"]>120000:
            raise AssertionError("source outside frozen 004D6 bounds")
    return cases

def check_source(path,c):
    if sha(path)!=c["original_decoded_CNF_sha256"]:
        raise AssertionError("original decoded SHA changed "+c["family"])
    dims=scan_dimacs(path)
    for key in ("n_variables","n_clauses","n_literal_occurrences"):
        if dims[key]!=c[key]:raise AssertionError("original DIMACS "+key+" mismatch "+c["family"])
    return dims

def child(original,case_index,out):
    resource.setrlimit(resource.RLIMIT_AS,(RLIMIT,RLIMIT))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    cases=verify_freeze()
    if not 0<=case_index<len(cases):raise AssertionError("invalid preregistered case index")
    c=cases[case_index]
    check_source(original,c)
    before=perf_counter()
    rows=read_cnf(original,c["n_variables"],c["n_clauses"],max_literals=120000)
    result=source_rank_experiment(rows,c["n_variables"])
    if result["status"]!="SOURCE_PROOF_REPLAY_AND_EXACT_GF2_RANK_PASS":
        raise AssertionError("source formal proof gate failed: "+result["status"])
    end_to_end=perf_counter()-before
    report={
       "schema":"JANUS-TIME-SAT-004D7-SOURCE-REPLAYED-RANK-CASE-V1",
       "family":c["family"],"GBD_id_NOT_SHA256":c["GBD_id_NOT_SHA256"],
       "original_SHA256":c["original_decoded_CNF_sha256"],
       "original_CNF_n":c["n_variables"],"original_CNF_m":c["n_clauses"],
       "original_CNF_literals":c["n_literal_occurrences"],
       "operator_identical_to_004D6":True,
       "source_only_elapsed_seconds_NOT_SAT_BENCHMARK":end_to_end,
       "child_peak_RSS_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
       "source_original_SHA_and_DAG_replay":"PASS",
       "rank_diagnostic":result,
       "source_original_CNF_preserved":True,
       "solver_calls":0,"production_C023":"UNCHANGED",
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    rank=result["independent_rank_analysis"]
    print("004D7_CASE",json.dumps({
       "family":c["family"],
       "resolvents":result["source_resolution_new_clause_count"],
       "new_forms":result["source_derived_new_syntactic_XOR_count"],
       "rank_new_coeff":rank["independent_new_coefficient_rank"],
       "rank_new_aug":rank["independent_new_augmented_rank"],
       "source_proof":"PASS",
       "truncated":result["source_resolution_truncated"]},sort_keys=True),flush=True)

def run(out):
    cases=verify_freeze()
    out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for i,c in enumerate(cases):
        case={"family":c["family"],"GBD_id_NOT_SHA256":c["GBD_id_NOT_SHA256"],
              "declared_original_SHA256":c["original_decoded_CNF_sha256"],
              "status":"NOT_ATTEMPTED","result":None}
        try:
            original,fetch_meta=retrieve({"hash":c["GBD_id_NOT_SHA256"],
                 "official_uri":"http://benchmark-database.de/file/"+c["GBD_id_NOT_SHA256"]},out)
            if fetch_meta["source_sha256"]!=c["original_transfer_sha256"]:
                raise AssertionError("original compressed transfer SHA mismatch")
            decoded=out/(c["GBD_id_NOT_SHA256"]+".original.cnf")
            unpack=unpack_bounded(original,decoded)
            if unpack["uncompressed_sha256"]!=c["original_decoded_CNF_sha256"]:
                raise AssertionError("original raw CNF SHA mismatch")
            check_source(decoded,c)
            case["source_verified"]="ORIGINAL_TRANSFER_AND_DECODED_SHA_DIMACS_PASS"
            case["original_transfer_bytes"]=fetch_meta["original_transfer_bytes"]
            case["original_download_SHA256"]=fetch_meta["source_sha256"]
            child_file=out/(c["family"]+"-exact-rank.json")
            cmd=[sys.executable,str(Path(__file__).resolve()),
                "--child",str(decoded),"--case-index",str(i),"--child-out",str(child_file)]
            began=perf_counter()
            try:
                response=subprocess.run(cmd,text=True,capture_output=True,timeout=WALL,check=False)
                if response.returncode:
                    case["result"]=classify_nonzero_exit(response.returncode)
                    case["result"]["stderr_tail"]=response.stderr[-1000:]
                    case["status"]="ABSTAIN_BOUNDED_CHILD_ERROR_OR_RESOURCE_LIMIT"
                else:
                    if not child_file.is_file():raise AssertionError("successful child emitted no proof file")
                    details=json.loads(child_file.read_text())
                    if details["original_SHA256"]!=c["original_decoded_CNF_sha256"]:
                        raise AssertionError("source proof digest mismatch")
                    rank=details["rank_diagnostic"]["independent_rank_analysis"]
                    case["result"]={
                        "verdict":"SOURCE_CERTIFICATE_RANK_PASS",
                        "original_explicit_GF2":details["rank_diagnostic"]["original_complete_mask_XOR_count"],
                        "new_full_XOR_forms":details["rank_diagnostic"]["source_derived_new_syntactic_XOR_count"],
                        "resolvents":details["rank_diagnostic"]["source_resolution_new_clause_count"],
                        "rank_increment_coeff":rank["independent_new_coefficient_rank"],
                        "rank_increment_augmented":rank["independent_new_augmented_rank"],
                        "independent_witnesses":rank["new_augmented_rank_witnesses"][:12],
                        "source_proof_file_sha256":sha(child_file)
                    }
                    case["status"]="SOURCE_PROOF_AND_GF2_RANK_PASS"
            except subprocess.TimeoutExpired:
                case["result"]={"verdict":"ABSTAIN_PARENT_WALL_TIMEOUT_NOT_SOLVER_UNSAT"}
                case["status"]="ABSTAIN_WALL_TIME"
            case["full_child_wall_seconds_NOT_SAT_BENCHMARK"]=perf_counter()-began
        except Exception as e:
            case["status"]="SOURCE_AUTHENTICITY_OR_PREP_EXCEPTION"
            case["error_class"]=type(e).__name__
            case["error_detail"]=str(e)[:250]
        rows.append(case)
        print("004D7_STATUS",c["family"],case["status"],
              case["result"],flush=True)
    report={
       "schema":"JANUS-TIME-SAT-004D7-THREE-SHA-FROZEN-NEW-TO-RESOLUTION-PUBLIC-SOURCES-V1",
       "status":"SOURCE_ONLY_DEVELOPMENT_TEST_NOT_BLIND_NOT_SAT_BENCHMARK",
       "original_004B_public_source_frozen_git_blob":OLD_BLOB,
       "004D7_registered_source_git_blob":FROZEN_BLOB,
       "run_id":os.environ.get("GITHUB_RUN_ID","LOCAL"),
       "head_sha":os.environ.get("GITHUB_SHA","LOCAL"),
       "original_source_download_and_decode_SHA_strict":True,
       "only_prior_004D6_bounded_resolution":"YES_IDENTICAL_LIMITS_NO_TUNING",
       "outcome_meaning":"Independent GF2 rank relative to original full sign-mask XOR base; no universal SAT or performance claim",
       "external_independent_Witness":"OPEN","C023_main":"UNCHANGED",
       "n_expected":len(cases),"n_completed":sum(x["status"]=="SOURCE_PROOF_AND_GF2_RANK_PASS" for x in rows),
       "cases":rows
    }
    (out/"summary.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("004D7_SUMMARY",json.dumps({
       "completed":report["n_completed"],"expected":len(cases),
       "positive_new_aug_rank":sum(1 for x in rows if
           x["result"] is not None and x["result"].get("rank_increment_augmented",0)>0),
       "no_solver_calls":True},sort_keys=True),flush=True)
    if report["n_completed"]!=len(cases):
        raise AssertionError("004D7_INCOMPLETE_FROZEN_COHORT_REPORT_PRESERVED")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--child",type=Path)
    p.add_argument("--case-index",type=int)
    p.add_argument("--child-out",type=Path)
    a=p.parse_args()
    if a.child:
        if a.child_out is None or a.case_index is None:raise SystemExit("missing child options")
        child(a.child,a.case_index,a.child_out)
    else:
        if a.out is None:raise SystemExit("need --out")
        run(a.out)
