#!/usr/bin/env python3
"""R5 E124: all one-check affine-closure branches on E123 Tutte-12."""

from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product

from r5_e64_connected_postquotient_nullity_firewall import (
    rank_q,
    tutte12_incidence,
    verify_square_cubic_linear,
)


def propagate(clauses, n, initial):
    vals=[None]*n
    for j,v in initial.items():
        vals[j]=v
    changed=True
    while changed:
        changed=False
        for vs in clauses:
            ones=sum(vals[j]==1 for j in vs)
            unk=[j for j in vs if vals[j] is None]
            if ones>1 or (ones==0 and not unk):
                return None
            if ones==1:
                for j in unk:
                    vals[j]=0
                    changed=True
            elif len(unk)==1:
                vals[unk[0]]=1
                changed=True
    return vals


def quotient(clauses, vals):
    unknown=[j for j,v in enumerate(vals) if v is None]
    xor=[]
    tern=[]
    for vs in clauses:
        u=[j for j in vs if vals[j] is None]
        if len(u)==2:
            xor.append(tuple(u))
        elif len(u)==3:
            tern.append(tuple(u))
        elif len(u)==1:
            raise AssertionError("unit propagation not closed")

    g=defaultdict(list)
    for a,b in xor:
        g[a].append((b,1))
        g[b].append((a,1))

    parity={}
    compid={}
    comps=[]
    for v in unknown:
        if v in parity:
            continue
        cid=len(comps)
        parity[v]=0
        stack=[v]
        comp=[]
        while stack:
            u=stack.pop()
            compid[u]=cid
            comp.append(u)
            for w,p in g[u]:
                want=parity[u]^p
                if w in parity:
                    if parity[w]!=want:
                        return None
                else:
                    parity[w]=want
                    stack.append(w)
        comps.append(comp)

    qtern=[tuple((compid[v],parity[v]) for v in tri) for tri in tern]
    return unknown,comps,parity,compid,qtern


def affine_closure(clauses, n, initial):
    assigned=dict(initial)

    while True:
        vals=propagate(clauses,n,assigned)
        if vals is None:
            return None

        q=quotient(clauses,vals)
        if q is None:
            return None
        unknown,comps,parity,compid,qtern=q

        forced={}
        repeated=0
        for tri in qtern:
            ids=sorted(set(c for c,p in tri))
            if len(ids)==3:
                continue

            repeated+=1
            loc={c:i for i,c in enumerate(ids)}
            allowed=[]
            for av in product((0,1),repeat=len(ids)):
                lits=[av[loc[c]]^p for c,p in tri]
                if sum(lits)==1:
                    allowed.append(av)

            if not allowed:
                return None

            for k,c in enumerate(ids):
                s={a[k] for a in allowed}
                if len(s)==1:
                    value=next(iter(s))
                    if c in forced and forced[c]!=value:
                        return None
                    forced[c]=value

        if forced:
            for c,t in forced.items():
                for v in comps[c]:
                    assigned[v]=t^parity[v]
            continue

        assert repeated==0
        return vals,unknown,comps,parity,compid,qtern


def signed_matrix(comps,qtern):
    rows=[]
    rhs=[]
    for tri in qtern:
        row=[0]*len(comps)
        ones=0
        for c,p in tri:
            if p:
                row[c]-=1
                ones+=1
            else:
                row[c]+=1
        rows.append(row)
        rhs.append(1-ones)
    return rows,rhs


def main():
    A=tutte12_incidence()
    n=len(A)
    assert n==63
    verify_square_cubic_linear(A,expected_girth=12)
    assert rank_q(A)==49
    base_nullity=n-rank_q(A)
    assert base_nullity==14

    clauses=[[j for j,v in enumerate(A[i]) if v] for i in range(n)]
    profiles=Counter()
    ranks=Counter()
    contradictions=0

    for c,vs in enumerate(clauses):
        assert len(vs)==3
        for chosen in vs:
            initial={j:(1 if j==chosen else 0) for j in vs}
            out=affine_closure(clauses,n,initial)
            if out is None:
                contradictions+=1
                continue

            vals,unknown,comps,parity,compid,qtern=out
            sizes=tuple(sorted((len(C) for C in comps),reverse=True))
            profiles[(len(unknown),len(comps),len(qtern),sizes)]+=1

            M,rhs=signed_matrix(comps,qtern)
            r=rank_q(M)
            # Consistency check over Q.
            aug=[row+[rhs[i]] for i,row in enumerate(M)]
            assert rank_q(aug)==r
            ranks[(r,len(comps)-r)]+=1

    assert contradictions==0

    expected_sizes=(2,)*12 + (1,)*32
    assert profiles==Counter({
        (56,44,48,expected_sizes):189
    })
    assert ranks==Counter({(34,10):189})

    print("R5 E124 Tutte-12 affine-support firewall: PASS")
    print("base q=63 rank_Q=49 nullity=14")
    print("one-check pin branches=189; affine contradictions=0")
    print("all branches: unknown=56 components=44 proper_ternary=48")
    print("all component multisets: 12x size2 + 32x size1")
    print("all signed quotient ranks=34; effective nullity=10")
    print("local affine closure apparent SUPPORT_c=111 at every check, yet E123 is UNSAT")
    print("finite nullity descent 14 -> 10; universal shrink theorem remains OPEN")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
