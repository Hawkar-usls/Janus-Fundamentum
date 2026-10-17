#!/usr/bin/env python3
from itertools import product

V=list(range(7))
E=[(0,2),(0,4),(0,5),(0,6),(1,2),(1,4),(1,5),(1,6),(2,3),(2,5),(3,4),(3,5),(3,6),(4,6)]
H=[0,4,1,2,5,3,6,0]
Q=[0,2,3,4,6,1,5,0]
COL=[0,0,1,0,1,2,2]


def cycle_edges(cyc):
    return {tuple(sorted((cyc[i],cyc[i+1]))) for i in range(len(cyc)-1)}


def central_coeff():
    total=0
    hits=0
    for choices in product((0,1), repeat=len(E)):
        exp=[0]*len(V)
        sign=1
        for (u,v),pick_hi in zip(E,choices):
            u,v=sorted((u,v))
            if pick_hi:
                exp[v]+=1
                sign=-sign
            else:
                exp[u]+=1
        if exp==[2]*len(V):
            hits+=1
            total+=sign
    return total,hits


def main():
    deg=[0]*len(V)
    for u,v in E:
        deg[u]+=1;deg[v]+=1
        assert COL[u]!=COL[v]
    assert deg==[4]*len(V)
    he=cycle_edges(H); qe=cycle_edges(Q)
    assert he.isdisjoint(qe)
    assert he|qe=={tuple(sorted(e)) for e in E}
    c,hits=central_coeff()
    assert hits==60
    assert c==0
    print('PASS: 7-vertex Hamiltonian 4-regular graph is 3-colourable but central Alon-Tarsi coefficient is zero')

if __name__=='__main__':
    main()
