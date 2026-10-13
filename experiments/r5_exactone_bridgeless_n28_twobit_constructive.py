#!/usr/bin/env python3
"""R5 breakthrough: PHYSICAL BRIDGELESS n28 GOOD-only TWO-BIT cubic sixpole.

Independent exhaustive proper edge-3-colouring verification:
- genuine simple connected cubic graph n28, 39 ordinary edges;
- six DISTINCT semiedge roots (1,4,6,9,17,23);
- no bridge in the ENTIRE physical ordinary-edge graph;
- full 3-edge-colourings: 144;
- distinct physical 6-port colour tuples: 72, each multiplicity 2;
- truth pairs on PORT INDICES ((0,5),(1,4),(2,3));
- bits exactly 100:36 and 010:36, zero forbidden/other states.

CONSTRUCTION:
Take the previously certified REAL n24 four-4pole K4-minus-edge
two-bit gadget. Its only actual physical bridge lies INSIDE a
6-vertex HETERO_TWO 4-pole. Independently find a BRIDGELESS connected
simple TEN-vertex 4-pole whose COMPLETE ORDERED 4-port colour relation
is IDENTICAL to that 6-vertex bridged block. Replace only that one
block, preserving interface port order. The resulting n28 graph is
physically bridgeless, and its full exact sixport relation is unchanged.

FINITE MINIMALITY of replacement: independently exhaust ALL labelled
simple cubic 4-poles of n4,6,8 with 4 distinct outer roots (ordinary
degrees 2x4 and 3x(n-4)); counts 3,54,6057. None of their BRIDGELESS
realizations has the HETERO_TWO two-orbit signature, up to all port
permutations. The explicit ten-vertex example is thus minimum order
among such bridgeless physical replacements. This is not a universal
statement about sixpole gadget sizes.

NO FULL THREE-BIT EXACT-ONE: the third bit 001 remains absent.
Universal polynomial SolveLinearCubicXSAT NOT CONSTRUCTED; P vs NP OPEN.
"""
from collections import Counter
from itertools import combinations


HETERO_EDGES = (
    (0,1),(0,2),(0,3),(1,2),(3,4),(3,5),(4,5)
)
HETERO_ROOTS = (1,2,4,5)

BRIDGELESS_FOUR_EDGES = (
    (0,1),(0,4),(1,5),(2,6),(2,7),(3,6),(3,8),
    (4,7),(4,9),(5,8),(5,9),(6,9),(7,8)
)
BRIDGELESS_FOUR_ROOTS = (0,3,1,2)

SIX_LOGICAL_PAIRS = ((0,5),(1,4),(2,3))
GOOD={"100","010","001"}

EXPECTED_N28_ROOTS=(1,4,6,9,17,23)
EXPECTED_N28_EDGES=(
    (0,1),(0,2),(0,3),(1,2),(2,20),(3,4),(3,5),
    (4,5),(5,26),(6,7),(6,10),(7,11),(7,21),(8,12),
    (8,13),(8,27),(9,12),(9,14),(10,13),(10,15),
    (11,14),(11,15),(12,15),(13,14),(16,17),(16,18),
    (16,19),(17,18),(18,24),(19,20),(19,21),(20,21),
    (22,23),(22,24),(22,25),(23,24),(25,26),(25,27),
    (26,27)
)
FOUR_ORBITS={
    (0,0,0,0):1,
    (0,0,1,1):2,
    (0,1,0,1):4,
    (0,1,1,0):8
}


def connected(edges,n):
    adj=[[] for _ in range(n)]
    for u,v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen={0}
    todo=[0]
    for u in todo:
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                todo.append(v)
    return len(seen)==n


def find_bridges(edges,n):
    return tuple(e for e in edges if not connected(
        tuple(f for f in edges if f!=e),n))


def validate_physical(edges,roots):
    n=max(max(e) for e in edges)+1
    assert set(v for e in edges for v in e)==set(range(n))
    assert len(set(roots))==len(roots)
    assert len(set(edges))==len(edges)
    assert all(u<v for u,v in edges)
    deg=Counter(v for edge in edges for v in edge)
    assert all(deg[v]==(2 if v in roots else 3) for v in range(n))
    assert 2*len(edges)+len(roots)==3*n
    assert connected(edges,n)
    return n


def all_physical_colours(edges,roots):
    """Independent full DFS: enumerate EVERY internal edge colouring."""
    n=validate_physical(edges,roots)
    used=[0]*n
    mask_all=(1<<len(edges))-1
    out=Counter()

    def search(done=0):
        if done==mask_all:
            physical=tuple((7^used[v]).bit_length()-1 for v in roots)
            assert all(0<=c<3 for c in physical)
            out[physical]+=1
            return
        best=None
        min_options=4
        options=0
        for k,(u,v) in enumerate(edges):
            if done&(1<<k):
                continue
            valid=7&~(used[u]|used[v])
            count=valid.bit_count()
            if count==0:
                return
            if count<min_options:
                best=k
                min_options=count
                options=valid
                if count==1:
                    break
        assert best is not None
        u,v=edges[best]
        for c in (1,2,4):
            if options&c:
                used[u]^=c
                used[v]^=c
                search(done|(1<<best))
                used[u]^=c
                used[v]^=c

    search()
    return out


def boundary_orbit_mask(states):
    result=0
    for physical in states:
        ren={}
        canonical=tuple(ren.setdefault(c,len(ren))
                        for c in physical)
        assert canonical in FOUR_ORBITS
        result |= FOUR_ORBITS[canonical]
    return result


def labelled_graphs_with_degrees(degrees):
    """Independent exhaustive graph generator, one graph per edge set."""
    n=len(degrees)

    def extend(u,rem,edges):
        if u==n:
            if not any(rem):
                yield tuple(sorted(edges))
            return
        if rem[u]==0:
            yield from extend(u+1,rem,edges)
            return
        later=[v for v in range(u+1,n) if rem[v]>0]
        for chosen in combinations(later,rem[u]):
            after=list(rem)
            after[u]=0
            for v in chosen:
                after[v]-=1
            yield from extend(
                u+1,tuple(after),
                edges+tuple((u,v) for v in chosen)
            )
    yield from extend(0,tuple(degrees),())


def check_minimum_replacement():
    """No bridgeless hetero 2-orbit 4-pole has n=4,6,8."""
    # Port permutations of class mask 12 form the three masks below.
    hetero_class_orbits={6,10,12}
    expected={4:3,6:54,8:6057}
    counts={}
    for n in (4,6,8):
        total=0
        bridgeless_hetero=0
        for e in labelled_graphs_with_degrees(
                (2,)*4+(3,)*(n-4)):
            total+=1
            if not connected(e,n) or find_bridges(e,n):
                continue
            mask=boundary_orbit_mask(
                all_physical_colours(e,(0,1,2,3))
            )
            if mask in hetero_class_orbits:
                bridgeless_hetero+=1
        assert total==expected[n],(n,total)
        assert bridgeless_hetero==0,(n,bridgeless_hetero)
        counts[n]=total
    print("MINIMAL_BRIDGELESS_HETERO_4POLE_N10",{
        "fully_enumerated_n4_n6_n8":counts,
        "bridgeless_hetero_orbit_classes_found":0
    },flush=True)


def build_k4minus_two_bit(use_bridgeless_B):
    """Create original n24 or improved n28 physical assembly."""
    A=(HETERO_EDGES,tuple(HETERO_ROOTS[i] for i in (0,2,1,3)))
    B=((BRIDGELESS_FOUR_EDGES,BRIDGELESS_FOUR_ROOTS)
       if use_bridgeless_B
       else (HETERO_EDGES,HETERO_ROOTS))
    C=(HETERO_EDGES,tuple(HETERO_ROOTS[i] for i in (0,2,3,1)))
    D=C
    current=0
    edges=set()
    outer=[]
    for inner,ports in (A,B,C,D):
        n=validate_physical(tuple(sorted(inner)),ports)
        edges.update(tuple(sorted((u+current,v+current)))
                     for u,v in inner)
        outer.append(tuple(p+current for p in ports))
        current+=n
    pa,pb,pc,pd=outer
    interfaces=(
        (pa[2],pc[1]),(pa[3],pd[1]),
        (pb[2],pc[2]),(pb[3],pd[2]),
        (pc[3],pd[3])
    )
    edges.update(tuple(sorted(e)) for e in interfaces)
    physical_ports=pa[:2]+pb[:2]+pc[:1]+pd[:1]
    out=tuple(sorted(edges))
    assert validate_physical(out,physical_ports)==current
    return out,physical_ports


def bits(s):
    return "".join(str(int(s[a]==s[b]))
                   for a,b in SIX_LOGICAL_PAIRS)


def run():
    assert validate_physical(
        BRIDGELESS_FOUR_EDGES,BRIDGELESS_FOUR_ROOTS)==10
    assert not find_bridges(BRIDGELESS_FOUR_EDGES,10)
    old_four=all_physical_colours(HETERO_EDGES,HETERO_ROOTS)
    new_four=all_physical_colours(
        BRIDGELESS_FOUR_EDGES,BRIDGELESS_FOUR_ROOTS)
    assert len(old_four)==len(new_four)==12
    assert sum(old_four.values())==12
    assert sum(new_four.values())==24
    assert set(old_four)==set(new_four)
    assert boundary_orbit_mask(new_four)==12
    assert set(new_four.values())=={2}
    print("TEN_VERTEX_BRIDGELESS_FOURPOLE_REPLACES_SIX_VERTEX_BRIDGED_SAME_RELATION PASS")

    n24,ports24=build_k4minus_two_bit(False)
    n28,ports28=build_k4minus_two_bit(True)
    assert len(n24)==33 and len(n28)==39
    assert ports28==EXPECTED_N28_ROOTS
    assert n28==EXPECTED_N28_EDGES
    assert find_bridges(n24,24)==((6,9),)
    assert not find_bridges(n28,28)
    original=all_physical_colours(n24,ports24)
    improved=all_physical_colours(n28,ports28)
    assert len(original)==len(improved)==72
    assert sum(original.values())==72
    assert sum(improved.values())==144
    assert set(original)==set(improved)
    assert set(original.values())=={1}
    assert set(improved.values())=={2}
    truth=Counter(bits(p) for p in improved)
    assert truth==Counter({"100":36,"010":36}),truth
    assert not set(truth)-GOOD
    check_minimum_replacement()
    print("ACTUAL_BRIDGELESS_N28_TWO_BIT_PHYSICAL_GADGET",{
        "vertices":28,
        "ordinary_edges":39,
        "ordered_ports":ports28,
        "logical_pairs":SIX_LOGICAL_PAIRS,
        "bridges":0,
        "distinct_physical_states":72,
        "full_internal_colourings":144,
        "fibre_size_for_every_physical_state":2,
        "bit_histogram":dict(truth),
        "forbidden":0,
    },flush=True)
    print("FIRST_TARGET_BRIDGE_ELIMINATION_COMPLETE")
    print("THIRD_BIT_001_NOT_REALIZED; FULL_108_GADGET_OPEN")
    print("SolveLinearCubicXSAT=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__=="__main__":
    run()
