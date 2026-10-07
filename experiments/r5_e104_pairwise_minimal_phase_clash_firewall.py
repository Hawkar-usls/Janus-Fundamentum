#!/usr/bin/env python3
"""R5 E104: pairwise-minimal witness phase-clash firewall.

E103 showed that C4-free/cubic/six-witness geometry alone does not kill the
smallest E102 H_a^0/H_a^1 holonomy clash.

E104 strengthens the firewall: even choosing each of the three OPPOSITE
TARGET6 witness pairs at GLOBAL minimum symmetric-difference distance does not
kill the clash.

Construction:
  * E92 five-port TARGET6 cluster (18 internal variables, checks 0..18);
  * a 27x27 Pappus phase gadget for direction a=(0,1):
      H_a^0 block: empty | {3} | {0,1,2,4,5}
      neutral     : {0,1,2} | {3} | {4,5}
      H_a^1 block: empty | {4,5} | {0,1,2,3}
  * two internal support-preserving switches connecting the three Pappus blocks;
  * TWO nonzero-support graft switches into E92:
      support {3},
      support {4,5}.

The combined five-port cluster has:
  45 internal variables,
  46 internal checks,
  connected C4-free Tanner geometry,
  all six actual TARGET6 masks feasible.

Exact Algorithm-X enumeration gives witness counts:
  raw1  = 4
  raw2  = 4
  raw4  = 4
  raw19 = 2
  raw21 = 4
  raw22 = 2
  raw8  = 4

For opposite pairs
  (1,22), (2,21), (4,19)
the global minimum internal symmetric-difference distance is 24 in all three
cases.  The six support-labelled witnesses attain those minima.

Each chosen opposite-pair exchange graph has exactly two connected components,
each with two boundary terminals:
  G0: sizes 6 and 18;
  G1: sizes 6 and 18;
  G2: sizes 18 and 6.
Thus there is no terminal-free exchange component and every chosen pair is in
the E98 2+2 rectangle normal form.

Nevertheless one connected nonzero-h holonomy component still contains both
H_(0,1)^0 and H_(0,1)^1, so its Good intersection is empty.

At the same time raw8 has four exact witnesses.

Therefore:
  geometry + actual TARGET6 witnesses + pairwise-global-minimum opposite
  witnesses + E98 2+2 rectangles
is STILL insufficient to kill bad holonomy.

The missing force is now isolated to exact-parent/no-raw8 semantics:
a valid counterexample would have to realize the same kind of minimal clash
while forbidding every raw8 witness.

P_VS_NP remains OPEN.
"""

from itertools import combinations, product
from collections import Counter

TARGETS=(1,2,4,19,21,22)
OPP=((0,5),(1,4),(2,3))
D1=frozenset({0,1,4,5})
D2=frozenset({0,2,3,5})
OPPOSITE=(
    frozenset({0,5}),
    frozenset({1,4}),
    frozenset({2,3}),
)
K=((0,0),(1,0),(0,1),(1,1))

E92_CUBICS=(
    (0,2,18),(0,6,13),(1,9,14),(1,10,16),(2,3,4),
    (3,5,12),(3,9,15),(4,7,11),(4,8,14),(5,6,7),
    (5,11,17),(6,10,15),(7,12,18),(8,9,10),(8,13,16),
    (11,12,13),(14,15,16),
)
E92_SUPPORTS=(
    frozenset(),
    frozenset({1,2,5}),
    frozenset({0,4}),
    frozenset({2}),
    frozenset({0,1,3}),
    frozenset({4,5}),
    frozenset({2}),
    frozenset({4,5}),
    frozenset({2}),
    frozenset({3}),
    frozenset({0,1,2}),
    frozenset({0,4}),
    frozenset({0,1,2}),
    frozenset({1,3,5}),
    frozenset({0,4}),
    frozenset({3}),
    frozenset({1,3,5}),
    frozenset({3,4,5}),
)

PAPPUS_EDGES=(
    (0,0),(0,2),(0,8),
    (1,0),(1,1),(1,6),
    (2,1),(2,2),(2,7),
    (3,2),(3,3),(3,5),
    (4,0),(4,3),(4,4),
    (5,1),(5,4),(5,5),
    (6,5),(6,6),(6,8),
    (7,3),(7,6),(7,7),
    (8,4),(8,7),(8,8),
)
PAPPUS_COVERS=(
    frozenset({0,5,7}),
    frozenset({1,3,8}),
    frozenset({2,4,6}),
)

GROUPS=(
    # H_(0,1)^0 : d=000,001,001
    (
        frozenset(),
        frozenset({3}),
        frozenset({0,1,2,4,5}),
    ),
    # neutral : d=111,001,110
    (
        frozenset({0,1,2}),
        frozenset({3}),
        frozenset({4,5}),
    ),
    # H_(0,1)^1 : d=000,110,110
    (
        frozenset(),
        frozenset({4,5}),
        frozenset({0,1,2,3}),
    ),
)


def hcolor(S):
    return (len(S&D1)&1, len(S&D2)&1)


def base_bit(S):
    return 1 if len(S)%2==0 else 0


def corrected_bit(S,k):
    h=hcolor(S)
    return base_bit(S) ^ ((k[0]&h[0]) ^ (k[1]&h[1]))


def good_set(parts):
    return frozenset(
        k for k in K
        if sum(corrected_bit(S,k) for S in parts)==1
    )


def H0(a):
    return frozenset(k for k in K if ((k[0]&a[0])^(k[1]&a[1]))==0)


def H1(a):
    return frozenset(k for k in K if ((k[0]&a[0])^(k[1]&a[1]))==1)


def build_phase_gadget():
    vn=[set() for _ in range(27)]
    support=[None]*27
    for comp in range(3):
        voff=9*comp
        coff=9*comp
        for v,c in PAPPUS_EDGES:
            vn[voff+v].add(coff+c)
        for v in range(9):
            cls=next(i for i,C in enumerate(PAPPUS_COVERS) if v in C)
            support[voff+v]=GROUPS[comp][cls]

    # comp0 <-> comp1 through identical support {3}
    u,v=1,10
    a,b=0,9
    assert support[u]==support[v]==frozenset({3})
    vn[u].remove(a); vn[v].remove(b)
    vn[u].add(b); vn[v].add(a)

    # comp1 <-> comp2 through identical support {4,5}
    u,v=11,19
    a,b=10,18
    assert support[u]==support[v]==frozenset({4,5})
    vn[u].remove(a); vn[v].remove(b)
    vn[u].add(b); vn[v].add(a)

    return vn,support


def build_combined():
    gvn,gsup=build_phase_gadget()

    vn=[set(t) for t in E92_CUBICS] + [set((17,18))]
    support=list(E92_SUPPORTS)

    for N,S in zip(gvn,gsup):
        vn.append({19+c for c in N})
        support.append(S)

    # Nonzero-support graft 1:
    # E92 var9 support {3}, edge check5
    # gadget global var19 (= local1) support {3}, edge global check25
    assert support[9]==support[19]==frozenset({3})
    assert 5 in vn[9] and 25 in vn[19]
    vn[9].remove(5); vn[19].remove(25)
    vn[9].add(25); vn[19].add(5)

    # Nonzero-support graft 2:
    # E92 var5 support {4,5}, edge check3
    # gadget global var29 (= local11) support {4,5}, edge global check35
    assert support[5]==support[29]==frozenset({4,5})
    assert 3 in vn[5] and 35 in vn[29]
    vn[5].remove(3); vn[29].remove(35)
    vn[5].add(35); vn[29].add(3)

    return tuple(frozenset(N) for N in vn),tuple(support)


def check_neighbors(vn):
    cn=[set() for _ in range(46)]
    for v,N in enumerate(vn):
        for q in N:
            cn[q].add(v)
    return tuple(frozenset(N) for N in cn)


def verify_geometry(vn):
    cn=check_neighbors(vn)
    assert len(vn)==45 and len(cn)==46
    assert all(len(vn[v])==(2 if v==17 else 3) for v in range(45))
    for q,N in enumerate(cn):
        assert len(N)==(2 if q in (0,1,2,17) else 3)

    for u,v in combinations(range(45),2):
        assert len(vn[u]&vn[v])<=1

    seen=set(); stack=[("v",0)]
    while stack:
        kind,i=stack.pop()
        if (kind,i) in seen:
            continue
        seen.add((kind,i))
        if kind=="v":
            stack.extend(("c",q) for q in vn[i])
        else:
            stack.extend(("v",v) for v in cn[i])
    assert len(seen)==91
    return cn


def verify_target_witnesses(cn,support):
    bpos={0:0,1:1,2:2,17:3}
    witnesses=[]
    for lab,mask in enumerate(TARGETS):
        C=frozenset(v for v,S in enumerate(support) if lab in S)
        witnesses.append(C)
        for q,N in enumerate(cn):
            count=sum(v in C for v in N)
            if q in bpos:
                assert count+((mask>>bpos[q])&1)==1
            else:
                assert count==1
        assert (17 in C)==bool((mask>>4)&1)
    return tuple(witnesses)


def enumerate_boundary_witnesses(vn,mask,limit=1000):
    cn=check_neighbors(vn)
    req=[1]*46
    bpos={0:0,1:1,2:2,17:3}
    for q,pos in bpos.items():
        req[q]=1-((mask>>pos)&1)

    vbit=(mask>>4)&1
    fixed_sel={17} if vbit else set()
    fixed_unsel=set() if vbit else {17}

    covered=set()
    chosen=[]
    for v in fixed_sel:
        assert all(req[q]==1 for q in vn[v])
        covered.update(vn[v])
        chosen.append(v)

    forbidden=set(fixed_unsel)
    for v,N in enumerate(vn):
        if any(req[q]==0 for q in N):
            forbidden.add(v)
    assert not (fixed_sel & forbidden)

    out=[]
    def rec(covered,chosen):
        if len(out)>=limit:
            raise AssertionError("enumeration limit hit")
        uncovered=[q for q in range(46) if req[q]==1 and q not in covered]
        if not uncovered:
            out.append(frozenset(chosen))
            return

        opts=None
        for q in uncovered:
            vv=[
                v for v in cn[q]
                if v not in forbidden
                and v not in chosen
                and all(req[t]==1 and t not in covered for t in vn[v])
            ]
            if not vv:
                return
            if opts is None or len(vv)<len(opts):
                opts=vv
                if len(opts)==1:
                    break

        for v in opts:
            rec(covered|set(vn[v]),chosen+[v])

    rec(covered,chosen)
    return tuple(out)


def exchange_components(vn,cn,support,coord):
    nodes={v for v,S in enumerate(support)
           if len(S&OPPOSITE[coord])==1}
    adj={v:set() for v in nodes}
    terminals={v:[] for v in nodes}

    for q,N in enumerate(cn):
        xs=[v for v in N if v in nodes]
        if q in (0,1,2):
            assert len(xs)==1
            terminals[xs[0]].append(("A","B","C")[q])
        else:
            assert len(xs) in (0,2)
            if len(xs)==2:
                u,v=xs
                adj[u].add(v); adj[v].add(u)

    assert 17 in nodes
    terminals[17].append("V")

    comps=[]
    seen=set()
    for s in nodes:
        if s in seen:
            continue
        stack=[s]; C=set(); T=[]
        while stack:
            v=stack.pop()
            if v in C:
                continue
            C.add(v); seen.add(v)
            T.extend(terminals[v])
            stack.extend(adj[v]-C)
        comps.append((frozenset(C),tuple(sorted(T))))
    return tuple(comps)


def verify_bad_holonomy(cn,support):
    a=(0,1)
    expected=Counter({H0(a):9,frozenset(K):9,H1(a):9})

    # Only the 27 gadget checks 19..45 are needed to force emptiness.
    sigs=[]
    for q in range(19,46):
        sigs.append(good_set(tuple(support[v] for v in cn[q])))
    assert Counter(sigs)==expected

    nz={v for v,S in enumerate(support) if hcolor(S)!=(0,0)}
    adj={v:set() for v in nz}
    for q,N in enumerate(cn):
        xs=[v for v in N if v in nz]
        for u,v in combinations(xs,2):
            adj[u].add(v); adj[v].add(u)

    # Locate the component containing gadget nonzero variables.
    gadget_nz={v for v in range(18,45) if v in nz}
    start=next(iter(gadget_nz))
    C=set(); stack=[start]
    while stack:
        v=stack.pop()
        if v in C:
            continue
        C.add(v); stack.extend(adj[v]-C)
    assert gadget_nz <= C

    allowed=set(K)
    for q,N in enumerate(cn):
        if any(v in C for v in N):
            allowed &= set(good_set(tuple(support[v] for v in N)))
    assert allowed==set()
    return len(C)


def main():
    vn,support=build_combined()
    cn=verify_geometry(vn)
    labelled=verify_target_witnesses(cn,support)

    exact={}
    for mask in TARGETS+(8,):
        exact[mask]=enumerate_boundary_witnesses(vn,mask)

    counts={m:len(exact[m]) for m in TARGETS+(8,)}
    assert counts=={1:4,2:4,4:4,19:2,21:4,22:2,8:4}

    minima={}
    for coord,(i,j) in enumerate(OPP):
        a,b=TARGETS[i],TARGETS[j]
        dmin=min(len(X^Y) for X in exact[a] for Y in exact[b])
        minima[(a,b)]=dmin
        assert dmin==24
        assert len(labelled[i]^labelled[j])==dmin

        comps=exchange_components(vn,cn,support,coord)
        footprints=sorted((len(C),T) for C,T in comps)
        if coord in (0,1):
            assert footprints==[(6,("A","B")),(18,("C","V"))]
        else:
            assert footprints==[(6,("B","C")),(18,("A","V"))]

    bad_size=verify_bad_holonomy(cn,support)

    assert len(exact[8])==4

    print("R5 E104 pairwise-minimal witness phase-clash firewall: PASS")
    print("combined cluster: 45 variables / 46 checks, connected and C4-free")
    print("exact witness counts:",counts)
    print("opposite-pair global minimum distances:",minima)
    print("labelled witnesses attain all three minima")
    print("all three exchange graphs are 2+2 terminal-component normal forms")
    print("bad nonzero-h holonomy component size=",bad_size)
    print("component Good intersection=empty")
    print("raw8 exact witnesses=",len(exact[8]))
    print("MINIMALITY_ONLY_PHASE_CLASH_KILLER = FALSIFIED")
    print("next target: exploit exact NO-RAW8 parent semantics; minimality/geometry alone are insufficient")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
