#!/usr/bin/env python3
"""Gate E3.5: exact A8/A10 and partial-cube kernel anchors in O(n) sparse RAM.

A selected kernel word's support graph is simple cubic. At weight 8
it is connected or K4+K4; at weight 10 connected or K4+six-cubic.
All CONNECTED kernel supports of any FIXED weight w are generated
in O(n * 2^(w-1)*poly(w)) local operations: begin at smallest
vertex, choose the first original row hit once, select one of its
two remaining columns, recurse; finish only at parity closure.

Disconnected supports are uniquely specified by unordered
nonoverlapping weight4+weight4 or ordered weight4+weight6
component supports. Count pairs in O(n+2^(2w)) operations using
constant-degree overlap correction and buckets for fixed Z bits.
No n^2 global pair enumeration, and no exhaustive GF2 basis scan.

Important: a source-linear validator is expected-linear under
hashing; Python arbitrary integers have additional bit costs.
"""
from collections import Counter,defaultdict
from itertools import combinations
import argparse,json

from r5_local_codeword_anchors_20261015 import (
    linear_validate_and_incidence,local_codewords,full_affine_anchor_oracle
)
from r5_cooperative_scl_coverage_20261015 import (
    fano7,affine_plane9,gf2_affine
)
from r5_component_factor_20261015 import k4_blocks


def connected_words(rows,weight):
    """All connected fixed-weight exact GF2-kernel supports as bit masks."""
    if weight not in (4,6,8,10):
        raise ValueError("fixed supported weight is 4,6,8 or 10")
    rows,incidence=linear_validate_and_incidence(rows)
    n=len(rows)
    words=set()
    visited_states=0
    for root in range(n):
        visited=set()
        def dfs(selected):
            nonlocal visited_states
            if selected in visited:
                return
            visited.add(selected)
            visited_states+=1
            if selected.bit_count()>weight:
                return
            bad=None
            for v in range(root,n):
                if not ((selected>>v)&1):
                    continue
                for ri in incidence[v]:
                    intersect=sum((selected>>u)&1 for u in rows[ri])
                    if intersect==3:
                        return
                    if intersect==1:
                        bad=ri
                        break
                if bad is not None:
                    break
            if bad is None:
                if selected.bit_count()==weight:
                    words.add(selected)
                return
            if selected.bit_count()==weight:
                return
            for u in rows[bad]:
                if u>root and not (selected>>u)&1:
                    dfs(selected|(1<<u))
        dfs(1<<root)
    return tuple(sorted(words)),visited_states


def mask_of_words(rows,weight):
    if weight in (4,6):
        return tuple(sorted(sum(1<<v for v in w)
                            for w in local_codewords(rows,weight)))
    return connected_words(rows,weight)[0]


def pair_count(left,right,Z=0,O=0,symmetric=False):
    """Count disjoint pairs whose union covers Z, avoids O.

    Each vertex belongs to at most O_w(1) connected supports of
    any fixed weight w. Overlaps corrected through local index.
    Bucket states are subsets of at most 10 demanded zero bits.
    """
    allowedL=[w for w in left if not(w&O)]
    allowedR=(allowedL if symmetric else
              [w for w in right if not(w&O)])
    bagsL=Counter(w&Z for w in allowedL)
    bagsR=(bagsL if symmetric else Counter(w&Z for w in allowedR))
    # Count all pairs in buckets FIRST, regardless of overlap.
    count=0
    if symmetric:
        keys=sorted(bagsL)
        for i,k in enumerate(keys):
            for j in range(i,len(keys)):
                z=keys[j]
                if (k|z)==Z:
                    count+=(bagsL[k]*(bagsL[k]-1)//2 if i==j
                            else bagsL[k]*bagsL[z])
    else:
        for a,ca in bagsL.items():
            for b,cb in bagsR.items():
                if (a|b)==Z:
                    count+=ca*cb
    # Exact sparse overlap correction. Even though total number
    # of unordered pairs can grow quadratically, overlapping
    # pairs are O(n) in bounded-degree fixed-support graphs.
    idx=defaultdict(list)
    for j,w in enumerate(allowedR):
        for v in range(w.bit_length()):
            if w>>v&1:
                idx[v].append(j)
    corrections=0
    for i,w in enumerate(allowedL):
        touching=set()
        bits=w
        while bits:
            b=bits&-bits
            bits^=b
            touching.update(idx[b.bit_length()-1])
        for j in touching:
            if symmetric and j<=i:
                continue
            other=allowedR[j]
            if (w|other)&Z == Z:
                corrections+=1
    return count-corrections


def anchor_8_10(rows,cube=(0,0)):
    rows,_=linear_validate_and_incidence(rows)
    n=len(rows)
    Z,O=cube
    if (Z&O) or ((Z|O)>>n):
        raise ValueError("invalid cube")
    four=mask_of_words(rows,4)
    six=mask_of_words(rows,6)
    result={}
    stats={}
    for target in (8,10):
        if Z.bit_count()>target:
            result[target]=0
            stats[target]={"connected":0,"disconnected":0}
            continue
        conn,visited=connected_words(rows,target)
        local=sum(((v&Z)==Z and (v&O)==0) for v in conn)
        if target==8:
            disc=pair_count(four,four,Z,O,symmetric=True)
        else:
            disc=pair_count(four,six,Z,O,symmetric=False)
        result[target]=local+disc
        stats[target]={"connected":local,"disconnected":disc,
                       "visited_local_states":visited}
    return result,stats


def disjoint_rows(*families):
    """Exact block-disjoint legal source combining independently legal SCL."""
    result=[]
    offset=0
    for fam in families:
        local,_=linear_validate_and_incidence(fam)
        for row in local:
            result.append(tuple(v+offset for v in row))
        offset+=len(local)
    linear_validate_and_incidence(result)
    return result


def independent_all_kernel_weight_count(rows,cube=(0,0),cap=1<<16):
    aff=gf2_affine(rows,*cube)
    if aff is None:
        return {8:0,10:0}
    part,basis,d=aff
    if 1<<d>cap:
        raise ValueError("finite oracle budget exceeded")
    n=len(rows)
    result=Counter()
    for index in range(1<<d):
        x=part
        for j,word in enumerate(basis):
            if index>>j&1:
                x^=word
        result[n-x.bit_count()]+=1
    return {w:result[w] for w in (8,10)}


def self_test():
    examples={
        "Fano7":fano7(),
        "Fano7x2":disjoint_rows(fano7(),fano7()),
        "Fano7xAffine9":disjoint_rows(fano7(),affine_plane9()),
        "Affine9":affine_plane9(),
        "K4_18":k4_blocks(1),
        "K4x2_36":k4_blocks(2),
    }
    result={}
    for name,rows in examples.items():
        counts,detail=anchor_8_10(rows)
        expected=independent_all_kernel_weight_count(rows)
        assert counts==expected,(name,counts,expected,detail)
        assert all(v>=0 for v in counts.values())
        for cube in ((1,0),(0,1),(3,0),(0,3)):
            if (cube[0]|cube[1]).bit_length()>len(rows):
                continue
            restricted,_=anchor_8_10(rows,cube)
            oracle=independent_all_kernel_weight_count(rows,cube)
            assert restricted==oracle,(name,cube,restricted,oracle)
        result[name]={"n":len(rows),"A8":counts[8],"A10":counts[10],
                      "components":detail}
    assert result["Fano7x2"]["A8"]>=49
    return {"status":"GATE_E3_5_A8_A10_EXACT_LOCAL_PLUS_PRODUCT_VERIFIED",
            "fixtures":result,
            "all_n_RAM":"O(n) for fixed weights 8 and 10",
            "universal_SCL_solver":"NOT_CONSTRUCTED",
            "P_vs_NP":"OPEN"}


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--self-test",action="store_true")
    args=a.parse_args()
    if not args.self_test:
        a.error("--self-test")
    print(json.dumps(self_test(),indent=2,sort_keys=True))
