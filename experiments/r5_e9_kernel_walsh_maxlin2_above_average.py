#!/usr/bin/env python3
from collections import Counter


def rows_to_cols(rows,n):
    cols=[0]*n
    for r,row in enumerate(rows):
        for j in row: cols[j]|=1<<r
    return cols

def kernel_basis(cols):
    piv={}; out=[]
    for j,v0 in enumerate(cols):
        v=v0; comb=1<<j
        while v:
            p=v.bit_length()-1
            if p in piv:
                v^=piv[p][0]; comb^=piv[p][1]
            else:
                piv[p]=(v,comb); break
        if not v: out.append(comb)
    return out

def words(basis):
    out=[0]
    for b in basis: out += [x^b for x in out]
    return out

def syndrome(cols,w):
    s=0
    for j,c in enumerate(cols):
        if (w>>j)&1: s^=c
    return s

def build(rows,S):
    n=len(rows); cols=rows_to_cols(rows,n); basis=kernel_basis(cols)
    sm=sum(1<<i for i in S)
    assert syndrome(cols,sm)==(1<<n)-1
    masks=[sum(((b>>j)&1)<<q for q,b in enumerate(basis)) for j in range(n)]
    Sin=set(S); d=Counter()
    for i,a in enumerate(masks):
        if a: d[a] += 1 if i in Sin else -1
    aS=sum(masks[i]!=0 for i in S)
    aO=sum(masks[i]!=0 for i in range(n) if i not in Sin)
    C=aS-aO; D=-C
    vals=[]
    for lam in range(1<<len(basis)):
        H=sum(v*((a&lam).bit_count()&1) for a,v in d.items())
        # Desired parity is 1 for d>0 and 0 for d<0.
        E=0
        for a,v in d.items():
            p=(a&lam).bit_count()&1
            sat=(p==1) if v>0 else (p==0)
            E += abs(v) if sat else -abs(v)
        assert E==2*H-C
        vals.append((H,E,lam))
    return len(basis),aS,aO,D,d,vals

ROWS1=[
[0,7,9],[1,7,10],[2,5,8],[1,3,13],[0,4,16],[5,12,15],
[1,6,15],[7,11,13],[6,8,14],[3,9,14],[8,10,16],[4,11,17],
[10,11,12],[0,2,13],[5,14,17],[2,4,15],[9,12,16],[3,6,17],]
S1=[0,1,4,5,11,14,16,17]
ROWS2=[
[0,11,14],[1,10,13],[2,5,14],[2,3,4],[4,6,7],[1,3,5],
[6,15,16],[5,7,17],[1,7,8],[0,9,16],[0,3,10],[6,11,12],
[8,9,12],[4,11,13],[8,14,15],[9,13,15],[2,16,17],[10,12,17],]
S2=[1,3,5,6,11,12,15,16]

for rows,S,expected_k in ((ROWS1,S1,2),(ROWS2,S2,3)):
    k,aS,aO,D,d,vals=build(rows,S)
    assert k==expected_k
    assert (aS,aO,D)==(6,10,4)
    assert max(h for h,e,l in vals)>0
    # H>0 iff unscaled excess >=D+2.
    assert all((h>0)==(e>=D+2) for h,e,l in vals)
    # After doubling weights, standard AA parameter kappa=D+2 asks excess >=2*kappa.
    kappa=D+2
    assert all((h>0)==((2*e)>=2*kappa) for h,e,l in vals)

# Generic signed-multiplicity sanity, independent of source controls.
d={1:3,2:-2,3:1}
C=sum(d.values()); D=-C
for lam in range(4):
    H=sum(v*((a&lam).bit_count()&1) for a,v in d.items())
    E=0
    for a,v in d.items():
        p=(a&lam).bit_count()&1
        sat=(p==1) if v>0 else (p==0)
        E += abs(v) if sat else -abs(v)
    assert E==2*H-C

print('PASS: exact Walsh score -> weighted MaxLin2 excess identity E=2H-C')
print('PASS: both negative-mean KWM hostile controls have D=4 and kappa=6')
print('PASS: H>0 iff doubled-weight MaxLin2-AA reaches excess 2*(D+2)')
print('P_VS_NP=OPEN; E8_D1=EMPTY')
