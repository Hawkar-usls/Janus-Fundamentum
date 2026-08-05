# C049.1 B4.6.3 — Node-8 up_k closure rebound onto multiplicity hardening

## Route correction

PR #94 was originally stacked directly on PR #93. PR #99 later hardened the Node-8 frontier theorem with a complete multiplicity contract. Therefore PR #94 and its descendants cannot be treated as admitted merely because their original CI was green.

This branch is a two-parent proof-carrying rebound:

```text
parent 1: PR #99 hardened multiplicity head
b85fb7a41a4cf8b7ae98c081ae6ed34df4d13f19

parent 2: PR #94 original Node-8 up_k head
f664976520ee07b1f7b0af2d88b87e512c815c83
```

The exact producer, independent verifier and workflow blobs from PR #94 are retained unchanged. The dedicated rebound workflow additionally regenerates and independently verifies the PR #99 hardening artifact before invoking Node-8 `up_k`.

## Required replay order

```text
negative prefix
-> dimension-two preorder hardening
-> node-6 integration
-> node-7 frontier
-> node-7 up_k
-> node-7 integration / node-8 preflight
-> exact PR #93 Node-8 frontier theorem
-> original PR #93 verifier
-> PR #99 multiplicity hardening
-> PR #99 independent verifier and 20 repaired tampers
-> PR #94 Node-8 up_k closure
-> PR #94 independent verifier and 10 repaired tampers
```

No supplied frontier table, multiplicity table or closure is accepted as discovery.

## Frozen boundaries

```text
Node-8 frontier classes       61
retained up_k generators      28
direct removals               33
complete reachable entries    15,948
up_k idempotent               true
```

The closure does not integrate Node-8 into the executor and does not begin Node-9 refinement.

```text
FOUND_LAYOUT             = FORBIDDEN
NO_LAYOUT_AT_CAP         = FORBIDDEN
CURRENT_GLOBAL_TERMINAL  = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP                  = OPEN
```

After exact-head CI succeeds, the next permitted gate is the sequential replay and rebound of PR #95.

Draft only. No automatic merge.
