#!/usr/bin/env python3
"""R5 original-source-SHA-only prospective test generator. No learning or labels.

All 120 source hashes are committed before training/evaluation. Internal
synthetic only, no externally blinded test set or external SAT endorsement.
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

SEEDS=(2026111591,2026111592,2026111593,2026111594)
COUNT=30
N=16
FAMILIES=("XOR3_TWO_BRANCH_SWITCH","TWO_INDEPENDENT_XOR2_SWITCH",
          "XOR3_UNIT_GUARD","DIRECT_XOR3_NOISE","PLANTED_3CNF_NO_XOR",
          "TWO_GUARDED_XOR2_WITH_NOISE","XOR2_SINGLE_GATE_WITH_NOISE",
          "XOR3_TWO_BRANCH_WITH_MANY_DECOYS")
SCHEMA="JANUS-JUXTAPOSE-R5-120-NEW-ORIGINAL-CNF-SHA-SOURCE-ONLY-V1"

def generate(seed,slot):
    if seed not in SEEDS or type(slot) is not int or not 0<=slot<COUNT:
        raise ValueError("not pre-registered")
    rng=random.Random(seed*71831+slot*62731+2903)
    truth={i:bool(rng.randrange(2)) for i in range(1,N+1)}
    selected=rng.sample(range(1,N+1),12)
    xyz=selected[:3]
    guard=selected[3]
    family=FAMILIES[slot%len(FAMILIES)]
    parity=lambda x:sum(int(truth[v]) for v in x)%2
    rows=[]
    if family in ("XOR3_TWO_BRANCH_SWITCH","XOR3_TWO_BRANCH_WITH_MANY_DECOYS"):
        base=exact.parity_clauses(xyz,parity(xyz))
        rows=[[guard]+c for c in base]+[[-guard]+c for c in base]
    elif family in ("TWO_INDEPENDENT_XOR2_SWITCH","TWO_GUARDED_XOR2_WITH_NOISE"):
        for x,g in ((selected[:2],selected[3]),(selected[5:7],selected[7])):
            base=exact.parity_clauses(x,parity(x))
            rows.extend([[g]+c for c in base]+[[-g]+c for c in base])
    elif family=="XOR3_UNIT_GUARD":
        truth[guard]=False
        base=exact.parity_clauses(xyz,parity(xyz))
        rows=[[guard]+c for c in base]+[[-guard]]
    elif family=="DIRECT_XOR3_NOISE":
        rows=exact.parity_clauses(xyz,parity(xyz))
    elif family=="XOR2_SINGLE_GATE_WITH_NOISE":
        vv=selected[1:3]
        base=exact.parity_clauses(vv,parity(vv))
        rows=[[guard]+c for c in base]+[[-guard]+c for c in base]
    elif family!="PLANTED_3CNF_NO_XOR":
        raise AssertionError("unknown family")
    decoys=(20 if family=="PLANTED_3CNF_NO_XOR"
            else 18 if family=="XOR3_TWO_BRANCH_WITH_MANY_DECOYS"
            else 12 if family.endswith("WITH_NOISE") else 8)
    for _ in range(decoys):
        vs=rng.sample(range(1,N+1),3)
        c=[v if rng.randrange(2) else -v for v in vs]
        if not any(truth[abs(l)]==(l>0) for l in c):
            c[0]=-c[0]
        rows.append(c)
    rng.shuffle(rows)
    seen={}
    for r in rows:
        c=tuple(sorted(set(r),key=lambda x:(abs(x),x<0)))
        if any(-v in c for v in c):
            raise AssertionError("tautological clause in synthetic original")
        seen.setdefault(c,None)
    original=[list(c) for c in seen]
    if not all(1<=len(c)<=4 for c in original):
        raise AssertionError("verifier source width > 4")
    witness=[i if truth[i] else -i for i in range(1,N+1)]
    if certified_model(original,N,witness)["status"]!="SAT_VERIFIED_EVERY_ORIGINAL_CLAUSE":
        raise AssertionError("original source SAT model invalid")
    return {"seed":seed,"slot":slot,"family":family,"n":N,
            "rows":original,"source_logical_sha256":exact.source_digest(original,N)}

def manifest():
    out=[]
    for seed in SEEDS:
        for slot in range(COUNT):
            f=generate(seed,slot)
            out.append({k:f[k] for k in ("seed","slot","family","n","source_logical_sha256")})
    if len(out)!=120 or len(set(x["source_logical_sha256"] for x in out))!=120:
        raise AssertionError("duplicate new original SHA")
    return {"schema":SCHEMA,"original_source_count":120,
            "no_model_labels_or_outcomes":True,
            "external_source_independence":"NO_SAME_ADMIN_SYNTHETIC",
            "items":out}

if __name__=="__main__":
    q=argparse.ArgumentParser()
    q.add_argument("--out",type=Path)
    args=q.parse_args()
    m=manifest()
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(m,sort_keys=True,indent=2)+"\n")
    print("R5_ORIGINAL_SOURCE_SHA_ONLY="+json.dumps(m,sort_keys=True,separators=(",",":")))
