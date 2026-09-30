# C028 — JANUS Model-Scope and Direct-Sum Audit

**Status:** `TWO PROOF TRANSITIONS REJECTED / ONE CURRENT CLAIM HELD OPEN / P_VS_NP=OPEN`

## A. Czerwinski 2022 — additive brute-force lower bound

The paper considers

```text
S = {(M,1^n,1^t): some n-bit y is accepted by M within t steps}
```

and claims an `Omega(2^n t/log t)` lower bound by adding the alleged cost of testing each word.

### Failure 1 — Rice's theorem is outside the bounded problem

For fixed unary `t`, acceptance within `t` steps is decidable by bounded simulation. Rice's theorem concerns nontrivial semantic properties of the unbounded language computed by a machine; it does not imply that a bounded-time algorithm must inspect all candidate words independently.

### Failure 2 — missing direct-sum theorem

Even if one predicate costs `t`, `m` predicates need not cost `m t`. They can share one computation. The machine-checked countermodel makes every predicate depend on the same `t`-step result:

```text
individual cost: t
m claimed independent costs: m t
actual shared cost: t
```

Lower bounds do not add without a proved direct-product/direct-sum theorem.

**Verdict:** `LEMMA 2 AND THE FINAL EXPONENTIAL LOWER BOUND ARE NOT ESTABLISHED`.

## B. Meek 2008 — representative search partitions

The proof argues from the exponential number of assignments to a claim that a deterministic computation can process at most one candidate input set per step, and therefore a polynomial solver must discover a polynomial representative partition.

This restricts the universe of algorithms to assignment-enumerating search.

The exact countermodel uses `n` independent GF(2) equations. There are `2^n` possible assignments, yet Gaussian elimination determines consistency and the unique witness in polynomial work without classifying assignments one by one.

```text
n=128
candidate assignments = 2^128
elimination upper bound = n^3
```

The same conceptual failure appears in 2-SAT, Horn-SAT, matching, flow, and other problems where one inference summarizes exponentially many candidates.

**Verdict:** `SEARCH-PARTITION NECESSITY REFUTED AS A GENERAL MACHINE CLAIM`.

This does not prove an NP-complete problem easy. It shows that the proposed argument cannot exclude such an algorithm merely by counting assignments.

## C. Gordeev v10 — current claim retained under attack

The current arXiv version is v10, dated 12 May 2026. It explicitly says its approximation controls only positive parts of double graphs.

Its auxiliary acceptance relation is based on

```text
E+ subseteq G
```

and does not test the negative part `E-`.

For the one-literal formula

```text
NOT e0
```

the real Boolean semantics accepts exactly half of the three-edge graphs, while the positive-support abstraction accepts every graph because its positive support is empty.

Machine check:

```text
semantic accepts: 4 / 8
positive-support proxy accepts: 8 / 8
false proxy accepts: 4
```

This is consistent with the 2021 Narváez–Phillips criticism that an earlier version's approximation did not control negated inputs. However, v10 contains new bridge lemmas, so this mismatch alone is not yet a complete refutation.

### Remaining decisive target

Construct a DMN term/circuit for which the positive-only approximation violates one of the exact bounds in Lemma 13 or the semantic transfer in Lemma 18, while respecting all current v10 definitions.

**Verdict:** `SERIOUS NEGATION-SENSITIVE GATE; CURRENT PROOF NOT YET TERMINALLY REFUTED`.

## New JANUS gates

### H-C028-A — No Free Direct Sum

A lower bound for one subproblem can be multiplied by the number of candidates only after proving that computations and certificates cannot be shared.

### H-C028-B — Candidate Volume Is Not Work

`2^n` potential witnesses do not imply `2^n` operations. A valid lower bound must exclude global algebraic, graph, logical, and proof-theoretic summaries.

### H-C028-C — Negation-Sensitive Approximation

Any approximation method claiming lower bounds for unrestricted Boolean circuits must control both positive and negative literal information, or prove that forgetting one side cannot invalidate its error accounting.

## Reproduction

```bash
python experiments/direct/janus_c028_model_scope_audit.py --self-test
```

Integrity:

```text
17c2abbebdeeaf6b8b31099d2692c418f09e1114f332e948edeff4132f62f1e3
```
