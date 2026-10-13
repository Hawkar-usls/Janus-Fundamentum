#!/usr/bin/env python3
"""Exact C4 Boolean wire / C6 odd-XOR gate and trivial-SAT global no-go.

Only uses standard Python; every finite status is assertion-backed.
The universal claims also have symbolic proofs in paired research note.
Native SCL is the ORIGINAL 3-edge-colour Holyer source: edge-row plus
one vertex-colour row per colour, with square+cubic+linear guarantees.

Do NOT interpret any of these gadgets as a PC hardness reduction.
"""
from collections import Counter
from itertools import product


def cycle_edge_colourings(n):
    # n internal ring edges e_i=(i,i+1 mod n), with one dangling
    # port at vertex i; the port colour is the third distinct colour.
    for es in product(range(3), repeat=n):
        if any(es[i] == es[(i - 1) % n] for i in range(n)):
            continue
        ports = tuple(3 - es[(i - 1) % n] - es[i] for i in range(n))
        assert all(set((es[(i-1)%n], es[i], ports[i])) == {0,1,2}
                   for i in range(n))
        yield es, ports


def wire_c4():
    counts = Counter()
    boundary = Counter()
    witnesses = {}
    for es, ports in cycle_edge_colourings(4):
        t = (int(ports[0] == ports[1]), int(ports[2] == ports[3]))
        assert t[0] == t[1], ("violates parity 4-pole", es, ports)
        # Exact COLOUR-level transfer, stronger than equality of bits:
        # TRUE input AA -> output BB (any B, possibly A);
        # FALSE input AB -> output BA (necessarily reversed).
        if t[0] == 0:
            assert ports[0] == ports[3] and ports[1] == ports[2]
        counts[t] += 1
        boundary[ports] += 1
        witnesses.setdefault(t[0], (es, ports))
    assert counts == {(1,1):12, (0,0):6}, counts
    expected_true={(a,a,b,b) for a in range(3) for b in range(3)}
    expected_false={(a,b,b,a) for a in range(3) for b in range(3) if a!=b}
    assert set(boundary)==expected_true|expected_false
    assert len(boundary)==15
    assert all(boundary[(a,a,a,a)]==2 for a in range(3))
    assert all(v==1 for k,v in boundary.items() if k[0]!=k[1] or k[0]!=k[2])
    print("C4_COLOUR_PORT_TRANSFORM: 15 boundary signatures exactly:")
    print("  TRUE AA -> BB any colour B; FALSE AB -> BA reversed PASS")
    assert set(witnesses) == {0,1}
    # A base Boolean variable b selects an explicit legal colour
    # assignment in the 4-pole. Target edge-indicator P_e,c(b) is
    # affine interpolation: (1-b)*indicator_state0 + b*indicator_state1.
    # Each target native Exact-One row is IDENTICALLY zero over F3[b],
    # while each target Boolean axiom P^2-P is 0 or (b^2-b).
    x0 = witnesses[0][0] + witnesses[0][1]
    x1 = witnesses[1][0] + witnesses[1][1]
    coeff = {}
    for e in range(8):
        for c in range(3):
            a = int(x0[e] == c)
            z = int(x1[e] == c)
            coeff[e,c] = (a, z-a)
            u,v = coeff[e,c]
            pol = ((u*u-u)%3, (2*u*v-v)%3, (v*v)%3)
            assert pol == (0,0,0) if v==0 else pol==(0,2,1), (e,c,pol)
    edge_rows=[tuple((i,c) for c in range(3)) for i in range(8)]
    vertex_rows=[]
    for v in range(4):
        incident=((v-1)%4,v,4+v)
        for c in range(3):
            vertex_rows.append(tuple((e,c) for e in incident))
    for row in edge_rows+vertex_rows:
        const=sum(coeff[x][0] for x in row)-1
        linear=sum(coeff[x][1] for x in row)
        assert const==0 and linear==0, ("affine source row fail",row)
    # Decoder of equality bit is quadratic in the port indicators
    # T(p0,p1) = sum_c X_(p0,c) X_(p1,c) (mod3).
    # Verify it is precisely b in the Boolean quotient b^2-b.
    for b in (0,1):
        vals=[(u+v*b)%3 for e in range(8) for c in range(3)
              for u,v in [coeff[e,c]]]
        assert sum(vals[3*4+c]*vals[3*5+c] for c in range(3))%3==b
    print("C4_BOOLEAN_WIRE: 18 valid assignments (12 TRUE,6 FALSE);")
    print("  explicit affine native edge/vertex source interpolation and Boolean PC degree2 PASS")


def xor6():
    counts=Counter()
    signatures=set()
    witnesses={}
    for es, ports in cycle_edge_colourings(6):
        t=tuple(int(ports[i]==ports[i+3]) for i in range(3))
        assert sum(t)%2 == 1, ("invalid odd parity",es,ports,t)
        counts[t]+=1
        signatures.add(ports)
        witnesses.setdefault(t,(es,ports))
    assert counts=={(1,1,1):12,(1,0,0):18,(0,1,0):18,(0,0,1):18},counts
    assert len(signatures)==63,len(signatures)
    # Odd XOR in GF3: (1+t0)(1+t1)(1+t2)+1 = 0,
    # because 1+0=1 and 1+1=2=-1 in GF3.
    for t in witnesses:
        assert ((1+t[0])*(1+t[1])*(1+t[2])+1)%3==0
    print("C6_ODD_XOR: 66 valid internal assignments, 63 boundary colour signatures,")
    print("  Boolean relation {(111),(100),(010),(001)} EXACT PASS")


def legal_original_scl(edges,nv,colors=None):
    edges=tuple(tuple(sorted(e)) for e in edges)
    assert len(edges)==len(set(edges))
    assert all(0<=a<b<nv for a,b in edges)
    assert all(sum(v in e for e in edges)==3 for v in range(nv))
    rows=[tuple((e,c) for c in range(3)) for e in edges]
    for v in range(nv):
        for c in range(3):
            rows.append(tuple((e,c) for e in edges if v in e))
    assert all(len(r)==3 for r in rows)
    assert len(rows)==3*len(edges)
    vars_=set(x for r in rows for x in r)
    assert len(vars_)==len(rows)
    assert all(sum(x in r for r in rows)==3 for x in vars_)
    sets=[set(r) for r in rows]
    assert all(len(a&b)<=1 for i,a in enumerate(sets) for b in sets[i+1:])
    if colors is not None:
        witness={(edge,colors[edge]) for edge in edges}
        assert all(len(witness & row)==1 for row in sets)
    return len(rows)


def sixcycle_expansion(base_edges, nv):
    base_edges=tuple(tuple(sorted(e)) for e in base_edges)
    assert len(base_edges)==3*nv//2 and len(base_edges)==len(set(base_edges))
    incidence={v:[] for v in range(nv)}
    for e in base_edges:
        for v in e:incidence[v].append(e)
    assert all(len(incidence[v])==3 for v in incidence)
    # Order incident base edges, assign pair i and i+3 to each.
    offset={(v,e):i for v in range(nv) for i,e in enumerate(sorted(incidence[v]))}
    edges=set()
    for v in range(nv):
        for i in range(6):
            edges.add(tuple(sorted((6*v+i, 6*v+(i+1)%6))))
    # Each base edge becomes TWO connecting links between distinct
    # ring-vertex ports; the two terminal wires at each end are paired.
    for e in base_edges:
        u,v=e
        i,j=offset[u,e],offset[v,e]
        for k in (0,3):
            edges.add(tuple(sorted((6*u+i+k,6*v+j+k))))
    assert len(edges)==9*nv
    # For ANY input G the expanded graph has the canonical colouring:
    # internal ring edges alternate 0/1, all inter-ring links are 2.
    col={}
    for e in edges:
        u,v=e
        if u//6 != v//6:
            col[e]=2
        else:
            # Edge {ring i, ring i+1}, incl wrap {0,5}.
            a,b=sorted((u%6,v%6))
            idx=5 if (a,b)==(0,5) else a
            col[e]=idx%2
    return len(edges),legal_original_scl(edges,6*nv,col)


def verify_global_no_go():
    k4=[(u,v) for u in range(4) for v in range(u+1,4)]
    k33=[(u,v) for u in range(3) for v in range(3,6)]
    # Petersen: outer pentagon, spokes, inner star.
    pete=[(i,(i+1)%5) for i in range(5)]
    pete += [(i,i+5) for i in range(5)]
    pete += [(5+i,5+(i+2)%5) for i in range(5)]
    for name,G,nv in (("K4",k4,4),("K33",k33,6),("PETERSEN",pete,10)):
        m,n=sixcycle_expansion(G,nv)
        assert (m,n)==(9*nv,27*nv)
        print(f"EXPAND_{name}: 6-cycle tensor expansion has {6*nv} cubic vertices,")
        print(f"  {m} edges, native legal SCL{n}; explicit original SAT witness PASS")
    print("GENERAL_GLOBAL_SAT_WITNESS: symbolic alternating ring 0/1 + all ports 2 => PROVED")


if __name__=="__main__":
    wire_c4()
    xor6()
    verify_global_no_go()
    print("GATES: pure six-cycle Tseitin-hardness import REFUTED by universal SAT witness")
    print("       general native PC unbounded-degree OPEN; polynomial solver NOT CONSTRUCTED; P vs NP OPEN")
