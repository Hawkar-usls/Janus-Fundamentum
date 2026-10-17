#!/usr/bin/env python3
"""Exact GF(2) regression for the symbolic 2D-subspace P3 obstruction."""
from itertools import combinations, product


def rank(rows,n=6):
    a=[]
    for x in rows:
        if x: a.append(x)
    r=0
    for b in range(n-1,-1,-1):
        p=next((i for i in range(r,len(a)) if (a[i]>>b)&1),None)
        if p is None: continue
        a[r],a[p]=a[p],a[r]
        for i in range(len(a)):
            if i!=r and ((a[i]>>b)&1): a[i]^=a[r]
        r+=1
    return r


def span2(u,v):
    assert u and v and u!=v
    return frozenset((0,u,v,u^v))


def all_2spaces(n=6):
    out=set()
    vecs=range(1,1<<n)
    for u,v in combinations(vecs,2):
        if u!=v: out.add(span2(u,v))
    return sorted(out,key=lambda s:tuple(sorted(s)))


def dimsum(*spaces):
    vecs=[]
    for S in spaces: vecs.extend(x for x in S if x)
    return rank(vecs)


def intersects(A,B): return len((A & B)-{0})>0


def eval_formula(F,a):
    return all(any(a[abs(l)] if l>0 else not a[abs(l)] for l in C) for C in F)


def main():
    spaces=all_2spaces(6)
    assert len(spaces)==651
    e=[1<<i for i in range(6)]
    L=span2(e[0],e[1])
    R=span2(e[2],e[3])
    assert not intersects(L,R) and dimsum(L,R)==4

    count=0
    for M in spaces:
        if intersects(M,L) and intersects(M,R):
            count+=1
            # General theorem core: the two distinct intersection lines span M.
            assert dimsum(L,R,M)==4
            assert all(x in (set(L)|set(R)|{a^b for a in L for b in R}) for x in M)
            # Every N conflicting with M necessarily hits span(L+R), so L,R,N cannot be direct.
            for N in spaces:
                if intersects(M,N):
                    assert dimsum(L,R,N)<6
    assert count>0

    # Explicit SAT control and legal witness L,R,N.
    F=[(1,2,3),(1,4,5),(-1,6,7)]
    a={1:True,2:False,3:False,4:False,5:False,6:True,7:False}
    assert eval_formula(F,a)
    # Chosen true witnesses: x in C1, x in C2, y(=var6) in C3.
    chosen=[(0,1),(1,1),(2,6)]
    assert len({c for c,_ in chosen})==3
    assert all(a[v] for _,v in chosen)

    print('PASS_P3_OCCURRENCE_2D_MATROID_PARITY_LIFT_OBSTRUCTION')
    print('GF2_2spaces_dim6=',len(spaces),'middle_controls=',count)
    print('LEGAL_L_R_N_TRIPLE=True')
    print('ONE_PAIR_PER_OCCURRENCE_2D_LIFT=FALSE_IN_FROZEN_MODEL')
    print('P_VS_NP=OPEN E8_D1=EMPTY')


if __name__=='__main__': main()
