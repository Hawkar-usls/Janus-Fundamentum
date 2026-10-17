#!/usr/bin/env python3
"""Replay q8 overlap-junction witness and recursive delta-hierarchy firewall."""

from collections import Counter
from functools import lru_cache

from r5_e81_q8_global_delta_partition_counterexample import (
    Q, Q8_SETS, exhaustive_delta_rows,
)
from r5_e77_source_aligned_delta_composition_frontier import (
    source_matrix, tanner_adj,
)

FULL=(1<<(2*Q))-1
CHECK_MASK=(1<<Q)-1
VAR_MASK=FULL ^ CHECK_MASK

def component_masks(mask,adj):
    out=[]
    rem=mask
    while rem:
        root=(rem & -rem).bit_length()-1
        seen=1<<root
        stack=[root]
        while stack:
            u=stack.pop()
            for v in adj[u]:
                if ((rem>>v)&1) and not ((seen>>v)&1):
                    seen |= 1<<v
                    stack.append(v)
        out.append(seen)
        rem &= ~seen
    return out

def all_delta_masks(A,connected_rows):
    adj=tanner_adj(A)
    connected={r["mask"] for r in connected_rows}
    out={0}
    for mask in range(1,FULL+1):
        if all(c in connected for c in component_masks(mask,adj)):
            out.add(mask)
    return out

def recursive_buildable(delta_masks):
    buildable={1<<i for i in range(2*Q)}
    by_size={}
    for m in delta_masks:
        by_size.setdefault(m.bit_count(),[]).append(m)

    for size in range(2,2*Q+1):
        for m in by_size.get(size,[]):
            if not m:
                continue
            anchor=m & -m
            s=(m-1)&m
            while s:
                if s & anchor:
                    t=m^s
                    if t and s in buildable and t in buildable:
                        buildable.add(m)
                        break
                s=(s-1)&m
    return buildable

def main():
    A=source_matrix(Q,Q8_SETS)
    _,rows=exhaustive_delta_rows(A)
    assert len(rows)==200

    delta=all_delta_masks(A,rows)
    assert len(delta)==448
    assert Counter(m.bit_count() for m in delta)==Counter({
        0:1,1:8,2:28,3:56,4:70,5:56,6:28,7:8,8:1,
        12:48,13:120,14:24,
    })

    var_delta=[m for m in delta if m & VAR_MASK]
    assert len(var_delta)==192
    assert min(m.bit_count() for m in var_delta)==12

    A1=0xdf3f
    B =0x9fff
    C =0xbfbe
    SAB=A1&B
    SBC=B&C
    SAC=A1&C

    assert A1 in delta and B in delta and C in delta
    assert SAB==0x9f3f and SAB in delta and SAB.bit_count()==12
    assert SBC==0x9fbe and SBC in delta and SBC.bit_count()==12
    assert SAC==0x9f3e and SAC not in delta and SAC.bit_count()==11
    assert (SAC & ~B)==0
    assert (A1|B|C)==FULL

    buildable=recursive_buildable(delta)
    assert FULL not in buildable
    assert not any(m in buildable for m in var_delta)

    print("Q8_DELTA_JUNCTION_PATH: PASS")
    print("bags: A=0xdf3f(13), B=0x9fff(14), C=0xbfbe(13)")
    print("adjacent separators: 0x9f3f(12) delta, 0x9fbe(12) delta")
    print("nonadjacent overlap: 0x9f3e(11) non-delta, contained in B")
    print("all induced delta masks=448 including empty")
    print("variable-containing delta masks=192; minimum size=12")
    print("binary recursive delta hierarchy from singleton atoms: FALSE")
    print("variable-containing delta bags recursively buildable: 0")
    print("P_VS_NP remains OPEN")

if __name__=="__main__":
    main()
