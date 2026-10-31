# R5 E9 — Projective-Signature Walsh Arrangement Quotient

Date: 2026-09-28

Status: `JANUS_DERIVED_EXACT_WALSH_QUOTIENT__ROW_ARRANGEMENT_SEMANTICS_ELIMINATED__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_BINARY_KERNEL_SIGNATURE_SERIES_PROJECTIVE_AVOIDANCE_2026-09-28_v1.0.md`
- `research/R5_E9_ROOTED_SERIES_PAIR_SYNDROME_CONTRACTION_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_projective_signature_walsh_arrangement_quotient.py`

Scientific ceiling:

```text
THIS NOTE PROVES AN EXACT GLOBAL QUOTIENT FOR SERIES-IRREDUCIBLE
LINEAR-CUBIC EXACT-ONE SOURCES.
IT REMOVES THE CHOICE OF 3-REGULAR PROJECTIVE-LINE DECOMPOSITION FROM THE
SEMANTIC DECISION OBJECT.
IT DOES NOT GIVE A POLYNOMIAL ALGORITHM FOR THE REMAINING MAXIMUM-WEIGHT
BINARY-KERNEL / WALSH OPTIMIZATION.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Setup

Let `A in {0,1}^{n x n}` be a connected linear cubic square Exact-One source and
assume the augmented binary matroid `M_F2([A|1])` is series-irreducible.

Let

```text
K = ker_F2(A),
k = dim_F2(K),
S = {sigma_1,...,sigma_n} subset F2^k
```

be the actual binary-kernel signatures from the parent theorem. Series
irreducibility implies the `sigma_j` are distinct and nonzero. Every source row
`R={a,b,c}` satisfies

```text
sigma_a + sigma_b + sigma_c = 0,
```

so the row is the projective line

```text
{u,v,u+v}.
```

For `t in F2^k`, put

```text
chi_s(t)=(-1)^(s dot t),
H_t={s:s dot t=0}.
```

Let `q(t)` be the number of source rows whose entire projective line lies in
`H_t`.

The parent theorem gives

```text
A is Exact-One SAT iff exists t with q(t)=0.
```

## 2. Local Walsh identity

Take one source row with signatures `{u,v,u+v}`. Because

```text
chi_(u+v)(t)=chi_u(t) chi_v(t),
```

its bad-line indicator is

\[
1_{\{u,v,u+v\}\subseteq H_t}
=\frac{(1+\chi_u(t))(1+\chi_v(t))}{4}
=\frac{1+\chi_u(t)+\chi_v(t)+\chi_{u+v}(t)}4.
\]

This identity is exact for every `t`.

## 3. Global cubic collapse

Sum the local identity over all `n` source rows. There are exactly `n` rows and,
because the source is cubic, every original column/signature occurs in exactly
three rows. Therefore every character `chi_sigma` is counted exactly three
times:

\[
\boxed{
q(t)=\frac n4+\frac34\sum_{\sigma\in S}(-1)^{\sigma\cdot t}.
}
\]

### Theorem WALSH-1 — arrangement-independence

For a series-irreducible linear-cubic source, the complete function `q(t)` is
determined solely by the actual kernel-signature point set `S`.

Consequently, if two valid 3-regular projective-line decompositions have the
same actual signature set `S`, they have identical Exact-One SAT status and the
same set of coefficient witnesses `t`.

Thus the source-row line arrangement can be discarded *after* `S` has been
computed and series irreducibility certified.

This is an exact representation-changing quotient, not a heuristic statistic.

## 4. Maximum-weight kernel form

Define

\[
w(t)=|\{\sigma\in S:\sigma\cdot t=1\}|.
\]

Then

\[
\sum_{\sigma\in S}(-1)^{\sigma\cdot t}=n-2w(t),
\]

so WALSH-1 becomes

\[
\boxed{q(t)=n-\frac32w(t).}
\]

Since `q(t)>=0`, every kernel evaluation word has

\[
w(t)\le \frac{2n}{3}.
\]

Moreover

\[
\boxed{
A\text{ Exact-One SAT}
\iff
\max_{t\in F_2^k} w(t)=\frac{2n}{3}.
}
\]

Equivalently, because `z_j=sigma_j dot t` parametrizes exactly `K`,

\[
\boxed{
A\text{ Exact-One SAT}
\iff
K\text{ contains a word of Hamming weight }2n/3.
}
\]

The corresponding Exact-One witness is `x=1+z` over `F2`; its support is the
zero-set of the kernel word and has size `n/3`. The already-proved parity+weight
normal form verifies it over the integers.

This does **not** make the remaining optimization polynomial. Generic maximum
weight / coset-leader / subspace-avoidance problems are hard. A PASS still has
to exploit additional source-generated structure or introduce a stronger global
contraction.

## 5. First two Walsh moments

Because `S` contains distinct nonzero vectors and `t` is uniform in `F2^k`,
character orthogonality gives

\[
\mathbb E_t\sum_{\sigma\in S}\chi_\sigma(t)=0
\]

and

\[
\mathbb E_t\left(\sum_{\sigma\in S}\chi_\sigma(t)\right)^2=n.
\]

Hence

\[
\boxed{\mathbb E q(t)=n/4,\qquad \operatorname{Var}(q(t))=9n/16.}
\]

These moments are exact diagnostics, not a decision algorithm.

## 6. Frozen controls

The companion checker reuses the exact series-irreducible controls from the
parent theorem.

For `PG15_UNSAT_R13`:

```text
rank_F2(A)=11,
k=4,
S=F2^4-{0},
max_t w(t)=8,
min_t q(t)=3,
Exact-One=UNSAT.
```

For `PG15_SAT_R11`:

```text
rank_F2(A)=10,
k=5,
|S|=15 distinct nonzero,
max_t w(t)=10=2n/3,
min_t q(t)=0,
Exact-One=SAT.
```

The checker verifies both the direct row count and the Walsh formula for every
`t` on both controls.

## 7. Sharpened live gate

Freeze

```text
R5_E9_PROJECTIVE_POINTSET_MAXWEIGHT_GLOBAL_CONTRACTION_GATE_V1
```

Input after exact series preprocessing:

```text
S subset F2^k-{0},
all points distinct,
S spans F2^k,
S comes from a linear cubic square source,
ker(S-matrix)=rowspan_F2(A),
source rows generate dependencies by projective triangles.
```

Decision obligation:

```text
is max_t |{sigma in S : sigma dot t = 1}| = 2|S|/3 ?
```

A PASS must give a deterministic polynomial algorithm or an exact
representation-changing contraction with polynomial witness reconstruction.

Forbidden pseudo-progress:
- enumerating all `2^k` characters when `k` is superlogarithmic;
- generic nearest-codeword / Max-Lin2 or union-of-subspaces as if polynomial;
- reintroducing the row arrangement after this quotient unless a new theorem
  proves the arrangement supplies additional algorithmic information;
- finite PG(3,2) census promoted as an asymptotic theorem.

## 8. Ceiling

```text
BAD-LINE WALSH IDENTITY
= PROVED

ROW-ARRANGEMENT DEPENDENCE AFTER SERIES IRREDUCIBILITY
= ELIMINATED EXACTLY

SAT
= MAXIMUM KERNEL EVALUATION WEIGHT 2n/3
= PROVED

FIRST TWO WALSH MOMENTS
= PROVED

POLYNOMIAL MAXWEIGHT SOLVER FOR SOURCE-GENERATED POINT SETS
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
