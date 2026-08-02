# H108 — polynomial bit bound for rational LDL certificates

## Status

`FORMALIZING`, reproducibility `R2`.

The argument is a standard fraction-free elimination route written for the
JANUS certificate language. Independent review of the pivoted minor identities
is still required before promotion.

## Input model

Let `Q` be an `n × n` rational PSD matrix. Let `L` denote its total binary input
length, including every numerator and denominator.

Choose a positive common denominator

\[
D=\prod_{i,j}\operatorname{den}(Q_{ij}).
\]

Its bit length is at most the sum of the input denominator bit lengths and is
therefore at most `L`. The integer matrix

\[
A=DQ
\]

is PSD and every entry has bit length polynomial in `L`.

## Zero pivots

For a PSD matrix, every two-by-two principal minor is nonnegative:

\[
Q_{ii}Q_{jj}-Q_{ij}^2\ge0.
\]

If `Q_ii=0`, then `Q_ij=0` for every `j`. Thus a zero diagonal position has a
zero row and column in the current PSD Schur complement. It may be moved to the
end or emitted as a zero diagonal LDL entry without division by zero.

If a residual block is nonzero, at least one diagonal entry is positive and can
be selected by a symmetric permutation.

## Fraction-free elimination

Use symmetric Bareiss-style elimination on `A`, selecting a positive diagonal
pivot in every nonzero residual block. The exact pivots, Schur-complement
entries, and multipliers can be represented as ratios of minors of `A` (or of a
symmetrically permuted `A`).

The key point is not their magnitude but their binary length.

## Minor bound

Let `M` be the maximum absolute entry of `A`. For any `k × k` minor `B`,
Hadamard's inequality gives

\[
|\det B|
\le
\prod_{i=1}^{k}\|\text{row}_i(B)\|_2
\le
(\sqrt{k}M)^k.
\]

Therefore

\[
\log_2(1+|\det B|)
=O\bigl(k(\log k+\log(1+M))\bigr).
\]

Since `k <= n` and `log(1+M)` is polynomially bounded by the explicit input
length, every numerator and denominator occurring as a ratio of minors has
polynomial bit length in `n+L`.

There are only `O(n^2)` entries in the lower-triangular factor and `n` diagonal
entries. Hence the complete certificate has polynomial total bit length.

## Verification

The existing exact verifier checks

\[
PQP^T=LDL^T,
\]

unit lower-triangular form, a valid permutation, and nonnegative rational
entries of `D`. Its arithmetic cost is polynomial in the supplied certificate
size.

## Seeded stress suite

```bash
python experiments/theta/seeded_ldl_stress.py --self-test
```

Seed `9379992` generates fourteen explicit rational PSD matrices, including
singular cases. Construction and exact replay must succeed for every fixture.
The test is implementation evidence only and is not used in the universal
proof.

## Remaining review gate

A publication-quality version should state one precise fraction-free symmetric
elimination recurrence and prove by induction the exact minor formula under
pivoting and singular zero blocks. The determinant-size argument above then
supplies the bit bound immediately.

## Claim boundary

This lemma concerns explicit rational PSD matrices. It does not prove that an
SDP optimum is rational or that a short rational optimum can always be found.
