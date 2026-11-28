#!/usr/bin/env python3
"""Replay the E83 canonical-twist -> ordinary matroid-intersection gluing identity.

This is an exact set-system replay on the E78 q=6 and q=9 frozen partitions.
It does not implement a generic matroid-intersection algorithm; it verifies the
bijection that makes the deterministic polynomial terminal valid once the
module matroids are supplied by representation/oracle.
"""

from itertools import product

from r5_e78_linear_delta_equality_gluing_meta_solver import (
    Q6_SETS, Q9_SETS, source_matrix, exhaustive_delta_clusters,
    min_max_partition, cluster_labelled_relation, crossing_edges,
    compatible_tuples, exact_one_solutions,
)


def variable_side_boundary(A, mask):
    q=len(A)
    C={i for i in range(q) if (mask>>i)&1}
    V={j for j in range(q) if (mask>>(q+j))&1}
    return frozenset(
        (i,j)
        for j in V
        for i in range(q)
        if A[i][j] and i not in C
    )


def verify(name,A,expected_sizes,expected_count):
    q=len(A)
    rows=exhaustive_delta_clusters(A)
    mm,parts=min_max_partition(q,rows)
    assert sorted(r["size"] for r in parts)==expected_sizes
    relations=[]
    twists=[]
    bases=[]
    for row in parts:
        ground,fam=cluster_labelled_relation(A,row["mask"])
        P=variable_side_boundary(A,row["mask"])
        assert P <= ground
        B=frozenset(F ^ P for F in fam)
        # E83 consequence for these delta modules: all twisted feasible sets
        # are equicardinal (matroid bases).
        assert len({len(x) for x in B})==1
        relations.append(fam); twists.append(P); bases.append(B)

    cut=crossing_edges(A,parts)
    # Under canonical twists, equality of F copies is exactly one B copy per
    # original cut incidence.
    good=[]
    for choice in product(*[tuple(B) for B in bases]):
        if all(sum(e in choice[t] for t in range(len(parts)))==1 for e in cut):
            good.append(choice)

    comp=compatible_tuples(relations)
    exact=exact_one_solutions(A)
    assert len(good)==len(comp)==len(exact)==expected_count

    # Explicit bijection B_t <-> F_t by canonical twist.
    mapped={
        tuple(choice[t] ^ twists[t] for t in range(len(parts)))
        for choice in good
    }
    assert mapped==set(comp)

    print(
        f"{name}: pieces={expected_sizes} cut={len(cut)} "
        f"common_basis_tuples={len(good)} exact={len(exact)} PASS"
    )


def main():
    verify("RXC3_Q6_UNSAT",source_matrix(6,Q6_SETS),[1,1,10],0)
    verify("LINEAR_Q9_SAT",source_matrix(9,Q9_SETS),[1,1,1,15],1)
    print("CANONICAL_TWIST_MATROID_INTERSECTION_GLUING: PASS")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
