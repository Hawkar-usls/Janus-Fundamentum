# C041 — Proof-Carrying Laminar Affine-Subspace Avoidance

```text
P_VS_NP=OPEN
```

## Purpose

C040 solves Horn/dual-Horn plus affine composition by enumerating the `2^d` assignments of a projected affine interface of dimension `d`.

C041 asks whether the affine coordinates can be factored without enumerating all points.

The exact reformulation is:

```text
CNF satisfiability inside an affine space
= avoidance of a union of affine subspaces.
```

This is the SUB-SAT / union-of-subspaces-avoidance view identified in the primary literature. C041 does not promote the reformulation itself as new.

## Coordinate construction

Let the affine module be `A x = b` over `GF(2)`. Provenance-carrying Gaussian elimination constructs either a contradiction or:

```text
x = p + B lambda,
lambda in GF(2)^d.
```

For a clause `C`, falsifying every literal fixes selected `x_i` values. After substitution these conditions become a linear system in `lambda`.

Define:

```text
U_C = {lambda : clause C is false under x = p + B lambda}.
```

`U_C` is an affine subspace or is empty. Therefore:

```text
F AND (A x = b) is SAT
iff
there exists lambda outside UNION_C U_C.
```

The transformation is exact and witness preserving.

## Admitted class

The nonempty forbidden spaces are laminar when every pair `U,V` satisfies one of:

```text
U intersect V = empty
U subseteq V
V subseteq U.
```

Each relation is decided by Gaussian elimination. If two spaces overlap but neither contains the other, C041 returns `OPEN_NON_LAMINAR` with explicit points witnessing the common intersection and both failed containments.

## Constructive theorem

For a laminar family, remove duplicates and every space contained in another. The remaining maximal spaces are pairwise disjoint.

For a canonical affine system `M lambda = c` of rank `r`:

```text
|Models(M lambda = c)| = 2^(d-r).
```

Hence the number of forbidden points is exactly:

```text
SUM_(maximal U) 2^dim(U).
```

The formula is UNSAT exactly when this sum equals `2^d`. This yields a polynomial UNSAT procedure and certificate without enumerating the affine points.

### SAT witness recovery

When the union does not cover the space, C041 fixes the coordinates of `lambda` one at a time. For each candidate bit value it computes the branch size and the exact number of points covered in that branch by intersecting the prefix with every pairwise-disjoint maximal forbidden subspace.

At least one branch has `covered_points < branch_points`. Choosing it preserves an uncovered point. After `d` steps the remaining singleton is outside every forbidden space and is lifted through `x = p + B lambda` to a complete SAT witness.

## Complexity

For `m` clauses and affine-coordinate dimension `d`:

```text
pairwise laminarity checks       O(m^2)
containment/maximality checks    O(m^2)
greedy witness counting          O(dm)
each primitive                   polynomial GF(2) elimination
certificate volume               polynomial
```

Total work is `O(m^2 * poly(L,d))`. Integers such as `2^d` have only `O(d)` bits. No loop over `2^d` points occurs.

## Proof-carrying records

The certificate records the affine RREF and basis, every clause-forbidden affine system, pairwise disjointness/containment relations, maximal spaces, exact coverage counts, the SAT greedy trace or complete UNSAT cover, explicit budgets, and the lifted witness.

The verifier deterministically rebuilds every object using only `GF(2)` elimination and CNF evaluation. Corrupted records are rejected.

## Frozen audit

```text
450 generated laminar instances       450 EXACT
350 general affine/CNF instances      259 EXACT / 91 OPEN
semantic mismatches                   0
witness failures                      0
verification failures                 0
```

### 128-dimensional controls

```text
complementary forbidden half-spaces
 dimension 128 / maximal spaces 2 / UNSAT

nested forbidden family
 dimension 128 / unique spaces 16 / maximal spaces 1 / SAT
```

Neither control enumerates `2^128` points.

### Negative controls

```text
crossing hyperplanes             -> OPEN_NON_LAMINAR
NAND3+NEQ reduction image        -> OPEN_NON_LAMINAR
contradictory affine system      -> UNSAT
corrupt certificate              -> REJECTED
explicit pair budget exhaustion  -> OPEN_BUDGET
```

## Decisive limitation

On the `{NAND3,NEQ}` image, clause-falsifying subspaces overlap on nonempty regions while neither contains the other. The laminar counting proof fails exactly where nontrivial overlap and inclusion-exclusion begin.

C041 does not show that non-laminar arrangements are hard. It only refuses to claim a polynomial result for the current proof language.

## New gate

```text
NON_LAMINAR_AFFINE_SUBSPACE_UNION_COMPRESSION
```

The next route must compress overlapping incomparable forbidden subspaces through a polynomially discoverable exact representation, such as a bounded intersection poset, structured inclusion-exclusion, decomposable arrangement circuit, or another proof-carrying cover algebra.

## Claim boundary

C041 is a polynomial algorithm for one exact subspace-arrangement class. It does not solve general SUB-SAT, arbitrary CNF, the general NAND3+NEQ image, or P versus NP.
