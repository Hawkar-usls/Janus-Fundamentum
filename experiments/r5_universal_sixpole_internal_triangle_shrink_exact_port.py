#!/usr/bin/env python3
"""Source-aligned triangle-contraction exact six-port colour-state audit.

General symbolic theorem: a cubic triangle with three outgoing
incidences has a physical proper 3-edge colouring iff those three
outer colours are ALL distinct; then the three internal triangle
edge colours are UNIQUE (each equals the opposite outer colour).
Consequently contraction of any internal triangle to a single cubic
vertex preserving a SIMPLE connected interior graph preserves ALL
proper external six-port physical colour tuples EXACTLY and hence
all 15 paired equality-bit relations. This is all-size structural
reduction, not a new general solver or unbounded PC result.

CI independently checks every contractible triangle of EVERY
nauty-isomorphism representative with n=6,8,10 and six open ports.
This implements port remapping even when some original triangle
vertices carry dangling semiedges.
"""
from itertools import combinations
from collections import Counter
import shutil
import subprocess

from r5_universal_exposed_exactone_nauty_n8_all_graphs import (
    graph6_edges, enumerate_port_signatures,
)


def port_keys(n,E):
    degree=Counter(v for edge in E for v in edge)
    assert all(1<=degree[v]<=3 for v in range(n))
    return tuple((v,j) for v in range(n)
                 for j in range(3-degree[v]))


def shrink_triangle(n,E,triangle):
    tri=set(triangle)
    edges=set(E)
    assert all(tuple(sorted(e)) in edges for e in combinations(triangle,2))
    root=min(tri)
    kept=tuple(v for v in range(n) if v not in tri or v==root)
    assert len(kept)==n-2
    mapping={v:root if v in tri else v for v in range(n)}
    shrunk=[]
    for a,b in E:
        if a in tri and b in tri:
            continue
        pair=tuple(sorted((mapping[a],mapping[b])))
        assert pair[0]!=pair[1]
        shrunk.append(pair)
    if len(set(shrunk))!=len(shrunk):
        return None
    newE=tuple(sorted(shrunk))
    assert len(newE)==len(E)-3
    d=Counter(v for pair in newE for v in pair)
    assert all(1<=d[v]<=3 for v in kept)
    assert sum(3-d[v] for v in kept)==6
    # Port names at triangles are mapped in ascending source vertex order,
    # each triangle vertex has <=1 port since degree>=2.
    original_ports=port_keys(n,E)
    new_slots={p:[] for p in kept}
    for old in original_ports:
        new_slots[mapping[old[0]]].append(old)
    new_port_order=[]
    for new_v in kept:
        new_port_order.extend(new_slots[new_v])
    assert len(new_port_order)==6
    permutation=tuple(original_ports.index(old)
                      for old in new_port_order)
    # Relabel contracted 14-vertex graph contiguously for legacy parser.
    linear={v:i for i,v in enumerate(kept)}
    compact=tuple(sorted(tuple(sorted((linear[a],linear[b])))
                         for a,b in newE))
    return compact,permutation


def check_graph(n,E):
    expected_m=(3*n-6)//2
    assert len(E)==expected_m
    source_ports=port_keys(n,E)
    assert len(source_ports)==6
    original_states=None
    checked=0
    for t in combinations(range(n),3):
        if not all(tuple(sorted(e)) in E for e in combinations(t,2)):
            continue
        result=shrink_triangle(n,E,t)
        if result is None:
            continue
        target_edges,perm=result
        if original_states is None:
            _,original_states,_=enumerate_port_signatures(n,E)
        _,smaller_states,_=enumerate_port_signatures(n-2,target_edges)
        mapped=frozenset(tuple(s[j] for j in perm) for s in original_states)
        assert mapped==smaller_states,(
            "triangle physical signature mismatch",n,E,t,perm,
            len(mapped),len(smaller_states),
            sorted(mapped^smaller_states)[:5])
        checked+=1
    return checked


def audit(n):
    geng=shutil.which("nauty-geng") or shutil.which("geng")
    if not geng:
        raise RuntimeError("nauty-geng absent: finite replay UNKNOWN")
    m=(3*n-6)//2
    p=subprocess.run([geng,"-c","-q","-d1","-D3",str(n),str(m)],
                     capture_output=True,text=True,check=True)
    counts=Counter()
    for line in p.stdout.splitlines():
        if not line or line.startswith(">>"):
            continue
        nn,E=graph6_edges(line)
        assert nn==n
        counts["graphs"]+=1
        k=check_graph(n,E)
        counts["checked_contractible_triangles"]+=k
        if k:
            counts["graphs_with_contractible_triangles"]+=1
    assert counts["graphs"]>0
    assert counts["checked_contractible_triangles"]>0
    print("TRIANGLE_SOURCE_RETRACTION",n,dict(counts),flush=True)
    return counts


def main():
    all_=Counter()
    for n in (6,8,10):
        all_.update(audit(n))
    print("ALL_SOURCE_RETRACTION_CONTROLS",dict(all_),flush=True)
    print("ALL_N THEOREM: whenever triangle contraction remains simple,")
    print(" exact full six-port physical colouring signatures preserved.")
    print("N18 EXACTONE CANDIDATE: NO CONTRACTIBLE INTERNAL TRIANGLE,")
    print("  since contraction would give forbidden n16 exactone.")
    print("SOURCE_F3_PC_MAP: existing triangle inflation literal degree1 lemma.")
    print("NO_P_VS_NP_RESULT; UNIVERSAL_SOLVER_NOT_CONSTRUCTED.")


if __name__=="__main__":
    main()
