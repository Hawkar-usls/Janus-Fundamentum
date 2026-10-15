#!/usr/bin/env python3
"""Exact factorization of square/cubic/linear SCL into independent components.

Components are derived from row-variable incidence, NOT presumed from
source provenance. When each component has affine nullity d_i with
2**d_i <= n**3, exact SAT count + #111 histogram are computed locally,
then multiplied/convolved. Complexity poly(n)*sum_i 2**d_i
(with fixed polynomial cost for bit checking and convolution).
Useful even when global nullity is linear and 2**sum(d_i) is enormous.
"""
from itertools import combinations
from collections import Counter
from math import comb
import argparse, json

from r5_cooperative_scl_coverage_20261015 import (
    validate_scl, gf2_affine, holyer, valid_witness
)


def connected_scl_components(rows):
    rows=validate_scl(rows)
    n=len(rows)
    parents=list(range(n))
    def find(v):
        while parents[v]!=v:
            parents[v]=parents[parents[v]]
            v=parents[v]
        return v
    def union(u,v):
        ru,rv=find(u),find(v)
        if ru!=rv:
            parents[rv]=ru
    for a,b,c in rows:
        union(a,b)
        union(a,c)
    blocks={}
    for v in range(n):
        blocks.setdefault(find(v),[]).append(v)
    result=[]
    for verts in sorted(blocks.values(),key=lambda x:min(x)):
        ren={v:i for i,v in enumerate(verts)}
        local=validate_scl([tuple(ren[v] for v in row)
                            for row in rows if row[0] in ren])
        assert len(local)==len(verts)
        result.append({"variables":verts,"rows":local})
    return result


def factor_exact(rows,exponent=3):
    if not 0<=exponent<=3:
        raise ValueError("exponent is a fixed 0..3")
    components=connected_scl_components(rows)
    n=len(rows)
    hist=Counter({0:1})
    solution_count=1
    total_checks=0
    stats=[]
    witness=0
    for item in components:
        local=item["rows"]
        affine=gf2_affine(local,0,0)
        if affine is None:
            return {"verdict":"UNSAT","solution_count":0,
                    "components":len(components),"reason":"GF2 inconsistent"}
        part,basis,d=affine
        local_count=1<<d
        if local_count>n**exponent:
            return {"verdict":"DECLINE","component_nullity":d,
                    "affine_words":local_count,
                    "polynomial_cap":n**exponent}
        loch=Counter()
        local_solutions=0
        first=None
        for selector in range(local_count):
            x=part
            for j,vector in enumerate(basis):
                if (selector>>j)&1:
                    x^=vector
            t=sum(all((x>>v)&1 for v in row) for row in local)
            assert t%3==0
            loch[t]+=1
            if valid_witness(local,x):
                local_solutions+=1
                if first is None:
                    first=x
        assert local_solutions==loch[0]
        total_checks+=local_count
        solution_count*=local_solutions
        stats.append({"n":len(local),"nullity":d,
                      "affine_words":local_count,
                      "SAT_solutions":local_solutions,
                      "violations_histogram":dict(sorted(loch.items()))})
        if first is not None:
            witness|=sum(1<<item["variables"][i] for i in range(len(local))
                         if (first>>i)&1)
        nxt=Counter()
        for t,a in hist.items():
            for u,b in loch.items():
                nxt[t+u]+=a*b
        hist=nxt
    if solution_count:
        assert valid_witness(rows,witness)
    assert hist[0]==solution_count
    return {"verdict":"SAT" if solution_count else "UNSAT",
            "solution_count":solution_count,
            "components":len(components),"component_info":stats,
            "total_parity_words_checked":total_checks,
            "global_affine_words":sum(hist.values()),
            "histogram":dict(sorted(hist.items())),
            "witness":witness if solution_count else None}


def k4_blocks(blocks=4):
    edges=[(4*b+u,4*b+v) for b in range(blocks)
           for u,v in combinations(range(4),2)]
    return holyer(4*blocks,edges)


def self_test():
    rows=k4_blocks(4)
    result=factor_exact(rows)
    assert result["components"]==4
    assert [item["nullity"] for item in result["component_info"]]==[6]*4
    assert result["total_parity_words_checked"]==256
    assert result["global_affine_words"]==2**24
    assert result["solution_count"]==6**4==1296
    assert result["histogram"][0]==1296
    # A standalone component must independently yield exactly six.
    solo=factor_exact(k4_blocks(1))
    assert solo["solution_count"]==6 and solo["total_parity_words_checked"]==64
    return {"status":"EXACT_COMPONENT_FACTORIZATION",
            "global_n":72,"global_nullity":24,
            "local_dimensions":[6,6,6,6],
            "local_parity_checks":256,
            "SAT_count":1296,
            "all_n_complexity":"poly(n)*sum(2**d_i) under fixed caps",
            "P_vs_NP":"OPEN"}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:
        print(json.dumps(self_test(),indent=2,sort_keys=True))
    else:
        p.error("run --self-test")
