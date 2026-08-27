#!/usr/bin/env python3
"""Regression for the global raw signed-clause-universe bound.

P vs NP remains OPEN. The theorem itself is in the paired JSON artifact.
"""

from itertools import combinations, product

from experiments.direct import janus_unified_proof_carrying_akinator_jec as core
from experiments.direct import janus_proof_selector_v05_candidate as v05
from experiments.direct.janus_pair_support_mass_distinct_resolvent_ceiling import wmax

P_VS_NP = "OPEN"


def global_raw_bound(r: int, K: int) -> int:
    kk = min(K, 3 ** r)
    return 1 + kk + wmax(r, kk)


def all_unitfree_clauses(n: int):
    rows=[]
    for width in range(2,n+1):
        for support in combinations(range(1,n+1),width):
            for signs in product((1,-1),repeat=width):
                rows.append(tuple(v*s for v,s in zip(support,signs)))
    return tuple(core.canon_clause(c) for c in rows)


def verify_small_actual_raw_sets() -> None:
    clauses=all_unitfree_clauses(3)
    checked=0
    for m in range(2,5):
        for chosen in combinations(clauses,m):
            cnf=core.canon_cnf(chosen)
            if len(cnf)!=m or not core.vars_of(cnf):
                continue
            live=core.vars_of(cnf)
            deg={v:v05.incidence_degree(cnf,v) for v in live}
            d=min(deg.values())
            pivot=min(v for v in live if deg[v]==d)
            out,stats=core.eliminate_var_capped(cnf,pivot,10**9)
            assert out is not None

            pos=[c for c in cnf if pivot in c]
            neg=[c for c in cnf if -pivot in c]
            retained=[c for c in cnf if pivot not in c and -pivot not in c]
            raw=set(retained)
            for a in pos:
                for b in neg:
                    rr=core.resolve_on_var(a,b,pivot)
                    if rr is not None:
                        raw.add(rr)
            r=len(live)-1
            K=len(raw)
            exact_units=core.state_units(tuple(raw))
            assert exact_units<=global_raw_bound(r,K),(cnf,pivot,exact_units,r,K)
            assert stats['raw_units']==exact_units,(stats,exact_units)
            checked+=1
    print(f'GLOBAL_RAW_UNIVERSE_SMALL_EXHAUSTIVE=PASS:{checked}')


def verify_N58_repair_number() -> None:
    r=6; K=620
    assert wmax(r,K)==2676
    bound=global_raw_bound(r,K)
    assert bound==3297
    assert bound<58*58
    assert 3375>58*58
    print('GLOBAL_RAW_UNIVERSE_N58_OLD_BOUND=3375')
    print('GLOBAL_RAW_UNIVERSE_N58_REPAIRED_BOUND=3297')
    print('GLOBAL_RAW_UNIVERSE_N58_LOCAL_REPAIR=PASS')


def selftest() -> None:
    verify_small_actual_raw_sets()
    verify_N58_repair_number()
    print('GLOBAL_RAW_SIGNED_CLAUSE_UNIVERSE_BOUND_REGRESSION=PASS')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('UNBOUNDED_TOTALITY=OPEN')
    print('P_VS_NP=OPEN')


if __name__=='__main__':
    selftest()
