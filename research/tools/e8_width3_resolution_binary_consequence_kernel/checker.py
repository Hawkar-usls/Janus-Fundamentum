#!/usr/bin/env python3
"""Exact regression for width-3 resolution binary-consequence extraction."""

from itertools import product, combinations
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent / 'e8_terminal_rank3_implication_primitive_normal_form' / 'checker.py'
spec=importlib.util.spec_from_file_location('v38',PARENT)
v38=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(v38)


def canon(c):
    s=set(c)
    if any(-l in s for l in s): return None
    return frozenset(s)


def width3_closure(F):
    clauses=set()
    parent={}
    for c in F:
        q=canon(c)
        if q is not None and len(q)<=3:
            clauses.add(q)
    changed=True
    while changed:
        changed=False
        arr=list(clauses)
        for i,A in enumerate(arr):
            for B in arr[i+1:]:
                pivots=[x for x in A if -x in B]
                for x in pivots:
                    R=canon((set(A)-{x}) | (set(B)-{-x}))
                    if R is None or len(R)>3: continue
                    if R not in clauses:
                        clauses.add(R)
                        parent[R]=(A,B,x)
                        changed=True
                        if len(R)==0:
                            return clauses,parent
    return clauses,parent


def sat(F): return v38.satisfiable([tuple(c) for c in F])


def augmented_normal_form(F):
    closure,parent=width3_closure(F)
    if frozenset() in closure:
        return [tuple()],closure,parent
    binary=[tuple(sorted(C,key=lambda x:(abs(x),x<0))) for C in closure if len(C)<=2]
    # Keep original ternary clauses; derived ternaries were only internal proof states.
    orig3=[]
    for c in F:
        q=canon(c)
        if q is not None and len(q)==3:
            orig3.append(tuple(sorted(q,key=lambda x:(abs(x),x<0))))
    N=v38.primitive_normal_form(binary+orig3)
    return N,closure,parent


def exhaustive():
    vars_=(1,2,3,4)
    pool=[]
    for size in (2,3):
        for vs in combinations(vars_,size):
            for signs in product((1,-1), repeat=size):
                pool.append(tuple(s*v for s,v in zip(signs,vs)))
    checked=0; refuted=0; enriched=0
    # All formulas with up to three distinct clauses: >29k exact controls.
    for r in range(4):
        for ids in combinations(range(len(pool)),r):
            F=[pool[i] for i in ids]
            N,C,_=augmented_normal_form(F)
            before=sat(F); after=sat(N)
            assert before==after,(F,N)
            if frozenset() in C:
                assert not before
                refuted+=1
            base_binary={frozenset(c) for c in F if len(c)<=2}
            derived_binary={c for c in C if len(c)<=2}
            if derived_binary-base_binary:
                enriched+=1
            checked+=1
    return checked,refuted,enriched


def targeted():
    F=[(1,2,3),(1,2,-3)]
    N,C,_=augmented_normal_form(F)
    assert frozenset((1,2)) in C
    assert sat(F)==sat(N)
    # Both ternary clauses become redundant relative to the derived binary clause.
    assert all(len(c)<=2 for c in N),N

    # Width-3 refutable control.
    U=[(1,2,3),(1,2,-3),(1,-2,3),(1,-2,-3),
       (-1,2,3),(-1,2,-3),(-1,-2,3),(-1,-2,-3)]
    N,C,_=augmented_normal_form(U)
    assert frozenset() in C
    assert not sat(U) and not sat(N)


def main():
    checked,refuted,enriched=exhaustive(); targeted()
    print('PASS_WIDTH3_RESOLUTION_BINARY_CONSEQUENCE_KERNEL')
    print(f'exhaustive_formulas_checked={checked}')
    print(f'width3_refutations={refuted}')
    print(f'instances_with_new_binary_consequence={enriched}')
    print('SAT_equivalence=True')
    print('E8_D1=EMPTY P_VS_NP=OPEN')


if __name__=='__main__': main()
