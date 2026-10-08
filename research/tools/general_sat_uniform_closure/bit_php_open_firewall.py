#!/usr/bin/env python3
"""Bit-pigeonhole scalable firewall beyond UGIC + choice-resource Hall.

For ell>=2 let h=2^ell holes and p=h+1 pigeons.  Pigeon i is represented by
ell Boolean address bits x_{i,b}.  For every pair i<j require their addresses
to differ:

  OR_{b=0}^{ell-1} (x_{i,b} XOR x_{j,b}).

This is native XNF.  By pigeonhole principle it is UNSAT.

Convert each width-ell XNF clause to exact 2-XNF using the same polynomial
conversion used by the uniform-closure audit.

Facts frozen here:
  * UGIC returns OPEN with learned affine rank 0;
  * the one-hot choice/resource Hall terminal returns OPEN;
  * residual normal rank is
        C(p,2)(ell-2) + ell(p-1),
    i.e. all auxiliary coordinates plus the even-difference subspace in each
    bit layer;
  * the represented normal matroid is connected.  Connectivity is certified
    by:
      - every active rank-2 clause line as a 3-circuit;
      - for each bit b and pigeon triple i,j,k,
            d_ij,b + d_jk,b + d_ik,b = 0,
        a graphic triangle circuit of K_p.

Thus BPHP is an explicit infinite high-rank connected residue after the
Gaussian implication and simple Hall terminals.

This is a firewall only.  It does not prove SAT requires superpolynomial time.
"""

from itertools import combinations

from php_scalable_open_firewall import xnf_to_2xnf
from uniform_gaussian_implication_audit import (
    rank_vectors,
    uniform_gaussian_implication_closure,
)
from choice_resource_hall_terminal import hall_terminal


def bphp_xnf(ell):
    holes=1<<ell
    pigeons=holes+1
    n0=pigeons*ell

    def bitvar(p,b):
        return p*ell+b

    clauses=[]
    diffs={}
    for i,j in combinations(range(pigeons),2):
        C=[]
        for b in range(ell):
            L=((1<<bitvar(i,b))^(1<<bitvar(j,b)),0)
            diffs[(i,j,b)]=L[0]
            C.append(L)
        clauses.append(tuple(C))
    return tuple(clauses),n0,diffs,pigeons,holes


def line_points(formula):
    out=[]
    for a,b in formula:
        x,y=a[0],b[0]
        assert x and y and x!=y
        out.append(frozenset((x,y,x^y)))
    return tuple(out)


def circuit_connectivity(formula,diffs,pigeons,ell):
    # Ground set = distinct nonzero normals visible in the represented system.
    lines=line_points(formula)
    ground=set(g for L in lines for g in L)

    adj={g:set() for g in ground}

    def join_circuit(C):
        C=[g for g in C if g]
        assert len(C)>=2
        root=C[0]
        for g in C[1:]:
            adj[root].add(g)
            adj[g].add(root)

    # Clause rank-2 lines.
    for L in lines:
        join_circuit(tuple(L))

    # Graphic triangle circuits inside each address-bit K_p difference system.
    for b in range(ell):
        for i,j,k in combinations(range(pigeons),3):
            a=diffs[(i,j,b)]
            c=diffs[(j,k,b)]
            d=diffs[(i,k,b)]
            assert a^c^d==0
            assert {a,c,d} <= ground
            join_circuit((a,c,d))

    start=next(iter(ground))
    seen={start}
    stack=[start]
    while stack:
        u=stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)

    assert seen==ground
    return len(ground)


def expected_sizes(ell):
    holes=1<<ell
    pigeons=holes+1
    pairs=pigeons*holes//2
    aux=pairs*max(0,ell-2)
    N=pigeons*ell+aux
    M=pairs if ell==2 else pairs*(2*ell-3)
    normal_rank=aux + ell*(pigeons-1)
    return N,M,normal_rank


def verify_instance(ell):
    source,n0,diffs,pigeons,holes=bphp_xnf(ell)
    formula,n=xnf_to_2xnf(source,n0)

    N,M,R=expected_sizes(ell)
    assert n==N
    assert len(formula)==M

    # Source UNSAT theorem is pigeonhole: p=holes+1 distinct ell-bit strings
    # would inject p objects into exactly holes=2^ell addresses.
    assert pigeons==holes+1

    status,eqs,active=uniform_gaussian_implication_closure(formula,n)
    assert status=="OPEN"
    assert eqs==tuple()
    assert len(active)==len(formula)

    # The source is XNF, not the one-hot ordinary-CNF macro recognized by the
    # scoped Hall detector.
    hall=hall_terminal(source)
    assert hall["status"]=="OPEN"

    lines=line_points(active)
    normals=[g for L in lines for g in L]
    r=rank_vectors(normals)
    assert r==R

    ground=circuit_connectivity(active,diffs,pigeons,ell)

    return {
        "ell":ell,
        "holes":holes,
        "pigeons":pigeons,
        "variables_2xnf":n,
        "clauses_2xnf":len(formula),
        "UGIC":"OPEN",
        "learned_affine_rank":0,
        "Hall_terminal":"OPEN",
        "normal_rank":r,
        "distinct_normal_elements":ground,
        "normal_component_count":1,
    }


def main():
    receipts=[verify_instance(ell) for ell in range(2,5)]

    print("BIT-PIGEONHOLE UNIFORM-CLOSURE FIREWALL: PASS")
    for r in receipts:
        print(r)
    print("symbolic source theorem: 2^ell+1 distinct ell-bit addresses into 2^ell holes is impossible")
    print("UGIC and simple choice-resource Hall both leave the family OPEN")
    print("normal rank grows as C(p,2)(ell-2)+ell(p-1)")
    print("represented normal matroid is connected by clause-line + K_p bit-layer triangle circuits")
    print("unrestricted parity-resolution saturation is NOT licensed as polynomial closure")
    print("GENERAL_SAT_IN_P = NOT_PROVED")
    print("P_VS_NP = OPEN")


if __name__=="__main__":
    main()
