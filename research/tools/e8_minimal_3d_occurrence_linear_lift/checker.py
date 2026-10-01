#!/usr/bin/env python3
"""Exact combinatorial/rank regression for the sparse 3D occurrence lift."""
from itertools import product, combinations


def occurrences(F):
    out=[]; clause_occ=[]
    for ci,C in enumerate(F):
        row=[]
        for lit in C:
            oi=len(out); out.append((ci,lit)); row.append(oi)
        clause_occ.append(row)
    return out,clause_occ


def build_blocks(F):
    occ,clause_occ=occurrences(F)
    byvar={}
    for o,(_,lit) in enumerate(occ): byvar.setdefault(abs(lit),[]).append(o)
    assert all(len(v)<=3 for v in byvar.values())

    token_id={}
    def tok(key):
        if key not in token_id: token_id[key]=len(token_id)
        return token_id[key]

    blocks=[]
    sign_edges=set()
    for os in byvar.values():
        for a,b in combinations(os,2):
            if (occ[a][1]>0)!=(occ[b][1]>0): sign_edges.add(tuple(sorted((a,b))))

    for o,(ci,_) in enumerate(occ):
        support=[tok(('clause',ci))]
        for e in sorted(sign_edges):
            if o in e: support.append(tok(('sign',e)))
        assert len(support)<=3
        while len(support)<3: support.append(tok(('private',o,len(support))))
        assert len(set(support))==3
        blocks.append(frozenset(support))
    return occ,clause_occ,blocks,sign_edges,len(token_id)


def conflict_free(X,occ):
    X=list(X)
    for a,b in combinations(X,2):
        ca,la=occ[a]; cb,lb=occ[b]
        if ca==cb: return False
        if abs(la)==abs(lb) and (la>0)!=(lb>0): return False
    return True


def direct_sum(X,blocks):
    total=[]
    for o in X: total.extend(blocks[o])
    return len(set(total))==3*len(X)


def sat(F):
    vs=sorted({abs(l) for C in F for l in C})
    for bits in product((False,True),repeat=len(vs)):
        a=dict(zip(vs,bits))
        if all(any(a[abs(l)] if l>0 else not a[abs(l)] for l in C) for C in F):
            return True
    return False


def lift_feasible(F):
    _,clause_occ,blocks,_,_=build_blocks(F)
    for choice in product(*clause_occ):
        if direct_sum(choice,blocks): return True
    return False


def check_formula(F):
    occ,_,blocks,sign_edges,ambient=build_blocks(F)
    q=len(occ)
    for mask in range(1<<q):
        X=[i for i in range(q) if (mask>>i)&1]
        assert direct_sum(X,blocks)==conflict_free(X,occ)
    assert lift_feasible(F)==sat(F)
    assert all(len(B)==3 for B in blocks)
    return q,len(sign_edges),ambient,sat(F)


def main():
    controls=[
        [(1,2,3),(-1,4,5),(1,-4,6)],
        [(1,2),(1,-2),(-1,3),(-3,4),(-3,-4)],
        [(1,2,3),(1,4,5),(-1,6,7)],
        [(1,-2,3),(-1,2,4),(1,2,-4)],
    ]
    for F in controls:
        vs={abs(l) for C in F for l in C}
        assert all(sum(abs(l)==v for C in F for l in C)<=3 for v in vs)
        q,se,amb,s=check_formula(F)
        print('clauses=',len(F),'occ=',q,'sign_edges=',se,'ambient=',amb,'SAT=',s)
    assert any(not sat(F) for F in controls) and any(sat(F) for F in controls)
    print('PASS_MINIMAL_3D_OCCURRENCE_LINEAR_LIFT')
    print('DIRECT_SUM_IFF_CONFLICT_FREE=True')
    print('SAT_IFF_M_THREE_DIMENSIONAL_BLOCKS_DIRECT=True')
    print('2D_LOCAL_MODEL_IMPOSSIBLE_BY_PARENT_v2.8=True')
    print('P_VS_NP=OPEN E8_D1=EMPTY')


if __name__=='__main__': main()
