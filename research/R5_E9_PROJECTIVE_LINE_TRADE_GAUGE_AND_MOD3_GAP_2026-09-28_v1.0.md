# R5 E9 — Projective Line-Trade Gauge and Mod-3 Walsh Gap

Date: 2026-09-28

Status: `JANUS_DERIVED_EXACT_REPRESENTATION_GAUGE__TERMINAL_EXPOSING_CONTROL__OBJECTIVE_GAP__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_BINARY_KERNEL_SIGNATURE_SERIES_PROJECTIVE_AVOIDANCE_2026-09-28_v1.0.md`
- `research/R5_E9_PROJECTIVE_SIGNATURE_WALSH_ARRANGEMENT_QUOTIENT_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_projective_line_trade_gauge_mod3_gap.py`

Scientific ceiling:

```text
THIS NOTE PROVES AN EXACT SEMANTIC GAUGE, A TERMINAL-EXPOSING FINITE CONTROL,
AND A SOURCE-SPECIFIC OBJECTIVE GAP.
IT DOES NOT PROVE THAT EVERY RESIDUAL HAS A POLYNOMIALLY DISCOVERABLE TRADE
SEQUENCE TO A KNOWN TERMINAL.

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

Take a row `{a,b,c}` of `A'`. For every `z in K`,

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

So a degree-preserving projective-line trade that passes one polynomial `F2` rank
test is an **exact semantic representation change**: SAT/UNSAT and every Boolean
witness are preserved. Witness lifting is the identity map.

## 3. Local trade certificate

A convenient local form replaces a set `R` of source lines by a disjoint set `R'`
of projective lines such that every point has the same incidence multiplicity in
`R` and `R'`. This preserves all column degrees. If the resulting square matrix
passes

```text
rank_F2(A') = rank_F2(A),
```

PLTG-1 applies immediately.

The rank test is ordinary Gaussian elimination and is polynomial. The theorem does
**not** claim that a useful trade always exists or that a polynomial sequence to a
known terminal always exists.

## 4. Terminal-exposing `PG(3,2)` hostile control

On frozen `PG15_UNSAT_R13`, the actual signature set is all fifteen nonzero vectors
of `F2^4`; hence it contains all 35 projective lines. The original 15 source lines
have

```text
rank_F2(A)=11,
rank_Q(A)=13,
Exact-One = UNSAT.
```

Exhaustively census all degree-preserving 3-for-3 exchanges using projective lines
outside the source arrangement and retain only those preserving `rank_F2=11`.
The checker finds exactly

```text
31 rank-safe 3<->3 trades,
6 of them expose rank_Q(A')=15.
```

One explicit terminal-exposing trade is

```text
remove:
  (1,12,13)
  (3,8,11)
  (6,9,15)

add:
  (1,8,9)
  (3,12,15)
  (6,11,13)
```

It satisfies

```text
old rank_F2 = 11,
new rank_F2 = 11,
old rank_Q  = 13,
new rank_Q  = 15,
old kernel  = new kernel,
old Exact-One witness set = new witness set = empty.
```

Therefore one exact local gauge move turns this hostile-looking representation into
the already admitted full-rational-rank polynomial UNSAT terminal while preserving
all Boolean semantics.  This is a finite positive control for **useful** line-trade
rewriting, not an asymptotic convergence theorem.

## 5. Mod-3 bad-line gap

For a coefficient vector `t`, let

```text
w(t) = number of signatures sigma with sigma dot t = 1,
q(t) = number of source rows fully contained in H_t.
```

The proved Walsh identity is

\[
q(t)=n-\frac32 w(t),
\]

so

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
SAT \Longrightarrow w_{max}=2n/3,
\qquad
UNSAT \Longrightarrow w_{max}\le2n/3-2.
}
\]

This gap is source-specific but is not by itself a polynomial approximation
algorithm. Generic nearest-codeword hardness is only a boundary control; it is not
a lower bound theorem for the stricter JANUS image.

## 6. New global gate

The point-set quotient now admits an exact rewrite system:

```text
same actual signature point set S
+ degree-preserving projective-line re-decomposition
+ full F2-rank preserved
=> exact same Boolean Exact-One witness set.
```

Freeze the candidate mechanism gate

```text
R5_E9_PROJECTIVE_LINE_TRADE_TERMINALIZATION_GATE_V1
```

A universal PASS must prove that every unresolved source either is already in an
admitted polynomial terminal or admits a polynomially discoverable rank-safe trade
(or polynomial-size batch of trades) such that a polynomially bounded potential
strictly improves, eventually reaching a terminal or constructive witness form.

Required:
1. trade discovery in polynomial time;
2. exact `F2` rank preservation at every semantic rewrite;
3. polynomial total number and size of rewrites;
4. strict global potential, not a local heuristic;
5. identity or explicit polynomial witness lifting.

Forbidden:
- assuming that every extra projective triangle participates in a useful trade;
- exponential search through all 3-regular line decompositions;
- finite PG(3,2) connectivity promoted to an asymptotic theorem;
- a trade sequence whose destination terminal is known only after solving SAT.

## 7. Ceiling

```text
RANK-PRESERVING PROJECTIVE LINE TRADE
=> EXACT KERNEL PRESERVATION
= PROVED

PARITY-SOLUTION / EXACT-ONE WITNESS SET
= IDENTICAL BEFORE/AFTER TRADE

PG15_UNSAT RANK-SAFE 3<->3 TRADES
= 31 EXACTLY (FINITE CONTROL)

PG15_UNSAT FULL-Q-RANK-EXPOSING TRADES
= 6 EXACTLY (FINITE CONTROL)

ONE LOCAL TRADE TO KNOWN POLY TERMINAL
= EXPLICIT

BAD-LINE CONGRUENCE
q(t) = n (mod 3)
= PROVED

3|n UNSAT GAP
q_min >= 3
w_max <= 2n/3-2
= PROVED

POLYNOMIAL TRADE-TERMINALIZATION THEOREM
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1 = EMPTY
P_VS_NP = OPEN
```
