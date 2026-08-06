# C049.1 B4.6.3 — corrected Node-7 six-generator `up_k` hardening

## Stack

```text
BASE_PR = #112
BASE_EXACT_HEAD = 796ad144de65906c702e29928f683e6d53e3529c
GATE = C049.1_B4.6.3_CORRECTED_NODE7_SIX_GENERATOR_UP_K_HARDENING
```

Draft only. No merge and no automatic merge.

## Candidate construction

The producer binds the frozen PR #112 frontier certificate byte-for-byte and extracts exactly the six admitted corrected Node-7 zero-envelope generators:

```text
LEFT_A-HVQ00
LEFT_A-HVQ01
LEFT_A-HVQ02
LEFT_B-HVQ00
LEFT_B-HVQ01
LEFT_B-HVQ02
```

Every generator has four distinct canonical GF(2) geometry blocks. The full `6 × 6` extension-preorder matrix is computed with `(1,0)`, `(0,1)`, and `(1,1)` steps. The candidate has six reflexive relations, retains all six generators, and performs no deletion. Consequently the direct-retained-witness obligation is checked for every deletion and is vacuous on this exact family; no transitive deletion witness is used.

## Complete binary typical closure

For `k=1`, each geometry block uses the complete binary typical catalog:

```text
0, 01, 010, 1, 10, 101
```

Each four-block generator therefore has `6^4 = 1,296` scalar assignments. The complete candidate closure contains:

```text
6 × 1,296 = 7,776 entries
```

The producer materializes every source generator, four-pattern assignment, independently reconstructible trajectory digest, and width. The frozen certificate stores the complete global closure root plus six per-generator roots; the independent verifier regenerates all 7,776 entries. The producer recomputes the closure from the normalized skeletons of the closure itself and proves byte-for-byte idempotence:

```text
closure(closure(X)) = closure(X)
```

## Independent verifier

The verifier imports neither producer nor historical B1/B2 theorem cores. It independently rebuilds:

```text
GF(2) RREF normalization for all 24 generator statistics
six source generators from the frozen PR #112 certificate
all 36 preorder pairs and direct lattice witnesses
complete six-pattern scalar catalog
all 7,776 closure entries and trajectory digests
closure idempotence over all 7,776 entries
fixed-point certificate bytes and semantic digest
```

Ten digest-repaired semantic attacks are rerun through the full verifier and must fail at their expected invariant:

```text
source-head substitution
generator deletion
generator-geometry mutation
preorder-matrix flip
retained-generator deletion
scalar-catalog deletion
closure-count mutation
closure-root substitution
false idempotence
false NO_LAYOUT_AT_CAP terminal
```

## Determinism

```text
ORIGINAL
REVERSED
SEEDED_SHUFFLE
```

must produce byte-identical candidate certificates.

## Frozen candidate receipt

```text
certificate bytes  = 5,983
certificate sha256 = 593e926d9b21e2f073df4fdbdeb23f056b519bfe09f5657965615123074f85b8
semantic digest    = d5ad79fc8ec336cd64ecb9f10ec327507ef4b6a485495f1d8c558569fefc4124
closure entries    = 7,776
closure digest     = b7ffb31c984a2181b8c174ba4c5f1765305796ca19a17d5919d467656c6476a6
```

This is a candidate package pending exact-head CI and independent review. It does not admit Node-7 `up_k` merely because a frozen file exists.

## Strict boundary

```text
PR112_CORRECTED_NODE7_FRONTIER_COMPRESSION = ADMITTED
CORRECTED_NODE7_PARENT_REFINEMENT_COMPLETE = TRUE
CORRECTED_NODE7_PARENT_UP_K_COMPLETE = FALSE
CORRECTED_BOTTOM_UP_REPLAY_COMPLETE = FALSE
ROOT_PARENT_REFINEMENT_COMPLETE = FALSE
ROOT_FULL_SET_COMPUTED = FALSE
ROOT_EMPTY_PROVED = FALSE
FOUND_LAYOUT = FORBIDDEN
NO_LAYOUT_AT_CAP = FORBIDDEN
CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP = OPEN
```
