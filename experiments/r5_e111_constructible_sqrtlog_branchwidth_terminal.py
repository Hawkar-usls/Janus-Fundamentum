#!/usr/bin/env python3
"""R5 E111: constructible sqrt(log n)-branchwidth terminal.

For the E110 arrangement of active rank-2 subspaces L_c <= W define
    lambda(X) = dim(sum_{c in X} L_c)
              + dim(sum_{c notin X} L_c)
              - dim(W).
This equals dim(W_X intersect W_notX), hence exactly the E110 cut width.

lambda is a symmetric submodular connectivity function and is evaluable by
GF(2) Gaussian elimination in polynomial time.

External theorem (Korhonen-Oum 2026):
branch-width of a connectivity function given by an oracle is FPT with running
time 2^{O(k^2)} * gamma * m^6 log m.

Therefore, whenever the arrangement has branchwidth
    k = O(sqrt(log n)),
a width-k decomposition can itself be found in polynomial time.  E110 then
solves the residual flat-avoidance instance in n*2^{O(k)} poly(n), also
polynomial.

The checker verifies lambda's exact intersection formula, symmetry and
submodularity exhaustively on a small arrangement, and replays E104's balanced
decomposition width<=3.

This is a theorem-plus-literature algorithmic terminal; it does not prove a
universal sqrt(log n) width bound.

P_VS_NP remains OPEN.
"""

from itertools import product

from r5_e110_subspace_arrangement_branch_dp import (
    span_basis,
    span_set,
    intersection_basis,
    balanced_tree,
    leaves,
    BranchDP,
    flat_line_and_character,
)
from r5_e106_affine_unit_propagation_rank2_core import (
    build_e104_flat_sets,
    propagate_explicit,
    all_points,
)


def rank(vecs):
    return len(span_basis(vecs))


def lambda_value(lines,mask):
    m=len(lines)
    left=[]
    right=[]
    for i,L in enumerate(lines):
        (left if ((mask>>i)&1) else right).extend(L)
    allv=left+right
    return rank(left)+rank(right)-rank(allv)


def intersection_width(lines,mask):
    left=[]
    right=[]
    for i,L in enumerate(lines):
        (left if ((mask>>i)&1) else right).extend(L)
    return len(intersection_basis(span_basis(left),span_basis(right)))


def verify_connectivity_function():
    lines=(
        (1,2),
        (2,4),
        (4,8),
        (1,8),
    )
    m=len(lines)
    full=(1<<m)-1

    vals={mask:lambda_value(lines,mask) for mask in range(1<<m)}

    assert vals[0]==0
    for X in range(1<<m):
        assert vals[X]==vals[full^X]
        assert vals[X]==intersection_width(lines,X)

    # Exhaustive submodularity:
    # lambda(X)+lambda(Y) >= lambda(X cap Y)+lambda(X union Y).
    for X in range(1<<m):
        for Y in range(1<<m):
            assert vals[X]+vals[Y] >= vals[X&Y]+vals[X|Y]


def tree_width(lines,tree):
    allidx=leaves(tree)
    width=0

    def rec(node):
        nonlocal width
        if isinstance(node,int):
            S=frozenset({node})
        else:
            rec(node[0]); rec(node[1])
            S=leaves(node)
        if S!=allidx:
            mask=sum(1<<i for i in S)
            width=max(width,lambda_value(lines,mask))
    rec(tree)
    return width


def verify_e104_width():
    vn,support,cn,basis,words,e,flats=build_e104_flat_sets()
    d=len(basis)
    D=all_points(d)
    D2,active,unsat=propagate_explicit(D,flats)
    assert not unsat

    lines=[]
    forbidden=[]
    for B in active:
        L,phi=flat_line_and_character(B,d)
        lines.append(L)
        forbidden.append(phi)

    tree=balanced_tree(range(len(lines)))
    w=tree_width(tuple(lines),tree)

    dp=BranchDP(d,tuple(lines),tuple(forbidden),tree)
    ans,states,w2=dp.solve()
    assert ans
    assert w==w2
    assert w<=3

    return {
        "active_subspaces":len(lines),
        "ambient_rank":d,
        "balanced_tree_width":w,
    }


def verify_complexity_threshold():
    # Symbolic exponent check:
    # k <= C sqrt(log2 n) => 2^(A k^2) <= n^(A C^2).
    # Freeze integer examples.
    for L in (4,9,16,25,36):
        k=int(L**0.5)
        assert k*k<=L
        # with A=C=1: 2^(k^2) <= 2^L = n for n=2^L.
        assert (1<<(k*k)) <= (1<<L)


def main():
    verify_connectivity_function()
    verify_complexity_threshold()
    stats=verify_e104_width()

    print("R5 E111 constructible sqrt-log branchwidth terminal: PASS")
    print("lambda(X)=dim(sum X intersection sum complement), symmetric submodular")
    print("lambda oracle is polynomial via GF(2) rank")
    print("Korhonen-Oum 2026: branchwidth FPT in 2^O(k^2)*gamma*m^6*log m")
    print("therefore k=O(sqrt(log n)) => polynomial decomposition construction")
    print("combine with E110 => polynomial exact flat-avoidance solver")
    print("E104 replay:",stats)
    print("next target: large-width (>sqrt(log n)) Tanner-derived arrangements")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
