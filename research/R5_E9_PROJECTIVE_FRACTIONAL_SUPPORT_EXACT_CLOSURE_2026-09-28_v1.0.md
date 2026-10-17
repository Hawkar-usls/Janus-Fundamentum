# R5 E9 — Projective Fractional-Support Exact Closure

Date: 2026-09-28

Status: `JANUS_DERIVED_EXACT_POLYNOMIAL_GLOBAL_CLOSURE__FULL_RANK_UNSAT_TERMINAL__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_BINARY_KERNEL_SIGNATURE_SERIES_PROJECTIVE_AVOIDANCE_2026-09-28_v1.0.md`
- `research/R5_E9_PROJECTIVE_SIGNATURE_WALSH_ARRANGEMENT_QUOTIENT_2026-09-28_v1.0.md`
- `research/R5_E9_PROJECTIVE_FIXED_R_TRADE_RANK_ASCENT_ROUTER_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_projective_fractional_support_exact_closure.py`

Scientific ceiling:

```text
THIS NOTE GIVES A DETERMINISTIC POLYNOMIAL, WITNESS-SET-PRESERVING GLOBAL
CLOSURE OF THE PROJECTIVE-LINE REPRESENTATION.
IT DOES NOT PROVE THAT THE REMAINING CLOSURE NULLITY IS O(log n), NOR THAT
RANK DEFICIENCY IMPLIES SAT.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Source-generated projective point set

Work after the exact series preprocessing. Let

```text
S={sigma_1,...,sigma_n} subset F2^k-{0}
```

be the distinct actual binary-kernel signatures. Let `L(S)` be the set of every
projective line on the existing coordinates:

```text
ell={a,b,c} in L(S) iff sigma_a+sigma_b+sigma_c=0.
```

There are at most `O(n^2)` such lines: every unordered pair determines at most
one third point.

Let `R` be the `|L(S)| x n` 0/1 point-line incidence matrix.
The original source rows form a subset `D subseteq L(S)` and are cubic:
every point is contained in exactly three source rows.

## 2. Fractional 3-factor polytope

Define

\[
\mathcal P(S)=\{\lambda\in\mathbb R_{\ge0}^{L(S)}:R^T\lambda=3\mathbf1\}.
\]

`P(S)` is nonempty: the indicator of the original source-row set `D` belongs to
it.

Call a projective line **fractionally active** if it has positive weight in at
least one member of `P(S)`. Write

```text
L*={ell in L(S): exists lambda in P(S), lambda_ell>0}
```

and let `R*` be the incidence matrix of `L*`.

### Polynomial construction

For each `ell in L(S)`, solve the rational LP

```text
maximize lambda_ell
subject to R^T lambda = 3 1,
           lambda >= 0.
```

The line is active iff the optimum is positive. There are `O(n^2)` LPs, each
having polynomial dimensions and 0/1 integer coefficients of polynomial bit
length. Standard rational linear programming therefore constructs `L*` in
deterministic polynomial time.

Equivalently, one may average one feasible maximizer for each active line to
obtain a single member of `P(S)` that is strictly positive on all of `L*`.

## 3. Exact witness-set preservation

### Theorem PFSC-1

For every Boolean Exact-One witness `x` of the original source and every
fractionally active line `ell`,

\[
\boxed{r_\ell x=1.}
\]

#### Proof

The projective-line identity implies that for every parity solution `x=1+z`
and every `ell in L(S)`, the number `r_ell x` is odd. Since a line has three
points,

```text
r_ell x in {1,3}.
```

Take any `lambda in P(S)`. Since an Exact-One source witness has `|x|=n/3`,

\[
\sum_\ell\lambda_\ell(r_\ell x)
=x^T R^T\lambda
=3|x|
=n.
\]

On the other hand, summing the equations `R^T lambda=3 1` over all point
coordinates and using that each line has size three gives

\[
\sum_\ell\lambda_\ell=n.
\]

Every term `r_ell x` is at least one and every `lambda_ell` is nonnegative.
Equality of the two displayed sums therefore forces

```text
lambda_ell>0 => r_ell x=1.
```

If `ell` is active, choose a feasible `lambda` with `lambda_ell>0`. QED.

### Corollary PFSC-2 — exact closure

The original source line indicator belongs to `P(S)`, so every original source
line is active. Therefore

\[
\boxed{
\{x\in\{0,1\}^n:A x=1\}
=
\{x\in\{0,1\}^n:R_*x=\mathbf1\}.
}
\]

The forward inclusion is PFSC-1. The reverse inclusion holds because the
original source rows are a subset of `L*`.

Thus fractional-support closure may add many global redundant Exact-One
equations, but it neither creates nor destroys a Boolean witness. Witness
lifting is the identity map.

## 4. Full-rational-rank polynomial UNSAT terminal

Every row of `R*` has weight three, hence

```text
R* (1/3 1)=1
```

over the rationals.

If

\[
\operatorname{rank}_{\mathbb Q}(R_*)=n,
\]

the rational solution of `R*x=1` is unique and equals `(1/3)1`, which is not
Boolean. PFSC-2 then gives

\[
\boxed{\operatorname{rank}_{\mathbb Q}(R_*)=n\Longrightarrow UNSAT.}
\]

This is a new polynomial terminal reached after a genuinely global closure, not
a claim that singularity of the original source decides SAT.

## 5. Exact rank-deficiency router

Put

\[
d_*=n-\operatorname{rank}_{\mathbb Q}(R_*).
\]

Choose `rank(R*)` pivot columns. Enumerate the Boolean values of the remaining
`d*` free coordinates. For each assignment, solve the pivot variables by exact
rational Gaussian elimination and accept iff every recovered coordinate is
Boolean and all equations hold.

Hence the closed system has the deterministic exact bound

\[
\boxed{T=2^{d_*}\operatorname{poly}(n,L).}
\]

In particular `d*=O(log n)` is a polynomial terminal. This statement is a
standard linear-system parameterization and does not assume a free SAT oracle.

## 6. Relation to fixed-r line trades

Every integral 3-regular projective line decomposition is an element of
`P(S)`. Therefore every line reachable by any sequence of degree-preserving
line trades is contained in `L*`.

The fractional closure simultaneously exposes the union of all lines that can
participate in *any* fractional 3-factor, without enumerating trade sequences or
choosing a trade radius `r`.

It does not follow that every active line belongs to an integral decomposition;
the theorem needs only fractional feasibility.

## 7. Frozen controls

### PG15_UNSAT_R13

The point set is all fifteen nonzero points of `F2^4`. It contains all 35
projective lines. Uniform weights

```text
lambda_ell=3/7
```

put every line in `L*`, because every point of `PG(3,2)` lies on seven lines.
The complete 35-line incidence matrix has rational rank 15. Therefore PFSC-2
reaches the full-rank UNSAT terminal.

### PG15_SAT_R11

The frozen SAT control has 19 projective lines and three Exact-One witnesses.
The original 15 source lines are active. For each of the four extra lines, at
least one exact witness selects all three of its points; PFSC-1 therefore proves
that such a line cannot be active. Thus `L*` is exactly the original 15-line
support, whose rational rank is 11. The closure correctly does not declare
UNSAT.

These are finite controls only. They do not prove a universal bound on `d*`.

## 8. Polyhedral interpretation and anti-overclaim

With the affine change

\[
\pi=3x-\mathbf1,
\]
SAT witnesses give nonzero vectors of total sum zero whose projective-line sums
are nonnegative. This suggests a stronger LP/integrality conjecture, but it is
**not** proved here. Coding-theoretic LP decoding warns that even all redundant
parity checks may leave pseudocodewords outside geometrically-perfect code
classes.

Therefore the following inference is forbidden without a separate theorem:

```text
rank_Q(R*) < n => SAT.
```

The admitted result is only the exact closure plus the full-rank/low-nullity
terminals above.

## 9. Sharpened gate

Freeze

```text
R5_E9_PROJECTIVE_FRACTIONAL_SUPPORT_RANK_DEFICIENT_GATE_V1
```

Input:

```text
series-irreducible source point set S,
all projective lines enumerated,
fractional support closure L* computed,
rank_Q(R*) < n,
d*=n-rank_Q(R*) superlogarithmic,
all earlier polynomial terminals failed.
```

A PASS must provide at least one of:

1. prove `d*=O(log n)` for every source-generated closure;
2. construct a deterministic polynomial exact contraction that strictly lowers
   `d*` or another polynomially bounded global potential;
3. prove and algorithmize a source-specific integrality theorem for the closed
   optimum face, with polynomial witness extraction;
4. supply the complete universal SAT algorithm contract.

Mandatory hostile controls include the frozen SAT/UNSAT PG15 pair, the
series-contracted high-nullity lineages, and any geometrically-imperfect code
minor that is realizable inside the exact source image.

## 10. Ceiling

```text
FRACTIONAL PROJECTIVE 3-FACTOR POLYTOPE
= POLYNOMIALLY CONSTRUCTIBLE

UNION OF FRACTIONALLY ACTIVE LINES L*
= POLYNOMIALLY CONSTRUCTIBLE

BOOLEAN EXACT-ONE WITNESS SET AFTER CLOSURE
= EXACTLY PRESERVED

WITNESS LIFT
= IDENTITY

rank_Q(R*)=n
=> POLYNOMIAL UNSAT TERMINAL

d*=n-rank_Q(R*)
=> 2^d* poly(n,L) EXACT ROUTER

UNIVERSAL d*=O(log n)
= OPEN

RANK-DEFICIENT CLOSURE => SAT
= NOT CLAIMED

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY
P_VS_NP
= OPEN
```
