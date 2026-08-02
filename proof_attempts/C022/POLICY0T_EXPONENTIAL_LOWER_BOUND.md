# C022 theorem chain — exponential lower bound for the non-affine Policy-0T core

## Status

`COMPLETE CONDITIONAL CHAIN / DEPENDS ON C022 SIMULATION PROOF REVIEW`

## Goal

Prove an asymptotic lower bound for one exact SAT policy, not for all SAT
algorithms:

> On MAJ3-lifted odd-charge Tseitin formulas over a constant-degree expander
> family, the non-affine Policy-0T search core requires `2^{Omega(n)}` charged
> work.

Here `n` is the number of variables, equivalently vertices up to constant
factors, in the base bounded-degree Tseitin formula. The lifted formula has
`N=3n` gadget variables up to the same constant-factor convention.

## Ingredient 1 — base Resolution width

Classical Tseitin lower bounds on constant-degree expanders imply an infinite
family of unsatisfiable constant-width CNFs `phi_n` with `Theta(n)` variables and
clauses such that every ordinary Resolution refutation has width

```text
w_n >= c n
```

for an absolute constant `c>0` after choosing a fixed expander family.

Primary sources registered by C021 are:

- Urquhart, *Hard Examples for Resolution*;
- Ben-Sasson and Wigderson, *Short Proofs Are Narrow — Resolution Made Simple*.

## Ingredient 2 — MAJ3 lifting theorem

Itsykson, Podolskii and Shekhovtsov (ECCC TR26-018, 2026) prove that for every
unsatisfiable CNF requiring Resolution width at least `w`, and every constant
1-stifling gadget `g`, any `Res(⊕)` refutation of the lifted formula `phi o g`
with size `S` has depth

```text
D >= k w^2 / log S
```

for an absolute constant `k>0` hidden by the theorem's asymptotic notation.
MAJ3 is explicitly listed as a 1-stifling gadget.

## Ingredient 3 — exact encoding match

The registered generator replaces every base edge variable by one independent
MAJ3 block and encodes each substituted bounded-degree vertex relation by its
complete exact CNF truth table. This is a direct CNF encoding of

```text
phi_n o MAJ3.
```

Because base degree and gadget arity are constants, the lifted formula has
`Theta(n)` variables, clauses and encoding length.

## Ingredient 4 — affine dispatcher is disabled uniformly

The C022 MAJ3 non-affinity lemma proves that every local relation

```text
XOR_i MAJ3(block_i) = charge
```

is non-affine. Therefore the exact visible-affine detector covers none of the
complete local relation blocks and returns

```text
affine_answer = None
```

on the entire lifted family.

Thus Policy-0T enters precisely the non-affine search core governed by H132.

## Ingredient 5 — execution-to-proof simulation

The C022 simulation theorem transforms every terminating UNSAT core execution
with charged work `W` into an ordinary Resolution refutation satisfying

```text
S <= a W,
D <= 2N + 2 <= A n
```

for constants `a,A>0`. Ordinary Resolution is a restricted fragment of
`Res(⊕)`, so the same derivation is a valid `Res(⊕)` refutation with no larger
size or depth.

## Lower-bound derivation

Apply the lifting theorem to the translated proof:

```text
A n >= D >= k (c n)^2 / log S.
```

Rearranging gives

```text
log S >= (k c^2 / A) n.
```

Hence

```text
S >= 2^{Omega(n)}.
```

Since `S <= aW`,

```text
W >= S/a = 2^{Omega(n)}.
```

Because the lifted formula length `L` is `Theta(n)`, the same statement is

```text
W >= 2^{Omega(L)}.
```

## Consequence

No implementation of this exact non-affine Policy-0T core can have polynomial
worst-case work on all CNFs. The MAJ3-lifted expander-Tseitin family is an
explicit proof-complexity obstruction once one fixed expander family is chosen.

This upgrades the earlier finite quadratic-cap failure to an asymptotic
exponential lower bound **conditional only on independent acceptance of the
C022 trace-to-Resolution theorem and the exact encoding correspondence**.

## What this does not imply

The result does not prove `P != NP` because it excludes only one concrete policy
class. It does not exclude:

- exact residual formula caching;
- stronger clause learning;
- a different semantic module detector;
- mixed proof systems beyond the Policy-0T core;
- arbitrary polynomial-time SAT algorithms.

It identifies what every successor must add: a proof-theoretic capability not
simulated by this no-cache DPLL/Resolution core on the lifted family.

## Next falsification gates

1. independently check the universal simulation induction and constants;
2. verify the exact lifted CNF is accepted by the theorem's encoding convention;
3. freeze one constant-degree expander family and its linear Resolution-width
   citation;
4. search for a Policy-0T transition not represented by the provenance model;
5. attempt to produce a shallow polynomial-size `Res(⊕)` proof contradicting
   the claimed application.

## Claim boundary

Until those gates are independently checked, this remains a theorem chain under
formalization rather than a canonical proved result. Even after acceptance it is
an exponential lower bound for Policy-0T, not a resolution of `P` versus `NP`.
