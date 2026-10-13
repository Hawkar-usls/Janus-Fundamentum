#!/usr/bin/env python3
"""R5 all-n EXACT six-marked-edge cycle-trace quotient for GF(2)^2 envelopes.

THEOREM (no claim about proper colourability):
For connected cubic 6poles with six labelled semiedges at DISTINCT
roots, construct a six-edge multigraph Q:
(1) split each marked degree-2 root into two stubs joined by a
    *special* edge (one special edge per port);
(2) retain all original ordinary edges, each attached to its stub
    if the endpoint was marked, and otherwise to the old vertex;
(3) DELETE all six special edges and contract each connected
    component of the remainder;
(4) retain the six labelled special edges between component vertices.
Q is a connected multigraph with exactly six labelled edges, q<=7
vertices, and loops/multiple edges allowed.

Let beta=m-n+1=(n-4)/2 for the internal ordinary graph; let
h=dim H1(Q,F2)=7-q. Define W_s as Klein-four flows on six Q edges
with D_i in span_F2(code(s_i)) for each physical port colour s_i.

Then the exact sequence of F2-linear spaces is
  0 -> H1(H - six specials;F2^2)
    -> Z_s(G)
    -> W_s(Q)
    -> 0.
Hence
  dim Z_s(G) = 2*(beta-h) + dim W_s(Q)
             = (n-4) - r_s(Q),
where 0<=r_s(Q)=2*h-dim W_s(Q)<=6.

Q is obtained in O(n+m) via union-find. Its W_s dimension is computed
by Gaussian elimination on 12 variables. Thus all 729 external
colour-tuples can be audited in O(n+m)+O(729) fixed-size field work.
This is a polynomial EXACT normalization of the LINEAR envelope,
NOT of the nonlinear nowhere-zero/proper 3-colouring set.

In particular, ALWAYS max(0,n-10)<=dim Z_s<=n-4.
For even n>=12, dim Z_s>=2 for every boundary tuple, so the old
rank0/rank1 local-firewall witnesses CANNOT apply to n>=12,
whether reducible or high-connectivity irreducible.

The six-length binary trace code T is H1(Q,F2), with at most 2825
possible abstract subspaces of F2^6 (sum of Gaussian binomials).
No claim that all 2825 are physically realized by cubic sixpoles.

Regression:
C6 n6:  all 729 direct ranks match Q: dim0=726, dim1=3.
physical n8: dim0=468, dim1=252, dim2=9.
diamond n10: dim4=726, dim5=3.
inflated C6 n14,n18: all 729 equal; +4 per inflation.
"""

from collections import Counter
from itertools import product

from r5_universal_portfree_two_three_edge_cut_exact_signature_retraction import (
    graph_cycle6, inflate_edge_diamond, norm,
)
from r5_kempe_fixed_port_gf4_linear_envelope import linear_envelope
from r5_kempe_physical_fiveloop_gf4_flow_witness import WITNESS_EDGES


def gf2_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            lead = row.bit_length() - 1
            if lead in pivots:
                row ^= pivots[lead]
            else:
                pivots[lead] = row
                break
    return len(pivots)


def marked_six_edge_quotient(edges, port_roots):
    """Return (Q edges in SAME port order, number of quotient vertices, n).

    All input edges are sorted undirected (u<v) and all ports have
    distinct roots and ONE dangling semiedge per root.
    """
    edges = tuple(edges)
    port_roots = tuple(port_roots)
    assert len(port_roots) == len(set(port_roots)) == 6
    assert len(edges) == len(set(edges))
    adj = {}
    for j, (u, v) in enumerate(edges):
        assert u < v
        adj.setdefault(u, []).append(j)
        adj.setdefault(v, []).append(j)
    vertices = set(adj) | set(port_roots)
    roots = set(port_roots)
    assert all(len(adj.get(v, [])) == (2 if v in roots else 3)
               for v in vertices)
    n = len(vertices)
    assert 2*len(edges) + 6 == 3*n
    assert n % 2 == 0

    # A marked root becomes TWO stubs, connected by one labelled
    # special edge; an unmarked vertex stays a single node.
    node_ids = {}
    index = 0
    for r in port_roots:
        for e in sorted(adj[r]):
            node_ids[(r, e)] = index
            index += 1
    for v in sorted(vertices - roots):
        node_ids[(v, None)] = index
        index += 1

    parent = list(range(index))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(u, v):
        a, b = find(u), find(v)
        if a != b:
            parent[a] = b

    def stub(v, edge_id):
        return node_ids[(v, edge_id if v in roots else None)]

    # Contract the components of the graph WITHOUT its six marked edges.
    for j, (u, v) in enumerate(edges):
        union(stub(u, j), stub(v, j))

    comps = {
        representative: index
        for index, representative in enumerate(
            sorted({find(k) for k in range(len(parent))})
        )
    }
    Q = []
    for r in port_roots:
        j, k = sorted(adj[r])
        Q.append((comps[find(node_ids[(r, j)])],
                  comps[find(node_ids[(r, k)])]))
    q = len(comps)
    assert 1 <= q <= 7
    assert len(Q) == 6
    assert connected_multigraph(q, Q)
    h = 7 - q
    assert 0 <= h <= (n-4)//2
    return tuple(Q), q, n


def connected_multigraph(n, edges):
    neighbours = [[] for _ in range(n)]
    for u, v in edges:
        neighbours[u].append(v)
        neighbours[v].append(u)
    seen, todo = {0}, [0]
    while todo:
        u = todo.pop()
        for v in neighbours[u]:
            if v not in seen:
                seen.add(v)
                todo.append(v)
    return len(seen) == n


def six_edge_flow_rank(Q, q, colours):
    """Return (W_s dimension, codimension r_s) using just 12 bits."""
    assert len(Q) == len(colours) == 6
    assert connected_multigraph(q, Q)
    rows = []
    for v in range(q):
        for bit in (0,1):
            mask = 0
            for j, (u, w) in enumerate(Q):
                if (u == v) != (w == v):
                    mask ^= 1 << (2*j+bit)
            rows.append(mask)
    for j,c in enumerate(colours):
        assert c in (0,1,2)
        if c == 0:  # span(code0=01): high bit=0
            rows.append(1 << (2*j+1))
        elif c == 1: # span(code1=10): low bit=0
            rows.append(1 << (2*j))
        else:        # span(code2=11): low==high
            rows.append((1 << (2*j)) | (1 << (2*j+1)))
    w = 12 - gf2_rank(rows)
    h = 7-q
    r = 2*h-w
    assert 0 <= r <= 6
    return w, r


def gaussian_binomial(n,k):
    numerator, denominator = 1,1
    for i in range(k):
        numerator *= (2**n - 2**i)
        denominator *= (2**k - 2**i)
    assert numerator % denominator == 0
    return numerator//denominator


def regression(label, edges, roots=tuple(range(6)), reference=None):
    Q,q,n = marked_six_edge_quotient(edges, roots)
    m = len(edges)
    beta = m-n+1
    h = 7-q
    assert beta==(n-4)//2 and 2*m+6==3*n
    assert 0<=h<=beta
    histogram=Counter()
    colour_tests=tuple(product(range(3),repeat=6))
    assert len(colour_tests)==729
    for s in colour_tests:
        w,r = six_edge_flow_rank(Q,q,s)
        expected = 2*(beta-h)+w
        independent, _ = linear_envelope(edges, roots, s)
        assert independent == expected == (n-4-r), (
            label, s, independent, expected, r
        )
        assert max(0,n-10)<=expected<=n-4
        histogram[expected]+=1
        if reference is not None:
            assert independent == reference[s]+4, (
                label, s, reference[s], independent
            )
    print("SIX_EDGE_TRACE_ALL_729",label,{
        'vertices':n,
        'full_cycle_rank':beta,
        'trace_quotient_vertices':q,
        'trace_cycle_rank':h,
        'Q_six_labelled_edges':Q,
        'dim_Zs_histogram':dict(sorted(histogram.items())),
        'all_Q_vs_direct_exact':True,
    },flush=True)
    return {s:2*(beta-h)+six_edge_flow_rank(Q,q,s)[0]
            for s in colour_tests}, Q


def test():
    assert [gaussian_binomial(6,k) for k in range(7)] == [
        1,63,651,1395,651,63,1
    ]
    assert sum(gaussian_binomial(6,k) for k in range(7)) == 2825
    c6,ports = graph_cycle6()
    base,Q0 = regression("BASE_C6",tuple(sorted(c6)),ports)
    assert Counter(base.values())==Counter({0:726,1:3})

    w,Qw = regression("N8_PHYSICAL_FIVE_LOOP",WITNESS_EDGES,ports)
    assert Counter(w.values())==Counter({0:468,1:252,2:9})

    E, _ = inflate_edge_diamond(c6,norm(0,1),first_new=6)
    prior,Q = regression("DIAMOND_1_N10",tuple(sorted(E)),ports,base)
    assert Counter(prior.values())==Counter({4:726,5:3})

    # Diamond within previous diamond, preserves six-edge trace code.
    link=norm(8,9)
    for num in (2,3):
        first_new=6+4*(num-1)
        E,_=inflate_edge_diamond(E,link,first_new)
        nxt,Qn = regression(
            "DIAMOND_%s_N%s" % (num,6+4*num),
            tuple(sorted(E)),ports,prior
        )
        assert all(nxt[s]-base[s]==4*num for s in base)
        prior=nxt
        link=norm(first_new+2,first_new+3)
    print("ALL_N_EXACT_SEQUENCE: LINEAR_Zs_TO_FIXED_6_EDGE_FLOW_GRAPH PASS")
    print("ALL_N_DIM_LOWER_BOUND_n_MINUS_10; RANK0_RANK1_IMPOSSIBLE_n_GE_12")
    print("ONLY_LINEAR_RELATION_NORMALIZED; NONZERO_EDGE_COLOURABILITY_NOT_DECIDED")
    print("SolveLinearCubicXSAT=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__ == "__main__":
    test()
