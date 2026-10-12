#!/usr/bin/env python3
"""JANUS R5 sound odd-automorphism PC3 adapter for the shared portfolio.

A supplied permutation is UNTRUSTED until verified against EVERY original
Exact-One triple. Verify it is a bijection, has O(n)-bounded odd order,
permutes original source rows with orbit sizes dividing its odd order, and preserves all clauses exactly.

Only then run the existing NO-LOSS odd-order GF2 PC3 orbit compression:
1 in the full degree-3 Boolean polynomial-calculus space iff 1 occurs
in its invariant projection. If it returns UNSAT it reconstructs and
rechecks a genuine sum-of-generators algebraic contradiction.

Missing/invalid symmetry => UNKNOWN, never SAT/UNSAT.
No symmetry discovery is claimed, and no worst-case all-SCL coverage.
"""
from __future__ import annotations

from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_odd_automorphism_pc3_snark_probe import pc3_symmetry_test


def validate_odd_row_regular_symmetry(rows,n,sigma):
    """Return odd order <=n, or None (untrusted/unsupported)."""
    rows=validate_sparse(rows,n)
    if sigma is None or len(sigma)!=n:return None
    if not all(type(x) is int and 0<=x<n for x in sigma):return None
    if len(set(sigma))!=n:return None
    sigma=tuple(sigma)
    source={tuple(sorted(row)) for row in rows}
    if {tuple(sorted(sigma[v] for v in row)) for row in rows}!=source:
        return None
    perm=tuple(range(n))
    order=None
    for t in range(1,n+1):
        perm=tuple(sigma[v] for v in perm)
        if perm==tuple(range(n)):
            order=t
            break
    if order is None or order%2==0 or order<=1:return None
    seen=set()
    for row in rows:
        canonical=tuple(sorted(row))
        if canonical in seen:continue
        current=canonical
        orb=[]
        while current not in orb:
            if current in seen:return None
            orb.append(current)
            current=tuple(sorted(sigma[v] for v in current))
        if current!=canonical:return None
        if order%len(orb)!=0 or len(orb)%2==0:return None
        seen.update(orb)
    if len(seen)!=len(source):return None
    return order


def certified_odd_symmetry_pc3(rows,n,sigma):
    order=validate_odd_row_regular_symmetry(rows,n,sigma)
    if order is None:
        return {'status':'UNKNOWN','reason':'SYMMETRY_MISSING_OR_NOT_CERTIFIED',
                'certificate':None}
    refuted,stats=pc3_symmetry_test(rows,tuple(sigma),order)
    if refuted:
        assert stats['verified_orbit_certificate_terms']>0
        return {'status':'UNSAT',
                'reason':'CROSS_CHECKED_ODD_GROUP_PC3_REFUTATION',
                'certificate_type':'SYMMETRY_ORBIT_GF2_PC3',
                'symmetry_order':order,'stats':stats}
    return {'status':'UNKNOWN',
            'reason':'FULL_DEGREE3_PC_INCONCLUSIVE',
            'symmetry_order':order,'stats':stats}


def main():
    from r5_universal_e118_c9_invariant_pc3 import equivariant_target
    from r5_universal_odd_automorphism_pc3_snark_probe import (
        automorphism_flower,direct_scl_action,
    )
    from r5_universal_cubic_flow_lowmoment_collision_20v import flower
    from r5_universal_certified_expert_portfolio import (
        SolveLinearCubicXSAT_Portfolio,
    )

    for name,a,b,sat in (('E118_UNSAT90',1,6,False),
                         ('E118_SAT90',1,2,True)):
        rows,ports,index,sigma=equivariant_target(a,b)
        n=len(rows)
        assert validate_odd_row_regular_symmetry(rows,n,sigma)==9
        res=certified_odd_symmetry_pc3(rows,n,sigma)
        assert (res['status']=='UNSAT')==(not sat)
        answer=SolveLinearCubicXSAT_Portfolio(
            rows,n,poly_only=True,pc3_max_n=0,
            bounded_states=0,certified_symmetry=sigma,
            sym_pc3_max_n=126,
        )
        assert answer['status']==res['status']
        if not sat:
            assert answer['expert']=='VERIFIED_ODD_SYMMETRY_PC3'
            assert answer['symmetry_order']==9
        else:
            assert answer['status']=='UNKNOWN'
        print(f'{name}: certified_symmetry_order=9 '
              f'portfolio_status={answer["status"]} expert={answer["expert"]}',
              flush=True)

    raw=flower(5)
    e=tuple(sorted(tuple(sorted(edge)) for edge in raw))
    rows,sigma=direct_scl_action(e,automorphism_flower(5),5)
    n=len(rows)
    assert n==90 and validate_odd_row_regular_symmetry(rows,n,sigma)==5
    verdict=SolveLinearCubicXSAT_Portfolio(
        rows,n,poly_only=True,pc3_max_n=0,bounded_states=0,
        certified_symmetry=sigma,sym_pc3_max_n=126,
    )
    assert verdict['status']=='UNSAT'
    assert verdict['expert']=='VERIFIED_ODD_SYMMETRY_PC3'
    print('J5_SNARK_SCL90_SYMMETRY_UNSAT_INTEGRATED=PASS',flush=True)

    # A non-automorphism or even-order symmetry may never certify UNSAT.
    damaged=list(sigma);damaged[0],damaged[1]=damaged[1],damaged[0]
    assert certified_odd_symmetry_pc3(rows,n,damaged)['status']=='UNKNOWN'
    invalid=SolveLinearCubicXSAT_Portfolio(
        rows,n,poly_only=True,pc3_max_n=0,bounded_states=0,
        certified_symmetry=damaged,sym_pc3_max_n=126,
    )
    assert invalid['status']=='UNKNOWN'
    print('UNTRUSTED_SYMMETRY_GUARD_RETURNS_UNKNOWN=VERIFIED',flush=True)

    print('ODD_GROUP_PC3_TRANSITIVE_EXPERT_INTEGRATION = VERIFIED_FINITE')
    print('ALL_INPUT_POLY_SOLVER = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=='__main__':
    main()
