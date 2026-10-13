#!/usr/bin/env python3
"""R5 rank-inflation firewall: signature-preserving diamond expansions.

ALL-SIZE THEOREM (no computational assumption):
For any connected cubic sixpole G with six distinct external roots,
replace an ordinary internal edge e=(u,v) by the K4-minus-edge diamond
2-pole: create 4 fresh vertices a,b,c,d and edges
u-a, v-b, a-c, a-d, b-c, b-d, c-d. Original uv edge is removed.
The new graph G' remains simple, connected and cubic.

The diamond is properly 3-edge-colourable; parity plus S3 relabelling
ensures its 2 physical cut colours are equal and any common colour is
available. Therefore Col6(G')=Col6(G) (exact ordered physical states).

For EVERY prescribed six-port tuple s, even if not physically
realisable, let Z_s(G) denote the linear difference-circulation
envelope over F2^2 with original boundary-root line constraints.

At all 4 new internal vertices, conservation implies the two cut
flows are equal. Collapsing them to the old edge gives a surjective
linear projection Z_s(G') -> Z_s(G), whose kernel is the cycle-flow
space of K4 minus one edge: cyclomatic rank 5-4+1=2, over
two-dimensional F2^2 => kernel dimension 4. An extension of each
old flow is given by carrying D_e along u-a-c-b-v and zero elsewhere.
Hence dim Z_s(G')=dim Z_s(G)+4, for ANY s.

Repeating k diamond inflations produces G_k with n+4k vertices,
identical physical six-port relation, and rank inflated by exactly 4k.
Thus bare linear rank is NOT a signature-invariant hardness measure.
Low-cut contraction must precede rank analysis on irreducible cores.

FINITE regression: C6 -> diamond n10 -> two diamonds n14 -> three
diamonds n18. Exhaustively check 729 external port tuples for exact
rank shift at each expansion and independently replay all 6-physical
edge-colouring states for each n.
"""
from itertools import product

from r5_universal_portfree_two_three_edge_cut_exact_signature_retraction import (
    graph_cycle6, inflate_edge_diamond, assert_simple_cubic_multipole,
    colour_states, norm
)
from r5_kempe_fixed_port_gf4_linear_envelope import linear_envelope


def run():
    base, ports = graph_cycle6()
    assert ports == tuple(range(6))
    states0, _ = colour_states(base, ports)
    assert len(states0) == 63
    all_tuples = tuple(product(range(3), repeat=6))
    assert len(all_tuples) == 729
    previous = dict(
        (s, linear_envelope(base,ports,s)[0])
        for s in all_tuples
    )
    edge_to_replace=(0,1)
    E=base
    for k in range(1,4):
        n = len(assert_simple_cubic_multipole(E,ports))
        assert n == 6+4*(k-1)
        E, B=inflate_edge_diamond(E,edge_to_replace,n)
        assert len(B)==4
        next_vertices=assert_simple_cubic_multipole(E,ports)
        assert len(next_vertices)==6+4*k
        current=dict(
            (s,linear_envelope(E,ports,s)[0])
            for s in all_tuples
        )
        assert all(current[s]-previous[s]==4 for s in all_tuples)
        states,_=colour_states(E,ports)
        assert states==states0,(k,len(states),len(states0))
        print("DIAMOND_RANK_INFLATION", {
            "diamonds":k,
            "n":6+4*k,
            "all_729_port_tuples_exact_plus4":True,
            "physical_sixport_state_count":len(states),
            "min_good_port_rank": min(
                current[s] for s in all_tuples
                if (s[0]==s[1])+(s[2]==s[3])+(s[4]==s[5])==1
                and all(s.count(c)%2==0 for c in range(3))
            )
        },flush=True)
        previous=current
        edge_to_replace=norm(n+2,n+3)
    print("ALL_SIZE_THEOREM Col6 unchanged, dimZ_s increases by 4 per diamond")
    print("UNBOUNDED_LINEAR_RANK_NOT_SIGNATURE_INVARIANT")
    print("MANDATORY: LOW_CUT_CONTRACTION_BEFORE_IRREDUCIBLE_FLOW_RANK")
    print("SolveLinearCubicXSAT=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__=="__main__":
    run()
