#!/usr/bin/env python3
from itertools import product

P=3
N=8
H=[(i,(i+1)%N) for i in range(N)]
C4S=[(0,3,1,6),(2,4,7,5)]
EXTRA=[]
for cyc in C4S:
    EXTRA.extend((cyc[i],cyc[(i+1)%4]) for i in range(4))
EDGES={tuple(sorted(e)) for e in H+EXTRA}

X=[
[1,0,0,0,0,0,0,0,0],
[0,1,1,2,0,0,0,0,0],
[0,1,1,0,0,0,0,0,0],
[0,2,0,1,0,0,0,0,0],
[0,0,0,0,1,0,0,0,0],
[0,0,0,0,0,1,0,0,0],
[0,0,0,0,0,0,1,0,0],
[0,0,0,0,0,0,0,1,0],
[0,0,0,0,0,0,0,0,1],
]

def rank_mod(A):
    A=[row[:] for row in A]
    r=0
    for c in range(len(A[0])):
        piv=next((i for i in range(r,len(A)) if A[i][c]%P),None)
        if piv is None: continue
        A[r],A[piv]=A[piv],A[r]
        inv=1 if A[r][c]%P==1 else 2
        A[r]=[(inv*v)%P for v in A[r]]
        for i in range(len(A)):
            if i!=r and A[i][c]%P:
                f=A[i][c]%P
                A[i]=[(A[i][j]-f*A[r][j])%P for j in range(len(A[0]))]
        r+=1
    return r

def three_colorable():
    for col in product(range(3), repeat=N):
        if all(col[u]!=col[v] for u,v in EDGES):
            return True,col
    return False,None

def interval(u,v):
    ell=[0]*N
    i=u
    while i!=v:
        ell[i]=1
        i=(i+1)%N
    return ell

def y_forms(cyc):
    a=[interval(cyc[j],cyc[(j+1)%4]) for j in range(4)]
    out=[]
    for k in (1,2,3):
        out.append([(-(a[0][i]+a[k][i]))%P for i in range(N)])
    return out

def quad(ell,Xt):
    s=0
    for i in range(N):
        for j in range(N):
            s=(s+ell[i]*Xt[i][j]*ell[j])%P
    return s

def main():
    deg=[0]*N
    for u,v in EDGES:
        deg[u]+=1;deg[v]+=1
    assert deg==[4]*N
    ok,_=three_colorable()
    assert not ok

    assert rank_mod(X)==9
    assert all(X[i][i]%P==1 for i in range(9))
    assert sum(X[0][1:])%P==0
    Xt=[row[1:] for row in X[1:]]
    for cyc in C4S:
        val=sum(quad(ell,Xt) for ell in y_forms(cyc))%P
        assert val==1,(cyc,val)

    print('PASS: explicit 8-vertex non-3-colourable C4 source passes linear moment relaxation at rank 9')

if __name__=='__main__':
    main()
