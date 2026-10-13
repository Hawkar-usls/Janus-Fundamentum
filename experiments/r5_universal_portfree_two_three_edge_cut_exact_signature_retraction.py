#!/usr/bin/env python3
"""All-size certified boundary-free 2/3-edge-cut replacement in cubic 6poles.

For a colourable port-free block with exactly k=2 or k=3 ordinary cut
edges, the block's complete cut-colour relation is respectively
{AA : A in 012} (same colour) or permutations(012) (three distinct).
Proof: cubic colour-parity + global S3 colour symmetry.
Thus replace k=2 block by an edge, or k=3 by a trivalent vertex,
preserving the EXACT ordered six-physical-port colour signature set
provided quotient remains a SIMPLE connected cubic 6pole. Distinct
source-colouring multiplicities need NOT be preserved.

Explicitly this makes every hypothetical minimal open equality-pair
ExactOne n=18 gadget irreducible under all such port-free 2/3 cuts
whose quotient is simple, because every quotient would have n<=16,
ruled out by authoritative n<=16 finite GitHub CI #38408523974.

The small assertions below check COMPLETE physical colour states:
- C6 original 6pole;
- C6 with one K4-minus-edge diamond 2pole, n10;
- chain of two diamond 2poles, n14, collapse WHOLE 8-vertex block;
- C6+diamond, inflate a port-free trivalent internal vertex into
  triangle (3pole), n12, collapse 3-vertex port-free block;
- twice inflating within same vertex, collapse the combined 5-vertex
  port-free 3pole at n14.

All DFS enumerations independently rebuild actual edge-colour
assignments and semiedge colours. No nauty, scipy, numerical solver.
Does NOT prove any polynomial-size PC-back-simulation on arbitrary
blocks, whose arbitrary interior might require unbounded local degree.
"""
from collections import Counter
from itertools import permutations, product


COLORS=(0,1,2)


def norm(a,b):
    assert a!=b
    return tuple(sorted((a,b)))


def assert_simple_cubic_multipole(edges,ports):
    edges=tuple(edges)
    assert len(set(edges))==len(edges)
    vertices=set(v for e in edges for v in e)|set(ports)
    deg=Counter(v for e in edges for v in e)
    sem=Counter(ports)
    assert all(deg[v]+sem[v]==3 for v in vertices),(
        "not trivalent",[(v,deg[v],sem[v]) for v in vertices])
    assert all(deg[v]>=1 for v in vertices)
    return vertices


def colour_states(edges,port_roots):
    """Full ordered physical semiedge-colour relation; no anchoring."""
    vertices=assert_simple_cubic_multipole(edges,port_roots)
    edge_list=tuple(sorted(edges))
    inc={v:[] for v in vertices}
    for i,(a,b) in enumerate(edge_list):
        inc[a].append(i);inc[b].append(i)
    C=[-1]*len(edge_list)
    state_set=set()
    full_count=0
    port_order={v:[] for v in vertices}
    for j,v in enumerate(port_roots):
        port_order[v].append(j)
    def rec(i):
        nonlocal full_count
        if i==len(edge_list):
            full_count+=1
            local={}
            for v in vertices:
                miss=tuple(c for c in COLORS
                           if all(C[e]!=c for e in inc[v]))
                if port_order[v]:
                    assert len(miss)==len(port_order[v])
                    local[v]=tuple(permutations(miss))
            for choices in product(*(local[v] for v in sorted(local))):
                vals=[None]*len(port_roots)
                for v,ch in zip(sorted(local),choices):
                    for j,color in zip(port_order[v],ch):
                        vals[j]=color
                assert None not in vals
                state_set.add(tuple(vals))
            return
        a,b=edge_list[i]
        for color in COLORS:
            if any(C[j]==color for v in (a,b) for j in inc[v] if j<i):
                continue
            C[i]=color
            rec(i+1)
            C[i]=-1
    rec(0)
    return frozenset(state_set),full_count


def graph_cycle6():
    return frozenset(norm(v,(v+1)%6) for v in range(6)),tuple(range(6))


def inflate_edge_diamond(E,link,first_new):
    """Replace old edge (u,v) by K4\{ab} with 2 dangling interfaces."""
    E=set(E)
    u,v=norm(*link)
    assert (u,v) in E
    assert all(first_new+j not in {x for e in E for x in e}
               for j in range(4))
    a,b,c,d=(first_new+j for j in range(4))
    E.remove((u,v))
    E.update({norm(u,a),norm(v,b),norm(a,c),norm(a,d),
              norm(b,c),norm(b,d),norm(c,d)})
    return frozenset(E),frozenset((a,b,c,d))


def inflate_trivalent_vertex_triangle(E,vertex,first_new):
    E=set(E)
    ns=sorted(v if u==vertex else u for u,v in E if vertex in (u,v))
    assert len(ns)==3 and len(set(ns))==3
    assert all(first_new+j not in {x for e in E for x in e}
               for j in range(3))
    for v in ns:E.remove(norm(v,vertex))
    a,b,c=(first_new+j for j in range(3))
    E.update({norm(a,b),norm(a,c),norm(b,c),
              norm(a,ns[0]),norm(b,ns[1]),norm(c,ns[2])})
    return frozenset(E),frozenset((a,b,c))


def component_cut(E,B):
    B=set(B)
    cut=tuple(sorted((u,v) for u,v in E if (u in B)!=(v in B)))
    inside=tuple(sorted((u,v) for u,v in E if u in B and v in B))
    outside=tuple(sorted((u,v) for u,v in E if u not in B and v not in B))
    outside_ends=[]
    inside_ends=[]
    for u,v in cut:
        if u in B:
            inside_ends.append(u);outside_ends.append(v)
        else:
            inside_ends.append(v);outside_ends.append(u)
    return cut,inside,outside,tuple(inside_ends),tuple(outside_ends)


def connected(vertices,E):
    vertices=set(vertices)
    q=[next(iter(vertices))]
    seen=set(q)
    adj={v:[] for v in vertices}
    for a,b in E:
        adj[a].append(b);adj[b].append(a)
    while q:
        for x in adj[q.pop()]:
            if x not in seen:seen.add(x);q.append(x)
    return seen==vertices


def replace_colourable_block(E,ports,B):
    vertices=assert_simple_cubic_multipole(E,ports)
    B=set(B)
    assert B and B<=vertices and not (B & set(ports))
    cut,inside,outside,inside_ends,outside_ends=component_cut(E,B)
    k=len(cut)
    assert k in (2,3) and connected(B,inside)
    block_states,block_count=colour_states(inside,inside_ends)
    assert block_states, "NONCOLOURABLE component: reduction is NOT legal"
    target=(frozenset((c,c) for c in COLORS) if k==2
            else frozenset(permutations(COLORS)))
    assert block_states==target,("block parity theorem violated",block_states)
    if k==2:
        a,b=outside_ends
        if a==b or norm(a,b) in outside:
            return None
        quotient=frozenset(outside+(norm(a,b),))
    else:
        assert len(set(outside_ends))==3
        marker=max(vertices)+1
        quotient=frozenset(outside+tuple(
            norm(marker,v) for v in outside_ends))
    quotient_vertices=assert_simple_cubic_multipole(quotient,ports)
    assert connected(quotient_vertices,quotient)
    assert len(quotient_vertices)<len(vertices)
    return quotient,block_states,block_count


def test_case(label,E,ports,B):
    assert B.isdisjoint(ports)
    n0=len(assert_simple_cubic_multipole(E,ports))
    original,original_count=colour_states(E,ports)
    assert original
    ans=replace_colourable_block(E,ports,B)
    assert ans is not None,("quotient not simple",label)
    reduced,block_states,block_count=ans
    reduced_states,reduced_count=colour_states(reduced,ports)
    assert original==reduced_states,(
        "INVALID all-six-physical-colours retreaction",label,
        len(original),len(reduced_states),list(original^reduced_states)[:3])
    print("CUT_RETRACTION",label,{"n_before":n0,
          "n_after":len(assert_simple_cubic_multipole(reduced,ports)),
          "k_cut":len(component_cut(E,B)[0]),
          "block_vertices":len(B),
          "block_colours":block_count,
          "physical_boundary_states":len(original),
          "source_inner_colours":original_count,
          "quotient_inner_colours":reduced_count},flush=True)
    return len(original)


def main():
    C6,ports=graph_cycle6()
    base,first=inflate_edge_diamond(C6,(0,1),6)
    test_case("DIAMOND_TWOPOLE",base,ports,first)
    e2,second=inflate_edge_diamond(base,(8,9),10)
    test_case("DOUBLE_DIAMOND_8_VERTEX_TWOPOLE",e2,ports,first|second)
    e3,tri1=inflate_trivalent_vertex_triangle(base,6,10)
    test_case("TRIANGLE_THREEPOLE",e3,ports,tri1)
    e4,tri2=inflate_trivalent_vertex_triangle(e3,10,13)
    combined=(tri1-{10})|tri2
    test_case("NESTED_TRIANGLE_5_VERTEX_THREEPOLE",e4,ports,combined)
    print("THEOREM: colourable port-free 2pole/3pole has EXACT SAME")
    print("  physical k-port signature as an edge/vertex respectively.")
    print("  All six original semiedge colours preserved under legal SIMPLE quotients.")
    print("FILTER_FOR_MINIMAL_EXACTONE_N18=NO_PORTFREE_K2_OR_K3_SIMPLE_REDUCTION")
    print("LIMIT: Colourability of an arbitrary removed block is a PRECONDITION;")
    print("  this is NOT a general polynomial-time reduction or uniform PC simulation.")
    print("UNBOUNDED_NATIVE_PC_DEGREE=OPEN; SolveLinearCubicXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
