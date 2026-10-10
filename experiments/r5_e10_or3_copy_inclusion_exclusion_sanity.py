#!/usr/bin/env python3
"""Exact sanity checks for R5 E10 OR/COPY closure and inclusion-exclusion."""

from itertools import product
import random

B=((0,1),(-1,1))

def mat_vec(M,v):
    return tuple(sum(M[i][j]*v[j] for j in range(2)) for i in range(2))

def tensor3(v,w,z):
    return {(i,j,k):v[i]*w[j]*z[k] for i,j,k in product(range(2), repeat=3)}

def add(X,Y,scale=1):
    out=dict(X)
    for k,v in Y.items():
        out[k]=out.get(k,0)+scale*v
    return out

def transform3(T1,T2,T3,X):
    out={}
    for a,b,c in product(range(2), repeat=3):
        out[a,b,c]=sum(
            T1[a][i]*T2[b][j]*T3[c][k]*X[i,j,k]
            for i,j,k in product(range(2), repeat=3)
        )
    return out

def sat_count(n, clauses):
    ans=0
    for x in product([0,1], repeat=n):
        if all(any(x[v] if sign else 1-x[v] for v,sign in C) for C in clauses):
            ans+=1
    return ans

def ie_count(n, clauses):
    m=len(clauses)
    total=0
    for mask in range(1<<m):
        forced={}
        ok=True
        chosen=0
        for ci,C in enumerate(clauses):
            if (mask>>ci)&1:
                chosen+=1
                for v,sign in C:
                    value=0 if sign else 1
                    if v in forced and forced[v]!=value:
                        ok=False
                        break
                    forced[v]=value
                if not ok:
                    break
        if ok:
            total += (-1)**chosen * 2**(n-len(forced))
    return total

def main():
    u=(1,1); e0=(1,0); e1=(0,1)
    OR=add(tensor3(u,u,u),tensor3(e0,e0,e0),-1)
    COPY=add(tensor3(e0,e0,e0),tensor3(e1,e1,e1))
    assert mat_vec(B,u)==e0
    assert mat_vec(B,e0)==(0,-1)
    assert transform3(B,B,B,OR)==COPY

    rng=random.Random(0xE10)
    for n in range(1,7):
        for _ in range(200):
            m=rng.randint(0,min(8,max(1,2*n)))
            clauses=[]
            for __ in range(m):
                ar=min(3,n)
                vs=rng.sample(range(n),ar)
                clauses.append([(v,rng.randint(0,1)) for v in vs])
            assert sat_count(n,clauses)==ie_count(n,clauses)

    print("R5 E10 OR/COPY + inclusion-exclusion sanity: PASS")

if __name__=="__main__":
    main()
