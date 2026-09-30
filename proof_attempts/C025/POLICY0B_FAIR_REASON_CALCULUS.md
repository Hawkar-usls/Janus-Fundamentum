# C025 — Policy-0B Fair Proof-Carrying Reason Calculus

**Status:** design; fair frozen-layer scheduler bound proved; implementation gate active.

**Claim ceiling:** no polynomial-SAT or P-vs-NP conclusion is claimed.

## Origin

C024 Issue #211 refuted the universal polynomial residual-count premise for current Policy-0A. The counterfamily exploits the single global early-pivot cutoff in local Resolution. C025 treats the counterexample as a design constraint.

## Lemma 1 — complete one-layer pair scheduling is polynomial in current state size

For a frozen pre-resolution key `K`, let `p_x` and `q_x` be the numbers of clauses containing `x` and `~x`. Let `L` be total literal occurrences. A scheduler that visits every frozen complementary parent pair exactly once performs

```text
A(K) = sum_x p_x q_x
```

attempts. Since

```text
sum_x p_x + sum_x q_x = L,
```

we have

```text
A(K) <= (sum_x p_x)(sum_x q_x) <= L^2/4.
```

Thus a complete fair frozen-layer scan is polynomial in the current representation size and has no early-pivot starvation. □

This removes the exact C024 resolution-sink failure class: an irrelevant earlier pivot can add attempts, but cannot prevent a later pivot from being visited.

## What this lemma does not prove

- `L` is not yet polynomially bounded in original input length; Issue #212 remains active.
- retaining every resolvent can create `O(L^2)` new clauses in one layer and compound across depth;
- visiting every core pivot does not guarantee useful proof progress;
- a short proof in a stronger proof system does not give a deterministic polynomial-time proof-search algorithm.

## Policy-0B target resources

Policy-0B separates:

```text
FAIR_FROZEN_LAYER_INFERENCE
EXACT_RESIDUAL_CACHE
CONTEXT_INDEPENDENT_PROOF_CARRYING_REASON
ACTIVE_REPRESENTATION_NORMALIZER
CERTIFICATE_AND_REPLAY_LEDGER
```

A returned reason must have a standalone verifier and a proved reuse condition. The extraction/search algorithm is charged separately.

## Killer gates

```text
C025-A FAIR_SCHEDULER_IMPLEMENTATION           = ACTIVE
C025-B REASON_SOUNDNESS                        = OPEN
C025-C DETERMINISTIC_REASON_EXTRACTION_COST    = OPEN
C025-D PROOF_EXISTENCE_VS_SEARCH_GAP            = OPEN
C025-E POLYNOMIAL_ACTIVE_REPRESENTATION         = OPEN / linked to #212
C025-F ADVERSARIAL_FAMILY_SUITE                 = OPEN
```

Required adversaries include source `GT_n`, C024 padded GT, masked/lifted Tseitin, PHP and padding attacks against ordering/frequency/index structures.

## Hard law

```text
SHORT_PROOF_EXISTS != DETERMINISTIC_POLICY_FINDS_SHORT_PROOF
```

Any proof-system simulation theorem is admitted only at its actual proof-existence/translation scope unless a deterministic proof-search theorem is separately established.

`P_VS_NP = OPEN`.
