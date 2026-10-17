#!/usr/bin/env python3
"""Exact regression for IF2E router and the n=15 three-external hostile control."""
from itertools import combinations, product
import json

P=[14,5,13,10,11,6,3,1,12,8,2,7,0,4,9]
Q=[7,8,11,13,14,0,1,12,3,2,6,9,4,5,10]


def source_matrix(P,Q):
    n=len(P); A=[[0]*n for _ in range(n)]
    for i in range(n):
        for j in (i,P[i],Q[i]): A[i][j]=1
    assert all(sum(r)==3 for r in A)
    assert all(sum(A[i][j] for i in range(n))==3 for j in range(n))
    supp=[{j for j,v in enumerate(r) if v} for r in A]
    assert all(len(supp[i]&supp[j])<=1 for i in range(n) for j in range(i))
    return A


def cols(A):
    n=len(A); out=[]
    for j in range(n):
        v=0
        for i in range(n):
            if A[i][j]: v|=1<<i
        out.append(v)
    return out


def basis(C,S):
    B={}
    for j in sorted(S):
        v=C[j]; comb=1<<j
        while v:
            p=v.bit_length()-1
            if p in B:
                v^=B[p][0]; comb^=B[p][1]
            else:
                B[p]=(v,comb); break
        if v==0: return B,comb
    return B,None


def solve_span(C,S,target):
    B,dep=basis(C,S); assert dep is None
    v=target; comb=0
    while v:
        p=v.bit_length()-1
        if p not in B: return None
        v^=B[p][0]; comb^=B[p][1]
    return comb


def bits(mask,n): return {i for i in range(n) if (mask>>i)&1}


def matvec_mod2(A,S):
    return [sum(A[r][j] for j in S)%2 for r in range(len(A))]


def router(A):
    C=cols(A); n=len(C); S=set(range(n)); moves=[]
    while True:
        _,dep=basis(C,S)
        if dep is not None:
            D=bits(dep,n); S-=D; moves.append(("zero",sorted(D),len(S))); continue

        moved=False
        for e in range(n):
            if e in S: continue
            sol=solve_span(C,S,C[e])
            if sol is not None:
                T=bits(sol,n); assert len(T)>=2
                S=(S-T)|{e}; moves.append(("one",e,sorted(T),len(S))); moved=True; break
        if moved: continue

        outside=[e for e in range(n) if e not in S]
        for e,f in combinations(outside,2):
            sol=solve_span(C,S,C[e]^C[f])
            if sol is not None:
                T=bits(sol,n)
                if len(T)>=4:
                    S=(S-T)|{e,f}; moves.append(("two",(e,f),sorted(T),len(S))); moved=True; break
        if moved: continue
        return S,moves


def kernel(A):
    n=len(A); out=[]
    for mask in range(1<<n):
        S=bits(mask,n)
        if all(v==0 for v in matvec_mod2(A,S)): out.append(mask)
    return out


def is_independent(C,S): return basis(C,S)[1] is None


def verify_terminal(A,S):
    C=cols(A); n=len(C)
    assert is_independent(C,S)
    # closed
    for e in range(n):
        if e not in S: assert solve_span(C,S,C[e]) is None
    # no negative two-external move
    for e,f in combinations([i for i in range(n) if i not in S],2):
        sol=solve_span(C,S,C[e]^C[f])
        if sol is not None: assert len(bits(sol,n))<=2


def main():
    A=source_matrix(P,Q); n=15; C=cols(A)
    assert matvec_mod2(A,set(range(n)))==[1]*n

    S,moves=router(A)
    assert S=={0,1,4,7,9,10,11,12,14}
    assert len(S)==9
    verify_terminal(A,S)

    K=kernel(A)
    assert len(K)==4
    weights=sorted(m.bit_count() for m in K)
    assert weights==[0,6,8,8]
    global_min=n-max(weights)
    assert global_min==7

    Sstar={0,4,5,6,9,12,13}
    assert matvec_mod2(A,Sstar)==[1]*n
    D=S^Sstar
    assert D=={1,5,6,7,10,11,13,14}
    assert matvec_mod2(A,D)==[0]*n
    inside=D&S; outside=D-S
    assert len(inside)==5 and len(outside)==3
    assert len(Sstar)-len(S)==-2

    # Circuit minimality: no nonempty proper kernel support is contained in D.
    for m in K:
        T=bits(m,n)
        if T and T!=D: assert not T < D

    # Exhaust Exact-One models to bind UNSAT status of the control.
    models=0
    for mask in range(1<<n):
        X=bits(mask,n)
        if all(sum(A[r][j] for j in X)==1 for r in range(n)):
            models+=1
    assert models==0

    print(json.dumps({
      "status":"PASS_IF2E_THREE_EXTERNAL_HOSTILE_CONTROL",
      "n":n,
      "kernel_weights":weights,
      "if2e_terminal_support":sorted(S),
      "if2e_terminal_weight":len(S),
      "global_parity_minimum":global_min,
      "missing_circuit":sorted(D),
      "missing_inside":sorted(inside),
      "missing_outside":sorted(outside),
      "missing_charge":len(outside)-len(inside),
      "exact_one_models":models,
      "scientific_boundary":{"E8_D1":"EMPTY","P_VS_NP":"OPEN"}
    },indent=2,sort_keys=True))

if __name__=='__main__': main()
