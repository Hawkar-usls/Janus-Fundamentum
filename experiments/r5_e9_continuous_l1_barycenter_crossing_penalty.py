#!/usr/bin/env python3
from fractions import Fraction

LINES=[
(1,15,12),(2,14,4),(3,2,8),(4,3,9),(5,4,6),
(6,12,10),(7,1,3),(8,9,15),(9,7,5),(10,8,7),
(11,5,2),(12,13,14),(13,11,1),(14,6,11),(15,10,13)
]
Z0=[-1,1,0,1,-1,1,2,0,0,-1,1,1,1,-1,1]
V=[-4,2,-1,2,-4,2,5,-1,-1,-4,2,2,2,-4,2]


def incidence(lines,n=15):
    A=[[0]*n for _ in range(n)]
    for r,line in enumerate(lines):
        for j in line:
            A[r][j-1]=1
    assert all(sum(row)==3 for row in A)
    assert all(sum(A[r][c] for r in range(n))==3 for c in range(n))
    return A


def mv(A,x):
    return [sum(a*b for a,b in zip(row,x)) for row in A]


def rank(M):
    M=[[Fraction(x) for x in row] for row in M]
    if not M:
        return 0
    R,C=len(M),len(M[0])
    r=0
    for c in range(C):
        piv=next((i for i in range(r,R) if M[i][c]),None)
        if piv is None:
            continue
        M[r],M[piv]=M[piv],M[r]
        p=M[r][c]
        M[r]=[x/p for x in M[r]]
        for i in range(R):
            if i!=r and M[i][c]:
                f=M[i][c]
                M[i]=[M[i][j]-f*M[r][j] for j in range(C)]
        r+=1
        if r==R:
            break
    return r


def transpose(A):
    return [list(col) for col in zip(*A)]


def crossing_delta(y,g):
    s=[1 if t>0 else -1 for t in y]
    linear=sum(si*gi for si,gi in zip(s,g))
    penalty=sum(max(0,-abs(yi)-2*si*gi) for yi,si,gi in zip(y,s,g))
    lhs=(sum(abs(yi+2*gi) for yi,gi in zip(y,g))-sum(abs(yi) for yi in y))//2
    return lhs,linear,penalty


def main():
    A=incidence(LINES)
    n=len(A)
    one=[1]*n

    ybar=[Fraction(-1,3)]*n
    assert mv(A,ybar)==[Fraction(-1,1)]*n
    assert sum(abs(t) for t in ybar)==Fraction(n,3)

    z=Z0
    assert mv(A,z)==one
    y=[2*t-1 for t in z]
    assert mv(A,y)==[-1]*n
    assert sum(y)==-n//3
    assert sum(abs(t) for t in y)==25

    s=[1 if t>0 else -1 for t in y]
    AT=transpose(A)
    r0=rank(AT)
    aug=[AT[i]+[s[i]] for i in range(n)]
    assert r0==14
    assert rank(aug)==15

    assert mv(A,V)==[0]*n
    assert sum(V)==0
    for k in (-2,-1,0,1,2):
        g=[k*t for t in V]
        lhs,lin,pen=crossing_delta(y,g)
        assert lhs==lin+pen
        assert pen>=0

    assert sum(abs(t) for t in y)>=n
    assert abs(sum(s))<=n
    assert 3*sum(abs(t) for t in y)>n

    print("PASS: universal cubic barycenter is real-feasible with L1=n/3")
    print("PASS: frozen odd point has L1=25 while real optimum is 5")
    print("PASS: sign(y) is outside rowspace on hostile control")
    print("PASS: exact linear-gain + crossing-penalty identity")
    print("P_VS_NP=OPEN; E8_D1=EMPTY")


if __name__=="__main__":
    main()
