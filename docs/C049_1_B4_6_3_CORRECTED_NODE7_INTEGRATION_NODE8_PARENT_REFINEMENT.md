# C049.1 B4.6.3 — corrected Node-7 integration and Node-8 parent refinement

## Stack boundary

```text
BASE_PR = #113
BASE_EXACT_HEAD = 024afebb322c67953f310af48818d3386fdcfc27
GATE = C049.1_B4.6.3_CORRECTED_NODE7_INTEGRATION_AND_NODE8_PARENT_REFINEMENT
```

Draft only. No merge and no automatic merge.

## Corrected executor handoff

The admitted corrected Node-7 `up_k` certificate is replayed from its frozen source. Its complete `7,776`-entry closure is reconstructed and handed to the bottom-up state at Node 7 without fabricating generic child-pair or refinement records.

```text
NODE7_CERTIFIED_ENTRIES = 7,776
GENERIC_NODE7_PAIR_RECORDS = 0
GENERIC_NODE7_REFINEMENT_RECORDS = 0
PROCESSED_INTERNAL_NODE_IDS = [6, 7]
```

## Exact corrected Node-8 workload

Node 8 joins the corrected Node-7 full set against the 36-entry leaf-3 full set.

```text
left entries                    = 7,776
right entries                   = 36
child pairs                     = 279,936
ordinary H/V refinements        = 70,875,648
Cartesian child pairs materialized = 0
fine H/V paths materialized        = 0
```

The old diagonal-inclusive Node-8 frontier is not consumed.

## Geometry and nonidentity shrink

```text
left boundary   = [4,2]
right boundary  = [3]
common boundary = [4,2,1]
parent boundary = [4,1]
join correction = zero
shrink identity = FALSE
```

Across the 120 quotient cells:

```text
shrink correction 0 = 80
shrink correction 1 = 40
```

## Corrected H/V quotient frontier

Each of the six admitted Node-7 skeletons has exactly four ordinary H/V quotient paths against the two-state right skeleton.

```text
6 × 4 H/V paths        = 24 pre-shrink paths
post-shrink classes    = 20
source-path collisions = 4
```

All twenty generators have length five and width one. Every class is reached by a direct ordinary-H/V source path. Universal local coverage after shrink compactification replays:

```text
LOCAL_DIRECT_WITNESS_ASSIGNMENTS = 17,424
DIRECT_WITNESS_KIND = EXTENSION_PREORDER_DIRECT
TRANSITIVE_CLOSURE_USED = FALSE
```

## Candidate receipts

```text
INVARIANTS = 12/12
DIGEST_REPAIRED_TAMPERS_REJECTED = 12/12
ORIGINAL = REVERSED = SEEDED_SHUFFLE
CERTIFICATE_BYTES = 30,024
CERTIFICATE_SHA256 = 30329bdb77802016ef3479d37a29fdb8e1fc95c5d534484fc179916a0cfdbb0a
SEMANTIC_DIGEST = 41df529e471aa4fb1c0ce1192cd4e0fa8ae8de2eb230c38343bbf04abf7f6708
FROZEN_STORAGE = BASE64_CHUNKS
FROZEN_PARTS = 12
```

## Pending boundary

```text
PR113_NODE7_SIX_GENERATOR_UP_K_ADMITTED = TRUE
CORRECTED_NODE7_INTEGRATED_INTO_BOTTOM_UP_EXECUTOR = TRUE
CORRECTED_NODE8_PARENT_GENERATOR_FRONTIER_COMPLETE = TRUE
CORRECTED_NODE8_PARENT_REFINEMENT_COMPLETE = TRUE
CORRECTED_NODE8_PARENT_UP_K_COMPLETE = FALSE
CORRECTED_BOTTOM_UP_REPLAY_COMPLETE = FALSE
ROOT_PARENT_REFINEMENT_COMPLETE = FALSE
ROOT_FULL_SET_COMPUTED = FALSE
ROOT_EMPTY_PROVED = FALSE
FOUND_LAYOUT = FORBIDDEN
NO_LAYOUT_AT_CAP = FORBIDDEN
CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP = OPEN
```

Only exact-head CI and a separate semantic admission audit may open:

```text
C049.1_B4.6.3_CORRECTED_NODE8_TWENTY_GENERATOR_UP_K_HARDENING
```
