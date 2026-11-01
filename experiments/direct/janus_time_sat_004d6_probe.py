#!/usr/bin/env python3
"""004D6 four original SHA-pinned public CNFs: bounded source-only resolution.

No SAT engines, no benchmark, no hidden test claim. Verify each positive proof
via separate replay code; retain negative findings and truncation unchanged.
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
from janus_time_sat_004d6_bounded_resolution import source_derived_xor
from janus_time_sat_004d6_replay import replay_all

ROOT=Path("experiments/time_sat_004_external")
REG=ROOT/"PREREGISTERED_004D6_BOUNDED_RESOLUTION_20261102.json"
REG_BLOB="150d16f6cc90551afba81e964adc09ad0fe7c032"
SOURCE_REG=ROOT/"PREREGISTERED_004D4B_PUBLIC_FOUR_MIXED_20261101.json"
SOURCE_BLOB="0cbf0eee23aa77b399ad2057f113ac1e48bd8405"
PRIOR_REG=ROOT/"PREREGISTERED_004D5_BINARY_SCC_20261101.json"
PRIOR_BLOB="7e9c15aa9206dae147c6d318ccc8f1b9de093d78"
SOURCE=ROOT/"time_sat_004d4b_evidence"
PRIOR_BASE={"linear-equations":0,"xor-shifting":1643,
            "minimum-disagreement-parity":639,"binary-tree-parity":857}
FAMILIES=list(PRIOR_BASE)

def path_sha(path):
    h=sha256()
    with path.open("rb") as fd:
        for chunk in iter(lambda:fd.read(65536),b""):
            h.update(chunk)
    return h.hexdigest()

def verify_registration():
    for path,expected in [(REG,REG_BLOB),(SOURCE_REG,SOURCE_BLOB),
                          (PRIOR_REG,PRIOR_BLOB)]:
        got=subprocess.run(["git","hash-object",str(path)],
                           text=True,capture_output=True,check=True).stdout.strip()
        if got!=expected:
            raise AssertionError("frozen registered source/blob changed "+str(path))
    j=json.loads(REG.read_text())
    b=j["frozen_budgets"]
    exact={
      "max_antecedent_clause_width":4,"max_derived_clause_width":4,
      "max_pivots_per_round":128,"max_positive_parents_per_pivot":8,
      "max_negative_parents_per_pivot":8,"max_pairs_per_pivot":64,
      "max_total_new_resolvents":2000,"max_rounds":2,"max_new_xor_witnesses":8
    }
    if any(b[k]!=value for k,value in exact.items()):
        raise AssertionError("004D6 fixed budget changed")
    if j["source_cases"]!=FAMILIES:
        raise AssertionError("004D6 original cohort selection changed")

def probe(out):
    resource.setrlimit(resource.RLIMIT_AS,(2_147_483_648,2_147_483_648))
    resource.setrlimit(resource.RLIMIT_CPU,(18,19))
    verify_registration()
    candidates=json.loads(SOURCE_REG.read_text())["candidates"]
    if [c["family"] for c in candidates]!=FAMILIES:
        raise AssertionError("not original four source files")
    cases=[]
    for m in candidates:
        name=m["family"]
        path=SOURCE/(m["GBD_id_NOT_SHA256"]+".original.cnf")
        if path_sha(path)!=m["decoded_CNF_SHA256"]:
            raise AssertionError("original source SHA mismatch "+name)
        shape=scan_dimacs(path)
        if shape!=m["original_shape"]:
            raise AssertionError("original DIMACS dimensions changed "+name)
        rows=read_cnf(path,shape["n_variables"],shape["n_clauses"],
                      max_literals=120000)
        start=perf_counter()
        proof=source_derived_xor(rows,shape["n_variables"])
        seconds=perf_counter()-start
        if proof["status"]!="SOURCE_RESOLUTION_BOUNDED_PASS":
            raise AssertionError("unexpected source scan abstain "+name+":"+proof["status"])
        if proof["original_explicit_xor_equations"]!=PRIOR_BASE[name]:
            raise AssertionError("prior certified explicit XOR changed "+name)
        if not replay_all(rows,shape["n_variables"],proof):
            raise AssertionError("original-source resolution replay FAILED "+name)
        receipts={
            "family":name,
            "GBD_ID_NOT_SHA256":m["GBD_id_NOT_SHA256"],
            "original_decoded_CNF_SHA256":m["decoded_CNF_SHA256"],
            "original_dimensions":shape,
            "scan_elapsed_seconds_NOT_BENCHMARK":seconds,
            "proof_validation":"ALL_RESOLUTION_STEPS_AND_ALL_NEW_PARITY_MASKS_SOURCE_REPLAY_PASS",
            "new_resolvents":proof["total_new_resolvents"],
            "new_complete_XOR_equations_beyond_explicit_source":proof["new_complete_xor_sign_mask_equations"],
            "truncated_by_total_resolvent_budget":proof["truncated_by_total_resolvent_cap"],
            "round_stats":proof["round_stats"],
            "report_scope":"REUSED_PUBLIC_SOURCE_BOUNDED_CLASSICAL_RESOLUTION_NOT_ALL_IMPLIED_XOR",
            "source_original_clauses_unchanged":True,
            "original_CNF_SAT_UNSAT":"NOT_SOLVED",
            "evidence":proof,
        }
        cases.append(receipts)
        print("004D6_REAL_SOURCE",name,"new_resolvents",
              receipts["new_resolvents"],"new_xor",
              receipts["new_complete_XOR_equations_beyond_explicit_source"],
              "rounds",len(proof["round_stats"]),"replay",receipts["proof_validation"],
              flush=True)
    result={
        "schema":"JANUS-TIME-SAT-004D6-FOUR-ORIGINAL-BOUNDED-RESOLUTION-V1",
        "registration_git_blob":REG_BLOB,
        "original_source_manifest_git_blob":SOURCE_BLOB,
        "run_id":os.getenv("GITHUB_RUN_ID","LOCAL"),
        "run_head":os.getenv("GITHUB_SHA","LOCAL"),
        "scope":"PREVIOUSLY_USED_PUBLIC_COMPETITION_SOURCES_NOT_HIDDEN",
        "no_solver_or_benchmark":True,
        "source_original_clause_SAT_model":"NOT_REQUESTED",
        "source_CNF_unmodified":True,
        "separate_same_admin_certificate_checker":True,
        "independent_admin_Witness":"OPEN",
        "production_C023":"UNCHANGED",
        "cases":cases
    }
    out.mkdir(parents=True,exist_ok=True)
    (out/"result.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("004D6_SUMMARY",json.dumps({
       "original_sources":len(cases),
       "total_derived_resolvents":sum(c["new_resolvents"] for c in cases),
       "total_new_full_source_implied_XOR":sum(
           c["new_complete_XOR_equations_beyond_explicit_source"] for c in cases),
       "original_source_replays":len(cases),
       "SAT_solver_trials":0
    },sort_keys=True),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    probe(p.parse_args().out)
