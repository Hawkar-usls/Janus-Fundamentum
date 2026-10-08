#!/usr/bin/env python3
"""Scalable 5-chromatic Kneser firewall for the graph-quotient closure stack.

Family
------
For every k>=4 let

    G_k = KG(2k+3,k),

whose vertices are the k-subsets of [2k+3], adjacent iff disjoint.

External theorem inputs (source-first, not rediscovered numerically):
  * Lovasz 1978: chi(KG(n,k)) = n-2k+2 for n>=2k.
    Hence chi(G_k)=5.
    DOI 10.1016/0097-3165(78)90022-5.
  * Watkins 1970 / standard Kneser connectivity consequence:
    vertex connectivity of KG(n,k), n>2k, equals its regular degree
        C(n-k,k).
    DOI 10.1016/S0021-9800(70)80005-9.

Elementary consequences proved/frozen here:
  * n=2k+3 < 3k for k>=4, so G_k is triangle-free.
  * degree d_k=C(k+3,k)=C(k+3,3) >=35.
  * therefore kappa(G_k)=d_k>4: no separator of size <=4.
  * no nonadjacent neighborhood domination is possible:
      for distinct intersecting k-sets A,B choose b in B\A and extend {b}
      to a k-set C subseteq complement(A); then C is adjacent to A but not B.
  * every vertex has degree >4, so degree<=3 peeling / Brooks Delta<=4
    terminals do not fire.
  * triangle-free implies no K5 obstruction.

For the exact 4-color 2-XNF encoding F_G:
  * variables = 2|V|;
  * clauses   = |E|;
  * F_G is UNSAT because chi(G_k)=5;
  * normal span rank = 2(|V|-1), since G_k is connected and each bit layer
    spans the even-difference space.

Thus the quotient-structural portfolio has an explicit infinite high-rank,
high-connectivity, domination-free family.  This does NOT prove that every
other affine/Gaussian closure layer returns OPEN on the whole family; it is a
firewall specifically against completing the proof by graph critical-core,
Brooks, domination, or bounded-size separator rules alone.

GENERAL_SAT_IN_P is NOT proved. P_VS_NP remains OPEN.
"""

from itertools import combinations
from math import comb


def params(k):
    assert k>=4
    n=2*k+3
    V=comb(n,k)
    d=comb(n-k,k)  # = C(k+3,k) = C(k+3,3)
    assert d==comb(k+3,3)
    assert n<3*k
    E=V*d//2
    chi=n-2*k+2
    assert chi==5
    kappa=d
    return {
        "k":k,
        "ground_n":n,
        "vertices":V,
        "degree":d,
        "edges":E,
        "chromatic":chi,
        "triangle_free":True,
        "vertex_connectivity":kappa,
        "separator_le4":False,
        "2xnf_variables":2*V,
        "2xnf_clauses":E,
        "normal_rank":2*(V-1),
    }


def vertices(k):
    n=2*k+3
    return tuple(combinations(range(n),k))


def exact_k4_control():
    """Finite independent structural replay for the first family member."""
    k=4
    vs=vertices(k)
    N=len(vs)
    assert N==330
    sets=tuple(frozenset(x) for x in vs)

    adj=[set() for _ in range(N)]
    for i in range(N):
        A=sets[i]
        for j in range(i+1,N):
            if A.isdisjoint(sets[j]):
                adj[i].add(j); adj[j].add(i)

    d=comb(7,4)
    assert d==35
    assert all(len(A)==d for A in adj)

    # Triangle-free replay.
    for u in range(N):
        Nu=adj[u]
        assert all(v not in adj[w] for v,w in combinations(Nu,2))

    # Exact no-domination replay for every nonadjacent pair.
    checked=0
    for u in range(N):
        for v in range(u+1,N):
            if v in adj[u]:
                continue
            assert not (adj[u] <= adj[v])
            assert not (adj[v] <= adj[u])
            checked+=1

    return {
        "vertices":N,
        "degree":d,
        "edges":sum(map(len,adj))//2,
        "nonadjacent_pairs_checked":checked,
        "triangle_free":True,
        "domination_free":True,
    }


def verify_symbolic_family():
    rows=[params(k) for k in range(4,11)]
    for r in rows:
        assert r["degree"]>4
        assert r["vertex_connectivity"]>4
        assert r["normal_rank"]==r["2xnf_variables"]-2
        assert r["chromatic"]==5
    return rows


def main():
    first=exact_k4_control()
    rows=verify_symbolic_family()

    print("KNESER 5-CHROMATIC GRAPH-QUOTIENT FIREWALL: PASS")
    print("first exact structural control:",first)
    for r in rows:
        print(r)
    print("external theorem inputs: Lovasz chi(KG(n,k))=n-2k+2; Kneser vertex connectivity=degree")
    print("family consequence: triangle-free 5-chromatic, domination-free, kappa>4, Delta>4 for all k>=4")
    print("C11 separator<=4 + low-degree + domination + Brooks stack cannot close this infinite family")
    print("this does NOT claim pairwise Gaussian closure stalls for every k")
    print("GENERAL_SAT_IN_P = NOT_PROVED")
    print("P_VS_NP = OPEN")


if __name__=="__main__":
    main()
