# R5 E9 — Rational-Tope Defect Syndrome Projective Filter

Date: 2026-09-28

Status: `JANUS_DERIVED_EXACT_CROSS_FIELD_PROJECTIVE_PARITY_FILTER__SMITH_2TORSION_IDENTITY__NO_NEW_LOW_NULLITY_COVERAGE__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_RATIONAL_KERNEL_TUKEY_DEPTH_BOUNDARY_QUOTIENT_2026-09-28_v1.0.md`
- `research/R5_E9_RATIONAL_KERNEL_PROJECTIVE_RATIO_PINNING_QUOTIENT_2026-09-28_v1.0.md`
- `research/R5_E9_RATIONAL_KERNEL_NULLITY_FPT_ROUTER_2026-09-27_v1.0.md`
- `research/R5_E9_SOURCE_KERNEL_POLYNOMIAL_NAVIGATION_SHELL_2026-09-28_v1.0.md`
- `research/R5_E9_SIGNED_TORSION_SIDE_CODE_QUOTIENT_2026-09-23_v1.0.md`

Checker:
- `experiments/r5_e9_rational_tope_defect_syndrome_projective_filter.py`

Scientific ceiling:

```text
FOR EVERY FULL-SUPPORT RATIONAL-KERNEL TOPE,

    d = 1 + A x (mod 2),   x_i=1[y_i>0],

IS EXACTLY THE INDICATOR OF ++- SOURCE ROWS, SO

    |d|=3p-n,
    BOUNDARY <=> d=0.

AFTER RATIONAL PROJECTIVE CLASS COLLAPSE,

    x(z)=x0+Rz,
    Gz=d0,  G=AR (mod 2)

IS AN EXACT AFFINE FILTER FOR ALL BOUNDARY TOPES.

AFTER THE RKPR PIN/EQUALITY PREPROCESSOR, EVERY SURVIVING PROJECTIVE CLASS
HAS EQUAL RATIONAL KERNEL ROWS.  WRITING B=RH THEN GIVES

    ker_Q(AR)=col(H),
    nullity_Q(AR)=d=nullity_Q(A).

IF tau_2 IS THE NUMBER OF EVEN NONZERO SMITH INVARIANT FACTORS OF AR, THEN

    kappa := nullity_F2(AR) = d + tau_2 >= d.

THEREFORE THE 2^kappa ENUMERATOR IS EXACT BUT DOES NOT CREATE A NEW
LOW-NULLITY POLYNOMIAL ISLAND BEYOND THE EXISTING 2^d RATIONAL-KERNEL
ROUTER.  ITS VALUE IS STRUCTURAL: IT IDENTIFIES THE EXTRA CROSS-FIELD
OBSTRUCTION PRECISELY AS 2-TORSION AND BINDS PARITY TO REAL TOPE DEFECTS.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Rational-kernel sign defect

Let `A in {0,1}^{n x n}` be a cubic square positive Exact-One source and let
`B in Q^{n x d}` have columns forming a basis of `ker_Q(A)`.  For a
full-support coefficient vector `alpha`, put

```text
y=B alpha,
x_i=1[y_i>0],
p=|x|.
```

Every source row contains three nonzero entries of `y` summing to zero.
Therefore its sign type is exactly one of

```text
+--
++-
```

up to permutation.

The Tukey-depth boundary theorem already gives

```text
#(++- rows)=3p-n.
```

## 2. Exact defect-syndrome theorem

Over `F2`, define

```text
d(x)=1+A x.
```

On a `+--` row, `Ax=1`, hence `d_r=0`.  On a `++-` row, `Ax=0`, hence
`d_r=1`.  Thus:

### Theorem RTDS-1

\[
\boxed{d(x)=\mathbf1+A x\pmod2}
\]

is exactly the indicator vector of the `++-` rows, and

\[
\boxed{|d(x)|=3p-n.}
\]

Consequently

\[
\boxed{p=n/3\iff d(x)=0\iff Ax=\mathbf1\pmod2.}
\]

For an arbitrary Boolean vector, odd row parity would not imply Exact-One.
For a rational-kernel tope it does, because the zero-sum/nonzero condition
already restricts every row to one or two positives.  Hence a realizable tope
with zero defect syndrome gives an integer Exact-One witness immediately.

## 3. Projective toggle coordinates

Partition the nonzero rows of `B` into rational projective classes
`C_1,...,C_q`.  Let `R in F2^{n x q}` be their incidence matrix:

\[
R_{ij}=1\iff i\in C_j.
\]

Choose one full-support base tope and let `x0` be its positive-coordinate bit
vector.  Every other chamber of the simplified projective arrangement differs
from the base on a unique projective toggle vector `z in F2^q`.

Flipping class `C_j` reverses every raw coordinate sign in that class, even when
some representatives are antiparallel. Therefore

\[
\boxed{x(z)=x_0+Rz\pmod2.}
\]

Put

```text
G  = A R       (mod 2),
d0 = 1 + A x0  (mod 2).
```

Then RTDS-1 yields

\[
\boxed{d(z)=d_0+Gz.}
\]

and hence:

### Theorem RTDS-2 — projective parity filter

A realizable projective sign pattern is a boundary tope iff

\[
\boxed{Gz=d_0.}
\]

Thus Exact-One is equivalent to asking whether the affine binary slice

```text
Z={z in F2^q : Gz=d0}
```

contains a sign vector realizable by the rational hyperplane arrangement.

## 4. Exact affine-slice enumerator

Let

```text
kappa=nullity_F2(G).
```

Gaussian elimination either proves `Gz=d0` inconsistent or returns one solution
plus a basis of `ker_F2(G)`.  In the consistent case there are exactly
`2^kappa` candidates.

For each candidate, rational tope realizability is the strict homogeneous system

\[
s_j h_j\alpha>0\qquad(j=1,...,q),
\]

where `h_j` is an oriented rational representative of projective class `C_j`.
By positive scaling this is equivalent to rational LP feasibility of

\[
s_j h_j\alpha\ge1\qquad(j=1,...,q).
\]

Therefore the slice can be searched exactly in

```text
2^kappa * poly(input bit length)
```

time, with direct witness reconstruction when a realizable member is found.

This statement is exact, but the next section shows why it is not a new
low-nullity coverage theorem.

## 5. Equality-quotient rational kernel

Apply the already frozen RKPR preprocessing first.  Illegal rational row ratios
reject, `-2/-1/2` classes pin and propagate, and every surviving unpinned
projective class consists of **equal**, not merely proportional, rational kernel
rows.

On that hard residual choose one row representative per class and place them in

```text
H in Q^{q x d}.
```

Because rows inside each class are equal,

\[
\boxed{B=RH.}
\]

Let

```text
M=AR
```

over the integers/rationals.

Since `AB=0`,

\[
MH=ARH=AB=0.
\]

So `col(H) subseteq ker_Q(M)`.

Conversely, if `Mc=0`, then

```text
A(Rc)=0,
```

so `Rc in ker_Q(A)=col(B)=col(RH)`.  Hence for some `alpha`,

```text
Rc=RH alpha.
```

The class-incidence matrix `R` has disjoint nonempty columns and therefore has
full column rank.  Cancelling `R` gives

```text
c=H alpha.
```

Thus:

### Theorem RTDS-3 — exact quotient-kernel identity

\[
\boxed{\ker_Q(AR)=\operatorname{col}(H)}
\]

and therefore

\[
\boxed{\nu_Q(AR)=d=\nu_Q(A).}
\]

This is basis-independent after the RKPR equality quotient.

## 6. Smith decomposition of kappa

Let the nonzero Smith invariant factors of the integer matrix `M=AR` be

```text
s_1 | s_2 | ... | s_r,
r=rank_Q(M)=q-d.
```

Reduction modulo two keeps one pivot for every odd `s_i` and loses one pivot for
every even `s_i`.  Let

```text
tau_2 = # {i : s_i is even}.
```

Then

```text
rank_F2(M)=r-tau_2.
```

Therefore:

### Theorem RTDS-4 — exact cross-field nullity law

\[
\boxed{
\kappa
=\nu_{F_2}(AR)
=q-(r-\tau_2)
=d+\tau_2.
}
\]

In particular

\[
\boxed{\kappa\ge d.}
\]

This corrects the tempting interpretation that projective parity filtering might
create a smaller exponential parameter than rational nullity on the RKPR hard
residual.  It cannot: any excess is precisely characteristic-two Smith torsion.

Consequences:

```text
kappa=O(log n) => d=O(log n),
```

so the old rational-kernel `2^d poly(n)` router already covers that island.
The parity filter remains useful as a structural coupling and as a possible
source of compact certificates, but not as a new asymptotic low-nullity router.

## 7. PG15 exact control

For `PG15_SAT_R11`, the eleven equality projective classes are

```text
{1,5}, {2,6}, {3}, {4}, {7}, {8,12},
{9}, {10}, {11,15}, {13}, {14}.
```

With

```text
alpha0=(-1,2,2,-2)
```

the base tope has

```text
p=6,
|d0|=3=3p-15.
```

The exact checker proves

```text
q=11,
rank_F2(AR)=7,
kappa=4,
# {z:Gz=d0}=16.
```

Here `d=4`, so the observed control has `tau_2=0` and `kappa=d`.

All sixteen parity candidates are certified exactly:

- four are realized by the four known integer `alpha` vectors for the four
  Exact-One boundary topes;
- each of the remaining twelve has a positive dependence certificate: three
  desired signed projective normals sum exactly to zero, so their three strict
  positive inequalities cannot hold simultaneously.

Hence the affine slice contains exactly the four known realizable boundary
topes on this control, with no floating-point argument.

## 8. Corrected strategic meaning

Freeze the following facts:

```text
DEFECT SYNDROME / REAL TOPE BRIDGE
= NEW EXACT STRUCTURAL IDENTITY

PROJECTIVE AFFINE GF(2) FILTER
= EXACT

LOW-kappa ENUMERATION
= EXACT BUT ASYMPTOTICALLY SUBSUMED BY LOW-d RATIONAL NULLITY

EXCESS kappa-d
= EXACTLY 2-TORSION COUNT tau_2 OF AR
```

Do not count the `2^kappa` enumerator as independent progress toward P=NP.

The useful new universal question is instead whether the high-rational-nullity
core admits a polynomial operation on the affine parity slice **without**
enumerating it, possibly exploiting its coupling to the realizable oriented
arrangement and/or its Smith structure.

## 9. Live gate

Freeze

```text
R5_E9_HIGH_NULLITY_PROJECTIVE_PARITY_SLICE_GLOBAL_CONTRACTION_GATE_V2
```

Input after admitted preprocessing:

```text
d=nu_Q(A)=omega(log n),
kappa=d+tau_2,
Z={z:Gz=d0},
exact rational projective arrangement.
```

A PASS requires one of:

1. a deterministic polynomial method deciding whether `Z` contains a realizable
   tope, without `2^kappa` enumeration;
2. a polynomial contraction of the affine slice / oriented arrangement with
   exact witness reconstruction;
3. a polynomially verifiable UNSAT certificate excluding the entire affine
   slice;
4. another complete universal polynomial solver satisfying the E8-DIRECT
   contract.

Forbidden pseudo-progress:
- claiming low `kappa` adds coverage beyond low rational nullity;
- enumerating `2^kappa` on the high-nullity core;
- treating parity compatibility as rational realizability;
- using floating-point sampling as proof;
- treating torsion magnitude alone as hardness or tractability;
- promoting D1 or claiming P=NP.

## 10. Ceiling

```text
RATIONAL-TOPE DEFECT SYNDROME
= EXACT ++- ROW INDICATOR

|d|
= 3p-n

BOUNDARY
<=> d=0

PROJECTIVE TOGGLE FORM
x(z)=x0+Rz

BOUNDARY AFFINE FILTER
AR z=d0 (mod 2)

AFTER RKPR EQUALITY QUOTIENT
ker_Q(AR)=col(H)
nu_Q(AR)=d

SMITH CROSS-FIELD LAW
kappa=d+tau_2 >= d

PG15
q=11, d=4, kappa=4, tau_2=0
16 parity candidates -> exactly 4 realizable boundary topes

NEW LOW-NULLITY COVERAGE
= NONE

HIGH-NULLITY GLOBAL PARITY-SLICE / TOPE INTERSECTION
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```