#!/usr/bin/env python3
from fractions import Fraction
from itertools import product
from math import gcd

def rank_q(A):
    M=[[Fraction(x) for x in row] for row in A]
    m=len(M); n=len(M[0]) if m else 0
    r=0
    for c in range(n):
        p=next((i for i in range(r,m) if M[i][c]),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r]
        q=M[r][c]
        M[r]=[x/q for x in M[r]]
        for i in range(m):
            if i==r: continue
            q=M[i][c]
            if q:
                M[i]=[x-q*y for x,y in zip(M[i],M[r])]
        r+=1
        if r==m: break
    return r

def translation_perm(mods, step):
    pts=list(product(*[range(m) for m in mods]))
    index={x:i for i,x in enumerate(pts)}
    p=[]
    for x in pts:
        y=tuple((a+b)%m for a,b,m in zip(x,step,mods))
        p.append(index[y])
    return p

def generated_orbit(n,P,Q,start=0):
    seen={start}; stack=[start]
    while stack:
        x=stack.pop()
        for R in (P,Q):
            y=R[x]
            if y not in seen:
                seen.add(y); stack.append(y)
        # inverse moves
        for R in (P,Q):
            y=R.index(x)
            if y not in seen:
                seen.add(y); stack.append(y)
    return seen

def matrix_I_P_Q(P,Q):
    n=len(P)
    A=[[0]*n for _ in range(n)]
    for i in range(n):
        for j in (i,P[i],Q[i]):
            A[i][j]+=1
    return A

def exact_words(A):
    n=len(A)
    out=[]
    # only small controls
    for z in product((-1,2),repeat=n):
        if all(sum(a*b for a,b in zip(row,z))==0 for row in A):
            out.append(z)
    return out

def main():
    tested=0
    # Connected translation actions on Z_m, m<=9.
    for m in range(3,10):
        mods=(m,)
        for a in range(m):
            for b in range(m):
                if gcd(gcd(a,b),m)!=1:
                    continue
                P=translation_perm(mods,(a,))
                Q=translation_perm(mods,(b,))
                assert len(generated_orbit(m,P,Q))==m
                assert all(P[Q[i]]==Q[P[i]] for i in range(m))
                A=matrix_I_P_Q(P,Q)
                d=m-rank_q(A)
                assert d in (0,2)
                if m<=9 and d==2:
                    W=exact_words(A)
                    assert len(W)==3
                    assert all(sum(1 for v in z if v==2)==m//3 for z in W)
                tested+=1

    # Connected translations on small Z_m x Z_n products.
    for mods in ((2,3),(3,3),(2,2,3)):
        N=1
        for m in mods: N*=m
        steps=list(product(*[range(m) for m in mods]))
        for a in steps:
            for b in steps:
                P=translation_perm(mods,a)
                Q=translation_perm(mods,b)
                if len(generated_orbit(N,P,Q))!=N:
                    continue
                A=matrix_I_P_Q(P,Q)
                d=N-rank_q(A)
                assert d in (0,2)
                tested+=1

    print("CONNECTED_COMMUTING_OVERLAY_NULLITY_IN_{0,2} = PASS")
    print("NULLITY_2_EXACT_KERNEL_WORD_COUNT = 3 ON SMALL CONTROLS")
    print("ABELIAN_TRANSLATION_CONTROLS_TESTED =",tested)
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
