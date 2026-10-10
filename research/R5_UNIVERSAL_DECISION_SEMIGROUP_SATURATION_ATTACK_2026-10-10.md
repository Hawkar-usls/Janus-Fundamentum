# Universal Decision-Only Attack: Integer Semigroup Saturation vs Actual Feasibility

Date: 2026-10-10
Authority (before this note): PR #515 branch commit
`c28b77c52b5f00db94bf43ae4c0c5224f25f44d9`.
R5 run `38066950581` = SUCCESS (all 92 steps);
JANUS registry run `38066950539` = SUCCESS.
Referenced canonical executables: E64, E65, E118, E123, SC23 and
the previously integrated universal coefficient checker.

**Absolute goal:** a deterministic worst-case polynomial-time
`SolveLinearCubicXSAT(F)` for every square, cubic, C4-free Positive
Exact-One instance, including SAT+witness and UNSAT.

**Verdict:** attempted alternative decision-only algebraic route;
GLOBAL_NONNEGATIVE_SEMIGROUP_MEMBERSHIP_ALGORITHM = NOT CONSTRUCTED.
No result here implies P=NP. This is an anti-loop audit and is not a
partial solver or a claimed advancement toward the final complexity bound.

## 1. Why a decision-only alternative is needed

The earlier exact coefficient/CRT approach computes the whole witness
**count**, while the goal only needs the Boolean predicate of existence
and, if true, a witness. Exact coefficients, full Hilbert series,
explicit symbolic continuation tables, and complete solution enumeration
can have substantially higher output/construction burdens than a
decision procedure. Do not silently replace the requested decision-only
polynomial theorem by a stronger unproved counting theorem.

A different candidate is *integer semigroup membership*, which retains
the nonnegative integer constraint absent from the E123 all-prime
linear-consistency check.

## 2. General exact semigroup/cokernel identities (proved for ALL inputs)

Let A be the n x n 0/1 incidence matrix, every row and column having
sum three, and let b=(1,...,1). Let its integer column semigroup be

    S(A) = {A x : x in Z_>=0^n}.

Every nonnegative integral solution to A x=b is automatically Boolean:
each row is a sum of three nonnegative integers equal to one, and
every column occurs in three rows. Thus

    ExactOne(A) SAT  <=>  b in S(A).

Independently of SAT, cubicity supplies

    A * 1 = 3 b,
    A * (1/3 * 1) = b.

Hence for every valid input:

    3b in S(A),
    b in rational_nonnegative_cone(A),
    3[b]=0 in coker_Z(A) = Z^n / A Z^n.

Therefore the cokernel class [b] has additive order **either 1 or 3**.
Its order can be computed by polynomial-time Smith normal form over
the integers (with bit-complexity accounting).

If order([b])=3, then UNSAT is rigorously certified: no *integer*
solution exists. But order=1 is NOT sufficient; it merely says b is an
integer lattice combination of columns, possibly with negative
coefficients.

The naively tempting universal normalization rule would be

    if b in (Z A intersect Q_>=0 A) then b in S(A).

This is **false** for this exact input class.

## 3. The E123 counterexample is an explicit order-three semigroup hole

On the frozen q=63 Tutte-12 oriented incidence matrix R:

    rank_Q(R)=49,
    kernel_Q nullity=14,
    ExactOne(R)=UNSAT by complete 2^14 rational-basis replay.

E65 enumerates 252 parity near-models of weight 23. For each, the
three triple-selected checks are the entire support of a unique
selected column v. Subtracting 2 from its selected coefficient changes
that coefficient +1 into -1, and changes the three affected row sums
from 3 to 1, leaving all other 60 sums equal to 1. Therefore there is
an explicitly constructible vector

    z in {-1,0,1}^63,
    exactly one z_v=-1,
    R z=b.

Thus [b]=0 in coker_Z(R), b belongs to the rational nonnegative
column cone (via the uniform 1/3 solution), and b does NOT belong to
S(R) because E64/E123 prove there is no Boolean solution.

In standard affine-semigroup terminology, b is a **hole** of S(R)
inside its normalization `Z R intersect Q_>=0 R`; moreover
`3b=R 1` belongs to S(R). It is a saturation hole witnessed
by a factor of three.

This is exactly why global Smith checks, field-linear checks for
arbitrarily many primes, rational feasibility, and generic
semigroup-normality assumptions cannot decide SUPPORT.

## 4. Essential transpose control, not a disconnected gadget

E65 proves that R^T (the same n=63 Levi graph with the two sides
exchanged) is SAT with exactly 36 Boolean witnesses, while R is UNSAT.

R and R^T have identical Smith invariant factors, rational rank,
determinantal divisors and graph girth. For BOTH orientations,
[b]=0 in the corresponding integer cokernel, and the uniform 1/3
vector lies in the nonnegative rational cone. However

    b not in S(R),
    b in S(R^T).

Therefore neither Smith invariants nor the binary predicate of
saturation membership, even combined with all transpose-invariant
Levi/spectral data, is enough. A successful global algorithm has
to capture the **oriented nonnegative semigroup membership**
obstruction itself, not merely lattice feasibility.

This is a precise refutation of the proposed shortcut, not a
refutation of every possible semigroup algorithm.

## 5. The actual missing *algorithmic* statement

A valid constructive successor would prove:

    GLOBAL_TARGET_SEMIGROUP_MEMBERSHIP

    Given *any* n x n 0/1, 3-regular C4-free incidence A,
    decide in n^{O(1)} bit operations whether 1 is in
    A Z_>=0^n, and, if yes, return its nonnegative integral
    preimage x.

Together with the elementary identity of Section 2 this directly
produces the requested SolveLinearCubicXSAT and its SAT witness.

To make this noncircular one must supply a concrete, polynomially
constructible mechanism: e.g. an oriented hole-separating certificate,
polynomially bounded augmentation system, or direct symbolic
membership computation, **with a proven polynomial cost for all A**.
Merely naming an integer-programming, toric-ideal, Hilbert-basis,
normalization, or Graver-basis oracle is NOT an algorithm. Neither
the number of holes nor the description complexity of their universal
separation has been bounded polynomially.

This construction has NOT been found or proved here. E118 confirms
that the whole input class remains NP-complete.

Literature context on semigroup normalization:
https://doi.org/10.1016/j.disc.2004.07.038
Normality of semigroups with some links to graph theory:
graph edge semigroups have an odd-cycle criterion, but hypergraph
normalization has a substantially more difficult combinatorial
description; no applicable universal polynomial decision theorem was
verified in this sweep.

## 6. Reproduction and provenance

Previously integrated, independent checker commands:

    python experiments/r5_e64_connected_postquotient_nullity_firewall.py
    python experiments/r5_e65_transpose_asymmetry_quantized_defect.py
    python experiments/r5_e118_universal_linear_cubic_exactone_hardness_bridge.py
    python experiments/r5_e123_e64_tutte12_post_e18_kloc3_rebind.py
    python experiments/r5_universal_support_coefficient_extraction_attack.py

The final checker additionally validates 252 integral Ax=b vectors
and their all-189 pinned extension profiles. The new semigroup
conclusions are exact deductions from those executable witnesses,
not new finite benchmark results. No duplicate checker is introduced.

Current real branch R5 after fixing E129's q24 structural-validator
dimension bug: 38066950581 SUCCESS, 92/92 steps.
Registry check: 38066950539 SUCCESS.

## 7. Final claim boundary

UNIVERSAL_SEMIGROUP_FORMULATION = EXACT BUT NOT AN ALGORITHM.
GENERAL_COKERNEL_3_TORSION = PROVED.
SMITH_ORDER_3 => UNSAT = PROVED.
E123_SATURATION_HOLE_WITH_3b_IN_S = PROVED FROM EXISTING CHECKS.
R_VS_R_TRANSPOSE_SEMIGROUP_ORIENTATION = PROVED FROM EXISTING CHECKS.
GLOBAL_POLYNOMIAL_NONNEGATIVE_SEMIGROUP_MEMBERSHIP = OPEN.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT CONSTRUCTED.
P_VS_NP = OPEN.
