#!/usr/bin/env python3
"""E4.3 targeted high-girth admissibility, Moore barrier & separator policy.

For a linear/cubic square SCL source A, the incidence graph B_A is
bipartite degree3 on 2n vertices. Girth >=12 implies the kernel
support graph G_v has girth >=6, hence by the degree-3 Moore
edge-neighborhood bound, |support(v)|>=14 for every nonzero v.

Therefore A4=A6=A8=A10=A12=0 on any such legal source.

A cubic graph ALWAYS has a size-three LOCAL vertex separator
(neighbors of one vertex); demanding an absolute large minimum
separator is meaningless. A relevant adversarial target requires
BALANCED separators (or quantified expansion). This file certifies
absence/presence of balanced separators of size <=2 only. It does
NOT claim a full separator lower bound or a SAT/UNSAT twin.

For bipartite degree3 girth>=12 the Moore bound forces
2n>=2*(1+2+4+8+16+32)=126, n>=63.
"""
import argparse,json
from collections import deque
from itertools import combinations

from r5_local_codeword_anchors_20261015 import (
    linear_validate_and_incidence,local_codewords
)
from r5_local_codeword_anchors_8_10_20261015 import anchor_8_10
from r5_connected_coverage_breaker_20261015 import make_connected
from r5_branch_stable_spectral_twins_20261015 import permute_source
from r5_cooperative_scl_coverage_20261015 import valid_witness,gf2_affine
from r5_component_factor_20261015 import k4_blocks


def incidence_neighbors(rows):
    rows,_=linear_validate_and_incidence(rows)
    n=len(rows)
    g=[set() for _ in range(2*n)]
    for i,row in enumerate(rows):
        for v in row:
            g[i].add(n+v)
            g[n+v].add(i)
    assert all(len(x)==3 for x in g)
    return tuple(tuple(sorted(gv)) for gv in g)


def has_cycle_less_than_12(rows):
    """O(n) fixed-depth BFS short-cycle witness on cubic bipartite B_A.

    For a shortest cycle of length 4/6/8/10, from any vertex
    on the cycle, two breadth-first paths of length <=5 meet
    before depth6. If a cross-edge is discovered between
    already discovered nonparent vertices, a short cycle exists.
    """
    g=incidence_neighbors(rows)
    for root in range(len(g)):
        dist={root:0}
        parent={root:None}
        queue=deque([root])
        while queue:
            u=queue.popleft()
            if dist[u]>=5:
                continue
            for v in g[u]:
                if v not in dist:
                    dist[v]=dist[u]+1
                    parent[v]=u
                    queue.append(v)
                elif parent[u]!=v:
                    return True
    return False


def girth12_gate(rows):
    rows,_=linear_validate_and_incidence(rows)
    n=len(rows)
    if n<63:
        return {"pass":False,"n":n,"reason":"MOORE_SIZE_BARRIER",
                "min_rows_cols":63}
    bad=has_cycle_less_than_12(rows)
    return {"pass":not bad,"n":n,
            "reason":"SHORT_INCIDENCE_CYCLE" if bad else "GIRTH_AT_LEAST_12",
            "min_rows_cols":63,
            "forced_zero_kernel_weights":(4,6,8,10,12) if not bad else ()}


def component_sizes_excluding(g,removed):
    blocked=set(removed)
    seen=set(blocked)
    sizes=[]
    for start in range(len(g)):
        if start in seen:
            continue
        todo=[start]
        seen.add(start)
        size=0
        while todo:
            u=todo.pop()
            size+=1
            for v in g[u]:
                if v not in seen:
                    seen.add(v)
                    todo.append(v)
        sizes.append(size)
    return sizes


def small_balanced_separator_profile(rows,max_removed=2,
                                     fraction=0.25):
    """Exact search ONLY over size<=2 B_A vertex deletion sets.

    A balanced separator exists if some split into TWO disjoint
    unions of resulting components has each side >= alpha*N.
    A sufficient computable test: if components admit such a
    partition. Component sizes are <=O(N). Count check by small
    integer subset-sum DP, with no SAT complexity implications.
    """
    g=incidence_neighbors(rows)
    N=len(g)
    threshold=__import__("math").ceil(fraction*N)
    if not 0<fraction<0.5:
        raise ValueError("fraction between 0 and half required")
    if max_removed not in (0,1,2):
        raise ValueError("only exhaustive k<=2 supported")
    examples=[]
    for k in range(max_removed+1):
        for S in combinations(range(N),k):
            sizes=component_sizes_excluding(g,S)
            if len(sizes)<=1:
                continue
            reached={0}
            for sz in sizes:
                reached|={s+sz for s in tuple(reached)}
            if any(threshold<=s<=(N-k)-threshold for s in reached):
                examples.append({"deleted":S,"components":sizes})
                return {"k_at_most":max_removed,
                        "balanced_fraction":fraction,
                        "found":True,"first":examples[0],
                        "complete_for_this_k":True}
    return {"k_at_most":max_removed,
            "balanced_fraction":fraction,"found":False,
            "complete_for_this_k":True,
            "larger_separators":"NOT_CHECKED"}


def self_test():
    fixtures={}
    for k in (1,2):
        rows=k4_blocks(k)
        f=girth12_gate(rows)
        assert not f["pass"] and f["reason"]=="MOORE_SIZE_BARRIER"
        fixtures["K4x"+str(k)]={"n":len(rows),"girth12":f}
    rows,witness,_=make_connected(4,20261015)
    assert len(rows)==72 and valid_witness(rows,witness)
    affine=gf2_affine(rows,0,0)
    assert affine[2]==21
    g=girth12_gate(rows)
    perm=permute_source(rows,5,2)
    assert girth12_gate(perm)==g
    if g["pass"]:
        w4=local_codewords(rows,4)
        w6=local_codewords(rows,6)
        high,_=anchor_8_10(rows)
        assert not w4 and not w6 and high[8]==high[10]==0
    balanced=small_balanced_separator_profile(rows,max_removed=2)
    fixtures["Connected72"]={
        "n":72,"GF2_nullity":21,
        "SAT_witness_verified":True,"girth12":g,
        "balanced_separator_k_le2":balanced,
        "balanced_separator_k_ge3":"NOT_MEASURED",
        "exact_SAT_count":"NOT_MEASURED",
        "proof_of_hardness":"NONE"}
    return {
        "status":"MOORE_GIRTH12_BARRIER_AND_HONEST_BALANCED_SEPARATOR_GATE",
        "Moore_min_incidence_vertices":126,"Moore_min_SCL_n":63,
        "all_n_girth12_implication":"A4=A6=A8=A10=A12=0",
        "controls":fixtures,"uniform_solver":"NOT_CONSTRUCTED",
        "P_vs_NP":"OPEN"
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    q=p.parse_args()
    if not q.self_test:p.error("--self-test")
    print(json.dumps(self_test(),sort_keys=True,indent=2))
