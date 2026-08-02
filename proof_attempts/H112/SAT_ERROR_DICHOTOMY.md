# H112/H113 — one-sided SAT error funnel

## Status

`OPEN`, reproducibility `R2` for the certificate audit and `R1` for the missing
constructor.

## The asymmetry

For a candidate SAT circuit `C` and formula `F`, there are two error types.

### False negative

```text
F is satisfiable
C(F) = 0
```

A satisfying assignment is a polynomial-time checkable certificate of the
error.

### False positive

```text
F is unsatisfiable
C(F) = 1
```

An assignment cannot certify unsatisfiability. A polynomially checkable
certificate requires a separately fixed refutation system, and polynomial
certificates for every required negative instance can reintroduce the
`NP` versus `coNP` problem.

H031 and H056 mixed these two polarities. H112 removes the second one.

## Sufficient anti-checker theorem

For every constant `k`, suppose a polynomial-time constructor outputs a list

```text
(F_1,a_1),...,(F_m,a_m)
```

of polynomial total length such that every `a_i` satisfies `F_i`, and every
size-`n^k` candidate SAT circuit outputs zero on at least one listed formula.

Then no size-`n^k` circuit decides SAT at that length. Applying the construction
for every constant `k` gives

```text
SAT not in P/poly.
```

Since every language in `P` has polynomial-size circuits, this implies
`SAT not in P` and therefore `P != NP`.

## Remaining circularity wall

The constructor may not enumerate candidate circuits and call SAT or circuit
equivalence to locate errors. It must generate the universal false-negative
list from `1^n` in deterministic polynomial time.

Thus H112 removes certificate asymmetry but does not remove the central
uniform diagonalization problem.

## H113 range-avoidance bridge

H113 asks for more than generic missing-string output. Its decoder must
preserve all of the following:

1. the missing string identifies a candidate SAT-circuit error;
2. the error polarity is always false negative;
3. a satisfying assignment is decoded directly;
4. formula length and witness length stay polynomial;
5. no SAT oracle is used by the decoder.

Existing range-avoidance frameworks connect avoidance algorithms to strong
circuit lower bounds, but that does not automatically provide this SAT-specific
one-sided decoder.

## Executable audit

```bash
python experiments/direct/sat_error_audit.py --self-test
```

The self-test verifies satisfying assignments for false negatives and confirms
that the same NP-witness interface supplies nothing for a false positive. Its
brute-force solver is test-only.

## Claim boundary

No anti-checker list or decoder has been constructed. The progress is the
removal of an unnecessary coNP obligation and a precise statement of the
remaining one-sided diagonalization theorem.
