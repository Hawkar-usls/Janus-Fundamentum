# C049.1 B4.6.3 — corrected Node-8 parent frontier compression

## Exact stack

```text
BASE_PR         = #114
BASE_EXACT_HEAD = cb1c1151c8a71defb72a86cb05ee4fec92ecc046
TARGET_PR       = #115
GATE            = C049.1_B4.6.3_CORRECTED_NODE8_PARENT_FRONTIER_COMPRESSION
```

Draft only. No merge and no automatic merge.

## Corrected source frontier

The source chain is the admitted corrected Node-7 integration checkpoint. The complete Node-7 closure is reconstructed from six zero-envelope generators and is never accepted as a supplied full-set table.

```text
corrected Node-7 zero-envelope classes = 6
corrected Node-7 closure entries        = 7,776
Node-8 right leaf entries               = 36
Node-8 child pairs                      = 279,936
ordinary H/V refinements                = 70,875,648
diagonal join steps                     = 0
```

No child Cartesian product and no fine-refinement transcript is materialized by this candidate.

## First executable compression result

Every corrected left zero envelope has length four. The right leaf zero envelope has length two. Each `4 × 2` grid therefore has exactly four ordinary horizontal/vertical quotient paths.

```text
6 left classes × 4 ordinary H/V paths = 24 quotient paths
quotient cells checked                 = 120
```

The exact Node-8 geometry is replayed in ambient `GF(2)^3`:

```text
left boundary   = [4,2]
right boundary  = [3]
common boundary = [4,2,1]
parent boundary = [4,1]
left expansion  = identity
shrink          = non-identity
```

Join correction is zero on all 120 quotient cells. Genuine shrink produces:

```text
shrink correction 0 = 80 cells
shrink correction 1 = 40 cells
```

After shrink and canonical compactification:

```text
pre-shrink quotient paths = 24
post-shrink classes       = 20
source-path collisions    = 4
multiplicity histogram    = 16 × 1, 4 × 2
class length histogram    = 20 × length 5
class width histogram     = 20 × width 1
```

Every class stores a direct quotient-path reachability witness. Universal local direct coverage replays `17,424` binary typical-pattern assignments under the extension preorder. No transitive-closure-only witness is accepted.

## Independent controls

The verifier imports neither the candidate producer nor the historical contaminated Node-8 compression theorem. It independently reconstructs:

```text
GF(2) sum/intersection and coordinate lifting
24 ordinary H/V quotient paths
120 join/shrink correction cells
20 post-shrink classes and the complete path partition
17,424 direct coverage checks
12 invariant gates
10 digest-repaired tamper rejections
```

Original, reversed, and seeded-shuffle source orders must produce byte-identical certificates.

## Strict current boundary

```text
PR114_CORRECTED_NODE7_INTEGRATION_ADMITTED          = TRUE
CORRECTED_NODE8_PARENT_REFINEMENT_STARTED           = TRUE
CORRECTED_NODE8_PARENT_GENERATOR_FRONTIER_CANDIDATE = TRUE
CORRECTED_NODE8_PARENT_FRONTIER_COMPRESSION_ADMITTED = FALSE
CORRECTED_NODE8_PARENT_REFINEMENT_COMPLETE          = FALSE
CORRECTED_NODE8_PARENT_UP_K_COMPLETE                = FALSE
CORRECTED_NODE8_INTEGRATED_INTO_EXECUTOR            = FALSE
CORRECTED_BOTTOM_UP_REPLAY_COMPLETE                 = FALSE
ROOT_PARENT_REFINEMENT_COMPLETE                     = FALSE
ROOT_FULL_SET_COMPUTED                              = FALSE
ROOT_EMPTY_PROVED                                   = FALSE
FOUND_LAYOUT                                        = FORBIDDEN
NO_LAYOUT_AT_CAP                                    = FORBIDDEN
CURRENT_GLOBAL_TERMINAL                             = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP                                             = OPEN
NEXT_GATE                                           = CLOSED_PENDING_CURRENT_GATE_EXACT_HEAD_ADMISSION
```

This draft attacks the current gate. It does not admit the twenty-class frontier and does not open an `up_k` gate.
