#!/usr/bin/env python3
"""BABEL-21 independent exact Q source syzygy replay (not a producer import).

Each source proof is re-expanded from the frozen legal row incidence and
tested against every source Fourier frequency. Its nonzero new response is
then recomputed directly on the frozen 2-cover coefficients.
"""
import argparse,json
from fractions import Fraction
from collections import defaultdict
from pathlib import Path
from crossbase_rank2 import setup
from source_kernel_probe import complement
from janus_babel6_transfer import xor_labels

def verify(seed):
    base="SCL126_flip16"
    filename=Path(f"babel21_{base}_seed{seed}_modloc_exactQ.json")
    doc=json.loads(filename.read_text())
    source,lift,cover_labels,base_Q,Q,kernel,fibers,coord,_,_=setup(seed,base)
    src_labels,src_Q,d=xor_labels(source)
    assert set(src_Q)==set(base_Q)
    hs,alphas=complement(base,seed)
    combined=[]
    for alpha in alphas:
        h=defaultdict(Fraction)
        for a,raw in zip(alpha,hs):
            for i,v in raw.items():h[i]+=a*v
        combined.append(h)
    checks=[]
    for proof in doc["verified_exact_source_syzygies"]:
        terms=proof["terms"];basefreq=defaultdict(Fraction);coverfreq=defaultdict(Fraction)
        assert len(terms)==proof["nonzero_terms"]
        for rr,u,v in terms:
            assert 0<=rr<len(source) and u in base_Q
            x=Fraction(v)
            for freq in (u,*(u^src_labels[j] for j in source[rr])):basefreq[freq]+=x
            cover_u=fibers[u][0]
            for freq in (cover_u,*(cover_u^cover_labels[j] for j in lift[rr])):
                coverfreq[freq]+=x
        assert not any(basefreq.values()),"source Fourier syzygy failed"
        response=[sum(h.get(coord.get(freq,-1),0)*v for freq,v in coverfreq.items()) for h in combined]
        assert response==[Fraction(v) for v in proof["source_response"]],"lift response mismatch"
        assert any(response),"old-syzygy response only"
        checks.append({"terms":len(terms),"nonzero_response":[str(v) for v in response],"exact_Q_replay":"PASS"})
        print("BABEL21_INDEPENDENT_SOURCE_SYZYGY_Q_PASS",seed,"terms",len(terms),flush=True)
    assert len(checks)==doc["exact_source_syzygy_response_rank"]
    outcome={"status":("BABEL21_INDEPENDENT_EXACT_Q_SOURCE_RELATION_PASS" if checks else "OPEN_NO_EXACT_SOURCE_SYZYGY"),
       "seed":seed,"base":base,"proof_count":len(checks),
       "source_Q_zero_exactly":True,"new_cover_response_independently_verified":True,
       "proofs":checks,
       "full_degree2_cover_certificate_proved":False,"P_equals_NP_proved":False}
    Path(f"babel21_{base}_seed{seed}_independent_Q_replay.json").write_text(json.dumps(outcome,indent=2,sort_keys=True)+"\n")
    print("BABEL21_INDEPENDENT_Q_SUMMARY",json.dumps({k:v for k,v in outcome.items() if k!="proofs"},sort_keys=True),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--seed",type=int,required=True)
    verify(p.parse_args().seed)
