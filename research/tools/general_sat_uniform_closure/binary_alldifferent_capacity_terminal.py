#!/usr/bin/env python3
"""Polynomial AllDifferent capacity terminal for native XNF.

Detects a complete pairwise-distinctness macro over fixed-width Boolean blocks
directly from syntax, without benchmark names.

Accepted structure:
  * every clause has the same width ell>=2;
  * every lineral is a positive XOR of exactly two base variables;
  * the graph of all XOR pairs has exactly ell connected components;
  * every component is a clique K_p of the same size p;
  * every clause contains exactly one edge from every component;
  * there are exactly C(p,2) clauses;
  * the edge correspondence induced by clause IDs preserves incidence between
    every component and a chosen reference component.

The incidence-preserving edge correspondence reconstructs a vertex bijection
from each bit-layer K_p to the reference K_p.  Hence each reference vertex is
one object and the ell components are its ell Boolean address bits.

Every clause then says one object pair differs in at least one address bit.
Since all C(p,2) pairs occur, all p bit-vectors must be distinct.

If p > 2^ell, UNSAT follows by finite-domain capacity.  The certificate is:
  (ell,p, layer cliques, reconstructed bijections, all-pair coverage,
   p > 2^ell).

This closes standard bit-PHP_{2^ell+1}^{2^ell} without branching.

It is a scoped terminal. Failure to match the syntax or p<=2^ell returns OPEN.
"""

from collections import defaultdict, deque
from itertools import combinations

from bit_php_open_firewall import bphp_xnf, expected_sizes
from php_scalable_open_firewall import xnf_to_2xnf
from uniform_gaussian_implication_audit import uniform_gaussian_implication_closure
from choice_resource_hall_terminal import hall_terminal


def endpoints(mask):
    bits=[i for i in range(mask.bit_length()) if (mask>>i)&1]
    assert len(bits)==2
    return tuple(bits)


def variable_graph(source):
    adj=defaultdict(set)
    clause_edges=[]
    for C in source:
        edges=[]
        for mask,const in C:
            if const!=0 or mask.bit_count()!=2:
                return None
            u,v=endpoints(mask)
            adj[u].add(v)
            adj[v].add(u)
            edges.append((u,v) if u<v else (v,u))
        clause_edges.append(tuple(edges))
    return adj,tuple(clause_edges)


def components(adj):
    unseen=set(adj)
    out=[]
    while unseen:
        s=min(unseen)
        unseen.remove(s)
        C={s}
        q=deque([s])
        while q:
            u=q.popleft()
            for v in adj[u]:
                if v in unseen:
                    unseen.remove(v)
                    C.add(v)
                    q.append(v)
        out.append(frozenset(C))
    return tuple(sorted(out,key=lambda C:min(C)))


def is_clique(C,adj):
    return all((v in adj[u]) for u in C for v in C if u!=v)


def edge_component_index(edge,owner):
    u,v=edge
    if owner.get(u)!=owner.get(v):
        return None
    return owner[u]


def common_endpoint(edges):
    if not edges:
        return None
    S=set(edges[0])
    for e in edges[1:]:
        S &= set(e)
    if len(S)!=1:
        return None
    return next(iter(S))


def reconstruct_layer_map(ref_vertices, ref_edge_by_clause, target_edge_by_clause):
    """Recover target vertex for every reference vertex from mapped stars."""
    mapping={}
    for r in ref_vertices:
        ids=[cid for cid,e in ref_edge_by_clause.items() if r in e]
        image_edges=[target_edge_by_clause[cid] for cid in ids]
        t=common_endpoint(image_edges)
        if t is None:
            return None
        mapping[r]=t

    if len(set(mapping.values()))!=len(mapping):
        return None

    for cid,re in ref_edge_by_clause.items():
        te=set(target_edge_by_clause[cid])
        mapped={mapping[re[0]],mapping[re[1]]}
        if te!=mapped:
            return None

    return mapping


def detect_complete_alldifferent(source):
    if not source:
        return {"status":"OPEN","reason":"empty"}

    widths={len(C) for C in source}
    if len(widths)!=1:
        return {"status":"OPEN","reason":"mixed_clause_width"}
    ell=next(iter(widths))
    if ell<2:
        return {"status":"OPEN","reason":"width_lt_2"}

    vg=variable_graph(source)
    if vg is None:
        return {"status":"OPEN","reason":"non_pair_xor_lineral"}
    adj,clause_edges=vg

    comps=components(adj)
    if len(comps)!=ell:
        return {"status":"OPEN","reason":"component_count_not_width"}

    sizes={len(C) for C in comps}
    if len(sizes)!=1:
        return {"status":"OPEN","reason":"layer_sizes_differ"}
    p=next(iter(sizes))

    if any(not is_clique(C,adj) for C in comps):
        return {"status":"OPEN","reason":"layer_not_clique"}

    if len(source)!=p*(p-1)//2:
        return {"status":"OPEN","reason":"not_all_pair_clause_count"}

    owner={}
    for i,C in enumerate(comps):
        for v in C:
            owner[v]=i

    by_layer=[{} for _ in comps]
    for cid,edges in enumerate(clause_edges):
        seen=set()
        for e in edges:
            i=edge_component_index(e,owner)
            if i is None or i in seen:
                return {"status":"OPEN","reason":"clause_not_one_edge_per_layer"}
            seen.add(i)
            by_layer[i][cid]=e
        if seen!=set(range(ell)):
            return {"status":"OPEN","reason":"clause_missing_layer"}

    # Each layer edge appears exactly once because clause count equals C(p,2).
    for i,C in enumerate(comps):
        vals=list(by_layer[i].values())
        if len(set(vals))!=len(vals):
            return {"status":"OPEN","reason":"layer_edge_repeated"}
        if set(vals)!={tuple(sorted(e)) for e in combinations(sorted(C),2)}:
            return {"status":"OPEN","reason":"layer_edge_coverage_incomplete"}

    # Reconstruct object alignment from edge correspondences.
    ref_vertices=tuple(sorted(comps[0]))
    maps=[{r:r for r in ref_vertices}]
    for i in range(1,ell):
        m=reconstruct_layer_map(ref_vertices,by_layer[0],by_layer[i])
        if m is None:
            return {"status":"OPEN","reason":"edge_correspondence_not_vertex_induced"}
        maps.append(m)

    if p>1<<ell:
        return {
            "status":"UNSAT",
            "reason":"ALLDIFFERENT_DOMAIN_CAPACITY",
            "objects":p,
            "bit_width":ell,
            "domain_size":1<<ell,
            "clause_count":len(source),
            "layer_count":len(comps),
            "layer_size":p,
            "bijections":tuple(
                tuple((r,m[r]) for r in ref_vertices)
                for m in maps
            ),
        }

    return {
        "status":"OPEN",
        "reason":"ALLDIFFERENT_CAPACITY_NOT_VIOLATED",
        "objects":p,
        "bit_width":ell,
        "domain_size":1<<ell,
    }


def verify_certificate(source,receipt):
    assert receipt["status"]=="UNSAT"
    again=detect_complete_alldifferent(source)
    assert again["status"]=="UNSAT"
    assert again["objects"]==receipt["objects"]
    assert again["bit_width"]==receipt["bit_width"]
    assert receipt["objects"]>receipt["domain_size"]
    assert receipt["domain_size"]==(1<<receipt["bit_width"])
    return True


def main():
    receipts=[]
    for ell in range(2,6):
        source,n0,_,p,h=bphp_xnf(ell)
        rec=detect_complete_alldifferent(source)
        assert rec["status"]=="UNSAT"
        assert rec["objects"]==p
        assert rec["bit_width"]==ell
        assert rec["domain_size"]==h
        assert verify_certificate(source,rec)

        # Baseline layers still leave the normalized 2-XNF OPEN.
        formula,n=xnf_to_2xnf(source,n0)
        st,eqs,_=uniform_gaussian_implication_closure(formula,n)
        assert st=="OPEN" and eqs==tuple()
        assert hall_terminal(source)["status"]=="OPEN"

        receipts.append({
            "ell":ell,
            "objects":p,
            "domain":h,
            "clauses":len(source),
            "alldifferent_terminal":"UNSAT",
        })

    print("BINARY-DOMAIN ALLDIFFERENT CAPACITY TERMINAL: PASS")
    for r in receipts:
        print(r)
    print("detection uses syntax only: XOR-pair clique layers + incidence-preserving edge correspondence")
    print("proof: all object address vectors distinct but objects > 2^ell")
    print("no Boolean branching or Res(oplus) saturation")
    print("terminal is SCOPED; unmatched formulas remain OPEN")
    print("GENERAL_SAT_IN_P = NOT_PROVED")
    print("P_VS_NP = OPEN")


if __name__=="__main__":
    main()
