#!/usr/bin/env python3
"""BABEL-21 independent exact-Q verifier of GENERAL source-ker(A) syzygies.

Does not import producer; re-expands every source and cover Fourier generator
and checks the certificate. Independently checks rank over Q jointly with
the pre-verified Koszul/equal-column source responses.
"""
import argparse,json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from crossbase_rank2 import setup
from janus_babel6_transfer import xor_labels
from source_kernel_probe import complement
from exact_cokernel import SmallElimination

def verify(seed):
    base="SCL126_flip16"
    path=Path(f"babel21_{base}_seed{seed}_exact_source_syzygies.json")
    srcdoc=json.loads(path.read_text())
    source,cover,clabels,base_Q,Q,kernel,fibers,coord,_,_=setup(seed,base)
    slabels,sQ,d=xor_labels(source)
    assert set(sQ)==set(base_Q)
    hs,alpha=complement(base,seed)
    assert len(alpha)==srcdoc["unexplained_Q_response_dim"]
    funcs=[]
    for vec in alpha:
        h=defaultdict(Fraction)
        for factor,witness in zip(vec,hs):
            if factor:
                for i,v in witness.items():h[i]+=factor*v
        funcs.append({k:v for k,v in h.items() if v})
    span=SmallElimination(len(alpha))
    verified=[]
    for cert in srcdoc["exact_certificates"]:
        terms=cert["coefficients"]
        assert len(terms)==cert["nonzero_terms"]>0
        base_freq=defaultdict(Fraction)
        cover_freq=defaultdict(Fraction)
        for r,u,value in terms:
            assert 0<=r<len(source) and u in base_Q
            x=Fraction(value)
            assert x
            for q in (u,*(u^slabels[j] for j in source[r])):
                base_freq[q]+=x
            lift_u=fibers[u][0]
            for q in (lift_u,*(lift_u^clabels[j] for j in cover[r])):
                cover_freq[q]+=x
        assert not any(base_freq.values()),"A z != 0 over Q"
        response=[sum(h.get(coord.get(q,-1),0)*v
                for q,v in cover_freq.items()) for h in funcs]
        expected=[Fraction(v) for v in cert["response"]]
        assert response==expected and any(response),("cover response mismatch",response,expected)
        if span.add(response,("independent general syzygy",cert["pivot_source_column"])):
            verified.append({"terms":len(terms),"new_response":[str(x) for x in response]})
        print("BABEL21_INDEPENDENT_GENERAL_Q_PASS",seed,"terms",len(terms),flush=True)
    assert len(verified)==srcdoc["verified_new_syzygy_Q_rank"]
    full=len(verified)==len(alpha)
    result={"gate":"BABEL21_INDEPENDENT_GENERAL_KERA_Q_REPLAY",
       "seed":seed,"base":base,"source_syzygies_replayed":len(srcdoc["exact_certificates"]),
       "general_new_independent_source_response_rank":len(verified),
       "previously_unknown_response_dimension":len(alpha),
       "known_original_source_response_rank":len(hs)-len(alpha),
       "total_source_response_rank":len(hs)-len(alpha)+len(verified),
       "all_source_cokernel_directions_filled":full,
       "rational_cover_correction_surjectivity":full,
       "all_source_zero_Fourier_check":True,
       "all_cover_response_exactly_checked":True,
       "no_uniform_degree_claim":True,
       "full_degree2_negative_witness":False,
       "replayed":verified}
    Path(f"babel21_{base}_seed{seed}_independent_general_Q.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("BABEL21_INDEPENDENT_GENERAL_RESULT",json.dumps({k:v for k,v in result.items() if k!="replayed"},sort_keys=True),flush=True)
    return result
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--seed",type=int,required=True,choices=(20,37))
    verify(p.parse_args().seed)
