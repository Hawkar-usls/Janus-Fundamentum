#!/usr/bin/env python3
"""TIME-SAT-004D6R: post-hoc *rank diagnostic* of already frozen 004D6.

Derived XORs may be redundant linear combinations of earlier source XORs.
This reads original immutable source and original 004D6 proof, independently
regenerates every width<=4 complete mask group, and computes exact GF(2)
coefficient/augmented rank change. Post-hoc, not a new blind holdout or
performance evidence. No SAT solver.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import sys

from janus_time_sat_004b_acquire import scan_dimacs
from janus_time_sat_004b_baselines import read_cnf
from janus_time_sat_004d4d_paged_support import extract_paged_mixed_xor
from janus_time_sat_004d6_replay import replay_all

ROOT=Path("experiments/time_sat_004_external")
ARCHIVE=ROOT/"time_sat_004d6_evidence"/"original-ubuntu22.json"
PARENT=ROOT/"time_sat_004d4b_evidence"
REG=ROOT/"PREREGISTERED_004D4B_PUBLIC_FOUR_MIXED_20261101.json"
EXPECTED={"linear-equations":0,"xor-shifting":169,
          "minimum-disagreement-parity":0,"binary-tree-parity":164}


def digest(blob):
    return sha256(blob).hexdigest()


def canon(row):
    s=set(row)
    if any(-x in s for x in s):return None
    return tuple(sorted(s,key=lambda v:(abs(v),v<0)))


def ranks(equations,n):
    """Return exact variable-space and augmented-space GF2 ranks."""
    a={};b={}
    def place(row,base):
        while row:
            pivot=row.bit_length()-1
            if pivot not in base:
                base[pivot]=row
                return
            row^=base[pivot]
    for vs,rhs in equations:
        x=0
        for v in vs:x^=1<<(v-1)
        place(x,a)
        place(x|((rhs&1)<<n),b)
    return len(a),len(b)


def derive_keys(rows,n,evidence,known):
    table={}
    m=len(rows)
    for i,c in enumerate(rows):
        if 1<=len(c)<=4:
            cc=canon(c)
            if cc is not None:table[i]=cc
    for step in evidence["resolution_proof_DAG"]:
        table[step["id"]]=tuple(step["clause"])
    group=defaultdict(set)
    original=defaultdict(set)
    for i,c in table.items():
        if not 1<=len(c)<=4:continue
        vs=tuple(sorted(abs(v) for v in c))
        if len(set(vs))!=len(c):continue
        mask=sum(1<<k for k,v in enumerate(vs) if -v in c)
        group[vs].add(mask)
        if i<m:original[vs].add(mask)
    newly=set()
    for vs,masks in group.items():
        for p in (0,1):
            want={mask for mask in range(1<<len(vs)) if mask.bit_count()%2==p}
            key=(vs,1^p)
            if want.issubset(masks) and not want.issubset(original[vs]) and key not in known:
                newly.add(key)
    return newly


def run(out):
    items=json.loads(REG.read_text())["candidates"]
    data=json.loads(ARCHIVE.read_text())
    if len(data["cases"])!=4:raise AssertionError("original source archived case count")
    cases=[]
    for meta,receipt in zip(items,data["cases"]):
        family=meta["family"]
        if family!=receipt["family"]:raise AssertionError("source order mismatch")
        src=PARENT/(meta["GBD_id_NOT_SHA256"]+".original.cnf")
        if digest(src.read_bytes())!=meta["decoded_CNF_SHA256"]:
            raise AssertionError("original source SHA invalid "+family)
        shape=scan_dimacs(src)
        if shape!=meta["original_shape"]:
            raise AssertionError("source shape invalid")
        n=shape["n_variables"]
        rows=read_cnf(src,n,shape["n_clauses"],max_literals=120000)
        ev=receipt["evidence"]
        if not replay_all(rows,n,ev):
            raise AssertionError("original entire resolution DAG invalid "+family)
        explicit=extract_paged_mixed_xor(rows,n)
        if explicit["status"]!="SOURCE_PARTITION_VERIFIED":
            raise AssertionError("original explicit XOR invalid")
        known={(tuple(x["variables"]),x["rhs"]) for x in explicit["equations"]}
        new=derive_keys(rows,n,ev,known)
        if len(new)!=ev["new_complete_xor_sign_mask_equations"] or len(new)!=EXPECTED[family]:
            raise AssertionError("new parity key count changed "+family)
        rank0,aug0=ranks(known,n)
        rank1,aug1=ranks(known|new,n)
        cases.append({
            "family":family,
            "original_source_SHA256":meta["decoded_CNF_SHA256"],
            "explicit_source_XOR_equations":len(known),
            "derived_additional_XOR_keys":len(new),
            "variable_coefficient_rank_before":rank0,
            "variable_coefficient_rank_after":rank1,
            "variable_coefficient_rank_increment":rank1-rank0,
            "augmented_GF2_rank_before":aug0,
            "augmented_GF2_rank_after":aug1,
            "augmented_GF2_rank_increment":aug1-aug0,
            "original_explicit_GF2_already_inconsistent":aug0>rank0,
            "new_derived_GF2_inconsistent_after":aug1>rank1,
            "rank_interpretation":"Linear independence ONLY relative to explicit source XOR equations, not proof of SAT speedup.",
            "all_source_resolution_proofs_replayed_again":"PASS",
        })
        print("004D6R_RANK",family,"new_keys",len(new),
              "coefficient_increment",rank1-rank0,
              "augmented_increment",aug1-aug0,flush=True)
    payload={
      "schema":"JANUS-TIME-SAT-004D6R-POSTHOC-GF2-INDEPENDENCE-DIAGNOSTIC-V1",
      "source_original_CI":41355380127,
      "source_original_HEAD":"f191948ae9c0b5bf20420d57afdbcfdc35b72592",
      "scope":"POST_HOC_ANALYSIS_OF_ALREADY_SEEN_PUBLIC_SOURCE_NO_BLIND_CLAIM",
      "source_original_archive":"experiments/time_sat_004_external/time_sat_004d6_evidence/summary.json",
      "original_bounded_resolution_limit_unchanged":True,
      "no_solvers_or_performance_comparison":True,
      "external_independent_Witness":"OPEN",
      "production_C023":"UNCHANGED",
      "cases":cases
    }
    out.mkdir(parents=True,exist_ok=True)
    (out/"rank.json").write_text(json.dumps(payload,sort_keys=True,indent=2)+"\n")
    print("004D6R_SUMMARY",json.dumps({
      "source_cases":len(cases),
      "new_parity_representations":sum(c["derived_additional_XOR_keys"] for c in cases),
      "incremental_coefficient_rank":sum(c["variable_coefficient_rank_increment"] for c in cases),
      "incremental_augmented_rank":sum(c["augmented_GF2_rank_increment"] for c in cases)
    },sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    run(p.parse_args().out)
