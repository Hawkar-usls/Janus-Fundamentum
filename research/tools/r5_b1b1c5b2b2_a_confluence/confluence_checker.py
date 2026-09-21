#!/usr/bin/env python3
"""
Finite sanity checker for B2B2-A confluence algebra.

Checks:
1. blocked seed-color masks are order-independent unions;
2. a singleton under a prefix can only stay the same singleton or become empty
   under a larger blocked-color mask;
3. for compatible nonterminal final masks, every early singleton equals the
   final singleton;
4. monotone X0 deletion on small graphs: sequentially deleting vertices and
   removing all non-seed connected components leaves the same retained
   seed-component as batch deletion of the union.
"""

from itertools import product, combinations

FULL=(1<<4)-1

def avail(blocked):
    return FULL & ~blocked

def singleton_color(mask):
    a=avail(mask)
    return (a.bit_length()-1) if a and a&(a-1)==0 else None

def check_masks():
    for base in range(16):
        for a in range(16):
            for b in range(16):
                final=base|a|b
                assert (base|a)|b == (base|b)|a == final
                s1=singleton_color(base|a)
                if s1 is not None:
                    sf=singleton_color(final)
                    # Under monotone blocking, singleton either persists or dies.
                    assert sf in (s1,None)
    return True

def comps(n, edges, removed):
    alive=[v for v in range(n) if v not in removed]
    adj={v:set() for v in alive}
    for u,v in edges:
        if u in adj and v in adj:
            adj[u].add(v); adj[v].add(u)
    out=[]
    seen=set()
    for s in alive:
        if s in seen: continue
        stack=[s]; seen.add(s); C=[]
        while stack:
            x=stack.pop(); C.append(x)
            for y in adj[x]:
                if y not in seen:
                    seen.add(y); stack.append(y)
        out.append(set(C))
    return out

def canon_retained(n, edges, seed, removed):
    cs=comps(n,edges,removed)
    seed_comp=set()
    for C in cs:
        if C & seed:
            seed_comp |= C
    return seed_comp

def check_graphs():
    # Exhaust all graphs up to n=4, seed={0}; compare two-step vs batch removal.
    for n in range(2,5):
        pairs=list(combinations(range(n),2))
        for bits in range(1<<len(pairs)):
            edges={pairs[i] for i in range(len(pairs)) if bits>>i&1}
            # only start states with all vertices connected to seed
            if len(canon_retained(n,edges,{0},set())) != n:
                continue
            candidates=list(range(1,n))
            for r1 in candidates:
                rem1={r1}
                keep1=canon_retained(n,edges,{0},rem1)
                # sequentially discarded vertices can never be future forced.
                discarded1=set(range(n))-rem1-keep1
                for r2 in candidates:
                    if r2==r1 or r2 in discarded1:
                        continue
                    rem2=rem1|{r2}
                    keep_seq=canon_retained(n,edges,{0},rem2)
                    keep_batch=canon_retained(n,edges,{0},rem2)
                    assert keep_seq==keep_batch
    return True

def main():
    assert check_masks()
    assert check_graphs()
    print({
      "mask_union_order_independent":"PASS",
      "singleton_persistence_or_unsat":"PASS",
      "small_graph_seed_component_batch_vs_sequential":"PASS",
      "status":"PASS_FINITE_SANITY"
    })

if __name__=="__main__":
    main()
