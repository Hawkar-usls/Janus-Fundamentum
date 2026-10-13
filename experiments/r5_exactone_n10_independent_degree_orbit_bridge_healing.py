#!/usr/bin/env python3
"""R5 independent checks for exhaustive n10 and targeted bridge healing.

NO UNIVERSAL n>=12 statement.

(a) Independent exact transfer-DP counts 888292 labelled SIMPLE graphs
    with degree vector (2,2,2,2,2,2,3,3,3,3), WITHOUT using the
    edge-by-edge exhaustive C++ generator.
(b) The labelled graph orbit of the REAL previously verified n10
    two-bit GOOD-only witness under all 48 logical-root pair
    permutations/swaps and 24 permutations of four nonroots has
    exactly 144 DISTINCT members. The independent C++ exhaustive
    census finds exactly 144 GOOD-only n10 graphs, proving all such
    graphs lie in this ONE orbit (conditional on both exact checks).
(c) Among all 72 distinct connected simple two-edge switches from the
    original physical n10 source, NONE preserves its two-bit GOOD-only
    signature without its bridge. We independently enumerate the
    whole physical proper edge-colouring boundary relation.
(d) Genuine Diamond rank-preserving insertion then ONE bridge-healing
    cross-shore two-edge switch: n14 1060 physically bridgeless
    construction attempts (11 permitted insertion edges); n18 9908
    attempts (all 55 pairs of distinct permitted insertion edges).
    EACH admits a full proper colouring with a FORBIDDEN equality bit.
    Colourability witnesses can be found with a one-colour pin on the
    first chosen internal edge by global S3 colour symmetry. The
    pinned search is complete for EXISTENCE of a forbidden bit.

The 1060 / 9908 attempts are NOT claimed pairwise nonisomorphic or a
complete enumeration of all n14/n18 sixpoles: this is a finite
normal-form search under two Diamond inflations and ONE cross-shore
edge switch from ONE fixed n10 starting graph. No all-n no-go.

The physical full 108-state gadget and native general solver remain
NOT CONSTRUCTED; P versus NP remains OPEN.
"""
from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations, product


SOURCE_EDGES = tuple(sorted((
    (0,1),(0,6),(1,5),(2,4),(2,5),(3,5),
    (3,6),(3,9),(4,6),(7,8),(7,9),(8,9)
)))
SOURCE_ROOTS=(0,1,2,4,7,8)
SOURCE_PAIRS=((0,2),(1,3),(4,5))
BRIDGE=(3,9)
GOOD=frozenset(("100","010","001"))

# The same physical graph independently relabelled to roots 0..5
# and canonical logical pairs (0,1),(2,3),(4,5).
NORMALIZED_N10=tuple(sorted((
    (0,2),(0,8),(1,3),(1,7),(2,7),(3,8),
    (4,5),(4,9),(5,9),(6,7),(6,8),(6,9)
)))


@lru_cache(None)
def degree_graph_count(next_vertex, remaining):
    """Independent transfer-DP, one simple undirected edge set each."""
    if next_vertex==10:
        return int(not any(remaining))
    degree=remaining[next_vertex]
    if degree==0:
        return degree_graph_count(next_vertex+1,remaining)
    available=tuple(i for i in range(next_vertex+1,10)
                    if remaining[i]>0)
    if len(available)<degree:
        return 0
    result=0
    for neighbours in combinations(available,degree):
        updated=list(remaining)
        updated[next_vertex]=0
        for j in neighbours:
            updated[j]-=1
        result+=degree_graph_count(next_vertex+1,tuple(updated))
    return result


def rooted_orbit_size():
    """Permute logical pairs, swap within pairs, permute 4 nonroots."""
    orbit=set()
    for outer in permutations(range(3)):
        for swap in product((0,1),repeat=3):
            roots={}
            for i in range(3):
                roots[2*i]=2*outer[i]+swap[i]
                roots[2*i+1]=2*outer[i]+1-swap[i]
            for inner in permutations(range(6,10)):
                change=dict(roots)
                change.update({6+i:inner[i] for i in range(4)})
                candidate=tuple(sorted(tuple(sorted(
                    (change[u],change[v]))) for u,v in NORMALIZED_N10))
                orbit.add(candidate)
    return len(orbit)


def connected(edges,n):
    neighbours=[[] for _ in range(n)]
    for u,v in edges:
        neighbours[u].append(v)
        neighbours[v].append(u)
    visited={0}
    queue=[0]
    for u in queue:
        for v in neighbours[u]:
            if v not in visited:
                visited.add(v)
                queue.append(v)
    return len(visited)==n


def bridges(edges,n):
    return [e for e in edges if not connected(
        [other for other in edges if other!=e],n)]


def edge_switches(edges):
    """ALL simple 2-edge endpoint interchanges, canonically deduped."""
    source=set(edges)
    outputs=set()
    for (a,b),(c,d) in combinations(edges,2):
        if len({a,b,c,d})!=4:
            continue
        for candidates in (((a,c),(b,d)),((a,d),(b,c))):
            replacements={tuple(sorted(e)) for e in candidates}
            if len(replacements)!=2 or replacements & source:
                continue
            outputs.add(tuple(sorted(
                source-{(a,b),(c,d)}|replacements)))
    return outputs


def colouring_bits(edges,roots=SOURCE_ROOTS,pairs=SOURCE_PAIRS,
                  stop_at_forbidden=True):
    """True proper cubic edge 3-colouring DFS, with safe global S3 pin.

    When stop_at_forbidden, a pinned reference edge has colour 0;
    any proper colouring (forbidden or allowed) can have one internal
    edge recoloured to 0 by a global colour name permutation, leaving
    ALL boundary equality bits invariant. Thus a forbidden witness
    is never lost by this speed-up.
    """
    n=max(max(e) for e in edges)+1
    incidence=[0]*n
    for u,v in edges:
        incidence[u]+=1
        incidence[v]+=1
    rootset=set(roots)
    assert len(rootset)==6
    assert all(incidence[v]==(2 if v in rootset else 3)
               for v in range(n))
    used=[0]*n
    histogram=Counter()
    forbidden=False
    endmask=(1<<len(edges))-1

    def recurse(done):
        nonlocal forbidden
        if forbidden and stop_at_forbidden:
            return
        if done==endmask:
            outside=tuple((7^used[v]).bit_length()-1 for v in roots)
            value="".join(str(int(outside[u]==outside[v]))
                          for u,v in pairs)
            histogram[value]+=1
            if value not in GOOD:
                forbidden=True
            return
        chosen=None
        minoptions=4
        allowed=0
        for i,(u,v) in enumerate(edges):
            if done&(1<<i):
                continue
            possible=7&~(used[u]|used[v])
            nc=possible.bit_count()
            if nc==0:
                return
            if nc<minoptions:
                chosen=i
                minoptions=nc
                allowed=possible
                if nc==1:
                    break
        assert chosen is not None
        u,v=edges[chosen]
        options=([allowed&-allowed] if done==0 else
                 [1<<k for k in range(3) if allowed&(1<<k)])
        for colour in options:
            used[u]^=colour
            used[v]^=colour
            recurse(done|(1<<chosen))
            used[u]^=colour
            used[v]^=colour
            if forbidden and stop_at_forbidden:
                return

    recurse(0)
    return histogram,forbidden


def diamond(edges,to_replace,new_start):
    u,v=to_replace
    assert to_replace in edges
    a,b,c,d=range(new_start,new_start+4)
    insert=((u,a),(v,b),(a,c),(a,d),(b,c),(b,d),(c,d))
    return tuple(sorted((set(edges)-{to_replace})|
                        {tuple(sorted(e)) for e in insert}))


def no_bridge_heal_after_diamonds(max_diamonds):
    """One shore-crossing two-edge switch after rank-preserving inserts."""
    original_A=set(range(7))
    original_B=set(range(7,10))
    expandable=tuple(e for e in SOURCE_EDGES if e!=BRIDGE)
    insertion_sets=(
        ((e,),) for e in expandable
    ) if max_diamonds==1 else (
        (es,) for es in combinations(expandable,2)
    )
    attempts=0
    for (insertion_edges,) in insertion_sets:
        expanded=SOURCE_EDGES
        A=set(original_A)
        B=set(original_B)
        for i,e in enumerate(insertion_edges):
            start=10+4*i
            expanded=diamond(expanded,e,start)
            (A if e[0] in original_A else B).update(
                range(start,start+4))
        side_A=tuple(e for e in expanded if set(e)<=A)
        side_B=tuple(e for e in expanded if set(e)<=B)
        n=10+4*max_diamonds
        for eA in side_A:
            for eB in side_B:
                a,b=eA
                c,d=eB
                for raw in (((a,c),(b,d)),((a,d),(b,c))):
                    replacement={tuple(sorted(e)) for e in raw}
                    candidate=tuple(sorted(
                        (set(expanded)-{eA,eB})|replacement))
                    if len(candidate)!=len(expanded):
                        continue
                    if bridges(candidate,n):
                        continue
                    attempts+=1
                    _,bad=colouring_bits(candidate)
                    assert bad, (
                        "FOUND NEW BRIDGELESS GOODONLY CANDIDATE",
                        insertion_edges,eA,eB,candidate
                    )
    expected=1060 if max_diamonds==1 else 9908
    assert attempts==expected,(max_diamonds,attempts,expected)
    return attempts


def triangle_expansion(edges,vertex,next_start):
    """Replace unmarked trivalent vertex by a 3-cycle (+2 vertices).

    Each original incident edge connects to a different corner of the
    triangle, so all 3 outer incident colours must differ exactly as
    at the old vertex. Every proper colouring extends uniquely,
    preserving the COMPLETE original sixport physical colour relation.
    """
    neighbours=sorted(v if u==vertex else u
                      for u,v in edges if vertex in (u,v))
    assert len(neighbours)==3
    a,b=next_start,next_start+1
    removed={tuple(sorted((vertex,w))) for w in neighbours}
    added={(vertex,a),(vertex,b),(a,b)}
    added |= {tuple(sorted((vertex,neighbours[0]))),
              tuple(sorted((a,neighbours[1]))),
              tuple(sorted((b,neighbours[2])))}
    return tuple(sorted(set(edges)-removed|added))


def no_bridge_heal_after_triangle_expansions():
    """Check all expansion sequences of 1,2,3 marked-free vertices.

    n12: 4 labelled expansion histories, 278 bridgeless repairs
    n14: 24 histories, 2388 repairs
    n16: 192 histories, 25728 repairs
    Different histories/repairs need not be nonisomorphic; the grammar
    is EXACTLY 'triangle vertex inflations then ONE cross-shore
    two-edge switch', not all graphs of corresponding size.
    """
    states=[(SOURCE_EDGES,set(range(7)),set(range(7,10)),10,())]
    expected=((4,278),(24,2388),(192,25728))
    for level,(expected_histories,expected_attempts) in enumerate(expected,1):
        successors=[]
        checked=0
        for edges,A,B,n,history in states:
            deg=Counter(v for edge in edges for v in edge)
            possible=tuple(v for v in range(n)
                           if v not in SOURCE_ROOTS and deg[v]==3)
            for vertex in possible:
                new_edges=triangle_expansion(edges,vertex,n)
                next_A=set(A);next_B=set(B)
                (next_A if vertex in A else next_B).update(
                    (n,n+1))
                successors.append((
                    new_edges,next_A,next_B,n+2,history+(vertex,)
                ))
                inner_A=[e for e in new_edges if set(e)<=next_A]
                inner_B=[e for e in new_edges if set(e)<=next_B]
                for eA in inner_A:
                    for eB in inner_B:
                        a,b=eA
                        c,d=eB
                        for cross in (((a,c),(b,d)),((a,d),(b,c))):
                            additions={tuple(sorted(e)) for e in cross}
                            candidate=tuple(sorted(
                                (set(new_edges)-{eA,eB})|additions
                            ))
                            if len(candidate)!=len(new_edges):
                                continue
                            if bridges(candidate,n+2):
                                continue
                            checked+=1
                            _,forbidden=colouring_bits(candidate)
                            assert forbidden,(
                                "BRIDGELESS GOODONLY AFTER TRIANGLE HEALING",
                                level,history,vertex,eA,eB,candidate
                            )
        assert len(successors)==expected_histories
        assert checked==expected_attempts,(
            level,len(successors),checked,expected_attempts
        )
        print("TRIANGLE_INFLATION_DEPTH",level,
              "HISTORIES",len(successors),
              "BRIDGELESS_HEALING_ATTEMPTS",checked,
              "ALL_HAVE_FORBIDDEN_COLOURING PASS",flush=True)
        states=successors


def test():
    assert degree_graph_count(0,(2,)*6+(3,)*4)==888292
    assert rooted_orbit_size()==144
    print("INDEPENDENT_N10_DEGREE_SEQUENCE_COUNT_888292 PASS",flush=True)
    print("ROOT_PAIR_AND_INNER_PERM_N10_TWO_BIT_ORBIT_144 PASS",flush=True)

    signature,bad=colouring_bits(SOURCE_EDGES,stop_at_forbidden=False)
    assert not bad
    assert signature==Counter({"100":12,"010":12}),signature
    # The colour-0 pin removes a factor exactly three; restoring all
    # three choices of the first internal edge gives 72 full colourings.
    assert 3*sum(signature.values())==72
    switches=edge_switches(SOURCE_EDGES)
    assert len(switches)==72
    counts=Counter()
    for candidate in switches:
        bridged=bool(bridges(candidate,10))
        bits,bad=colouring_bits(candidate,stop_at_forbidden=False)
        assert bad
        counts[(bridged,tuple(sorted(bits)))] += 1
    assert counts==Counter({
        (False,("000","001","010","100","111")):36,
        (True,("000","010","100")):28,
        (False,("001","010","100","111")):8,
    }),counts
    print("ALL_72_IMMEDIATE_EDGE_SWITCHES_FAIL_GOODONLY",dict(counts),flush=True)

    no_bridge_heal_after_triangle_expansions()
    for k in (1,2):
        n=no_bridge_heal_after_diamonds(k)
        print("DIAMOND_INSERTIONS",k,"BRIDGELESS_HEALING_ATTEMPTS",n,
              "ALL_CONTAIN_FORBIDDEN_BIT PASS",flush=True)

    print("N10_FULL_EXHAUSTIVE_CENSUS_REQUIRES_COMPANION_CPP")
    print("N14_N18_TARGETED_GRAMMAR_NOT_ALL_GRAPHS")
    print("FULL_108_EXACTONE_OPEN; SolveLinearCubicXSAT_NOT_CONSTRUCTED; P_VS_NP_OPEN")


if __name__=="__main__":
    test()
