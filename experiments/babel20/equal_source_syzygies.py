#!/usr/bin/env python3
"""BABEL20 independent equal-source-column syzygy response supplement.

Exact-Q image of source-generator equalities, combined with independently
verified Koszul responses. Positive full rank is a sufficient existence proof.
Incomplete rank says NOTHING about full degree4 impossibility.
"""
import argparse,gzip,json
from pathlib import Path
from collections import defaultdict
from crossbase_rank2 import setup
from exact_cokernel import SmallElimination
from janus_babel6_transfer import xor_labels

def audit(base,seed):
    with gzip.open(f"babel20_{base}_seed{seed}_exact_Q_cokernel.json.gz","rt") as f:cok=json.load(f)
    hs=[{int(i):int(v) for i,v in h} for h in cok["exact_rational_annihilators"]]
    m=len(hs)
    ks=json.loads(Path(f"babel20_{base}_seed{seed}_koszul.json").read_text())
    src,lift,labels,base_Q,Q,kernel,fibers,coord,_,_=setup(seed,base)
    q_src,srcq,ds=xor_labels(src)
    assert set(srcq)==set(base_Q)
    basis=SmallElimination(m)
    for item in ks["selected"]:
        assert basis.add(item["response"],["KOSZUL",item["r"],item["s"],item["t"]])
    initial_rank=len(basis.selected)
    rep={};collisions=0;nonzero=0;selected=[]
    for r,row in enumerate(src):
        srcdef=[q_src[j] for j in row]
        liftdef=[labels[j] for j in lift[r]]
        for p in sorted(base_Q):
            key=tuple(sorted((p,*(p^a for a in srcdef))))
            u=fibers[p][0]
            chars=(u,*(u^a for a in liftdef))
            response=tuple(sum(h.get(coord[q],0) for q in chars if q in coord) for h in hs)
            if key not in rep:
                rep[key]=(r,p,response)
                continue
            collisions+=1
            s,v,sv=rep[key]
            delta=[response[j]-sv[j] for j in range(m)]
            if not any(delta):continue
            nonzero+=1
            assert key==tuple(sorted((v,*(v^a for a in [q_src[j] for j in src[s]]))))
            if basis.add(delta,["EQUAL_SOURCE_COLUMNS",s,v,r,p]):
                selected.append({"rowA":s,"source_uA":v,"rowB":r,"source_uB":p,
                                 "source_signature":list(key),"response":delta})
                print("BABEL20_EQUAL_SYZYGY_NEW_PIVOT",base,seed,len(basis.selected),"of",m,flush=True)
    report={"gate":"BABEL20_EQUAL_COLUMN_PLUS_KOSZUL",
       "base":base,"seed":seed,"cokernel_dim":m,
       "koszul_Q_rank":initial_rank,
       "source_generator_fingerprints":len(rep),
       "exact_equal_source_collisions":collisions,
       "nonzero_equal_column_anti_responses":nonzero,
       "combined_independent_Q_rank":len(basis.selected),
       "all_cokernel_directions_filled":len(basis.selected)==m,
       "new_equal_column_witnesses":selected,
       "scope":"Positive full span only; missing directions do not prove full degree4 nonmembership."}
    path=Path(f"babel20_{base}_seed{seed}_combined_syzygies.json")
    path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("BABEL20_EQUAL_RESULT",json.dumps({k:v for k,v in report.items() if k!="new_equal_column_witnesses"},sort_keys=True),flush=True)
    return report
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--base",required=True);ap.add_argument("--seed",type=int,required=True)
    args=ap.parse_args();audit(args.base,args.seed)
