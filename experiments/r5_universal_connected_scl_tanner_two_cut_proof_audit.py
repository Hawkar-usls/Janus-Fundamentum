#!/usr/bin/env python3
"""R5 exact all-source Tanner 1/2-edge separator audit.

THEOREM for EVERY square+cubic/linear positive exact-one SCL matrix:
Its bipartite row-variable incidence (Tanner/Levi) graph is simple
3-regular and bipartite. For ANY vertex subset S, if a crossing
incidence ends at a row vertex on the S side and b at a variable
vertex on the S side, then
     a - b = 3*(#rows(S)-#variables(S)).
A one-edge cut would imply a-b=+/-1, contradiction. Consequently
a connected legal SCL Tanner graph has NO BRIDGES.

For any 2-edge cut, a+b=2 and a-b multiple 3. The only possibility
is a=b=1, #rows(S)=#variables(S). Thus every 2-cut separates
BOTH sides into square internal constraint fragments, each with
exactly ONE clause-port and ONE variable-port. Such fragments
are NOT themselves legal 3-regular SCL matrices before border
reconstruction; don't simply route them to normal SCL solver.

Enumerating all edge pairs and doing exact graph reachability is
O(n^3) for bounded degree3; no heuristic topology inference.
If a connected SCL source has no 2-edge cut, it is exactly
3-edge-connected (degree 3 supplies a vertex cut of size3).
This is a structural reduction of the unresolved input frontier,
NOT a solver/coverage theorem on connected hard cores.
"""
from __future__ import annotations
from itertools import combinations
from collections import Counter,deque

from r5_universal_exact_support_residual_dag_attack import validate_sparse


def exact_tanner_graph(rows,n):
    rows=validate_sparse(rows,n)
    vertices=2*n
    edges=tuple((ci,n+v) for ci,row in enumerate(rows) for v in row)
    assert len(edges)==3*n
    neighbors=[[] for _ in range(vertices)]
    for ei,(a,b) in enumerate(edges):
        neighbors[a].append((b,ei))
        neighbors[b].append((a,ei))
    assert all(len(nn)==3 for nn in neighbors)
    return edges,tuple(tuple(x) for x in neighbors)


def reach(neighbors,banned=()):
    blocked=set(banned)
    found={0}; queue=[0]
    while queue:
        for nxt,ei in neighbors[queue.pop()]:
            if ei not in blocked and nxt not in found:
                found.add(nxt);queue.append(nxt)
    return frozenset(found)


def crossing_profile(edges,n,side):
    outgoing=[i for i,(a,b) in enumerate(edges)
              if (a in side)!=(b in side)]
    row_out=sum(1 for i in outgoing if edges[i][0] in side)
    variable_out=sum(1 for i in outgoing if edges[i][1] in side)
    row_count=sum(v<n for v in side)
    variable_count=len(side)-row_count
    assert row_out-variable_out==3*(row_count-variable_count)
    return {'crossing_edges':tuple(outgoing),'row_out':row_out,
            'variable_out':variable_out,'rows_side':row_count,
            'variables_side':variable_count}


def certified_tanner_edge_connectivity(rows,n,first_only=True):
    edges,adj=exact_tanner_graph(rows,n)
    assert len(reach(adj))==2*n, 'input is disconnected; decompose first'
    # A connected 3-regular bipartite graph must be bridgeless.
    # Verify each original incidence independently in this finite test.
    for i in range(len(edges)):
        assert len(reach(adj,(i,)))==2*n
    inspected=0;witnesses=[]
    for i,j in combinations(range(len(edges)),2):
        inspected+=1
        side=reach(adj,(i,j))
        if len(side)==2*n:continue
        profile=crossing_profile(edges,n,side)
        assert set(profile['crossing_edges'])=={i,j}
        assert profile['row_out']==profile['variable_out']==1
        assert profile['rows_side']==profile['variables_side']
        back=crossing_profile(edges,n,set(range(2*n))-set(side))
        assert back['row_out']==back['variable_out']==1
        assert back['rows_side']==back['variables_side']
        witnesses.append({'edge_ids':(i,j),
                          'edge_incidence':(edges[i],edges[j]),
                          'side':side,'profile':profile})
        if first_only:break
    return {
        'n':n,'edges':len(edges),
        'one_edge_cuts':0,
        'two_edge_cut_exists':bool(witnesses),
        'edge_connectivity':2 if witnesses else 3,
        'pairs_examined':inspected,
        'cuts':witnesses,
    }


def certified_two_cut_mod3_rules(rows,n,max_n=None):
    """Certified polynomial preprocessing on CONNECTED sources.

    For a 2-edge cut side S with r internal rows and r internal vars,
    the two crossing original-incidence ports define u=inside variable
    incident to an external clause, and v=external variable incident
    to an inside clause. Exact-One row-sum over S yields

        3*sum_{w in variables(S)} x_w = r + x_u - x_v.

    Hence (r modulo 3):
      0 -> x_u=x_v (two certified forbidden unequal pairs);
      1 -> x_u=0, x_v=1;
      2 -> x_u=1, x_v=0.

    Every forced pin is backed by the original cut rows/variable IDs.
    This preprocessing runs at most O(n^3) bounded-degree graph work.
    If max_n restricts its execution, it returns SKIPPED, not a guess.
    """
    rows=validate_sparse(rows,n)
    if max_n is not None and n>max_n:
        return {'status':'SKIPPED_SIZE_GUARD',
                'pins':{},'equalities':(),'certificates':()}
    edges,adj=exact_tanner_graph(rows,n)
    assert len(reach(adj))==2*n, 'component preprocessing comes first'
    props=certified_tanner_edge_connectivity(rows,n,first_only=False)
    pins={};equalities=set();certs=[]
    for cut in props['cuts']:
        side=cut['side']
        profile=cut['profile']
        assert profile['row_out']==profile['variable_out']==1
        a,b=cut['edge_ids']
        edge_pair=(edges[a],edges[b])
        outgoing=[(row,var) for row,var in edge_pair if row in side]
        incoming=[(row,var) for row,var in edge_pair if n+var in side]
        assert len(outgoing)==len(incoming)==1
        # edges[] hold (row node, n+variable node) not local index:
        ext_variable=outgoing[0][1]-n
        int_variable=incoming[0][1]-n
        assert n+int_variable in side and n+ext_variable not in side
        residue=profile['rows_side']%3
        record={
            'edge_ids':(a,b),
            'row_side_count':profile['rows_side'],
            'variable_side_count':profile['variables_side'],
            'inside_var':int_variable,
            'outside_var':ext_variable,
            'residue':residue,
            'algebraic_identity':'3sum_inside_x = rows_inside + inside_x - outside_x',
        }
        certs.append(record)
        if residue==0:
            equalities.add(tuple(sorted((int_variable,ext_variable))))
        else:
            assignments=(
                {int_variable:0,ext_variable:1}
                if residue==1
                else {int_variable:1,ext_variable:0}
            )
            for v,b in assignments.items():
                if v in pins and pins[v]!=b:
                    return {'status':'UNSAT',
                            'reason':'CONFLICTING_VERIFIED_TWO_CUT_ARITHMETIC_PINS',
                            'pins':pins,'equalities':tuple(sorted(equalities)),
                            'certificates':tuple(certs)}
                pins[v]=b
    return {'status':'CERTIFIED',
            'pins':pins,'equalities':tuple(sorted(equalities)),
            'certificates':tuple(certs)}


def exact_connected_incidence_switch(source_a,source_b):
    """Join two valid SCL sources with a certified 2-edge Tanner cut."""
    na=len(source_a);nb=len(source_b)
    rows=[tuple(row) for row in validate_sparse(source_a,na)]
    rows.extend(tuple(v+na for v in row)
                for row in validate_sparse(source_b,nb))
    inside=rows[0][0];outside=rows[na][0]
    rows[0]=tuple(sorted((set(rows[0])-{inside})|{outside}))
    rows[na]=tuple(sorted((set(rows[na])-{outside})|{inside}))
    total=validate_sparse(rows,na+nb)
    assert len(canonical_connected_components_for_test(total,na+nb))==1
    return total


def canonical_connected_components_for_test(rows,n):
    edges,adj=exact_tanner_graph(rows,n)
    parts=[]
    unvisited=set(range(2*n))
    while unvisited:
        start=min(unvisited);todo=[start];found={start}
        while todo:
            for v,_ in adj[todo.pop()]:
                if v not in found:
                    found.add(v);todo.append(v)
        parts.append(found)
        unvisited-=found
    return parts


def main():
    from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
    from r5_universal_cubic_edgecolor_direct_scl_bridge import K4,make_scl
    from r5_universal_certified_scl_component_decomposition import (
        canonical_scl_components,
    )

    fano=cyclic(7)
    seven=certified_tanner_edge_connectivity(fano,7)
    assert seven['edge_connectivity']==3 and not seven['cuts']
    print('FANO_SCL7_HEAWOOD_TANNER_THREE_EDGE_CONNECTED=VERIFIED',
          flush=True)

    seed,n,_,_=make_scl(K4())
    a=tuple(seed)
    out=[tuple(row) for row in a]
    out.extend(tuple(v+n for v in row) for row in a)
    local_a=out[0][0]
    local_b=out[n][0]
    r0=(set(out[0])-{local_a})|{local_b}
    r1=(set(out[n])-{local_b})|{local_a}
    out[0]=tuple(sorted(r0));out[n]=tuple(sorted(r1))
    out=validate_sparse(out,2*n)
    assert len(canonical_scl_components(out,2*n))==1
    shape=certified_tanner_edge_connectivity(out,2*n)
    assert shape['edge_connectivity']==2 and shape['cuts']
    cut=shape['cuts'][0]
    assert sorted((cut['profile']['rows_side'],2*n-cut['profile']['rows_side']))==[n,n]
    print(f'CONNECTED_SCL36_INCIDENCE_SWAP_CUT2=VERIFIED '
          f'row_partition={cut["profile"]["rows_side"]}+{2*n-cut["profile"]["rows_side"]} '
          f'cut_edges={cut["edge_incidence"]}',flush=True)
    fano_cyclic=cyclic(7)
    cyclic8=validate_sparse(
        [tuple(sorted((i,(i+1)%8,(i+3)%8))) for i in range(8)],8
    )
    connected15=exact_connected_incidence_switch(fano_cyclic,cyclic8)
    derived=certified_two_cut_mod3_rules(connected15,15,max_n=32)
    assert derived['status']=='CERTIFIED'
    assert derived['pins'] and len(derived['pins'])==2
    assert len(derived['certificates'])>=1
    # TRUE universal implication checked independently for every
    # complete Boolean assignment of this finite n15 instance.
    satisfying=0
    for mask in range(1<<15):
        if all(sum((mask>>v)&1 for v in clause)==1
               for clause in connected15):
            satisfying+=1
            assert all(((mask>>v)&1)==b
                       for v,b in derived['pins'].items())
    print(f'CONNECTED_SCL15_CUT2_ARITHMETIC_FORCES_PINS={derived["pins"]} '
          f'finite_sat_witnesses={satisfying}',flush=True)
    assert satisfying>0, 'ensure forced pins are nonvacuous'
    same=certified_two_cut_mod3_rules(out,2*n,max_n=40)
    assert same['status']=='CERTIFIED'
    assert len(same['pins'])==0 and len(same['equalities'])>=1
    print(f'CONNECTED_SCL36_CUT2_MOD3_EQUALITIES={same["equalities"][:2]}',
          flush=True)
    print('UNIVERSAL_SCL_TWO_CUT_MOD3_BOUNDARY_RULES=PROVED',flush=True)
    print('ALL_SCL_TANNER_SINGLE_EDGE_CUT_IMPOSSIBLE=PROVED_ALL_INPUTS',flush=True)
    print('ALL_SCL_TANNER_TWO_EDGE_CUT_BALANCED_CROSS_PORTS=PROVED_ALL_INPUTS',flush=True)
    print('CONNECTED_NO_CUT2_IMPLIES_3_EDGE_CONNECTED=PROVED_ALL_INPUTS',flush=True)
    print('THIS_IS_BOUNDARY_RECOGNITION_NOT_AN_EXACT_BOUNDARY_DP_SOLVER',flush=True)
    print('UNIVERSAL_POLY_SOLVER=NOT_CONSTRUCTED')
    print('P_VS_NP=OPEN')


if __name__=='__main__':
    main()
