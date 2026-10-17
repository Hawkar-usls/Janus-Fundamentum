#!/usr/bin/env python3
from fractions import Fraction
from itertools import product

ROWS = [
    (0,5,12),(1,7,9),(2,9,14),(3,10,11),(3,4,13),
    (1,5,10),(6,7,14),(2,3,7),(1,4,8),(0,6,9),
    (2,10,12),(5,11,13),(6,8,12),(0,8,13),(4,11,14),
]


def mat_from_rows(rows, n):
    A=[[0]*n for _ in range(n)]
    for i,row in enumerate(rows):
        for j in row:
            A[i][j]=1
    return A


def rank_q(M):
    M=[[Fraction(x) for x in row] for row in M]
    m=len(M); n=len(M[0]); r=0
    for c in range(n):
        p=next((i for i in range(r,m) if M[i][c]),None)
        if p is None:
            continue
        M[r],M[p]=M[p],M[r]
        pv=M[r][c]
        M[r]=[x/pv for x in M[r]]
        for i in range(m):
            if i!=r and M[i][c]:
                f=M[i][c]
                M[i]=[M[i][j]-f*M[r][j] for j in range(n)]
        r+=1
    return r


def mv(A,x):
    return [sum(Fraction(a)*Fraction(b) for a,b in zip(row,x)) for row in A]


def mtv(A,y):
    n=len(A)
    return [sum(Fraction(y[i])*Fraction(A[i][j]) for i in range(n)) for j in range(n)]


def lift(A,pair):
    n=len(A)
    E=[[0]*n for _ in range(n)]
    for i,j in pair:
        assert A[i][j]==1
        E[i][j]=1
    P=[[A[i][j]-E[i][j] for j in range(n)] for i in range(n)]
    H=[[0]*(2*n) for _ in range(2*n)]
    for i in range(n):
        for j in range(n):
            H[i][j]=P[i][j]
            H[i][j+n]=E[i][j]
            H[i+n][j]=E[i][j]
            H[i+n][j+n]=P[i][j]
    return H


def signed(A,pair):
    S=[row[:] for row in A]
    for i,j in pair:
        assert S[i][j]==1
        S[i][j]=-1
    return S


def sym(x):
    return list(x)+list(x)


def asym(x):
    return list(x)+[-Fraction(v) for v in x]


def zero_eval_basis(W,j):
    vals=[Fraction(w[j]) for w in W]
    if all(v==0 for v in vals):
        return [list(map(Fraction,w)) for w in W]
    p=next(i for i,v in enumerate(vals) if v)
    out=[]
    for q in range(len(W)):
        if q==p:
            continue
        coeff=[Fraction(0)]*len(W)
        coeff[q]=1
        coeff[p]=-vals[q]/vals[p]
        v=[sum(coeff[t]*Fraction(W[t][r]) for t in range(len(W))) for r in range(len(W[0]))]
        assert v[j]==0
        out.append(v)
    return out


A0=mat_from_rows(ROWS,15)
assert all(sum(r)==3 for r in A0)
assert all(sum(A0[i][j] for i in range(15))==3 for j in range(15))
assert all(len(set(ROWS[i]) & set(ROWS[j]))<=1 for i in range(15) for j in range(i))
assert rank_q(A0)==14

g=[1,4,1,1,-2,-2,1,-2,-2,-2,-2,1,1,1,1]
ell=[-8,4,-5,-11,1,16,-14,10,-20,1,-5,-8,13,7,19]
assert mv(A0,g)==[0]*15
assert mtv(A0,ell)==[0]*15

# Frozen seed UNSAT brute replay (2^15 only; theorem parent supplies symbolic proof).
assert not any(all(sum(A0[i][j]*x[j] for j in range(15))==1 for i in range(15))
               for x in product((0,1), repeat=15))

F0=((0,12),(2,9))
S0=signed(A0,F0)
z=[-7,-4,3,1,-2,2,-1,-4,6,8,2,-3,-5,1,5]
assert mv(S0,z)==[0]*15
assert rank_q(S0)==14
assert ell[0]!=ell[2]

A1=lift(A0,F0)
assert len(A1)==30
# Block theorem plus exact ranks of A0,S0 imply nullity(A1)=2.

# Persistent explicit strong odd 3x3 cycle, disjoint from all distinguished edges.
R=(1,6,9); C=(6,7,9)
sub=[[A1[i][j] for j in C] for i in R]
assert sub==[[0,1,1],[1,1,0],[1,0,1]]

# Full 2D kernel basis of A1 from sum/difference decomposition.
W=[sym(g),asym(z)]
assert all(mv(A1,w)==[0]*30 for w in W)
assert rank_q(list(map(list,zip(*W))))==2

F=((0,5),(1,1))
assert all(A1[i][j]==1 for i,j in F)
assert F[0][0]!=F[1][0] and F[0][1]!=F[1][1]
# ev_1 = -2 ev_5 on W.
assert all(Fraction(w[1])==-2*Fraction(w[5]) for w in W)
y=sym(ell)
assert mtv(A1,y)==[0]*30
assert y[0]!=y[1]

A=A1
tracked=[]
for step in range(4):
    n=len(A)
    (i1,j1),(i2,j2)=F
    assert A[i1][j1]==1 and A[i2][j2]==1
    assert i1!=i2 and j1!=j2
    assert all(mv(A,w)==[0]*n for w in W)
    assert all(Fraction(w[j2])==-2*Fraction(w[j1]) for w in W)
    assert mtv(A,y)==[0]*n and y[i1]!=y[i2]
    d=len(W)
    tracked.append((n,d))
    assert d >= n//30 + 1

    W0=zero_eval_basis(W,j1)
    assert len(W0)>=d-1
    assert all(w[j1]==0 and w[j2]==0 for w in W0)

    Anew=lift(A,F)
    Wnew=[sym(w) for w in W] + [asym(w) for w in W0]
    assert len(Wnew)>=2*d-1
    assert all(mv(Anew,w)==[0]*(2*n) for w in Wnew)

    # upper-right crossed copies become the next distinguished pair
    Fnew=((i1,j1+n),(i2,j2+n))
    assert Anew[Fnew[0][0]][Fnew[0][1]]==1
    assert Anew[Fnew[1][0]][Fnew[1][1]]==1
    assert all(Fraction(w[Fnew[1][1]])==-2*Fraction(w[Fnew[0][1]]) for w in Wnew)

    ynew=sym(y)
    assert mtv(Anew,ynew)==[0]*(2*n)
    assert ynew[Fnew[0][0]]!=ynew[Fnew[1][0]]

    A,W,F,y=Anew,Wnew,Fnew,ynew

assert tracked==[(30,2),(60,3),(120,5),(240,9)]
print("PASS_TWO_EDGE_EXACT_UNSAT_LINEAR_NULLITY_PRIME_TOWER")
print("tracked",tracked)
print("theorem: d_{t+1}>=2d_t-1, n_{t+1}=2n_t, hence d_t>=n_t/30+1")
print("scientific_ceiling: E8_D1=EMPTY P_VS_NP=OPEN")
