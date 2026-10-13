#!/usr/bin/env python3
"""R5: fixed six-port physical signature membership is NP-complete at fixed Q.

SOURCE THEOREM: Holyer (1981), 3-edge-colorability of cubic graphs is
NP-complete, SIAM J Comput 10(4):718-720, DOI 10.1137/0210055.

NEW ELEMENTARY GADGET REDUCTION (proved for every source size):
Given any connected simple cubic G, choose an edge uv on a cycle, so
G - uv is connected. Remove uv. Create a disjoint six-cycle C6 with
vertices 0..5 and six external semiedges at its distinct vertices.
Remove the cycle edge 01, and connect u to 0 and v to 1. Result M_G
is a connected simple cubic SIXPOLE with six distinct port roots.

Fix physical tuple s*=(0,0,1,2,2,1), truth bits 100.
Among all proper colourings of the six-cycle part with those external
colours and TWO interface edges of the SAME colour, the unique one
has interface colour 1, and cycle path e1..e5 colours 2,0,1,0,2
(cycle e_i=(i,i+1 modulo 6)). The G-side colour-parity / GF4 flow
law forces its two connector colours equal (even if G-e is disconnected).
The forced common colour can be closed as the original edge uv.

Consequently:
  s* in Col6(M_G)  IFF  G has a proper three-edge-colouring.
  Col6(M_G) = Col6(C6) of 63 physical states, if G colourable,
             EMPTY otherwise.
  Number of full interior colourings of M_G extending s*
    = #proper full edge-3-colourings of G with uv colour1
    = #proper full edge-3-colourings of G / 3.
The equivalence, membership in NP, and Holyer's input theorem
establish NP-COMPLETENESS of fixed physical s*-membership among
simple connected cubic sixpoles with six distinct roots.

Moreover, because G-uv is CONNECTED, the canonical six-marked-edge
Klein-four trace multigraph Q_M is EXACTLY the same labelled six-cycle
Q_C6, regardless of colourability. Thus all 729 normalized flow ranks
are identical, and the NP-complete yes/no is hidden wholly in the
nonlinear nowhere-zero/proper-colouring condition.

Implication: selecting the nonempty full boundary signature of an
ARBITRARY port-free 2-pole is NP-hard. The previous port-free 2-cut
semantic contraction is valid IF the block is colourable, but cannot
be invoked as an unconditional polynomial-time source algorithm.

Finite controls independently enumerate all full edge colourings of
source G and M_G for G=K4, triangular prism, Q3 cube, Petersen. Expected:
                 source  fixed-uv=1   M pinned   M physical |Col6|
  K4                 6          2         2           63
  Prism              6          2         2           63
  Cube Q3           24          8         8           63
  Petersen           0          0         0            0
All 4 constructed M_G have exactly the SAME ordered 6-edge Q as C6.

THEOREM LIMIT: This does NOT prove the required Exact-One no-go, PC
lower bounds, or polynomial SCL algorithm. It is a structural hardness
barrier to deciding the general nonlinear six-terminal signature.
"""

from collections import defaultdict, Counter

from r5_universal_portfree_two_three_edge_cut_exact_signature_retraction import (
    graph_cycle6, colour_states, norm,
)
from r5_kempe_six_marked_edge_trace_quotient import (
    marked_six_edge_quotient, six_edge_flow_rank,
)

FIXED_PORTS = (0, 0, 1, 2, 2, 1)
PORT_ROOTS = tuple(range(6))
CYCLE_EDGES = tuple(norm(j, (j+1) % 6) for j in range(6))


def is_connected(n, edges):
    adj=[[] for _ in range(n)]
    for u,v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen, stack = {0}, [0]
    while stack:
        for v in adj[stack.pop()]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen)==n


def source_graphs():
    K4 = (4, tuple((i,j) for i in range(4) for j in range(i+1,4)))
    prism=(6, ((0,1),(1,2),(0,2),(3,4),(4,5),(3,5),
              (0,3),(1,4),(2,5)))
    cube=(8, tuple((v,v^(1<<k)) for v in range(8)
                   for k in range(3) if v<(v^(1<<k))))
    petersen_edges=[
        norm(i,(i+1)%5) for i in range(5)
    ]+[(i,i+5) for i in range(5)]+[
        norm(i+5,((i+2)%5)+5) for i in range(5)
    ]
    petersen=(10,tuple(petersen_edges))
    return (
        ("K4",K4,6,2,63,132),
        ("PRISM",prism,6,2,63,132),
        ("Q3_CUBE",cube,24,8,63,528),
        ("PETERSEN",petersen,0,0,0,0),
    )


def check_cubic(n, edges):
    assert all(0<=u<v<n for u,v in edges)
    assert len(set(edges))==len(edges)
    deg=Counter(v for e in edges for v in e)
    assert all(deg[v]==3 for v in range(n))
    assert is_connected(n, edges)


def choose_nonbridge_edge(n, edges):
    """Pick an edge whose deletion preserves connectedness (always exists)."""
    for e in edges:
        after=[x for x in edges if x != e]
        if is_connected(n,after):
            return e
    raise AssertionError("no cycle edge in connected cubic graph")


def splice(G, edge=None):
    n,E=G
    E=tuple(sorted(norm(*e) for e in E))
    check_cubic(n,E)
    if edge is None:
        edge=choose_nonbridge_edge(n,E)
    u,v=norm(*edge)
    assert (u,v) in E
    assert is_connected(n,[e for e in E if e!=(u,v)])
    # Label 0..5 the six terminals of the fixed C6 fragment.
    cycle_without_01={e for e in CYCLE_EDGES if e!=(0,1)}
    old_without_edge={norm(a+6,b+6) for a,b in E if (a,b)!=(u,v)}
    join={norm(0,u+6),norm(1,v+6)}
    M=tuple(sorted(cycle_without_01|old_without_edge|join))
    N=n+6
    assert is_connected(N,M)
    degree=Counter(v for e in M for v in e)
    assert all(degree[v]==(2 if v in PORT_ROOTS else 3)
               for v in range(N))
    assert len(M)==(3*N-6)//2
    return N,M,(u,v)


def count_full_colourings(n, edges, roots=(), ports=(), fixed_edge=None):
    """Standalone MRV full proper edge-colouring count with optional pins."""
    edges=tuple(edges)
    assert len(roots)==len(ports)
    used=[set() for _ in range(n)]
    for v,c in zip(roots,ports):
        assert c not in used[v]
        used[v].add(c)
    count=0
    def recurse(todo):
        nonlocal count
        if not todo:
            count+=1
            return
        choices=[]
        for k in todo:
            u,v=edges[k]
            allowed=set((0,1,2))-used[u]-used[v]
            if fixed_edge == k:
                allowed &= {1}
            if not allowed:
                return
            choices.append((len(allowed),k,allowed))
        _,k,choices_k=min(choices)
        u,v=edges[k]
        next_todo=[j for j in todo if j!=k]
        for c in choices_k:
            used[u].add(c);used[v].add(c)
            recurse(next_todo)
            used[u].remove(c);used[v].remove(c)
    recurse(list(range(len(edges))))
    return count


def cycle_fragment_interface_audit():
    """Enumerate all 3^5 path colour assignments given s* and equal cuts."""
    from itertools import product
    accepted={}
    for a in range(3):
        paths=[]
        for e1,e2,e3,e4,e5 in product(range(3),repeat=5):
            triples=((a,e5,FIXED_PORTS[0]),
                     (a,e1,FIXED_PORTS[1]),
                     (e1,e2,FIXED_PORTS[2]),
                     (e2,e3,FIXED_PORTS[3]),
                     (e3,e4,FIXED_PORTS[4]),
                     (e4,e5,FIXED_PORTS[5]))
            if all(set(t)=={0,1,2} for t in triples):
                paths.append((e1,e2,e3,e4,e5))
        accepted[a]=tuple(paths)
    assert accepted=={
        0:(),
        1:((2,0,1,0,2),),
        2:(),
    }
    return accepted


def run():
    assert (FIXED_PORTS[0]==FIXED_PORTS[1],
            FIXED_PORTS[2]==FIXED_PORTS[3],
            FIXED_PORTS[4]==FIXED_PORTS[5])==(True,False,False)
    assert cycle_fragment_interface_audit()[1]==((2,0,1,0,2),)
    c6, c6ports = graph_cycle6()
    physical_c6,total_c6=colour_states(c6,c6ports)
    assert len(physical_c6)==63 and total_c6==66
    assert FIXED_PORTS in physical_c6
    base_Q,base_q,base_n=marked_six_edge_quotient(
        tuple(sorted(c6)),PORT_ROOTS)
    assert base_n==6 and base_q==6
    assert len(base_Q)==6

    for (label,G,total_expected,fixed_expected,
         outer_expected,total_M_expected) in source_graphs():
        n,E=G
        E=tuple(sorted(norm(*e) for e in E))
        check_cubic(n,E)
        N,M,deleted=splice((n,E))
        selected=E.index(deleted)
        total_G=count_full_colourings(n,E)
        colour1_G=count_full_colourings(n,E,fixed_edge=selected)
        pinned_M=count_full_colourings(N,M,PORT_ROOTS,FIXED_PORTS)
        physical_M,total_M=colour_states(M,PORT_ROOTS)
        Q,q,check_N=marked_six_edge_quotient(M,PORT_ROOTS)
        assert Q==base_Q and q==base_q and check_N==N
        assert physical_M==(
            physical_c6 if total_G else frozenset())
        assert (total_G,colour1_G,pinned_M,len(physical_M),total_M)==(
            total_expected,fixed_expected,fixed_expected,
            outer_expected,total_M_expected
        ),label
        assert total_G==3*colour1_G
        # Every prescribed six-port linear defect is the SAME.
        for a in range(3):
            for b in range(3):
                for c in range(3):
                    sample=(a,a,b,b,c,c)
                    assert six_edge_flow_rank(Q,q,sample)==six_edge_flow_rank(
                        base_Q,base_q,sample)
        print("FIXED_Q_NP_COMPLETE_PIN_WITNESS",{
            "source":label,"source_vertices":n,
            "source_3edge_colourings":total_G,
            "source_edge_colour_1":colour1_G,
            "sixpole_vertices":N,
            "pinned_001221_full_colours":pinned_M,
            "full_sixport_physical_states":len(physical_M),
            "all_full_sixpole_colours":total_M,
            "Q_matches_C6":True,
        },flush=True)
    print("ALL_N_THEOREM: s_star_MEMBERSHIP_NP_COMPLETE_WITH_SAME_FIXED_Q")
    print("ALL_N_THEOREM: Col6(M_G) either EXACT_C6_63 or EMPTY")
    print("TWO_POLE_COLOURABILITY_PROMISE_NP_HARD; DO_NOT_CONTRACT_BLINDLY")
    print("NOT_EXACTONE_GADGET; NO_GENERAL_POLY_SCL_SOLVER; P_VS_NP_OPEN")


if __name__=="__main__":
    run()
