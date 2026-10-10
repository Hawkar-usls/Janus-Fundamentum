#!/usr/bin/env python3
from fractions import Fraction
from itertools import product
from math import gcd

ROWS=[
(0,15,17),(1,4,12),(2,10,14),(3,4,11),(4,8,9),(3,5,13),
(1,6,10),(2,7,15),(1,8,14),(3,7,9),(9,10,16),(7,11,13),
(5,12,17),(0,13,16),(0,12,14),(5,8,15),(2,6,16),(6,11,17)
]
X=[1,1,1,0,0,1,0,0,0,1,0,1,0,0,0,0,0,0]
K1=[0,0,-2,-2,3,3,1,2,-3,0,-1,-1,-3,-1,3,0,1,0]
K2=[-2,-2,0,3,-2,-5,0,-1,4,-2,2,-1,4,2,-2,1,0,1]

def incidence(rows,n):
    A=[[0]*n for _ in range(n)]
    for i,row in enumerate(rows):
        for j in row:A[i][j]=1
    return A

def mv(A,x): return [sum(a*b for a,b in zip(row,x)) for row in A]
def rank_q(M):
    a=[[Fraction(x) for x in row] for row in M]; r=0
    for c in range(len(a[0])):
        p=next((i for i in range(r,len(a)) if a[i][c]),None)
        if p is None: continue
        a[r],a[p]=a[p],a[r]
        q=a[r][c]; a[r]=[v/q for v in a[r]]
        for i in range(len(a)):
            if i!=r and a[i][c]:
                q=a[i][c]; a[i]=[a[i][j]-q*a[r][j] for j in range(len(a[0]))]
        r+=1
    return r

def primitive(v):
    g=0
    for x in v:g=gcd(g,abs(x))
    v=[x//g for x in v]
    for x in v:
        if x:
            if x<0:v=[-u for u in v]
            break
    return tuple(v)
def F(z): return sum(abs(2*v-1) for v in z)

A=incidence(ROWS,18)
assert rank_q(A)==16
assert mv(A,X)==[1]*18
assert mv(A,K1)==[0]*18 and mv(A,K2)==[0]*18

# Unique-model regression.
models=[]
for x in product((0,1),repeat=18):
    if mv(A,x)==[1]*18: models.append(x)
assert models==[tuple(X)]

# In a 2D kernel, every support-minimal projective direction occurs as the
# kernel of at least one nonzero coordinate functional.
circuits=set()
for i in range(18):
    a,b=K2[i],-K1[i]
    if a==0 and b==0: continue
    v=[a*K1[j]+b*K2[j] for j in range(18)]
    if any(v): circuits.add(primitive(v))
assert len(circuits)==9
for c in circuits: assert mv(A,c)==[0]*18

zc=[1-2*x for x in X]
assert mv(A,zc)==[1]*18
assert F(zc)==30 and F(X)==18

pairs=[]
for c in sorted(circuits):
    fp=F([z+cj for z,cj in zip(zc,c)])
    fm=F([z-cj for z,cj in zip(zc,c)])
    assert fp>=30 and fm>=30
    # Convexity of the 1D absolute-value objective makes neighbor optimality global.
    pairs.append((fp,fm))
assert pairs==[(62,66),(108,130),(56,92),(58,92),(80,130),(82,130),(118,174),(118,174),(154,196)]

print('PASS: kernel dimension 2 and all 9 rational circuit directions enumerated')
print('PASS: zc objective 30, exact witness objective 18')
print('PASS: every primitive circuit has F(zc+c)>=30 and F(zc-c)>=30')
print('PASS: convex line-search implies no integer circuit line improves zc')
print('P_VS_NP=OPEN; E8_D1=EMPTY')
