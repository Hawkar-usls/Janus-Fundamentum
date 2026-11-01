#!/usr/bin/env python3
"""TIME-SAT-004D4D: full supported-mask coverage of four SHA-pinned public CNFs.

Reuses the unchanged public 004D4B original source cohort. No SAT solver,
no P=NP, no performance claim, and no claim that implicit XOR is absent.
The 004D4C 20k index cap is preserved per page; missed supports get another
complete pass, without retaining prior support dictionaries.
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
from janus_time_sat_004d4c_bounded_support import extract_bounded_mixed_xor
from janus_time_sat_004d4d_paged_support import extract_paged_mixed_xor

FROZEN=Path("experiments/time_sat_004_external/PREREGISTERED_004D4B_PUBLIC_FOUR_MIXED_20261101.json")
ORIGINAL=Path("experiments/time_sat_004_external/time_sat_004d4b_evidence")
FROZEN_BLOB="0cbf0eee23aa77b399ad2057f113ac1e48bd8405"
CAP=20000
UNCHANGED={"xor-shifting":1643, "minimum-disagreement-parity":639,
           "binary-tree-parity":857}

def digest(path):
    h=sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(65536),b""):
            h.update(chunk)
    return h.hexdigest()

def hash_indices(indices):
    return sha256(json.dumps(indices,separators=(",",":")).encode("ascii")).hexdigest()

def execute(out):
    resource.setrlimit(resource.RLIMIT_AS,(2_147_483_648,2_147_483_648))
    resource.setrlimit(resource.RLIMIT_CPU,(12,13))
    blob=subprocess.run(["git","hash-object",str(FROZEN)],
                        text=True,capture_output=True,check=True).stdout.strip()
    if blob!=FROZEN_BLOB:
        raise AssertionError("frozen original cohort registration changed")
    cohort=json.loads(FROZEN.read_text())["candidates"]
    if [x["family"] for x in cohort]!=[
         "linear-equations","xor-shifting",
         "minimum-disagreement-parity","binary-tree-parity"]:
        raise AssertionError("frozen family identities changed")
    cases=[]
    for c in cohort:
        family=c["family"]
        src=ORIGINAL/(c["GBD_id_NOT_SHA256"]+".original.cnf")
        original_sha=digest(src)
        if original_sha!=c["decoded_CNF_SHA256"]:
            raise AssertionError("original source SHA256 mismatch "+family)
        shape=scan_dimacs(src)
        if shape!=c["original_shape"]:
            raise AssertionError("strict source DIMACS shape changed "+family)
        rows=read_cnf(src,shape["n_variables"],shape["n_clauses"],
                      max_literals=120000)
        before=perf_counter()
        prior=extract_bounded_mixed_xor(rows,shape["n_variables"],
                                        max_groups=CAP)
        prior_seconds=perf_counter()-before
        before=perf_counter()
        current=extract_paged_mixed_xor(rows,shape["n_variables"],
                                        max_groups=CAP)
        current_seconds=perf_counter()-before
        if prior["status"]!="SOURCE_PARTITION_VERIFIED" or current["status"]!="SOURCE_PARTITION_VERIFIED":
            raise AssertionError("source scan was not safe/complete "+family)
        if current["source_logical_sha256"]!=prior["source_logical_sha256"]:
            raise AssertionError("source logical checksum mismatch")
        if current["first_page_unindexed_source_clause_rows"] != prior["skipped_unindexed_source_clause_rows"]:
            raise AssertionError("paged first scan diverged from frozen 004D4C")
        if current["page_stats"][0]["xor_equations"] != prior["complete_xor_equation_count"]:
            raise AssertionError("paged first pass XOR count differs from 004D4C")
        if current["page_stats"][0]["xor_source_clauses"] != prior["source_xor_clauses"]:
            raise AssertionError("paged first pass original XOR clause count differs")
        if current["source_xor_clauses"]+current["source_residual_clauses"]!=len(rows):
            raise AssertionError("lost original clauses")
        if current["page_stats"][-1]["unindexed_rows_forwarded"]!=0:
            raise AssertionError("not all eligible support groups scanned")
        if family in UNCHANGED:
            if current["page_count"]!=1 or current["complete_xor_equation_count"]!=UNCHANGED[family]:
                raise AssertionError("previous public XOR count changed "+family)
            for field in ("xor_source_clause_indices","residual_source_clause_indices"):
                if current[field]!=prior[field]:
                    raise AssertionError("existing source clause partition regressed "+family)
        else:
            if len(rows)!=21040 or prior["skipped_unindexed_source_clause_rows"]!=1040:
                raise AssertionError("expected previously unindexed linear-equations source mismatch")
            if current["page_count"]!=2:
                raise AssertionError("linear-equations missing/extra source support scan")
        receipt={
            "family":family,
            "GBD_ID_NOT_SHA256":c["GBD_id_NOT_SHA256"],
            "original_decoded_CNF_SHA256":original_sha,
            "original_dimensions":shape,
            "logical_source_SHA256":current["source_logical_sha256"],
            "original_source_rows":len(rows),
            "first_indexed_support_limit":CAP,
            "previously_unindexed_source_clause_rows":prior["skipped_unindexed_source_clause_rows"],
            "all_supported_sign_mask_source_groups_scanned":True,
            "page_stats":current["page_stats"],
            "complete_source_XOR_equations":current["complete_xor_equation_count"],
            "source_clauses_consumed_by_XOR":current["source_xor_clauses"],
            "original_residual_clauses_retained_unchanged":current["source_residual_clauses"],
            "xor_source_indices_SHA256":hash_indices(current["xor_source_clause_indices"]),
            "original_residual_indices_SHA256":hash_indices(current["residual_source_clause_indices"]),
            "source_partition":current["status"],
            "legacy_004D4C_structural_seconds":prior_seconds,
            "new_004D4D_structural_seconds":current_seconds,
            "zero_yield_scope":"ONLY_EXPLICIT_COMPLETE_SIGN_MASK_BLOCKS_WIDTH_LE_6",
            "cannot_rule_out_implicit_or_other_encodings":True,
            "SAT_UNSAT_solver":"NOT_INVOKED",
            "production_C023":"UNCHANGED",
        }
        cases.append(receipt)
        print("004D4D_CASE",family,"pages",current["page_count"],
              "first_skipped",prior["skipped_unindexed_source_clause_rows"],
              "xor_equations",current["complete_xor_equation_count"],
              "last_remaining",current["page_stats"][-1]["unindexed_rows_forwarded"],
              flush=True)
    result={
        "schema":"JANUS-TIME-SAT-004D4D-SHA-PINNED-PAGED-FULL-SOURCE-SCAN-V1",
        "status":"SOURCE_ONLY_COMPLETE_SUPPORTED_MASK_COVERAGE_NOT_SAT_SOLVING",
        "frozen_manifest_git_blob":FROZEN_BLOB,
        "run_head":os.getenv("GITHUB_SHA","LOCAL"),
        "run_id":os.getenv("GITHUB_RUN_ID","LOCAL"),
        "source_cohort":"REUSED_PUBLIC_NOT_HIDDEN",
        "max_support_group_index_PER_PASS":CAP,
        "all_supported_groups_scanned":True,
        "independently_administered_Witness":"OPEN",
        "no_general_algorithmic_speedup_claim":True,
        "no_claim_no_implicit_XOR":True,
        "production_C023":"UNCHANGED",
        "cases":cases,
    }
    out.mkdir(parents=True,exist_ok=True)
    (out/"result.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("004D4D_SUMMARY",json.dumps({
        "sources":len(cases),
        "linear_equations_full_scanned":cases[0]["all_supported_sign_mask_source_groups_scanned"],
        "linear_equations_equations":cases[0]["complete_source_XOR_equations"],
        "linear_equations_pages":len(cases[0]["page_stats"]),
        "prior_3_regressions":0,
        "solver_runs":0,
    },sort_keys=True),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    execute(p.parse_args().out)
