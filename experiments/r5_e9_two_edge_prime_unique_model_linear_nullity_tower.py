#!/usr/bin/env python3
from fractions import Fraction
from itertools import product

ROWS=[
(0,15,17),(1,4,12),(2,10,14),(3,4,11),(4,8,9),(3,5,13),
(1,6,10),(2,7,15),(1,8,14),(3,7,9),(9,10,16),(7,11,13),
(5,12,17),(0,13,16),(0,12,14),(5,8,15),(2,6,16),(6,11,17)
]
X=[1,1,1,0,0,1,0,0,0,1,0,1,0,0,0,0,0,0]
K1=[0,0,-2,-2,3,3,1,2,-3,0,-1,-1,-3,-1,3,0,1,0]
K2=[-2,-2,0,3,-2,-5,0,-1,4,-2,2,-1,4,2,-2,1,0,1]
ELL=[1,2,2,-1,-1,-1,-1,-3,-1,2,-1,1,-1,0,-1,2,1,0]
PAIR=((0,15),(1,1))


def incidence(rows,n):
    A=[[0]*n for _ in range(n)]
    for i,row in enumerate(rows):
        for j in row: A[i][j]=1
    return A

def mv(A,x): return [sum(a*b for a,b in zip(row,x)) for row in A]
def mtv(A,x): return [sum(A[i][j]*x[i] for i in range(len(A))) for j in range(len(A[0]))]

def rank_q(M):
    a=[[Fraction(x) for x in row] for row in M]
    r=0
    for c in range(len(a[0])):
        p=next((i for i in range(r,len(a)) if a[i][c]),None)
        if p is None: continue
        a[r],a[p]=a[p],a[r]
        q=a[r][c]; a[r]=[v/q for v in a[r]]
        for i in range(len(a)):
            if i!=r and a[i][c]:
                q=a[i][c]
                a[i]=[a[i][j]-q*a[r][j] for j in range(len(a[0]))]
        r+=1
    return r

def lift(A,pair):
    n=len(A)
    E=[[0]*n for _ in range(n)]
    for i,j in pair:
        assert A[i][j]==1
        E[i][j]=1
    P=[[A[i][j]-E[i][j] for j in range(n)] for i in range(n)]
    return [P[i]+E[i] for i in range(n)] + [E[i]+P[i] for i in range(n)]

def linear(A):
    supp=[{j for j,v in enumerate(row) if v} for row in A]
    return all(len(supp[i]&supp[j])<=1 for i in range(len(A)) for j in range(i))

A=incidence(ROWS,18)
assert all(sum(row)==3 for row in A)
assert all(sum(A[i][j] for i in range(18))==3 for j in range(18))
assert linear(A)
assert rank_q(A)==16
assert mv(A,X)==[1]*18
assert mv(A,K1)==[0]*18 and mv(A,K2)==[0]*18
assert mtv(A,ELL)==[0]*18

# Seed uniqueness: finite regression only; theorem uses signed-trade-free parent.
models=[]
for x in product((0,1), repeat=18):
    if mv(A,x)==[1]*18: models.append(x)
assert models==[tuple(X)]

(i1,j1),(i2,j2)=PAIR
assert i1!=i2 and j1!=j2
assert (K1[j1],K2[j1])==(0,1)
assert (K1[j2],K2[j2])==(0,-2)
assert ELL[i1]==1 and ELL[i2]==2
# Finite defect condition for two-edge signed-trade preservation.
admiss=[]
for d1 in range(-2,3):
    for d2 in range(-2,3):
        if (d1+d2)%3==0 and ELL[i1]*d1+ELL[i2]*d2==0:
            admiss.append((d1,d2))
assert admiss==[(0,0)]

A1=lift(A,PAIR)
assert len(A1)==36 and all(len(row)==36 for row in A1)
assert all(sum(row)==3 for row in A1)
assert all(sum(A1[i][j] for i in range(36))==3 for j in range(36))
assert linear(A1)
# Parent block decomposition predicts k1=3; exact elimination replays it.
assert rank_q(A1)==33
X1=X+X
assert mv(A1,X1)==[1]*36

# Three explicit independent kernel vectors in the first lift.
B1=K1+K1
B2=K2+K2
B3=K1+[-v for v in K1]
assert mv(A1,B1)==[0]*36
assert mv(A1,B2)==[0]*36
assert mv(A1,B3)==[0]*36
assert rank_q([B1,B2,B3])==3

# Symmetric left-kernel witness inherits row values 1,2 for the next recursive pair.
ELL1=ELL+ELL
assert mtv(A1,ELL1)==[0]*36
assert ELL1[0]==1 and ELL1[1]==2

print('PASS: frozen 18_3 seed is unique-model, rank 16, nullity 2')
print('PASS: distinguished two-edge pair has rank-1 kernel evaluation and defect-safe left witness')
print('PASS: first two-edge lift is linear-cubic, SAT, rank 33, nullity 3')
print('PASS: tracked symmetric/antisymmetric kernel recurrence starts at 2 -> 3')
print('PASS: recursive left-kernel defect certificate is inherited')
print('P_VS_NP=OPEN; E8_D1=EMPTY')
