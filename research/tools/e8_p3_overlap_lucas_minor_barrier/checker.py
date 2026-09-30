#!/usr/bin/env python3
"""Exact integer regression for the P3-overlap Lucas determinant barrier."""


def det_bareiss(A):
    A=[list(map(int,row)) for row in A]
    n=len(A)
    if n==0: return 1
    sign=1; prev=1
    for k in range(n-1):
        p=next((r for r in range(k,n) if A[r][k]!=0),None)
        if p is None: return 0
        if p!=k:
            A[k],A[p]=A[p],A[k]; sign=-sign
        pivot=A[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                num=A[i][j]*pivot-A[i][k]*A[k][j]
                assert num%prev==0
                A[i][j]=num//prev
        for i in range(k+1,n): A[i][k]=0
        prev=pivot
    return sign*A[-1][-1]


def lucas(n):
    a,b=2,1
    if n==0:return a
    if n==1:return b
    for _ in range(2,n+1): a,b=b,a+b
    return b


def family(n):
    # C_i = (x_i OR x_{i+1} OR NOT x_{i+2}), indices mod n.
    clauses=[]
    for i in range(n):
        clauses.append(((i,+1),((i+1)%n,+1),((i+2)%n,-1)))
    cols=[]; byvar={j:{+1:[],-1:[]} for j in range(n)}
    for ci,C in enumerate(clauses):
        crow=[]
        for var,sgn in C:
            col=len(cols); cols.append((ci,var,sgn)); crow.append(col)
            byvar[var][sgn].append(col)
        assert len(crow)==3
    q=3*n
    Q=[]
    for ci in range(n):
        row=[0]*q
        for col,(cj,_,_) in enumerate(cols):
            if cj==ci: row[col]=1
        Q.append(row)
    for var in range(n):
        pos=byvar[var][+1]; neg=byvar[var][-1]
        assert len(pos)==2 and len(neg)==1
        m=neg[0]
        for p in pos:
            row=[0]*q; row[p]=1; row[m]=1; Q.append(row)
    assert len(Q)==q

    B=[[0]*n for _ in range(n)]
    for i,C in enumerate(clauses):
        for var,sgn in C: B[i][var]=sgn
    return clauses,Q,B


def expected(n):
    return 1 + ((-1)**n)*(1-lucas(n))


def main():
    # Full 3n x 3n exact determinant checks.
    for n in range(4,11):
        clauses,Q,B=family(n)
        # all-true assignment satisfies via one of the first two positive literals
        assert all(any(sgn==1 for _,sgn in C) for C in clauses)
        dQ=det_bareiss(Q); dB=det_bareiss(B); e=expected(n)
        assert dB==e, (n,dB,e)
        assert abs(dQ)==abs(dB), (n,dQ,dB)

    # Longer exact quotient checks establish the Lucas closed form numerically.
    vals=[]
    for n in range(4,21):
        _,_,B=family(n)
        d=det_bareiss(B); e=expected(n)
        assert d==e
        vals.append((n,abs(d),lucas(n)))
        if n%2: assert abs(d)==lucas(n)
        else: assert abs(d)==lucas(n)-2

    assert vals[-1][1]>1000
    print('PASS_P3_OVERLAP_EXPONENTIAL_MINOR_LUCAS_BARRIER')
    print('checked_full_Q_n=4..10 quotient_B_n=4..20')
    print('det_formula=1+(-1)^n*(1-L_n)')
    print('last=',vals[-1])
    print('BOUNDED_DELTA_SHORTCUT=FALSE')
    print('P_VS_NP=OPEN E8_D1=EMPTY')


if __name__=='__main__': main()
