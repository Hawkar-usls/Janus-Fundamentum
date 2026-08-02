# H111 — refutation by compositional Circuit-Frege upper bound

## Terminal status

`DESTROYED` by attack `A419`.

The refutation concerns the exact H111 architecture: a fixed constant-size
equivalent gadget pair inserted into a polynomial-size acyclic circuit context.
It does not refute H110 for globally hard endpoint equivalences.

## H111 architecture

H111 assumes:

- a constant-size equivalent pair of Boolean circuits `A` and `B`;
- a uniform polynomial-size acyclic context `Comp_n`;
- endpoints `C_n = Comp_n(A)` and `D_n = Comp_n(B)`;
- a superpolynomial distance under Krajíček's exact rewrite relation.

The context may share subcircuits and may represent exponentially many
occurrences in its fully unwound formula. Circuit Frege operates on the DAG and
therefore does not pay once per unwound occurrence.

## Constant local proof

Because `A` and `B` have constant size and compute the same Boolean function,
`A ≡ B` has a constant-size Frege proof. Equivalently, it has a constant-size
Circuit-Frege proof.

For a finite library of constant gadget pairs, take the maximum of these
constant proof sizes.

## Bottom-up contextual proof

Traverse the DAG of `Comp_n` in topological order.

At every gadget port use the constant proof of `A ≡ B`. At every internal gate
use one of the fixed congruence tautologies:

```text
u ≡ v                         ->  ¬u ≡ ¬v
u ≡ v and u' ≡ v'             ->  (u ∧ u') ≡ (v ∧ v')
u ≡ v and u' ≡ v'             ->  (u ∨ u') ≡ (v ∨ v')
```

Each gate requires only a constant number of Circuit-Frege steps. A shared DAG
gate is proved once and reused; it is not reproved for every path in the
unwound formula.

Thus `C_n ≡ D_n` has a Circuit-Frege proof of size polynomial in
`|Comp_n|`, hence polynomial in `n`.

## Rewrite-chain upper bound

Krajíček's 2026 theorem states that an equivalence with a size-`s`
Extended-Frege or Circuit-Frege proof induces a chain under his polynomial-time
local circuit relation of length `s^{O(1)}`.

Applying that theorem to the compositional proof above gives a polynomial-length
rewrite chain from `C_n` to `D_n`.

This contradicts H111's required superpolynomial rewrite distance and therefore
terminates the exact hypothesis.

## Why exponential unfolding does not help

A polynomial DAG can encode exponentially many paths to one shared gadget.
H111 attempted to turn these paths into an additive superpolynomial potential
gap. Circuit Frege preserves the sharing: equivalence is propagated once per
DAG gate. The executable audit illustrates the accounting gap:

```bash
python experiments/direct/contextual_ef_upper_bound.py --self-test
```

A shared depth-24 context has more than sixteen million unfolded port
occurrences but only twenty-five DAG nodes and a linear compositional proof
bound.

## Surviving route

Any H110 endpoint family must avoid polynomial-size compositional equivalence
proofs. In particular, it cannot arise solely by inserting a fixed finite
library of EF-easy equivalent gadgets into a polynomial-size context.

The endpoint equivalence itself must carry the global proof complexity; this is
not obtainable by transparent local gadget amplification.

## Claim boundary

This refutation does not prove an Extended-Frege lower bound or `P != NP`. It
removes one proposed shortcut to such a lower bound.
