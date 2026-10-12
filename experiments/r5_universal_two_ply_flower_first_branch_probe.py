#!/usr/bin/env python3
"""Frozen partial J5/J7 two-ply adversarial branch diagnostic.

Evaluate one outer variable x_0 in both Boolean states after the
unconditional certified one-ply root test. A child is itself the
polynomial exhaustive single-assumption closure. A pair of UNSAT
children proves whole source UNSAT; a child SAT must provide and
verify a full original Boolean witness. If they are UNKNOWN the
correct status is ONLY 'SELECTED_BRANCH_OPEN', not full two-ply
closure incompleteness. No n-dependent depth search is allowed.
"""
from __future__ import annotations
import os
from r5_universal_cubic_flow_lowmoment_collision_20v import flower
from r5_universal_cubic_edgecolor_direct_scl_bridge import make_scl
from r5_universal_certified_failed_literal_boolean_closure import (
    certified_failed_literal_closure,verify_probe_certificate,
    check_original_witness,
)


def main():
    k=int(os.environ.get('FLOWER_K','5'))
    assert k in (5,7)
    rows,n,_,_=make_scl(flower(k))
    root=certified_failed_literal_closure(rows,n)
    assert verify_probe_certificate(rows,n,{},root)
    assert root['status'] in ('UNSAT','UNKNOWN')
    print(f'FLOWER_J{k}_ONE_PLY_ROOT={root["status"]}',flush=True)
    if root['status']=='UNSAT':
        return
    results=[]
    for b in (0,1):
        assumptions={0:b}
        child=certified_failed_literal_closure(rows,n,assumptions)
        assert verify_probe_certificate(rows,n,assumptions,child)
        assert child['status'] in ('UNSAT','UNKNOWN')
        results.append(child['status'])
        print(f'FLOWER_J{k}_TWO_PLY_FIRST_VARIABLE_{b}='
              f'{child["status"]} calls={child["probes"]}',
              flush=True)
    if results==['UNSAT','UNSAT']:
        print(f'FLOWER_J{k}_FIRST_VARIABLE_TWO_CASE_UNSAT=PROVED',
              flush=True)
    else:
        print(f'FLOWER_J{k}_SELECTED_BRANCH_OPEN_NOT_GLOBAL_DEPTH2_BARRIER',
              flush=True)
    print('UNIVERSAL_POLY_SOLVER=NOT_CONSTRUCTED')
    print('P_VS_NP=OPEN')


if __name__=='__main__':
    main()
