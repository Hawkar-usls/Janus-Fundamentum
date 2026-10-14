#!/usr/bin/env python3
"""R5 seven-FOURPOLE synchronous-coupling hub: exact finite frontier.

For 7 connected cubic fourpoles joined by 11 ordinary interblock
edges, the exposed number of ports is 7*4-2*11=6. Restrict to SIMPLE
3-edge-connected block skeletons; degree sum 22 and min degree 3
force degree sequence (4,3,3,3,3,3,3). The unique four-interface
block is an internal shared "synchronization hub" with ZERO exposed
physical ports; the other six 3-interface blocks each expose ONE port.

Exhaustively generate ALL simple labelled degree-sequence realizations
on vertices 0..6: exactly 5670 distinct labelled graphs. Compare to
the COMPLETE orbits under all 7! vertex relabellings of the four
reference skeletons: class sizes (2520,1260,1260,630), disjoint,
cover all 5670; independently check that each realization has
edge-connectivity >=3. Thus EXACTLY FOUR unlabelled simple
3-edgeconnected block skeletons exist in this SEVEN-block 11-join
high-connectivity grammar.

For each of four representatives, independently enumerate all 3^11
assignments of the interblock edge colours and compute the legal local
FOUR-colour orbit at every constituent block (AAAA/AABB/ABAB/ABBA).
The six terminal blocks' one external colour is uniquely forced by
their 3 connector colours via the Klein-four parity law; the central
fourport hub itself must have zero sum of its four connector colours.

Finite exact local orbit-record counts for four skeletons:
  0: 1328 records, 10479 proper connector-colour assignments
  1: 1400 records, 10371 proper connector-colour assignments
  2: 1379 records, 10413 proper connector-colour assignments
  3: 1272 records, 10551 proper connector-colour assignments.

Exploratory seeded 11-class sampling of these EXACT relations is
allowed for DISCOVERY only; failing to find 108 GOOD states with 0
forbidden ones is NOT a mathematical NO-GO or an UNSAT certificate.
No universal polynomial solver or P=NP result follows.

A true full physical 108-state 6pole still requires one genuine graph,
six distinct physical roots, and complete proper 3-edge-colouring DFS.
"""
from collections import Counter,defaultdict
from itertools import combinations,permutations,product
from random import Random

COLOURS=(0,1,2)
GF4=(1,2,3)
ORBIT_REPS=((0,0,0,0),(0,0,1,1),(0,1,0,1),(0,1,1,0))
ORBIT_ID={r:i for i,r in enumerate(ORBIT_REPS)}
CLASSES=tuple(k for j in (2,3,4) for k in combinations(range(4),j))
MASKS=tuple(sum(1<<o for o in k) for k in CLASSES)
assert len(CLASSES)==11

SKELETONS=(
    ((0,4),(0,5),(0,6),(1,3),(1,5),(1,6),(2,3),(2,4),(2,6),(3,6),(4,5)),
    ((0,3),(0,5),(0,6),(1,2),(1,5),(1,6),(2,3),(2,4),(3,4),(4,5),(4,6)),
    ((0,1),(0,2),(0,4),(0,5),(1,3),(1,4),(2,3),(2,5),(3,6),(4,6),(5,6)),
    ((0,1),(0,2),(0,3),(0,4),(1,2),(1,6),(2,6),(3,4),(3,5),(4,5),(5,6)),
)


def connected(E):
    adj=[[] for _ in range(7)]
    for u,v in E:
        adj[u].append(v);adj[v].append(u)
    visited={0};todo=[0]
    for u in todo:
        for v in adj[u]:
            if v not in visited:
                visited.add(v);todo.append(v)
    return len(visited)==7


def edge_connectivity_at_least_three(E):
    if not connected(E):
        return False
    for subset in range(1, (1<<7)-1):
        cut=sum(bool(subset&(1<<u))!=bool(subset&(1<<v))
                for u,v in E)
        if cut<3:return False
    return True


def verify_all_four_nonisomorphic_skeletons():
    # Full independent labelled-isomorphism partition. Each orbit is
    # enumerated by all 7! permutations (no graph atlas dependency).
    orbits=[]
    for E in SKELETONS:
        assert len(E)==11 and edge_connectivity_at_least_three(E)
        relabelled=set()
        for perm in permutations(range(7)):
            relabelled.add(tuple(sorted(
                tuple(sorted((perm[u],perm[v]))) for u,v in E
            )))
        orbits.append(relabelled)
    sizes=tuple(map(len,orbits))
    assert sizes==(2520,1260,1260,630),sizes
    complete_orbit=set().union(*orbits)
    assert sum(sizes)==len(complete_orbit)==5670
    universe=tuple(combinations(range(7),2))
    total=0
    for chosen in combinations(universe,11):
        d=Counter(v for e in chosen for v in e)
        if sorted(d[v] for v in range(7))!=[3]*6+[4]:
            continue
        total+=1
        assert chosen in complete_orbit
        assert edge_connectivity_at_least_three(chosen)
    assert total==5670
    print("SEVEN_FOURPOLE_3_EDGE_CONNECTED_SIMPLE_SKELETONS",{
        "unique_representatives":4,
        "labelled_degree_realizations":total,
        "four_full_orbit_sizes":sizes,
        "all_connected_edge_connectivity_ge3":True,
    },flush=True)


def orbit4(t):
    name={}
    rep=tuple(name.setdefault(x,len(name)) for x in t)
    return ORBIT_ID.get(rep,-1)


def phase_hub_records(E):
    """Exact 729-bit physical support per seven local orbit types."""
    edges=tuple(sorted(E))
    inc=[tuple(k for k,e in enumerate(edges) if v in e)
         for v in range(7)]
    outer=[v for v in range(7) if len(inc[v])==3]
    hub=[v for v in range(7) if len(inc[v])==4]
    assert len(outer)==6 and len(hub)==1
    relation=defaultdict(int)
    allowed=0
    for c in product(COLOURS,repeat=11):
        local=[]
        port={}
        for v in range(7):
            wires=tuple(c[j] for j in inc[v])
            x=0
            for a in wires:
                x ^= GF4[a]
            if len(wires)==3:
                if not x:
                    break
                out=GF4.index(x)
                port[v]=out
                four=(out,)+wires
            else:
                if x:
                    break
                four=wires
            orb=orbit4(four)
            if orb<0:break
            local.append(orb)
        else:
            external=tuple(port[v] for v in outer)
            assert all(external.count(x)%2==0 for x in COLOURS)
            code=sum(x*3**(5-i) for i,x in enumerate(external))
            relation[tuple(local)] |= 1<<code
            allowed+=1
    return relation,allowed,outer


def logical_pairings(indices=(0,1,2,3,4,5)):
    if not indices:
        yield ()
        return
    a=indices[0]
    for j in range(1,len(indices)):
        for suffix in logical_pairings(indices[1:j]+indices[j+1:]):
            yield ((a,indices[j]),)+suffix


def relation_histogram(states,logical_pairs):
    hist=Counter()
    while states:
        bit=states&-states
        code=bit.bit_length()-1
        c=tuple((code//3**(5-i))%3 for i in range(6))
        k=''.join(str(int(c[a]==c[b])) for a,b in logical_pairs)
        hist[k]+=1
        states^=bit
    return hist


def sample_synchronous_hub_candidate(record, logical_pairs, rng, samples=500):
    """HEURISTIC exploration only, exact evaluation of sampled choices."""
    records=tuple((tuple(1<<v for v in o),b)
                  for o,b in record.items())
    best=None
    for _ in range(samples):
        labels=tuple(rng.randrange(11) for _ in range(7))
        mask=tuple(MASKS[j] for j in labels)
        states=0
        for values,outs in records:
            if all(mask[v]&values[v] for v in range(7)):
                states |= outs
        hist=relation_histogram(states,logical_pairs)
        n_good=sum(hist[b] for b in ("100","010","001"))
        n_forbidden=sum(k for b,k in hist.items()
                        if b not in ("100","010","001"))
        penalty=n_forbidden+4*(108-n_good)
        observation=(penalty,n_forbidden,n_good,labels,hist)
        if best is None or observation[0]<best[0]:
            best=observation
    return best


def run():
    verify_all_four_nonisomorphic_skeletons()
    pairings=tuple(logical_pairings())
    assert len(pairings)==15
    expected=((1328,10479),(1400,10371),(1379,10413),(1272,10551))
    rng=Random(20261014)
    best_global=None
    for index,E in enumerate(SKELETONS):
        records,n,ports=phase_hub_records(E)
        assert (len(records),n)==expected[index],(index,len(records),n)
        candidate=None
        for pair in pairings:
            sample=sample_synchronous_hub_candidate(
                records,pair,rng,samples=500)
            if candidate is None or sample[0]<candidate[0]:
                candidate=(sample[0],pair,sample)
        if best_global is None or candidate[0]<best_global[0]:
            best_global=(candidate[0],index,candidate)
        print("SEVEN_BLOCK_HUB_EXACT_ORBIT_RECORDS",{
            "index":index,"connectors":11,
            "three_edge_connected":True,
            "exact_local_orbit_records":len(records),
            "exact_colour_assignments":n,
            "six_exposed_port_blocks":ports,
            "sampled_best_cost":candidate[0],
            "sampled_best_pairing":candidate[1],
            "sampled_best_truth_histogram":dict(candidate[2][4]),
        },flush=True)
    print("SEVEN_BLOCK_PHASE_HUB_HEURISTIC_BEST",best_global)
    print("HEURISTIC_NO_UNSAT_PROOF_NO_PHYSICAL_108_GADGET")
    print("SolveLinearCubicXSAT=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__=="__main__":
    run()
