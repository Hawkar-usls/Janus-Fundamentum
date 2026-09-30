#!/usr/bin/env python3
"""Exact regression for the implication-primitive rank-3 terminal normal form."""

from itertools import product, combinations


def canon_clause(c):
    # remove duplicate literals; tautology => None (always true)
    s=set(c)
    if any(-l in s for l in s):
        return None
    return tuple(sorted(s, key=lambda x:(abs(x), x<0)))


def simplify_formula(F):
    out=[]
    seen=set()
    for c in F:
        q=canon_clause(c)
        if q is None:
            continue
        if not q:
            return [tuple()]
        if q not in seen:
            seen.add(q); out.append(q)
    return out


def eval_formula(F,A):
    for c in F:
        if not c:
            return False
        if not any(A.get(abs(l),0) if l>0 else 1-A.get(abs(l),0) for l in c):
            return False
    return True


def satisfiable(F):
    vs=sorted({abs(l) for c in F for l in c})
    if any(len(c)==0 for c in F): return False
    for bits in product((0,1), repeat=len(vs)):
        A=dict(zip(vs,bits))
        if eval_formula(F,A): return True
    return False


def implication_closure(H):
    H=simplify_formula(H)
    if any(len(c)==0 for c in H): return None,None
    vs=sorted({abs(l) for c in H for l in c})
    lits=[]
    for v in vs: lits.extend((v,-v))
    idx={l:i for i,l in enumerate(lits)}
    g=[[] for _ in lits]
    for c in H:
        assert len(c)<=2
        if len(c)==1:
            a=c[0]
            g[idx[-a]].append(idx[a])
        else:
            a,b=c
            g[idx[-a]].append(idx[b]); g[idx[-b]].append(idx[a])
    reach=[]
    for s in range(len(lits)):
        seen={s}; stack=[s]
        while stack:
            u=stack.pop()
            for w in g[u]:
                if w not in seen:
                    seen.add(w); stack.append(w)
        reach.append(seen)
    for v in vs:
        if idx[-v] in reach[idx[v]] and idx[v] in reach[idx[-v]]:
            return None,None
    def entails_imp(a,b):
        if a not in idx or b not in idx:
            return a==b
        return idx[b] in reach[idx[a]]
    def entails_lit(a):
        return entails_imp(-a,a)
    def entails_clause2(a,b):
        # H |= a OR b iff H |= (not a -> b); for satisfiable 2-CNF.
        return entails_imp(-a,b)
    return (entails_imp,entails_lit,entails_clause2),H


def primitive_normal_form(F):
    F=simplify_formula(F)
    H=[c for c in F if len(c)<=2]
    F3=[c for c in F if len(c)==3]
    if any(len(c)==0 for c in H): return [tuple()]

    changed=True
    while changed:
        changed=False
        funcs,Hc=implication_closure(H)
        if funcs is None:
            return [tuple()]
        entails_imp,entails_lit,entails_clause2=funcs
        H=Hc
        newF3=[]
        for c in F3:
            lits=list(c)
            # forced true => delete clause
            if any(entails_lit(a) for a in lits):
                changed=True
                continue
            # forced false => delete literal(s)
            kept=[a for a in lits if not entails_lit(-a)]
            if len(kept)<3:
                changed=True
                q=canon_clause(kept)
                if q is None:
                    continue
                if len(q)==0:
                    return [tuple()]
                if len(q)<=2:
                    H.append(q)
                    continue
                lits=list(q)
            # entailed subclause => redundant
            redundant=False
            for a,b in combinations(lits,2):
                if entails_clause2(a,b):
                    redundant=True; break
            if redundant:
                changed=True
                continue
            # implication domination a->b: (a or b or c) == (b or c) under H
            reduced=None
            for a in lits:
                for b in lits:
                    if a!=b and entails_imp(a,b):
                        reduced=tuple(x for x in lits if x!=a)
                        break
                if reduced is not None: break
            if reduced is not None:
                changed=True
                q=canon_clause(reduced)
                if q is None:
                    continue
                H.append(q)
                continue
            newF3.append(tuple(lits))
        F3=newF3
    return simplify_formula(H+F3)


def is_primitive(F):
    H=[c for c in F if len(c)<=2]
    F3=[c for c in F if len(c)==3]
    funcs,_=implication_closure(H)
    if funcs is None: return True
    entails_imp,entails_lit,entails_clause2=funcs
    for c in F3:
        for a in c:
            if entails_lit(a) or entails_lit(-a): return False
        for a,b in combinations(c,2):
            if entails_clause2(a,b): return False
            if entails_imp(a,b) or entails_imp(b,a): return False
    return True


def exhaustive():
    vars_=(1,2,3)
    pool=[]
    for size in (1,2,3):
        for vs in combinations(vars_,size):
            for signs in product((1,-1), repeat=size):
                pool.append(tuple(s*v for s,v in zip(signs,vs)))
    checked=0
    # exhaustive combinations up to 4 clauses from this finite pool
    for r in range(5):
        for ids in combinations(range(len(pool)),r):
            F=[pool[i] for i in ids]
            N=primitive_normal_form(F)
            assert satisfiable(F)==satisfiable(N), (F,N)
            assert is_primitive(N), (F,N)
            checked+=1
    return checked


def targeted():
    cases=[
        # a->b makes (a or b or c) reduce to (b or c)
        [(-1,2),(1,2,3)],
        # forced false literal
        [(-1,), (1,2,3)],
        # forced true literal deletes clause
        [(1,), (1,2,3)],
        # binary subclause entails whole 3-clause
        [(1,2),(1,2,3)],
        # cascading reduction
        [(-1,2),(-2,3),(1,2,3),(1,-3,2)],
    ]
    for F in cases:
        N=primitive_normal_form(F)
        assert satisfiable(F)==satisfiable(N), (F,N)
        assert is_primitive(N), (F,N)


def main():
    n=exhaustive(); targeted()
    print('PASS_TERMINAL_RANK3_IMPLICATION_PRIMITIVE_NORMAL_FORM')
    print(f'exhaustive_formulas_checked={n}')
    print('SAT_equivalence=True primitive_fixed_point=True')
    print('E8_D1=EMPTY P_VS_NP=OPEN')


if __name__=='__main__': main()
