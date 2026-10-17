# R5 E9 — PG15 AF3 affine-implication threshold 8 and NOR return

Date: 2026-10-01

Status:
`JANUS_EXACT_FINITE_AF3_MACRO_TRANSFER_BARRIER__FIRST_IMPLICATION_AT_8__NOR_RETURN__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_PG15_AUGMENTED_TERNARY_FUNDAMENTAL_SUPPORT7_BARRIER_2026-09-30_v1.0.md`
- `research/R5_E9_PALEY_ORBIT_CANONICAL_DIAMOND_CYCLE_AF3_POLYSIZE_COVER_2026-10-01_v1.0.md`

Scientific ceiling:

```text
This is a finite exact transfer test on the frozen PG15_SAT_R11 source.
It proves that the five-coordinate Paley diamond implication mechanism is not
universal in direct AF3 coordinate language.

The residual four-point relation is exactly Boolean NOR after an explicit
coordinate relabelling, but NO source-level NOR composition/universality theorem
is claimed here.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Frozen PG15 source and canonical AF3 chart

Use the canonical PG15 `15 x 15` cubic Exact-One incidence matrix with rows

```text
(1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),
(3,4,7),(3,5,6),(4,9,13),(4,10,14),(5,8,13),
(5,10,15),(6,8,14),(6,9,15),(7,8,15),(7,11,12).
```

Over `F3`, exact elimination gives

```text
rank(A)=11,
dim ker(A)=4,
A r=1 consistent.
```

The checker uses the deterministic free-coordinate chart with free source
coordinates `12,13,14,15` in one-based indexing.  Write

```text
r(alpha)=r0+B alpha,
alpha in F3^4.
```

For source coordinate `i`, let

```text
H_i={alpha : r_i(alpha)=0}.
```

Avoiding a selected coordinate family `I` means

```text
S_I={alpha in F3^4 : r_i(alpha)!=0 for every i in I}.
```

## 2. Affine implication number

Define

```text
kappa(PG15)
=
min {|I| : S_I is nonempty and affdim(S_I)<4}.
```

This quantity is independent of the chosen affine parameterization of the
solution space: changing the particular solution/kernel basis applies an
invertible affine automorphism to `F3^4`, which preserves nonemptiness and
affine dimension of every `S_I`.

An inequality macro can force a nontrivial affine equality only if its avoidance
set has affine dimension below four.  Thus `kappa` is a direct lower bound on
the number of original coordinate inequalities required by any such direct
AF3 affine-implication macro.

## 3. Exhaustive threshold theorem

The checker enumerates all coordinate subsets of the fifteen source columns.
For every

```text
|I| <= 7
```

it obtains

```text
S_I nonempty,
affdim(S_I)=4.
```

Therefore no family of at most seven PG15 coordinate inequalities forces any
nontrivial affine equality in the residual parameter space.

At size eight, exactly eight subsets have affine dimension three.  In zero-based
source-coordinate indexing they are

```text
{0,2,3,6,8,9,12,13}
{1,2,3,6,8,9,12,13}
{2,3,4,6,8,9,12,13}
{2,3,5,6,8,9,12,13}
{2,3,6,7,8,9,12,13}
{2,3,6,8,9,10,12,13}
{2,3,6,8,9,11,12,13}
{2,3,6,8,9,12,13,14}.
```

Equivalently, in one-based indexing they share the seven-coordinate core

```text
C={3,4,7,9,10,13,14}
```

and add exactly one coordinate from

```text
{1,2,5,6,8,11,12,15}.
```

Hence

```text
boxed(kappa(PG15)=8).
```

This exactly falsifies direct transfer of the Paley `K4-e` five-coordinate
implication mechanism to PG15.

## 4. All first implications are the same affine equation

For each of the eight threshold subsets, `S_I` has exactly five points and its
affine hull is the same hyperplane

```text
alpha_0 + alpha_1 + alpha_2 + 2 alpha_3 = 0 mod 3.
```

Thus the first implication is unique up to nonzero scaling of the affine form.

The common seven-coordinate core alone leaves nine points and still spans all
of `F3^4`; adding any one of the eight complementary source coordinates removes
the unique off-hyperplane obstruction and forces the displayed equation.

## 5. Affine closure stops after one dimension

The full-support set

```text
S_[15]
={alpha : every one of the 15 source coordinates is nonzero}
```

has exactly four points:

```text
(1,1,2,1)
(1,2,1,1)
(1,2,2,2)
(2,1,1,1).
```

These four points have affine dimension exactly three and all lie on

```text
alpha_0+alpha_1+alpha_2+2alpha_3=0.
```

Because every full-support point lies in every `S_I`, no coordinate-avoidance
family `I subseteq [15]` can ever have affine dimension below three.
Therefore direct affine-implication closure from original PG15 coordinate
inequalities can reduce the four-dimensional chart by at most one dimension.

This is stronger than the threshold-8 statement: arbitrary larger direct macros
cannot produce a second independent affine equality while preserving all actual
full-support solutions.

## 6. Exact NOR return

On the forced hyperplane,

```text
alpha_3=alpha_0+alpha_1+alpha_2 mod 3.
```

For each of the four full-support points, the first three coordinates lie in
`{1,2}`.  Define Boolean variables

```text
beta_i=alpha_i-1 in {0,1}, i=0,1,2.
```

The four points become

```text
(beta_0,beta_1,beta_2)
=
(0,0,1),
(0,1,0),
(0,1,1),
(1,0,0).
```

This is exactly the graph of the Boolean NOR function:

```text
boxed(beta_0 = NOT(beta_1 OR beta_2)).
```

The checker also reconstructs `r(alpha)` and verifies that every full-support
ternary solution has entries in `{1,2}` and that

```text
x=r-1 in {0,1}^15
```

is an exact Boolean Exact-One model.  There are exactly four such models.

Thus maximal direct affine implication does not yield a linear terminal on
PG15; it exposes a Boolean functional gate.

## 7. Strategic consequence

The new frontier is not to keep increasing fixed affine-macro size blindly.
PG15 shows

```text
Paley five-coordinate diamond propagation
-> not universal;

all direct PG15 affine implications
-> at most one independent equality;

remaining exact full-support relation
-> Boolean NOR.
```

Freeze

```text
R5_E9_PG15_NOR_SOURCE_GEOMETRY_COMPOSITION_GATE_V1.
```

The next admissible question is whether the NOR relation is merely a finite
local residue of PG15 or can be composed through the exact JANUS source geometry
into arbitrary Boolean circuits.  A source-level composition theorem would be
a hardness/representation result, not a solver; a failure could expose the
additional global structure needed for polynomial contraction.

## 8. Ceiling

```text
PG15 AF3 dimension                         = 4
coordinate hyperplanes                     = 15
minimum direct affine-implication size      = 8
number of minimum implication families      = 8
unique first forced affine hyperplane       = alpha0+alpha1+alpha2+2alpha3=0
full-support affine dimension               = 3
second independent direct affine implication = IMPOSSIBLE
full-support affine points                  = 4
Boolean residual                            = EXACT NOR GRAPH
source-level NOR composition theorem        = OPEN
universal polynomial SAT solver             = NOT PROVED
E8_D1                                       = EMPTY
P_VS_NP                                     = OPEN
```
