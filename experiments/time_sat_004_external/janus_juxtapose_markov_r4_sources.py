#!/usr/bin/env python3
"""Source-only manifest for JUXTAPOSE x Markov R4. Never inspect XOR outcomes.

120 new planted-SAT original CNFs are frozen by their canonical source digests
before any trained Markov experiment. Same-admin synthetic, not external blind.
"""
from __future__ import annotations
import argparse,json,random,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import janus_juxtapose67_sat_xor as janus
from janus_time_sat_004d8_sat_gate import certified_model
SEEDS=(2026111551,2026111552,2026111553,2026111554)
COUNT=30
N=15
FAMILIES=("XOR3_TWO_BRANCH_SWITCH","TWO_INDEPENDENT_XOR2_SWITCH",
          "XOR3_UNIT_GUARD","DIRECT_XOR3_NOISE",
          "PLANTED_3CNF_NO_XOR","TWO_GUARDED_XOR2_WITH_NOISE")
SCHEMA="JANUS-JUXTAPOSE-MARKOV-R4-120-SOURCE-SHA-MANIFEST-V1"

def generate(seed,slot):
    if seed not in SEEDS or type(slot) is not int or not 0<=slot<COUNT:
        raise ValueError("Not a preregistered seed/slot")
    rng=random.Random(seed*17321 + slot*14879+411)
    truth={k:bool(rng.randrange(2)) for k in range(1,N+1)}
    names=rng.sample(range(1,N+1),11)
    xyz=names[:3]
    guard=names[3]
    rest=names[4:]
    kind=FAMILIES[slot%len(FAMILIES)]
    parity=lambda vs:sum(int(truth[v]) for v in vs)%2
    rows=[]
    if kind=="XOR3_TWO_BRANCH_SWITCH":
        core=janus.parity_clauses(xyz,parity(xyz))
        rows=[[guard]+c for c in core]+[[-guard]+c for c in core]
    elif kind=="TWO_INDEPENDENT_XOR2_SWITCH":
        for pair,g in ((names[:2],guard),(names[5:7],names[7])):
            core=janus.parity_clauses(pair,parity(pair))
            rows.extend([[g]+c for c in core]+[[-g]+c for c in core])
    elif kind=="XOR3_UNIT_GUARD":
        truth[guard]=False
        core=janus.parity_clauses(xyz,parity(xyz))
        rows=[[guard]+c for c in core]+[[-guard]]
    elif kind=="DIRECT_XOR3_NOISE":
        rows=janus.parity_clauses(xyz,parity(xyz))
    elif kind=="TWO_GUARDED_XOR2_WITH_NOISE":
        for pair,g in ((names[:2],guard),(names[5:7],names[7])):
            core=janus.parity_clauses(pair,parity(pair))
            rows.extend([[g]+c for c in core]+[[-g]+c for c in core])
    elif kind!="PLANTED_3CNF_NO_XOR":
        raise AssertionError("unknown preregistered family")
    count=19 if kind=="PLANTED_3CNF_NO_XOR" else (11 if kind.endswith("WITH_NOISE") else 7)
    for _ in range(count):
        vs=rng.sample(range(1,N+1),3)
        row=[v if rng.randrange(2) else -v for v in vs]
        if not any(truth[abs(l)]==(l>0) for l in row):
            row[0]=-row[0]
        rows.append(row)
    rng.shuffle(rows)
    d={}
    for row in rows:
        t=tuple(sorted(set(row),key=lambda l:(abs(l),l<0)))
        if any(-l in t for l in t):
            raise AssertionError("unexpected tautology")
        d.setdefault(t,None)
    original=[list(row) for row in d]
    if any(not 1<=len(row)<=4 for row in original):
        raise AssertionError("Original width incompatible with fixed independent replay")
    signed=[v if truth[v] else -v for v in range(1,N+1)]
    if certified_model(original,N,signed)["status"]!="SAT_VERIFIED_EVERY_ORIGINAL_CLAUSE":
        raise AssertionError("bad planted model")
    return {"seed":seed,"slot":slot,"family":kind,"n":N,"rows":original,
            "source_logical_sha256":janus.source_digest(original,N)}

def manifest():
    items=[]
    for seed in SEEDS:
        for slot in range(COUNT):
            x=generate(seed,slot)
            items.append({k:x[k] for k in ("seed","slot","family","n","source_logical_sha256")})
    if len(items)!=120 or len({x["source_logical_sha256"] for x in items})!=120:
        raise AssertionError("Nonunique original CNF source hashes")
    return {"schema":SCHEMA,"source_count":len(items),
            "source_type":"SYNTHETIC_SHA_ONLY_NO_MODEL_LABELS",
            "scientific_independence":"NOT_EXTERNAL",
            "items":items}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    result=manifest()
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("MARKOV_R4_SOURCE_ONLY_MANIFEST="+json.dumps(result,sort_keys=True,separators=(",",":")))
if __name__=="__main__":
    main()
