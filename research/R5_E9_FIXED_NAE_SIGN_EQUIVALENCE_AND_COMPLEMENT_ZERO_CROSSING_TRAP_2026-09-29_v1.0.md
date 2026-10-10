# R5 E9 — Fixed-NAE signed equivalence and complement zero-crossing trap

Date: 2026-09-29

Status: `JANUS_DERIVED_EXACT_SIGN_EQUIVALENCE__ZERO_CROSSING_ONLY_UNIVERSAL_ROUTE_FALSIFIED__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_NAE_TRANSVERSAL_COPY_FLOW_NORMAL_FORM_2026-09-29_v1.0.md`
- `research/R5_E9_CONTINUOUS_L1_BARYCENTER_AND_CROSSING_PENALTY_BARRIER_2026-09-29_v1.0.md`

Scientific ceiling:

```text
THIS NOTE DOES NOT PROVIDE A UNIVERSAL POLYNOMIAL SAT DECIDER.
IT IDENTIFIES THE FIXED-NAE COPY MATRIX AS A ROW/COLUMN SIGNING OF THE
ORIGINAL INCIDENCE MATRIX AND PROVES THAT ZERO-CROSSING AUGMENTATION ALONE
CANNOT BE COMPLETE, EVEN ON SAT INSTANCES.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Fixed NAE threshold

Let `A` be a square row/column-weight-three incidence matrix and let

\[
z\in\mathbb Z^n,\qquad Az=\mathbf 1.
\]

Threshold

\[
b_i=\mathbf 1[z_i\ge 1].
\]

For a threshold arising from an integer feasible point, every row has Boolean
weight one or two. Put

\[
\tau_r=(Ab)_r-1\in\{0,1\}.
\]

Define the variable sign

\[
s_i=2b_i-1\in\{-1,+1\}
\]

and diagonal matrix

\[
S_b=\operatorname{diag}(s_i).
\]

For each row define

\[
\rho_r=1-2\tau_r\in\{-1,+1\},
\qquad
R_b=\operatorname{diag}(\rho_r).
\]

The copy-flow normal form uses one magnitude `r_i>=0` per source variable.  In
each source row, if `m` is the unique minority coordinate and `u,v` the two
majorities, its equation is

\[
r_m-r_u-r_v=\tau_r.
\]

Let `M_b` be the matrix having coefficient `+1` on the minority entry and `-1`
on the two majority entries of each row.

## 2. Exact signed-matrix identity

### Theorem SNE-1

\[
\boxed{M_b=R_b A S_b.}
\]

### Proof

If row `r` has Boolean weight one, then `tau_r=0`, `rho_r=+1`; the unique
minority is the unique coordinate with `b_i=1`, hence `s_i=+1` there and
`s_i=-1` on the two majorities. Thus row `r` of `R_bAS_b` is exactly
`(+1,-1,-1)` on its support.

If row `r` has Boolean weight two, then `tau_r=1`, `rho_r=-1`; the minority is
the unique coordinate with `b_i=0`, where `s_i=-1`, while both majorities have
`s_i=+1`. Multiplication by `rho_r=-1` again produces `(+1,-1,-1)` ordered as
minority/majority/majority. QED.

Consequently `M_b` is not a new network matrix. It is obtained from `A` only by
row and column sign changes. In particular:

- every square minor changes only by a sign;
- `rank(M_b)=rank(A)` over every field of characteristic not two, and the same
  rank equality holds over `F2` because signs disappear;
- `ker_Z(M_b)=S_b ker_Z(A)`;
- total-unimodularity, determinant growth, and primitive-kernel coefficient
  obstructions are inherited exactly.

Thus the copy-flow representation exposes the surviving fanout coupling but does
not erase the source integer geometry.

## 3. Zero-crossing augmentation is exactly fixed-threshold augmentation

Write the odd-coset point as

\[
y_i=s_i(2r_i+1),\qquad r_i\in\mathbb Z_{\ge0}.
\]

A source trade is an integer vector

\[
g\in\ker_{\mathbb Z}(A),
\qquad y' = y+2g.
\]

The signs do not change iff

\[
\boxed{s_i g_i\ge-r_i\quad\forall i.}
\]

Put

\[
h=S_b g.
\]

Then exactly

\[
r'=r+h\ge0,
\qquad
M_bh=R_bAS_bg=0.
\]

Conversely every integer `h in ker_Z(M_b)` with `r+h>=0` gives a unique
zero-crossing source trade `g=S_bh`.

Hence zero-crossing descent is not a relaxation: it is precisely integer
augmentation inside one fixed NAE orthant.

Using the proved copy-flow objective

\[
F=\frac n3+2|B|+4\sum_{i:b_i=1}r_i,
\]

its exact objective change within a fixed threshold is

\[
\boxed{F(r+h)-F(r)=4\sum_{i:b_i=1}h_i.}
\]

## 4. Universal complement-witness trap

Assume the source is SAT and let

\[
x\in\{0,1\}^n,
\qquad Ax=\mathbf1.
\]

Because every row has three ones,

\[
A\mathbf1=3\mathbf1.
\]

Define the integer feasible point

\[
\boxed{z^{c}=\mathbf1-2x.}
\]

Then

\[
Az^{c}=3\mathbf1-2\mathbf1=\mathbf1.
\]

Its threshold is the complement

\[
b^{c}=\mathbf1-x.
\]

Every source row contains exactly one selected coordinate of `x`, so every row
contains exactly two selected coordinates of `b^c`. Therefore

\[
T=E(H),
\qquad |B^c|=\frac{2n}{3}.
\]

For this point the positive overshoot layer is identically zero:

\[
p=0.
\]

The exact objective is therefore

\[
\boxed{F(z^c)=\frac n3+2\frac{2n}{3}=\frac{5n}{3}.}
\]

Inside the fixed threshold `b^c`, the objective has the form

\[
\frac{5n}{3}+4\|p\|_1,
\]

so `p=0` is already a global optimum of that entire zero-crossing fiber. Thus:

\[
\boxed{\text{there is no strict zero-crossing improving trade from }z^c.}
\]

Yet the Boolean witness `x` has objective

\[
F(x)=n<\frac{5n}{3}.
\]

The direct improving trade is

\[
\boxed{g=x-z^c=3x-\mathbf1\in\ker_{\mathbb Z}(A),}
\]

and it crosses the sign of every coordinate.

### Corollary SNE-2

Any purported universal algorithm of the form

```text
repeat:
  find a zero-crossing improving integer source trade;
  if none exists, certify global optimum;
```

is false even on satisfiable cubic Exact-One instances.

This is an arbitrary-instance theorem conditional only on the existence of an
Exact-One witness; it is not a finite counterexample.

## 5. Algorithmic meaning

The first subgate in the previous checkpoint can therefore be used only as a
**local terminal test inside one orthant**. Failure of zero-crossing descent
cannot certify global odd-coset optimality.

A universal source-trade algorithm must support a threshold-changing move and
must price the exact crossing penalty. The live problem is therefore genuinely
cross-orthant:

```text
R5_E9_GLOBAL_SIGN_CROSSING_SOURCE_TRADE_GATE_V2
```

A PASS must, on every nonoptimal integer feasible point, either construct a
polynomially encoded sign-crossing improving move or prove by another exact
polynomial certificate that the point is globally optimal. It may not assume a
small crossing set, bounded primitive coefficients, low nullity, or small
separators.

## 6. Ceiling

```text
M_b = R_b A S_b
= PROVED

ZERO-CROSSING AUGMENTATION
= EXACTLY FIXED-NAE COPY-FLOW AUGMENTATION

COPY MATRIX NETWORK/TU SHORTCUT
= CLOSED IN GENERAL BY SIGN EQUIVALENCE

COMPLEMENT OF EVERY EXACT-ONE WITNESS
= INTEGER-FEASIBLE FIXED-ORTHANT LOCAL OPTIMUM AT 5n/3

ZERO-CROSSING-ONLY UNIVERSAL AUGMENTATION
= FALSIFIED

SIGN-CROSSING AUGMENTATION
= REQUIRED / OPEN

UNIVERSAL POLYNOMIAL DECIDER
= NOT PROVED

E8_D1
= EMPTY
P_VS_NP
= OPEN
```
