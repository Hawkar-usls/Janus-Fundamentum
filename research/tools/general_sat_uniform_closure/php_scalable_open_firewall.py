#!/usr/bin/env python3
"""Scalable OPEN-family firewall for uniform Gaussian implication closure.

Family
------
Take the standard pigeonhole CNF PHP_{k+1}^k (k+1 pigeons, k holes), and
convert each wide positive pigeon clause to 2-XNF using the exact
Andraschko-Danner-Kreuzer XNF->2-XNF step.

For every k>=3, the resulting implication graph has a symbolic four-level DAG:

  level 0: positive R=Y XOR Z linerals, negative Y linerals
  level 1: positive original X linerals
  level 2: negative original X linerals
  level 3: negative R linerals, positive Y linerals

All implication edges go strictly upward.  A label check shows that no node
reaches its own complement.  Thus SCC/failed-lineral closure learns no affine
equation.  With no initial affine equations, uniform Gaussian implication
closure returns OPEN.

Yet PHP_{k+1}^k is UNSAT by the pigeonhole principle.

Size
----
Original variables: k(k+1).
Auxiliary 2-XNF variables: (k+1)(k-2).
Total:
    N_k = 2(k^2-1).

2-XNF clauses:
    M_k = (k+1)(2k^2+3k-6)/2.

The active rank-2 normal system has full rank N_k.  If every line is completed
by its third nonzero vector a XOR b, the represented normal matroid is connected.

Branchwidth firewall
--------------------
Fix one hole.  Its at-most-one clauses contain every pair of the q=k+1
pigeon-coordinate normals.  Their rank-2 leaf subspaces are
    span(e_i,e_j), 1<=i<j<=q,
the complete-graph K_q edge-subspace arrangement.

Any subcubic branch tree on M=C(q,2) leaves has a cut with both sides at least
M/3 leaves.  If S is the set of coordinate vertices occurring on both sides,
all vertices outside S must have the same side type (K_q is complete), hence
the opposite side has all of its >=M/3 edges inside S.  Therefore
    C(|S|,2) >= M/3.
The cut width equals |S|, so branchwidth is at least
    min{s : C(s,2) >= C(q,2)/3} = Omega(q)=Omega(k).

Thus the current low-normal-rank / low-branchwidth exact terminals do not give
a polynomial bound on this explicit infinite OPEN family.

This is a firewall, not a lower bound on SAT and not a proof that every future
uniform rule must branch.
"""

from collections import defaultdict
from itertools import combinations, product
from math import comb

from uniform_gaussian_implication_audit import (
    neg,
    rank_vectors,
    uniform_gaussian_implication_closure,
)


def xor_lineral(a,b):
    return a[0]^b[0], a[1]^b[1]


def php_cnf(k):
    """Standard PHP_{k+1}^k as clauses of ordinary linerals."""
    pigeons=k+1
    idx={(p,h):p*k+h for p in range(pigeons) for h in range(k)}
    clauses=[]

    # Every pigeon uses at least one hole.
    for p in range(pigeons):
        clauses.append(tuple((1<<idx[p,h],0) for h in range(k)))

    # One pigeon cannot occupy two holes.
    for p in range(pigeons):
        for h1,h2 in combinations(range(k),2):
            clauses.append(((1<<idx[p,h1],1),(1<<idx[p,h2],1)))

    # One hole cannot contain two pigeons.
    for h in range(k):
        for p1,p2 in combinations(range(pigeons),2):
            clauses.append(((1<<idx[p1,h],1),(1<<idx[p2,h],1)))

    return tuple(clauses),pigeons*k,idx


def xnf_to_2xnf(cnf,n0):
    """Exact Algorithm-1 style reduction of each clause to at most 2 linerals."""
    out=[]
    nextvar=n0

    for raw in cnf:
        C=list(raw)

        if len(C)==1:
            out.append((C[0],C[0]))
            continue

        while len(C)>2:
            L1,L2=C[0],C[1]
            Y=(1<<nextvar,0)
            nextvar+=1

            # (Y OR NOT L2)
            out.append((Y,neg(L2)))

            # (NOT(Y XOR L1) OR L2)
            out.append((neg(xor_lineral(Y,L1)),L2))

            C=[Y]+C[2:]

        out.append((C[0],C[1]))

    return tuple(out),nextvar


def eval_lineral(l,x):
    m,c=l
    return ((m&x).bit_count()&1)^c


def local_conversion_truth_table(width):
    """Independent local check of one positive width-w OR conversion."""
    assert width>=3
    original=tuple((1<<i,0) for i in range(width))
    converted,n=xnf_to_2xnf((original,),width)
    aux=n-width

    for x in range(1<<width):
        source=any((x>>i)&1 for i in range(width))
        extension=False
        for y in range(1<<aux):
            z=x | (y<<width)
            if all(eval_lineral(a,z) or eval_lineral(b,z) for a,b in converted):
                extension=True
                break
        assert extension==source


def implication_graph(formula):
    nodes=set()
    edges=defaultdict(set)
    for a,b in formula:
        nodes.update((a,neg(a),b,neg(b)))
        edges[neg(a)].add(b)
        edges[neg(b)].add(a)
    return nodes,edges


def reachable(start,edges):
    seen={start}
    stack=[start]
    while stack:
        u=stack.pop()
        for v in edges[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return seen


def verify_graph_closure_stall(formula):
    nodes,edges=implication_graph(formula)

    # Finite replay of the symbolic theorem: no node reaches its complement.
    for u in nodes:
        assert neg(u) not in reachable(u,edges)

    status,eqs,active=uniform_gaussian_implication_closure(formula, max(
        (m.bit_length() for clause in formula for m,_ in clause), default=0
    ))
    assert status=="OPEN"
    assert eqs==tuple()
    assert len(active)==len(formula)

    return active,nodes,edges


def line_points(active):
    lines=[]
    for a,b in active:
        x,y=a[0],b[0]
        assert x and y and x!=y
        lines.append(frozenset((x,y,x^y)))
    return tuple(lines)


def circuit_union_connected(lines):
    adj=defaultdict(set)
    for L in lines:
        a,b,c=tuple(L)
        for u,v in ((a,b),(a,c),(b,c)):
            adj[u].add(v)
            adj[v].add(u)

    start=next(iter(adj))
    seen={start}
    stack=[start]
    while stack:
        u=stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)

    assert seen==set(adj)
    return len(seen)


def width_lower_bound_complete_pair_subarrangement(q):
    M=comb(q,2)
    # Balanced branch-tree cut has at least ceil(M/3) leaves on both sides.
    need=(M+2)//3
    s=0
    while comb(s,2)<need:
        s+=1
    return s


def expected_sizes(k):
    N=2*(k*k-1)
    M=(k+1)*(2*k*k+3*k-6)//2
    return N,M


def verify_php_instance(k):
    assert k>=3

    cnf,n0,idx=php_cnf(k)
    formula,n=xnf_to_2xnf(cnf,n0)
    N,M=expected_sizes(k)
    assert n==N
    assert len(formula)==M

    active,_,_=verify_graph_closure_stall(formula)

    lines=line_points(active)
    normals=[g for L in lines for g in L]

    # Every coordinate direction, original and auxiliary, is visible.
    assert rank_vectors(normals)==n

    # Circuit-overlap connectivity certifies one represented normal component.
    distinct_normals=circuit_union_connected(lines)

    # One fixed hole contains every pair span(e_i,e_j) over q=k+1 pigeons.
    q=k+1
    h=0
    wanted={
        frozenset((1<<idx[p1,h],1<<idx[p2,h],(1<<idx[p1,h])^(1<<idx[p2,h])))
        for p1,p2 in combinations(range(q),2)
    }
    assert wanted <= set(lines)

    width_lb=width_lower_bound_complete_pair_subarrangement(q)

    return {
        "k":k,
        "pigeons":q,
        "holes":k,
        "variables_2xnf":n,
        "clauses_2xnf":len(formula),
        "learned_affine_rank":0,
        "normal_rank":rank_vectors(normals),
        "distinct_line_normals":distinct_normals,
        "normal_component_count":1,
        "clique_subarrangement_leaves":comb(q,2),
        "branchwidth_lower_bound":width_lb,
    }


def main():
    for w in range(3,7):
        local_conversion_truth_table(w)

    receipts=[verify_php_instance(k) for k in range(3,7)]

    print("SCALABLE UNIFORM-CLOSURE OPEN-FAMILY FIREWALL: PASS")
    print("family: standard PHP_{k+1}^k -> exact 2-XNF conversion")
    for r in receipts:
        print(r)
    print("symbolic family facts:")
    print("  UGIC learns no affine equation for every k>=3 (four-level DAG / no complement reachability)")
    print("  source PHP is UNSAT by pigeonhole principle")
    print("  N_k=2(k^2-1), M_k=(k+1)(2k^2+3k-6)/2")
    print("  full-line normal span has rank N_k and is circuit-connected")
    print("  fixed-hole K_{k+1} subarrangement gives branchwidth Omega(k)")
    print("therefore low-rank and low-width polynomial terminals do not close this infinite residue")
    print("GENERAL_SAT_IN_P = NOT_PROVED")
    print("P_VS_NP = OPEN")


if __name__=="__main__":
    main()
