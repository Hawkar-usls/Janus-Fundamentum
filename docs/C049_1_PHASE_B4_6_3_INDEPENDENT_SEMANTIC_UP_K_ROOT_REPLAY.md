# C049.1 Phase B4.6.3 — independent semantic up_k root replay

## Purpose

The inventory receipt proves that the serialized child-pair, refinement, generator, deletion, and root-entry counts are internally complete. This patch checks the stronger semantic obligation.

For every internal node of every B4.6.2 round, an independent verifier streams the chunked transcript and reconstructs:

```text
all successful refinement outputs
-> exact trajectory equivalence classes
-> canonical successful generator family
-> duplicate-attempt partition
-> ordered up_k input generator handoff
-> exact extension preorder
-> exact retained generator family
-> every dominance/equivalence removal witness
-> complete bounded trajectory universe
-> exact up_k closure entries and extension witnesses
-> output receipt entry count and entries digest
```

The verifier imports neither the B4.5/B4.6 producer nor the B2 implementation core. Its GF(2), compactification, extension-preorder, universe-generation, minimization, and closure routines are independent copies aligned with the hardened B2 transcript verifier.

## Streaming boundary

The round-03 transcript expands to roughly 950 MB. The verifier therefore reads one deterministic gzip chunk at a time. It does not materialize the refinement transcript. Only the successful output partition and the much smaller generator/deletion inventories are retained.

This is part of the proof contract: a completeness verifier that requires unbounded transcript materialization would not be a usable independent replay at the scale already reached by B4.6.2.

## Local result

On the frozen positive B4.6.2 cycle, both rounds replay semantically. For every node:

- successful refinement outputs equal the serialized unique generator family;
- provenance attempt lists form an exact disjoint partition;
- duplicate deletion records equal all noncanonical successful attempts;
- `input_generator_provenance` reconstructs the exact `node_up_k.input_generators` order;
- independent minimization reproduces every retained generator and removal witness;
- independent universe enumeration and extension checks reproduce the complete `entries` array;
- output receipt counts and entry digests match.

## Strict boundary

This closes semantic `up_k` replay on the positive frozen cycle. It does **not** yet establish terminal completeness for a genuine negative engine run. The engine still lacks a complete executed negative root transcript whose empty accepting set is independently replayed.

```text
INVENTORY_COMPLETENESS = GREEN_CANDIDATE
SEMANTIC_UP_K_REPLAY_POSITIVE_CYCLE = IMPLEMENTED_CANDIDATE
NEGATIVE_ROOT_ENGINE_REPLAY = OPEN
TERMINAL_COMPLETENESS = OPEN
FOUND_LAYOUT = FORBIDDEN_YET
NO_LAYOUT_AT_CAP = FORBIDDEN_YET
CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP = OPEN
```

H002/PR #84 and SIM-3 remain outside the proof perimeter.
