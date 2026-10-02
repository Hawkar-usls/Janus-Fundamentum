#!/usr/bin/env python3
"""Exact PG15 falsifier for bisubmodularity of the partial-sign projected cost.

Stdlib only.  No MILP/LP/float solver.
The only finite enumeration is a complete 52,200-tuple coefficient box for the
hypothesis D(z)<=3, derived from a certified unimodular integer-kernel minor.
"""

from fractions import Fraction
from itertools import product

SAT_LINES = [
    (1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),
    (3,4,7),(3,5,6),(4,9,13),(4,10,14),(5,8,13),
    (5,10,15),(6,8,14),(6,9,15),(7,8,15),(7,11,12),
]
X = [1 if i in {0,4,6,8,13} else 0 for i in range(15)]
N = [
    [-1,-1, 2,-1,-1,-1,-1, 1, 1, 1,0,1,0,0,0],
    [-1, 0, 1,-1,-1, 0, 0, 0, 0, 1,0,0,1,0,0],
    [ 0,-1, 1,-1, 0,-1, 0, 0, 1, 0,0,0,0,1,0],
    [ 0, 0, 0, 1, 0, 0,-1, 0,-1,-1,1,0,0,0,1],
]
SELECT = (0,1,3,7)
# B=N[:,SELECT].  With row-vector convention c B=q, so c=q B^{-1}.
B_INV = [
    [0,-1, 0,-1],
    [0, 0,-1,-1],
    [0, 0, 0, 1],
    [1,-1,-1,-1],
]


def incidence(lines, n=15):
    A=[[0]*n for _ in lines]
    for r,row in enumerate(lines):
        for j in row:
            A[r][j-1]=1
    return A


def mv(A,x):
    return [sum(a*b for a,b in zip(row,x)) for row in A]


def rank_q(M):
    a=[[Fraction(v) for v in row] for row in M]
    r=0
    m=len(a); n=len(a[0])
    for c in range(n):
        p=next((i for i in range(r,m) if a[i][c]),None)
        if p is None:
            continue
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
        if p is None:
            return 0
        if p!=c:
            a[c],a[p]=a[p],a[c]
            sign*=-1
        q=a[c][c]
        det*=q
        for j in range(c,n):
            a[c][j]/=q
        for i in range(c+1,n):
            q=a[i][c]
            if q:
                for j in range(c,n):
                    a[i][j]-=q*a[c][j]
    return int(det*sign)


def matmul4(A,B):
    return [[sum(A[i][k]*B[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def add_kernel(c):
    return [X[j]+sum(c[k]*N[k][j] for k in range(4)) for j in range(15)]


def dist_cost(z):
    out=0
    for v in z:
        if v<0:
            out += -v
        elif v>1:
            out += v-1
    return out


def coefficient_ranges(K):
    # If D(z)<=K then -K<=z_i<=K+1 for every coordinate.
    # q=z-X on SELECT and c=q B_INV.  Interval arithmetic therefore gives
    # a complete coefficient box for every hypothetical point with D<=K.
    qr=[]
    for pos in SELECT:
        qr.append((-K-X[pos], K+1-X[pos]))
    cr=[]
    for j in range(4):
        lo=hi=0
        for k in range(4):
            coef=B_INV[k][j]
            qlo,qhi=qr[k]
            if coef>=0:
                lo += coef*qlo; hi += coef*qhi
            else:
                lo += coef*qhi; hi += coef*qlo
        cr.append((lo,hi))
    return cr


def verify_zero_witness(c, required_positive):
    z=add_kernel(c)
    assert mv(A,z)==[1]*15
    assert all(v in (0,1) for v in z)
    assert dist_cost(z)==0
    assert all(z[i]>=1 for i in required_positive)
    return z


A=incidence(SAT_LINES)
assert all(sum(row)==3 for row in A)
assert all(sum(A[r][c] for r in range(15))==3 for c in range(15))
assert mv(A,X)==[1]*15
assert rank_q(A)==11
for row in N:
    assert mv(A,row)==[0]*15

B=[[N[i][j] for j in SELECT] for i in range(4)]
assert det_fraction(B)==-1
assert matmul4(B,B_INV)==[[1 if i==j else 0 for j in range(4)] for i in range(4)]

# Psi(empty,empty)=0 since X itself is Boolean feasible.
assert dist_cost(X)==0

# Exact zero-cost witnesses for the two one-coordinate partial signs.
z7 = verify_zero_witness((1,0,-1,0), {7})
z13 = verify_zero_witness((0,1,0,1), {13})

# Explicit jointly constrained cost-4 witness.
c_joint=(1,0,0,1)
z_joint=add_kernel(c_joint)
assert mv(A,z_joint)==[1]*15
assert z_joint[7]>=1 and z_joint[13]>=1
assert dist_cost(z_joint)==4

# To prove optimality, exclude every hypothetical joint point with D<=3.
K=3
cr=coefficient_ranges(K)
assert cr==[(-3,4),(-7,7),(-8,6),(-14,14)], cr
box_size=1
for lo,hi in cr:
    box_size *= hi-lo+1
assert box_size==52200

found_better=[]
checked=0
for c0,c1,c2,c3 in product(
    range(cr[0][0],cr[0][1]+1),
    range(cr[1][0],cr[1][1]+1),
    range(cr[2][0],cr[2][1]+1),
    range(cr[3][0],cr[3][1]+1),
):
    checked += 1
    z=add_kernel((c0,c1,c2,c3))
    if z[7] < 1 or z[13] < 1:
        continue
    if dist_cost(z) <= K:
        found_better.append(((c0,c1,c2,c3),z,dist_cost(z)))

assert checked==52200
assert found_better==[]

psi_empty=0
psi_p=0
psi_q=0
psi_join=4
assert psi_p+psi_q < psi_empty+psi_join

print("PASS: rank_Q(A)=11; frozen kernel rows span ker_Q(A)")
print("PASS: det kernel minor on columns (0,1,3,7)=-1 => full saturated integer-kernel parametrization")
print(f"PASS: Psi(empty)=0; Psi(+7)=0 witness={z7}")
print(f"PASS: Psi(+13)=0 witness={z13}")
print(f"PASS: joint witness c={c_joint} has Psi(+7,+13)<=4 z={z_joint}")
print(f"PASS: exhausted complete D<=3 coefficient box tuples={checked}; no joint better point")
print("PASS: Psi(+7,+13)=4 exactly")
print("VIOLATION: Psi(+7)+Psi(+13)=0 < Psi(empty)+Psi(+7,+13)=4")
print("VERDICT: PARTIAL_SIGN_PROJECTED_COST_IS_NOT_BISUBMODULAR_ON_FROZEN_PG15_SAT")
print("NEXT: R5_E9_GLOBAL_SIGN_CROSSING_SOURCE_TRADE_GATE_V2")
print("P_VS_NP=OPEN; E8_D1=EMPTY")
