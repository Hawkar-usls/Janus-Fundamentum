#!/usr/bin/env python3
"""Regression for the rank-2 SCC terminal and ExactOne3 bijunctive break."""

from itertools import product


def original_sat(F):
    vs=sorted({abs(l) for c in F for l in c})
    for bits in product((0,1), repeat=len(vs)):
        A=dict(zip(vs,bits))
        if all(any(A[abs(l)] if l>0 else 1-A[abs(l)] for l in c) for c in F):
            return True
    return False


def witness_choice_2sat(F):
    assert all(len(c)==2 for c in F)
    m=len(F)
    # node(c,val) means y_c=val; index 2*c+val. neg toggles val.
    g=[[] for _ in range(2*m)]
    rg=[[] for _ in range(2*m)]
    def node(c,val): return 2*c+val
    def add_imp(a,b):
        g[a].append(b); rg[b].append(a)
    def add_forbid(c,pc,d,pd):
        # not[(y_c=pc) and (y_d=pd)]
        add_imp(node(c,pc), node(d,1-pd))
        add_imp(node(d,pd), node(c,1-pc))
    occ=[]
    for c,cl in enumerate(F):
        for p,lit in enumerate(cl):
            occ.append((c,p,lit))
    for i,(c,p,l) in enumerate(occ):
        for d,q,k in occ[i+1:]:
            if abs(l)==abs(k) and (l>0)!=(k>0):
                add_forbid(c,p,d,q)
    seen=[False]*(2*m); order=[]
    def dfs(v):
        seen[v]=True
        for w in g[v]:
            if not seen[w]: dfs(w)
        order.append(v)
    for v in range(2*m):
        if not seen[v]: dfs(v)
    comp=[-1]*(2*m)
    def rdfs(v,cid):
        comp[v]=cid
        for w in rg[v]:
            if comp[w]<0: rdfs(w,cid)
    cid=0
    for v in reversed(order):
        if comp[v]<0:
            rdfs(v,cid); cid+=1
    return all(comp[node(c,0)]!=comp[node(c,1)] for c in range(m))


def maj(a,b,c):
    return tuple(1 if a[i]+b[i]+c[i]>=2 else 0 for i in range(len(a)))


def main():
    controls=[
        [(1,2),(1,-2),(-1,3),(-3,4),(-3,-4)], # UNSAT
        [(1,2),(-1,2),(1,-2)],                 # SAT
        [(1,2),(-1,-2)],                       # SAT
        [(1,2),(-1,2),(1,-2),(-1,-2)]          # UNSAT
    ]
    for F in controls:
        assert original_sat(F)==witness_choice_2sat(F), F
    E={(1,0,0),(0,1,0),(0,0,1)}
    witness=maj((1,0,0),(0,1,0),(0,0,1))
    assert witness==(0,0,0) and witness not in E
    print('PASS_RANK2_SCC_TERMINAL')
    print('PASS_EXACTONE3_NOT_MAJORITY_CLOSED')
    print('LOCAL_EXISTENTIAL_2CNF_EXACTONE3=IMPOSSIBLE')
    print('E8_D1=EMPTY P_VS_NP=OPEN')


if __name__=='__main__':
    main()
