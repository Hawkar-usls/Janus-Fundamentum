#!/usr/bin/env python3
from fractions import Fraction
from itertools import product
import json

# Basis order 000,001,010,011,100,101,110,111.
EQ3=[Fraction(0)]*8
EQ3[0]=Fraction(1)
EQ3[7]=Fraction(1)
W=[Fraction(0)]*8
for i in (1,2,4):
    W[i]=Fraction(1)

def anti(b):
    b=Fraction(b)
    assert b != 0
    return ((Fraction(0),b),(Fraction(1,1)/b,Fraction(0)))

def tr(A):
    return tuple(zip(*A))

def kron_apply(ms, v):
    out=[Fraction(0)]*8
    for y in range(8):
        yb=((y>>2)&1,(y>>1)&1,y&1)
        s=Fraction(0)
        for x in range(8):
            xb=((x>>2)&1,(x>>1)&1,x&1)
            c=Fraction(1)
            for j in range(3):
                c *= ms[j][yb[j]][xb[j]]
            s += c*v[x]
        out[y]=s
    return out

def eq(a,b):
    return all(x==y for x,y in zip(a,b))

def scale(v,s):
    return [s*x for x in v]

controls=[]
for b1,b2 in ((1,1),(2,3),(-2,3),(Fraction(1,2),-3)):
    for eps in (1,-1):
        b3=Fraction(eps,1)/(Fraction(b1)*Fraction(b2))
        ms=[anti(b1),anti(b2),anti(b3)]
        # Every matrix is traceless and squares to I.
        for A in ms:
            assert A[0][0]+A[1][1] == 0
            assert A[0][0]*A[0][0]+A[0][1]*A[1][0] == 1
            assert A[1][0]*A[0][1]+A[1][1]*A[1][1] == 1
        got=kron_apply(ms,EQ3)
        assert eq(got,scale(EQ3,eps))
        # Transposed anti-diagonal product sends weight-one support to weight-two.
        wout=kron_apply([tr(A) for A in ms],W)
        supp=[i for i,x in enumerate(wout) if x]
        assert supp
        assert all(bin(i).count('1')==2 for i in supp)
        assert not eq(wout,W) and not eq(wout,scale(W,-1))
        controls.append({"b":[str(Fraction(b1)),str(Fraction(b2)),str(b3)],"eps":eps,"w_support":supp})

print(json.dumps({
    "status":"PASS_EDGEWISE_MATCHGATE_GAUGE_BARRIER_SANITY",
    "controls":controls,
    "theorem_scope":"finite checker validates anti-diagonal branch; arbitrary-gauge completeness is proved in the companion theorem",
    "boundary":{"universal_solver":"NOT_PROVED","P_VS_NP":"OPEN"}
},sort_keys=True))
