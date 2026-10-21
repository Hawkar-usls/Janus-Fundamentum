#!/usr/bin/env python3
"""BABEL-21G exact Gram rank difference for image R(ker A).

Theorem, any A in Q^(F x E), R in Q^(k x E):
rank_Q(R|ker A) = rank_Q(A^T A + R^T R)-rank_Q(A^T A).
Both Gram matrices have E rows/cols and A^T A is computable from
degree-2 Fourier generator intersections (support at most four).
No enumeration of the 2^d Fourier STATE space is needed to build Gram.

This is fixed-degree linear algebra, NOT a uniform degree bound.
"""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import json
from noncover_scout import synthesize,valid
from janus_babel6_transfer import xor_labels

def rank(columns):
    pivot={}
    for col in columns:
        vec={j:Fraction(v) for j,v in col.items() if v}
        while vec:
            j=min(vec)
            if j not in pivot:
                norm=1/vec[j]
                pivot[j]={i:v*norm for i,v in vec.items()}
                break
            k=vec[j];row=pivot[j]
            for i,v in row.items():
                nxt=vec.get(i,0)-k*v
                if nxt:vec[i]=nxt
                elif i in vec:del vec[i]
    return len(pivot)

def gram(columns,R):
    E=len(columns)
    gcols=[]
    hcols=[]
    for j,col in enumerate(columns):
        original={}
        updated={}
        for i,other in enumerate(columns):
            inner=sum(v*other.get(f,0) for f,v in col.items())
            if inner:original[i]=inner
            extra=inner+sum(R[q][i]*R[q][j] for q in range(len(R)))
            if extra:updated[i]=extra
        gcols.append(original)
        hcols.append(updated)
    return gcols,hcols

def audit(seed,E=72):
    rows=synthesize(seed)
    assert rows is not None and valid(rows)
    labels,Q,d=xor_labels(rows)
    dim=1<<d
    # mixed base row / Fourier-shift generators; exactly degree <=2
    shifts=sorted(Q)
    keys=[(r,u) for r in range(len(rows)) for u in shifts]
    keys=keys[:E//2]+keys[::max(1,len(keys)//(E-E//2))][:E-E//2]
    keys=list(dict.fromkeys(keys))
    assert len(keys)>=E//2
    columns=[]
    for r,u in keys:
        counts=Counter((u,*(u^labels[j] for j in rows[r])))
        columns.append(dict(counts))
    E2=len(columns)
    # Independent Q-linear functionals on source coefficients, as toy responses
    R=[
       [(r%3)-(u%3) for r,u in keys],
       [((r+u)%5)-2 for r,u in keys],
       [1 if (r+2*u)%7==0 else 0 for r,u in keys],
    ]
    A=rank(columns)
    stacked=[]
    for j,col in enumerate(columns):
        vec=dict(col)
        for i in range(len(R)):
            if R[i][j]:vec[dim+i]=R[i][j]
        stacked.append(vec)
    AR=rank(stacked)
    G,H=gram(columns,R)
    g=rank(G);h=rank(H)
    assert A==g,(A,g)
    assert AR==h,(AR,h)
    assert 0<=h-g<=len(R)
    report={"seed":seed,"rows":len(rows),"nullity_d":d,"raw_fourier_states":dim,
        "tested_legal_degree2_columns":E2,
        "direct_fourier_rank_A":A,"gram_rank_A":g,
        "direct_stacked_rank":AR,"gram_augmented_rank":h,
        "rank_R_of_kernel_A":h-g,
        "rank_identity_over_Q":"EXACT_PASS",
        "gram_built_using_only_4_sparse_character_intersections":True,
        "universal_degree_bound_proved":False}
    print("BABEL21_GRAM_RANK_PASS",json.dumps(report,sort_keys=True),flush=True)
    return report

if __name__=="__main__":
    results=[audit(i) for i in (0,1,2,3)]
    Path("babel21_rank_difference_gram_regression.json").write_text(
        json.dumps({"gate":"BABEL21G_FIXED_DEGREE_GRAM_KERNEL_IMAGE",
        "cases":results,"all_exact_Q_regressions_pass":True},indent=2,sort_keys=True)+"\n")
