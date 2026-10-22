#!/usr/bin/env python3
"""BABEL-23 proof-carrying, two-sided fixed-degree Fourier Gram controls.

Exact rational arithmetic, standard library only; no imports from BABEL22
producer/solver. The all-n proof is in the associated research note.
A conditional SAT witness is an actual Boolean assignment verified row by row.
"""
import json
from collections import Counter
from fractions import Fraction


def fano7():
    return [tuple(sorted((i, (i+1)%7, (i+3)%7))) for i in range(7)]


def affine9():
    pt=lambda x,y:3*x+y
    return [tuple(sorted(row)) for k in range(3) for row in (
        [pt(k,y) for y in range(3)],
        [pt(x,k) for x in range(3)],
        [pt(x,y) for x in range(3) for y in range(3) if (x+y)%3==k]
    )]


def kernel(rows):
    n=len(rows)
    assert all(len(r)==3 and len(set(r))==3 for r in rows)
    assert Counter(i for r in rows for i in r)==Counter({i:3 for i in range(n)})
    piv={}
    for r in rows:
        w=sum(1<<i for i in r)
        while w:
            j=w.bit_length()-1
            if j in piv:w^=piv[j]
            else:piv[j]=w;break
    result=[]
    for j in range(n):
        if j in piv:continue
        w=1<<j
        for p in sorted(piv):
            if (w&piv[p]).bit_count()&1:w^=1<<p
        assert all((w & sum(1<<i for i in r)).bit_count()%2==0 for r in rows)
        result.append(w)
    return result


def sparse_columns(rows,basis,degree):
    n=len(rows)
    labels=[sum(1<<i for i,v in enumerate(basis) if (v>>j)&1)
            for j in range(n)]
    support={0}
    if degree>=1:support.update(labels)
    if degree>=2:
        support.update(labels[i]^labels[j] for i in range(n) for j in range(i))
    return [Counter([u]+[u^labels[j] for j in row])
            for row in rows for u in sorted(support)]


def exact_gram_solution(cols):
    E=len(cols)
    G=[[sum(v*other.get(freq,0) for freq,v in col.items())
        for other in cols] for col in cols]
    c=[col.get(0,0) for col in cols]
    a=[[Fraction(v) for v in G[i]+[c[i]]] for i in range(E)]
    rank=0;piv=[]
    for col in range(E):
        i=next((j for j in range(rank,E) if a[j][col]),None)
        if i is None:continue
        a[i],a[rank]=a[rank],a[i]
        factor=a[rank][col]
        a[rank]=[z/factor for z in a[rank]]
        for j in range(E):
            if j!=rank and a[j][col]:
                f=a[j][col]
                a[j]=[a[j][k]-f*a[rank][k] for k in range(E+1)]
        piv.append(col);rank+=1
    assert all(a[i][-1]==0 for i in range(rank,E))
    x=[Fraction(0)]*E
    for i,p in enumerate(piv):x[p]=a[i][-1]
    assert all(sum(G[i][j]*x[j] for j in range(E))==c[i] for i in range(E))
    h={0:Fraction(1)}
    for t,col in zip(x,cols):
        if t:
            for q,z in col.items():h[q]=h.get(q,0)-t*z
    h={q:z for q,z in h.items() if z}
    h0=h.get(0,Fraction(0))
    assert h0==sum(z*z for z in h.values())
    assert h0==1-sum(z*t for z,t in zip(c,x))
    assert all(sum(h.get(q,0)*z for q,z in col.items())==0 for col in cols)
    return h,h0,rank


def value(h,v):
    return sum(z*(-1 if (q&v).bit_count()%2 else 1) for q,z in h.items())


def prefix_mean(h,prefix,length):
    return sum(z*(-1 if (q&prefix).bit_count()%2 else 1)
               for q,z in h.items() if q>>length==0)


def recover_sat(rows,basis,h):
    h0=h.get(0,Fraction(0))
    tail=sum(abs(z) for q,z in h.items() if q)
    assert h0>0 and h0>=tail
    pref=0
    assert prefix_mean(h,pref,0)>0
    for i in range(len(basis)):
        p0=prefix_mean(h,pref,i+1)
        p1=prefix_mean(h,pref|(1<<i),i+1)
        assert p0+p1==2*prefix_mean(h,pref,i)
        if p0<=0:
            assert p1>0
            pref|=1<<i
    assert value(h,pref)>0
    v=0
    for i,w in enumerate(basis):
        if pref>>i&1:v^=w
    x=((1<<len(rows))-1)^v
    assert all(sum((x>>j)&1 for j in row)==1 for row in rows)
    return [j for j in range(len(rows)) if (x>>j)&1]


def ground_truth(rows,basis):
    v=0;count=0
    for i in range(1<<len(basis)):
        if i:v^=basis[(i&-i).bit_length()-1]
        x=((1<<len(rows))-1)^v
        count+=all(sum((x>>j)&1 for j in r)==1 for r in rows)
    return count


def audit(label,rows,degree,expected):
    basis=kernel(rows)
    cols=sparse_columns(rows,basis,degree)
    h,h0,rank=exact_gram_solution(cols)
    maxsat=int((1<<len(basis))*h0)
    tail=sum(abs(z) for q,z in h.items() if q)
    sat=ground_truth(rows,basis)
    assert sat==expected and sat<=maxsat
    h_positive=bool(h0>0 and h0>=tail)
    witness=recover_sat(rows,basis,h) if h_positive else None
    if h0==0 or (1<<len(basis))*h0<1:
        status="UNSAT_SOUND"
        assert sat==0
    elif h_positive:
        status="SAT_SOUND_WITNESS_REPLAYED"
        assert sat>0
    else:
        status="UNKNOWN_SOUND"
    for v in range(1<<len(basis)):
        assert value(h,v)==sum(
            z*(-1 if (q&v).bit_count()%2 else 1) for q,z in h.items()
        )
    return {"case":label,"degree":degree,"n":len(rows),"dimK":len(basis),
            "E":len(cols),"gram_rank":rank,
            "h0":str(h0),"tail_l1":str(tail),"sat_upper_bound":maxsat,
            "sat_count_independent":sat,"l1_dominance":h_positive,
            "status":status,"sat_witness_one_indices":witness,
            "h_support":len(h),
            "H_0":str(value(h,0))}


def main():
    tests=[audit("FANO7",fano7(),0,0),
           audit("FANO7",fano7(),1,0),
           audit("AFFINE9",affine9(),0,3)]
    assert [t["status"] for t in tests]==[
        "UNKNOWN_SOUND","UNSAT_SOUND","SAT_SOUND_WITNESS_REPLAYED"]
    assert tests[0]["h0"]=="9/16" and tests[0]["tail_l1"]=="21/16"
    assert tests[0]["H_0"]=="-3/4"
    assert tests[2]["h0"]=="3/4" and tests[2]["tail_l1"]=="3/4"
    assert tests[2]["sat_upper_bound"]==tests[2]["sat_count_independent"]==3
    print(json.dumps({
        "gate":"BABEL23_GRAM_TWO_SIDED_PROOF_CARRYING",
        "all_controls_exact_fraction_PASS":True,
        "all_n_sat_bound":"PROVED",
        "conditional_sat_witness_recovery":"PROVED",
        "universal_polynomial_decider":"NOT_PROVED",
        "P_vs_NP":"OPEN",
        "cases":tests},indent=2,sort_keys=True))


if __name__=="__main__":
    main()
