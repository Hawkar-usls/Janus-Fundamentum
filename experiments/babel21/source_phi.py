#!/usr/bin/env python3
"""BABEL21: exact remaining functional on the ENTIRE source degree2 module.

For the rank-1 quotient after Koszul and equal-source generator repairs,
extract a normalized h in the rational annihilator of selected source syzygies.
Compute its response on all original source row/multiplier generators exactly.

This is NOT a full ker(A) decision. The produced response is a reproducible
input to the complete source-module solver.
"""
import argparse,gzip,json,math,hashlib
from pathlib import Path
from fractions import Fraction
from collections import defaultdict,Counter
from crossbase_rank2 import setup
from exact_cokernel import SmallElimination
from janus_babel6_transfer import xor_labels

def normalized_int(vector):
    common=math.lcm(*(Fraction(q).denominator for q in vector))
    vals=[int(Fraction(q)*common) for q in vector]
    d=math.gcd(*(abs(v) for v in vals))
    assert d>0
    vals=[v//d for v in vals]
    s=next(v for v in vals if v)
    return [-v if s<0 else v for v in vals]

def run(base,seed):
    with gzip.open(f"babel20_{base}_seed{seed}_exact_Q_cokernel.json.gz","rt") as f:
        cok=json.load(f)
    kos=json.loads(Path(f"babel20_{base}_seed{seed}_koszul.json").read_text())
    eq=json.loads(Path(f"babel20_{base}_seed{seed}_combined_syzygies.json").read_text())
    hs=[{int(i):Fraction(v) for i,v in arr} for arr in cok["exact_rational_annihilators"]]
    m=len(hs)
    elimination=SmallElimination(m)
    for item in kos["selected"]:
        assert elimination.add(item["response"],["koszul",item["r"],item["s"],item["t"]])
    for item in eq["new_equal_column_witnesses"]:
        assert elimination.add(item["response"],["equal",item["rowA"],item["rowB"]])
    null=elimination.annihilators()
    assert len(null)==m-eq["combined_independent_Q_rank"]
    print("BABEL21_REMAINING_RATIONAL_Q_DIM",base,seed,len(null),flush=True)
    src,lift,labels,base_Q,Q,kernel,fibers,coord,nactive,norbits=setup(seed,base)
    src_labels,srcQ,d=xor_labels(src)
    assert set(srcQ)==set(base_Q)
    records=[]
    for k,v in enumerate(null):
        ints=normalized_int(v)
        H=defaultdict(Fraction)
        for c,hi in zip(ints,hs):
            if c:
                for i,z in hi.items():H[i]+=c*z
        H={i:z for i,z in H.items() if z}
        assert H
        phi=[]
        dist=Counter()
        sample=[]
        for r,row in enumerate(src):
            for p in sorted(base_Q):
                u=fibers[p][0]
                coeff=sum(H.get(coord[q],0) for q in (u,*(u^labels[j] for j in lift[r])) if q in coord)
                if coeff:
                    assert coeff.denominator==1
                    val=int(coeff)
                    phi.append([r,p,val])
                    dist[str(val)]+=1
                    if len(sample)<12:sample.append([r,p,val])
        # The target has no direct anti-coordinate contribution at e0.
        anti0=H.get(coord.get(0,-1),0)
        print("BABEL21_SOURCE_PHI",base,seed,"k",k,
              "Hsupport",len(H),"phi_nnz",len(phi),
              "coeff_hist",json.dumps(dict(dist),sort_keys=True),
              "first",json.dumps(sample),flush=True)
        records.append({
           "component":k,"quotient_coefficients":ints,
           "cover_anti_left_functional":[[int(i),str(z)] for i,z in sorted(H.items())],
           "source_phi_response":[[r,p,v] for r,p,v in phi],
           "source_phi_nnz":len(phi),"source_phi_histogram":dict(dist),
           "anti_e0_value":str(anti0),
           "full_source_kernel_status":"NOT_YET_TESTED"
        })
    report={"gate":"BABEL21_SOURCE_PHI_EXACT_PROBE","base":base,"seed":seed,
       "all_kerT_cokernel_exact_Q_dim":m,"known_source_syzygy_response_rank":len(elimination.selected),
       "remaining_after_two_syzygy_families":len(null),
       "source_degree2_multiplier_count":len(src)*len(base_Q),
       "source_frequency_rank":d,
       "annihilator_representatives":records,
       "global_polynomial_solver_proved":False}
    path=Path(f"babel21_{base}_seed{seed}_source_phi.json.gz")
    with gzip.open(path,"wt",encoding="utf-8",compresslevel=6) as f:
        json.dump(report,f,separators=(",",":"),sort_keys=True)
    print("BABEL21_PHI_REPORT",json.dumps({k:v for k,v in report.items() if k!="annihilator_representatives"},sort_keys=True),flush=True)
    print("BABEL21_PHI_SHA256",hashlib.sha256(path.read_bytes()).hexdigest(),flush=True)
    return report
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--base",default="SCL126_flip16");a.add_argument("--seed",type=int,default=20)
    args=a.parse_args();run(args.base,args.seed)
