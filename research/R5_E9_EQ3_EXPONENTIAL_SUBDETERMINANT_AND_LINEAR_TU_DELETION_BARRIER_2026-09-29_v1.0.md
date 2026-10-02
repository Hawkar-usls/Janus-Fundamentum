# R5 E9 — EQ3 exponential subdeterminant and linear TU-deletion barrier

Date: 2026-09-29

Status: `JANUS_DERIVED_ARBITRARY_SIZE_MINOR_BARRIER__BOUNDED_DELTA_AND_CONSTANT_NEAR_TU_ROUTES_CLOSED_ON_HARD_IMAGE__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_LINEAR_CUBIC_EQ3_REGULARIZATION_UNIVERSALITY_2026-09-27_v1.0.md`
- `research/R5_E9_EQ3_LOCAL_GAUGE_QUOTIENT_RETURNS_SOURCE_HARDNESS_2026-09-28_v1.0.md`

Scientific ceiling:

```text
THIS NOTE DOES NOT PROVE P=NP.
IT DOES NOT RULE OUT EVERY POSSIBLE PRECONDITIONER OR REPRESENTATION CHANGE.
IT PROVES THAT THE FROZEN NP-HARD EQ3 REGULARIZED IMAGE IS NOT A
BOUNDED-SUBDETERMINANT FAMILY AND IS NOT O(1)-ROW/COLUMN-DELETION-TO-TU.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Frozen EQ3 gadget

Use terminals `0,1,2` and auxiliaries `3,...,9`, with gadget rows

```text
r0 = (2,5,6)
r1 = (1,4,7)
r2 = (5,7,9)
r3 = (0,3,7)
r4 = (4,6,9)
r5 = (2,4,8)
r6 = (3,8,9)
r7 = (0,5,8)
r8 = (1,3,6)
```

The exact regularizer uses one disjoint copy of these gadget rows and auxiliary columns for every source variable, while the terminal occurrence columns are shared only with the retained source clauses.

## 2. A terminal-free determinant-two minor

Take gadget rows

```text
r0, r2, r4
```

and auxiliary columns

```text
5, 6, 9.
```

The resulting square submatrix is

\[
B=
\begin{pmatrix}
1&1&0\\
1&0&1\\
0&1&1
\end{pmatrix}.
\]

Direct expansion gives

\[
\boxed{\det B=-2.}
\]

Crucially, `B` uses no terminal column. It is entirely internal to one variable gadget.

Therefore every copy of the EQ3 gadget contains its own row/column-disjoint non-TU certificate.

## 3. Exponential subdeterminant on the full hard image

Let the cubic source have `m` variables. The frozen regularizer produces `N=10m` variables and `N=10m` rows.

For each source variable `v`, select the three local gadget rows corresponding to `(r0,r2,r4)` and the three local auxiliary columns corresponding to `(5,6,9)`.

Different gadgets have disjoint selected rows and disjoint selected auxiliary columns. No selected gadget row contains an auxiliary column of another gadget. Hence the union of all selected rows and columns forms a block-diagonal `3m x 3m` submatrix

\[
\operatorname{diag}(B,B,\ldots,B).
\]

Therefore

\[
\boxed{
\left|\det\operatorname{diag}(B^m)\right|=2^m=2^{N/10}.
}
\]

### Theorem EQ3-DET

The exact NP-hard linear-cubic EQ3-regularized image has maximum absolute subdeterminant at least `2^(N/10)`.

Consequently no constant bound `Delta=O(1)` on subdeterminants follows from this representation.

## 4. Linear lower bound on deletion-to-TU

A totally unimodular matrix cannot contain a square submatrix of determinant magnitude two.

The `m` copies of `B` above are pairwise row-disjoint and column-disjoint. A deletion of one row or one column can hit at most one of these frozen copies.

Therefore any set of row/column deletions whose remaining matrix is totally unimodular must hit all `m` copies and has size at least

\[
\boxed{m=N/10.}
\]

### Theorem EQ3-TU-DEL

For the frozen EQ3 regularized image,

```text
minimum number of rows+columns whose deletion can make the matrix TU
>= number of source variables
= N/10.
```

This is a direct packing lower bound from explicit determinant-two minors; it does not rely on complexity assumptions.

Because every network matrix and transpose of a network matrix is totally unimodular, the same certificate rules out obtaining such a matrix merely by deleting `O(1)` rows and columns from the frozen hard image.

## 5. Prior-art boundary

This theorem is used only to scope possible integer-programming donors.

Relevant current literature includes:
- M. Aprile, S. Fiorini, G. Joret, S. Kober, M. T. Seweryn, S. Weltge, Y. Yuditsky, *Integer programs with nearly totally unimodular matrices: the cographic case*, SODA 2025 / Mathematics of Operations Research 2026, DOI `10.1287/moor.2024.0830`. Their positive result assumes that deleting a constant number of rows/columns exposes a transpose-of-network structure.
- Work on congruency-constrained TU and bounded-subdeterminant IP gives powerful polynomial islands under TU/bimodular or related structural promises; those promises are not automatic on the frozen EQ3 image.

The present result does **not** rule out:
- a non-deletion row-equivalent preconditioner;
- a nonlinear representation change;
- a decomposition whose pieces are TU although the whole matrix has large minors;
- a new polynomial Graver-step algorithm exploiting structure other than bounded determinants.

## 6. Consequence for the L1/Graver frontier

The exact odd-L1 / Graver gate cannot be closed merely by asserting that cubic-linearity makes the matrix nearly TU or bounded-determinant.

The NP-hard image itself contains linearly many disjoint determinant-two obstructions and an exponentially large subdeterminant.

Thus the surviving positive target must be stronger and genuinely global, e.g. a polynomial source-trade augmentation rule that tolerates these obstructions rather than deleting a constant number of them.

## 7. Ceiling

```text
INTERNAL EQ3 DET-2 MINOR
= PROVED

m DISJOINT DET-2 MINORS ON m-VARIABLE HARD IMAGE
= PROVED

ABSOLUTE SUBDETERMINANT >= 2^m = 2^(N/10)
= PROVED

ROW/COLUMN DELETION DISTANCE TO TU >= m = N/10
= PROVED

BOUNDED-DELTA AS AUTOMATIC SOURCE PROPERTY
= FALSE

O(1)-DELETION-TO-TU/NETWORK AS AUTOMATIC SOURCE PROPERTY
= FALSE

GLOBAL SOURCE-TRADE / GRAVER AUGMENTATION
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= NOT PROVED

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
