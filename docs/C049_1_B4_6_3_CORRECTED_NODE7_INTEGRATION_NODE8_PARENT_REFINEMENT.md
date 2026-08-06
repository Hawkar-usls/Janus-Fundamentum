# C049.1 B4.6.3 — corrected Node-7 integration and Node-8 parent-refinement attack

## Exact stack

```text
BASE_PR         = #113
BASE_EXACT_HEAD = 024afebb322c67953f310af48818d3386fdcfc27
TARGET_PR       = #114
GATE            = C049.1_B4.6.3_CORRECTED_NODE7_INTEGRATION_AND_NODE8_PARENT_REFINEMENT
```

Draft only. No merge and no automatic merge.

## First executable checkpoint

The corrected Node-7 closure stores six zero-envelope generators and a frozen closure digest, but intentionally does not store all 7,776 trajectories. This checkpoint reconstructs the complete closure from the six admitted generators and the six binary typical scalar patterns.

```text
corrected Node-7 generators       = 6
assignments per generator         = 6^4 = 1,296
reconstructed closure entries     = 7,776
closure digest                    = 99a702ea7005e4a41d99fc4454040314ab106632672b267bffb5f59e29afa728
```

The reconstructed length histogram is:

```text
4:96, 5:384, 6:960, 7:1536, 8:1824,
9:1536, 10:960, 11:384, 12:96
```

Against the exact 36-entry leaf-3 family, the corrected ordinary H/V preflight is:

```text
Node-8 child pairs              = 279,936
ordinary H/V refinements        = 70,875,648
join steps                      = (1,0), (0,1)
diagonal join steps             = 0
configured pair cap             = 10,000
configured refinement cap       = 2,000,000
```

No Node-8 Cartesian pair set or fine-refinement transcript is materialized by this bootstrap.

## Current strict boundary

```text
PR113_NODE7_SIX_GENERATOR_UP_K_ADMITTED          = TRUE
CORRECTED_NODE7_EXECUTOR_INTEGRATION_IMPLEMENTED = FALSE
CORRECTED_NODE7_INTEGRATION_ADMITTED             = FALSE
CORRECTED_NODE8_PARENT_PREFLIGHT_CANDIDATE       = TRUE
CORRECTED_NODE8_PARENT_REFINEMENT_STARTED        = FALSE
CORRECTED_NODE8_PARENT_REFINEMENT_COMPLETE       = FALSE
CORRECTED_NODE8_PARENT_UP_K_COMPLETE             = FALSE
CORRECTED_BOTTOM_UP_REPLAY_COMPLETE              = FALSE
ROOT_PARENT_REFINEMENT_COMPLETE                  = FALSE
ROOT_FULL_SET_COMPUTED                           = FALSE
ROOT_EMPTY_PROVED                                = FALSE
FOUND_LAYOUT                                     = FORBIDDEN
NO_LAYOUT_AT_CAP                                 = FORBIDDEN
CURRENT_GLOBAL_TERMINAL                          = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP                                          = OPEN
NEXT_GATE                                        = CLOSED_PENDING_CURRENT_GATE_EXACT_HEAD_ADMISSION
```

This commit is the attack bootstrap, not an admission theorem. The executor bridge and complete Node-8 parent-refinement proof remain inside the current open gate.
