# R5 E9 — AF3 source-valid linear-dimension UNSAT cover family

Date: 2026-09-30

Status: `JANUS_EXACT_CROSS_ROUTE_BARRIER__SOURCE_TRIANGLE_RELATIONS_PLUS_HIGH_DIMENSION_DO_NOT_FORCE_SAT__NO_D1_PROMOTION`

Parents:
- `R5_E9_AFFINE_F3_NOWHERE_ZERO_EXACTONE_NORMAL_FORM_2026-09-30_v1.0`
- `R5_E9_DEFECT_FREE_TWO_EDGE_UNSAT_LINEAR_NULLITY_FAMILY_2026-09-28_v1.0`

## 1. AF3 source geometry

For a row-weight-three source matrix `A`, every consistent affine solution space of

\[
Ar=\mathbf1\quad(\mathbb F_3)
\]

can be written

\[
r=r^{(0)}+B\alpha,
\]

with `B` a basis of `ker_F3(A)`. The coordinate forms

\[
\ell_i(\alpha)=r_i^{(0)}+b_i\alpha
\]

obey, for every source row `{i,j,k}`,

\[
\boxed{\ell_i+\ell_j+\ell_k=1.}
\]

Exact-One SAT is equivalent to an `alpha` with all `ell_i(alpha)` nonzero. Thus an UNSAT source gives a cover of the entire affine parameter space by the coordinate-zero hyperplanes `ell_i=0`.

## 2. Use the frozen defect-free UNSAT lift family

The parent theorem constructs an infinite family `A_t` of connected square linear-cubic sources with

```text
Exact-One(A_t) = UNSAT,
nu_Q(A_t) >= 2 + n_t/60.
```

The seed `A_0` is affine-consistent over `F3`: exact elimination gives

```text
rank_F3(A_0)=14,
dim ker_F3(A_0)=1,
A_0 r_0 = 1
```

for example

```text
r_0=(0,2,0,0,1,1,0,1,1,1,1,0,0,0,0).
```

## 3. Affine consistency survives every 2-lift

A two-edge lift has block form

\[
\widehat A=\begin{pmatrix}P&E\\E&P\end{pmatrix},\qquad P+E=A.
\]

If `Ar=1` over `F3`, then the fiber-constant vector `(r,r)` satisfies

\[
\widehat A(r,r)^T=((P+E)r,(P+E)r)^T=(1,1)^T.
\]

Hence every member `A_t` of the recursive family has a nonempty affine solution space over `F3`.

## 4. Ternary affine dimension is linear

For every integer matrix,

\[
\operatorname{rank}_{\mathbb F_3}(A)\le \operatorname{rank}_{\mathbb Q}(A),
\]

because any nonzero minor modulo 3 is a nonzero integer minor over `Q`. Therefore

\[
\nu_{\mathbb F_3}(A)\ge\nu_{\mathbb Q}(A).
\]

Applying the frozen rational-nullity bound gives

\[
\boxed{
\dim\ker_{\mathbb F_3}(A_t)
\ge 2+n_t/60
=\Omega(n_t).
}
\]

Since `A_t r=1` is consistent, this is also the dimension of its AF3 affine parameter space.

## 5. Yet the coordinate hyperplanes cover everything

Every `A_t` is Exact-One UNSAT. By AF3-1, no affine solution of `A_t r=1` is nowhere-zero. Equivalently every parameter point lies on at least one coordinate-zero hyperplane.

Thus for arbitrarily large `n_t` there are source-generated affine hyperplane systems satisfying simultaneously:

```text
parameter dimension = Omega(n_t),
connected / square / linear / cubic source,
every source triple obeys ell_i+ell_j+ell_k=1,
no parameter point avoids all coordinate hyperplanes.
```

Therefore

\[
\boxed{
\text{SOURCE TRIANGLE RELATIONS + LARGE AF3 DIMENSION}\not\Rightarrow\text{SAT}.
}
\]

This is stronger than the generic four-hyperplane cover barrier because it lives inside the literal JANUS source carrier.

## 6. Consequence

The universal AF3 algorithm cannot be based only on:

```text
large affine dimension,
number of coordinate hyperplanes,
source-local relation ell_i+ell_j+ell_k=1,
connectedness / linearity / cubicity,
or rational/ternary nullity growth.
```

It must exploit a genuinely global distinction between SAT and UNSAT source-generated covers: e.g. a constructive global contraction, decomposition, signed trade, matching/general-factor certificate, or another invariant not shared by the frozen SAT and UNSAT towers.

## 7. Ceiling

```text
AF3 AFFINE CONSISTENCY OF SEED = PASS
FIBER-CONSTANT CONSISTENCY UNDER LIFT = PROVED
TERNARY NULLITY >= RATIONAL NULLITY = PROVED
INFINITE UNSAT AF3 COVER WITH DIMENSION Omega(n) = PROVED
HIGH-d SOURCE-TRIANGLE COVER SHORTCUT = CLOSED
UNIVERSAL POLYNOMIAL FULL-SUPPORT CONSTRUCTOR = OPEN
E8_D1 = EMPTY
P_VS_NP = OPEN
```
