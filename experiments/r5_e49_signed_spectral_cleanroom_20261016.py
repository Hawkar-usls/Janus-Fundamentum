#!/usr/bin/env python3
"""E4.9 CLEAN_ROOM_RAMANUJAN_NEW_SIGNING: frozen standard-library verifier.

Completely independent from numpy candidate search and JANUS modules.
Given frozen C45 source, separately frozen signing sigma, and exact
rational brackets, check source and signed 45x45 Gram eigenvalue
INERTIA with Fraction Schur elimination and direct integer lifted
Exact-One witnesses for TWO distinct source z.

The acceptance certificate proves:
 - both z active under ONE frozen sigma;
 - 4 distinct explicit SAT witnesses in the 90-variable 2-lift;
 - all new eigenvalues of its bipartite signed adjacency lie
   STRICTLY within the Ramanujan bound 2sqrt2, using an
   exact rational upper interval <2sqrt2;
 - source old lambda2 STRICTLY above 2sqrt2, so NO signing
   can turn this source's lift into a full Ramanujan graph.
This neither proves 4 is ALL SAT solutions for this new signing
nor proves global optimization within 2^27 signings.
"""
import argparse,hashlib,json
from fractions import Fraction
from pathlib import Path


def graph_and_gram(rows,voltage):
    n=len(rows)
    deg=[0]*n
    M=[[0]*n for _ in range(n)]
    B=[[0]*n for _ in range(n)]
    bit=0;pair=set()
    for i,row in enumerate(rows):
        assert len(row)==3 and len(set(row))==3
        for j in row:
            assert 0<=j<n
            B[i][j]=-1 if (voltage>>bit)&1 else 1
            bit+=1;deg[j]+=1
        for a,j in enumerate(sorted(row)):
            for k in sorted(row)[a+1:]:
                assert (j,k) not in pair
                pair.add((j,k))
    assert deg==[3]*n and bit==3*n
    for i in range(n):
        for j in range(n):
            M[i][j]=sum(B[i][k]*B[j][k] for k in range(n))
        assert M[i][i]==3
    return M,B


def negative_inertia_q2_minus_gram(G,q):
    """Independent symmetric Schur complement (upper triangle only)."""
    n=len(G)
    # Explicit upper triangular view, independent of producer's
    # lower-index exact LDL loops.
    D=[[Fraction(q*q if i==j else 0)-G[i][j]
         for j in range(n)] for i in range(n)]
    negative=0
    for i in range(n):
        p=D[i][i]
        assert p!=0,("zero rational pivot",i,str(q))
        if p<0:negative+=1
        for j in range(i+1,n):
            if not D[i][j]:continue
            t=D[i][j]/p
            for k in range(j,n):
                D[j][k]-=t*D[i][k]
                D[k][j]=D[j][k]
        for j in range(i+1,n):
            D[i][j]=D[j][i]=0
    return negative


def rowwise_lift(rows,sign):
    n=len(rows)
    lookup={}
    c=0
    for i,row in enumerate(rows):
        for j in row:
            lookup[(i,j)]=(sign>>c)&1
            c+=1
    assert sign>>c==0
    lifted=[]
    for layer in (0,1):
        for i,row in enumerate(rows):
            lifted.append([j+n*(layer^lookup[(i,j)]) for j in row])
    return lifted,lookup


def exact_witness_for_z(rows,z,lookup):
    n=len(rows)
    singles={j for j in range(n) if (z>>j)&1}
    doubles={1,16}
    assert not singles&doubles
    neighbors={j:[] for j in singles}
    for i,row in enumerate(rows):
        chosen=[j for j in row if j in singles]
        if chosen:
            assert len(chosen)==2
            assert not doubles.intersection(row)
            j,k=chosen
            req=1^lookup[(i,j)]^lookup[(i,k)]
            neighbors[j].append((k,req))
            neighbors[k].append((j,req))
        else:
            assert len(doubles.intersection(row))==1
    labels={}
    for root in sorted(singles):
        if root in labels:continue
        labels[root]=0;Q=[root]
        while Q:
            j=Q.pop()
            for k,t in neighbors[j]:
                expected=labels[j]^t
                if k in labels:
                    assert labels[k]==expected
                else:
                    labels[k]=expected;Q.append(k)
    assert len(labels)==len(singles)
    result=0
    for j in doubles:
        result|=(1<<j)|(1<<(n+j))
    for j,v in labels.items():
        result|=1<<(j+n*v)
    return result


def exact_one(rows,x):
    return all(sum((x>>j)&1 for j in row)==1 for row in rows)


def replay(fixture_path,signing_path):
    source=json.loads(Path(fixture_path).read_text())
    sig=json.loads(Path(signing_path).read_text())
    assert sig["version"]=="R5_E49_CONSTRAINED_SIGNING_FROZEN_1"
    assert source["base_canonical_sha256"]==sig["source_sha256"]
    rows=source["base_45_rows"]
    n=len(rows)
    assert n==45
    signed=int(sig["best_signed_voltage_mask_decimal"])
    Gs,Bs=graph_and_gram(rows,signed)
    Go,Bo=graph_and_gram(rows,0)
    lifted,lookup=rowwise_lift(rows,signed)
    witnesses=[]
    for zstr in source["distinct_z_decimal"]:
        z=int(zstr)
        x=exact_witness_for_z(rows,z,lookup)
        full=(1<<n)-1
        swap=((x&full)<<n)|(x>>n)
        assert x!=swap
        assert exact_one(lifted,x) and exact_one(lifted,swap)
        assert (x&full)^(x>>n)==z
        assert (swap&full)^(swap>>n)==z
        witnesses.extend((x,swap))
    assert len(set(witnesses))==4
    def bracket(G,label,expected_lower,expected_upper):
        b=sig[label]
        def parse(s):
            p,q=map(int,s.split("/"));return Fraction(p,q)
        lo,hi=parse(b["lower"]),parse(b["upper"])
        assert lo==expected_lower and hi==expected_upper
        n_lo=negative_inertia_q2_minus_gram(G,lo)
        n_hi=negative_inertia_q2_minus_gram(G,hi)
        return {"lower":str(lo),"upper":str(hi),
                "eigenvalues_singular_gt_lower":n_lo,
                "eigenvalues_singular_gt_upper":n_hi}
    new=bracket(Gs,"best_new_signed_radius_exact_interval",
                Fraction(2668,1000),Fraction(2671,1000))
    old=bracket(Go,"source_old_lambda2_exact_interval",
                Fraction(29049,10000),Fraction(29050,10000))
    assert (new["eigenvalues_singular_gt_lower"],
            new["eigenvalues_singular_gt_upper"])==(1,0)
    assert (old["eigenvalues_singular_gt_lower"],
            old["eigenvalues_singular_gt_upper"])==(2,1)
    assert Fraction(2671,1000)**2<8
    assert Fraction(29049,10000)**2>8
    return {"gate":"E4_9_CLEAN_ROOM_NEW_RAMANUJAN_SIGNING",
            "stdlib_only":True,"source_sha256":sig["source_sha256"],
            "frozen_signing_decimal":str(signed),
            "two_distinct_z_both_active_under_one_signing":True,
            "independent_2lift_integer_SAT_witnesses":[str(x) for x in witnesses],
            "number_explicit_valid_SAT_witnesses":len(witnesses),
            "total_SAT_solutions_for_this_signing":"NOT_COUNTED",
            "exact_new_signed_radius_interval":new,
            "exact_old_source_lambda2_interval":old,
            "strict_new_bound_below_2_sqrt2":True,
            "strict_old_lambda2_above_2_sqrt2":True,
            "global_minimization_over_all_signings":"NOT_PROVED",
            "P_vs_NP":"OPEN"}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--fixture",required=True)
    p.add_argument("--signing",required=True)
    v=p.parse_args()
    print(json.dumps(replay(v.fixture,v.signing),indent=2,sort_keys=True))
