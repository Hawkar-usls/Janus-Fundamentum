#!/usr/bin/env python3
"""Regression for regular-min-degree global support feasibility bound.

The paired JSON carries the proof. This executable evaluates the exact finite
integer optimization and checks the N58 second-OPEN specimen plus small actual
canonical states. P vs NP remains OPEN.
"""

from itertools import combinations, product

from experiments.direct import janus_unified_proof_carrying_akinator_jec as core
from experiments.direct import janus_proof_selector_v05_candidate as v05
from experiments.direct.janus_pair_support_mass_distinct_resolvent_ceiling import wmax

P_VS_NP = "OPEN"


def omission_product_exact(t: int, p: int, q: int) -> int:
    best=0
    for a in range(max(0,t-q),min(p,t)+1):
        b=t-a
        if 0<=b<=q:
            best=max(best,a*b)
    return best


def omitted_pair_dp(r: int, c: int, p: int, q: int) -> list[int]:
    maxR=r*c
    neg=-10**18
    dp=[neg]*(maxR+1); dp[0]=0
    f=[omission_product_exact(t,p,q) for t in range(c+1)]
    for _ in range(r):
        nd=[neg]*(maxR+1)
        for s,val in enumerate(dp):
            if val==neg: continue
            for t in range(c+1):
                if s+t>maxR: break
                cand=val+f[t]
                if cand>nd[s+t]: nd[s+t]=cand
        dp=nd
    return dp


def regular_raw_ceiling(n: int, m: int, d: int, p: int, q: int) -> tuple[int,dict]:
    assert p+q==d
    assert p>0 and q>0
    r=n-1; c=m-d; pq=p*q
    dp=omitted_pair_dp(r,c,p,q)
    best_raw=-1; best=None
    Dmax=min(pq,3**r)
    for R0 in range(2*c,c*r+1):
        O=dp[R0]
        if O<0: continue
        Smin=r*pq-O
        for D in range(Dmax+1):
            res_lb=max(0,Smin-(pq-D)*r)
            # Increasing h lowers K; take the first feasible h for this R0,D.
            for h in range(min(c,D)+1):
                K=c+D-h
                if K>3**r: continue
                width_lb=R0+res_lb-h*r
                W=wmax(r,K)
                if width_lb<=W:
                    raw=1+K+W
                    if raw>best_raw:
                        best_raw=raw
                        best={"R0":R0,"Omax":O,"Smin":Smin,"D":D,"h":h,"K":K,"resolvent_width_lower":res_lb,"raw_width_lower":width_lb,"Wmax":W}
                    break
    assert best_raw>=0
    return best_raw,best


def all_unitfree_clauses(n: int):
    rows=[]
    for width in range(2,n+1):
        for support in combinations(range(1,n+1),width):
            for signs in product((1,-1),repeat=width):
                rows.append(tuple(v*s for v,s in zip(support,signs)))
    return tuple(core.canon_clause(c) for c in rows)


def verify_small_actual_regular_states() -> None:
    clauses=all_unitfree_clauses(3)
    checked=0
    for m in range(2,5):
        for chosen in combinations(clauses,m):
            cnf=core.canon_cnf(chosen)
            if len(cnf)!=m or not core.vars_of(cnf): continue
            live=core.vars_of(cnf); n=len(live)
            deg={v:v05.incidence_degree(cnf,v) for v in live}
            d=min(deg.values())
            if sum(len(c) for c in cnf)!=n*d: continue
            pivot=min(v for v in live if deg[v]==d)
            p=sum(pivot in c for c in cnf); q=sum(-pivot in c for c in cnf)
            if p==0 or q==0: continue
            bound,_=regular_raw_ceiling(n,m,d,p,q)
            out,stats=core.eliminate_var_capped(cnf,pivot,10**9)
            assert out is not None
            assert stats['raw_units']<=bound,(cnf,pivot,stats,bound)
            checked+=1
    print(f'REGULAR_SUPPORT_SMALL_ACTUAL=PASS:{checked}')


def verify_N58_specimen() -> None:
    raw,w=regular_raw_ceiling(7,77,50,22,28)
    assert raw==3361,(raw,w)
    assert w=={"R0":162,"Omax":1092,"Smin":2604,"D":609,"h":0,"K":636,"resolvent_width_lower":2562,"raw_width_lower":2724,"Wmax":2724},w
    assert raw<58*58
    print('REGULAR_SUPPORT_N58_SECOND_OPEN_OLD=3389')
    print('REGULAR_SUPPORT_N58_REPAIRED=3361')
    print('REGULAR_SUPPORT_N58_MARGIN=3')
    print('REGULAR_SUPPORT_N58_LOCAL_REPAIR=PASS')


def selftest() -> None:
    verify_small_actual_regular_states()
    verify_N58_specimen()
    print('REGULAR_MIN_DEGREE_GLOBAL_SUPPORT_FEASIBILITY_REGRESSION=PASS')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('UNBOUNDED_TOTALITY=OPEN')
    print('P_VS_NP=OPEN')


if __name__=='__main__':
    selftest()
