#!/usr/bin/env python3
"""Independent memoized DP audit of sevenblock loopless multigraph counts.

Independent from graph-listing C++ generator: no enumerated graphs,
no connectivity routines, no orbit canonicalization.
For each of the 21 distinct block pairs select a multiplicity >=0,
with sum of multiplicities exactly 11 and max block degree <=4.

Result: 5,229,168 degree-feasible labelled multigraph edge-multisets.
With prescribed one hub degree four and six terminal degrees three:
exactly 13,440 labelled edge-multisets.

This DP is an independent arithmetic control on two input universes,
NOT a proof that the 2-edge-connected colour-signature cases are UNSAT.
"""
from functools import lru_cache
from itertools import combinations

PAIRS=tuple(combinations(range(7),2))
HUB_TARGET=(4,3,3,3,3,3,3)


@lru_cache(None)
def count_bounded(k,needed,degrees):
    if needed==0:return 1
    if k==len(PAIRS):return 0
    u,v=PAIRS[k]
    limit=min(needed,4-degrees[u],4-degrees[v])
    total=0
    for m in range(limit+1):
        next_degrees=list(degrees)
        next_degrees[u]+=m
        next_degrees[v]+=m
        total+=count_bounded(k+1,needed-m,tuple(next_degrees))
    return total


@lru_cache(None)
def count_hub_exact(k,needed,degrees):
    if needed==0:return int(degrees==HUB_TARGET)
    if k==len(PAIRS):return 0
    u,v=PAIRS[k]
    limit=min(needed,HUB_TARGET[u]-degrees[u],
              HUB_TARGET[v]-degrees[v])
    total=0
    for m in range(limit+1):
        next_degrees=list(degrees)
        next_degrees[u]+=m
        next_degrees[v]+=m
        total+=count_hub_exact(k+1,needed-m,tuple(next_degrees))
    return total


def main():
    broad=count_bounded(0,11,(0,)*7)
    hub=count_hub_exact(0,11,(0,)*7)
    assert broad==5229168,broad
    assert hub==13440,hub
    print("INDEPENDENT_MEMOIZED_DEGREE_DP",{
        "all_sevenblock_multigraph_degree_eligible":broad,
        "unique_fourinterface_hub_degree_realizations":hub,
        "broad_DP_states":count_bounded.cache_info().currsize,
        "hub_DP_states":count_hub_exact.cache_info().currsize,
        "not_a_colouring_or_connectedness_certificate":True,
    },flush=True)


if __name__=="__main__":
    main()
