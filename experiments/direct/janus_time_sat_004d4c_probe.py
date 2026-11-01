#!/usr/bin/env python3
"""004D4C source-only real-original audit; NO calls to SAT/CDCL engines.

Original inputs and SHA256 fixed by archived 004D4B dual-runner evidence.
Compare 004D4 mixed extractor vs conservative fixed-size support index:
one previous ABSTAIN_GROUP_BUDGET is inspected, other cases must be
unchanged. Store any negative/zero-yield result explicitly.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import resource
import subprocess
from time import perf_counter

from janus_time_sat_004b_acquire import scan_dimacs
from janus_time_sat_004b_baselines import read_cnf
from janus_time_sat_004d4_mixed_xor import extract_mixed_xor
from janus_time_sat_004d4c_bounded_support import extract_bounded_mixed_xor

FROZEN=Path("experiments/time_sat_004_external/PREREGISTERED_004D4B_PUBLIC_FOUR_MIXED_20261101.json")
ORIGINAL=Path("experiments/time_sat_004_external/time_sat_004d4b_evidence")
BLOB="0cbf0eee23aa77b399ad2057f113ac1e48bd8405"
CAP=20000
PROVED_COUNTS={
 "xor-shifting":1643,
 "minimum-disagreement-parity":639,
 "binary-tree-parity":857,
}
EXPECTED_OLD={"linear-equations":"ABSTAIN_GROUP_BUDGET"}
for f in PROVED_COUNTS:EXPECTED_OLD[f]="SOURCE_PARTITION_VERIFIED"

def sha(path):
    d=sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(65536),b""):d.update(b)
    return d.hexdigest()

def run(out):
    resource.setrlimit(resource.RLIMIT_AS,(2_147_483_648,2_147_483_648))
    resource.setrlimit(resource.RLIMIT_CPU,(12,13))
    blob=subprocess.run(["git","hash-object",str(FROZEN)],
        text=True,capture_output=True,check=True).stdout.strip()
    if blob!=BLOB:raise AssertionError("frozen source cohort changed")
    cohort=json.loads(FROZEN.read_text())["candidates"]
    if len(cohort)!=4:raise AssertionError("not four frozen original sources")
    cases=[]
    for c in cohort:
        name=c["family"]
        original=ORIGINAL/(c["GBD_id_NOT_SHA256"]+".original.cnf")
        if sha(original)!=c["decoded_CNF_SHA256"]:
            raise AssertionError("archived original competition SHA changed "+name)
        dims=scan_dimacs(original)
        if dims!=c["original_shape"]:
            raise AssertionError("original strict DIMACS shape changed "+name)
        rows=read_cnf(original,dims["n_variables"],dims["n_clauses"],max_literals=120000)
        start_old=perf_counter()
        old=extract_mixed_xor(rows,dims["n_variables"])
        old_s=perf_counter()-start_old
        if old["status"]!=EXPECTED_OLD[name]:
            raise AssertionError("original 004D4 result changed "+name)
        start_new=perf_counter()
        revised=extract_bounded_mixed_xor(rows,dims["n_variables"],max_groups=CAP)
        new_s=perf_counter()-start_new
        if revised["status"]!="SOURCE_PARTITION_VERIFIED":
            raise AssertionError("new algorithm failed original safe source "+name)
        if revised["source_xor_clauses"]+revised["source_residual_clauses"]!=len(rows):
            raise AssertionError("source clause partition malformed")
        # All old positives must remain byte-identical in the clause partition.
        if name in PROVED_COUNTS:
            for key in ("complete_xor_equation_count","source_xor_clauses",
                        "source_residual_clauses","xor_source_clause_indices",
                        "residual_source_clause_indices"):
                if revised[key]!=old[key]:
                    raise AssertionError("previous correct mixed XOR allocation REGRESSION "+name+" "+key)
            if revised["complete_xor_equation_count"]!=PROVED_COUNTS[name]:
                raise AssertionError("previous verified equation count changed "+name)
        case={
            "family":name,"GBD_ID_NOT_SHA256":c["GBD_id_NOT_SHA256"],
            "exact_original_CNF_SHA256":c["decoded_CNF_SHA256"],
            "source_n":dims["n_variables"],"source_original_clauses":len(rows),
            "old_status":old["status"],"old_structural_seconds":old_s,
            "new_status":revised["status"],"new_structural_seconds":new_s,
            "indexed_unique_supports":revised["indexed_unique_support_count"],
            "max_support_index":revised["indexed_support_limit"],
            "index_exhausted":revised["index_exhausted"],
            "unindexed_original_clause_rows_kept":revised["skipped_unindexed_source_clause_rows"],
            "xor_equations":revised["complete_xor_equation_count"],
            "xor_source_clauses":revised["source_xor_clauses"],
            "unaltered_residual_source_clauses":revised["source_residual_clauses"],
            "source_clause_partition_exact":"PASS",
            "SAT_or_UNSAT":"NOT_ATTEMPTED",
            "performance_win":"NOT_BENCHMARKED",
            "incomplete_index_scope":"Cannot infer source contains no XOR outside indexed supports",
        }
        cases.append(case)
        print("TIME_SAT_004D4C",name,old["status"],"=>",revised["status"],
              "equations",case["xor_equations"],
              "residual",case["unaltered_residual_source_clauses"],
              "skipped",case["unindexed_original_clause_rows_kept"],flush=True)
    data={
      "schema":"JANUS-TIME-SAT-004D4C-REAL-ORIGINAL-SUPPORT-INDEX-SAFETY-PILOT-V1",
      "original_source_corpus":"Exact SHA-pinned previously tested PUBLIC 004D4B four-CNF source",
      "sealed_hidden_holdout":"NOT_PERFORMED",
      "new_algorithm":"bounded 20000 support index; retain unindexed original clauses verbatim",
      "frozen_registration_git_blob":BLOB,
      "original_git_archive_head":"f0b9d03d4b8034b356c6c51e8e8c6e0b959eb0e7",
      "run_id":os.environ.get("GITHUB_RUN_ID","LOCAL"),
      "run_head":os.environ.get("GITHUB_SHA","LOCAL"),
      "no_solver_invocations":True,"external_independent_witness":"OPEN",
      "original_C023":"UNCHANGED","performance_or_P_equals_NP_claim":"NONE",
      "cases":cases}
    out.mkdir(parents=True,exist_ok=True)
    (out/"result.json").write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    print("TIME_SAT_004D4C_SUMMARY",json.dumps({
        "original_sources":len(cases),
        "new_complete_structural_partitions":sum(x["new_status"]=="SOURCE_PARTITION_VERIFIED" for x in cases),
        "new_linear_eq":cases[0]["xor_equations"],
        "previous_success_regressions":0,
        "solver_trials":0
    },sort_keys=True),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    run(p.parse_args().out)
