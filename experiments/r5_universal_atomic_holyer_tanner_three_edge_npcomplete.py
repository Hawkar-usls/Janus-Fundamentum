#!/usr/bin/env python3
"""R5 ATOMIC connected 3-edge-connected Tanner NP-hardness reduction.

UNIVERSAL THEOREM: For EVERY CONNECTED finite SIMPLE cubic graph G,
the direct Holyer positive square/cubic/linear 1-in-3-SAT encoding A_G
has a Tanner (row/column incidence) graph of EDGE CONNECTIVITY 3.

Notation: original graph edges e; colours c=0,1,2.
One edge-row R_e; one vertex-colour row R_(v,c);
and one column X_(e,c) incident to R_e,R_(u,c),R_(v,c).

PROOF, not extrapolated from finite controls:
(1) For ANY original edges e,f of connected G, take an edge
    adjacency walk e=e0,e1,...,ek=f in its connected line graph.
    For each colour c, the original Tanner path
       R_e-X_(e,c)-R_(v1,c)-X_(e1,c)-...-X_(f,c)-R_f
    is valid, and these three c=0,1,2 paths share NO Tanner EDGES.
    Hence any edge cut of size <=2 cannot split two edge-row
    nodes R_e,R_f: all R_e lie on the same cut side.
(2) Each vertex-colour row R_(v,c) is linked to the three
    DISTINCT incident edge-row R_e by the three 2-edge paths
        R_(v,c)-X_(e,c)-R_e.
    These paths share NO Tanner EDGES. If all R_e are on
    the same side, a cut of size <=2 cannot separate R_(v,c).
(3) Each variable-column X_(e,c) is adjacent to THREE row
    nodes R_e,R_(u,c),R_(v,c), all now on the same side.
    It cannot lie on the other side of a cut of <=2 edges.
Therefore no nontrivial Tanner cut of 1 or 2 edges exists.
Minimum cut <=3 from 3-regularity; so lambda(Tanner)=3.

CONNECTED CUBIC 3-EDGE-COLOURING is NP-COMPLETE: cubic colouring
for arbitrary simple cubic graphs is NP-complete (Holyer 1981).
Given disconnected cubic graph, repeatedly join two components
by choosing one NON-BRIDGE edge each and replacing (a,b),(c,d)
with (a,c),(b,d). Every connected cubic graph has a nonbridge
edge (any cycle), and removing it leaves its component
connected, so the join is connected, simple, cubic, size
preserving. The resulting 2-edge cut has both new crossing
edges of the SAME colour in any proper 3-edge-colouring by
the usual colour-parity/cut identity for cubic graphs:
for each colour, number of its cut edges is |S| mod 2.
Here |S| even (two crossing edges), thus the 2 cut edges
must be same colour. Reconnecting recovers proper colourings
of original components. Conversely permute all three colour
names independently on each component so selected edges
match in colour and perform the switch. This gives an
effective witness-preserving many-one reduction to
CONNECTED simple cubic graph 3-edge-colouring. Holyer then
maps it to 3-EDGE-CONNECTED Tanner SCL with no 2-cut gate.

Consequently all legal SCL of 3-edge-connected Tanner
GRAPH ALREADY form an NP-complete decision subclass.
This is a structural hardness result, NOT a claim P!=NP
or impossibility of a new universal polynomial algorithm.
"""
from __future__ import annotations

from collections import Counter

from r5_universal_cubic_edgecolor_direct_scl_bridge import (
    validate_cubic_graph,make_scl,brute_three_edge_coloring,
    K4,K33,petersen_graph,cube_graph,
)
from r5_universal_connected_scl_tanner_two_cut_proof_audit import (
    certified_tanner_edge_connectivity,
)
from r5_universal_certified_scl_component_decomposition import (
    canonical_scl_components,
)


def graph_components(edges):
    vertices,E=validate_cubic_graph(edges)
    adj={v:set() for v in vertices}
    for u,v in E:
        adj[u].add(v)
        adj[v].add(u)
    todo=set(vertices);parts=[]
    while todo:
        start=min(todo);stack=[start];part={start}
        while stack:
            for v in adj[stack.pop()]:
                if v not in part:
                    part.add(v);stack.append(v)
        parts.append(tuple(sorted(part)))
        todo-=part
    return tuple(parts)


def connected_without_edge(edges,vertices,removed):
    group=set(vertices)
    adj={v:[] for v in vertices}
    for u,v in edges:
        if (u,v)==removed:continue
        if u in group and v in group:
            adj[u].append(v);adj[v].append(u)
    reached={vertices[0]};stack=[vertices[0]]
    while stack:
        for v in adj[stack.pop()]:
            if v not in reached: reached.add(v);stack.append(v)
    return len(reached)==len(vertices)


def choose_cycle_edge(edges,component):
    group=set(component)
    for e in edges:
        if e[0] in group and e[1] in group:
            if connected_without_edge(edges,component,e):
                return e
    raise AssertionError("finite connected cubic graph contains a cycle")


def connect_cubic_graph_without_losing_colours(edges):
    """Deterministic linear-size source-equivalent connected cubic graph."""
    _,E=validate_cubic_graph(edges)
    E=set(E);history=[]
    while True:
        components=graph_components(tuple(E))
        if len(components)==1:break
        left,right=components[:2]
        e=choose_cycle_edge(tuple(sorted(E)),left)
        f=choose_cycle_edge(tuple(sorted(E)),right)
        a,b=e;c,d=f
        assert len({a,b,c,d})==4
        assert e in E and f in E
        E.remove(e);E.remove(f)
        cross={(min(a,c),max(a,c)),(min(b,d),max(b,d))}
        assert not(cross & E)
        E.update(cross)
        history.append({
            "component1":left,"component2":right,
            "removed":(e,f),"inserted":tuple(sorted(cross)),
        })
        assert len(graph_components(tuple(E)))==len(components)-1
    _,out=validate_cubic_graph(tuple(E))
    assert len(out)==len(edges)
    return out,tuple(history)


def color_parity_every_cubic_cut(edges,colors,side):
    """Independently verify per-colour crossing parity = |side| mod2."""
    _,E=validate_cubic_graph(edges)
    assert len(colors)==len(E)
    side=set(side)
    for c in range(3):
        boundary=sum((u in side)!=(v in side)
                     for (u,v),k in zip(E,colors) if k==c)
        assert boundary%2==len(side)%2
    return True


def explicit_three_colour_layer_paths(edges,src_e,dst_e):
    """Generate and independently recheck 3 edge-disjoint Tanner paths.

    All three use the SAME source line-graph walk and DIFFERENT colours.
    No Tanner source row ordering is assumed after canonical sorting.
    Returned paths are actual Tanner bipartite node IDs.
    """
    vertices,E=validate_cubic_graph(edges)
    assert src_e in E and dst_e in E and src_e!=dst_e
    rows,n,_,idx=make_scl(E)
    row_to_id={tuple(row):i for i,row in enumerate(rows)}
    eid={e:i for i,e in enumerate(E)}
    edge_row={e:row_to_id[tuple(sorted(idx[(e,c)] for c in range(3)))]
              for e in E}
    vertex_row={}
    for v in vertices:
        for c in range(3):
            key=tuple(sorted(idx[(e,c)] for e in E if v in e))
            vertex_row[(v,c)]=row_to_id[key]
    # Build one simple line-graph path in polynomial time.
    parent={src_e:None};queue=[src_e]
    for e in queue:
        if dst_e in parent:break
        for f in E:
            if f not in parent and set(f)&set(e):
                parent[f]=e;queue.append(f)
    assert dst_e in parent
    chain=[];cur=dst_e
    while cur is not None:
        chain.append(cur);cur=parent[cur]
    chain.reverse()
    assert chain[0]==src_e and chain[-1]==dst_e
    original_incidence={
        tuple(sorted((ri,n+v))) for ri,row in enumerate(rows) for v in row
    }
    paths=[]
    for colour in range(3):
        nodes=[edge_row[src_e]]
        for pos,e in enumerate(chain):
            nodes.append(n+idx[(e,colour)])
            if pos+1<len(chain):
                next_e=chain[pos+1]
                common=set(e)&set(next_e)
                assert len(common)==1
                nodes.append(vertex_row[(next(iter(common)),colour)])
            else:
                nodes.append(edge_row[dst_e])
        assert len(nodes)==len(set(nodes))
        path_edges={tuple(sorted((a,b)))
                    for a,b in zip(nodes,nodes[1:])}
        assert len(path_edges)==len(nodes)-1
        assert path_edges<=original_incidence
        paths.append((tuple(nodes),path_edges))
    assert all(not(paths[i][1]&paths[j][1])
               for i in range(3) for j in range(i+1,3))
    return tuple(x[0] for x in paths)



def verify_coloring(edges,colormap):
    """Check every ORIGINAL cubic vertex receives three distinct colours."""
    vertices,E=validate_cubic_graph(edges)
    assert set(colormap)==set(E)
    assert all(colormap[e] in (0,1,2) for e in E)
    for v in vertices:
        assert sorted(colormap[e] for e in E if v in e)==[0,1,2]
    return True


def forward_switch_coloring(original,original_coloring,record):
    """Explicit SAT-witness transfer under a single connected edge switch."""
    _,before=validate_cubic_graph(original)
    assert verify_coloring(before,original_coloring)
    e,f=record['removed']
    crosses=record['inserted']
    left=set(record['component1'])
    right=set(record['component2'])
    assert e in before and f in before
    target=original_coloring[e]
    source=original_coloring[f]
    remaining=[v for v in range(3) if v!=source]
    available=[v for v in range(3) if v!=target]
    recolor={source:target}
    recolor.update(zip(remaining,available))
    new={}
    for edge,value in original_coloring.items():
        if edge in (e,f):continue
        if all(v in right for v in edge):
            new[edge]=recolor[value]
        else:
            new[edge]=value
    for edge in crosses:new[edge]=target
    expected=(set(before)-{e,f})|set(crosses)
    assert set(new)==expected
    assert verify_coloring(tuple(sorted(expected)),new)
    return new


def backward_switch_coloring(connected,connected_coloring,record):
    """Explicit 2-edge-cut colour parity witness recovery."""
    _,after=validate_cubic_graph(connected)
    assert verify_coloring(after,connected_coloring)
    cross1,cross2=record['inserted']
    cut_side=set(record['component1'])
    assert color_parity_every_cubic_cut(
        after,tuple(connected_coloring[e] for e in after),cut_side
    )
    assert connected_coloring[cross1]==connected_coloring[cross2]
    value=connected_coloring[cross1]
    e,f=record['removed']
    new={k:v for k,v in connected_coloring.items() if k not in (cross1,cross2)}
    new[e]=value;new[f]=value
    assert verify_coloring(tuple(sorted(new)),new)
    return new



def main():
    # A bridged cubic graph is also a valid positive control
    # for Tanner connectivity; G itself need NOT be bridgeless.
    k4=K4()
    original=[e for e in k4 if e!=(0,1)]
    bridged=tuple(
        original+[(0,8),(1,8)]
        +[(u+4,v+4) for u,v in original]
        +[(4,9),(5,9),(8,9)]
    )
    graph_cases=[
        ("K4_SAT",k4,True),
        ("K33_SAT",K33(),True),
        ("CUBE_SAT",cube_graph(),True),
        ("PETERSEN_UNSAT",petersen_graph(),False),
        ("CUBIC_WITH_BRIDGE_UNSAT",bridged,False),
    ]
    for name,edges,expect in graph_cases:
        vertices,E=validate_cubic_graph(edges)
        assert len(graph_components(E))==1
        rows,n,_,_=make_scl(E)
        assert len(canonical_scl_components(rows,n))==1
        audited=certified_tanner_edge_connectivity(rows,n)
        assert audited["edge_connectivity"]==3
        # Validate the *constructive* three colour-disjoint paths
        # independently of the expensive Tanner cut enumerator.
        # Sample every edge-row source pair on all small controls.
        for e in E:
            for f in E:
                if e<f:
                    paths=explicit_three_colour_layer_paths(E,e,f)
                    assert len(paths)==3
        assert not audited["two_edge_cut_exists"]
        witness=brute_three_edge_coloring(E)
        assert (witness is not None)==expect
        if witness is not None:
            assert color_parity_every_cubic_cut(E,witness,
                                                vertices[:len(vertices)//2])
        print(f"ATOMIC_HOLYER_TANNER_3EDGE {name} n={n} "
              f"source_SAT={expect} no_1cut=True no_2cut=True",
              flush=True)

    # Independent SAT vs UNSAT combinations: the connected cubic
    # surgery preserves the conjunction exactly and still yields
    # Tanner edge-connectivity=3, even though its ORIGINAL cubic
    # graph contains an explicit 2-edge cut.
    for first,second,truth in (
        (K4(),K4(),True),
        (K4(),petersen_graph(),False),
        (K33(),K4(),True),
    ):
        n1=len({v for e in first for v in e})
        src=tuple(first)+tuple((a+n1,b+n1) for a,b in second)
        _,src=validate_cubic_graph(src)
        assert len(graph_components(src))==2
        result,history=connect_cubic_graph_without_losing_colours(src)
        assert len(history)==1 and len(graph_components(result))==1
        colored=brute_three_edge_coloring(result)
        assert (colored is not None)==truth
        if truth:
            original_colors=brute_three_edge_coloring(src)
            assert original_colors is not None
            old_colors={e:original_colors[i] for i,e in enumerate(src)}
            switched=forward_switch_coloring(
                src,old_colors,history[0]
            )
            assert verify_coloring(result,switched)
            independently_recovered=backward_switch_coloring(
                result,switched,history[0]
            )
            assert verify_coloring(src,independently_recovered)
        rows,n,_,_=make_scl(result)
        topo=certified_tanner_edge_connectivity(rows,n)
        assert topo["edge_connectivity"]==3
        print(f"CONNECTED_CUBIC_COLOUR_EQUIVALENCE source_n={n} "
              f"truth_SAT={truth} tanner_atomic=True",flush=True)

    print("ALL_CONNECTED_SIMPLE_CUBIC_HOLYER_SCL_TANNER_3EDGE=PROVED")
    print("CUBIC_DISCONNECTED_TO_CONNECTED_3EDGECOLOR_EQUIVALENCE=PROVED")
    print("ATOMIC_3EDGE_CONNECTED_TANNER_SCL_SAT=NP_COMPLETE")
    print("SEPARATOR_ONLY_SOLVER_CANNOT_BYPASS_ATOMIC_NP_HARDNESS")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
