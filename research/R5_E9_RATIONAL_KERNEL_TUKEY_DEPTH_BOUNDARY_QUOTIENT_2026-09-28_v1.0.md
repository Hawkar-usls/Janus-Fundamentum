# R5 E9 — Rational-Kernel Tukey-Depth Boundary Quotient

Date: 2026-09-28

Status: `JANUS_DERIVED_EXACT_SIGN_TOPE_DEPTH_QUOTIENT__SOURCE_DEPTH_LOWER_BOUND_ONE_THIRD__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_CUBIC_KERNEL_WORD_NORMAL_FORM_2026-09-24_v1.0.md`
- `research/R5_E9_RATIONAL_KERNEL_NULLITY_FPT_ROUTER_2026-09-27_v1.0.md`
- `research/R5_E9_SINGULAR_UNSAT_RANK14_COUNTERCONTROL_2026-09-27_v1.0.md`
- `research/R5_E9_PROJECTIVE_FRACTIONAL_SUPPORT_EXACT_CLOSURE_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_rational_kernel_tukey_depth_boundary.py`

Scientific ceiling:

```text
THIS NOTE GIVES AN EXACT REPRESENTATION CHANGE FROM THE {-1,2} RATIONAL
KERNEL SLICE TO A SIGN / HYPERPLANE-ARRANGEMENT BOUNDARY PROBLEM.

FOR THE SOURCE-GENERATED CONFIGURATION THE ORIGIN HAS HALFSPACE DEPTH AT
LEAST 1/3, AND EXACT-ONE SAT IS EXACTLY THE CASE WHERE THIS LOWER BOUND IS
ATTAINED.

GENERIC EXACT HALFSPACE DEPTH / DENSEST HEMISPHERE / MAXIMUM FEASIBLE
SUBSYSTEM IS NOT A POLYNOMIAL DONOR IN UNBOUNDED DIMENSION.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Cubic square source

Let

```text
A in {0,1}^{n x n}
```

be the incidence matrix of one connected cubic positive Exact-One component.
Every row and every column has exactly three ones, so

```text
A 1 = 3 1,
1^T A = 3 1^T.
```

The source problem is

```text
A x = 1,
x in {0,1}^n.
```

The earlier rational-kernel normal form gives the exact equivalence

```text
A x = 1, x Boolean
iff
there exists y in ker_Q(A) with y in {-1,2}^n,
```

through `y=3x-1`.

The present note proves that at the decision boundary the magnitudes `1` and
`2` are unnecessary: only the sign pattern of a full-support rational kernel
vector matters.

## 2. Sign-count identity

Take any full-support vector

```text
y in ker_Q(A),
y_i != 0 for every i.
```

Let

```text
P(y)={i:y_i>0},
p=|P(y)|.
```

For every source row `e={a,b,c}`,

```text
y_a+y_b+y_c=0.
```

Because no coordinate is zero, the three entries cannot all have the same
sign. Therefore each source row is of exactly one of the two types

```text
ONE_POSITIVE:  +--
TWO_POSITIVE:  ++-
```

(up to magnitudes).

Let `m_1(y)` and `m_2(y)` be the number of rows of these two types. There are
`n` source rows, hence

```text
m_1+m_2=n.
```

Count positive vertex-row incidences in a second way. Every positive coordinate
occurs in exactly three rows, so the total is `3p`. A ONE_POSITIVE row
contributes one positive incidence and a TWO_POSITIVE row contributes two.
Thus

```text
m_1+2m_2=3p.
```

Solving the two equations gives the exact identities

\[
\boxed{m_2(y)=3p-n},
\qquad
\boxed{m_1(y)=2n-3p}.
\]

Since both counts are nonnegative,

\[
\boxed{\frac n3\le p\le\frac{2n}{3}}.
\]

For integer `p`, read the bounds with ceiling/floor when `3` does not divide
`n`.

This is stronger than the old zero-sum identity `sum_i y_i=0`: it controls the
number of positive coordinates of every full-support rational kernel vector,
not merely its coordinate sum.

## 3. Boundary-sign theorem

### Theorem RKTD-1

For a cubic square Exact-One source `A`,

\[
\boxed{
A\text{ is Exact-One SAT}
\iff
\exists y\in\ker_{\mathbb Q}(A)
\text{ with full support and exactly }n/3\text{ positive coordinates}.
}
\]

### Proof: SAT => boundary tope

Let `x` be a Boolean Exact-One witness and put

```text
y=3x-1.
```

Then `Ay=0`, every coordinate of `y` is `2` or `-1`, and cubic regularity gives
`|supp(x)|=n/3`. Hence `y` is full support with exactly `n/3` positive
coordinates.

### Proof: boundary tope => SAT

Let `y in ker_Q(A)` be full support with exactly `p=n/3` positive coordinates.
The sign-count identity gives

```text
m_2(y)=3p-n=0.
```

Therefore every source row contains exactly one positive coordinate. Define

```text
x_i = 1  iff  y_i>0.
```

Then every row of `A` contains exactly one selected coordinate, so

```text
A x = 1.
```

Thus `x` is an Exact-One witness. QED.

### Immediate corollary

If `n mod 3 != 0`, equality `p=n/3` is impossible and the component is UNSAT,
recovering the earlier divisibility terminal.

## 4. Rational kernel as a hyperplane arrangement

Let

```text
d = dim_Q ker(A)
```

and compute a rational kernel-basis matrix

```text
B in Q^{n x d}
```

whose columns span `ker_Q(A)`. Write `b_i in Q^d` for row `i` of `B`. Every
kernel vector has the form

```text
y=B alpha,
```

so

```text
y_i = b_i dot alpha.
```

If some `b_i=0`, then every rational kernel vector has coordinate `i` equal to
zero. RKTD-1 then gives an immediate polynomial UNSAT certificate, because a
SAT witness would yield the full-support vector `3x-1`.

Assume now that every `b_i` is nonzero. The hyperplanes

```text
H_i={alpha:b_i dot alpha=0}
```

form a central rational hyperplane arrangement. Every chamber determines one
full-support sign vector of the rational kernel.

Define its minimum positive chamber count

\[
h(A)=\min_{\alpha:\ b_i\cdot\alpha\ne0\ \forall i}
|\{i:b_i\cdot\alpha>0\}|.
\]

Because `-alpha` reverses every sign, one may orient a chamber so that its
positive side has at most `n/2` points.

The sign-count identity proves the source-specific lower bound

\[
\boxed{h(A)\ge\lceil n/3\rceil}.
\]

When `3|n`, RKTD-1 becomes

\[
\boxed{A\text{ SAT}\iff h(A)=n/3.}
\]

Thus the remaining decision is not an arbitrary threshold: the source itself
proves a universal lower bound and SAT is exactly attainment of that boundary.

## 5. Tukey / halfspace-depth form

For a finite point cloud `B_rows={b_1,...,b_n}` and query point `0`, the
unnormalized Tukey halfspace depth is

\[
HD_0(B)=\min_{u\ne0}|\{i:u\cdot b_i\ge0\}|.
\]

When no row `b_i` is zero, a minimizing direction may be taken away from every
arrangement hyperplane. A direct finite perturbation argument is enough here:
start from any direction, perturb it slightly so all previously strict signs are
unchanged and all zero dot products become nonzero. The new number of positive
points is at most the old number of nonnegative points. Conversely every generic
direction is already allowed in the closed-halfspace minimum. Hence

```text
HD_0(B)=h(A).
```

Therefore, for the source-generated rational-kernel row configuration,

\[
\boxed{HD_0(B)\ge\lceil n/3\rceil}
\]

and, when `3|n`,

\[
\boxed{
A\text{ Exact-One SAT}
\iff
HD_0(B)=n/3.
}
\]

Normalized by `n`, the origin has Tukey depth at least `1/3`, and SAT is exactly
attainment of depth `1/3`.

This is an exact representation-changing quotient of the cubic source into a
central hyperplane-arrangement / oriented-matroid tope problem.

## 6. Defect form

For a full-support kernel vector oriented with `p<=n/2`, define

```text
defect(y)=# source rows of sign type ++-.
```

The identity above gives

\[
\boxed{defect(y)=3p-n.}
\]

Consequently, when `3|n`,

```text
minimum defect over rational-kernel topes = 3 h(A)-n,
SAT iff minimum defect = 0.
```

So halfspace depth above `1/3` has an exact source meaning: it counts the
unavoidable two-positive source rows in the best rational-kernel chamber.

This may be a more useful potential than raw rational nullity because it is
directly semantic at its zero boundary.

## 7. Interaction with fractional-support closure

Let `R*` be the projective fractional-support exact closure from the parent
note. It contains every original source row and preserves exactly the Boolean
Exact-One witness set.

Put

```text
K*=ker_Q(R*).
```

Then `K* subseteq ker_Q(A)`. Every full-support vector in `K*` still obeys the
source sign-count bound, while every SAT witness `x` still supplies

```text
y=3x-1 in K*
```

because every active closure row contains exactly one selected coordinate.
Therefore the same boundary theorem holds after closure:

```text
R* full rank                     => UNSAT,
R* has a zero rational-kernel row => UNSAT,
otherwise SAT iff h(R*)=n/3.
```

Moreover, restricting a linear subspace can only delete realizable chambers,
so the minimum positive chamber count is monotone nondecreasing under any
additional homogeneous exact closure:

```text
K' subseteq K => h(K') >= h(K)
```

whenever the full-support chamber sets are nonempty.

For SAT instances an exact witness-preserving closure must keep the boundary
value `n/3`; on UNSAT instances it may raise the depth gap or destroy full
support entirely.

## 8. Frozen controls

### SAT control: PG15_SAT_R11

The frozen series-irreducible SAT control has

```text
n=15,
rank_Q(A)=11,
nullity_Q(A)=4.
```

Its exact Boolean witnesses give vectors `y=3x-1` with exactly five positive
coordinates. RKTD-1 supplies the universal lower bound `p>=5`, so its exact
kernel halfspace depth is

```text
h(A)=5=n/3.
```

This is the positive boundary control.

### UNSAT control: SINGULAR_UNSAT_RANK14

The frozen connected linear-cubic UNSAT control has one-dimensional rational
kernel generated by

```text
g=(1,4,1,1,-2,-2,1,-2,-2,-2,-2,1,1,1,1).
```

It has nine positive and six negative coordinates. Every nonzero kernel vector
is a scalar multiple of `g`, so the two chambers have positive counts `9` and
`6`. Hence

```text
h(A)=6>5=n/3.
```

The new quotient therefore separates the old singular countercontrol for the
right reason: singularity supplies a rational kernel, but every kernel chamber
stays strictly above the Exact-One depth boundary.

The depth gap is

```text
3h-n = 18-15 = 3,
```

which equals the minimum number of unavoidable `++-` source rows.

## 9. Prior-art / anti-loop audit

Classical halfspace depth is the minimum number of data points in a closed
halfspace through the query point. Exact computation in unbounded dimension is
closely tied to the densest-hemisphere and Maximum Feasible Subsystem problems.
The general problem is not a polynomial donor:

- D. S. Johnson and F. P. Preparata, *The Densest Hemisphere Problem*,
  Theoretical Computer Science 6 (1978), 93–107,
  DOI `10.1016/0304-3975(78)90006-3`, gives NP-completeness for the
  discretized problem when both the number of points and dimension vary.
- R. Dyckerhoff and P. Mozharovskyi, *Exact computation of the halfspace
  depth*, Computational Statistics & Data Analysis 98 (2016), 19–30,
  DOI `10.1016/j.csda.2015.12.011`, develops exact algorithms and explicitly
  connects the task to densest hemisphere.
- E. Amaldi and V. Kann, *The complexity and approximability of finding
  maximum feasible subsystems of linear relations*, Theoretical Computer
  Science 147 (1995), 181–210,
  DOI `10.1016/0304-3975(94)00254-G`, proves NP-hardness for several Max-FS
  variants including homogeneous linear inequalities.

Therefore the following inference is forbidden:

```text
EXACT TUKEY-DEPTH QUOTIENT
=> POLYNOMIAL SAT ALGORITHM.
```

The admissible opportunity is narrower and source-specific: the Gale/kernel
configuration is not arbitrary. Its rows come from a cubic incidence kernel,
every source triple sums to zero as vectors, and this forces the dimension-free
`1/3` depth floor. A future PASS must exploit those extra identities rather
than importing a generic halfspace-depth solver.

No claim of literature novelty is made by this note; the theorem is a JANUS
derivation and the cited audit only establishes that the generic computational
problem is not a free tractability result.

## 10. Sharpened live gate

Freeze

```text
R5_E9_SOURCE_KERNEL_ONE_THIRD_DEPTH_BOUNDARY_GATE_V1
```

Input after all currently admitted exact preprocessing, including projective
fractional-support closure when applicable:

```text
exact-equivalent cubic source,
rational kernel dimension superlogarithmic,
full-rank and zero-kernel-row terminals failed,
source-induced kernel row configuration B,
h(B) known structurally to satisfy h(B)>=n/3,
SAT iff h(B)=n/3.
```

A PASS must provide at least one of:

1. a deterministic polynomial algorithm deciding whether the source-induced
   origin depth attains `n/3`, with a boundary chamber reconstructed on YES;
2. an exact polynomial contraction of the kernel row configuration that
   preserves boundary attainment and strictly lowers a polynomially bounded
   potential;
3. a source-specific theorem forcing a polynomially findable boundary chamber
   or a polynomial UNSAT depth-gap certificate;
4. the complete universal SAT algorithm contract.

Mandatory hostile controls:
- `PG15_SAT_R11`: boundary depth `5/15`;
- `SINGULAR_UNSAT_RANK14`: depth `6/15`;
- projective-fractional full-rank UNSAT control;
- high-nullity exact source families already frozen in the E9 ledger.

Forbidden pseudo-progress:
- enumerating all arrangement chambers;
- generic densest-hemisphere / Max-FS branch-and-bound called polynomial;
- using the `1/3` lower bound alone as a decision rule;
- assuming rational singularity implies boundary attainment;
- treating a numerical depth approximation as an exact `n/3` certificate.

## 11. Ceiling

```text
FULL-SUPPORT y in ker_Q(A)
=> n/3 <= #positive(y) <= 2n/3

#(++- source rows)
= 3 #positive(y) - n

EXACT-ONE SAT
<=> EXISTS FULL-SUPPORT KERNEL TOPE WITH #positive=n/3
<=> SOURCE KERNEL ORIGIN HALFSPACE DEPTH = n/3

NORMALIZED SOURCE DEPTH FLOOR
= 1/3

PG15_SAT_R11
= BOUNDARY DEPTH 5/15

SINGULAR_UNSAT_RANK14
= STRICT DEPTH 6/15

GENERIC EXACT HALFSPACE DEPTH
= NOT A POLYNOMIAL DONOR IN UNBOUNDED DIMENSION

UNIVERSAL SOURCE-SPECIFIC DEPTH-BOUNDARY ALGORITHM
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```