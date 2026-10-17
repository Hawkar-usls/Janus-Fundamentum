# R5 E9 — Fixed-r Projective Trade Rational-Rank Ascent Router

Date: 2026-09-28

Status: `JANUS_DERIVED_EXACT_DETERMINISTIC_POLYNOMIAL_PREPROCESSOR__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_PROJECTIVE_LINE_TRADE_GAUGE_AND_MOD3_GAP_2026-09-28_v1.0.md`
- `research/R5_E9_PROJECTIVE_SIGNATURE_WALSH_ARRANGEMENT_QUOTIENT_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_projective_fixed_r_trade_rank_ascent.py`

Scientific ceiling:

```text
FOR EACH FIXED CONSTANT r, THIS NOTE GIVES A DETERMINISTIC POLYNOMIAL
SEMANTICS-PRESERVING PREPROCESSOR WITH A STRICT RATIONAL-RANK POTENTIAL.
IT DOES NOT PROVE THAT A FIXED-r LOCAL MAXIMUM IS A POLYNOMIAL TERMINAL.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Input and exact trade oracle

Start from a cubic square source `A` with actual binary-kernel signature set `S`.
Enumerate all projective triples on existing coordinates:

```text
L(S) = {{a,b,c}: sigma_a + sigma_b + sigma_c = 0}.
```

There are at most `O(n^3)` such triples and they are constructible after one
Gaussian elimination over `F2`.

Fix a constant `r>=1`.  An admissible `r`-trade replaces `r` current rows by `r`
distinct triples from `L(S)` such that:

1. the removed and added sets have identical point-degree vectors;
2. the resulting matrix has the same `F2` rank as the current matrix.

By the parent line-trade gauge theorem, every admissible trade preserves the
entire `F2` kernel, the parity-solution affine space, and the complete Boolean
Exact-One witness set.

## 2. Rank-ascent rule

Among all admissible trades of size at most `r`, accept only those satisfying

\[
\operatorname{rank}_{\mathbb Q}(A')>
\operatorname{rank}_{\mathbb Q}(A).
\]

Choose one deterministically, e.g. lexicographically by `(removed,added)` after
maximizing the new rational rank.

### Theorem FRTA-1

For every fixed constant `r`, repeated rank-ascent trading is a deterministic
polynomial-time exact preprocessor.

### Proof

**Polynomial candidate generation.** `|L(S)|=O(n^3)`.  For each
`s<=r`, enumerate a current-row subset and an added-line subset of size `s`.
The number of pairs is at most `n^{O(r)}`.  Point-degree equality, `F2` rank, and
rational rank are all polynomial-time tests.

**Semantic exactness.** Every accepted move satisfies the hypotheses of the
parent theorem, so the Boolean witness set is unchanged. Since the kernel is
unchanged, the same signature set `S` is valid at the next iteration; no
semantic recomputation oracle is needed.

**Strict termination.** Every accepted move strictly raises the integer
potential

```text
rho(A)=rank_Q(A),
```

which is bounded by `n`. Hence at most `n-rank_Q(A_0)` moves occur.

**Total complexity.** A polynomial number of iterations times `n^{O(r)}`
polynomial rank tests is polynomial for every fixed `r`. QED.

## 3. Full-rank terminal

If the process reaches

```text
rank_Q(A)=n,
```

then, because the current representation remains cubic, `A 1 = 3 1` over the
integers.  The unique rational solution of `Ax=1` is therefore `x=(1/3)1`, which
is not Boolean. So the current representation is Exact-One UNSAT. Since every
trade preserved the complete witness set, the original source is UNSAT as well.

Thus fixed-r trading is not merely normalization: it can expose an already
proved polynomial UNSAT terminal.

If no improving trade exists before full rank, return the exact equivalent
certificate

```text
FIXED_r_PROJECTIVE_TRADE_RATIONAL_RANK_LOCAL_MAXIMUM.
```

This residual is not declared easy.

## 4. Exact finite controls

### PG15_UNSAT_R13

For the frozen series-irreducible UNSAT control:

```text
35 actual projective lines,
31 F2-rank-safe 3<->3 trades,
6 raise rank_Q from 13 to 15.
```

Hence the `r=3` router reaches the full-rank polynomial UNSAT terminal in one
accepted move.

### PG15_SAT_R11 rigidity control

For the frozen series-irreducible SAT control:

```text
15 source lines,
19 total actual projective lines,
4 extra projective lines.
```

The checker enumerates every 15-line subset of those 19 lines and finds exactly
one 3-regular line decomposition: the original one. Therefore this point set has
extra projective lines but no alternative cubic line decomposition at all.

This proves the important anti-loop statement

```text
EXTRA PROJECTIVE LINE => TRADE EXISTS
```

is false.

The SAT control is already covered by older polynomial routes; it is used here
only to stop an invalid universal trade-existence inference.

## 5. Relation to the global bottleneck

Unrestricted search for a new 3-regular line decomposition is not a free step.
Selecting candidate projective lines with degree `0/3` on line-vertices and
exact degree `3` on points is another General-Factor / 3-uniform selection
problem containing the same kind of `{0,3}` coupling previously isolated as
hard.  The router therefore permits only fixed-size explicitly enumerable
trades unless a new polynomial global selection theorem is proved.

The strengthened live residual after applying all admitted terminals and this
preprocessor is:

```text
source-generated projective point-set maxweight instance
+ all prior polynomial terminals failed
+ fixed-r projective trade rational-rank local maximum
+ max kernel weight still unknown.
```

A universal completion still requires a theorem acting on that residual, not an
exponential search through line decompositions.

## 6. Ceiling

```text
FIXED-r TRADE ENUMERATION
= n^{O(r)} / POLYNOMIAL FOR CONSTANT r

EVERY ACCEPTED TRADE
= EXACT WITNESS-SET PRESERVING

STRICT POTENTIAL
= rank_Q(A)

NUMBER OF ACCEPTED STEPS
<= n

FULL-Q-RANK REACHED
=> POLYNOMIAL UNSAT TERMINAL

PG15_UNSAT
r=3 => FULL-RANK IN ONE STEP
= EXACT FINITE CONTROL

PG15_SAT
EXTRA LINES BUT UNIQUE 3-REGULAR DECOMPOSITION
= EXACT FINITE COUNTERCONTROL

FIXED-r LOCAL MAXIMUM
= NOT YET A TERMINAL

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1 = EMPTY
P_VS_NP = OPEN
```
