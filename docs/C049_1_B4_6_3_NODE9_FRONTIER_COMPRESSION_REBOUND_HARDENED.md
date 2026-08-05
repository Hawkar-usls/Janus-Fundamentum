# C049.1 B4.6.3 — Hardened Node-9 Frontier Compression Rebound

## Purpose

Historical PR #96 proves a structural compression of the exact Node-9 frontier, but its ancestry passes through historical PR #95. PR #101 is the admitted hardened rebound of Node-8 integration and Node-9 preflight. This layer binds the historical Node-9 theorem to PR #101 without rewriting either historical branch.

```text
hardened parent PR #101
1d4ab24c487f3508aaea2bcde6dba30493c57c53

historical theorem PR #96
02f877e96026c2844d8b4bb968cc97e148c0100b

rebound merge commit
92bc06b884e06c8ceaede709ec7df9e8fdbb3b52
```

The draft is stacked on PR #101 and must remain unmerged.

## Required replay order

The dedicated workflow must reconstruct the complete negative prefix and then replay, on one exact head:

1. Node-6 hardening and integration.
2. Node-7 frontier, `up_k`, and executor integration.
3. Exact Node-8 frontier plus its independent verifier.
4. PR #99 multiplicity hardening: 16 invariants and 20 digest-repaired tamper attacks.
5. PR #100 Node-8 `up_k`: 10 invariants and 10 digest-repaired tamper attacks.
6. PR #101 coordinate handoff and Node-9 preflight: 10 invariants and 10 digest-repaired tamper attacks.
7. Historical PR #96 Node-9 frontier compression in original, reversed, and seeded-shuffled input orders.
8. Independent Node-9 verifier and 10 digest-repaired tamper attacks.

A supplied scaffold, frontier, quotient table, full-set table, or layout is never accepted as discovery.

## Frozen theorem target

```text
Node-9 child pairs               574,128
naive fine refinements     1,284,995,408
Cartesian pairs materialized           0
fine lattice paths enumerated           0

left retained classes                  28
right leaf skeletons                    1
quotient cells                        818
quotient paths                        182
successful quotient paths             118
universal failed quotient paths        64
post-shrink generators                 15
local direct assignment checks     13,248
```

The 64 failed quotient paths retain explicit lower-envelope width witnesses. The 118 successful paths are genuinely projected through the non-identity shrink from parent geometry `[4,1]` to `[1]` and compactified to 15 generators. Direct extension-preorder coverage is required; transitive-closure-only coverage is forbidden.

## Frozen artifact

```text
bytes             312,448
sha256            6eefd8e31ba4808e5587475c2faa2c000fd0093da4de2c488db42d103c059890
semantic digest   62e9178821fe56cbf094e8512dd20b687796c6fd87e08c0fea8ea833ef6c5e80
```

## Strict boundary

Before exact-head CI admission:

```text
NODE8_INTEGRATED_INTO_EXECUTOR        = TRUE
NODE9_REACHED_ON_REBOUND_CHAIN        = TRUE
NODE9_PARENT_GENERATOR_FRONTIER_COMPLETE = FALSE
NODE9_PARENT_REFINEMENT_COMPLETE      = FALSE
NODE9_PARENT_UP_K_COMPLETE            = FALSE
ROOT_REACHED_ON_REBOUND_CHAIN         = FALSE
FOUND_LAYOUT                          = FORBIDDEN
NO_LAYOUT_AT_CAP                      = FORBIDDEN
CURRENT_GLOBAL_TERMINAL               = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP                               = OPEN
```

After green exact-head admission, the only permitted next gate is:

```text
REPLAY_AND_REBIND_PR97_TO_HARDENED_NODE9_FRONTIER_HEAD
```
