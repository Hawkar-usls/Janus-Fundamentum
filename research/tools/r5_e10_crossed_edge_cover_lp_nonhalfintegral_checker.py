#!/usr/bin/env python3
from fractions import Fraction as Q

EPLUS=[(0,1),(0,2),(0,5),(1,2),(1,3),(2,4),(3,4),(3,5),(4,5)]
EMINUS=[(0,3),(2,3),(2,5),(1,2),(1,4),(4,5),(0,4),(0,5),(1,3)]
X=[Q(0),Q(1),Q(0),Q(1),Q(1,3),Q(0),Q(1,3),Q(1,3),Q(2,3)]

def incident(edges,v): return [i for i,e in enumerate(edges) if v in e]

def rank(A):
    A=[row[:] for row in A]
    if not A: return 0
    r=0
    for c in range(len(A[0])):
        p=next((i for i in range(r,len(A)) if A[i][c]),None)
        if p is None: continue
        A[r],A[p]=A[p],A[r]
        z=A[r][c]
        A[r]=[a/z for a in A[r]]
        for i in range(len(A)):
            if i!=r and A[i][c]:
                z=A[i][c]
                A[i]=[A[i][j]-z*A[r][j] for j in range(len(A[i]))]
        r+=1
        if r==len(A): break
    return r

def main():
    assert all(len(incident(EPLUS,v))==3 for v in range(6))
    assert all(len(incident(EMINUS,v))==3 for v in range(6))
    # LP feasibility: plus-star red coverage >=1; minus-star red degree <=2.
    ps=[sum(X[i] for i in incident(EPLUS,v)) for v in range(6)]
    ms=[sum(X[i] for i in incident(EMINUS,v)) for v in range(6)]
    assert all(z>=1 for z in ps)
    assert all(z<=2 for z in ms)
    assert all(Q(0)<=z<=Q(1) for z in X)
    # Active equalities.
    rows=[]
    for v,z in enumerate(ps):
        if z==1:
            row=[Q(0)]*9
            for i in incident(EPLUS,v): row[i]=1
            rows.append(row)
    for v,z in enumerate(ms):
        if z==2:
            row=[Q(0)]*9
            for i in incident(EMINUS,v): row[i]=1
            rows.append(row)
    for i,z in enumerate(X):
        if z in (0,1):
            row=[Q(0)]*9; row[i]=1; rows.append(row)
    assert rank(rows)==9
    assert any(z.denominator==3 for z in X)
    print('CUBIC_PAIR = PASS')
    print('LP_FEASIBLE = PASS')
    print('ACTIVE_CONSTRAINT_RANK = 9')
    print('EXTREME_POINT = PASS')
    print('HALF_INTEGRALITY = FALSIFIED')
    print('EXTREME_POINT = 0,1,0,1,1/3,0,1/3,1/3,2/3')
    print('D1 = EMPTY')
    print('P_VS_NP = OPEN')

if __name__=='__main__': main()
