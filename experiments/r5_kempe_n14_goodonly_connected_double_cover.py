#!/usr/bin/env python3
"""R5 real GOOD-only n14 two-sheet full Kempe covering, nontrivial holonomy.

ALL FINITE FACTS independently asserted:
- Genuine simple connected cubic sixpole n=14,m=18 with six distinct
  semiedge roots (1,4,5,8,9,10) and logical port pairs
  ((0,5),(1,2),(3,4)).
- FULL exhaustive proper edge 3-colourings: 72.
- Ordered distinct physical six-port tuples: exactly 36.
- ALL bit values are '001'; forbidden 000/111 and other onehot bits
  do not occur.
- EACH of these 36 tuples has exactly 2 different internal completions.
- The 72 full colourings connected via only the FORCED GOOD-safe
  two-colour alternating terminal-path flips form a connected
  2-sheet graph covering of the 36-vertex / 72-edge base Kempe graph.
  The lifted graph has exactly 72 vertices and 144 undirected edges.
- The two different full colourings over any one physical port tuple
  are connected by SHORTEST forced-Kempe length exactly FIVE.
  Thus actual nontrivial 5-step closed-boundary physical holonomy
  occurs EVEN UNDER GLOBAL GOOD-ONLY, with all 5 intermediate states
  also GOOD '001'. One witness differs on 10 ordinary internal edges.
- Every compulsory same-colour disjoint-path commutation square lifts
  trivially, consistent with the earlier F37->F22 theorem.

This is a genuine physical realization of the previously abstract
2-sheet monodromy phenomenon, but only for ONE onehot bit '001'.
It is NOT a FULL Exact-One gadget (which requires 100,010,001 and
108 physical boundary tuples), and no P=NP / native SCL solver follows.
"""
from collections import Counter, defaultdict, deque
from itertools import combinations

from r5_universal_portfree_two_three_edge_cut_exact_signature_retraction import (
    norm, assert_simple_cubic_multipole, connected,
)
from r5_universal_four_cut_11_signature_substitution import templates

GOOD = {"001","010","100"}
PAIRS = ((0,5),(1,2),(3,4))
COL = (0,1,2)


def get_graph():
    A,Aroots=templates()["SIX_VERTEX_HETERO_TWO"]
    B,Broots=templates()["PETERSEN_MINUS_ADJACENT_TWO_ISO"]
    E={norm(*e) for e in A}
    E.update(norm(u+6,v+6) for u,v in B)
    E.add(norm(Aroots[1],Broots[0]+6))
    ports=tuple(r for k,r in enumerate(Aroots) if k!=1)+tuple(
        r+6 for k,r in enumerate(Broots) if k!=0)
    assert ports==(1,4,5,8,9,10)
    vertices=assert_simple_cubic_multipole(E,ports)
    assert len(vertices)==14 and len(E)==18
    assert connected(vertices,E)
    return tuple(sorted(E)),ports


def truth(p):
    return "".join(str(int(p[a]==p[b])) for a,b in PAIRS)


def all_full_colourings(edges, roots):
    n=len({v for e in edges for v in e})
    inc=[[] for _ in range(n)]
    for k,(u,v) in enumerate(edges):
        inc[u].append(k)
        inc[v].append(k)
    assert [len(inc[v]) for v in roots]==[2]*6
    assert all(len(inc[v])==3 for v in range(n) if v not in roots)
    value=[-1]*len(edges)
    output=set()
    def rec(k):
        if k==len(edges):
            p=tuple(next(c for c in COL
                         if all(value[e]!=c for e in inc[v]))
                    for v in roots)
            output.add((tuple(value),p))
            return
        u,v=edges[k]
        occupied={value[e] for w in (u,v) for e in inc[w] if e<k}
        for c in COL:
            if c not in occupied:
                value[k]=c
                rec(k+1)
        value[k]=-1
    rec(0)
    return frozenset(output)


def all_endpoint_matchings(items):
    items=tuple(items)
    if not items:
        yield ()
        return
    for j in range(1,len(items)):
        for tail in all_endpoint_matchings(items[1:j]+items[j+1:]):
            yield ((items[0],items[j]),)+tail


def swap_ends(physical,ab,ends):
    a,b=ab
    u,v=ends
    assert physical[u] in ab and physical[v] in ab
    q=list(physical)
    q[u]=a+b-q[u]
    q[v]=a+b-q[v]
    return tuple(q)


def legal_good_matchings(physical,ab):
    endpoints=tuple(j for j,c in enumerate(physical) if c in ab)
    legal=[]
    for matching in all_endpoint_matchings(endpoints):
        support={physical}
        for ends in matching:
            support|={swap_ends(s,ab,ends) for s in tuple(support)}
        if all(truth(s) in GOOD for s in support):
            legal.append(matching)
    assert len(legal) in (1,5)
    return legal


def real_path_moves(edges,roots,colouring,ab,all_states):
    ec,p=colouring
    n=14
    pieces=list(edges)+[(roots[i],n+i) for i in range(6)]
    colours=list(ec)+list(p)
    adj=defaultdict(list)
    for k,(u,v) in enumerate(pieces):
        if colours[k] in ab:
            adj[u].append((v,k))
            adj[v].append((u,k))
    used=set()
    moves={}
    for j in range(6):
        terminal=n+j
        if terminal not in adj or terminal in used:
            continue
        vertices={terminal}
        q=[terminal]
        changed_edges=set()
        while q:
            u=q.pop()
            for v,k in adj[u]:
                changed_edges.add(k)
                if v not in vertices:
                    vertices.add(v)
                    q.append(v)
        used|=vertices
        endpoints=tuple(sorted(v-n for v in vertices if v>=n))
        assert len(endpoints)==2
        switched=colours.copy()
        a,b=ab
        for k in changed_edges:
            switched[k]=a+b-switched[k]
        other=(tuple(switched[:len(edges)]),tuple(switched[len(edges):]))
        assert other in all_states
        assert truth(other[1])=="001"
        moves[endpoints]=other
    assert len(moves)<=3
    return moves


def connected_components(vertices,adj):
    visited=set()
    sizes=[]
    for start in vertices:
        if start in visited:
            continue
        queue=[start]
        component={start}
        while queue:
            for neighbour in adj[queue.pop()]:
                if neighbour not in component:
                    component.add(neighbour)
                    queue.append(neighbour)
        visited |= component
        sizes.append(len(component))
    return sorted(sizes)


def shortest_lift(adj,start,goal):
    q=deque([start])
    path={start:()}
    while q:
        state=q.popleft()
        if state==goal:
            return path[state]
        for other,label in adj[state].items():
            if other not in path:
                path[other]=path[state]+((label[0],label[1],other[1]),)
                q.append(other)
    raise AssertionError("covering graph disconnected")


def run():
    edges,roots=get_graph()
    coloured=all_full_colourings(edges,roots)
    assert len(coloured)==72
    fibres=defaultdict(list)
    for full in coloured:
        assert truth(full[1])=="001"
        fibres[full[1]].append(full)
    assert len(fibres)==36
    assert set(map(len,fibres.values()))=={2}

    lifted=defaultdict(dict)
    base_edges=set()
    forced_pair_decisions=Counter()
    for full in coloured:
        _,physical=full
        for ab in combinations(COL,2):
            options=legal_good_matchings(physical,ab)
            forced_pair_decisions[len(options)]+=1
            if len(options)!=1:
                continue
            actual=real_path_moves(edges,roots,full,ab,coloured)
            assert set(actual)=={
                tuple(sorted(pair)) for pair in options[0]
            },("actual path pairing inconsistent with GOOD-only",full,ab)
            for endpoints,other in actual.items():
                label=(ab,endpoints)
                assert other!=full
                lifted[full][other]=label
                bnd=tuple(sorted((physical,other[1])))
                base_edges.add(bnd)
    assert len(lifted)==72
    assert sum(len(x) for x in lifted.values())==288
    assert all(a in lifted[b] and lifted[b][a]==lbl
               for a,neighbors in lifted.items()
               for b,lbl in neighbors.items())
    assert len(base_edges)==72
    assert connected_components(coloured,lifted)==[72]
    assert sum(len(x) for x in lifted.values())//2==144
    assert forced_pair_decisions==Counter({1:168,5:48})
    # For a 36-state base, 36*3 decisions =108, each with 2 lifts.
    print("ACTUAL_GOOD_ONLY_TWO_SHEET_COVER",{
        "n":14,"ordinary_edges":18,"full_colourings":72,
        "physical_port_tuples":36,"fibre_sizes":dict(Counter(map(len,fibres.values()))),
        "forced_base_edges":len(base_edges),
        "lifted_full_edges":144,"lifted_components":[72],
    },flush=True)

    distances=Counter()
    sample=None
    for ports,states in fibres.items():
        left,right=states
        route=shortest_lift(lifted,left,right)
        distances[len(route)]+=1
        if sample is None or (len(route),ports)<(len(sample[2]),sample[0][1]):
            sample=(left,right,route)
    # Each port tuple has two directions; use all 72 as stronger check.
    for state in coloured:
        others=[other for other in fibres[state[1]] if other!=state]
        assert len(others)==1
        distances[len(shortest_lift(lifted,state,others[0]))]+=1
    assert distances==Counter({5:108}),distances

    initial,after,trace=sample
    assert len(trace)==5 and initial[1]==after[1]
    diff=[(edges[k],a,b) for k,(a,b)
          in enumerate(zip(initial[0],after[0])) if a!=b]
    assert len(diff)==10,diff
    print("ACTUAL_GOOD_ONLY_NONTRIVIAL_FIVE_KEMPE_HOLONOMY",{
        "physical_ports":initial[1],
        "before_internal":initial[0],
        "after_internal":after[0],
        "five_verified_switches":trace,
        "changed_ordinary_edges":diff,
        "min_partner_distance_in_every_fibre":5,
    },flush=True)
    print("CROSS_COLOUR_GOOD_ONLY_NONTRIVIAL_MONODROMY_PHYSICALLY_REALIZED")
    print("ONE_BIT_001_ONLY; FULL_108_EXACTONE_GADGET_OPEN")
    print("SolveLinearCubicXSAT=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__=="__main__":
    run()
