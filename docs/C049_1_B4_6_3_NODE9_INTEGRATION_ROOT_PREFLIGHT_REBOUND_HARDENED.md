# C049.1 B4.6.3 — hardened Node-9 integration and root preflight rebound

## Route repair

Historical PR #98 integrates the certified Node-9 `up_k` family into the bottom-up executor and reaches the root preflight, but its ancestry descends from historical PR #97. PR #103 is the admitted hardened rebound of the complete Node-9 `up_k` closure. This layer performs the fifth and final sequential rebound without rewriting either historical branch.

```text
HARDENED_PARENT = PR #103
775c00396f629ae0361fbc0993e4ce936cbc97e4

HISTORICAL_PARENT = PR #98
69c090d432d2af7910b328f763f99b87ab897b3d

TWO_PARENT_REBOUND_COMMIT =
f5beeebf59dfa9d0b738fdfe9f989c70bcdb6a43
```

## Executable contract

The dedicated workflow first executes every literal shell gate from the admitted PR #103 workflow on the exact candidate head. It then consumes only the regenerated frozen Node-9 frontier and `up_k` artifacts.

```text
negative prefix
-> Node-6 hardening/integration
-> Node-7 frontier/up_k/integration
-> exact Node-8 frontier and independent verifier
-> PR #99 multiplicity hardening
-> PR #100 Node-8 up_k
-> PR #101 coordinate handoff/integration
-> PR #102 Node-9 frontier compression
-> PR #103 Node-9 up_k closure
-> historical PR #98 Node-9 integration
-> independent integration verifier
-> exact root preflight
```

No supplied frontier, full-set table, root table, compact-universe table, or layout is accepted as discovery.

## Frozen bridge target

```text
INPUT_GENERATORS    = 15
RETAINED_GENERATORS = 2
DIRECT_REMOVALS     = 13
NODE9_UP_K_ENTRIES  = 252

NODE9_OUTPUT_RECEIPT =
1a23cdd127a35932d8515c742034e67443ebf4c2a42ac06458f809d63d65ca5a

GENERIC_NODE9_PAIR_RECORDS       = 0
GENERIC_NODE9_REFINEMENT_RECORDS = 0
```

The closure is already expressed in coordinates of parent boundary `[1]`. Only `execute_node(node_id=9)` is replaced by the certified handoff; the generic executor then continues to Node 10.

## Root preflight target

```text
PROCESSED_INTERNAL_NODE_IDS = [6,7,8,9]
ROOT_NODE                   = 10
LEFT_CHILD_NODE9_ENTRIES    = 252
RIGHT_CHILD_LEAF5_ENTRIES   = 36
ROOT_CHILD_PAIRS            = 9,072
ROOT_NAIVE_REFINEMENTS      = 4,954,128
```

```text
PAIR_CAP                    = 10,000
PAIR_CAP_EXCEEDED           = FALSE
REFINEMENT_CAP              = 2,000,000
REFINEMENT_CAP_EXCEEDED     = TRUE
STOP_REASON                 = REFINEMENT_CAP_EXCEEDED
NO_LAYOUT_AT_CAP            = FALSE
```

No root pair or refinement transcript is fabricated. The root full set is not computed.

## Root geometry

```text
LEFT_BOUNDARY    = [1]
RIGHT_BOUNDARY   = [1]
COMMON_BOUNDARY  = [1]
PARENT_BOUNDARY  = []

LEFT_EXPAND_IDENTITY  = TRUE
RIGHT_EXPAND_IDENTITY = TRUE
SHRINK_IDENTITY       = FALSE
```

The next theorem must therefore cover a genuine shrink from boundary `[1]` to the empty root boundary.

## Frozen byte boundary

```text
MANIFEST_BYTES = 16,175,333
MANIFEST_SHA256 =
563bc6d4148dfb94e7c5aa3c9b8e6ffa28e0b0e9cc6603fe0bffe39e71a636a9
MANIFEST_DIGEST =
cb124decfa45c2adfd58fe7bf86c9e8a7cd45afff84dde4ff90d4090721c74fd

SUMMARY_BYTES = 4,406
SUMMARY_SHA256 =
640d0a9f18d7a0e7639d4f0c4fa9d2acfe691662af70b2ad5b2f89458fc8faf0
SUMMARY_SEMANTIC_DIGEST =
dc790f6294afb5fec24b5e8686f32725eb616b3125364d11a1fcb4d24b269443
```

## Proof controls

```text
NODE8_MULTIPLICITY_INVARIANTS = 16/16
NODE9_FRONTIER_INVARIANTS     = 10/10
NODE9_UP_K_INVARIANTS         = 10/10
NODE9_INTEGRATION_INVARIANTS  = 10/10
DIGEST_REPAIRED_TAMPERS       = 70/70
```

## Strict pre-admission boundary

```text
NODE9_PARENT_UP_K_COMPLETE               = TRUE
NODE9_INTEGRATED_INTO_BOTTOM_UP_EXECUTOR = FALSE
ROOT_REACHED_ON_REBOUND_CHAIN            = FALSE
ROOT_PARENT_REFINEMENT_STARTED           = FALSE
ROOT_PARENT_REFINEMENT_COMPLETE          = FALSE
ROOT_FULL_SET_COMPUTED                   = FALSE
ROOT_EMPTY_PROVED                        = FALSE
TERMINAL_COMPLETENESS_PROVED             = FALSE
FOUND_LAYOUT                             = FORBIDDEN
NO_LAYOUT_AT_CAP                         = FORBIDDEN
CURRENT_GLOBAL_TERMINAL                  = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP                                  = OPEN
```

After exact-head green admission, the only permitted gate is:

```text
C049.1_B4.6.3_ROOT_PARENT_FRONTIER_STRUCTURAL_COMPRESSION
```
