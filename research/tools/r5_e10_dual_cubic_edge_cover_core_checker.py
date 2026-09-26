#!/usr/bin/env python3
from itertools import combinations

EPLUS=[(0,4),(0,6),(0,2),(1,2),(1,5),(1,3),(2,4),(3,4),(3,7),(5,7),(5,6),(6,7)]
EMINUS=[(2,6),(0,4),(3,5),(2,3),(1,7),(6,7),(0,6),(1,5),(1,3),(0,2),(4,7),(4,5)]

def degrees(edges, labels):
    n=1+max(max(e) for e in edges)
    d=[0]*n
    for i in labels:
        u,v=edges[i]; d[u]+=1; d[v]+=1
    return d

def cover(edges, labels):
    return all(x>=1 for x in degrees(edges,labels))

def formula_sat(mask):
    m=len(EPLUS)
    T={i for i in range(m) if (mask>>i)&1}
    C=set(range(m))-T
    return cover(EPLUS,T) and cover(EMINUS,C)

def perfect_matchings(edges):
    n=1+max(max(e) for e in edges)
    m=len(edges)
    out=[]
    for comb in combinations(range(m),n//2):
        if all(x==1 for x in degrees(edges,comb)):
            out.append(set(comb))
    return out

def main():
    assert all(x==3 for x in degrees(EPLUS,range(len(EPLUS))))
    assert all(x==3 for x in degrees(EMINUS,range(len(EMINUS))))
    sats=[mask for mask in range(1<<len(EPLUS)) if formula_sat(mask)]
    assert sats
    witness=279
    assert formula_sat(witness)
    T={i for i in range(len(EPLUS)) if (witness>>i)&1}
    C=set(range(len(EPLUS)))-T
    assert cover(EPLUS,T)
    assert cover(EMINUS,C)
    P=perfect_matchings(EPLUS)
    M=perfect_matchings(EMINUS)
    assert len(P)==5 and len(M)==5
    assert not any(a.isdisjoint(b) for a in P for b in M)
    print(f'ASSIGNMENTS_CHECKED = {1<<len(EPLUS)}')
    print(f'SAT_ASSIGNMENTS = {len(sats)}')
    print('CROSSED_EDGE_COVER_WITNESS_MASK = 279')
    print('PERFECT_MATCHINGS_PLUS = 5')
    print('PERFECT_MATCHINGS_MINUS = 5')
    print('DISJOINT_PERFECT_MATCHING_SHORTCUT = FALSIFIED')
    print('D1 = EMPTY')
    print('P_VS_NP = OPEN')

if __name__=='__main__':
    main()
