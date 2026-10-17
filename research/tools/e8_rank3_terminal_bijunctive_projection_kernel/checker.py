#!/usr/bin/env python3
"""Exact regression for the rank-3 terminal bijunctive projection kernel."""

from itertools import product, combinations


def eval_formula(F,A):
    return all(any(A[abs(l)] if l>0 else 1-A[abs(l)] for l in c) for c in F)


def satisfiable(F):
    vs=sorted({abs(l) for c in F for l in c})
    for bits in product((0,1), repeat=len(vs)):
        A=dict(zip(vs,bits))
        if eval_formula(F,A): return True
    return False


def project_2cnf(F2, terminals):
    vars_=sorted({abs(l) for c in F2 for l in c} | set(terminals))
    if not vars_:
        return []
    lits=[]
    for v in vars_: lits.extend((v,-v))
    idx={l:i for i,l in enumerate(lits)}
    g=[[] for _ in lits]
    for c in F2:
        if len(c)==1:
            a=c[0]; g[idx[-a]].append(idx[a])
        else:
            a,b=c
            g[idx[-a]].append(idx[b]); g[idx[-b]].append(idx[a])
    reach=[]
    for s in range(len(lits)):
        seen={s}; stack=[s]
        while stack:
            u=stack.pop()
            for v in g[u]:
                if v not in seen:
                    seen.add(v); stack.append(v)
        reach.append(seen)
    for v in vars_:
        if idx[-v] in reach[idx[v]] and idx[v] in reach[idx[-v]]:
            return None
    tlits=[]
    for v in sorted(terminals): tlits.extend((v,-v))
    H=set()
    for a in tlits:
        for b in tlits:
            if idx[b] in reach[idx[a]]:
                H.add(tuple(sorted((-a,b))))
    return sorted(H)


def kernel(F):
    F2=[tuple(c) for c in F if len(c)<=2]
    F3=[tuple(c) for c in F if len(c)==3]
    T={abs(l) for c in F3 for l in c}
    H=project_2cnf(F2,T)
    if H is None:
        # explicit contradiction on a fresh dummy terminal for checking only
        d=max([abs(l) for c in F for l in c] or [0])+1
        return [(d,),(-d,)],T
    return H+F3,T


def exhaustive():
    # Exhaust all formulas made from up to four clauses selected from a small
    # mixed 2/3-clause pool on three variables.
    vars_=(1,2,3)
    pool=[]
    for size in (2,3):
        for vs in combinations(vars_,size):
            for signs in product((1,-1), repeat=size):
                pool.append(tuple(s*v for s,v in zip(signs,vs)))
    checked=0
    for r in range(0,5):
        # deterministic prefix-bounded census keeps CI small while mixing all forms
        for ids in combinations(range(len(pool)),r):
            F=[pool[i] for i in ids]
            K,T=kernel(F)
            assert satisfiable(F)==satisfiable(K), (F,K,T)
            assert len(T)<=3*sum(len(c)==3 for c in F)
            checked+=1
    return checked


def controls():
    tests=[
        [(1,2),(1,-2),(-1,3),(-3,4),(-3,-4)],
        [(1,2),(-1,3),(1,-2,4),(-3,-4,2)],
        [(1,-2,3),(-1,2),(-3,4),(1,-4,2)],
        [(1,2,3),(-1,-2,-3)],
    ]
    for F in tests:
        K,T=kernel(F)
        assert satisfiable(F)==satisfiable(K), (F,K)


def main():
    n=exhaustive(); controls()
    print('PASS_RANK3_TERMINAL_BIJUNCTIVE_PROJECTION_KERNEL')
    print(f'exhaustive_formulas_checked={n}')
    print('kernel_terminal_variables<=3k')
    print('kernel_binary_clauses=O(k^2)')
    print('E8_D1=EMPTY P_VS_NP=OPEN')


if __name__=='__main__': main()
