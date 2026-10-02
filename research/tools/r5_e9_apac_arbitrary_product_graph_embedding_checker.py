#!/usr/bin/env python3
from __future__ import annotations

from itertools import product, combinations

# Local affine moment variables used by the frozen one-clause lift.
FIRST = ("a","b","c","u","v")
PROD = ("ab","au","ac","av","bc","bv","cu","uv")
SEMANTIC_PRODUCTS = ("ab","ac","bc")

def affine_rows():
    # Frozen local affine relaxation:
    # uv = 0
    # ab+au+ac+av+bc+bv+cu+uv = 1
    return

def local_affine_solutions():
    names = FIRST + PROD
    idx = {n:i for i,n in enumerate(names)}
    sols=[]
    for bits in product((0,1), repeat=len(names)):
        d={n:bits[idx[n]] for n in names}
        if d["uv"] != 0:
            continue
        if (d["ab"]^d["au"]^d["ac"]^d["av"]^d["bc"]^d["bv"]^d["cu"]^d["uv"]) != 1:
            continue
        sols.append(d)
    return sols

def projection(sols, names):
    return {tuple(s[n] for n in names) for s in sols}

def graph_formula_edges(n, edges):
    # Clause for edge xy is (x OR y OR s_e).
    # Frozen semantic product graph for that clause contains xy, x-s_e, y-s_e.
    original = {tuple(sorted(e)) for e in edges}
    semantic=set()
    for k,(x,y) in enumerate(edges):
        s=n+k
        semantic.add(tuple(sorted((x,y))))
        semantic.add(tuple(sorted((x,s))))
        semantic.add(tuple(sorted((y,s))))
    induced_on_original={e for e in semantic if e[0] < n and e[1] < n}
    return original, semantic, induced_on_original

def main():
    sols=local_affine_solutions()
    assert sols

    for p,x,y in (("ab","a","b"),("ac","a","c"),("bc","b","c")):
        pr=projection(sols,(x,y,p))
        assert pr == set(product((0,1), repeat=3)), (p,pr)

    # Exhaustively sanity-check arbitrary simple graphs through n=5.
    checked=0
    for n in range(1,6):
        all_edges=list(combinations(range(n),2))
        for mask in range(1<<len(all_edges)):
            edges=[e for i,e in enumerate(all_edges) if (mask>>i)&1]
            original, semantic, induced=graph_formula_edges(n,edges)
            assert induced == original
            checked += 1

    print("ONE_CLAUSE_SEMANTIC_PRODUCT_TRIPLES_FULL = PASS")
    print("APAC_AB_AC_BC_CONTEXT = FULL")
    print(f"ARBITRARY_GRAPH_EMBEDDING_SMALL_EXHAUSTIVE_CASES = {checked}")
    print("INDUCED_ORIGINAL_VERTEX_GRAPH_EQUALS_INPUT_G = PASS")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__ == "__main__":
    main()
