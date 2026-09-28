# R5 E9 — Projective Line-Trade Gauge and Mod-3 Walsh Gap

Date: 2026-09-28

Status: `JANUS_DERIVED_EXACT_REPRESENTATION_GAUGE_AND_OBJECTIVE_GAP__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_BINARY_KERNEL_SIGNATURE_SERIES_PROJECTIVE_AVOIDANCE_2026-09-28_v1.0.md`
- `research/R5_E9_PROJECTIVE_SIGNATURE_WALSH_ARRANGEMENT_QUOTIENT_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_projective_line_trade_gauge_mod3_gap.py`

Scientific ceiling:

```text
THIS NOTE PROVES A NEW EXACT SEMANTIC GAUGE AND A SOURCE-SPECIFIC OBJECTIVE GAP.
IT DOES NOT GIVE A POLYNOMIAL ALGORITHM FOR FINDING A USEFUL TRADE SEQUENCE OR
FOR SOLVING THE REMAINING PROJECTIVE POINT-SET MAXIMUM-WEIGHT PROBLEM.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Setup

Let `A in {0,1}^{n x n}` be a square cubic Exact-One incidence matrix and let

```text
K = ker_F2(A),
k = dim_F2(K).
```

Choose a basis of `K` and let `sigma_j in F2^k` be the kernel signature of column `j`.
For every `z in K`, writing `z_j=sigma_j dot t` is exact.

Assume `A'` is another `n x n` 0/1 matrix satisfying:

1. every row of `A'` has weight three;
2. every column of `A'` has weight three;
3. every row `{a,b,c}` of `A'` is a projective line for the original signatures,
   i.e. `sigma_a+sigma_b+sigma_c=0`;
4. `rank_F2(A') = rank_F2(A)`.

No assumption is made that the rows of `A'` are the original source rows.

## 2. Rank-preserving projective line-trade gauge

### Theorem PLTG-1

Under the four conditions above,

\[
\boxed{\ker_{F_2}(A')=\ker_{F_2}(A)=K.}
\]

### Proof

Take a row `{a,b,c}` of `A'`.  For every `z in K`,

```text
z_a+z_b+z_c
=(sigma_a+sigma_b+sigma_c) dot t
=0.
```

Hence every row of `A'` lies in `K^perp`. Therefore

```text
rowspan(A') subseteq K^perp = rowspan(A).
```

Both spaces have dimension `rank_F2(A)` by condition 4, so they are equal.
Taking orthogonal complements gives `ker(A')=K`. QED.

Because every row has odd weight three,

```text
A 1 = 1,
A' 1 = 1
```

over `F2`. Therefore the two parity-solution affine spaces are identical:

\[
\boxed{
\{x:A x=1\}=1+K=\{x:A'x=1\}.
}
\]

For any cubic square incidence matrix and any Boolean parity solution `x`, let `t_3`
be the number of rows containing three selected columns. Double counting selected
incidences gives

\[
3|x| = n+2t_3.
\]

Thus `|x|>=n/3`, with equality iff every row contains exactly one selected column.
Consequently

\[
\boxed{
\operatorname{ExactOne}(A)
=
\{x\in 1+K:|x|=n/3\}
=
\operatorname{ExactOne}(A').
}
\]

So a degree-preserving projective-line trade that passes the single polynomial
rank test is an **exact semantic representation change**: SAT/UNSAT and every
Boolean witness are preserved.

## 3. Local trade certificate

A convenient local form replaces a set `R` of source lines by a disjoint set `R'`
of projective lines such that every point has the same incidence multiplicity in
`R` and `R'`. This preserves all column degrees.  If the resulting square matrix
passes

```text
rank_F2(A') = rank_F2(A),
```

PLTG-1 applies immediately.

The rank test is ordinary Gaussian elimination and is polynomial.  The theorem
does **not** claim that a useful trade always exists or that a polynomial sequence
to a known terminal always exists.

## 4. Exact PG(3,2) hostile control

On frozen `PG15_UNSAT_R13`, the actual signature set is all fifteen nonzero vectors
of `F2^4`; hence it contains all 35 projective lines. The original 15 source lines
admit the following degree-preserving 3-for-3 exchange:

```text
remove:
  (1,12,13)
  (2,4,6)
  (3,8,11)

add:
  (1,2,3)
  (4,8,12)
  (6,11,13)
```

Every point has identical removed/added multiplicity.  The checker verifies

```text
old rank_F2 = 11,
new rank_F2 = 11,
old kernel  = new kernel,
old Exact-One witness set = new witness set = empty.
```

Thus the line-arrangement gauge is nontrivial on an actual series-irreducible
hostile residual.

## 5. Mod-3 bad-line gap

For a coefficient vector `t`, let

```text
w(t) = number of signatures sigma with sigma dot t = 1,
q(t) = number of source rows fully contained in H_t.
```

The proved Walsh identity is

\[
q(t)=n-\frac32 w(t).
\]

Equivalently,

\[
\boxed{3w(t)=2(n-q(t)).}
\]

Reducing modulo three gives

\[
\boxed{q(t)\equiv n\pmod 3.}
\]

In particular, on every potentially satisfiable cubic source `3|n`,

```text
q(t) in {0,3,6,...}.
```

Since SAT is exactly `min_t q(t)=0`, every UNSAT instance with `3|n` obeys

\[
\boxed{\min_t q(t)\ge3.}
\]

Using `w(t)=2(n-q(t))/3` gives the exact objective gap

\[
\boxed{
SAT \Longrightarrow w_max=2n/3,
\qquad
UNSAT \Longrightarrow w_max\le2n/3-2.
}
\]

This gap is source-specific but is not by itself a polynomial approximation
algorithm. Generic nearest-codeword / syndrome-decoding hardness may not be
imported as a solver or as a lower bound for the stricter JANUS source image.

## 6. New admissible attack

The projective quotient now has an additional exact freedom:

```text
same actual signature point set S
+ degree-preserving projective-line re-decomposition
+ full F2-rank preserved
=> exact same Boolean Exact-One witness set.
```

A genuine next PASS may therefore search for a polynomially discoverable sequence
of rank-preserving line trades leading to an already admitted terminal
(separator, balanced, commuting, matroid, or other), provided it proves:

1. a trade or terminal always exists on every unresolved source;
2. each trade is found in polynomial time;
3. a polynomially bounded potential strictly decreases;
4. witness lifting is explicit (here it is the identity on `x`);
5. the total representation size remains polynomial.

Absent those five items this is a representation gauge, not a universal solver.

## 7. Ceiling

```text
RANK-PRESERVING PROJECTIVE LINE TRADE
=> EXACT KERNEL PRESERVATION
= PROVED

PARITY-SOLUTION AFFINE SPACE
= IDENTICAL BEFORE/AFTER TRADE

EXACT-ONE WITNESS SET
= IDENTICAL BEFORE/AFTER TRADE

PG15_UNSAT NONTRIVIAL 3<->3 TRADE
= EXACT CONTROL

BAD-LINE CONGRUENCE
q(t) = n (mod 3)
= PROVED

3|n UNSAT GAP
q_min >= 3
w_max <= 2n/3-2
= PROVED

POLYNOMIAL USEFUL-TRADE CONVERGENCE THEOREM
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1 = EMPTY
P_VS_NP = OPEN
```
