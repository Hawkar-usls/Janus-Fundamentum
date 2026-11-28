#!/usr/bin/env python3
"""R5 E121: KLOC3-clean E57 cyclic-3-lift near-miss."""

from fractions import Fraction
from itertools import combinations, product

P=[6,3,7,10,11,1,4,8,9,5,2,0]
Q=[3,4,5,8,7,0,9,6,2,11,1,10]
BASE_Z=[-1,-1,2,-1,2,2,2,-4,2,-4,-1,2]
SHIFTS=[
    (0,1,0),(0,1,0),(0,0,0),(0,0,1),
    (0,0,1),(0,0,2),(0,0,1),(0,1,2),
    (0,0,1),(0,2,0),(0,1,1),(0,2,1),
]
N0=12
N=36
ALPHABET=(-1,2)

# Q(omega), omega^2+omega+1=0, represented as a+b*omega.
def add(x,y): return (x[0]+y[0],x[1]+y[1])
def sub(x,y): return (x[0]-y[0],x[1]-y[1])
def mul(x,y):
    a,b=x; c,d=y
    return (a*c-b*d, a*d+b*c-b*d)
def inv(x):
    a,b=x
    n=a*a-a*b+b*b
    return ((a-b)/n,(-b)/n)
def zero(x): return x[0]==0 and x[1]==0

ONE=(Fraction(1),Fraction(0))
OMEGA=(Fraction(0),Fraction(1))
OMEGA2=(Fraction(-1),Fraction(-1))
POW=(ONE,OMEGA,OMEGA2)

def rank_qw(M):
    A=[row[:] for row in M]
    m=len(A); n=len(A[0]) if m else 0
    r=0
    for c in range(n):
        p=next((i for i in range(r,m) if not zero(A[i][c])),None)
        if p is None:
            continue
        A[r],A[p]=A[p],A[r]
        z=inv(A[r][c])
        A[r]=[mul(x,z) for x in A[r]]
        for i in range(m):
            if i!=r and not zero(A[i][c]):
                f=A[i][c]
                A[i]=[sub(A[i][j],mul(f,A[r][j])) for j in range(n)]
        r+=1
    return r,A

def nullvec_qw(M):
    rank,R=rank_qw(M)
    # Recompute pivots from RREF rows.
    piv=[]
    for row in R:
        p=next((j for j,x in enumerate(row) if not zero(x)),None)
        if p is not None:
            piv.append(p)
    free=[j for j in range(len(M[0])) if j not in piv]
    assert len(free)==1
    x=[(Fraction(0),Fraction(0)) for _ in range(len(M[0]))]
    x[free[0]]=ONE
    for i in range(len(piv)-1,-1,-1):
        c=piv[i]
        s=(Fraction(0),Fraction(0))
        for j in range(len(x)):
            if j!=c and not zero(R[i][j]) and not zero(x[j]):
                s=add(s,mul(R[i][j],x[j]))
        x[c]=(-s[0],-s[1])
    return rank,x

def base_matrix():
    A=[[0]*N0 for _ in range(N0)]
    for i in range(N0):
        for j in (i,P[i],Q[i]):
            A[i][j]=1
    return A

def twisted_matrix(power):
    M=[[(Fraction(0),Fraction(0)) for _ in range(N0)] for __ in range(N0)]
    for i in range(N0):
        for j,s in zip((i,P[i],Q[i]),SHIFTS[i]):
            M[i][j]=POW[(power*s)%3]
    return M

def lift_matrix():
    A=[[0]*N for _ in range(N)]
    for i in range(N0):
        for c in range(3):
            r=3*i+c
            for j,s in zip((i,P[i],Q[i]),SHIFTS[i]):
                A[r][3*j+((c+s)%3)]=1
    return A

def rational_kernel_rows():
    rank1,z=nullvec_qw(twisted_matrix(1))
    rank2,_=nullvec_qw(twisted_matrix(2))
    assert rank1==rank2==11
    assert all(not zero(v) for v in z)

    B=[]
    for j in range(N0):
        for c in range(3):
            v=z[j]
            if c==1:
                v=mul(v,OMEGA)
            elif c==2:
                v=mul(v,OMEGA2)
            B.append([Fraction(BASE_Z[j]),v[0],v[1]])
    return B

def rank_q(M):
    A=[[Fraction(x) for x in row] for row in M]
    m=len(A); n=len(A[0]) if m else 0
    r=0
    for c in range(n):
        p=next((i for i in range(r,m) if A[i][c]),None)
        if p is None:
            continue
        A[r],A[p]=A[p],A[r]
        z=A[r][c]
        A[r]=[x/z for x in A[r]]
        for i in range(m):
            if i!=r and A[i][c]:
                f=A[i][c]
                A[i]=[A[i][j]-f*A[r][j] for j in range(n)]
        r+=1
    return r

def local_compatible(B,S):
    M=[B[i] for i in S]
    r=rank_q(M)
    for sig in product(ALPHABET,repeat=len(S)):
        aug=[M[t]+[Fraction(sig[t])] for t in range(len(S))]
        if rank_q(aug)==r:
            return True
    return False

def proportional(u,v):
    lam=None
    for a,b in zip(u,v):
        if a:
            q=b/a
            if lam is None:
                lam=q
            elif lam!=q:
                return None
        elif b:
            return None
    return lam

def gf2_kernel(A):
    rows=[]
    for row in A:
        m=0
        for j,v in enumerate(row):
            if v:
                m|=1<<j
        rows.append(m)

    piv=[]
    r=0
    for c in range(N):
        bit=1<<c
        p=next((i for i in range(r,N) if rows[i]&bit),None)
        if p is None:
            continue
        rows[r],rows[p]=rows[p],rows[r]
        for i in range(N):
            if i!=r and rows[i]&bit:
                rows[i]^=rows[r]
        piv.append(c)
        r+=1

    free=[c for c in range(N) if c not in piv]
    basis=[]
    for f in free:
        x=1<<f
        for i in range(len(piv)-1,-1,-1):
            c=piv[i]
            if (rows[i]&x).bit_count()&1:
                x|=1<<c
        basis.append(x)
    return basis

def connected(A):
    adj=[[] for _ in range(2*N)]
    for i,row in enumerate(A):
        for j,v in enumerate(row):
            if v:
                adj[i].append(N+j)
                adj[N+j].append(i)
    seen={0}
    stack=[0]
    while stack:
        u=stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen)==2*N

def main():
    A=lift_matrix()

    assert all(sum(row)==3 for row in A)
    assert all(sum(A[i][j] for i in range(N))==3 for j in range(N))
    supports=[{j for j,v in enumerate(row) if v} for row in A]
    assert all(
        len(supports[i]&supports[j])<=1
        for i in range(N)
        for j in range(i)
    )
    assert connected(A)
    assert N%3==0

    # Character ranks: 11+11+11 => full rational rank 33, nullity 3.
    A0=base_matrix()
    assert rank_q(A0)==11
    assert rank_qw(twisted_matrix(1))[0]==11
    assert rank_qw(twisted_matrix(2))[0]==11

    B=rational_kernel_rows()
    assert rank_q(B)==3
    assert all(any(x for x in row) for row in B)

    # Complete KLOC <=3.
    for s in (1,2,3):
        for S in combinations(range(N),s):
            assert local_compatible(B,S)

    props=[]
    for i,j in combinations(range(N),2):
        q=proportional(B[i],B[j])
        if q is not None:
            props.append((i,j,q))
    assert len(props)==57
    assert {q for _,_,q in props}=={Fraction(1)}

    # Equality closure produces 12 classes.
    parent=list(range(N))
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]]
            x=parent[x]
        return x
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b:
            parent[b]=a
    for i,j,_ in props:
        union(i,j)

    classes={}
    for i in range(N):
        classes.setdefault(find(i),[]).append(i)
    sizes=sorted(len(v) for v in classes.values())
    assert len(classes)==12
    assert sizes==[1,1,1,2,2,2,3,3,3,6,6,6]

    # E58 exact binary cap.
    basis=gf2_kernel(A)
    assert len(basis)==3
    weights=[]
    for mask in range(1<<len(basis)):
        x=0
        for i,b in enumerate(basis):
            if (mask>>i)&1:
                x^=b
        weights.append(x.bit_count())
    assert max(weights)==22
    assert 2*N//3==24

    print("R5 E121 E57 3-lift near-miss: PASS")
    print("n=36 connected square/cubic/linear; 3|n")
    print("rank_Q=33 nullity_Q=3")
    print("KLOC1/KLOC2/KLOC3: all coordinate subsets clean")
    print("GF2 kernel dimension=3 max weight=22 < cap=24 => UNSAT")
    print("E18 equality pairs=57, all lambda=1")
    print("equality closure classes=12 sizes=",sizes)
    print("POST_E18_KLOC3_UNSAT remains OPEN")
    print("P_VS_NP remains OPEN")

if __name__=="__main__":
    main()
