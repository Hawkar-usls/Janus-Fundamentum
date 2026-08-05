# C049.1 B4.6.3 — Hardened Node-8 integration and Node-9 preflight rebound

## Purpose

Historical PR #95 integrated the Node-8 `up_k` closure into the bottom-up executor and reached the exact Node-9 capacity preflight. It was based on historical PR #94, before PR #99 hardened Node-8 frontier multiplicity accounting and PR #100 rebound the Node-8 `up_k` theorem onto that hardened foundation.

This draft does not rewrite PR #95. It creates a new proof-carrying ancestry with two parents:

```text
PR #100 admitted hardened Node-8 up_k head
7d09ff12a6112e217673b97b0576c829a6711cef

historical PR #95 theorem head
655676a4227aee4606688016a6e99bc9497b0f13

rebound merge commit
c08998c846eddb84bed4a4e25efd8ebbfeed4f6b
```

## Required replay order

The dedicated workflow must independently execute:

```text
frozen negative prefix
-> Node-6 hardening and integration
-> Node-7 frontier, up_k and integration
-> exact Node-8 frontier and original verifier
-> PR #99 multiplicity hardening and 20 repaired tampers
-> PR #100 Node-8 up_k and 10 repaired tampers
-> PR #95 coordinate handoff and executor integration
-> independent integration verifier and 10 repaired tampers
-> exact Node-9 pair and Delannoy preflight
```

A supplied frontier, multiplicity table, full-set table, branch decomposition or layout is never accepted as discovery.

## Frozen target

```text
Node-8 closure entries       15,948
Node-8 retained generators       28
Node-8 direct removals            33
Node-9 child pairs           574,128
Node-9 naive refinements 1,284,995,408
Node-9 stop reason CHILD_PAIR_CAP_EXCEEDED
```

The integration must preserve the exact coordinate conversion into parent boundary `[4,1]`, all whole-factor identities and affine offsets, and must emit no decorative generic Node-8 pair or refinement records.

## Strict boundary

Until exact-head CI succeeds:

```text
NODE8_INTEGRATED_INTO_BOTTOM_UP_EXECUTOR = FALSE
NODE9_REACHED_ON_REBOUND_CHAIN           = FALSE
NODE9_PARENT_REFINEMENT_STARTED          = FALSE
FOUND_LAYOUT                             = FORBIDDEN
NO_LAYOUT_AT_CAP                         = FORBIDDEN
CURRENT_GLOBAL_TERMINAL                  = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP                                  = OPEN
```

After admission, only the sequential PR #96 rebound is permitted. Draft only; no automatic merge.
