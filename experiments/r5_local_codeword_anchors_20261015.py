#!/usr/bin/env python3
"""Gate E3: certifiable LOCAL_CODEWORD_ANCHORS for linear cubic SCL.

For v in ker_GF2(A), its selected columns form a simple cubic
graph G_v: each selected column has exactly three partners in the
distinct rows incident to it, and linearity forbids parallel edges.

Any weight-4 word forms K4 (Pasch); weight-6 word forms a
connected cubic graph on 6 vertices (K3,3 or triangular prism).
Their support is a connected size-4/6 subset of the intersection
graph H of maximum degree SIX. Exact enumerators therefore visit
O(n) candidates for each fixed size 4,6, with constants depending
only on size and degree, and check Av=0 independently.

For a partial x-cube (Z=bits x fixed to zero, O=bits fixed to one),
the kernel word v=1+x MUST include Z and exclude O. Therefore
w_n(C)=1 iff Z=0, w_(n-3)(C)=0, and
w_(n-6)(C)=A4(C), w_(n-9)(C)=A6(C).
All included anchors are precise counts, not just upper bounds.
"""
from itertools import combinations
import json
import argparse

from r5_cooperative_scl_coverage_20261015 import validate_scl, gf2_affine
from r5_connected_coverage_breaker_20261015 import (
    make_connected, mutate_connected
)
import random


def linear_validate_and_incidence(rows):
    """O(n) expected-time sparse validator under bounded word-RAM hashing.

    Three variable IDs per row; pair uniqueness is equivalent to
    source linearity. Unlike older quadratic validator, scan each
    row and every pair once; no all-pairs row comparison.
    """
    n=len(rows)
    if not n:
        raise ValueError("empty SCL")
    seen_pairs=set()
    incid=[[] for _ in range(n)]
    canonical=[]
    for i,row in enumerate(rows):
        if len(row)!=3 or len(set(row))!=3 or not all(
                isinstance(v,int) and 0<=v<n for v in row):
            raise ValueError("invalid size-three SCL clause")
        r=tuple(row)
        canonical.append(r)
        for v in r:
            incid[v].append(i)
        for pair in combinations(sorted(r),2):
            if pair in seen_pairs:
                raise ValueError("nonlinear source: duplicate variable pair")
            seen_pairs.add(pair)
    if any(len(group)!=3 for group in incid):
        raise ValueError("noncubic column degree")
    return tuple(canonical),tuple(tuple(e) for e in incid)


def intersection_graph(rows):
    rows,_=linear_validate_and_incidence(rows)
    n=len(rows)
    adj=[set() for _ in range(n)]
    for row in rows:
        for a,b in combinations(row,2):
            adj[a].add(b)
            adj[b].add(a)
    assert all(len(neighbors)==6 for neighbors in adj)
    return tuple(tuple(sorted(x)) for x in adj)


def kernel_word(rows, chosen, incid=None):
    """Exact local GF2 kernel check in O(3*|chosen|), not O(n).

    Only clauses incident to selected variables can violate parity.
    Return true iff every touched row has exactly two selected
    variables (the source has exactly three per row).
    """
    if incid is None:
        _,incid=linear_validate_and_incidence(rows)
    hits={}
    for v in chosen:
        for r in incid[v]:
            hits[r]=hits.get(r,0)+1
    return all(k==2 for k in hits.values())


def local_codewords(rows,weight):
    if weight not in (4,6):
        raise ValueError("only weight 4 and 6 certified linear enumerators")
    rows,incid=linear_validate_and_incidence(rows)
    adj=intersection_graph(rows)
    n=len(rows)
    candidates=set()
    if weight==4:
        for root in range(n):
            for triple in combinations((v for v in adj[root] if v>root),3):
                candidate=(root,)+triple
                if kernel_word(rows,candidate,incid):
                    candidates.add(candidate)
    else:
        # Each cubic six-vertex G_v is connected. Enumerate rooted
        # connected subsets of H, keeping root as smallest coordinate.
        # All extension candidates are neighbors of the current set.
        for root in range(n):
            current={(root,)}
            for size in range(1,6):
                nxt=set()
                for subset in current:
                    chosen=set(subset)
                    boundary={v for u in chosen for v in adj[u]
                              if v>root and v not in chosen}
                    for v in boundary:
                        nxt.add(tuple(sorted(subset+(v,))))
                current=nxt
            assert all(len(s)==6 for s in current)
            for subset in current:
                if kernel_word(rows,subset,incid):
                    candidates.add(subset)
    return tuple(sorted(candidates))


def anchor_counts(rows,cube=(0,0),weights=(4,6),precomputed=None):
    rows,_=linear_validate_and_incidence(rows)
    zeros,ones=cube
    n=len(rows)
    if (zeros&ones) or ((zeros|ones)>>n):
        raise ValueError("invalid partial cube")
    # x=1+v: fixed x0 means v1; fixed x1 means v0.
    out={n: int(zeros==0),n-3: 0}
    for w in weights:
        wordsets=(precomputed[w] if precomputed is not None
                  else local_codewords(rows,w))
        count=0
        for tup in wordsets:
            mask=sum(1<<v for v in tup)
            if (mask&zeros)==zeros and not(mask&ones):
                count+=1
        out[n-3*w//2]=count
    return out


def incidence_girth_ge_10(rows):
    """O(n) check of absence of incidence cycles of lengths 4,6,8.

    The incidence graph has 2n vertices with degree 3. BFS out to
    depth 4 from each root scans at most O(3*2^4) edges per root.
    Check every cross edge whose origin has depth <4; any cycle of
    length <=8 is exposed in at least one rooted BFS.
    """
    rows,_=linear_validate_and_incidence(rows)
    n=len(rows)
    adj=[set() for _ in range(2*n)]
    for i,row in enumerate(rows):
        for v in row:
            adj[i].add(n+v)
            adj[n+v].add(i)
    for start in range(2*n):
        dist={start:0}
        parent={start:-1}
        queue=[start]
        for u in queue:
            if dist[u]>=4:
                continue
            for v in adj[u]:
                if v not in dist:
                    dist[v]=dist[u]+1
                    parent[v]=u
                    queue.append(v)
                elif parent[u]!=v:
                    # A short cycle exists within the explored ball.
                    return False
    return True


def full_affine_anchor_oracle(rows,cube=(0,0),limit=1<<16):
    """Independent finite oracle; NOT the claimed linear-time method."""
    aff=gf2_affine(rows,*cube)
    if aff is None:
        return {}
    part,basis,d=aff
    if 1<<d>limit:
        raise ValueError("finite oracle would exceed explicit limit")
    n=len(rows)
    counts={n:0,n-3:0,n-6:0,n-9:0}
    for seed in range(1<<d):
        x=part
        for i,b in enumerate(basis):
            if seed>>i&1:
                x^=b
        v=((1<<n)-1)^x
        weight=v.bit_count()
        if weight in (0,2,4,6):
            counts[n-3*weight//2]+=1
    return counts


def bounded_cubic_graph_certificate(rows,word):
    """Structural proof replay: selected 3-regular simple graph."""
    rows,_=linear_validate_and_incidence(rows)
    S=set(word)
    partners={v:set() for v in word}
    for clause in rows:
        subset=S.intersection(clause)
        if len(subset)==2:
            a,b=tuple(subset)
            partners[a].add(b)
            partners[b].add(a)
        elif len(subset)!=0:
            raise AssertionError("not a GF2 kernel word")
    assert all(len(neighbors)==3 for neighbors in partners.values())
    return True


def self_test():
    from r5_component_factor_20261015 import k4_blocks
    from r5_cooperative_scl_coverage_20261015 import fixtures
    base=fixtures()["AffinePlane9_SAT"]
    assert anchor_counts(base)==full_affine_anchor_oracle(base)
    for rows in (k4_blocks(1),k4_blocks(2),
                 fixtures()["HolyerPetersen_UNSAT"]):
        slow=full_affine_anchor_oracle(rows)
        fast=anchor_counts(rows)
        assert fast==slow,(len(rows),fast,slow)
        for weight in (4,6):
            for subset in local_codewords(rows,weight):
                assert bounded_cubic_graph_certificate(rows,subset)
        if incidence_girth_ge_10(rows):
            assert fast[len(rows)-6]==fast[len(rows)-9]==0

    pair=[]
    for seed in (0,13):
        rows,witness,_=make_connected(2,seed)
        rows,_=mutate_connected(rows,witness,
                               random.Random(seed*991+20261015),
                               moves=4+seed%13)
        counts=anchor_counts(rows)
        oracle=full_affine_anchor_oracle(rows)
        assert counts==oracle
        for cube in ((0,0),(1<<0,0),(0,1<<0),
                     (1<<1,1<<0)):
            anchored=anchor_counts(rows,cube)
            brute=full_affine_anchor_oracle(rows,cube)
            assert anchored==brute,(seed,cube,anchored,brute)
        a4=counts[36-6]
        a6=counts[36-9]
        assert 21*a4+15*a6<=188
        pair.append({
            "seed":seed,"n":36,"A4":a4,"A6":a6,
            "girth_ge_10":incidence_girth_ge_10(rows),
            "anchored_q_integer_bound":(188-21*a4-15*a6)//6,
            "all_partial_checks":"PASS"})
    return {
        "status":"EXACT_LOCAL_KERNEL_ANCHORS_AND_PARTIAL_FILTERS",
        "pair":pair,
        "all_n_linear_time_weight4_weight6":"O(n) sparse operations, fixed support size, bounded degree",
        "P_vs_NP":"OPEN"
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    opt=p.parse_args()
    if not opt.self_test:
        p.error("--self-test")
    print(json.dumps(self_test(),indent=2,sort_keys=True))
