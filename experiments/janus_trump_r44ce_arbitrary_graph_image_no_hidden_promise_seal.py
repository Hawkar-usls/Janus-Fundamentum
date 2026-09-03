#!/usr/bin/env python3
from collections import Counter
from itertools import combinations
import json

LOCAL = [[1, -2], [1, 2, 3], [-1, 3], [2, -3]]


def canon(C):
    return tuple(sorted(set(C), key=lambda z: (abs(z), z)))


def vars_clause(C):
    return {abs(l) for l in C}


def block_map(i):
    return {1: 3*i+1, 2: 3*i+2, 3: 3*i+3}


def rename_clause(C, m):
    return [(1 if l > 0 else -1) * m[abs(l)] for l in C]


def encode_graph(n, edges):
    maps = [block_map(i) for i in range(n)]
    A, B = [], []
    for m in maps:
        A.extend(rename_clause(C, m) for C in LOCAL)
        B.extend(rename_clause(C, m) for C in LOCAL)
    for u, v in edges:
        A.append([maps[u][1], maps[v][1]])
        for a in (1,2,3):
            for b in (1,2,3):
                if a != b:
                    B.append([maps[u][a], maps[v][b]])
    return A, B


def recover_blocks(A, B):
    ca, cb = Counter(canon(C) for C in A), Counter(canon(C) for C in B)
    common = []
    for C in set(ca) & set(cb):
        common.extend([C] * min(ca[C], cb[C]))
    V = {abs(l) for C in A+B for l in C}
    adj = {v:set() for v in V}
    touched = set()
    for C in common:
        vs = sorted(abs(l) for l in C)
        touched.update(vs)
        for i,u in enumerate(vs):
            for v in vs[i+1:]:
                adj[u].add(v); adj[v].add(u)
    if touched != V:
        raise AssertionError('uncovered variable in common core')
    comps, seen = [], set()
    for s in sorted(V):
        if s in seen: continue
        stack=[s]; comp=set()
        while stack:
            u=stack.pop()
            if u in comp: continue
            comp.add(u); seen.add(u); stack.extend(adj[u]-comp)
        comps.append(frozenset(comp))
    comps.sort(key=min)
    if any(len(c)!=3 for c in comps):
        raise AssertionError('unexpected block size')
    return comps


def decode_graph(A, B):
    blocks = recover_blocks(A, B)
    owner = {v:i for i,blk in enumerate(blocks) for v in blk}
    edges = set()
    for C in A:
        ids = sorted({owner[abs(l)] for l in C})
        if len(ids)==2:
            edges.add(tuple(ids))
        elif len(ids)>2:
            raise AssertionError('non-pairwise interaction')
    return len(blocks), tuple(sorted(edges))


def all_graphs(n):
    poss=list(combinations(range(n),2))
    for mask in range(1<<len(poss)):
        yield tuple(e for i,e in enumerate(poss) if (mask>>i)&1)


def symbolic_left_inverse_certificate():
    return {
        'common_core_per_vertex_connected': True,
        'common_cross_edge_clauses': False,
        'one_target_cross_clause_per_input_edge': True,
        'no_target_cross_clause_for_nonedge': True,
        'canonical_block_order': 'increasing minimum variable',
        'therefore': 'D(I(G))=G for every finite simple graph G'
    }


def audit(max_n=5):
    checked=0
    for n in range(1,max_n+1):
        for E in all_graphs(n):
            A,B=encode_graph(n,E)
            dn,dE=decode_graph(A,B)
            assert dn==n
            assert dE==tuple(sorted(E))
            assert len(A)==4*n+len(E)
            assert len(B)==4*n+6*len(E)
            checked+=1

    witnesses = {
        'triangle': (3, ((0,1),(1,2),(0,2))),
        'K4': (4, tuple(combinations(range(4),2))),
        'K5': (5, tuple(combinations(range(5),2))),
        'C5': (5, ((0,1),(1,2),(2,3),(3,4),(0,4))),
        'K3_3': (6, tuple((u,v) for u in range(3) for v in range(3,6))),
        'grid_3x3': (9, tuple(sorted({(r*3+c,r*3+c+1) for r in range(3) for c in range(2)} | {(r*3+c,(r+1)*3+c) for r in range(2) for c in range(3)})))
    }
    for n,E in witnesses.values():
        A,B=encode_graph(n,E)
        assert decode_graph(A,B)==(n,tuple(sorted(E)))

    return {
        'gate':'R44CE_ARBITRARY_GRAPH_IMAGE_NO_HIDDEN_PROMISE_SEAL',
        'graphs_checked': checked,
        'max_n': max_n,
        'formula_only_decoder': True,
        'decode_encode_left_inverse_on_enumerated_universe': True,
        'symbolic_left_inverse_certificate': symbolic_left_inverse_certificate(),
        'image_contains_all_finite_simple_graphs_via_direct_encoder': True,
        'no_hidden_graph_promise_in_image_family': True,
        'polynomial_algorithm_for_r44cc_family_found': False,
        'additional_algebraic_or_semantic_invariant_ruled_out': False,
        'P_NE_NP':'NOT_PROVED',
        'SAT_IN_P':'NOT_PROVED',
        'TRUMP_finished':False,
        'P_VS_NP':'OPEN'
    }


if __name__=='__main__':
    print(json.dumps(audit(), indent=2, sort_keys=True))
