# Active proof route — C049.1 B4.6.3 preorder appendix

## Frozen stack

```text
PR #74  C049 grouped-subspace partition obstruction
PR #75  C049.1 Phase A
PR #76  B1 compact trajectories
PR #77  B2 extension preorder and up_k
PR #78  B3 expand / join / shrink
PR #79  B4.1 cumulative round ledger and insertion obstruction
PR #80  B4.2-B4.5 charged scaffold and bottom-up full sets
PR #81  B4.6.1 witness reconstruction
PR #83  B4.6.2 complete positive iterative-compression cycle
PR #86  B4.6.3 terminal-completeness attack and honest negative prefix
PR #87  dimension-two preorder minimization hardening
```

## Closed gate

The PR #86 negative transcript reaches node 6 with `468` unique generators and
then stops inside the generic B2 minimizer. PR #87 closes that exact obstruction
without raising the work cap:

```text
468 input generators
-> 3 stutter-skeleton buckets
-> 3 canonical zero envelopes
-> 465 direct deletion witnesses
-> exact 468-entry reachable closure
```

All eight preorder admission invariants pass. Every deletion is direct and
traceable. The exact reachable set is unchanged.

## Surviving route

```text
PR #86 complete negative prefix
-> PR #87 hardened node-6 preorder and reachable up_k receipt
-> inject certified node-6 closure into bottom-up executor
-> execute parent full-set refinements
-> continue to empty root
-> prove root biconditional
-> only then consider NO_LAYOUT_AT_CAP
```

## Binding prohibitions

```text
INSERTION_FAILURE != NO_LAYOUT_AT_CAP
OPEN_WORK_BUDGET  != NO_LAYOUT_AT_CAP
NODE_6_CLOSURE    != NEGATIVE_ROOT_COMPLETENESS
EMPTY_ROOT        != NO_LAYOUT_AT_CAP until the published biconditional is replayed
```

## Current terminal

```text
DIMENSION_TWO_PREORDER_MINIMIZATION = COMPLETE
NODE_6_REACHABLE_UP_K_SET           = COMPLETE
NEGATIVE_ROOT_REACHED               = FALSE
TERMINAL_COMPLETENESS               = OPEN
FOUND_LAYOUT                        = FORBIDDEN_YET
NO_LAYOUT_AT_CAP                    = FORBIDDEN_YET
CURRENT_GLOBAL_TERMINAL             = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
NEXT_GATE                           = C049.1_B4.6.3_NEGATIVE_NODE_6_UP_K_INTEGRATION_AND_PARENT_REFINEMENT
P_VS_NP                             = OPEN
```

No automatic merge.
