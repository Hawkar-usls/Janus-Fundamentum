# H116 — parameterization failure

## Terminal status

`REJECTED` by attack `A447`.

This rejection concerns the exact implication stated by H116. It does not show
that length-normalized SAT-sound anti-checkers are impossible.

## The mismatch

H116 uses an external generator parameter `n` and allows the produced formulas
to have a length

\[
L_k(n)=n^{d(k)}
\]

for some polynomial relation whose exponent may depend on the quantified
circuit exponent `k`. Candidate circuits are nevertheless bounded by `n^k`.

The consequence claimed that if SAT had polynomial-size circuits, one could
choose `k` above their exponent and obtain a contradiction.

That inference compares exponents expressed in different variables.

## Explicit counterexample to the implication

Assume only for the purpose of checking the logic that SAT has circuits of size

\[
L^3
\]

on `L`-bit encodings.

Let an H116 generator use the allowed length relation

\[
L_k(n)=n^{k^2}.
\]

The inherited SAT circuit on the generated formulas has size

\[
L_k(n)^3=n^{3k^2}.
\]

But H116 attacks only circuits of size at most

\[
n^k.
\]

For every positive `k`,

\[
3k^2>k.
\]

Thus the exact SAT circuit is never inside the class hit by H116. There is no
choice of `k` that closes the promised contradiction.

The executable audit checks this arithmetic directly:

```bash
python experiments/direct/length_parameter_audit.py --self-test
```

## Why this is terminal

The consequence `H116 -> SAT not in P/poly` is part of the hypothesis's stated
research role. Without a common actual input-length parameter, the implication
is not valid. Repairing it changes the quantifiers and therefore creates a new
hypothesis rather than a cosmetic edit.

## Repair in H124

H124 uses the actual canonical formula length `L` everywhere:

- input to the generator: `1^L`;
- every generated formula: exactly `L` encoded bits;
- candidate circuit budget: `L^k`.

If SAT has circuits of size `L^c`, choosing `k>c` now puts the exact SAT circuit
inside the attacked class on the same domain.

The construction problem remains completely open; only the formal implication
is repaired.

## Claim boundary

This argument does not prove a SAT circuit lower bound or `P != NP`. It removes
a circular exponent comparison from one attempted route.
