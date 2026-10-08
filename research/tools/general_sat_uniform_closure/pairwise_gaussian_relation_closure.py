#!/usr/bin/env python3
"""Polynomial pairwise Gaussian relation closure for 2-XNF.

Motivation
----------
Two-sided probing learns unary affine facts (and affine equations common to
both sides), but the native language is 2-XNF.  A pair of affine parities may
have one forbidden joint value even when neither parity is individually
forced.

Fix one independent basis B={b_1,...,b_r} of the span of all nonzero normals
present in the input formula.  For every unordered pair b_i,b_j and every
(alpha,beta) in GF(2)^2, run the already-sound polynomial UGIC closure under

    b_i.x = alpha
    b_j.x = beta.

If that assumed context is UNSAT, learn the sound 2-XNF clause

    (b_i.x != alpha) OR (b_j.x != beta).

This is NOT recursive Boolean search.  The probe result is used only to add a
globally valid binary relation.  The solver never commits to one satisfying
probe branch.

There are at most 4*C(r,2) distinct pair-value exclusions.  Every successful
saturation round adds at least one new clause.  Thus at most O(r^2) strict
rounds occur, each making O(r^2) calls to polynomial UGIC plus one polynomial
global two-sided closure.  The deliberately naive implementation is therefore
bounded by one fixed polynomial.

The layer is sound and stronger than unary probing, but is NOT claimed
complete.  It is a parity-aware analogue of enforcing binary/path consistency.

GENERAL_SAT_IN_P is NOT proved.  P_VS_NP remains OPEN.
"""

from itertools import combinations, product

from uniform_gaussian_implication_audit import (
    obstruction_formula,
    uniform_gaussian_implication_closure,
)
from two_sided_gaussian_probe_closure import (
    two_sided_gaussian_probe_closure,
    vec_basis,
)
from php_scalable_open_firewall import php_cnf, xnf_to_2xnf
from bit_php_open_firewall import bphp_xnf
from graph4color_2xnf_firewall import (
    cycle_graph,
    mycielski,
    graph4_xnf,
    exact_k_colorable,
)


def normal_basis(formula):
    normals=tuple(L[0] for C in formula for L in C if L[0])
    return tuple(sorted(vec_basis(normals)))


def unit_equation_clause(mask,value):
    # L=mask.x XOR (1^value) is true exactly when mask.x=value.
    L=(mask,1^value)
    return (L,L)


def exclusion_clause(a,alpha,b,beta):
    # Clause is false exactly on a.x=alpha AND b.x=beta.
    A=(a,alpha)
    B=(b,beta)
    return tuple(sorted((A,B)))


def canonical_formula_set(formula):
    return {
        tuple(sorted(C))
        for C in formula
    }


def pairwise_gaussian_relation_closure(formula,n,max_rounds=None):
    formula=tuple(formula)
    basis=normal_basis(formula)
    existing=canonical_formula_set(formula)
    learned_pair_clauses=[]
    stats={
        "basis_rank":len(basis),
        "ugic_pair_probes":0,
        "strict_clause_rounds":0,
        "learned_pair_clauses":0,
    }

    max_possible=4*(len(basis)*(len(basis)-1)//2)
    if max_rounds is None:
        max_rounds=max_possible+1

    for _round in range(max_rounds):
        # First exploit the already-frozen stronger unary/affine layer.
        status,eqs,active,probe_stats=two_sided_gaussian_probe_closure(formula,n)
        if status!="OPEN":
            stats["unary_probe_calls_last"]=probe_stats["probe_calls"]
            return status,eqs,active,tuple(learned_pair_clauses),stats

        new=[]

        for a,b in combinations(basis,2):
            four_unsat=0
            for alpha,beta in product((0,1),repeat=2):
                C=exclusion_clause(a,alpha,b,beta)
                if C in existing:
                    # Already globally forbidden.
                    four_unsat+=1
                    continue

                assumed=(
                    formula
                    + (unit_equation_clause(a,alpha),)
                    + (unit_equation_clause(b,beta),)
                )
                st,_,_=uniform_gaussian_implication_closure(assumed,n)
                stats["ugic_pair_probes"]+=1

                if st=="UNSAT":
                    new.append(C)
                    four_unsat+=1

            if four_unsat==4:
                # Every valuation of two genuine Boolean parities is excluded.
                return "UNSAT",eqs,active,tuple(learned_pair_clauses+new),stats

        # Deduplicate simultaneous discoveries.
        unique=[]
        seen=set()
        for C in new:
            if C not in existing and C not in seen:
                seen.add(C)
                unique.append(C)

        if not unique:
            stats["unary_probe_calls_last"]=probe_stats["probe_calls"]
            return "OPEN",eqs,active,tuple(learned_pair_clauses),stats

        formula=formula+tuple(unique)
        existing.update(unique)
        learned_pair_clauses.extend(unique)
        stats["strict_clause_rounds"]+=1
        stats["learned_pair_clauses"]=len(learned_pair_clauses)

        assert len(learned_pair_clauses)<=max_possible

    raise AssertionError("pairwise relation saturation exceeded finite clause bound")


def verify_frozen():
    F=obstruction_formula()
    st,E,A,L,S=pairwise_gaussian_relation_closure(F,3)
    assert st=="UNSAT"
    return {
        "status":st,
        "learned_pair_clauses":len(L),
        **S,
    }


def verify_php(k):
    cnf,n0,_=php_cnf(k)
    F,n=xnf_to_2xnf(cnf,n0)
    st,E,A,L,S=pairwise_gaussian_relation_closure(F,n)
    # Source theorem: PHP is UNSAT. Closure may prove it or remain OPEN.
    assert st!="SAT_LINEAR"
    return {
        "k":k,
        "status":st,
        "learned_affine_rank":len(E or ()),
        "active":len(A),
        **S,
    }


def verify_bit_php(ell):
    source,n0,_,p,h=bphp_xnf(ell)
    F,n=xnf_to_2xnf(source,n0)
    st,E,A,L,S=pairwise_gaussian_relation_closure(F,n)
    assert st!="SAT_LINEAR"
    return {
        "ell":ell,
        "pigeons":p,
        "holes":h,
        "status":st,
        "learned_affine_rank":len(E or ()),
        "active":len(A),
        **S,
    }


def verify_graph_controls():
    satG=mycielski(cycle_graph(5))
    assert exact_k_colorable(satG,4)
    F,n=graph4_xnf(satG)
    st,E,A,L,S=pairwise_gaussian_relation_closure(F,n)
    assert st!="UNSAT"

    hard=mycielski(satG)
    assert not exact_k_colorable(hard,4)
    Fh,nh=graph4_xnf(hard)
    sth,Eh,Ah,Lh,Sh=pairwise_gaussian_relation_closure(Fh,nh)
    assert sth!="SAT_LINEAR"

    return {
        "M_C5_4colorable":{
            "status":st,
            "learned_affine_rank":len(E or ()),
            "active":len(A),
            "learned_pair_clauses":len(L),
            **S,
        },
        "M2_C5_not4colorable":{
            "status":sth,
            "learned_affine_rank":len(Eh or ()),
            "active":len(Ah),
            "learned_pair_clauses":len(Lh),
            **Sh,
        },
    }


def main():
    frozen=verify_frozen()
    # Keep scalable controls modest in CI; the theorem/resource bound is
    # symbolic and does not depend on these finite sample sizes.
    php=[verify_php(k) for k in (3,4)]
    bphp=[verify_bit_php(ell) for ell in (2,3)]
    graphs=verify_graph_controls()

    print("PAIRWISE GAUSSIAN RELATION CLOSURE: PASS")
    print("frozen obstruction:",frozen)
    print("PHP:")
    for r in php:
        print(r)
    print("bit-PHP:")
    for r in bphp:
        print(r)
    print("graph quotient controls:",graphs)
    print("resource certificate: <=4*C(r,2) learned pair exclusions; O(r^2) UGIC probes per strict round")
    print("no recursive pair probing and no committed Boolean branch")
    print("GENERAL_SAT_IN_P = NOT_PROVED")
    print("P_VS_NP = OPEN")


if __name__=="__main__":
    main()
