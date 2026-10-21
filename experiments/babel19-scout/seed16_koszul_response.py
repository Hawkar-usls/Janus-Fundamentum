#!/usr/bin/env python3
"""BABEL19: exact source Koszul-syzygy response to seed16 rational cokernel.

If a legal source-zero syzygy has nonzero pairing, one additional column
extends the already-proved ker(T) rank N-1 to N over Q; this establishes
existence of lifted degree-2 rational Fourier identity (NOT PSD SOS).
"""
import gzip,json,hashlib
from collections import defaultdict
from pathlib import Path
from crossbase_rank2 import setup
from janus_babel6_transfer import xor_labels
from rank2_geometry import restriction

def run():
    src,lift,labels,base_Q,Q,kernel,fibers,coord,nactive,norbits=setup(16,"SCL126_flip68")
    with gzip.open("babel19_seed16_exact_kerT_cokernel.json.gz","rt") as f:proof=json.load(f)
    h={int(i):int(v) for i,v in proof["witness"]}
    inv={i:q for q,i in coord.items()}
    print("BABEL19_COKERNEL_TWO_COORDINATES",[[inv[i],k] for i,k in h.items()],flush=True)
    src_labels,_,d=xor_labels(src)
    pi,_=restriction(src_labels,labels,d,17)
    defects=[(0,*(src_labels[j] for j in row)) for row in src]
    values={}
    for r in range(len(src)):
        for p,fiber in fibers.items():
            u=fiber[0]
            z=[u,*(u^labels[j] for j in lift[r])]
            v=sum(h.get(coord[q],0) for q in z if q in coord)
            if v:values[(r,p)]=v
    print("BABEL19_COKERNEL_SOURCE_RESPONSE_NONZERO",len(values),flush=True)
    selections=[];candidates=set()
    for (r,p),value in values.items():
        for s in range(len(src)):
            if r==s:continue
            for x in defects[s]:candidates.add((r,s,p^x))
    for r,s,t in sorted(candidates):
        if not all((t^a) in base_Q for a in defects[r]):continue
        if not all((t^a) in base_Q for a in defects[s]):continue
        response=sum(values.get((r,t^a),0) for a in defects[s])
        response-=sum(values.get((s,t^a),0) for a in defects[r])
        if not response:continue
        terms=[]
        for a in defects[s]:terms.append((r,t^a,1))
        for a in defects[r]:terms.append((s,t^a,-1))
        source_verify=defaultdict(int)
        lifted=defaultdict(int)
        for row,p,sign in terms:
            u=fibers[p][0]
            for a in defects[row]:source_verify[p^a]+=sign
            for q in (u,*(u^labels[j] for j in lift[row])):lifted[q]+=sign
        assert not any(source_verify.values())
        actual=sum(h.get(coord[q],0)*v for q,v in lifted.items() if q in coord)
        assert actual==response
        selections.append((r,s,t,response,terms,len([v for v in lifted.values() if v])))
        print("BABEL19_KOSZUL_HIT",json.dumps({"r":r,"s":s,"shift":t,"h_response":response},sort_keys=True),flush=True)
        break
    doc={"gate":"BABEL19_SEED16_SOURCE_KOSZUL_COKERNEL_REPAIR",
       "base":"SCL126_flip68","seed":16,
       "cokernel_coordinate_support":[[inv[i],k] for i,k in h.items()],
       "source_response_nonzero_coordinates":len(values),
       "searched_koszul_candidates":len(candidates),
       "source_syzygy_corrects_last_direction":bool(selections),
       "historical_degree4_rational_existence":bool(selections),
       "evidence_scope":"one source-zero Koszul witness lifts into missing kerT direction; does not generate full integer identity",
       "selected":[{"r":r,"s":s,"t":t,"response":resp,"terms":[list(x) for x in terms],"lifted_support":support}
                    for r,s,t,resp,terms,support in selections]}
    Path("babel19_seed16_koszul_response.json").write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
    print("BABEL19_KOSZUL_SUMMARY",json.dumps({k:v for k,v in doc.items() if k!="selected"},sort_keys=True),flush=True)
if __name__=="__main__":run()
