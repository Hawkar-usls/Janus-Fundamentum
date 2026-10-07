#!/usr/bin/env python3
"""R5 E103: signed phase-clash geometry counterexample + F2^3 flow normal form.

E102 reduced a rigid-free no-state8 obstruction to a bad holonomy component.
Its smallest signature-level obstruction is H_a^0 versus H_a^1 for one
nonzero direction a in GF(2)^2.

E103 first derives an exact F2^3 normal form.  For a variable support S among
the six TARGET6 witnesses, define the opposite-pair exchange-membership vector

    d(S) = (d0,d1,d2) in GF(2)^3,

where di=1 iff S contains exactly one label from opposite pair O_i.

Then
    p(S)=|S| mod2 = d0+d1+d2,
    h(S)=(d0+d1, d0+d2).

For correction k=(a,b), the E95/E102 candidate bit is
    e_k(S)=1+w(k).d(S),
where
    w(00)=111,
    w(10)=001,
    w(01)=010,
    w(11)=100.
Thus the four canonical candidates are exactly the four ODD linear
functionals on d.

At every ordinary check the three supports partition the six labels, hence
the three d-vectors xor to 000.  Local Good-sets therefore depend only on the
F2^3 span of the incident d-vectors.

Most importantly, E103 constructs an explicit connected square/cubic/C4-free
27x27 source with six exact covers such that:
  * no ordinary check is rigid;
  * all nonzero h-colored variables lie in ONE holonomy component;
  * 9 checks have Good=H_(1,0)^0;
  * 9 checks have Good=all GF(2)^2;
  * 9 checks have Good=H_(1,0)^1;
  * hence that one component has empty Good intersection.

Construction:
  three Pappus 9x9 components with constant support partitions
      H0      : empty | {0,1,2,3,5} | {4}
      NEUTRAL : {0,1,2} | {3,5} | {4}
      H1      : empty | {0,1,2,4} | {3,5}
  and two support-preserving Tanner 2-switches:
      comp0 v2 -- comp0 c1   with comp1 v2 -- comp1 c1
      comp1 v1 -- comp1 c0   with comp2 v2 -- comp2 c1
  (zero-based local Pappus indices).

The swapped variable pairs have identical six-witness supports, so all six
exact covers remain exact.  The resulting Tanner graph is connected, cubic,
and C4-free.

Therefore:
  C4-free + cubicity + six exact covers + rigid-free
does NOT by itself forbid the smallest H_a^0/H_a^1 phase clash.

The geometry has 8 total exact covers (the six labels use only 3 distinct
ones), exposing the correct next leverage: witness minimality / exchange
switching / exact TARGET6-no-raw8 semantics, not geometry alone.

P_VS_NP remains OPEN.
"""

from itertools import combinations, product
from collections import Counter, deque

U=frozenset(range(6))
D1=frozenset({0,1,4,5})
D2=frozenset({0,2,3,5})
OPPOSITE=(
    frozenset({0,5}),
    frozenset({1,4}),
    frozenset({2,3}),
)
K=((0,0),(1,0),(0,1),(1,1))
NZ=((1,0),(0,1),(1,1))

# Pappus graph in a 9-variable / 9-check bipartite indexing.
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

# The three exact-cover classes of the Pappus component.
PAPPUS_COVERS=(
    frozenset({0,5,7}),
    frozenset({1,3,8}),
    frozenset({2,4,6}),
)


# E92 five-port TARGET6 witness cluster used for the stronger graft regression.
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
TARGET6_MASKS=(1,2,4,19,21,22)  # A,B,C,E,V bit order

GROUPS=(
    # component 0: H_(1,0)^0
    (
        frozenset(),
        frozenset({0,1,2,3,5}),
        frozenset({4}),
    ),
    # component 1: neutral bridge, Good=K
    (
        frozenset({0,1,2}),
        frozenset({3,5}),
        frozenset({4}),
    ),
    # component 2: H_(1,0)^1
    (
        frozenset(),
        frozenset({0,1,2,4}),
        frozenset({3,5}),
    ),
)


def dot(x,y):
    return (x[0]*y[0] + x[1]*y[1]) & 1


def support_mask(S):
    return sum(1<<i for i in S)


def hcolor(S):
    return (
        len(S & D1) & 1,
        len(S & D2) & 1,
    )


def dvector(S):
    return tuple(len(S & A) & 1 for A in OPPOSITE)


def parity(S):
    return len(S) & 1


def base_bit(S):
    return 1 ^ parity(S)


def corrected_bit(S,k):
    h=hcolor(S)
    return base_bit(S) ^ dot(k,h)


def good_set(parts):
    return frozenset(
        k for k in K
        if sum(corrected_bit(S,k) for S in parts)==1
    )


def H0(a):
    return frozenset(k for k in K if dot(k,a)==0)


def H1(a):
    return frozenset(k for k in K if dot(k,a)==1)


def w_of_k(k):
    a,b=k
    return (1^a^b, 1^a, 1^b)


def verify_f2_3_normal_form():
    assert {w_of_k(k) for k in K} == {
        (1,1,1),(1,0,0),(0,1,0),(0,0,1)
    }

    for mask in range(64):
        S=frozenset(i for i in range(6) if (mask>>i)&1)
        d=dvector(S)
        p=parity(S)
        h=hcolor(S)

        assert p == (d[0]^d[1]^d[2])
        assert h == (d[0]^d[1], d[0]^d[2])

        for k in K:
            w=w_of_k(k)
            rhs=1 ^ (
                (w[0]&d[0]) ^
                (w[1]&d[1]) ^
                (w[2]&d[2])
            )
            assert corrected_bit(S,k)==rhs

    # Every support partition at a check gives d0 xor d1 xor d2 = 000.
    for assignment in product(range(3),repeat=6):
        parts=[
            frozenset(i for i,x in enumerate(assignment) if x==j)
            for j in range(3)
        ]
        ds=[dvector(S) for S in parts]
        assert tuple(ds[0][i]^ds[1][i]^ds[2][i] for i in range(3))==(0,0,0)


def build_source():
    # adjacency as sets; variables/checks are global integer ids 0..26.
    vnbr=[set() for _ in range(27)]
    support=[None]*27

    for comp in range(3):
        voff=9*comp
        coff=9*comp
        for v,c in PAPPUS_EDGES:
            vnbr[voff+v].add(coff+c)

        for v in range(9):
            cls=next(i for i,C in enumerate(PAPPUS_COVERS) if v in C)
            support[voff+v]=GROUPS[comp][cls]

    # Support-preserving switch 1:
    # comp0 v2/support{4} with comp1 v2/support{4}, both at local c1.
    u,v=2,9+2
    a,b=1,9+1
    assert support[u]==support[v]==frozenset({4})
    assert a in vnbr[u] and b in vnbr[v]
    vnbr[u].remove(a); vnbr[v].remove(b)
    vnbr[u].add(b); vnbr[v].add(a)

    # Support-preserving switch 2:
    # comp1 v1/support{3,5} at c0 with comp2 v2/support{3,5} at c1.
    u,v=9+1,18+2
    a,b=9+0,18+1
    assert support[u]==support[v]==frozenset({3,5})
    assert a in vnbr[u] and b in vnbr[v]
    vnbr[u].remove(a); vnbr[v].remove(b)
    vnbr[u].add(b); vnbr[v].add(a)

    return tuple(frozenset(x) for x in vnbr), tuple(support)


def check_neighbors(vnbr):
    cnbr=[set() for _ in range(27)]
    for v,N in enumerate(vnbr):
        for c in N:
            cnbr[c].add(v)
    return tuple(frozenset(x) for x in cnbr)


def verify_source_geometry(vnbr):
    cnbr=check_neighbors(vnbr)

    assert len(vnbr)==len(cnbr)==27
    assert all(len(N)==3 for N in vnbr)
    assert all(len(N)==3 for N in cnbr)

    # C4-free iff two variables share at most one check.
    for i,j in combinations(range(27),2):
        assert len(vnbr[i] & vnbr[j]) <= 1

    # Connected Tanner graph.
    start=("v",0)
    seen=set()
    stack=[start]
    while stack:
        kind,i=stack.pop()
        if (kind,i) in seen:
            continue
        seen.add((kind,i))
        if kind=="v":
            stack.extend(("c",c) for c in vnbr[i])
        else:
            stack.extend(("v",v) for v in cnbr[i])
    assert len(seen)==54

    return cnbr


def verify_six_exact_covers(cnbr,support):
    selected=[]
    for lab in range(6):
        C=frozenset(v for v,S in enumerate(support) if lab in S)
        assert len(C)==9
        assert all(sum(v in C for v in cnbr[c])==1 for c in range(27))
        selected.append(C)
    # The six labels intentionally use three distinct internal covers.
    assert len(set(selected))==3
    return tuple(selected)


def verify_phase_clash(cnbr,support):
    a=(1,0)
    h0=H0(a)
    h1=H1(a)
    full=frozenset(K)

    sigs=[]
    for c in range(27):
        parts=tuple(support[v] for v in cnbr[c])
        # supports are pairwise disjoint and cover the six labels.
        assert set().union(*parts)==set(range(6))
        for A,B in combinations(parts,2):
            assert not (A&B)
        G=good_set(parts)
        sigs.append(G)

        # d-flow conservation at the check.
        ds=[dvector(S) for S in parts]
        assert tuple(ds[0][i]^ds[1][i]^ds[2][i] for i in range(3))==(0,0,0)

    counts=Counter(sigs)
    assert counts==Counter({h0:9, full:9, h1:9})
    assert frozenset() not in counts

    # Build E102 nonzero-h holonomy graph.
    nz=[v for v,S in enumerate(support) if hcolor(S)!=(0,0)]
    adj={v:set() for v in nz}
    for c in range(27):
        xs=[v for v in cnbr[c] if v in adj]
        for u,v in combinations(xs,2):
            adj[u].add(v); adj[v].add(u)

    seen=set()
    stack=[nz[0]]
    while stack:
        v=stack.pop()
        if v in seen:
            continue
        seen.add(v)
        stack.extend(adj[v]-seen)
    assert seen==set(nz)

    allowed=set(K)
    for c,G in enumerate(sigs):
        if any(v in seen for v in cnbr[c]):
            allowed &= set(G)
    assert allowed==set()

    return counts,len(nz)


def enumerate_exact_covers(vnbr,limit=100):
    cnbr=check_neighbors(vnbr)
    out=[]

    def rec(covered,chosen):
        if len(out)>=limit:
            return
        if len(covered)==27:
            out.append(frozenset(chosen))
            return

        best=None
        opts=None
        for c in range(27):
            if c in covered:
                continue
            viable=[
                v for v in cnbr[c]
                if vnbr[v].isdisjoint(covered)
            ]
            if not viable:
                return
            if opts is None or len(viable)<len(opts):
                best,opts=c,viable
                if len(opts)==1:
                    break

        for v in opts:
            rec(covered | set(vnbr[v]), chosen+[v])

    rec(set(),[])
    return tuple(out)


def verify_support_preserving_switch_lemma():
    # A Tanner 2-switch between variables with identical six-witness supports
    # preserves all six exact-cover incidences at the two affected checks:
    # every witness selects either both swapped variables or neither.
    for S in (
        frozenset(),
        frozenset({4}),
        frozenset({3,5}),
        frozenset({0,1,2}),
    ):
        for lab in range(6):
            assert ((lab in S),(lab in S)) in ((False,False),(True,True))



def verify_e92_target6_graft(gadget_vnbr,gadget_support):
    # E92 cluster has checks 0..18 and variables 0..17.  Variable 17=x has
    # only checks 17,18 inside the cluster; its third Equality incidence is
    # the variable-side boundary port V.
    e92_vnbr=[set(t) for t in E92_CUBICS] + [set((17,18))]

    # Append the closed 27x27 E103 gadget with check offset 19.
    vnbr=[set(N) for N in e92_vnbr]
    for N in gadget_vnbr:
        vnbr.append({19+c for c in N})
    support=list(E92_SUPPORTS)+list(gadget_support)

    # Graft through two EMPTY-support variables, so all six target witnesses
    # retain identical selected counts at the switched checks.
    # E92 variable 0: support empty, edge to check 0.
    # Gadget variable 0: support empty, local edge to check 8 -> global 27.
    gv=18
    assert support[0]==support[gv]==frozenset()
    assert 0 in vnbr[0] and 27 in vnbr[gv]
    vnbr[0].remove(0); vnbr[gv].remove(27)
    vnbr[0].add(27); vnbr[gv].add(0)

    cnbr=[set() for _ in range(46)]
    for v,N in enumerate(vnbr):
        for q in N:
            cnbr[q].add(v)

    # Internal degree profile: all ordinary variables cubic, x degree 2 in
    # the cluster because its third incidence is boundary V.
    assert all(len(vnbr[v])==3 for v in range(17))
    assert len(vnbr[17])==2
    assert all(len(vnbr[v])==3 for v in range(18,45))

    # Four check-side boundary checks have internal degree 2; all others 3.
    for q,N in enumerate(cnbr):
        if q in (0,1,2,17):
            assert len(N)==2
        else:
            assert len(N)==3

    # C4-free on the internal Tanner geometry.
    for u,v in combinations(range(45),2):
        assert len(vnbr[u] & vnbr[v]) <= 1

    # Connected internal Tanner graph.
    seen=set(); stack=[("v",0)]
    while stack:
        kind,i=stack.pop()
        if (kind,i) in seen:
            continue
        seen.add((kind,i))
        if kind=="v":
            stack.extend(("c",q) for q in vnbr[i])
        else:
            stack.extend(("v",v) for v in cnbr[i])
    assert len(seen)==45+46

    # Verify the actual six E93 TARGET6 boundary masks remain feasible.
    bpos={0:0,1:1,2:2,17:3}
    for lab,mask in enumerate(TARGET6_MASKS):
        selected={v for v,S in enumerate(support) if lab in S}
        for q,N in enumerate(cnbr):
            count=sum(v in selected for v in N)
            if q in bpos:
                assert count + ((mask>>bpos[q])&1) == 1
            else:
                assert count == 1
        assert (17 in selected) == bool((mask>>4)&1)

    # The gadget's H0/full/H1 check signatures are support-preserved by the
    # empty-support graft.  Its nonzero variables remain in one bad holonomy
    # component (they may only gain extra zero-color adjacency outside).
    gadget_checks=range(19,46)
    sigs=[]
    for q in gadget_checks:
        parts=tuple(support[v] for v in cnbr[q])
        sigs.append(good_set(parts))
    a=(1,0)
    assert Counter(sigs)==Counter({H0(a):9, frozenset(K):9, H1(a):9})

    gadget_nz={18+v for v,S in enumerate(gadget_support) if hcolor(S)!=(0,0)}
    adj={v:set() for v in range(45) if hcolor(support[v])!=(0,0)}
    for q,N in enumerate(cnbr):
        xs=[v for v in N if v in adj]
        for u,v in combinations(xs,2):
            adj[u].add(v); adj[v].add(u)
    start=next(iter(gadget_nz)); reached=set(); stack=[start]
    while stack:
        v=stack.pop()
        if v in reached:
            continue
        reached.add(v); stack.extend(adj[v]-reached)
    assert gadget_nz <= reached

    allowed=set(K)
    for q in gadget_checks:
        if any(v in reached for v in cnbr[q]):
            allowed &= set(good_set(tuple(support[v] for v in cnbr[q])))
    assert allowed==set()

    return tuple(frozenset(N) for N in vnbr),tuple(support)


def main():
    verify_f2_3_normal_form()
    verify_support_preserving_switch_lemma()

    vnbr,support=build_source()
    cnbr=verify_source_geometry(vnbr)
    six=verify_six_exact_covers(cnbr,support)
    counts,nz=verify_phase_clash(cnbr,support)
    verify_e92_target6_graft(vnbr,support)

    allcovers=enumerate_exact_covers(vnbr,limit=100)
    assert len(allcovers)==8
    assert all(C in allcovers for C in six)

    print("R5 E103 signed phase-clash geometry firewall: PASS")
    print("F2^3 exchange-membership normal form verified for all 64 supports")
    print("source=27x27 connected square/cubic/C4-free")
    print("six labeled exact covers are valid; distinct internal covers=3")
    print("rigid checks=0")
    print("Good signatures: H_(1,0)^0=9, unrestricted=9, H_(1,0)^1=9")
    print("nonzero-h variables=",nz,"and form one holonomy component")
    print("component Good intersection=empty")
    print("total exact covers of constructed source=",len(allcovers))
    print("E92 five-port graft: all six actual TARGET6 masks remain feasible in a connected C4-free cluster with the same bad holonomy gadget")
    print("GEOMETRY_ONLY_SIGNED_PHASE_CLASH_KILLER = FALSIFIED")
    print("next leverage: witness minimality / exchange switching / exact no-raw8 parent semantics")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
