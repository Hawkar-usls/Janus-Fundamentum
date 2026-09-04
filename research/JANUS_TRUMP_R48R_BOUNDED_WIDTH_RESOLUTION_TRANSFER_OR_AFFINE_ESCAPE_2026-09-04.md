# JANUS TRUMP R48R — Bounded-Width Resolution Transfer or Affine/Transient-Width Escape

Date: 2026-09-04

Status: **CONDITIONAL LOWER-BOUND TRANSFER CHARTER; NO WIDTH-ROUTE REFUTATION YET**

## Motivation

R48N gives a sufficient polynomial-time route if every persisted normalized state can be kept under one root-independent constant clause width `W`.

A tempting attack is to combine this with classical Resolution width lower bounds: if a hard UNSAT family requires Resolution refutations of unbounded width, perhaps a constant-width TRUMP trajectory is impossible.

That implication is **not automatic**.

The reason is crucial:

\[
\boxed{\text{CONSTANT PERSISTED WIDTH} \neq \text{CONSTANT TRANSIENT PROOF WIDTH}.}
\]

R48N permits a projection/normalization probe to use wider temporary clauses, provided the selected **persisted normalized successor** returns to width at most `W` and the temporary representation remains polynomially bounded.

Therefore a Resolution-width lower bound can attack the R48N route only after a stronger local simulation theorem is proved.

## Definitions

Let a persisted TRUMP state `F` have maximum clause width at most `W`.

A selected transition consists schematically of

`F -> exact-DP(v) -> frozen normalization stack -> G`,

where `G` is terminal or a normalized persisted successor.

Define the **transition proof width** `TW(F,v)` as the smallest width bound under which the semantic implication/equisatisfiability certificates used by that selected transition can be simulated in ordinary Resolution, under the non-affine part of the frozen grammar.

This is not merely `max_width(F)` or `max_width(G)`.

It must account for every transient derived clause needed to justify:

- exact DP resolvents;
- R33 certified reductions;
- RUP strengthening/terminal certificates;
- SA-BVE eliminations and reconstruction obligations;
- Horn/2-SAT terminal proofs where used;
- any other non-affine proof authority admitted by the frozen grammar.

## Lemma 1 — one raw DP layer from persisted width W starts at width at most 2W-2

Every parent clause containing the pivot has at most `W` literals. Removing the pivot leaves at most `W-1` literals on each side.

Hence every direct DP resolvent has width at most

\[
\boxed{2W-2}.
\]

This is only the first transient layer.

It does **not** prove that the full normalization closure stays within `O(W)` width: later SA-BVE or other resolution-like transformations can combine temporary clauses again.

## Critical escape — transient width may grow while persisted width resets

A width-capped algorithm can in principle have the pattern

`persisted width W -> temporary width poly(N0) -> persisted width W`.

Such a trajectory can still be polynomial-time under R48N if the temporary representation is polynomially bounded.

But it would not yield a constant-width Resolution refutation.

Therefore

\[
\boxed{\text{PERSISTED }W=O(1)\not\Rightarrow\text{RESOLUTION WIDTH }O(1).}
\]

Any lower-bound transfer that skips this distinction is invalid.

## Conditional transfer theorem

Fix a constant `W` and an UNSAT 3-CNF family `{F_n}`.

Assume all of the following.

### A. Universal W-capped coverage on the family

The frozen first-certified width-`W` grammar reaches a verified UNSAT terminal from every `F_n`, while every persisted nonterminal state has width at most `W`.

### B. Affine-evasion / no non-Resolution proof escape

Along every selected trajectory relevant to the claim, the R34 affine authority never supplies a semantic terminal or another proof step outside the Resolution simulation class.

If another non-Resolution authority exists, it must either be simulated or explicitly excluded.

### C. Constant-width local simulation

There exists a function `g(W)` independent of `n` such that every selected non-affine transition admits a Resolution simulation whose every derived clause has width at most `g(W)`.

This obligation includes the **entire transient normalization closure**, not only persisted endpoints.

### D. Polynomial composition

The per-transition Resolution simulations compose into one Resolution refutation of `F_n` without increasing width beyond `g(W)` (or another root-independent constant function of `W`).

Then `{F_n}` has Resolution refutations of width at most `g(W)`.

Therefore, if an independently established Resolution lower bound says

\[
width_{Res}(F_n)\to\infty,
\]

at least one of A–D must fail.

In particular, universal constant-width TRUMP coverage would be refuted **only if** B–D are already sealed for that family/grammar.

## What a successful lower-bound attack would look like

A rigorous attack must provide:

1. an explicit polynomial-size exact-3CNF UNSAT family;
2. a proven Resolution width lower bound growing with input size;
3. proof that R34 affine recognition/solve does not escape on the relevant reachable states;
4. a local simulation theorem for exact DP + R33 + RUP + SA-BVE + terminal authorities with transition proof width bounded solely by persisted `W`;
5. composition of those local simulations.

Only then can a constant-width coverage claim be contradicted.

## Current candidate families

### Pigeonhole principle

R47AD/R47AE showed that the small PHP4 instance is non-affine at its residual root but becomes `RUP_UNSAT` after one certified projection with zero persisted slack.

Thus root non-affinity alone is insufficient. A PHP-based transfer would require an affine-evasion and trajectory theorem for the entire size family, not just the root.

### Parity/Tseitin-like contradictions

These have strong Resolution lower-bound structure but are dangerous candidates because the frozen affine recognizer may intentionally provide a polynomial semantic escape. They cannot be used without proving affine-evasion or explicitly accounting for that authority.

## Two legitimate outcomes of R48R

### Outcome 1 — lower-bound transfer closes

Prove B–D for a chosen affine-evasive hard family. Then a growing Resolution width lower bound can refute universal constant persisted width for that family.

### Outcome 2 — escape is essential

Find that transient width necessarily grows, or that R34/another semantic authority escapes the Resolution class. Then Resolution width lower bounds do not refute the R48N algorithmic route, and the escape mechanism itself becomes the next object to bound polynomially.

Both outcomes are scientifically useful.

## Canonical laws

\[
\boxed{PERSISTED\ WIDTH\ CAP \neq PROOF\ WIDTH\ CAP.}
\]

\[
\boxed{RESOLUTION\ WIDTH\ LOWER\ BOUND\ TRANSFERS\ ONLY\ AFTER\ TRANSIENT\ WIDTH\ +\ AFFINE\ ESCAPE\ ARE\ CLOSED.}
\]

## Firewalls

- `UNIVERSAL_WIDTH_4_COVERAGE = NOT_PROVED`.
- `UNIVERSAL_CONSTANT_WIDTH_COVERAGE = NOT_PROVED`.
- `BOUNDED_WIDTH_RESOLUTION_TRANSFER = NOT_PROVED`.
- `AFFINE_EVASION_FOR_HARD_FAMILY = NOT_PROVED`.
- `UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE = OPEN`.
- `O4_UNIVERSAL_COVERAGE = OPEN`.
- `SAT_IN_P = NOT_PROVED`.
- `P_EQ_NP = NOT_PROVED`.
- `P_NE_NP = NOT_PROVED`.
- `P_VS_NP = OPEN`.
- `TRUMP_finished = false`.
