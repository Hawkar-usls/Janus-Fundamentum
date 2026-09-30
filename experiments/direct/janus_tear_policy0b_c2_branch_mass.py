#!/usr/bin/env python3
"""Finite provider replay for the C025-C2 branch-mass progress gate."""
from __future__ import annotations


def restrict_once(cnf, var, value):
    out=[]
    for clause in cnf:
        residual=[]; sat=False
        for lit in clause:
            if abs(lit)!=var:
                residual.append(lit); continue
            lv=value if lit>0 else 1-value
            if lv:
                sat=True; break
        if not sat:
            out.append(tuple(residual))
    return tuple(out)


def litvol(cnf):
    return sum(map(len,cnf))


def main():
    for u in range(1,33):
        assert 2**(u-1)+2**(u-1)==2**u
    for u in range(3,33):
        assert 2*(u-1)>u

    parent=[(1,2),(-1,3)]
    v=4
    for _ in range(4):
        parent.append((v,v+1)); v+=2
    parent=tuple(parent)
    c0=restrict_once(parent,1,0)
    c1=restrict_once(parent,1,1)
    assert len(c0)+len(c1)>len(parent)
    assert litvol(c0)+litvol(c1)>litvol(parent)

    for n in range(8,21):
        B=n*n
        assert 2**B>n**10

    # Tiny telescoping witness for the sufficient frontier lemma mechanics.
    rank={'r':7,'a':3,'b':3,'a0':1,'a1':1,'b0':1,'b1':1}
    children={
        'r':('a','b'),
        'a':('a0','a1'),
        'b':('b0','b1'),
        'a0':(), 'a1':(), 'b0':(), 'b1':(),
    }
    frontier=['r']; expanded=0; phi=rank['r']
    while frontier:
        node=frontier.pop(0)
        kids=children[node]
        if not kids:
            continue
        assert sum(rank[k] for k in kids)<=rank[node]-1
        frontier.extend(kids); expanded+=1
        newphi=sum(rank[x] for x in frontier)
        assert newphi<=phi-1
        phi=newphi
    assert expanded<=rank['r']

    print('C025_C2_RAW_ASSIGNMENT_MASS_CONSERVATION = PASS')
    print('C025_C2_UNASSIGNED_COUNT_POTENTIAL = REFUTED_FINITE')
    print('C025_C2_CLAUSE_COUNT_POTENTIAL = REFUTED_FINITE')
    print('C025_C2_LITERAL_VOLUME_POTENTIAL = REFUTED_FINITE')
    print('C025_C2_NAIVE_POLY_BIT_PROOF_ENUMERATION = SUPERPOLY_FINITE_WITNESS_PASS')
    print('C025_C2_FRONTIER_TELESCOPING_MECHANICS = PASS')
    print('C025_C2_USEFUL_POLY_BOUNDED_FRONTIER_POTENTIAL = OPEN')
    print('C025_C2_DETERMINISTIC_DISCOVERY = OPEN')
    print('P_VS_NP = OPEN')


if __name__=='__main__':
    main()
