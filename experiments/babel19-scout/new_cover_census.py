#!/usr/bin/env python3
"""BABEL-19 structurally diversified connected SCL-cover exact SAT census.

Compares independent source incidence matrices and new signing seeds. Exact SAT
count uses GF(2) kernel Gray-code, never inferred from source UNSAT status.
Scientific scope: new fixtures/discovery only; no rational SOS certificates.
"""
import hashlib,json
from collections import Counter
from pathlib import Path
from janus_babel10_degree_scan import frozen_instances
from janus_babel10_lift_family import make_lift
from janus_babel6_transfer import xor_labels,assert_valid_double_cover
from janus_occam_solver import gf2_kernel,validate

def connected(rows):
    n=len(rows); bycol=[[] for _ in range(n)]
    for r,row in enumerate(rows):
        for j in row:bycol[j].append(r)
    seen_rows={0};seen_cols=set();stack=[(0,0)]
    while stack:
        t,v=stack.pop()
        if t==0:
            for j in rows[v]:
                if j not in seen_cols:
                    seen_cols.add(j);stack.append((1,j))
        else:
            for r in bycol[v]:
                if r not in seen_rows:
                    seen_rows.add(r);stack.append((0,r))
    return len(seen_rows)==len(rows) and len(seen_cols)==len(rows)

def exact_sat_count(rows):
    n=len(rows)
    _,basis=gf2_kernel(validate(rows,n),n)
    d=len(basis)
    assert d<=20,"pre-registered exact enumeration budget"
    target=2*n//3
    word=0;count=0
    for mask in range(1<<d):
        if mask:
            idx=(mask&-mask).bit_length()-1
            word^=basis[idx]
        if word.bit_count()==target:count+=1
    return d,count

def audit():
    frozen=frozen_instances()
    selected=[name for name in ("SCL63","SCL126_flip16","SCL126_flip68") if name in frozen]
    assert len(selected)>=2,(selected,list(frozen))
    output=[];sets=set()
    for base in selected:
        source=frozen[base]
        for seed in (6,11,19):
            lift=make_lift(source,seed)[0]
            assert_valid_double_cover(source,lift)
            c=connected(lift)
            assert c
            nullity,sat=exact_sat_count(lift)
            sha=hashlib.sha256(json.dumps(lift,sort_keys=True,separators=(",",":")).encode()).hexdigest()
            assert sha not in sets,(base,seed)
            sets.add(sha)
            record={"source":base,"seed":seed,"source_size":len(source),
                   "cover_n":len(lift),"cover_nullity":nullity,
                   "exact_kernel_states":1<<nullity,
                   "exact_sat_count":sat,"unsat_exact":sat==0,
                   "connected_incidence":True,"legal_cubic_linear":True,
                   "incidence_sha256":sha}
            print("BABEL19_NEW_COVER",json.dumps(record,sort_keys=True),flush=True)
            output.append(record)
    assert len(output)==len(selected)*3
    print("BABEL19_COVER_SUMMARY",json.dumps({"instances":len(output),
         "unsat":sum(r["unsat_exact"] for r in output),
         "sat":sum(not r["unsat_exact"] for r in output),
         "distinct_sources":len(selected)},sort_keys=True),flush=True)
    Path("babel19_new_source_cover_census.json").write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
if __name__=="__main__":audit()
