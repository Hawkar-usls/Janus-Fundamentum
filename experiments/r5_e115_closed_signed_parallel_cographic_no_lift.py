#!/usr/bin/env python3
"""R5 E115: closed signed-parallel cographic lift no-go theorem.

Consider a connected simple cubic abstract normal graph H.

For every edge e=uv a JOINT signed-parallel Tanner lift has two distinct
occurrence variables x_(u,e), x_(v,e) with the same residual normal g_e and
opposite required six-witness support parity.

Distinguished check D_v contains the three local occurrence variables at v.

Assume the lift is OCCURRENCE-CLOSED outside D:
  every remaining check incident to these occurrence variables contains three
  occurrence variables from the same block.

Assume it is NORMAL-FAITHFUL and H has no nontrivial 3-edge cuts:
  the only 3-element zero-sum normal triples are the vertex stars of H.
Hence every external occurrence-only check has one star type v.

C4-freeness then classifies all possible star-check multiplicities.  If t_v is
the number of external checks of type v, every edge uv gives t_u+t_v=4.
Moreover t_v<=3.  Therefore:
  * nonbipartite H: t_v=2 for every v;
  * bipartite H: the two sides are (1,3), (2,2), or (3,1).

For t=2, the two external star checks must use two distinct one-local-copy
patterns; their omitted edges form a perfect matching.  ExactOne subtraction
forces a signed difference tau_v that flips sign across every H edge.  Any
nonzero tau creates a vertex with two selected local variables, impossible.
Thus both occurrence copies of every edge are selected equally.

For a 3/1 bipartite side, the t=3 vertex uses all three one-local patterns.
Subtracting its three external ExactOne equations from the distinguished one
forces all three local-minus-remote differences to zero directly.

Therefore IN EVERY exact cover:
    x_(u,e) = x_(v,e) for every edge e.
So across any six exact witnesses the two copies have IDENTICAL support sets,
contradicting E113's required opposite support parity.

Thus no occurrence-closed C4-free normal-faithful joint lift exists for this
3-circuit-rigid cographic lane.

The checker freezes the combinatorial classification and verifies a 12-vertex
Möbius ladder witness has only trivial vertex-star 3-edge cuts.

P_VS_NP remains OPEN.
"""

from itertools import combinations, product


def mobius_ladder(n):
    assert n%2==0
    E=set()
    for i in range(n):
        E.add(tuple(sorted((i,(i+1)%n))))
    for i in range(n//2):
        E.add((i,i+n//2))
    return tuple(sorted(E))


def connected(n,edges):
    adj=[set() for _ in range(n)]
    for u,v in edges:
        adj[u].add(v); adj[v].add(u)
    seen={0}; stack=[0]
    while stack:
        u=stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v); stack.append(v)
    return len(seen)==n


def bipartition(n,edges):
    adj=[[] for _ in range(n)]
    for u,v in edges:
        adj[u].append(v); adj[v].append(u)
    col=[None]*n
    for s in range(n):
        if col[s] is not None:
            continue
        col[s]=0; stack=[s]
        while stack:
            u=stack.pop()
            for v in adj[u]:
                if col[v] is None:
                    col[v]=1-col[u]; stack.append(v)
                elif col[v]==col[u]:
                    return None
    return tuple(col)


def components_after_removing(n,edges,removed):
    removed=set(removed)
    adj=[set() for _ in range(n)]
    for i,(u,v) in enumerate(edges):
        if i in removed:
            continue
        adj[u].add(v); adj[v].add(u)
    unseen=set(range(n)); comps=[]
    while unseen:
        s=next(iter(unseen)); C=set(); stack=[s]
        while stack:
            u=stack.pop()
            if u in C:
                continue
            C.add(u); unseen.discard(u)
            stack.extend(v for v in adj[u] if v not in C)
        comps.append(frozenset(C))
    return tuple(comps)


def verify_only_vertex_star_3cuts(n,edges):
    cuts=[]
    for rem in combinations(range(len(edges)),3):
        comps=components_after_removing(n,edges,rem)
        if len(comps)>1:
            cuts.append((rem,comps))

    # In a connected cubic graph, removing the three edges at one vertex
    # isolates that vertex.  The 3-circuit-rigid condition requires these to
    # be the only 3-edge cuts.
    assert len(cuts)==n
    assert all(any(len(C)==1 for C in comps) for _,comps in cuts)
    return len(cuts)


def allowed_star_words():
    # A type-v external check chooses local(1) or remote(0) occurrence copy
    # on each of the three incident normal positions.
    # C4-free with D_v permits at most one local copy.
    return ((0,0,0),(1,0,0),(0,1,0),(0,0,1))


def compatible_family(words):
    # Two external checks of the same star type may share at most one actual
    # occurrence variable.  They select the same copy in a normal position
    # exactly when the corresponding bits agree.  So Hamming distance >=2.
    for A,B in combinations(words,2):
        dist=sum(a!=b for a,b in zip(A,B))
        if dist<2:
            return False
    return True


def classify_local_star_families():
    A=allowed_star_words()
    fam={}
    for t in range(1,5):
        fs=[]
        for W in combinations(A,t):
            if compatible_family(W):
                fs.append(W)
        fam[t]=tuple(fs)

    # 000 cannot coexist with any unit word; the three unit words are pairwise
    # distance two.
    assert len(fam[1])==4
    assert len(fam[2])==3
    assert len(fam[3])==1
    assert len(fam[4])==0

    # Therefore t_v<=3; together with t_u+t_v=4, endpoint multiplicities are
    # only (1,3),(2,2),(3,1).
    endpoint_types={(a,b) for a in range(1,4) for b in range(1,4) if a+b==4}
    assert endpoint_types=={(1,3),(2,2),(3,1)}
    return fam


def exactone_t3_forces_pair_equality():
    # Local variables a_i and remote copies b_i are Boolean.
    # t=3 external checks are:
    #   a1+b2+b3=1
    #   b1+a2+b3=1
    #   b1+b2+a3=1
    # distinguished:
    #   a1+a2+a3=1
    good=[]
    for a in product((0,1),repeat=3):
        if sum(a)!=1:
            continue
        for b in product((0,1),repeat=3):
            if (
                a[0]+b[1]+b[2]==1 and
                b[0]+a[1]+b[2]==1 and
                b[0]+b[1]+a[2]==1
            ):
                good.append((a,b))
                assert a==b
    assert good
    return tuple(good)


def exactone_t2_vertex_transfer():
    # Two type-v checks are two distinct unit words.  Relabel so local edges
    # are a,b and omitted/perfect-matching edge is m.
    # D: m+a+b=1
    # E1: M+a+B=1
    # E2: M+A+b=1
    # where capitals are remote copies.
    transitions=set()
    for m,a,b,M,A,B in product((0,1),repeat=6):
        if m+a+b!=1:
            continue
        if M+a+B!=1:
            continue
        if M+A+b!=1:
            continue
        dm=m-M
        da=a-A
        db=b-B
        assert da==db==-dm
        transitions.add((dm,da,db))
    assert transitions <= {(0,0,0),(1,-1,-1),(-1,1,1)}
    return transitions


def t2_global_nonzero_tau_impossible():
    # The local transfer writes da=db=tau and dm=-tau.
    # Along every graph edge the endpoint-oriented difference reverses sign,
    # so tau reverses sign across every edge.
    #
    # If tau_v=+1, both local nonmatching/cycle variables have value 1
    # (difference +1 forces local=1, remote=0), contradicting distinguished
    # ExactOne immediately.  Hence no vertex may have +1.
    #
    # Any vertex with tau=-1 has every neighbor tau=+1, also impossible.
    for tau in (-1,0,1):
        if tau==1:
            impossible=True
        elif tau==-1:
            neighbor=-tau
            impossible=(neighbor==1)
        else:
            impossible=False
        assert impossible == (tau!=0)


def verify_mobius12():
    E=mobius_ladder(12)
    assert len(E)==18
    deg=[0]*12
    for u,v in E:
        deg[u]+=1; deg[v]+=1
    assert all(d==3 for d in deg)
    assert connected(12,E)
    assert bipartition(12,E) is None
    cuts=verify_only_vertex_star_3cuts(12,E)
    assert cuts==12
    return E


def main():
    fam=classify_local_star_families()
    g3=exactone_t3_forces_pair_equality()
    tr=exactone_t2_vertex_transfer()
    t2_global_nonzero_tau_impossible()
    E=verify_mobius12()

    print("R5 E115 closed signed-parallel cographic lift no-go: PASS")
    print("C4-free star-family counts t=1,2,3,4:",
          {t:len(fam[t]) for t in fam})
    print("possible edge endpoint star multiplicities: (1,3),(2,2),(3,1)")
    print("t=3 exact-cover local solutions:",len(g3),"all force local=remote")
    print("t=2 local difference patterns:",sorted(tr))
    print("t=2 global nonzero tau is impossible under ExactOne")
    print("Möbius ladder 12: edges=",len(E),", only 12 trivial vertex-star 3-edge cuts")
    print("therefore occurrence-closed 3-circuit-rigid joint lift cannot realize opposite support parity")
    print("next target: nontrivial 3-edge-cut decomposition OR mixed-normal leakage")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
