#!/usr/bin/env python3
"""BABEL-19 exact rational certificate from BABEL-18B finite-field pivot basis.

Degree <=2 Fourier multipliers, independent ALL-frequency direct replay.
Rank modulo p is never used for coefficient value reconstruction: all numbers
are Python Fraction over Q. No extrapolation to other SCL families.
"""
import argparse,gzip,hashlib,json,math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from rational_dag_inverse import SparseExactInverse,synthetic_regression
from iterative_kerT import setup
from janus_babel6_transfer import make_projection
from janus_babel8_krylov_verify import input_data,normal

def clean_add(d,key,value):
    if value:
        new=d.get(key,0)+value
        if new:d[key]=new
        elif key in d:del d[key]

def term_support(row,u,lift,labels):
    return (u,*(u^labels[j] for j in lift[row]))

def source_lift(seed,src,lift,labels,Q,base_Q):
    rows,src_labels,src_basis,eq,origins=input_data(68)
    assert rows==src and set(src_basis)==set(base_Q)
    from rank2_geometry import restriction
    pi,kernel=restriction(src_labels,labels,15,17)
    reps={}
    for u in sorted(Q):reps.setdefault(pi(u),u)
    assert set(reps)==set(base_Q)
    polynomial_path=Path("babel9_BALANCED_BIT68_DEGREE4_KRYLOV.json")
    poly=json.loads(polynomial_path.read_text())["polynomial_coefficients_low_to_high"]
    P0=int(poly[0])
    assert P0!=0
    v=[0]*32768
    for step,c in enumerate(reversed(poly[1:])):
        v=normal(v,eq);v[0]+=c
        if (step+1)%100==0:print("BABEL19_SOURCE_HORNER",seed,step+1,flush=True)
    check=normal(v,eq)
    assert check[0]==-P0 and not any(check[1:])
    sign=-1 if P0>0 else 1
    D=4*abs(P0)
    source_coeff={}
    for a,b,c,d in eq:
        r,u=origins[(a,b,c,d)]
        coef=4*sign*(v[a]+v[b]+v[c]+v[d])
        if coef:clean_add(source_coeff,(r,reps[u]),coef)
    H=defaultdict(int)
    for (r,u),k in source_coeff.items():
        for q in term_support(r,u,lift,labels):
            H[q]+=k
    projected=defaultdict(int)
    for q,k in H.items():projected[pi(q)]+=k
    assert {q:k for q,k in projected.items() if k}=={0:D}
    print("BABEL19_SOURCE_LIFT_PROJECTION_PASS",seed,
          "source_coefficients",len(source_coeff),
          "D_digits",len(str(D)),"cover_nonzero_freq",sum(bool(k) for k in H.values()),flush=True)
    return D,source_coeff,H

def build(seed,output):
    src,lift,labels,base_Q,Q,kernel,fibers,coord,nactive,norbits=setup(seed)
    dim=len(coord)
    witness=Path(f"babel19_SCL126_flip68_seed{seed}_p65521_modular_pivots.json.gz")
    with gzip.open(witness,"rt") as f:proof=json.load(f)
    assert proof["seed"]==seed and proof["antisector_dimension"]==dim
    pivots=proof["pivots"]
    assert len(pivots)==dim-1,("expected one exact missing rank",len(pivots),dim)
    D,source_terms,H=source_lift(seed,src,lift,labels,Q,base_Q)
    residual={}
    for q,i in coord.items():
        value=(D if q==0 else 0)-H.get(q,0)
        if value:residual[i]=value
    print("BABEL19_RESIDUAL",seed,"active",len(residual),"dimension",dim,flush=True)
    source_pi_check=defaultdict(int)
    from rank2_geometry import restriction
    from janus_babel6_transfer import xor_labels
    src_labels,_,d=xor_labels(src)
    pi,kernel=restriction(src_labels,labels,d,17)
    for q,k in H.items():source_pi_check[pi(q)]+=k
    assert {q:k for q,k in source_pi_check.items() if k}=={0:D}
    solver=SparseExactInverse(dim)
    colmap=[]
    for j,(r,src_u,rr,u) in enumerate(pivots):
        assert rr in (r,r+len(src)) and u in Q
        anchor=fibers[src_u][0]
        accum=defaultdict(int)
        for q in term_support(rr,u,lift,labels):accum[q]+=1
        for q in term_support(r,anchor,lift,labels):accum[q]-=1
        c=[(coord[q],k) for q,k in accum.items() if k and q in coord]
        solver.add_column(c)
        colmap.append((r,anchor,rr,u))
        if (j+1)%10000==0:
            print("BABEL19_EXACT_DAG_PIVOTS",seed,j+1,"of",dim,
                "nodes",len(solver.nodes.nodes),flush=True)
    repair_doc=json.loads(Path("babel19_seed16_koszul_response.json").read_text())
    assert repair_doc["source_syzygy_corrects_last_direction"] and repair_doc["selected"]
    repair_terms=repair_doc["selected"][0]["terms"]
    accum=defaultdict(int)
    for r,p,sgn in repair_terms:
        assert p in base_Q
        u=fibers[p][0]
        for q in term_support(r,u,lift,labels):accum[q]+=sgn
    assert repair_doc["selected"][0]["response"]!=0
    solver.add_column([(coord[q],k) for q,k in accum.items() if k and q in coord])
    print("BABEL19_SEED16_SOURCE_SYZYGY_EXTRA_PIVOT",len(accum),flush=True)
    x=solver.solve(residual)
    print("BABEL19_RATIONAL_SOLUTION",seed,"nonzero",len(x),
          "noninteger",sum(v.denominator!=1 for v in x.values()),
          "DAG_nodes",len(solver.nodes.nodes),flush=True)
    sums=defaultdict(Fraction)
    for (r,u),k in source_terms.items():sums[(r,u)]=Fraction(k)
    for j,k in x.items():
        if j==len(colmap):
            for r,p,sgn in repair_terms:
                clean_add(sums,(r,fibers[p][0]),k*sgn)
        else:
            r,a,rr,u=colmap[j]
            clean_add(sums,(rr,u),k)
            clean_add(sums,(r,a),-k)
    outF=defaultdict(Fraction)
    for (r,u),k in sums.items():
        for q in term_support(r,u,lift,labels):outF[q]+=k
    nonzero={q:k for q,k in outF.items() if k}
    assert nonzero=={0:Fraction(D)},("FULL_FOURIER_FAILURE",len(nonzero))
    print("BABEL19_FULL_RATIONAL_FOURIER_PASS",seed,"terms",len(sums),flush=True)
    common=1
    for k in sums.values():
        common=math.lcm(common,k.denominator)
    intD=D*common
    assert intD>0
    out_terms=[[r,u,str(int(k*common))] for (r,u),k in sorted(sums.items()) if k]
    assert len(out_terms)==len(sums)
    doc={
      "format":"JANUS_BABEL19_SEED_FULL_INTEGER_FOURIER_V1","seed":seed,
      "degree_bound":2,"n":len(lift),"terms_count":len(out_terms),
      "positive_integer_D":str(intD),"source_D":str(D),
      "common_denominator":str(common),"terms":out_terms,
      "exact_rational_all_frequency_checked":True,
      "source_pivot_artifact":witness.name,
      "historical_minimum_degree":4,
      "standard_psd_sos_equivalence_proved":False,"P_equals_NP_proved":False
    }
    with gzip.open(output,"wt",encoding="utf-8",compresslevel=6) as f:
        json.dump(doc,f,separators=(",",":"),sort_keys=True)
    return {
       "status":"BABEL19_FULL_EXACT_INTEGER_FOURIER_IDENTITY_PASS",
       "seed":seed,"term_count":len(out_terms),
       "normalization_digits":len(str(intD)),
       "numerator_common_denominator_digits":len(str(common)),
       "output":str(output),
       "output_sha256":hashlib.sha256(Path(output).read_bytes()).hexdigest()
    }

def independent_verify(seed,output):
    src,lift,labels,base_Q,Q,kernel,fibers,coord,nactive,norbits=setup(seed)
    with gzip.open(output,"rt") as f:doc=json.load(f)
    assert doc["seed"]==seed and doc["degree_bound"]==2 and doc["n"]==252
    assert doc["terms_count"]==len(doc["terms"])
    D=int(doc["positive_integer_D"])
    assert D>0
    check=defaultdict(int)
    for r,u,v in doc["terms"]:
        assert 0<=r<252 and u in Q
        k=int(v)
        for q in (u,*(u^labels[j] for j in lift[r])):check[q]+=k
    remaining={q:v for q,v in check.items() if v}
    assert remaining=={0:D},("INDEPENDENT_REPLAY_MISMATCH",len(remaining))
    return {"status":"BABEL19_INDEPENDENT_FULL_INTEGER_REPLAY_PASS","seed":seed,
            "terms_count":len(doc["terms"]),"D_positive":True,
            "sha256":hashlib.sha256(Path(output).read_bytes()).hexdigest()}

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--seed",type=int,choices=(16,),default=16)
    parser.add_argument("--output",type=Path)
    parser.add_argument("--verify-only",action="store_true")
    args=parser.parse_args()
    out=args.output or Path(f"babel19_seed{args.seed}_full_integer_identity.json.gz")
    report=independent_verify(args.seed,out) if args.verify_only else build(args.seed,out)
    print("BABEL19_SEED16_EXACT_REPORT",json.dumps(report,sort_keys=True),flush=True)
