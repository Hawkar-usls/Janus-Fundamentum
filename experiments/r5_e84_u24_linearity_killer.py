#!/usr/bin/env python3
"""R5 E84: direct U2,4 / S5 linearity killer.

E83 reduced binary representability of an exact Tanner delta interface to the
ordinary matroid obstruction U_{2,4}. E84 attacks the strongest *direct*
four-boundary realization inside the square-cubic-linear / C4-free source
class.

Structural reduction proved in the companion note:

If a connected induced C4-free cubic Tanner cluster has exactly four free
boundary coordinates and its exact boundary relation is the S5 relation

    {0000, 0101, 0110, 1001, 1010, 1111},

with two check-side and two variable-side coordinates, then necessarily:

  * |C|=|V|=3t for some t>=2;
  * the four boundary coordinates lie on four distinct degree-2 Tanner
    vertices (two checks, two variables); every other Tanner vertex has
    internal degree 3;
  * using the all-one boundary state as a reference exact cover, the 2t
    unselected internal variables become the vertices of a SIMPLE CUBIC
    residual-exchange graph G; Tanner checks become the 3t edges of G;
  * G need not be connected: reference-cover variables may connect distinct
    residual components in the original Tanner cluster;
  * the two boundary checks are two distinguished edges of G;
  * the two boundary variables are two 2-edge matchings of G;
  * the remaining t-2 reference-cover variables are 3-edge matchings; these
    blocks partition every non-distinguished edge of G.

Thus direct S5 realizability is reduced exactly to a finite simple-cubic-graph
plus matching-partition problem.

This checker exhausts every such partition for ALL simple cubic residual
 topologies on 2t=4,6,8 vertices. The connected census has sizes 1,2,5; at
8 vertices there is one additional disconnected topology K4 disjoint-union K4.
Hence the complete topology counts used here are 1,2,6. This covers every
direct candidate with |C|=|V|=6,9,12. Frozen total = 106,090 matching
partitions. No S5 relation occurs. Every delta relation that does occur is
binary-even.

Scientific ceiling:

  * DIRECT C4-free S5/U2,4 is excluded through 12x12 clusters.
  * This is NOT a proof for 15x15 and larger clusters.
  * This does NOT exclude U2,4 appearing only after conditioning/minors of a
    larger boundary matroid.
  * It does NOT repair the static-partition obstruction E81.
  * P_VS_NP remains OPEN.
"""

from collections import Counter
from itertools import combinations

from r5_e77_source_aligned_delta_composition_frontier import symmetric_exchange_failure
from r5_e79_binary_reconstruction_matchgate_firewall import reconstruct_even_binary


S5 = frozenset({0, 5, 6, 9, 10, 15})

# Complete representatives of ALL simple cubic residual topologies on 4,6,8
# vertices.  The connected census sizes are 1,2,5.  On 8 vertices the only
# disconnected possibility is K4 disjoint-union K4, because every simple cubic
# component has at least four vertices.
CUBIC_REPS = {
    4: [
        ((0,1),(0,2),(0,3),(1,2),(1,3),(2,3)),
    ],
    6: [
        ((0,1),(0,2),(0,3),(1,2),(1,4),(2,5),(3,4),(3,5),(4,5)),
        ((0,1),(0,2),(0,3),(1,4),(1,5),(2,4),(2,5),(3,4),(3,5)),
    ],
    8: [
        ((0,1),(0,2),(0,3),(1,2),(1,3),(2,4),(3,5),(4,6),(4,7),(5,6),(5,7),(6,7)),
        ((0,1),(0,2),(0,3),(1,2),(1,4),(2,5),(3,4),(3,6),(4,7),(5,6),(5,7),(6,7)),
        ((0,1),(0,2),(0,3),(1,2),(1,4),(2,5),(3,6),(3,7),(4,6),(4,7),(5,6),(5,7)),
        ((0,1),(0,2),(0,3),(1,4),(1,5),(2,4),(2,6),(3,5),(3,6),(4,7),(5,7),(6,7)),
        ((0,1),(0,2),(0,3),(1,4),(1,5),(2,4),(2,6),(3,5),(3,7),(4,7),(5,6),(6,7)),
        ((0,1),(0,2),(0,3),(1,2),(1,3),(2,3),
         (4,5),(4,6),(4,7),(5,6),(5,7),(6,7)),
    ],
}

EXPECTED_TOTAL_PARTITIONS = {2: 6, 3: 360, 4: 105724}
EXPECTED_RELATIONS_T2 = Counter({(15,): 6})
EXPECTED_RELATIONS_T3 = Counter({(15,): 144, (0,15): 216})
EXPECTED_RELATIONS_T4 = Counter({
    (15,): 80130,
    (0,15): 19488,
    (6,15): 1592,
    (10,15): 1592,
    (5,15): 1420,
    (9,15): 1420,
    (0,6,9,15): 24,
    (0,5,10,15): 24,
    (5,9,15): 18,
    (6,10,15): 16,
})


def verify_cubic_graph(n, edges):
    E={tuple(sorted(e)) for e in edges}
    assert len(E)==3*n//2
    deg=[0]*n
    for u,v in E:
        assert 0 <= u < v < n
        deg[u]+=1; deg[v]+=1
    assert deg == [3]*n
    return tuple(sorted(E))


def graph_fingerprint(n, edges):
    E=set(edges)
    adj=[set() for _ in range(n)]
    for u,v in E:
        adj[u].add(v); adj[v].add(u)

    triangles=sum(
        1 for a,b,c in combinations(range(n),3)
        if b in adj[a] and c in adj[a] and c in adj[b]
    )
    common=Counter(len(adj[u] & adj[v]) for u,v in combinations(range(n),2))

    color={}
    bip=True
    components=0
    for root in range(n):
        if root in color:
            continue
        components += 1
        color[root]=0; stack=[root]
        while stack:
            u=stack.pop()
            for v in adj[u]:
                if v not in color:
                    color[v]=1-color[u]; stack.append(v)
                elif color[v]==color[u]:
                    bip=False
    return components, triangles, bip, tuple(sorted(common.items()))


def matching_masks(edges, size):
    out=[]
    for comb in combinations(range(len(edges)), size):
        used=set(); ok=True
        for i in comb:
            u,v=edges[i]
            if u in used or v in used:
                ok=False; break
            used.add(u); used.add(v)
        if ok:
            out.append(sum(1<<i for i in comb))
    return out


def independent_crossing_masks(n, edges):
    out=[]
    for S in range(1<<n):
        if any(((S>>u)&1) and ((S>>v)&1) for u,v in edges):
            continue
        cut=0
        for i,(u,v) in enumerate(edges):
            if ((S>>u)&1) ^ ((S>>v)&1):
                cut |= 1<<i
        out.append(cut)
    return tuple(out)


def uniform_status(cut, block):
    k=(cut & block).bit_count()
    s=block.bit_count()
    if k==0: return 0
    if k==s: return 1
    return None


def boundary_relation(cuts, c0, c1, u0, u1, core_blocks):
    family=set()
    for cut in cuts:
        # Every reference-cover block must be either wholly crossed by the
        # residual independent set, or wholly untouched. Partial crossing
        # would leave a check uncovered or doubly covered.
        if any(uniform_status(cut,B) is None for B in core_blocks):
            continue
        zu0=uniform_status(cut,u0)
        zu1=uniform_status(cut,u1)
        if zu0 is None or zu1 is None:
            continue
        zc0=int(bool(cut & c0))
        zc1=int(bool(cut & c1))
        # Original Tanner boundary bits are complements of crossing status:
        # check bit 1 means the check is left uncovered internally; variable
        # bit 1 means the corresponding reference-cover variable is selected.
        bits=(1-zc0, 1-zc1, 1-zu0, 1-zu1)
        family.add(sum(bit<<i for i,bit in enumerate(bits)))
    return frozenset(family)


def census_graph(n, edges, t):
    edges=verify_cubic_graph(n,edges)
    m=len(edges); full=(1<<m)-1
    pairs=matching_masks(edges,2)
    triples=set(matching_masks(edges,3))
    cuts=independent_crossing_masks(n,edges)

    total=0
    relations=Counter()
    for i,j in combinations(range(m),2):
        c0=1<<i; c1=1<<j
        rem=full ^ c0 ^ c1
        for u0 in pairs:
            if u0 & ~rem:
                continue
            rem1=rem ^ u0
            for u1 in pairs:
                if u1 & ~rem1:
                    continue

                rem2=rem1 ^ u1
                if t==2:
                    if rem2:
                        continue
                    cores=()
                    total += 1
                    rel=boundary_relation(cuts,c0,c1,u0,u1,cores)
                    relations[tuple(sorted(rel))] += 1
                elif t==3:
                    if rem2 not in triples:
                        continue
                    cores=(rem2,)
                    total += 1
                    rel=boundary_relation(cuts,c0,c1,u0,u1,cores)
                    relations[tuple(sorted(rel))] += 1
                elif t==4:
                    # The two 3-edge core blocks are unordered. Force the
                    # least remaining edge into the first block so each
                    # partition is counted exactly once.
                    first=rem2 & -rem2
                    for q0 in triples:
                        if not (q0 & first):
                            continue
                        if q0 & ~rem2:
                            continue
                        q1=rem2 ^ q0
                        if q1 not in triples:
                            continue
                        cores=(q0,q1)
                        total += 1
                        rel=boundary_relation(cuts,c0,c1,u0,u1,cores)
                        relations[tuple(sorted(rel))] += 1
                else:
                    raise AssertionError("E84 freezes t=2,3,4 only")
    return total, relations


def verify_distinct_representatives():
    expected={4:1,6:2,8:6}
    for n,reps in CUBIC_REPS.items():
        fps=[]
        for E in reps:
            E=verify_cubic_graph(n,E)
            fps.append(graph_fingerprint(n,E))
        assert len(reps)==expected[n]
        assert len(set(fps))==len(reps)


def verify_all_delta_relations_are_binary(relations):
    for key in relations:
        F=frozenset(key)
        if symmetric_exchange_failure(F,4) is None:
            reconstruct_even_binary(F,4)


def main():
    verify_distinct_representatives()

    aggregate={}
    grand_total=0
    for t,n in ((2,4),(3,6),(4,8)):
        total=0
        relations=Counter()
        for E in CUBIC_REPS[n]:
            count, rels=census_graph(n,E,t)
            total += count
            relations.update(rels)

        assert total == EXPECTED_TOTAL_PARTITIONS[t]
        assert tuple(sorted(S5)) not in relations
        verify_all_delta_relations_are_binary(relations)
        aggregate[t]=(total,relations)
        grand_total += total

    assert aggregate[2][1] == EXPECTED_RELATIONS_T2
    assert aggregate[3][1] == EXPECTED_RELATIONS_T3
    assert aggregate[4][1] == EXPECTED_RELATIONS_T4
    assert grand_total == 106090

    print("R5 E84 direct U2,4 / S5 C4-free linearity killer: PASS")
    print("normal form: direct 4-port S5 => |C|=|V|=3t and a simple cubic residual-exchange graph on 2t vertices")
    print("complete residual topology counts for 4/6/8 vertices = 1/2/6 (8-vertex set includes K4 disjoint-union K4)")
    print("matching partitions exhausted: t=2 -> 6; t=3 -> 360; t=4 -> 105724; total=106090")
    print("S5/U2,4 direct witnesses found=0 through 12x12 C4-free clusters")
    print("every delta relation encountered in the census is binary-even")
    print("remaining representation frontier: conditioned U2,4 minors and direct candidates at 15x15 or larger")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
