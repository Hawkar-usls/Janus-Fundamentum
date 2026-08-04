# C049.1 Phase B4.6.3 — root full-set completeness receipt

## Purpose

This patch converts the B4.5/B4.6.2 chunk transcript into a streaming, machine-checkable inventory receipt. It closes the quantitative chain without pretending that inventory equality alone proves the semantics of `up_k`.

For every internal node the receipt checks:

```text
left entry count * right entry count = child pairs replayed
sum(pair Delannoy counts) = refinement attempts replayed
refinements = successful + failed
successful attempt ids = disjoint union of generator provenance ids
unique successful trajectories = generator records
duplicate deletions + B2 dominance deletions = deletion records
node_up_k entry_count = serialized entries = output receipt entry_count
```

## Streaming requirement

The round-03 transcript expands to roughly 950 MB. A verifier that materializes every nested refinement record is not an admissible design: it can exhaust memory before reaching the root. The receipt therefore scans one compressed chunk at a time and retains only counters, successful attempt identifiers and generator provenance identifiers.

## Critical separation

The receipt distinguishes two obligations:

```text
INVENTORY_COMPLETENESS
SEMANTIC_UP_K_REPLAY
```

The current patch establishes only the first candidate. It intentionally emits:

```text
semantic_up_k_replay_complete = false
terminal_classifier = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
```

Even when all quantitative equalities hold and an accepting root entry is visible, neither `FOUND_LAYOUT` nor `NO_LAYOUT_AT_CAP` is enabled. The next patch must independently reconstruct every retained generator, dominance witness, extension path and exact `up_k` closure before terminal classification is legal.

## Tamper controls

The verifier rejects digest-repaired attempts to:

- assert outer completeness without node equality;
- claim semantic replay from the inventory receipt;
- promote the receipt to `NO_LAYOUT_AT_CAP`;
- enable the negative terminal flag.

## Strict boundary

```text
ROOT_INVENTORY_COMPLETENESS_RECEIPT = IMPLEMENTED_CANDIDATE
SEMANTIC_UP_K_REPLAY                = OPEN
FOUND_LAYOUT                        = FORBIDDEN_YET
NO_LAYOUT_AT_CAP                    = FORBIDDEN_YET
CURRENT_GLOBAL_TERMINAL             = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
NEXT_GATE                           = B4.6.3_INDEPENDENT_SEMANTIC_UP_K_ROOT_REPLAY
P_VS_NP                             = OPEN
```
