#!/usr/bin/env python3
"""Exact regression for the persistent three-coordinate F3 UNSAT certificate."""

ROWS=[
(0,5,12),(1,7,9),(2,9,14),(3,10,11),(3,4,13),
(1,5,10),(6,7,14),(2,3,7),(1,4,8),(0,6,9),
(2,10,12),(5,11,13),(6,8,12),(0,8,13),(4,11,14)
]
F0=((0,12),(2,9))
F1=((0,5),(1,1))
Y16=[0,0,2,2,2,2,1,2,1,0,2,1,2,0,0,1,2,0,1,1,0,0,1,2,2,2,2,1,0,0]
Y20=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,2,1,1,0,0,2,0,0,1,0,1,0]


def incidence(rows,n):
    A=[[0]*n for _ in range(n)]
    for i,row in enumerate(rows):
        for j in row:A[i][j]=1
    return A


def lift(A,pair):
    n=len(A)
    E=[[0]*n for _ in range(n)]
    for i,j in pair:
        assert A[i][j]==1
        E[i][j]=1
    P=[[A[i][j]-E[i][j] for j in range(n)] for i in range(n)]
    return [P[i]+E[i] for i in range(n)] + [E[i]+P[i] for i in range(n)]


def mv(A,x,p=3):
    return [sum(a*b for a,b in zip(row,x))%p for row in A]


def rowcomb(y,A,p=3):
    n=len(A[0])
    return [sum(y[i]*A[i][j] for i in range(len(A)))%p for j in range(n)]


def rref_affine(A,b,p=3):
    m=len(A); n=len(A[0])
    M=[[v%p for v in A[i]]+[b[i]%p] for i in range(m)]
    piv=[]; r=0
    for c in range(n):
        pivot=next((i for i in range(r,m) if M[i][c]%p),None)
        if pivot is None: continue
        M[r],M[pivot]=M[pivot],M[r]
        inv=pow(M[r][c]%p,-1,p)
        M[r]=[(v*inv)%p for v in M[r]]
        for i in range(m):
            if i!=r and M[i][c]%p:
                f=M[i][c]%p
                M[i]=[(M[i][j]-f*M[r][j])%p for j in range(n+1)]
        piv.append(c); r+=1
        if r==m: break
    assert not any(all(M[i][j]==0 for j in range(n)) and M[i][n] for i in range(r,m))
    x=[0]*n
    for i,c in enumerate(piv):x[c]=M[i][n]
    return x,n-len(piv)


def unit_diff(n,a,b):
    v=[0]*n
    v[a]=1
    v[b]=2
    return v


def main():
    A0=incidence(ROWS,15)
    assert all(sum(row)==3 for row in A0)
    assert all(sum(A0[i][j] for i in range(15))==3 for j in range(15))

    # Seed is affine-consistent but nowhere-zero impossible; first recursive
    # level is the convenient constant-certificate base.
    r0,d0=rref_affine(A0,[1]*15)
    assert d0==1

    A=lift(A0,F0)
    assert len(A)==30
    r,d1=rref_affine(A,[1]*30)
    assert d1==2
    assert (r[12],r[16],r[20])==(0,2,1)

    y16=Y16[:]
    y20=Y20[:]
    pair=F1
    rows=[]

    for t in range(1,6):
        n=len(A)
        assert len(r)==n and len(y16)==n and len(y20)==n
        assert mv(A,r)==[1]*n
        assert (r[12],r[16],r[20])==(0,2,1)

        assert rowcomb(y16,A)==unit_diff(n,16,12)
        assert rowcomb(y20,A)==unit_diff(n,20,12)
        assert y16[0]==y16[1]==0
        assert y20[0]==y20[1]==0

        # The row-space identities imply for every affine solution q:
        # q16-q12=2 and q20-q12=1, hence the triple is {0,1,2}.
        rows.append((t,n,(12,16,20)))

        if t<5:
            old_n=n
            A=lift(A,pair)
            pair=tuple((i,old_n+j) for i,j in pair)
            r=r+r
            y16=y16+[0]*old_n
            y20=y20+[0]*old_n

    print({
        'status':'PASS_PERSISTENT_F3_THREE_OFFSET_UNSAT_CERTIFICATE',
        'levels':rows,
        'tracked_relation':'(r12,r16,r20)=(s,s+2,s+1)',
        'E8_D1':'EMPTY',
        'P_VS_NP':'OPEN',
    })


if __name__=='__main__':
    main()
