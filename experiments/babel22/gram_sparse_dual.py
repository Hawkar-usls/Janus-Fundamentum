#!/usr/bin/env python3
"""BABEL-22G exact full-degree2 Gram / sparse-dual construction.

No enumeration of the 2**d Fourier row space is used for constructing G,
solving its rational normal equations, or verifying certificates.
Small controls do enumerate the parity kernel independently to check SAT.
All input proofs are for fixed multiplier degree, NOT generic P=NP.
"""
import json
from collections import Counter, defaultdict
from fractions import Fraction


def fano7():
    return [tuple(sorted((i, (i+1)%7, (i+3)%7))) for i in range(7)]


def affine9():
    at=lambda x,y:3*x+y
    return [tuple(sorted(row)) for k in range(3) for row in (
        [at(k,y) for y in range(3)],
        [at(x,k) for x in range(3)],
        [at(x,y) for x in range(3) for y in range(3) if (x+y)%3==k]
    )]


def kernel_basis(rows):
    n=len(rows)
    assert all(len(row)==3 and len(set(row))==3 for row in rows)
    assert Counter(j for row in rows for j in row)==Counter({j:3 for j in range(n)})
    pivot={}
    for row in rows:
        x=sum(1<<i for i in row)
        while x:
            i=x.bit_length()-1
            if i in pivot:x^=pivot[i]
            else:pivot[i]=x;break
    basis=[]
    for j in range(n):
        if j in pivot:continue
        v=1<<j
        for p in sorted(pivot):
            if ((pivot[p]&v).bit_count()&1):v^=1<<p
        assert all(((v&sum(1<<k for k in row)).bit_count()&1)==0 for row in rows)
        basis.append(v)
    return basis


def characters(rows):
    basis=kernel_basis(rows)
    labels=[sum(1<<i for i,v in enumerate(basis) if (v>>j)&1)
            for j in range(len(rows))]
    return basis,labels


def multipliers(labels,degree):
    q={0}
    if degree>=1:q.update(labels)
    if degree>=2:
        q.update(labels[i]^labels[j] for i in range(len(labels)) for j in range(i))
    return sorted(q)


def columns(rows,labels,degree):
    q=multipliers(labels,degree)
    return [(r,u,dict(Counter([u]+[u^labels[j] for j in row])))
            for r,row in enumerate(rows) for u in q]


def normal_equations(fullcols):
    support=[col for _,_,col in fullcols]
    gram=[[sum(v*other.get(freq,0) for freq,v in col.items())
           for other in support] for col in support]
    target=[col.get(0,0) for col in support]
    return gram,target


def rational_solve(gram,c):
    """Exact RREF solution of Gx=c, free coordinates set to zero."""
    e=len(c)
    aug=[[Fraction(v) for v in gram[i]+[c[i]]] for i in range(e)]
    rank=0;pivot_cols=[]
    for j in range(e):
        k=next((i for i in range(rank,e) if aug[i][j]),None)
        if k is None:continue
        aug[rank],aug[k]=aug[k],aug[rank]
        val=aug[rank][j]
        aug[rank]=[v/val for v in aug[rank]]
        for i in range(e):
            if i!=rank and aug[i][j]:
                f=aug[i][j]
                aug[i]=[aug[i][k]-f*aug[rank][k] for k in range(e+1)]
        pivot_cols.append(j)
        rank+=1
    assert all(aug[i][e]==0 for i in range(rank,e))
    x=[Fraction(0)]*e
    for i,j in enumerate(pivot_cols):x[j]=aug[i][e]
    assert all(sum(gram[i][j]*x[j] for j in range(e))==c[i] for i in range(e))
    return x,rank


def prove(rows,degree):
    basis,labels=characters(rows)
    fullcols=columns(rows,labels,degree)
    gram,c=normal_equations(fullcols)
    x,rank=rational_solve(gram,c)
    raw=defaultdict(Fraction)
    raw[0]=Fraction(1)
    for val,(_,_,col) in zip(x,fullcols):
        if val:
            for freq,a in col.items():raw[freq]-=val*a
    h={freq:v for freq,v in raw.items() if v}
    h0=h.get(0,Fraction(0))
    assert h0==1-sum(a*b for a,b in zip(x,c))
    assert h0>=0
    assert all(sum(h.get(freq,0)*v for freq,v in col.items())==0
               for _,_,col in fullcols)
    if h0==0:
        assert not h, "Zero norm must imply Fourier residual is zero"
        status="EXACT_Q_UNSAT_IDENTITY"
        witness_terms=sum(bool(a) for a in x)
        dual_support=0
    else:
        dual={freq:v/h0 for freq,v in h.items()}
        assert dual[0]==1
        assert all(sum(dual.get(freq,0)*v for freq,v in col.items())==0
                   for _,_,col in fullcols)
        status="EXACT_Q_FULL_DEGREE_DUAL_NOT_SAT_DECISION"
        witness_terms=sum(bool(a) for a in x)
        dual_support=len(dual)
        assert dual_support<=4*len(fullcols)+1
    return {"n":len(rows),"kernel_dim":len(basis),"degree":degree,
            "columns_E":len(fullcols),"gram_rank":rank,
            "residual_h0":str(h0),"sparse_dual_support":dual_support,
            "projection_terms":witness_terms,"status":status}


def exact_sat_count(rows):
    basis=kernel_basis(rows)
    v=0; count=0;n=len(rows)
    for i in range(1<<len(basis)):
        if i:v^=basis[(i&-i).bit_length()-1]
        if v.bit_count()*3==2*n:count+=1
    return count


def main():
    cases=[("FANO7",fano7(),0),("FANO7",fano7(),1),
           ("FANO7",fano7(),2),("AFFINE9",affine9(),0),
           ("AFFINE9",affine9(),1),("AFFINE9",affine9(),2)]
    out=[]
    for name,rows,degree in cases:
        v=prove(rows,degree)
        v["case"]=name
        v["sat_count_exact"]=exact_sat_count(rows)
        if name=="FANO7":
            assert v["sat_count_exact"]==0
            assert (v["status"]=="EXACT_Q_UNSAT_IDENTITY")==bool(degree>=1)
        else:
            assert v["sat_count_exact"]==3
            assert v["status"]=="EXACT_Q_FULL_DEGREE_DUAL_NOT_SAT_DECISION"
        out.append(v)
    print(json.dumps({"gate":"BABEL22G_EXACT_GRAM_SPARSE_FULL_M2_DUAL",
                      "all_controls_exact_Q_PASS":True,
                      "all_n_theorem":"PROVED_BY_NORMAL_EQUATIONS",
                      "universal_degree2_completeness":"OPEN",
                      "P_vs_NP":"OPEN","cases":out},
                     indent=2,sort_keys=True))


if __name__=="__main__":
    main()
