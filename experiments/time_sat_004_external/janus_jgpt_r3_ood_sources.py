#!/usr/bin/env python3
"""R3 source-only prospective OOD generator. NO neural, labels or test outcomes.

A complete list of original SHA256 identifiers must be generated, independently
frozen in Git, and bound by its immutable Git blob BEFORE neural evaluation.
Synthetic same-admin source selection is NOT independent external custody.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import random
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import janus_juxtapose67_sat_xor as exact
from janus_time_sat_004d8_sat_gate import certified_model

SEEDS=(2026111511,2026111512,2026111513)
FAMILIES=("XOR3_SWITCH_DIVERSE","TWO_GUARDED_XOR2",
          "XOR3_GUARDED_WITH_UNIT","DIRECT_XOR3_WITH_NOISE",
          "PLANTED_3CNF_NEGATIVE")
N=14
COUNT=22
SCHEMA="JANUS-JGPT-R3-COLD-FIRST-VERIFIED-HIT-EXACT-CNF-MANIFEST-V1"

def generate(seed,slot):
    if seed not in SEEDS or not 0<=slot<COUNT:
        raise ValueError("source not pre-registered")
    rng=random.Random(seed*99991+slot*67421+701)
    truth={v:bool(rng.randrange(2)) for v in range(1,N+1)}
    kind=FAMILIES[slot%len(FAMILIES)]
    selected=rng.sample(range(1,N+1),8)
    xyz=selected[:3]
    guard=selected[3]
    spare=selected[4:]
    par=lambda vs:sum(int(truth[v]) for v in vs)&1
    rows=[]
    if kind=="XOR3_SWITCH_DIVERSE":
        base=exact.parity_clauses(xyz,par(xyz))
        rows=[[guard]+r for r in base]+[[-guard]+r for r in base]
    elif kind=="TWO_GUARDED_XOR2":
        for pair,g in ((selected[:2],guard),(selected[4:6],spare[-1])):
            rhs=par(pair)
            base=exact.parity_clauses(pair,rhs)
            rows += [[g]+r for r in base]+[[-g]+r for r in base]
    elif kind=="XOR3_GUARDED_WITH_UNIT":
        truth[guard]=False
        base=exact.parity_clauses(xyz,par(xyz))
        rows=[[guard]+r for r in base]+[[-guard]]
    elif kind=="DIRECT_XOR3_WITH_NOISE":
        rows=exact.parity_clauses(xyz,par(xyz))
    elif kind!="PLANTED_3CNF_NEGATIVE":
        raise AssertionError("unregistered OOD family")
    # Independently sampled negative controls / decoys with planted true model.
    for k in range(7 if kind!="PLANTED_3CNF_NEGATIVE" else 15):
        vv=rng.sample(range(1,N+1),3)
        r=[v if rng.randrange(2) else -v for v in vv]
        if not any(truth[abs(l)]==(l>0) for l in r):
            r[0]=-r[0]
        rows.append(r)
    rng.shuffle(rows)
    dedupe={}
    for row in rows:
        c=tuple(sorted(set(row),key=lambda x:(abs(x),x<0)))
        dedupe.setdefault(c,None)
    rows=[list(x) for x in dedupe]
    assert all(1<=len(c)<=4 for c in rows)
    signed=[v if truth[v] else -v for v in range(1,N+1)]
    if certified_model(rows,N,signed)["status"]!="SAT_VERIFIED_EVERY_ORIGINAL_CLAUSE":
        raise AssertionError("Invalid original planted SAT model")
    digest=exact.source_digest(rows,N)
    return {"seed":seed,"slot":slot,"family":kind,"n":N,
            "rows":rows,"source_logical_sha256":digest}

def manifest():
    samples=[]
    for seed in SEEDS:
        for slot in range(COUNT):
            r=generate(seed,slot)
            samples.append({k:r[k] for k in ("seed","slot","family","n","source_logical_sha256")})
    if len(samples)!=66 or len({r["source_logical_sha256"] for r in samples})!=66:
        raise AssertionError("Reused source original in sealed synthetic cohort")
    return {"schema":SCHEMA,
            "source_sampling":"synthetic deterministic seeded original CNF precommitted before labels; not external independent",
            "source_family_count":len(FAMILIES),
            "source_variables":N,
            "train_labels_and_model_results":"NONE_INCLUDED",
            "source_count":66,
            "samples":samples}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    o=manifest()
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(o,sort_keys=True,indent=2)+"\n")
    print("JGPT_R3_SOURCE_ONLY_MANIFEST="+json.dumps(o,sort_keys=True,separators=(",",":")))
if __name__=="__main__":
    main()
