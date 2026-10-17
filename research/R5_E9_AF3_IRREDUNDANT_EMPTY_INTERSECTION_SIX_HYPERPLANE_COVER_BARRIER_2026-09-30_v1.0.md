# R5 E9 — AF3 irredundant empty-intersection six-hyperplane cover barrier

Date: 2026-09-30

Status: `JANUS_EXACT_AFFINE_COVER_BARRIER__DISTINCT_NORMALS_AND_EMPTY_TOTAL_INTERSECTION_STILL_INSUFFICIENT__NO_D1_PROMOTION`

## 1. Motivation

The AF3 source normal form turns UNSAT into coverage of an affine parameter space by coordinate-zero hyperplanes. Source covers have empty total intersection, because a common point would give the zero affine solution `r=0` while `Ar=1`.

The earlier four-hyperplane pencil barrier used a cover with common intersection. This note proves that adding `empty total intersection` still does not yield a dimension-growing cover lower bound.

## 2. Exact six-plane cover in F3^3

Use coordinates `(x,y,z)` over `F3`. Define

```text
H1: z = 0
H2: y = 0
H3: y+z = 0
H4: x = 0
H5: x+y+2z = 1
H6: x+2y+z = 2
```

The normal vectors are

```text
(0,0,1),
(0,1,0),
(0,1,1),
(1,0,0),
(1,1,2),
(1,2,1),
```

and are pairwise projectively distinct over `F3`.

Exact enumeration of all 27 points verifies

\[
\boxed{H_1\cup\cdots\cup H_6=\mathbb F_3^3.}
\]

Their total intersection is empty.

Moreover the cover is irredundant. Private points include:

```text
H1: (1,1,0)
H2: (1,0,2)
H3: (1,2,1)
H4: (0,1,1)
H5: (1,1,1)
H6: (2,1,1)
```

where each displayed point lies on the named hyperplane and on none of the other five.

## 3. Lift to arbitrary dimension

For every `d>=3`, pull the six equations back along the coordinate projection

\[
\pi:\mathbb F_3^d\to\mathbb F_3^3,
\qquad
\pi(\alpha_1,\ldots,\alpha_d)=(\alpha_1,\alpha_2,\alpha_3).
\]

The lifted family still:

```text
covers all of F3^d,
has pairwise projectively distinct normals,
has empty total affine intersection,
is irredundant.
```

Thus all these properties coexist with a constant-size cover independently of dimension.

## 4. Consequence for the AF3 source program

No universal SAT terminal may be inferred merely from

```text
large affine dimension,
empty total intersection,
pairwise projectively distinct coordinate normals,
irredundancy,
absence of a full parallel class.
```

The remaining exploitable information must be genuinely source-specific and global, such as the row identities `ell_i+ell_j+ell_k=1` together with the incidence coupling, or a different decomposition/augmentation invariant.

The separate source-valid infinite UNSAT lift family proves that even adding the local source identities and linear-dimensional parameter spaces still does not force SAT.

## 5. Ceiling

```text
DISTINCT NORMALS + EMPTY TOTAL INTERSECTION + IRREDUNDANCY
=> DIMENSION-GROWING COVER LOWER BOUND
= FALSE

EXPLICIT COVER SIZE
= 6 FOR EVERY d>=3

GENERIC AF3 COVER-SIZE ROUTE
= CLOSED

SOURCE-SPECIFIC GLOBAL CONSTRUCTOR
= OPEN

E8_D1 = EMPTY
P_VS_NP = OPEN
```
