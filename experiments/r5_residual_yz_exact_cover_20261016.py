#!/usr/bin/env python3
"""JANUS R5 E4.6 RESIDUAL_YZ_EXACT_COVER.

ALL-n bijection for fixed nonzero z in ker_GF2(A):
S=supp(z), R2=rows meeting S twice, R0=rows disjoint from S.
All y in {0,1,2}^n with integer Ay=2 and y mod2=z have:
 - y_j=1 on S;
 - y_j=0 off S when j meets R2;
 - y_j in {0,2} only for CLEAN outside columns meeting R0 only.
Exactly one 2-column covers each R0 row. Thus Y_z bijects
with exact covers of R0 by full triples of clean outside columns.

|R2|=3|z|/2; |R0|=n-3|z|/2; required #2-cols
p=n/3-|z|/2. DPLL at most 3 choices per step, with
at most 3^p leaves, poly(n) per node; budget returns UNKNOWN,
NOT an UNSAT theorem. No all-n polynomial claim.

The frozen proof independently checks |Y_z*|=1 by choosing
2 clean triples covering exactly 6 residual rows, not by
reading 72-bit lifted SAT oracle counts.
"""
from itertools import combinations
from collections import Counter
import argparse,json

from r5_cycle_parity_certificate_20261015 import context

def residual(rows,z,budget=30000):
    n=len(rows)
    if z<0 or z>>n:raise ValueError("invalid z")
    if any(sum((z>>j)&1 for j in row)%2 for row in rows):
        raise ValueError("z outside GF2 kernel")
    if not n%3==0:
        raise ValueError("number of rows must be divisible by3")
    S={j for j in range(n) if (z>>j)&1}
    R0=[]
    R2=[]
    for i,row in enumerate(rows):
        count=sum(j in S for j in row)
        if count==0:R0.append(i)
        elif count==2:R2.append(i)
        else:raise AssertionError("kernel row parity violation")
    assert len(R2)*2==3*len(S)
    p=n//3-len(S)//2
    if p<0 or 3*p!=len(R0):
        return {"status":"EXACT","count":0,"solutions":[],"nodes":0,
                "p":p,"reason":"impossible support size"}
    neighbors=[set() for j in range(n)]
    for i,row in enumerate(rows):
        for j in row:neighbors[j].add(i)
    clean=[j for j in range(n) if j not in S and
           neighbors[j].issubset(set(R0))]
    R0mask=sum(1<<i for i in R0)
    cmasks={j:sum(1<<i for i in neighbors[j]) for j in clean}
    candidates={i:tuple(j for j in clean if (cmasks[j]>>i)&1)
                for i in R0}
    assert all(len(v)<=3 for v in candidates.values())
    chosen=[]
    solutions=[]
    states=0
    unknown=False
    def rec(uncovered):
        nonlocal states,unknown
        if states>=budget:
            unknown=True
            return
        states+=1
        if uncovered==0:
            if len(chosen)!=p:raise AssertionError("wrong #2 columns")
            solutions.append(tuple(sorted(chosen)))
            return
        if len(chosen)>=p:return
        options=[]
        for row in R0:
            if not ((uncovered>>row)&1):continue
            possible=[j for j in candidates[row]
                      if (cmasks[j]&uncovered)==cmasks[j]]
            if not possible:return
            if not options or len(possible)<len(options):
                options=possible
        for j in options:
            chosen.append(j)
            rec(uncovered^cmasks[j])
            chosen.pop()
            if unknown:return
    rec(R0mask)
    if unknown:
        return {"status":"UNKNOWN_RESOURCE_LIMIT",
                "nodes":states,"partial_count":len(solutions),"p":p}
    assert len(set(solutions))==len(solutions)
    for sol in solutions:
        y=[int(j in S)+2*int(j in sol) for j in range(n)]
        assert all(v in (0,1,2) for v in y)
        assert all(sum(y[j] for j in row)==2 for row in rows)
        assert all((y[j]&1)==((z>>j)&1) for j in range(n))
    return {"status":"EXACT","n":n,"z_weight":len(S),
            "R2_rows":R2,"R0_rows":R0,
            "p":p,"clean_columns":clean,
            "candidate_count":len(clean),
            "exact_cover_columns":solutions,
            "count":len(solutions),
            "nodes":states,
            "max_branches_bound":3**p}


def brute_frozen_pairs(rows,z,report):
    """Independent direct all C(|J0|,2) combinations, not DPLL."""
    n=len(rows); R0=set(report["R0_rows"])
    options=[]
    for J in combinations(report["clean_columns"],2):
        y=[((z>>j)&1)+2*int(j in J) for j in range(n)]
        if all(sum(y[j] for j in row)==2 for row in rows):
            options.append(tuple(J))
    return options


def self_test():
    base,meta,frame,signs,sigma,y,witness,cover,z,k=context()
    r=residual(base,z)
    assert r["status"]=="EXACT"
    assert r["z_weight"]==20
    assert len(r["R0_rows"])==6
    assert r["p"]==2 and r["max_branches_bound"]==9
    assert r["count"]==1
    chosen=tuple(j for j,v in enumerate(y) if v==2)
    assert r["exact_cover_columns"]==[chosen]
    independent=brute_frozen_pairs(base,z,r)
    assert independent==r["exact_cover_columns"]
    assert r["nodes"]<=r["max_branches_bound"]*4
    return {
        "gate":"RESIDUAL_YZ_EXACT_COVER",
        "all_n_bijection":"PROVED",
        "source_n":len(base),"z_weight":z.bit_count(),
        "R0_count":len(r["R0_rows"]),
        "R0_rows":r["R0_rows"],
        "p":r["p"],
        "clean_outside_cols":r["clean_columns"],
        "exact_cover_y2_columns":list(chosen),
        "exact_cover_count":r["count"],
        "node_count":r["nodes"],
        "independent_pair_scan_count":len(independent),
        "parametrized_upper_bound":"3^p poly(n)",
        "uniform_polynomial_time":"NOT_PROVED",
        "P_vs_NP":"OPEN"}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    opt=p.parse_args()
    if not opt.self_test:p.error("--self-test")
    print(json.dumps(self_test(),indent=2,sort_keys=True))
