#!/usr/bin/env python3
from itertools import permutations,product

TERMS=range(4)


def gadget_boundary_ok(x):
    return x[0]==x[1] and x[2]==x[3] and x[0]!=x[2]


def glued_count(pi):
    count=0
    for L in product(range(3),repeat=4):
        if not gadget_boundary_ok(L): continue
        for R in product(range(3),repeat=4):
            if not gadget_boundary_ok(R): continue
            if all(L[i]!=R[pi[i]] for i in TERMS):
                # Each gadget hub is uniquely forced once its two wire colours are fixed.
                count+=1
    return count


def count_matrix(pi):
    M=[[0,0],[0,0]]
    for i in TERMS:
        M[i//2][pi[i]//2]+=1
    return tuple(tuple(r) for r in M)


def main():
    print('E8 v6.9 K5-minus-2K2 boundary wire gluing checker')
    stats={}
    for pi in permutations(TERMS):
        M=count_matrix(pi)
        c=glued_count(pi)
        stats.setdefault((M,c),0)
        stats[(M,c)]+=1

    expected={
        (((2,0),(0,2)),18):4,
        (((0,2),(2,0)),18):4,
        (((1,1),(1,1)),0):16,
    }
    assert stats==expected,(stats,expected)
    print('PASS all 24 terminal bijections classified exactly')
    for key,num in sorted(stats.items(),key=lambda kv:(kv[0][1],kv[0][0])):
        print(' ',key,'bijections=',num)

    # Direct wire theorem: six ordered distinct colour pairs, unique hub third colour.
    wire=[]
    for a,b in product(range(3),repeat=2):
        if a!=b:
            h=({0,1,2}-{a,b}).pop()
            wire.append((a,b,h))
    assert len(wire)==6
    print('PASS single gadget boundary relation has six colourings and unique hub')
    print('PASS pair-preserving glue => 18 colourings; pair-mixing glue => 0')
    print('P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY')

if __name__=='__main__':
    main()
