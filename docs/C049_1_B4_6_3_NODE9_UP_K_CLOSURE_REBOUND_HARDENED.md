# C049.1 B4.6.3 — hardened Node-9 `up_k` rebound

## Route position

This layer is the fourth sequential rebound after the Node-8 multiplicity hardening.

```text
PR #99   Node-8 multiplicity hardening             ADMITTED
PR #100  Node-8 up_k rebound                       ADMITTED
PR #101  Node-8 integration rebound                ADMITTED
PR #102  Node-9 frontier rebound                   ADMITTED
this PR  Node-9 up_k rebound                       CI PENDING
PR #98   Node-9 integration and root preflight     CONDITIONAL
```

The historical theorem is not rewritten. Its exact producer, independent verifier, and workflow blobs from PR #97 are attached to a two-parent commit whose first parent is the admitted exact head of PR #102.

```text
hardened parent  78b59bf447702146190070619fa03732481633f4
historical parent 7b537512fe45ef01f50912c22365716a41e0275f
rebound commit   4a2fa5acfd6bc97de3a94e1784a159c5a737ae8d
```

Draft only. No merge and no automatic merge.

## Exact replay rule

The dedicated workflow does not trust the historical PR #97 ancestry. It first executes every literal shell `run` step from the admitted PR #102 hardened workflow on the current exact head. This reconstructs and independently checks the complete chain through the frozen Node-9 frontier, including the Node-8 multiplicity hardening and all downstream rebound gates.

Only after that replay produces the exact frozen Node-9 frontier may the historical Node-9 `up_k` producer run.

```text
negative prefix
-> Node-6 hardening and integration
-> Node-7 frontier, up_k, and integration
-> exact Node-8 frontier and independent verifier
-> 16-invariant Node-8 multiplicity hardening
-> Node-8 up_k and independent verifier
-> Node-8 coordinate handoff and independent verifier
-> Node-9 frontier in three orders and independent verifier
-> Node-9 up_k in three orders and independent verifier
```

No supplied frontier, full-set table, compact-universe table, or layout is accepted as discovery.

## Frozen closure theorem

The exact fifteen post-shrink generators are compared under the direct extension preorder.

```text
input generators             15
ordered pair tests          225
relation edges               55
self relation edges          15
cross relation edges         40
equivalent cross pairs        0
retained generators           2
direct removals              13
```

The retained source classes are exactly:

```text
N9-S02
N9-S07
```

Every removal is certified by a direct retained predecessor. No transitive-closure-only deletion is accepted.

The six binary typical scalar patterns are:

```text
0, 01, 010, 1, 10, 101
```

Their direct scalar relation has 20 edges and 50 transitivity checks. Blockwise upward-set construction followed by global compactification yields the complete closure:

```text
N9-S02 reachable entries  216
N9-S07 reachable entries   36
complete reachable set    252
repeated closure checks  8,400
idempotent                TRUE
```

Every reachable entry carries a direct witness from one retained generator. The global compact trajectory universe is not enumerated.

## Frozen artifact boundary

```text
artifact bytes  555,527
artifact sha256 c6e369099ea2fdf6572409dab7ce6f5172d40543388b366ec37a821262c506e4
semantic digest f90aa04716ca2fa9019449e19b5866ac443cf545253bb41ae212dd3c68212713
```

`ORIGINAL`, `REVERSED`, and `SEEDED_SHUFFLE` must produce byte-identical artifacts.

## Adversarial controls

The new workflow inherits 50 digest-repaired tamper rejections from the hardened chain through PR #102 and requires the historical Node-9 `up_k` verifier to reject its ten attacks after digest repair.

```text
required digest-repaired tamper rejections = 60/60
```

## Strict boundary

Before exact-head CI admission:

```text
NODE9_PARENT_GENERATOR_FRONTIER_COMPLETE = TRUE
NODE9_PARENT_REFINEMENT_COMPLETE         = TRUE
NODE9_PARENT_UP_K_COMPLETE               = FALSE / CI PENDING
NODE9_INTEGRATED_INTO_BOTTOM_UP_EXECUTOR = FALSE
ROOT_REACHED_ON_REBOUND_CHAIN            = FALSE
ROOT_PARENT_REFINEMENT_STARTED           = FALSE
TERMINAL_COMPLETENESS_PROVED             = FALSE
FOUND_LAYOUT                             = FORBIDDEN
NO_LAYOUT_AT_CAP                         = FORBIDDEN
CURRENT_GLOBAL_TERMINAL                  = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP                                  = OPEN
```

After a green exact-head replay, the only permitted next gate is:

```text
REPLAY_AND_REBIND_PR98_TO_HARDENED_NODE9_UP_K_HEAD
```
