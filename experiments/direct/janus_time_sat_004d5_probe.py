#!/usr/bin/env python3
"""004D5 source-only SHA-pinned four public original CNF binary SCC experiment.

Neither an independent hidden challenge nor a performance comparison. Derive
source-entailed XOR only via original 2-CNF implication-path witnesses;
retain FULL original CNF. No solver run, no new P=NP claim.
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
from janus_time_sat_004d5_binary_scc import (
    source_proven_implied_xor,replay_equation_certificate
)
from janus_time_sat_004d4d_paged_support import extract_paged_mixed_xor

ROOT=Path("experiments/time_sat_004_external")
REG=ROOT/"PREREGISTERED_004D5_BINARY_SCC_20261101.json"
REG_BLOB="7e9c15aa9206dae147c6d318ccc8f1b9de093d78"
OLD=ROOT/"PREREGISTERED_004D4B_PUBLIC_FOUR_MIXED_20261101.json"
OLD_BLOB="0cbf0eee23aa77b399ad2057f113ac1e48bd8405"
SOURCE=ROOT/"time_sat_004d4b_evidence"
EXPECTED={"linear-equations":0,"xor-shifting":1643,
          "minimum-disagreement-parity":639,"binary-tree-parity":857}

def verify_source_blobs():
    for path,want in [(REG,REG_BLOB),(OLD,OLD_BLOB)]:
        got=subprocess.run(["git","hash-object",str(path)],
                           capture_output=True,text=True,check=True).stdout.strip()
        if got!=want:raise AssertionError("frozen source/preregister sha changed "+str(path))

def sha(path):
    h=sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<16),b""):h.update(chunk)
    return h.hexdigest()

def probe(out):
    resource.setrlimit(resource.RLIMIT_AS,(2_147_483_648,2_147_483_648))
    resource.setrlimit(resource.RLIMIT_CPU,(18,19))
    verify_source_blobs()
    frozen=json.loads(REG.read_text())
    prior=json.loads(OLD.read_text())["candidates"]
    if [x["family"] for x in prior]!=frozen["source"]["cases"]:
        raise AssertionError("not the frozen source case order")
    cases=[]
    for meta in prior:
        family=meta["family"]
        original=SOURCE/(meta["GBD_id_NOT_SHA256"]+".original.cnf")
        if sha(original)!=meta["decoded_CNF_SHA256"]:
            raise AssertionError("original source CNF sha changed "+family)
        shape=scan_dimacs(original)
        if shape!=meta["original_shape"]:
            raise AssertionError("original DIMACS shape changed "+family)
        rows=read_cnf(original,shape["n_variables"],shape["n_clauses"],
                      max_literals=120000)
        before=perf_counter()
        d=source_proven_implied_xor(rows,shape["n_variables"],max_examples=8)
        scan_seconds=perf_counter()-before
        baseline=extract_paged_mixed_xor(rows,shape["n_variables"])
        if baseline["status"]!="SOURCE_PARTITION_VERIFIED":
            raise AssertionError("source baseline equivalence safeguard failed")
        if len(baseline["equations"])!=EXPECTED[family]:
            raise AssertionError("original source baseline explicit XOR changed")
        if d["status"]=="WITNESSED_BINARY_EQUIVALENCE_PARITY_SOURCE_SCAN_PASS":
            for proof in d["sample_witnesses_original_source_replayed"]:
                if not replay_equation_certificate(rows,proof):
                    raise AssertionError("source-bound implication proof no longer valid")
        elif d["status"]!="ABSTAIN_BINARY_ONLY_SCC_CONTRADICTION_UNCERTIFIED":
            raise AssertionError("input graph unexpected error "+d["status"])
        case={
            "family":family,
            "GBD_ID_not_sha256":meta["GBD_id_NOT_SHA256"],
            "original_decoded_CNF_SHA256":meta["decoded_CNF_SHA256"],
            "original_dimensions":shape,
            "original_explicit_complete_XOR_equations":len(baseline["equations"]),
            "binary_equivalence_result":d,
            "source_only_analysis_seconds":scan_seconds,
            "original_CNF_kept_verbatim":True,
            "proof_scope":"SOURCE_ONLY_ORIGINAL_BINARY_PATH_WITNESS_NOT_DRAT_LRAT",
            "SAT_solver_calls":0,"source_purchased_external":"NO"}
        cases.append(case)
        print("004D5_SOURCE",family,d["status"],
              "original_xor",len(baseline["equations"]),
              "binary_orig",d.get("binary_original_clause_count"),
              "aliases",d.get("nontrivial_source_proven_signed_variable_aliases"),
              "new",d.get("new_implied_XOR_equations_beyond_prior_canonical_baseline"),
              "proofs",d.get("sample_count"),flush=True)
    result={
      "schema":"JANUS-TIME-SAT-004D5-SOURCE-BINARY-SCC-EQUIVALENCE-XOR-PROBE-V1",
      "source":"SHA_PINNED_FOUR_004D4B_PUBLIC_PRESEEN_CNF_NOT_HIDDEN",
      "registration_git_blob":REG_BLOB,
      "original_cohort_git_blob":OLD_BLOB,
      "run_id":os.environ.get("GITHUB_RUN_ID","LOCAL"),
      "run_head":os.environ.get("GITHUB_SHA","LOCAL"),
      "no_SAT_or_CDCL_solver_calls":True,
      "original_CNF_kept_100_percent":True,
      "any_derived_XOR_only_redundant_consequence_of_original_binary_clauses":True,
      "portable_external_Witness":"OPEN",
      "end_to_end_speedup":"NOT_MEASURED",
      "C023_and_main":"UNCHANGED",
      "cases":cases}
    out.mkdir(parents=True,exist_ok=True)
    (out/"result.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("004D5_SUMMARY",json.dumps({x["family"]: {
        "status":x["binary_equivalence_result"]["status"],
        "extra":x["binary_equivalence_result"].get(
            "new_implied_XOR_equations_beyond_prior_canonical_baseline",None),
        "source_verified_examples":x["binary_equivalence_result"].get("sample_count",0)
        } for x in cases},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    probe(p.parse_args().out)
