# JANUS TRUMP R47N — Fixed-Depth Escalation Polynomiality Barrier

Date: 2026-09-03

Status: **SYMBOLIC RESOURCE META-THEOREM; NOT AN O4 COVERAGE THEOREM**

## Motivation

R47L shows that one reachable residual can require a two-layer exact-DP macro even though no single DP+normalization layer is accepted. This is genuine algorithmic progress, but it creates a dangerous temptation: keep increasing DP depth until descent appears.

That move is not automatically polynomial.

## Frozen coarse recurrence

Let a macro begin from a canonical formula with `C_0` clauses and `V_0` variables. For one exact Davis-Putnam elimination on a pivot with `p` positive and `q` negative parents, the number of raw non-tautological resolvents is at most

`p q <= C^2 / 4`.

After retaining unaffected clauses, a coarse safe bound is

`C' = O(C^2)`.

R47J normalization closure can only reduce from the forced-DP state; it does not increase beyond that forced state. Therefore a worst-case depth recurrence for consecutive certified DP layers is

`C_{i+1} <= K * C_i^2`

for an irrelevant constant/coarse lower-order factor `K` absorbed into polynomial notation.

Ignoring constants,

`C_k <= C_0^(2^k)`.

Literal mass is at most the current clause count times the current variable bound, so the same exponent escalation appears in a coarse representation-size envelope.

## Search-tree recurrence

A deterministic exhaustive ordered pivot-sequence scan of depth `k` has at most

`V_0^k`

candidate sequences before pruning.

Thus a coarse total fixed-depth discovery envelope contains both

`V_0^k`

and

`C_0^(2^k)`.

## The barrier

For every fixed constant `k`, both expressions are polynomial in the original input size. This is why R47L depth 2 is theorem-safe as a resource extension.

But if `k=k(n)` is allowed to grow without an independently proved constant bound, the polynomial exponent itself grows with the input.

Under the frozen coarse recurrence:

- `k = O(1)` is compatible with an `n^c` bound for a fixed constant `c`;
- an unbounded `k(n)` is **not** justified as `n^{O(1)}` by this recurrence;
- even very slowly growing depth can produce superpolynomial or quasipolynomial envelopes;
- therefore `KEEP_ADDING_DP_LAYERS_UNTIL_DESCENT` is forbidden as a universal-polynomial argument.

This does not prove that deeper macros are intrinsically superpolynomial. It proves only that the current resource proof cannot authorize unbounded depth.

## Three legitimate escape routes

A future universal proof may proceed only by establishing at least one stronger statement:

1. **Universal constant-depth theorem** — prove a fixed constant `K` such that every reachable residual has a certified terminal/descent macro of depth at most `K`.
2. **Depth-independent representation bound** — prove that normalization/compression keeps every intermediate representation inside `n^c` for one fixed `c`, regardless of the number of composed DP layers used by the certified macro.
3. **Different symbolic representation/composition law** — replace explicit repeated CNF DP growth by a proof-carrying representation whose construction, update, and verification remain polynomial with a fixed exponent.

Without one of these, escalating `R47L -> depth3 -> depth4 -> ...` is finite experimentation, not a polynomial algorithm theorem.

## Consequence for R47M and successors

R47M is authorized because it tests a **fixed depth-2** grammar.

If R47M finds a depth-2 counterexample, the next action must not automatically be an unbounded-depth controller. We may run a frozen depth-3 witness probe as counterexample forensics, but any algorithmic promotion requires a constant-depth theorem or a stronger representation bound.

If R47M covers the full frozen one-swap frontier, that remains finite evidence only and does not establish a universal constant depth 2.

## Epistemic firewall

- `FIXED_DEPTH_2_POLYNOMIAL = RESOURCE_SAFE_UNDER_FROZEN_ENVELOPE`.
- `UNBOUNDED_DEPTH_POLYNOMIAL = NOT_PROVED`.
- `UNBOUNDED_DEPTH_COVERAGE = NOT_PROVED`.
- `O4_UNIVERSAL_COVERAGE = OPEN`.
- `SAT_IN_P = NOT_PROVED`.
- `P_EQ_NP = NOT_PROVED`.
- `P_NE_NP = NOT_PROVED`.
- `P_VS_NP = OPEN`.
- `TRUMP_finished = false`.
