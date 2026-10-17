#!/usr/bin/env python3
"""Exact controls for the AF3 one-zero -2 binary augmentation theorem."""
from itertools import product

SAT_ROWS=[
(1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),(3,4,7),
(3,5,6),(4,9,13),(4,10,14),(5,8,13),(5,10,15),(6,8,14),
(6,9,15),(7,8,15),(7,11,12)]
P=[5,7,9,10,3,1,14,2,4,6,12,13,8,0,11]
Q=[12,9,14,11,13,10,7,3,1,0,2,5,6,8,4]
R_SAT=[2,2,0,2,2,2,2,1,1,1,1,1,1,1,1]
R_UNSAT=[1,0,1,1,2,2,1,2,2,2,2,1,1,1,1]

def matrix_from_rows(rows): return [[int(j+1 in row) for j in range(15)] for row in rows]
def unsat_matrix():
    A=[[0]*15 for _ in range(15)]
    for i in range(15):
        for j in (i,P[i],Q[i]): A[i][j]=1
    return A

def kernel_basis(A,p=2):
    M=[[v%p for v in row] for row in A]; m=len(M); n=len(M[0]); r=0; piv=[]
    for c in range(n):
        k=next((i for i in range(r,m) if M[i][c]),None)
        if k is None: continue
        M[r],M[k]=M[k],M[r]
        inv=pow(M[r][c],-1,p); M[r]=[(x*inv)%p for x in M[r]]
        for i in range(m):
            if i!=r and M[i][c]:
                f=M[i][c]; M[i]=[(M[i][j]-f*M[r][j])%p for j in range(n)]
        piv.append(c); r+=1
    free=[j for j in range(n) if j not in piv]
    B=[]
    for f in free:
        x=[0]*n; x[f]=1
        for i,c in enumerate(piv): x[c]=(-M[i][f])%p
        B.append(x)
    return B

def kernel_words(A):
    B=kernel_basis(A,2); n=len(A[0]); out=[]
    for co in product((0,1),repeat=len(B)):
        x=[0]*n
        for a,v in zip(co,B):
            if a: x=[xx^vv for xx,vv in zip(x,v)]
        out.append(x)
    return out

def check(A,r,expect_improving):
    n=len(A); zero=[i for i,v in enumerate(r) if v==0]
    assert len(zero)==1; i=zero[0]
    assert all(sum(row[j]*r[j] for j in range(n))%3==1 for row in A)

    b=[int(v==2) for v in r]
    x0=b[:]; x0[i]=1
    defects=[rr for rr,row in enumerate(A) if row[i]]
    assert len(defects)==3
    assert all(sum(A[rr][j]*x0[j] for j in range(n))==3 for rr in defects)
    assert all(sum(A[rr][j]*x0[j] for j in range(n))==1 for rr in range(n) if rr not in defects)
    assert sum(x0)==n//3+2
    S={j for j,v in enumerate(x0) if v}

    improving=[]
    for z in kernel_words(A):
        C={j for j,v in enumerate(z) if v}; c=len(C); q=len(C&S)
        t=w=0
        for rr,row in enumerate(A):
            pair=[j for j,a in enumerate(row) if a and j in C]
            assert len(pair) in (0,2)
            if len(pair)==2:
                if rr in defects: t+=1
                elif all(j not in S for j in pair): w+=1
        delta=c-2*q
        assert 3*delta==2*(w-t)
        if delta<0:
            assert (delta,t,w)==(-2,3,0)
            x=[a^b for a,b in zip(x0,z)]
            assert sum(x)==n//3
            assert all(sum(row[j]*x[j] for j in range(n))==1 for row in A)
            improving.append(tuple(x))

    assert len(improving)==expect_improving
    return {'zero_index':i,'defect_rows':defects,'kernel_words':len(kernel_words(A)),'improving_moves':len(improving),'witnesses':len(set(improving))}

def main():
    sat=check(matrix_from_rows(SAT_ROWS),R_SAT,4)
    unsat=check(unsat_matrix(),R_UNSAT,0)
    print({'status':'PASS_AF3_ONE_ZERO_MINUS2_AUGMENTATION','PG15':sat,'UNSAT15':unsat})
    print('E8_D1 = EMPTY')
    print('P_VS_NP = OPEN')

if __name__=='__main__': main()
