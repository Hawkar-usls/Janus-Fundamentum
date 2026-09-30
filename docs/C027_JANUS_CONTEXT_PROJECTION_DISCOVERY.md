# C027 — JANUS Context Projection Discovery

**Status:** exploratory / software-only / not canonical.

Base: `f0ffb9b7afdd1797c4c6648b32f5ee5c5a80a9f0`.

The base already contains canonical C023 `JANUS-FC_local`. Its exact cache stores a completed residual Boolean judgement, but it does not automatically return one context-independent reusable reason.

C027 studies the missing operation:

```text
root formula
+ completed cached residual
+ reaching context
-> exact reusable context projection
```

No swarm node, ESP32 device, radio channel, miner, NAS runtime, Telegram backend, external LLM, BCI, biological sample, physical P–N junction, or quantum device was touched.

## Four charged costs

A reusable reason finder must pay for:

1. representation-language selection;
2. exact projection construction;
3. certificate replay;
4. decision and witness recovery in the selected language.

A compact projection is not sufficient if deciding it remains general SAT.

## OR context projection

A pure OR cone with output fixed true projects to one clause:

```text
x1 OR x2 OR ... OR xn
```

At `n=128`:

```text
gates                         127
summary clauses                 1
summary width                  128
cone replay records            127
Davis-Putnam resolution pairs  381
Davis-Putnam peak clauses      382
```

The reason is independently RUP-verified. There is no implied boundary clause of width below `n`; the full positive clause is the unique prime boundary implicate.

Thus unbounded clause width is not by itself a discovery barrier: the correct width-128 reason is found in linear cone work instead of searching through all `3^128-1` non-tautological clauses.

## XOR context projection

A pure XOR cone with output fixed to one projects to:

```text
x1 XOR x2 XOR ... XOR xn = 1
```

At `n=12`:

```text
GF(2) equations                 1
exact clause projection      2048 clauses
Davis-Putnam pairs         353663
```

At `n=16`:

```text
GF(2) equations                 1
exact clause projection     32768 clauses
Davis-Putnam status          OPEN
resolution pairs charged  5608839
peak clauses                 8200
```

Every prime CNF implicate of fixed parity has width `n`, and the exact clause projection contains `2^(n-1)` clauses. One GF(2) row represents the same relation exactly.

Therefore exponential clause volume is not necessarily semantic hardness; it can be a wrong-language artifact.

## Mixed general cone

Every source 3-CNF is compiled into OR trees for its clauses followed by an AND tree whose output is fixed true.

The circuit is linear-size and its boundary relation is exactly the source formula.

Balanced audit:

```text
cases                         80
SAT                           40
UNSAT                         40
source/circuit mismatches      0
false tractable admissions     0
target                         OPEN_GENERAL_CNF
```

Recognizing a compact mixed circuit does not make its boundary relation tractable. The exact projection is the original nonlinear SAT problem.

## Located bottleneck

### TRACTABLE_PROJECTION_DISCOVERY

Discover, construct and certify an exact context projection in a representation that is simultaneously:

- polynomial-size;
- polynomially constructible;
- independently verifiable;
- closed under the needed conjunction and elimination operations;
- polynomial-time decidable with witness recovery.

C027 separates three facts:

```text
large clause width can still be easy          OR
exponential clause volume can still be easy   XOR / GF(2)
compact circuit representation can be hard    general mixed circuit
```

## Exact lemmas for the explicit encodings

### OR Context Reason Lemma

For a pure OR cone with `n` distinct boundary leaves and output fixed true, the unique prime boundary implicate is the width-`n` disjunction of all leaves. A cone replay discovers it in `O(n)`.

### Parity Clause Projection Lemma

For `n`-bit parity fixed to `b`, every proper partial boundary assignment extends to both parity values. Hence every prime CNF implicate has width `n`, the exact CNF projection contains `2^(n-1)` clauses, and one GF(2) equation suffices.

## Next target

### C028 — Mixed-Cone Tractability Invariants

Candidate invariants:

- bounded interaction rank between gate types;
- bounded number of nonlinear gates on each input-output path;
- decomposability or determinism;
- bounded communication-matrix rank across actual separators;
- proof-carrying knowledge-compilation targets.

Every candidate must be attacked by the explicit mixed 3-CNF circuit embedding.

## Claim boundary

C027 does not prove `P=NP`, `P!=NP`, or a lower bound against all algorithms. It proves exact projection facts for explicit OR and XOR encodings and isolates tractable projection discovery as the next bottleneck.

## Reproduction

```bash
python experiments/direct/janus_context_projection_discovery.py
```
