#!/usr/bin/env python3
"""BABEL-17 exact combined source-zero image of two syzygy families."""
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from janus_babel17_syzygy import solve
from janus_babel14_antisector_augmented import prepare
from janus_babel6_transfer import make_projection
from janus_babel8_krylov_verify import input_data

def run():
    a=json.loads(Path("babel17_SEED3_SYZYGY_COMPATIBILITY.json").read_text())
    b=json.loads(Path("babel17_SEED3_KOSZUL_COMPATIBILITY.json").read_text())
    seven=a["invisible_frequencies"]
    assert seven==b["seven_invisible_frequencies"]
    target=[int(a["canonical_residual_cancel_target"][str(q)]) for q in seven]
    cols=[]
    for w in a["selected_source_syzygies"]:
        cols.append({"family":"EQUAL_COLUMNS","terms":[[w["r"],w["u"],1],[w["s"],w["v"],-1]],"signature":w["signature"]})
    for w in b["basis_witnesses"]:
        cols.append({"family":"KOSZUL","terms":w["source_zero_terms"],"signature":w["signature"]})
    echelon=[];basis=[]
    for c in cols:
        v=[Fraction(z) for z in c["signature"]]
        for pivot,bv in echelon:
            if v[pivot]:
                scale=v[pivot];v=[x-scale*y for x,y in zip(v,bv)]
        p=next((j for j,z in enumerate(v) if z),None)
        if p is not None:
            scale=v[p];echelon.append((p,[z/scale for z in v]))
            basis.append(c)
    x=solve([[w["signature"][i] for w in basis] for i in range(7)],target)
    rows,src_labels,_,_,_=input_data(68)
    _,lift,labels,Q,e,canonical,*_=prepare(3)
    pi,_=make_projection(src_labels,labels,15,16)
    for w in basis:
        assert all(u in Q for _,u,_ in w["terms"])
        image=defaultdict(int)
        lifted=[0]*7
        for r,u,k in w["terms"]:
            for src in (pi(u),*(pi(u)^src_labels[a] for a in rows[r])):
                image[src]+=k
            for z in (u,*(u^labels[a] for a in lift[r])):
                q,sgn=canonical(z)
                if q in seven:lifted[seven.index(q)]+=k*sgn
        assert not any(image.values()),"source syzygy validation"
        assert lifted==list(w["signature"]),"seven lift signature invalid"
    witness=[]
    for j,w in enumerate(basis):
        witness.append({**w,"exact_coefficient":str(x[j]) if x is not None else None})
    out={"gate":"BABEL17_COMBINED_SYZYGY_COMPATIBILITY","seed":3,
         "seven_invisible_frequencies":seven,"rank_exact":len(basis),
         "target_in_exact_span":x is not None,"basis":witness,
         "scientific_scope":"Only seven-frequency source-syzygy compatibility, not SOS4 full identity."}
    Path("babel17_SEED3_COMBINED_COMPATIBILITY.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("BABEL17_COMBINED_SUMMARY",json.dumps({"rank":len(basis),"target_in_span":x is not None,
               "families":[w["family"] for w in witness],
               "selected_nonzero_corrections":sum(bool(z) for z in x) if x is not None else None},
               sort_keys=True),flush=True)
    return out
if __name__=="__main__":run()
