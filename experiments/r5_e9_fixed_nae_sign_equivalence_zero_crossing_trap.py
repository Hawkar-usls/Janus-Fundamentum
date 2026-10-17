#!/usr/bin/env python3
from itertools import product
from fractions import Fraction

A=[
[0,0,0,0,0,0,1,1,1],
[0,1,1,0,0,0,0,1,0],
[0,0,1,0,1,0,1,0,0],
[1,1,0,0,0,0,1,0,0],
[0,0,1,1,0,1,0,0,0],
[0,0,0,1,1,0,0,0,1],
[1,0,0,0,1,1,0,0,0],
[1,0,0,1,0,0,0,1,0],
[0,1,0,0,0,1,0,0,1],
]
X=[1,0,1,0,0,0,0,0,1]


def mv(M,x): return [sum(a*b for a,b in zip(row,x)) for row in M]

def mm_diag_left_right(A, rho, s):
    return [[rho[i]*A[i][j]*s[j] for j in range(len(A))] for i in range(len(A))]

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
                q=a[i][c]; a[i]=[a[i][j]-q*a[r][j] for j in range(len(a[0]))]
        r+=1
    return r

n=len(A)
assert all(sum(row)==3 for row in A)
assert all(sum(A[i][j] for i in range(n))==3 for j in range(n))
assert mv(A,X)==[1]*n

# Complement-witness feasible integer point.
zc=[1-2*x for x in X]
assert mv(A,zc)==[1]*n
b=[1 if z>=1 else 0 for z in zc]
weights=mv(A,b)
assert weights==[2]*n
B=sum(b)
assert 3*B==2*n
p=[max(z-1,0) if b[i] else 0 for i,z in enumerate(zc)]
assert sum(p)==0
F=lambda z: sum(abs(2*v-1) for v in z)
assert 3*F(zc)==5*n
assert F(X)==n

g=[X[i]-zc[i] for i in range(n)]
assert mv(A,g)==[0]*n
# In odd coordinates this direct move flips every sign.
y=[2*z-1 for z in zc]
y2=[y[i]+2*g[i] for i in range(n)]
assert all(y[i]*y2[i] < 0 for i in range(n))

# Fixed-NAE matrix identity M_b = R_b A S_b.
s=[2*v-1 for v in b]
tau=[w-1 for w in weights]
rho=[1-2*t for t in tau]
M=mm_diag_left_right(A,rho,s)
for i,row in enumerate(A):
    supp=[j for j,a in enumerate(row) if a]
    minority_bit=0 if weights[i]==2 else 1
    minority=[j for j in supp if b[j]==minority_bit]
    assert len(minority)==1
    m=minority[0]
    for j in supp:
        assert M[i][j] == (1 if j==m else -1)
assert rank_q(M)==rank_q(A)

# Unique-model hostile control: complement orthant has no better fixed-b point.
models=[]
for x in product((0,1),repeat=n):
    if mv(A,x)==[1]*n: models.append(x)
assert models==[tuple(X)]
# The primitive kernel generator is 3X-1.
V=[3*x-1 for x in X]
assert mv(A,V)==[0]*n
# Integer affine line z(t)=X+tV. t=-1 is complement; only t=0 improves it nearby
# and in fact globally because absolute-value breakpoints are exhausted by this 1D line.
vals=[]
for t in range(-20,21):
    z=[X[i]+t*V[i] for i in range(n)]
    vals.append((F(z),t))
assert min(vals)==(n,0)
assert F([X[i]-V[i] for i in range(n)])==5*n//3

print('PASS: M_b = R_b A S_b on frozen unique-model control')
print('PASS: complement witness is integer feasible and fixed-threshold p=0 optimum')
print('PASS: global Boolean witness is strictly better and direct trade crosses all coordinates')
print('PASS: zero-crossing-only universal augmentation is falsified')
print('P_VS_NP=OPEN; E8_D1=EMPTY')
