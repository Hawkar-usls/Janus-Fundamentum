#!/usr/bin/env python3
"""Uniform degree-ONE original native SCL row-map for colourable k2/k3 cuts.

General theorem: if a colourable port-free k=2 or k=3 pole can be
contracted to one edge / one vertex with a SIMPLE connected cubic
quotient, there is an explicit one-source-variable-to-one-source-
variable GF3 (indeed, every field) map sending EVERY edge-3-colour
onehot original Exact-One row and EVERY vertex-colour Exact-One row
of the EXPANDED original simple cubic graph literally to one SOURCE
Exact-One row of the SMALLER graph. Each Boolean x²-x generator
also maps to one original Boolean generator. The same map is
degree-nonincreasing in PC; all degree-d refutation lower bounds of
the SMALLER source transfer to the EXPANDED source.

k=2: Fix a valid internal 3-edge colouring of the block with two
equal boundary colours q. Each internal edge h has fixed colour a_h,
and target indicator x_(h,c) maps to x_(replacement edge,c-a_h+q).
The cut edges have a_h=q so map identically. At any internal block
vertex its 3 incident a_h are a permutation of 012, so all
vertex-colour Exact-One rows map to the replacement edge onehot.

k=3: Fix a valid internal 3-edge colouring of the block with all
three boundary colours distinct, say a_i on cut index i.
For any internal edge h of reference colour a_i, map x_(h,c)
to x_(replacement outer edge i,c). At every old block
vertex the reference colours are 012, so its vertex-colour
Exact-One row maps to the NEW quotient vertex-colour onehot
over all three replacement edges. Cut edge variables map to their
corresponding replacement edge unchanged.

The map is literal (NO arbitrary degree multipliers, NO unknown
substitution truth table, NO source row linear combinations).
This is a LOCAL HOMOMORPHISM valid even for arbitrarily LARGE k2/3
port-free blocks with one reference colouring.

Four explicit original CLOSED simple cubic source tests glue every
open sixpole to a fresh disjoint ring sixpole via 6 physical edges,
then check EVERY source row, Boolean mapping, and all ORIGINAL
square+cubic+linear promises. Test geometries:
- single 4-vertex diamond 2pole;
- composed 8-vertex double diamond 2pole;
- 3-vertex triangle 3pole;
- nested 5-vertex port-free 3pole.

WARNING: This retraction cannot by itself establish unbounded
native PC refutation degree. Repeated expansion just preserves
existing lower bounds. Colourability of a removed arbitrary block
is an explicit precondition, not proved efficiently decidable.
"""
from collections import Counter,defaultdict
from itertools import permutations
from r5_universal_portfree_two_three_edge_cut_exact_signature_retraction import (
    norm,graph_cycle6,inflate_edge_diamond,
    inflate_trivalent_vertex_triangle,component_cut,
    replace_colourable_block,assert_simple_cubic_multipole,
    colour_states,
)


def find_reference_colouring(edges,cut_inside_roots):
    """One actual proper local edge-colouring and ordered cut-port state."""
    E=tuple(sorted(edges))
    vertices={v for e in E for v in e}|set(cut_inside_roots)
    inc={v:[] for v in vertices}
    for j,(a,b) in enumerate(E):
        inc[a].append(j);inc[b].append(j)
    # Each local vertex has exactly 3 incident local edges+cut ports.
    deficit=Counter(cut_inside_roots)
    assert all(len(inc[v])+deficit[v]==3 for v in vertices)
    c=[-1]*len(E)
    chosen=[None]
    def rec(i):
        if chosen[0] is not None:return
        if i==len(E):
            cut=[]
            available={v:list(x for x in range(3)
                         if all(c[j]!=x for j in inc[v])) for v in vertices}
            for v in cut_inside_roots:
                assert available[v]
                cut.append(available[v].pop(0))
            chosen[0]=(dict(zip(E,c)),tuple(cut))
            return
        a,b=E[i]
        for v in range(3):
            if any(c[j]==v for t in (a,b) for j in inc[t] if j<i):
                continue
            c[i]=v;rec(i+1);c[i]=-1
            if chosen[0] is not None:return
    rec(0)
    assert chosen[0] is not None,"uncolourable block"
    ecolor,portcolors=chosen[0]
    assert len(set(portcolors))==(1 if len(portcolors)==2 else 3)
    # Check all local original vertex-colour rows really form 012:
    for v in vertices:
        colours=[ecolor[e] for e in E if v in e]+[
          portcolors[j] for j,r in enumerate(cut_inside_roots) if r==v]
        assert sorted(colours)==[0,1,2],(v,colours)
    return ecolor,portcolors


def close_sixpole(E,ports,fixture_root):
    """Glue to cycle sixpole; all six original port roots are retained."""
    assert len(ports)==6
    assert len(set(ports))==6,"simple fixture needs distinct roots"
    assert all(fixture_root+j not in
               {v for e in E for v in e}|set(ports) for j in range(6))
    Q=set(E)
    for i in range(6):
        Q.add(norm(fixture_root+i,fixture_root+(i+1)%6))
        Q.add(norm(ports[i],fixture_root+i))
    return frozenset(Q)


def native_original_source(E):
    E=tuple(sorted(E))
    assert len(set(E))==len(E)
    V={v for e in E for v in e}
    incident={v:[] for v in V}
    for e in E:
        a,b=e
        incident[a].append(e);incident[b].append(e)
    assert all(len(incident[v])==3 for v in V)
    assert len(E)*2==len(V)*3
    edge_rows=[tuple((e,c) for c in range(3)) for e in E]
    vertex_rows=[tuple((e,c) for e in sorted(incident[v]))
                 for v in sorted(V) for c in range(3)]
    rows=edge_rows+vertex_rows
    assert all(len(r)==3 and len(set(r))==3 for r in rows)
    S=[frozenset(r) for r in rows]
    assert len(rows)==3*len(E)
    variables=set().union(*S)
    assert len(variables)==len(rows)
    assert all(sum(x in row for row in S)==3 for x in variables)
    assert all(len(a&b)<=1 for i,a in enumerate(S) for b in S[i+1:])
    return E,V,rows


def derive_literal_source_map(expanded,quotient,ports,B,fixture_root):
    vertices=assert_simple_cubic_multipole(expanded,ports)
    cut,inside,outside,inside_ends,outside_ends=component_cut(expanded,B)
    assert len(cut) in (2,3)
    reference,portcolors=find_reference_colouring(inside,inside_ends)
    k=len(cut)
    if k==2:
        assert portcolors[0]==portcolors[1]
        e=norm(*outside_ends)
        assert e in quotient
        boundary_ref=portcolors[0]
    else:
        newv=next(iter(({x for edge in quotient for x in edge}-
                         ({x for edge in expanded for x in edge}-set(B)))))
        new_edges=tuple(norm(newv,u) for u in outside_ends)
        assert all(x in quotient for x in new_edges)
        assert len(set(new_edges))==3
        boundary_to_index={c:i for i,c in enumerate(portcolors)}
        assert len(boundary_to_index)==3

    # Map edge e to quotient edge q(e) plus colour-index shift:
    # x'_(e,c) -> x_(q(e),(c+shift)%3).
    edge_map={}
    for h in outside:
        assert h in quotient
        edge_map[h]=(h,0)
    for i,h in enumerate(cut):
        edge_map[h]=((e if k==2 else new_edges[i]),0)
    for h in inside:
        if k==2:
            shift=(boundary_ref-reference[h])%3
            edge_map[h]=(e,shift)
        else:
            j=boundary_to_index[reference[h]]
            edge_map[h]=(new_edges[j],0)
    assert len(edge_map)==len(expanded)
    # Fixture edges & six physical connecting edges are retained.
    full_expanded=close_sixpole(expanded,ports,fixture_root)
    full_quotient=close_sixpole(quotient,ports,fixture_root)
    for h in full_expanded:
        if h not in edge_map:
            assert h in full_quotient
            edge_map[h]=(h,0)

    xe,_,expanded_rows=native_original_source(full_expanded)
    qe,_,small_rows=native_original_source(full_quotient)
    small_set={tuple(sorted(row)) for row in small_rows}
    image=Counter()
    for i,row in enumerate(expanded_rows):
        mapped=tuple(sorted((edge_map[h][0],
                             (c+edge_map[h][1])%3) for h,c in row))
        assert len(set(mapped))==3,("degenerate source row",i,row,mapped)
        assert mapped in small_set,("not literal source generator",i,row,mapped)
        image["rows"]+=1
        if i<len(xe):image["edge_onehot"]+=1
        else:image["vertex_onehot"]+=1
    assert all(h in edge_map for h in full_expanded)
    assert all(h2 in full_quotient for h2,_ in edge_map.values())
    # Boolean X'^2-X' maps to X^2-X on ONE source variable,
    # for every original indicator of every target edge and colour.
    assert len(xe)*3==len(edge_map)*3
    image["boolean_generators"]=3*len(xe)
    image["expanded_SCL"]=len(expanded_rows)
    image["reduced_SCL"]=len(small_rows)
    image["block_cut"]=k
    image["block_vertices"]=len(B)
    return image


def test_case(label,E,ports,B):
    result=replace_colourable_block(E,ports,B)
    assert result is not None,("quotient not SIMPLE",label)
    quotient,_,_=result
    original_states,_=colour_states(E,ports)
    reduced_states,_=colour_states(quotient,ports)
    assert original_states==reduced_states
    image=derive_literal_source_map(E,quotient,ports,B,fixture_root=1000)
    assert image["rows"]==image["expanded_SCL"]
    print("GF3_PC_DEGREE1_LITERAL_ROWS",label,dict(image),flush=True)


def main():
    C6,ports=graph_cycle6()
    base,first=inflate_edge_diamond(C6,(0,1),6)
    test_case("DIAMOND_4_VERTEX_TWOPOLE",base,ports,first)
    e2,second=inflate_edge_diamond(base,(8,9),10)
    test_case("DOUBLE_DIAMOND_8_VERTEX_TWOPOLE",e2,ports,first|second)
    e3,tri1=inflate_trivalent_vertex_triangle(base,6,10)
    test_case("TRIANGLE_3_VERTEX_THREEPOLE",e3,ports,tri1)
    e4,tri2=inflate_trivalent_vertex_triangle(e3,10,13)
    test_case("NESTED_TRIANGLE_5_VERTEX_THREEPOLE",e4,ports,(tri1-{10})|tri2)
    print("ALL_NATIVE_SCL_ROWS_AND_BOOLEAN_AXIOMS_LITERAL_PC_DEGREE1_PASS")
    print("UNIVERSAL_MATH: any FIXED actual block colouring yields a")
    print("  uniformly degree1 source-variable substitution for k=2 or3,")
    print("  independent of removed block size or field characteristic.")
    print("NO_NEW_UNBOUNDED_PC_DEGREE_LOWER_BOUND")
    print("SolveLinearCubicXSAT=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__=="__main__":
    main()
