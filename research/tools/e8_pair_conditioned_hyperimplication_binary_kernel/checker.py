#!/usr/bin/env python3
from collections import defaultdict, deque
from itertools import combinations, product


def canon_clause(C):
    C=frozenset(C)
    if any(-x in C for x in C):
        return None
    return C


def width3_closure(formula):
    clauses={canon_clause(c) for c in formula}
    clauses.discard(None)
    bylit=defaultdict(set)
    for C in clauses:
        for l in C:
            bylit[l].add(C)
    q=deque(list(clauses))
    while q:
        C=q.popleft()
        for l in tuple(C):
            for D in list(bylit.get(-l,())):
                R=(set(C)-{l}) | (set(D)-{-l})
                if any(-x in R for x in R) or len(R)>3:
                    continue
                R=frozenset(R)
                if R not in clauses:
                    clauses.add(R)
                    q.append(R)
                    for x in R:
                        bylit[x].add(R)
    return clauses


def unit_refutes(formula, assumptions):
    assign={}
    for lit in assumptions:
        v=abs(lit); val=(lit>0)
        if v in assign and assign[v]!=val:
            return True
        assign[v]=val
    changed=True
    while changed:
        changed=False
        for C in formula:
            sat=False
            unknown=[]
            for lit in C:
                v=abs(lit)
                if v in assign:
                    if assign[v]==(lit>0):
                        sat=True
                        break
                else:
                    unknown.append(lit)
            if sat:
                continue
            if not unknown:
                return True
            if len(unknown)==1:
                lit=unknown[0]
                v=abs(lit); val=(lit>0)
                if v in assign and assign[v]!=val:
                    return True
                if v not in assign:
                    assign[v]=val
                    changed=True
    return False


def eval_formula(F,bits):
    return all(any(bits[abs(l)-1]==(l>0) for l in C) for C in F)


def xor3_clauses(vars_, rhs):
    out=[]
    for vals in product((0,1), repeat=3):
        if (sum(vals)&1)==rhs:
            continue
        C=[]
        for v,a in zip(vars_,vals):
            C.append(v if a==0 else -v)
        out.append(frozenset(C))
    assert len(out)==4
    return out


def k4_tseitin():
    # Edges: 01,02,03,12,13,23 -> variables 1..6.
    inc={
        0:(1,2,3),
        1:(1,4,5),
        2:(2,4,6),
        3:(3,5,6),
    }
    charges={0:1,1:0,2:0,3:0}
    F=[]
    for v in range(4):
        F.extend(xor3_clauses(inc[v], charges[v]))
    return F


def main():
    # Strictness control.
    F=[
        frozenset((1,2,5)),
        frozenset((3,-4,-2)),
        frozenset((3,-4,-5)),
        frozenset((3,-4,-1)),
    ]
    W=width3_closure(F)
    target=frozenset((3,-4))
    assert target not in W
    assert not unit_refutes(F,(4,))
    assert not unit_refutes(F,(-3,))
    assert unit_refutes(F,(4,-3))
    # Semantic check of the derived binary consequence.
    sats=0
    for bits in product((False,True), repeat=5):
        if eval_formula(F,bits):
            sats += 1
            assert (not bits[3]) or bits[2]  # x4 -> x3
    assert sats>0

    # Explicit pair-probe-resistant UNSAT control.
    T=k4_tseitin()
    assert len(T)==16
    assert not any(eval_formula(T,bits) for bits in product((False,True), repeat=6))
    WT=width3_closure(T)
    assert WT==set(T)
    assert all(len(C)==3 for C in WT)

    lits=list(range(1,7))+list(range(-1,-7,-1))
    probes=0
    for p in lits:
        probes += 1
        assert not unit_refutes(T,(p,))
    for p,q in combinations(lits,2):
        if p==-q:
            continue
        probes += 1
        assert not unit_refutes(T,(p,q))

    print('PASS_PAIR_CONDITIONED_HYPERIMPLICATION_BINARY_KERNEL')
    print('strictness_binary=(NOT4 OR 3) width3_absent=True pair_probe_derived=True')
    print('strictness_sat_models=',sats)
    print('K4_Tseitin_clauses=16 width3_closure=16 pair_probes=',probes)
    print('K4_Tseitin_UNSAT=True pair_probe_silent=True')
    print('E8_D1=EMPTY P_VS_NP=OPEN')


if __name__=='__main__':
    main()
