#!/usr/bin/env python3
"""R5 all-size bridge and planar-port-order obstruction for full Exact-One.

Assume a connected simple cubic sixpole M with six distinctly rooted,
labelled physical semiedges, proper 3-edge-colouring, three ordered
logical equality-pairs (0,1),(2,3),(4,5), and FULL bit relation
exactly {100,010,001}.

Previously proven ALL-SIZE saturation via forced Kempe paths requires
all 108 even-parity physical tuples with those equality bits to occur.

THEOREM A (no nontrivial boundary bridge):
For any ordinary bridge e, choose one component H of M-e and let K be
its subset of the 6 labelled physical ports. Interpret edge colours
0,1,2 as nonzero Klein-four elements 1,2,3. Summing Kirchhoff
identities on H yields colour(e) = XOR_{i in K} colour(port_i) != 0.

On the 108-state full Exact-One set, for EVERY labelled K of sizes
0,2,3,4,6 there is a boundary tuple with XOR(K)=0. Thus a bridge
cannot split off 0,2,3,4,6 external ports.

If |K|=1 (or 5), the one-port side is a cubic 2-pole (its one outer
semiedge plus the bridge) whose two colours must agree by parity, and
if nonempty it allows each common colour by global S3 symmetry.
If the bridge endpoint in the OTHER component carries a different
physical semiedge, equality of those two external colours is forbidden
in every colouring, contradicting the all-108 target (each pair of
physical ports can be equal somewhere). Otherwise replace the whole
one-port pendant and the bridge by a semiedge at the outside endpoint:
this preserves FULL ordered Col6, simplicity, cubicity, connectivity,
and distinct physical port roots, while strictly decreasing |V|.
Therefore a MINIMUM-ORDER legal full-Exact-One sixpole is BRIDGELESS.
This is an all-size theorem, not a generic SAT solving algorithm.

THEOREM B (topological noncrossing Kempe condition):
Suppose a full Exact-One sixpole is embedded in a closed topological
disk, all six labelled semiedges meeting its boundary in cyclic order.
Among 108 required physical tuples and all 3 colour pairs, exactly
252 state/colour-pair decisions force a UNIQUE good-safe pairing of
Kempe terminal paths. Disjoint paths embedded in a disk cannot cross.

Exhaustively check all 60 unoriented cyclic orders of six labelled
ports up to rotation and reversal (fix 0 first and order[1]<order[-1]).
In EXACTLY 52 cyclic orders, >=1 of 252 forced pairings crosses.
The ONLY 8 remaining orders put all 3 logical port pairs consecutively
on the disk boundary. This is an all-size NECESSARY PLANAR ORDERING
condition; the 8 surviving orders are NOT asserted physically
realizable as full Exact-One gadgets.

FINITE POSITIVE WITNESS:
Join the 6-vertex hetero-two 4-pole and the Petersen-minus-two
8-vertex 4-pole at one semiedge each. The result is a connected simple
cubic n14 sixpole with 6 distinct physical semiedge roots and exactly
36 physical boundary tuples, with equality bits ONLY '001' under
the pairing (0,5),(1,2),(3,4). It supplies a REAL good-only SINGLE-BIT
sixpole, so the stronger statement "every good-only sixpole must
realise all three onehot bits" is FALSE. This graph has a 3+3 bridge,
and does not contradict Theorem A because it is NOT full Exact-One.

REGRESSIONS:
- all 108 even-parity target physical tuples reconstructed;
- for all 15 physical port pairs there exist equal and unequal states;
- for all 50 subsets of sizes 2,3,4, XOR zero is witnessed;
- exactly 60 boundary cyclic orders: crossing count histogram
  0:8, 48:12, 60:24, 96:12, 108:4;
- forced good-safe matching taxonomy 252 unique, 72 ambiguous;
- full DFS physical relation of explicit n14 singleton-bit gadget=36;
- n10 example of bridge-side colour-transfer (C6+diamond pendant)
  preserves exactly all 63 physical C6 boundary states.

LIMIT: Universal full Exact-One sixpole impossibility OPEN.
Native PC degree lower bounds and SolveLinearCubicXSAT OPEN; P vs NP OPEN.
"""
from collections import Counter
from itertools import combinations, permutations, product

from r5_universal_portfree_two_three_edge_cut_exact_signature_retraction import (
    assert_simple_cubic_multipole, colour_states, connected,
    graph_cycle6, norm
)
from r5_universal_four_cut_11_signature_substitution import templates

PAIRS=((0,1),(2,3),(4,5))
COLOURS=(0,1,2)
GOOD={"100","010","001"}
CODE={0:1,1:2,2:3}


def truth(p):
    return ''.join(str(int(p[u]==p[v])) for u,v in PAIRS)


def target_states():
    return frozenset(p for p in product(COLOURS,repeat=6)
       if all(p.count(c)%2==0 for c in COLOURS) and truth(p) in GOOD)


def endpoint_matchings(indices):
    indices=tuple(indices)
    if not indices:
        yield ()
    else:
        i=indices[0]
        for j in range(1,len(indices)):
            for rest in endpoint_matchings(indices[1:j]+indices[j+1:]):
                yield ((i,indices[j]),)+rest


def switch(p,colour_pair,ends):
    a,b=colour_pair
    i,j=ends
    assert p[i] in colour_pair and p[j] in colour_pair
    q=list(p)
    q[i]=a+b-q[i]
    q[j]=a+b-q[j]
    return tuple(q)


def legal_safe_matchings(p,pair):
    terminals=[i for i,c in enumerate(p) if c in pair]
    legal=[]
    for matching in endpoint_matchings(terminals):
        reachable={p}
        for ends in matching:
            reachable |= {switch(t,pair,ends) for t in tuple(reachable)}
        if all(truth(t) in GOOD for t in reachable):
            legal.append(matching)
    return tuple(legal)


def crossing(matching,order):
    position={a:i for i,a in enumerate(order)}
    for e,f in combinations(matching,2):
        a,b=sorted(position[i] for i in e)
        c,d=sorted(position[i] for i in f)
        if (a<c<b<d) or (c<a<d<b):
            return True
    return False


def pair_consecutive_in_order(pair,order):
    a,b=pair
    i,j=order.index(a),order.index(b)
    return (i-j)%6 in (1,5)


def all_size_boundary_certificates():
    states=target_states()
    assert len(states)==108
    assert Counter(map(truth,states))==Counter({"100":36,"010":36,"001":36})
    for k in (2,3,4):
        for subset in combinations(range(6),k):
            witnesses=[p for p in states if
                       (CODE[p[subset[0]]] ^
                        (0 if k==1 else CODE[p[subset[1]]]) ^
                        (0 if k<3 else CODE[p[subset[2]]]) ^
                        (0 if k<4 else CODE[p[subset[3]]]))==0]
            assert witnesses,subset
    for i,j in combinations(range(6),2):
        assert any(s[i]==s[j] for s in states)
        assert any(s[i]!=s[j] for s in states)
    print("BRIDGE_ZERO_FLOW_WITNESS_ALL_15_20_15_PORT_SUBSETS PASS")
    print("ALL_15_PHYSICAL_PORT_PAIRS_ALLOW_EQUAL_AND_UNEQUAL PASS")
    print("MINIMUM_FULL_EXACTONE_CUBIC_SIXPOLE_MUST_BE_BRIDGELESS PROVED")

    forced=[]
    histogram=Counter()
    for state in states:
        for pair in combinations(COLOURS,2):
            options=legal_safe_matchings(state,pair)
            assert len(options) in (1,5)
            histogram[len(options)]+=1
            if len(options)==1:
                forced.append((state,pair,options[0]))
    assert histogram==Counter({1:252,5:72}),histogram

    cyclic_hist=Counter()
    good_orders=[]
    bad_examples={}
    for tail in permutations(range(1,6)):
        order=(0,)+tail
        if order[1]>order[-1]:
            continue
        bad=[(s,pair,matching) for s,pair,matching in forced
             if crossing(matching,order)]
        cyclic_hist[len(bad)]+=1
        consecutive=all(pair_consecutive_in_order(pair,order) for pair in PAIRS)
        assert (len(bad)==0)==consecutive,(order,len(bad))
        if not bad:
            good_orders.append(order)
        else:
            bad_examples[order]=bad[0]
    assert len(good_orders)==8 and len(bad_examples)==52
    assert cyclic_hist==Counter({0:8,48:12,60:24,96:12,108:4}),cyclic_hist
    print("PLANAR_DISK_FORCED_KEMPE_CROSSING_HISTOGRAM",
          dict(sorted(cyclic_hist.items())),flush=True)
    print("EIGHT_SURVIVING_ORDERS_ALL_THREE_LOGICAL_PAIRS_CONSECUTIVE",good_orders)
    print("ALL_SIZE_PLANAR_ORDER_NECESSARY_NOT_SUFFICIENT PASS")


def real_singlebit_n14():
    atlas=templates()
    edgesA,rootsA=atlas["SIX_VERTEX_HETERO_TWO"]
    edgesB,rootsB=atlas["PETERSEN_MINUS_ADJACENT_TWO_ISO"]
    # Join original rootsA[1]=2 and rootsB[0]+6=6.
    nA=6
    E=set(norm(u,v) for u,v in edgesA)
    E.update(norm(u+nA,v+nA) for u,v in edgesB)
    E.add(norm(rootsA[1],rootsB[0]+nA))
    ports=tuple(r for i,r in enumerate(rootsA) if i!=1)+tuple(
        r+nA for i,r in enumerate(rootsB) if i!=0)
    assert ports==(1,4,5,8,9,10),ports
    vertices=assert_simple_cubic_multipole(E,ports)
    assert len(vertices)==14 and len(E)==18
    assert len(set(ports))==6
    assert connected(vertices,E)
    states,_=colour_states(E,ports)
    assert len(states)==36,(len(states),states)
    logical=((0,5),(1,2),(3,4))
    observed=Counter(''.join(str(int(s[a]==s[b])) for a,b in logical)
                     for s in states)
    assert observed==Counter({"001":36}),observed
    print("EXPLICIT_N14_CONNECTED_SIMPLE_SINGLE_ONEHOT_BIT_36",{
        "edges":tuple(sorted(E)),"port_roots":ports,
        "pairing":logical,"truth_hist":dict(observed),
    },flush=True)


def transfer_pendant_two_pole():
    """A colourable pendant cubic 2-pole transports any port colour."""
    core,ports=graph_cycle6()
    A,B,C,D=(6,7,8,9)
    E=set(core)
    E.update({
        norm(A,C),norm(A,D),norm(B,C),norm(B,D),
        norm(C,D),norm(0,B)
    })
    newports=(A,1,2,3,4,5)
    vertices=assert_simple_cubic_multipole(E,newports)
    assert len(vertices)==10 and connected(vertices,E)
    original,_=colour_states(core,ports)
    changed,_=colour_states(E,newports)
    assert changed==original and len(original)==63
    print("PENDANT_BRIDGE_1PLUS5_EXACT_SEMIPORT_TRANSFER_63 PASS")


def test():
    all_size_boundary_certificates()
    real_singlebit_n14()
    transfer_pendant_two_pole()
    print("FULL_EXACTONE_N14_NOT_CONSTRUCTED; ALL_SIZE_FULL_NO_GO_OPEN")
    print("SolveLinearCubicXSAT=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__=="__main__":
    test()
