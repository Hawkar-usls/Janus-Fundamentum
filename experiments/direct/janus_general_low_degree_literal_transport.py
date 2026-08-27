#!/usr/bin/env python3
"""Regression for the general low-degree literal-transport bound.

The theorem is algebraic. This executable protects representative mixed and
pure elimination cases against implementation drift. P vs NP remains OPEN.
"""

from experiments.direct import janus_unified_proof_carrying_akinator_jec as core

P_VS_NP = "OPEN"


def transport_bound(cnf: core.CNF, pivot: int) -> int:
    pos=[c for c in cnf if pivot in c]
    neg=[c for c in cnf if -pivot in c]
    retained=[c for c in cnf if pivot not in c and -pivot not in c]
    p,q=len(pos),len(neg); d=p+q
    L=sum(map(len,cnf)); m=len(cnf)
    if p==0 or q==0:
        return L-d
    k=max(p,q)
    return k*(L-d)-2*(k-1)*(m-d)


def actual_post_L(cnf: core.CNF, pivot: int) -> tuple[int,dict]:
    out,stats=core.eliminate_var_capped(cnf,pivot,10**9)
    assert out is not None
    return sum(map(len,out)),stats


def verify_degree4_balanced() -> None:
    cnf=core.canon_cnf([
      (6,7,8),(3,5,6),(2,7,8),(2,6,7),(3,5,8),(1,4,5),
      (3,4,5),(1,6,9),(-1,2,4),(-1,7,9),(3,8,9),(2,4,9)
    ])
    b=transport_bound(cnf,1); got,stats=actual_post_L(cnf,1)
    assert {stats['positive'],stats['negative']}=={2}
    assert b==48
    assert got<=b,(got,b)
    print('GENERAL_LITERAL_TRANSPORT_D4_BALANCED=PASS')


def verify_degree3_mixed() -> None:
    cnf=core.canon_cnf([
      (1,2,4),(2,3,5),(3,4,6),(4,5,7),(5,6,8),
      (6,7,9),(7,8,10),(-1,8,9),(2,9,10),(-1,3,10)
    ])
    b=transport_bound(cnf,1); got,stats=actual_post_L(cnf,1)
    assert {stats['positive'],stats['negative']}=={1,2}
    assert got<=b,(got,b)
    print(f'GENERAL_LITERAL_TRANSPORT_D3_BOUND={b}')
    print('GENERAL_LITERAL_TRANSPORT_D3_MIXED=PASS')


def verify_pure() -> None:
    cnf=core.canon_cnf([(1,2,3),(1,4,5),(2,4),(3,5)])
    b=transport_bound(cnf,1); got,stats=actual_post_L(cnf,1)
    assert stats['negative']==0
    assert got<=b,(got,b)
    print('GENERAL_LITERAL_TRANSPORT_PURE=PASS')


def selftest() -> None:
    verify_degree4_balanced()
    verify_degree3_mixed()
    verify_pure()
    print('GENERAL_LOW_DEGREE_LITERAL_TRANSPORT_REGRESSION=PASS')
    print('THEOREM_RUNTIME_HEURISTICS=FORBIDDEN')
    print('P_VS_NP=OPEN')


if __name__=='__main__': selftest()
