#!/usr/bin/env python3
"""Exact PG15 falsifier for binary submodularity of projected sign-crossing cost.

Stdlib only. No MILP/LP/float solver is used.
This is a scoped representation falsifier, not a P-vs-NP result.
"""
from fractions import Fraction
from itertools import product

SAT_LINES = [
    (1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),
    (3,4,7),(3,5,6),(4,9,13),(4,10,14),(5,8,13),
    (5,10,15),(6,8,14),(6,9,15),(7,8,15),(7,11,12),
]
X = [1 if i in {0,4,6,8,13} else 0 for i in range(15)]

# Rows are an integer kernel basis. The minor on columns (0,1,3,7) is unimodular.
N = [
    [-1,-1, 2,-1,-1,-1,-1, 1, 1, 1,0,1,0,0,0],
    [-1, 0, 1,-1,-1, 0, 0, 0, 0, 1,0,0,1,0,0],
    [ 0,-1, 1,-1, 0,-1, 0, 0, 1, 0,0,0,0,1,0],
    [ 0, 0, 0, 1, 0, 0,-1, 0,-1,-1,1,0,0,0,1],
]
SELECT = (0,1,3,7)
# B=N[:,SELECT], c B=q, hence c=q B^{-1}.
B_INV = [
    [0,-1, 0,-1],
    [0, 0,-1,-1],
    [0, 0, 0, 1],
    [1,-1,-1,-1],
]

C = {1,3,5,8,10,12,13,14}
D = {0,2,4,6,8,10,12,14}
I = C & D
U = C | D
EXPECTED = {
    "C": (C, 5, (1,0,0,0)),
    "D": (D, 5, (1,-1,-2,-1)),
    "I": (I, 15, (3,-1,-4,-1)),
    "U": (U, 15, (1,-2,0,-2)),
}


def incidence(lines, n=15):
    A=[[0]*n for _ in lines]
    for r,row in enumerate(lines):
        for j in row: A[r][j-1]=1
    return A


def mv(A,x): return [sum(a*b for a,b in zip(row,x)) for row in A]


def rank_q(M):
    a=[[Fraction(v) for v in row] for row in M]
    r=0
    m=len(a); n=len(a[0])
    for c in range(n):
        p=next((i for i in range(r,m) if a[i][c]),None)
        if p is None: continue
        a[r],a[p]=a[p],a[r]
        q=a[r][c]
        a[r]=[v/q for v in a[r]]
        for i in range(m):
            if i!=r and a[i][c]:
                q=a[i][c]
                a[i]=[a[i][j]-q*a[r][j] for j in range(n)]
        r+=1
    return r


def det_fraction(M):
    a=[[Fraction(v) for v in row] for row in M]
    n=len(a); det=Fraction(1); sign=1
    for c in range(n):
        p=next((i for i in range(c,n) if a[i][c]),None)
        if p is None: return 0
        if p!=c:
            a[c],a[p]=a[p],a[c]; sign*=-1
        q=a[c][c]; det*=q
        for j in range(c,n): a[c][j]/=q
        for i in range(c+1,n):
            q=a[i][c]
            if q:
                for j in range(c,n): a[i][j]-=q*a[c][j]
    return int(det*sign)


def add_kernel(c):
    return [X[j]+sum(c[k]*N[k][j] for k in range(4)) for j in range(15)]


def dist_cost(z):
    # sum_i dist(z_i,{0,1}) = (||2z-1||_1-n)/2
    out=0
    for v in z:
        if v<0: out += -v
        elif v>1: out += v-1
    return out


def positive_mask(z):
    return {i for i,v in enumerate(z) if v>=1}


def coefficient_ranges(K):
    # Any point with dist_cost<=K has -K <= z_i <= K+1.
    # On SELECT, q=z-X and c=q B_INV. Interval arithmetic gives a
    # complete coefficient box because the selected kernel minor is unimodular.
    qr=[]
    for pos in SELECT:
        qr.append((-K-X[pos], K+1-X[pos]))
    cr=[]
    for j in range(4):
        lo=hi=0
        for k,coef in enumerate(row[j] for row in B_INV):
            qlo,qhi=qr[k]
            if coef>=0:
                lo += coef*qlo; hi += coef*qhi
            else:
                lo += coef*qhi; hi += coef*qlo
        cr.append((lo,hi))
    return cr


def matmul4(A,B):
    return [[sum(A[i][k]*B[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def exact_phi(base_positive, flips, K):
    target=set(base_positive)^set(flips)
    cr=coefficient_ranges(K)
    best=None; best_c=None; best_z=None

    # Enumerate c0,c1,c2. For c3, fixed sign constraints give an integer interval;
    # within one fixed orthant dist_cost is affine in c3, so an endpoint minimizes it.
    for c0 in range(cr[0][0],cr[0][1]+1):
      for c1 in range(cr[1][0],cr[1][1]+1):
       for c2 in range(cr[2][0],cr[2][1]+1):
        fixed=[X[j]+c0*N[0][j]+c1*N[1][j]+c2*N[2][j] for j in range(15)]
        lo,hi=cr[3]
        ok=True
        for j in range(15):
            a=N[3][j]; f=fixed[j]
            if j in target:  # z_j >= 1
                if a==0:
                    if f<1: ok=False; break
                elif a==1: lo=max(lo,1-f)
                elif a==-1: hi=min(hi,f-1)
            else:            # z_j <= 0
                if a==0:
                    if f>0: ok=False; break
                elif a==1: hi=min(hi,-f)
                elif a==-1: lo=max(lo,f)
            if lo>hi: ok=False; break
        if not ok: continue
        for c3 in {lo,hi}:
            if c3<lo or c3>hi: continue
            c=(c0,c1,c2,c3)
            z=add_kernel(c)
            if positive_mask(z)!=target: continue
            val=dist_cost(z)
            if best is None or val<best:
                best,best_c,best_z=val,c,z

    assert best is not None
    assert best <= K  # explicit witness lies inside the complete K-box
    return best,best_c,best_z,cr


def main():
    A=incidence(SAT_LINES)
    assert all(sum(row)==3 for row in A)
    assert all(sum(A[r][c] for r in range(15))==3 for c in range(15))
    assert mv(A,X)==[1]*15
    assert rank_q(A)==11
    for row in N: assert mv(A,row)==[0]*15

    B=[[N[i][j] for j in SELECT] for i in range(4)]
    assert det_fraction(B)==-1
    assert matmul4(B,B_INV)==[[1 if i==j else 0 for j in range(4)] for i in range(4)]

    zc=[1-2*v for v in X]
    assert mv(A,zc)==[1]*15
    assert add_kernel((1,1,-2,1))==zc
    base_positive=positive_mask(zc)

    results={}
    for name,(flips,want,want_c) in EXPECTED.items():
        got,c,z,cr=exact_phi(base_positive,flips,want)
        assert got==want,(name,got,want)
        assert c==want_c,(name,c,want_c)
        assert mv(A,z)==[1]*15
        results[name]=(got,c,z,cr)
        print(f"PASS {name}: Phi={got} coeff={c} z={z}")

    assert I==C&D and U==C|D
    lhs=results['C'][0]+results['D'][0]
    rhs=results['I'][0]+results['U'][0]
    assert lhs==10 and rhs==30 and lhs<rhs

    print("PASS: rank_Q(A)=11 and det kernel minor=-1 certify full integer-kernel parametrization")
    print("PASS: exact projected minima are Phi(C),Phi(D),Phi(I),Phi(U)=5,5,15,15")
    print("VERDICT: PROJECTED_ORTHANT_COST_IS_NOT_SUBMODULAR_ON_FROZEN_PG15_SAT")
    print("NEXT: R5_E9_SIGN_CROSSING_PARTIAL_SIGN_BISUBMODULAR_GATE_V1")
    print("P_VS_NP=OPEN; E8_D1=EMPTY")


if __name__=='__main__':
    main()
