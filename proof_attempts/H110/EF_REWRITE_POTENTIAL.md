# H110/H111 — rewrite potential funnel to Extended Frege lower bounds

## Status

`OPEN`, reproducibility `R1`.

No endpoint family or universal potential has been proved. This file fixes the
exact shape of a sufficient argument and prevents finite chain experiments from
being confused with an asymptotic lower bound.

## External bridge already available

For the polynomial-time circuit relation used by H035, a size-`s` Extended
Frege or Circuit Frege proof of `C ≡ D` yields a rewrite chain

```text
C = E_0 approximately E_1 approximately ... approximately E_t = D
```

with `t <= s^O(1)`, and one relation step can be realized by deleting gates and
adding at most seven gates.

C015 treats this theorem as the registered bridge. It does not re-prove or
strengthen it.

## Sufficient invariant theorem

For explicit equivalent endpoints `(C_n,D_n)`, suppose there is an integer
potential `Phi_n` and polynomial `p` such that:

1. `Phi_n(E)` is computable in time polynomial in the encoding of `E` and `n`;
2. every exact legal rewrite step `E approximately E'` satisfies

   ```text
   |Phi_n(E') - Phi_n(E)| <= p(n);
   ```

3. the endpoint gap satisfies

   ```text
   |Phi_n(D_n) - Phi_n(C_n)| = n^omega(1) p(n).
   ```

For any chain of length `t`, the triangle inequality gives

```text
|Phi_n(D_n)-Phi_n(C_n)|
 <= sum_i |Phi_n(E_{i+1})-Phi_n(E_i)|
 <= t p(n).
```

Therefore `t = n^omega(1)`.

By the registered rewrite theorem, a polynomial-size Extended Frege proof would
produce a polynomial chain, contradiction. Thus the equivalence tautologies
require superpolynomial Extended Frege proofs.

A superpolynomial lower bound for Extended Frege rules out a polynomially
bounded propositional proof system of that strength and yields `NP != coNP`;
`P = NP` would imply `NP = coNP`, so the route ends in `P != NP`.

## H111 endpoint construction obligation

Arbitrary equivalent endpoints are unacceptable because their equivalence may
already hide the desired proof. H111 requires:

- a constant-size equivalent gadget pair `(A,B)`;
- an acyclic polynomial-size composition `Comp_n`;
- transparent equivalence of `Comp_n(A)` and `Comp_n(B)`;
- additive or otherwise controlled potential gap;
- a theorem that sharing and normalization cannot modify too many gadget
  contributions in one legal step.

The hardest attack is a global shortcut: one newly shared gate may affect many
syntactic copies. Any useful potential must be stable under the exact circuit
encoding and relation, not merely under tree-like replacement.

## Executable finite audit

```bash
python experiments/direct/rewrite_chain_audit.py --self-test
```

The auditor checks tiny circuits by exact truth tables, an added-gate budget of
seven, and a supplied finite potential bound. It is an artifact-format test,
not evidence for H110 or H111.

## Claim boundary

C015 has reduced the EF branch to a concrete invariant theorem, but has not
found the invariant. No Extended Frege lower bound or class separation is
claimed.
