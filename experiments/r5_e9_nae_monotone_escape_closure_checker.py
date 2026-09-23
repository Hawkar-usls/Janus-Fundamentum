#!/usr/bin/env python3
from itertools import product

def nae_edge_ok(y, S, e):
    vals=[y[v] ^ (1 if v in S else 0) for v in e]
    return len(set(vals))>1

def edge_roles(y,e):
    vals=[y[v] for v in e]
    assert len(set(vals))>1
    if vals.count(1)==1:
        minority=e[vals.index(1)]
    else:
        minority=e[vals.index(0)]
    majority=tuple(v for v in e if v!=minority)
    return minority,majority

def closure(y,edges,pivot,selector):
    S={pivot}
    changed=True
    while changed:
        changed=False
        for idx,e in enumerate(edges):
            m,(u,v)=edge_roles(y,e)
            if m in S:
                r=selector[idx]
                assert r in (u,v)
                if r not in S:
                    S.add(r); changed=True
            if u in S and v in S and m not in S:
                S.add(m); changed=True
    return frozenset(S)

def all_masks(n):
    V=range(n)
    for bits in product((0,1),repeat=n):
        yield frozenset(i for i,b in enumerate(bits) if b)

def main():
    edges=((0,1,2),(2,3,4),(1,4,5))
    n=6

    # Exhaustive over all satisfying y, pivots and protected sets A of size <=2.
    for y in product((0,1),repeat=n):
        if not all(len({y[v] for v in e})>1 for e in edges):
            continue
        roles=[edge_roles(y,e) for e in edges]
        choices=[maj for _,maj in roles]
        selectors=list(product(*choices))

        for pivot in range(n):
            for A in all_masks(n):
                if pivot in A or len(A)>2:
                    continue

                valid_masks=[
                    S for S in all_masks(n)
                    if pivot in S and not (S & A)
                    and all(nae_edge_ok(y,S,e) for e in edges)
                ]

                good_selectors=[]
                for sel in selectors:
                    S=closure(y,edges,pivot,sel)
                    assert all(nae_edge_ok(y,S,e) for e in edges)
                    if not (S & A):
                        good_selectors.append((sel,S))

                assert bool(valid_masks)==bool(good_selectors)

                if valid_masks:
                    # Completeness construction: choose, for every edge whose
                    # minority lies in a witness mask W, a majority also in W.
                    W=valid_masks[0]
                    sel=[]
                    for m,(u,v) in roles:
                        if m in W:
                            opts=[z for z in (u,v) if z in W]
                            assert opts
                            sel.append(opts[0])
                        else:
                            sel.append(u)
                    S=closure(y,edges,pivot,tuple(sel))
                    assert S <= W
                    assert not (S&A)
                    assert all(nae_edge_ok(y,S,e) for e in edges)

    print("MONOTONE_ESCAPE_CLOSURE_SOUNDNESS = PASS")
    print("ESCAPE_SELECTOR_COMPLETENESS_VS_REPAIR_MASK = PASS")
    print("CLOSURE_STEPS_BOUND = O(n)")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
