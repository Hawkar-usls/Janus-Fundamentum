#!/usr/bin/env python3
"""R6 *source-only* prospective originals. No proof labels or learner is called.

The Git-blob SHA of resulting original-source-only manifest is pinned in the
R6 evaluator only after this manifest is committed, before the first eval.
Same-admin synthetic, never external blinded data.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import random
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import janus_juxtapose67_sat_xor as janus
from janus_time_sat_004d8_sat_gate import certified_model

SEEDS=(2026111661,2026111662,2026111663,2026111664)
COUNT=60
N=17
FAMILIES=(
"XOR3_TWO_BRANCH_AND_NOISE","XOR2_MULTI_BRANCH","XOR3_UNIT_GUARD",
"DIRECT_XOR3_WITH_DECOYS","PLANTED_3CNF_NEGATIVE","DUAL_XOR2_WITH_NOISE",
"TWO_XOR3_SWITCHES","XOR2_SWITCH_PLUS_DIRECT_XOR2","PLANTED_2CNF_NEGATIVE")
SCHEMA="JANUS-JUXTAPOSE-R6-240-UNSEEN-ORIGINAL-CNF-SHA-MANIFEST-V1"

def source(seed,slot):
    if seed not in SEEDS or type(slot) is not int or not 0<=slot<COUNT:
        raise ValueError("UNREGISTERED_ORIGINAL_SOURCE")
    rng=random.Random(20261115*7919+seed*101173+slot*77941)
    truth={v:bool(rng.randrange(2)) for v in range(1,N+1)}
    picked=rng.sample(list(range(1,N+1)),15)
    x,y,z=picked[:3]
    g=picked[3]
    a,b,c,d=picked[4:8]
    h=picked[8]
    kind=FAMILIES[slot%len(FAMILIES)]
    parity=lambda vs:sum(int(truth[i]) for i in vs)%2
    rows=[]
    def switched(vs,guard):
        block=janus.parity_clauses(vs,parity(vs))
        return [[guard]+row for row in block]+[[-guard]+row for row in block]
    if kind=="XOR3_TWO_BRANCH_AND_NOISE":
        rows=switched([x,y,z],g)
    elif kind=="XOR2_MULTI_BRANCH":
        rows=switched([x,y],g)+switched([a,b],h)
    elif kind=="XOR3_UNIT_GUARD":
        truth[g]=False
        rows=[[g]+row for row in janus.parity_clauses([x,y,z],parity([x,y,z]))]+[[-g]]
    elif kind=="DIRECT_XOR3_WITH_DECOYS":
        rows=janus.parity_clauses([x,y,z],parity([x,y,z]))
    elif kind=="PLANTED_3CNF_NEGATIVE":
        rows=[]
    elif kind=="DUAL_XOR2_WITH_NOISE":
        rows=switched([x,y],g)+switched([a,b],h)
    elif kind=="TWO_XOR3_SWITCHES":
        rows=switched([x,y,z],g)+switched([a,b,c],h)
    elif kind=="XOR2_SWITCH_PLUS_DIRECT_XOR2":
        rows=switched([x,y],g)+janus.parity_clauses([a,b],parity([a,b]))
    elif kind=="PLANTED_2CNF_NEGATIVE":
        rows=[]
    else:
        raise AssertionError("UNREGISTERED_FAMILY")
    noise=22 if "NEGATIVE" in kind else 16 if "NOISE" in kind else 9
    for i in range(noise):
        width=2 if kind=="PLANTED_2CNF_NEGATIVE" else 3
        vars_=rng.sample(list(range(1,N+1)),width)
        clause=[v if rng.randrange(2) else -v for v in vars_]
        if not any(truth[abs(lit)]==(lit>0) for lit in clause):
            clause[0]=-clause[0]
        rows.append(clause)
    rng.shuffle(rows)
    ordered={}
    for row in rows:
        clause=tuple(sorted(set(row),key=lambda lit:(abs(lit),lit<0)))
        if any(-lit in clause for lit in clause):
            raise AssertionError("SYNTHETIC_TAUTOLOGY")
        ordered.setdefault(clause,None)
    original=[list(row) for row in ordered]
    if not all(1<=len(c)<=4 for c in original):
        raise AssertionError("SOURCE_WIDTH_VIOLATION")
    signed=[v if truth[v] else -v for v in range(1,N+1)]
    if certified_model(original,N,signed)["status"]!="SAT_VERIFIED_EVERY_ORIGINAL_CLAUSE":
        raise AssertionError("SYNTHETIC_ORIGINAL_SAT_MODEL_INVALID")
    return {"seed":seed,"slot":slot,"family":kind,"n":N,
            "rows":original,
            "source_logical_sha256":janus.source_digest(original,N)}

def manifest():
    items=[]
    for seed in SEEDS:
        for slot in range(COUNT):
            item=source(seed,slot)
            items.append({k:item[k] for k in ("seed","slot","family","n","source_logical_sha256")})
    if len(items)!=240 or len({x["source_logical_sha256"] for x in items})!=240:
        raise AssertionError("DUPLICATE_SOURCE_OR_WRONG_COHORT_SIZE")
    return {"schema":SCHEMA,"source_count":len(items),
            "nonindependent_synthetic_development":True,
            "no_outcome_labels":True,
            "items":items}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    d=manifest()
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("JUXTAPOSE_R6_SOURCE_ONLY_MANIFEST="+json.dumps(d,sort_keys=True,separators=(",",":")))
