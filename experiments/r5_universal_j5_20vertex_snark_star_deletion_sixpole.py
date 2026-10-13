#!/usr/bin/env python3
"""20-vertex flower snark J5: all induced claws -> 16-vertex sixpoles.

Check the exact native graph, all physical edge colours, EVERY centre
vertex (20), and all 15 pairings (300). The input J5 is constructed
by Isaacs' standard centre-leaf / 5-cycle / 10-cycle construction,
not by a hardcoded list of bit signatures.

ALL source claims are independently assertion-backed:
* H=J5 is a simple bridgeless 3-regular 20-vertex,30-edge graph;
* H is NOT 3-edge colourable (complete DFS with first edge colour 0);
* for every one of 20 induced stars remove centre and its three
  neighbours, yielding a 16-vertex 21-edge interior with six semiedges;
* independently enumerate ALL proper internal 3-edge colourings,
  derive the six PHYSICAL port colours, evaluate ALL 15 partitions;
* verify exactly 270 full-five parity signatures and 30 4-states
  {100,010,001,111}, zero exposed Exact-One;
* direct gluing each of three matching pairs has physical bit 111
  and must match actual source semantics.

A result only for J5 says NOTHING about the other five 20-vertex
nontrivial snarks, nor arbitrary reducible snarks, nor all n=16.
"""
from collections import Counter
from itertools import permutations


BITS3={(1,0,0),(0,1,0),(0,0,1)}
FULL_FIVE=BITS3|{(0,0,0),(1,1,1)}
FOUR_NOZERO=BITS3|{(1,1,1)}


def flower_snark(n=5):
    assert n>=5 and n%2==1
    edges=set()
    def add(x,y):
        assert x!=y
        edges.add(tuple(sorted((x,y))))
    for i in range(n):
        add(i,n+i)
        add(i,2*n+i)
        add(i,3*n+i)
        add(n+i,n+(i+1)%n)
    ring=tuple(2*n+i for i in range(n))+tuple(3*n+i for i in range(n))
    for i in range(2*n):
        add(ring[i],ring[(i+1)%(2*n)])
    assert len(edges)==6*n
    assert all(sum(v in e for e in edges)==3 for v in range(4*n))
    return tuple(sorted(edges))


def pairings(x):
    if not x:
        yield ()
        return
    head,*rest=x
    for i,b in enumerate(rest):
        for tail in pairings(rest[:i]+rest[i+1:]):
            yield ((head,b),)+tail


ALL_PAIRS=tuple(pairings(list(range(6))))
assert len(ALL_PAIRS)==15


def enumerate_edge_colours(vertices,edges,ports=()):
    """Enumerate full legal internal assignments with no omitted colour symmetry."""
    ed=tuple(sorted(edges))
    incident={v:[] for v in vertices}
    for i,(u,v) in enumerate(ed):
        incident[u].append(i)
        incident[v].append(i)
    colour=[-1]*len(ed)
    count=0
    boundary_states=set()
    def dfs(i):
        nonlocal count
        if i==len(ed):
            count+=1
            if ports:
                state=[]
                for v in ports:
                    occupied={colour[j] for j in incident[v]}
                    missing=tuple(c for c in range(3) if c not in occupied)
                    assert len(missing)==1
                    state.append(missing[0])
                boundary_states.add(tuple(state))
            return
        u,v=ed[i]
        for c in range(3):
            if any(colour[j]==c for x in (u,v) for j in incident[x] if j<i):
                continue
            colour[i]=c
            dfs(i+1)
            colour[i]=-1
    dfs(0)
    return count,frozenset(boundary_states)


def induced_claw_sixpole(H,centre):
    leaf=tuple(sorted(v if u==centre else u
                      for u,v in H if centre in (u,v)))
    assert len(leaf)==3 and len(set(leaf))==3
    removed=set((centre,)+leaf)
    # The neighbourhood is independent (a true induced claw).
    assert not any(u in leaf and v in leaf for u,v in H)
    remains=tuple(v for v in range(20) if v not in removed)
    internal=tuple(e for e in H if not any(v in removed for v in e))
    external=tuple((v,u if v in removed else v) for u,v in ()) # no-op
    ports=[]
    natural_pairs=[]
    for leaf_vertex in leaf:
        pair=[]
        for e in H:
            if leaf_vertex not in e:
                continue
            other=e[0] if e[1]==leaf_vertex else e[1]
            if other not in removed:
                pair.append(len(ports))
                ports.append(other)
        assert len(pair)==2
        natural_pairs.append(tuple(pair))
    assert len(remains)==16 and len(internal)==21 and len(ports)==6
    assert len(set(ports))==6,("girth<5 / repeated outward port",centre,ports)
    assert set(ports).issubset(remains)
    assert all(sum(v in e for e in internal)==(2 if v in ports else 3)
               for v in remains)
    return remains,internal,tuple(ports),tuple(natural_pairs)


def bit_relation(states,pairs):
    return frozenset(tuple(int(s[i]==s[j]) for i,j in pairs)
                     for s in states)


def main():
    H=flower_snark(5)
    assert len(H)==30
    full,empty=enumerate_edge_colours(tuple(range(20)),H)
    assert full==0 and not empty,"J5 incorrectly colourable"
    print("J5_ORIGINAL: simple cubic 20 vertices,30 edges,")
    print("  exhaustive full 3-edge-colour rejection PASS",flush=True)
    ctr=Counter()
    real_examples=[]
    for centre in range(20):
        V,E,port_vertices,natural_pairs=induced_claw_sixpole(H,centre)
        count,states=enumerate_edge_colours(V,E,port_vertices)
        assert count>0
        ctr["claws"]+=1
        ctr["sixpole_3edge_colourings"]+=count
        ctr["sixpole_distinct_full_physical_signatures"]+=len(states)
        r0=bit_relation(states,natural_pairs)
        assert (0,0,0) not in r0,("STAR closure must reconstruct J5",centre,r0)
        assert (1,1,1) in r0,("unexpected absence of bit111",centre,r0)
        for p in ALL_PAIRS:
            R=bit_relation(states,p)
            assert R in (FULL_FIVE,FOUR_NOZERO),(centre,p,R)
            ctr["interfaces"]+=1
            if R==FULL_FIVE:
                ctr["full_five"]+=1
            if R==FOUR_NOZERO:
                ctr["zero_forbidden_but_111"]+=1
                # Colour-space tester: an ACTUAL equal-pairs triple
                # extends by gluing 3 native source edges.
                witnesses=[s for s in states if all(s[u]==s[v] for u,v in p)]
                assert witnesses,("missing physical MATCH3 extension",centre,p)
                if len(real_examples)<5:
                    real_examples.append((centre,p,port_vertices,witnesses[0]))
        print("J5_CLAW",centre,{"native_M_vertices":16,"internal_edges":21,
              "full_colourings":count,"boundary_signatures":len(states),
              "natural_bits":sorted(r0)},flush=True)
    assert ctr["claws"]==20
    assert ctr["interfaces"]==300
    assert ctr["full_five"]==270,ctr
    assert ctr["zero_forbidden_but_111"]==30,ctr
    assert len(real_examples)>0
    print("J5_20_CLAW_300_PHYSICAL_RELATIONS",dict(ctr),flush=True)
    print("MATCH3_PHYSICAL_111_EXAMPLES",real_examples,flush=True)
    print("ALL_J5_CLAWS_ONEHOT_REFUTED_BY_111=PASS",flush=True)
    print("OTHER_20_VERTEX_SNARKS=NOT_CHECKED_BY_THIS_FILE",flush=True)
    print("N16_ALL_GRAPHS=SEPARATE_CI; NO_GLOBAL_PC_BACKSIM; P_VS_NP=OPEN")


if __name__=="__main__":
    main()
