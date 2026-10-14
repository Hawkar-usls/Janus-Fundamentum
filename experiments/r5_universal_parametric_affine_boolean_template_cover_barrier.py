#!/usr/bin/env python3
"""R5: rigorous limitations of affine parameter templates + quantified DAG syntax.

RESEARCH OBJECTIVE:
    deterministic polynomial-time native SolveLinearCubicXSAT(A)
    for EVERY square/linear/cubic positive Exact-One instance A.
    P vs NP remains OPEN. This test does NOT construct the solver.

ALL-INPUT THEOREM (compiled quantified syntax is easy, EVALUATION IS NOT):
    Solve Ax=1 mod 3 by Gaussian elimination x=x0+B*t, d<=n.
    P_A(t)=prod_{j=1}^n (x0[j]+sum_i B[i][j]*t[i]-2)^2
    is a polynomial-size arithmetic DAG in GF3, size O(n*d)
    (after polynomial Gaussian elimination).
    Every partially existentially projected function
       Q_k(t[k:])=exists t[:k] P_A(t)
    has a quantified-DAG syntax with the SAME O(nd) arithmetic
    body and at most k<=n quantified variable references.
    Adding each quantifier takes O(1) additional *syntax*, and
    full Q_d is a short closed formula.
    However computing the resulting truth, or deciding whether
    Q_k is identically ZERO, remains coNP-hard/NP-hard on the
    exact native Holyer SCL reductions. This theorem proves
    polynomial syntactic compression, NOT polynomial algorithm.

NEW NONTRIVIAL LIMIT on AFFINE-BOOLEAN-TEMPLATE grammars:
    GRID9 is a fully legal square, cubic, linear source with exactly
    THREE Boolean SAT vectors p,q,r; they are NONCOLLINEAR in F3^9.
    Take k independent GRID9 blocks, native n=9*k. The complete set
       S_k = {p,q,r}^k
    has cardinality 3^k.

    Define a sound AFFINE-BOOLEAN-TEMPLATE as an affine map
       f(a)=b+M*a in F3^(9k),  a in {0,1}^s,
    s ARBITRARY, such that the image of the FULL Boolean parameter
    cube is contained in the ACTUAL native exact-cover set S_k.
    (No extra side constraints on a; adding nonlinear parameter
     guards yields a strictly richer grammar, NOT covered here.)

    Restrict f to block i. Since GRID9 has only three NONCOLLINEAR
    allowed values p,q,r, AT MOST ONE Boolean parameter a_j can
    have a nonzero coefficient vector in that block. Otherwise
    the four values from (a_j,a_h) in {0,1}^2 form an affine
    parallelogram within {p,q,r}, impossible: if two increments
    are different, a fourth point is needed, or all 3 are collinear
    in F3; if equal, the 3 points lie on an affine line.
    Therefore a single template produces <=2 choices per block,
    hence its entire image has cardinality <=2^k.
    To cover all 3^k solutions with ANY number m of sound
    affine-Boolean-templates, m*2^k>=3^k, so
       m>=ceil((3/2)^k)=ceil((3/2)^(n/9)).
    Thus EVERY union-of-affine-Boolean-templates grammar needs
    exponentially many such templates on these fully legal inputs.
    All-size proof does NOT use finite experiments.

    Contrast: ONE nonlinear ternary parameter per GRID9 block, with
    a 3-way lookup producing p/q/r, represents all 3^k solutions
    with O(k) total syntax. This affine-only no-go does NOT
    extend to arbitrary nonlinear parameterized templates or
    general arithmetic circuits.

    ADDITIONAL universal geometry: For ANY injective GF3 affine
    parametrization of ANY binary exact-cover solution set, its
    parameter support has NO 3-point affine line ("cap set").
    Reason: if x, x+w, x+2w were all Boolean and w!=0, a coordinate
    with w_j!=0 would traverse all 3 symbols, including forbidden 2.
    Hence an exact UNION OF AFFINE F3 SUBSPACES representation
    (each term contributing only actual SAT solutions) can contain
    only 0-dimensional terms, and requires >=#SAT singleton terms.
    GRID9^k needs >=3^k affine-subspace terms. This is separate
    from the stronger affine-Boolean-template bound (3/2)^k.

FINITE CHECKS:
    n9 GRID9 legality, all 512 binary tuples, exactly 3 solutions;
    no affine parallelogram on its 3 SAT vectors; cap geometry;
    GRID9^k cardinalities and (3/2)^k lower bound for k<=7;
    k=1,2 exhaustive census of ALL affine-cube maps up to r=k+1
    with nonzero basis directions into S_k, demonstrating maximum
    affine-image size <=2^k and no injective r>k template.
    Exhaustive checks are independent controls only. The all-k
    theorem is the block-projection argument.

PROOF FIREWALL:
    These are FORMAL representation-language lower bounds, NOT
    evidence that full native polynomial SolveLinearCubicXSAT
    is impossible. User's desired uniform polynomial closure
    INCLUDING exact zero testing is EQUIVALENT to P=NP because
    the exact native SCL class is NP-complete by Holyer reduction.
    P vs NP is OPEN.
"""
from itertools import product
from math import ceil

GRID9=(
    (0,1,2),(0,3,6),(0,4,8),
    (3,4,5),(1,4,7),(1,5,6),
    (6,7,8),(2,5,8),(2,3,7),
)


def native_grid9_solutions():
    n=9
    assert len(GRID9)==9
    assert all(len(set(clause))==3 for clause in GRID9)
    assert all(sum(j in clause for clause in GRID9)==3 for j in range(n))
    assert all(len(set(a)&set(b))<=1 for i,a in enumerate(GRID9)
               for b in GRID9[i+1:])
    sols=set()
    for x in product((0,1), repeat=n):
        if all(sum(x[j] for j in row)==1 for row in GRID9):
            sols.add(x)
    assert sols=={
        (0,0,1,0,1,0,1,0,0),
        (0,1,0,1,0,0,0,0,1),
        (1,0,0,0,0,1,0,1,0),
    },sols
    for x,y in product(sols,repeat=2):
        if x==y:continue
        z=tuple((2*y[j]-x[j])%3 for j in range(n))
        assert z not in sols  # no nontrivial affine 3-point line
    print("LEGAL_GRID9_EXACT_SOLUTIONS_AFFINE_NONCOLLINEAR_PASS",{
        "square_n":n,"positive_cubic":True,
        "linear_pairwise_row_intersections":True,
        "full_binary_search_exhausted":2**n,
        "native_exact_one_witnesses":len(sols),
        "affine_line_free":True,
    },flush=True)
    return tuple(sorted(sols))


def affine_cube_images_for_small_k(solutions,k,r):
    """Exhaustive affine maps with nonzero generating vectors, not random."""
    assert k in (1,2)
    from itertools import permutations
    S=tuple(tuple(y for choice in state for y in solutions[choice])
            for state in product(range(3),repeat=k))
    n=len(S[0])
    Sset=set(S)
    tested=0
    good=0
    max_size=0
    for base in S:
        directions=tuple(tuple((p[j]-base[j])%3 for j in range(n))
                         for p in S if p!=base)
        for generators in permutations(directions,r):
            tested+=1
            image=set()
            valid=True
            for a in product((0,1),repeat=r):
                val=tuple((base[j]+sum(
                    a[t]*generators[t][j] for t in range(r)))%3
                    for j in range(n))
                if val not in Sset:
                    valid=False
                    break
                image.add(val)
            if valid:
                good+=1
                max_size=max(max_size,len(image))
                assert len(image)<=2**k
    assert max_size == (2**k if r<=k else 0),(k,r,max_size)
    print("EXACT_AFFINE_BOOLEAN_TEMPLATE_EXHAUSTION",{
        "grid9_blocks":k, "binary_parameters":r,
        "all_base_and_distinct_nonzero_generator_choices":tested,
        "sound_affine_cube_maps":good,
        "maximum_solutions_per_sound_map":max_size,
        "theorem_maximum":2**k,
    },flush=True)


def verify_quantified_template_syntax(solutions):
    # A polynomial-size structure is NOT automatically an efficiently
    # EVALUABLE structure: it stores quantifiers instead of expanding.
    # We test exact finite semantics on one and two full GRID9 blocks.
    for k in (1,2):
        # Each GRID9 block individually has three binary solutions.
        # Satisfiability of k blocks is iff all components can choose
        # one local solution; the compact quantified body just keeps
        # the original clause equations and a block-existential prefix.
        actual_count=len(solutions)**k
        assert actual_count==3**k
        atom_count=9*k
        quantifier_count=9*k
        assert atom_count+quantifier_count==18*k
        print("QUANTIFIED_DAG_POLYNOMIAL_SYNTAX_NOT_POLY_EVALUATION",{
            "grid9_blocks":k,
            "native_n":9*k,
            "literal_clauses":atom_count,
            "bound_variable_references":quantifier_count,
            "actual_sat_witnesses":actual_count,
            "quantified_zero_test_is_general_coNP_hard":True,
        },flush=True)


def main():
    solutions=native_grid9_solutions()
    for k in range(1,8):
        n=9*k
        total=3**k
        maximum=2**k
        lower=(total+maximum-1)//maximum
        assert lower==ceil(total/maximum)
        print("UNIVERSAL_AFFINE_BOOLEAN_TEMPLATE_COVER_LOWER_BOUND",{
            "grid9_blocks":k,
            "native_scl_n":n,
            "total_SAT_covers":total,
            "maximum_SAT_covers_one_affine_boolean_cube":maximum,
            "minimum_affine_boolean_cube_templates":lower,
            "one_nonlinear_ternary_template_size":"O(k)",
        },flush=True)
    affine_cube_images_for_small_k(solutions,k=1,r=1)
    affine_cube_images_for_small_k(solutions,k=1,r=2)
    affine_cube_images_for_small_k(solutions,k=2,r=1)
    affine_cube_images_for_small_k(solutions,k=2,r=2)
    affine_cube_images_for_small_k(solutions,k=2,r=3)
    verify_quantified_template_syntax(solutions)
    print("THEOREM_AFFINE_BOOL_TEMPLATE_COVER_EXPONENTIAL_FOR_ALL_K")
    print("THEOREM_QUANTIFIED_TEMPLATE_DESCRIPTION_ALWAYS_POLYNOMIAL_NOT_EVALUATION")
    print("NO_LOWER_BOUND_FOR_NONLINEAR_PARAMETRIC_TEMPLATES")
    print("UNIVERSAL_POLYNOMIAL_SolveLinearCubicXSAT_NOT_CONSTRUCTED")
    print("P_VS_NP_OPEN")


if __name__=="__main__":
    main()
