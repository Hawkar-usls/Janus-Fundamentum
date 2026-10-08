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
  * the represented normal matroid on the ACTUAL 2-XNF ground normals is
    connected.  This must be checked on the represented matroid itself:
    source difference vectors may be only linear combinations inside a
    conversion block and need not individually occur as ground elements.

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


def independent_basis(vecs):
    piv={}
    B=[]
    for x in vecs:
        y=x
        while y:
            p=y.bit_length()-1
            if p in piv:
                y ^= piv[p]
            else:
                piv[p]=y
                B.append(x)
                break
    return tuple(B)


def elimination_for_basis(B):
    piv={}
    for i,x in enumerate(B):
        y=x
        coeff=1<<i
        while y:
            p=y.bit_length()-1
            if p in piv:
                row,cm=piv[p]
                y ^= row
                coeff ^= cm
            else:
                piv[p]=(y,coeff)
                break
        assert y
    return piv


def coords_in_basis(x,B,piv=None):
    if piv is None:
        piv=elimination_for_basis(B)
    y=x
    coeff=0
    for p in sorted(piv,reverse=True):
        if (y>>p)&1:
            row,cm=piv[p]
            y ^= row
            coeff ^= cm
    assert y==0
    return coeff


def represented_matroid_components(vecs):
    """Exact connected components of the represented binary vector matroid."""
    elems=tuple(sorted(set(v for v in vecs if v)))
    B=independent_basis(elems)
    piv=elimination_for_basis(B)
    basis_set=set(B)

    adj={v:set() for v in elems}
    for e in elems:
        coeff=coords_in_basis(e,B,piv)
        support=[B[i] for i in range(len(B)) if (coeff>>i)&1]

        if e in basis_set and support==[e]:
            continue

        # e together with the basis vectors in its representation contains
        # the fundamental circuit (for a nonbasis e it is exactly that
        # circuit; duplicate vectors produce the expected parallel circuit).
        nodes=list(set(support)|{e})
        if len(nodes)>=2:
            root=nodes[0]
            for v in nodes[1:]:
                adj[root].add(v)
                adj[v].add(root)

    comps=[]
    seen=set()
    for s in elems:
        if s in seen:
            continue
        C=set()
        stack=[s]
        while stack:
            x=stack.pop()
            if x in C:
                continue
            C.add(x)
            seen.add(x)
            stack.extend(adj[x]-C)
        comps.append(frozenset(C))

    ranks=[len(independent_basis(C)) for C in comps]
    assert sum(ranks)==len(B)
    return tuple(comps),tuple(ranks)



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

    comps,component_ranks=represented_matroid_components(normals)
    assert len(comps)==1
    ground=len(set(normals))

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
        "normal_component_count":len(comps),
        "normal_component_ranks":component_ranks,
    }


def main():
    receipts=[verify_instance(ell) for ell in range(2,5)]

    print("BIT-PIGEONHOLE UNIFORM-CLOSURE FIREWALL: PASS")
    for r in receipts:
        print(r)
    print("symbolic source theorem: 2^ell+1 distinct ell-bit addresses into 2^ell holes is impossible")
    print("UGIC and simple choice-resource Hall both leave the family OPEN")
    print("normal rank grows as C(p,2)(ell-2)+ell(p-1)")
    print("represented normal matroid on actual ground normals is connected by exact fundamental-circuit decomposition")
    print("unrestricted parity-resolution saturation is NOT licensed as polynomial closure")
    print("GENERAL_SAT_IN_P = NOT_PROVED")
    print("P_VS_NP = OPEN")


if __name__=="__main__":
    main()
