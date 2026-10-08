#!/usr/bin/env python3
"""R5 E113: TARGET6 support-lift / signed-parallel normal firewall.

E112 constructs an abstract NO-RAW8 residual cover from the cycle space of the
12-vertex hexagonal prism.  Its 18 edge normals g_e occur in two vertex lines.
The forbidden marks at the two endpoints are opposite.

E113 restores exact six-witness support information.

Universal identity:
  for a Tanner variable with six-witness support S,
      e(S) = 1 iff |S| is even
  is the E95 raw8 parity candidate bit, and the E105 forbidden local bit is
      f(S) = 1 xor e(S) = |S| mod 2.
Thus f is a VARIABLE-GLOBAL mark: the same variable carries the same forbidden
bit at all three Tanner checks.

Consequences for the E112 prism:
  * the two endpoint occurrences of every abstract edge normal have opposite
    forbidden marks;
  * therefore ONE Tanner variable cannot realize both occurrences;
  * every joint lift must split each of the 18 normal directions into at least
    two distinct Tanner variables with the SAME residual normal and OPPOSITE
    six-support parity: a signed-parallel pair;
  * the 12 prism checks therefore already require at least 36 distinct active
    Tanner variables and leave at least 72 further cubic incidences outside
    those checks.

E113 also constructs a deterministic SUPPORT-ONLY lift:
  * 36 variables / 36 checks;
  * square, cubic, connected, C4-free;
  * every check's three variable supports partition all six witness labels;
  * hence six exact covers exist;
  * the distinguished 12 prism checks realize exactly the E112 endpoint mark
    pattern.

But its actual zero-boundary kernel does NOT realize the E112 normal
identifications: 0/18 prism edge-pairs have equal coordinate normals.

Finally the support-only gadget is grafted by a support-preserving 2-switch
into the real E92 five-port cluster.  The result is connected and C4-free and
all six actual TARGET6 boundary masks remain feasible.  Again 0/18 prism
edge-pairs are residual-normal equal.

Therefore:
  full six-state partition semantics, even with actual TARGET6 boundary
  witnesses, is not by itself the missing contradiction.
The unresolved requirement is the JOINT realization of support marks and
signed-parallel residual normals.

P_VS_NP remains OPEN.
"""

from itertools import combinations
from collections import defaultdict, Counter

TARGET6=(1,2,4,19,21,22)

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

# Two deterministic completion rounds for the support-only prism lift.
ROUND1=(
    (0,7,14),(5,13,20),(11,19,8),
    (6,1,4),(12,3,2),(18,9,17),(23,16,10),(15,21,25),
    (29,24,22),(33,27,31),(26,30,35),(32,34,28),
)
ROUND2=(
    (11,7,20),(0,13,8),(5,19,14),
    (12,1,10),(6,3,17),(15,9,2),(18,16,4),(26,21,28),
    (23,24,31),(32,27,35),(33,30,22),(29,34,25),
)


def gf2_nullspace(rows,n):
    rows=[r for r in rows if r]
    rank=0
    piv=[]
    for col in range(n):
        p=next((i for i in range(rank,len(rows)) if (rows[i]>>col)&1),None)
        if p is None:
            continue
        rows[rank],rows[p]=rows[p],rows[rank]
        for i in range(len(rows)):
            if i!=rank and ((rows[i]>>col)&1):
                rows[i]^=rows[rank]
        piv.append(col)
        rank+=1

    free=[c for c in range(n) if c not in set(piv)]
    basis=[]
    for f in free:
        x=1<<f
        for i,p in enumerate(piv):
            if (rows[i]>>f)&1:
                x |= 1<<p
        basis.append(x)
    return tuple(basis)


def coord_normals(basis,n):
    out=[]
    for v in range(n):
        g=0
        for i,row in enumerate(basis):
            if (row>>v)&1:
                g |= 1<<i
        out.append(g)
    return tuple(out)


def hex_prism():
    E=set()
    for off in (0,6):
        for i in range(6):
            E.add(tuple(sorted((off+i,off+(i+1)%6))))
    for i in range(6):
        E.add((i,6+i))
    return tuple(sorted(E))


def find_even_orientation(edges,nv):
    for bits in range(1<<len(edges)):
        indeg=[0]*nv
        for i,(u,v) in enumerate(edges):
            if (bits>>i)&1:
                indeg[u]+=1
            else:
                indeg[v]+=1
        if all(x%2==0 for x in indeg):
            return bits,tuple(indeg)
    raise AssertionError("no even orientation")


def head_bit(bits,i,vertex,edge):
    u,v=edge
    if (bits>>i)&1:
        return int(vertex==u)
    return int(vertex==v)


def forbidden_from_support(S):
    # E95 bit is 1 for even support. E105 forbidden bit = 1 xor E95 bit.
    e=int(len(S)%2==0)
    return 1^e


def verify_universal_mark_identity():
    for mask in range(64):
        S=frozenset(i for i in range(6) if (mask>>i)&1)
        assert forbidden_from_support(S)==(len(S)&1)


def build_support_only_prism():
    edges=hex_prism()
    orient,indeg=find_even_orientation(edges,12)

    inc_edges={
        v:[i for i,e in enumerate(edges) if v in e]
        for v in range(12)
    }

    variables=[]
    active=[]
    edge_vars=defaultdict(list)
    phi=[]

    vid=0
    for v in range(12):
        es=inc_edges[v]
        marks=tuple(head_bit(orient,e,v,edges[e]) for e in es)
        assert sum(marks)%2==0

        if marks==(0,0,0):
            supps=[
                frozenset({0,1}),
                frozenset({2,3}),
                frozenset({4,5}),
            ]
        else:
            marked=[i for i,b in enumerate(marks) if b]
            unmarked=[i for i,b in enumerate(marks) if not b]
            assert len(marked)==2 and len(unmarked)==1
            supps=[None]*3
            # Shared even support makes a connected six-cover completion possible.
            supps[unmarked[0]]=frozenset({0,1})
            supps[marked[0]]=frozenset({2})
            supps[marked[1]]=frozenset({3,4,5})

        tri=[]
        for e,m,S in zip(es,marks,supps):
            assert forbidden_from_support(S)==m
            variables.append((v,e,S))
            phi.append(m)
            edge_vars[e].append(vid)
            tri.append(vid)
            vid+=1
        active.append(tuple(tri))

    assert vid==36
    assert len(edge_vars)==18
    assert all(len(x)==2 for x in edge_vars.values())

    # E112 has opposite endpoint marks on every prism edge.
    for e,(a,b) in edge_vars.items():
        assert phi[a]^phi[b]==1

    checks=tuple(active)+ROUND1+ROUND2
    assert len(checks)==36

    supports=tuple(x[2] for x in variables)

    # Every check realizes the exact six-state partition condition.
    U=set(range(6))
    for T in checks:
        parts=[supports[v] for v in T]
        assert set().union(*parts)==U
        for A,B in combinations(parts,2):
            assert not (A&B)

    # Square/cubic/linear.
    vn=[set() for _ in range(36)]
    pair_count=Counter()
    for c,T in enumerate(checks):
        assert len(set(T))==3
        for v in T:
            vn[v].add(c)
        for a,b in combinations(T,2):
            pair_count[tuple(sorted((a,b)))]+=1
    assert all(len(N)==3 for N in vn)
    assert max(pair_count.values())==1

    # Connected Tanner graph.
    cn=[set(T) for T in checks]
    seen=set()
    stack=[("v",0)]
    while stack:
        kind,i=stack.pop()
        if (kind,i) in seen:
            continue
        seen.add((kind,i))
        if kind=="v":
            stack.extend(("c",c) for c in vn[i])
        else:
            stack.extend(("v",v) for v in cn[i])
    assert len(seen)==72

    # Six exact covers are induced directly by support membership.
    covers=[]
    for lab in range(6):
        C=frozenset(v for v,S in enumerate(supports) if lab in S)
        assert all(sum(v in C for v in T)==1 for T in checks)
        covers.append(C)

    # Actual zero-boundary kernel normals of this support-only lift.
    rows=[]
    for T in checks:
        r=0
        for v in T:
            r |= 1<<v
        rows.append(r)
    basis=gf2_nullspace(rows,36)
    normals=coord_normals(basis,36)

    equal_pairs=sum(
        normals[a]==normals[b]
        for a,b in edge_vars.values()
    )
    assert equal_pairs==0

    return {
        "edges":edges,
        "orientation":orient,
        "indegree":indeg,
        "variables":variables,
        "supports":supports,
        "checks":checks,
        "vn":tuple(frozenset(N) for N in vn),
        "edge_vars":dict(edge_vars),
        "kernel_basis":basis,
        "normal_equal_pairs":equal_pairs,
        "covers":tuple(covers),
    }


def verify_signed_parallel_requirement(data):
    # In any JOINT E112 lift, the two occurrences of edge e must retain the
    # same abstract residual normal g_e. But their support parities are opposite.
    # They therefore cannot be the same Tanner variable.
    for e,(a,b) in data["edge_vars"].items():
        Sa=data["supports"][a]
        Sb=data["supports"][b]
        assert (len(Sa)&1)^(len(Sb)&1)==1

    # Hence the 36 active prism incidences require 36 distinct variable
    # identities. Cubicity leaves two more incidences per variable.
    active_variables=36
    outside_incidence_stubs=2*active_variables
    assert outside_incidence_stubs==72
    return active_variables,outside_incidence_stubs


def graft_into_e92(data):
    # E92 internal variables 0..16 are cubic. x=17 has only checks 17,18
    # internally; its third edge is the variable-side boundary port V.
    vn=[set(t) for t in E92_CUBICS]+[set((17,18))]
    support=list(E92_SUPPORTS)

    # Append the closed support-only prism: variable offset 18, check offset 19.
    for N,S in zip(data["vn"],data["supports"]):
        vn.append({19+c for c in N})
        support.append(S)

    # Support-preserving 2-switch through support {4,5}.
    # E92 variable 5 has {4,5}; support-only prism variable 8 also has {4,5}.
    a=5
    b=18+8
    qa=3
    qb=33
    assert support[a]==support[b]==frozenset({4,5})
    assert qa in vn[a] and qb in vn[b]
    vn[a].remove(qa)
    vn[b].remove(qb)
    vn[a].add(qb)
    vn[b].add(qa)

    cn=[set() for _ in range(55)]
    for v,N in enumerate(vn):
        for q in N:
            cn[q].add(v)

    # Five-port degree profile.
    assert len(vn)==54 and len(cn)==55
    assert all(len(vn[v])==(2 if v==17 else 3) for v in range(54))
    for q,N in enumerate(cn):
        assert len(N)==(2 if q in (0,1,2,17) else 3)

    # C4-free.
    for u,v in combinations(range(54),2):
        assert len(vn[u]&vn[v])<=1

    # Connected.
    seen=set()
    stack=[("v",0)]
    while stack:
        kind,i=stack.pop()
        if (kind,i) in seen:
            continue
        seen.add((kind,i))
        if kind=="v":
            stack.extend(("c",q) for q in vn[i])
        else:
            stack.extend(("v",v) for v in cn[i])
    assert len(seen)==109

    # All six actual E93 TARGET6 masks remain exact.
    bpos={0:0,1:1,2:2,17:3}
    for lab,mask in enumerate(TARGET6):
        C={v for v,S in enumerate(support) if lab in S}
        for q,N in enumerate(cn):
            count=sum(v in C for v in N)
            if q in bpos:
                assert count+((mask>>bpos[q])&1)==1
            else:
                assert count==1
        assert (17 in C)==bool((mask>>4)&1)

    # Zero-boundary kernel: all check rows plus x=0.
    rows=[]
    for N in cn:
        r=0
        for v in N:
            r |= 1<<v
        rows.append(r)
    rows.append(1<<17)
    basis=gf2_nullspace(rows,54)
    normals=coord_normals(basis,54)

    equal_pairs=0
    for e,(a0,b0) in data["edge_vars"].items():
        a=18+a0
        b=18+b0
        if normals[a]==normals[b]:
            equal_pairs+=1
    assert equal_pairs==0

    return {
        "variables":54,
        "checks":55,
        "kernel_dim":len(basis),
        "normal_equal_pairs":equal_pairs,
    }


def main():
    verify_universal_mark_identity()
    data=build_support_only_prism()
    active_vars,out_stubs=verify_signed_parallel_requirement(data)
    graft=graft_into_e92(data)

    print("R5 E113 TARGET6 support-lift / signed-parallel normal firewall: PASS")
    print("universal identity: E105 forbidden incidence bit = six-support cardinality parity")
    print("E112 prism: all 18 abstract edge normals have opposite endpoint marks")
    print("edge-faithful one-variable-per-normal lift = IMPOSSIBLE")
    print("any joint lift needs at least",active_vars,"distinct active variables and",out_stubs,"additional cubic incidences")
    print("support-only lift: 36x36 connected square/cubic/C4-free with six exact covers")
    print("support-only lift prism normal equalities:",data["normal_equal_pairs"],"/18")
    print("E92 TARGET6 graft:",graft)
    print("actual six TARGET6 masks coexist with the prism support-mark pattern")
    print("but support-only geometry does NOT realize the E112 residual normal identifications")
    print("next target: signed-parallel normal-pair / weight-2 dual-series realization")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
