# C049.1 Phase B4.6.3 — terminal-completeness attack ledger

## Position

B4.6.2 replays every iterative-compression round of one positive fixture. It proves that the implemented positive ancestry mechanism composes across rounds, but it does not prove the biconditional needed for terminal completeness:

```text
accepting empty-boundary root entry exists
iff
there exists a whole-factor linear layout of width at most k.
```

B4.6.3 begins by attacking that missing implication with an independent bounded exhaustive oracle. This branch does not yet enable either global terminal.

## Frozen attack fixtures

The attack oracle enumerates every permutation and recomputes every prefix/suffix intersection width directly over the grouped input blocks.

```text
B4_6_2_POSITIVE_REPEATED_BLOCK
  6 permutations
  minimum width 1
  6 accepting layouts
  expected FOUND_LAYOUT

TWO_GROUPED_FULL_SPACES_NEGATIVE
  2 permutations
  minimum width 2 at k=1
  0 accepting layouts
  expected NO_LAYOUT_AT_CAP

INSERTION_ONLY_FALSE_NEGATIVE_CONTROL
  720 permutations
  minimum width 1
  72 accepting layouts
  expected FOUND_LAYOUT

ZERO_WIDTH_DISJOINT_CONTROL
  6 permutations
  minimum width 0
  6 accepting layouts
  expected FOUND_LAYOUT
```

Total: 734 complete layout replays.

The insertion control prevents terminal completeness from silently degenerating into the already-falsified insertion-only search rule.

## Attack ledger

```text
A1_ROOT_EMPTY_IFF_NO_LAYOUT
  oracle side: closed on bounded fixtures
  engine side: open

A2_OPEN_MUST_NOT_COLLAPSE_TO_NO
  classifier contract frozen
  engine interruption replay: open

A3_INSERTION_FAILURE_IS_NOT_NO_LAYOUT
  closed by explicit counterexample with 72 layouts

A4_NEGATIVE_REQUIRES_COMPLETE_ROOT_REPLAY
  exhaustive negative oracle closed
  independent empty-root engine replay: open
```

## Independent verification

The verifier imports neither the attack producer nor its linear-algebra helpers. It independently rebuilds GF(2) bases, every permutation, every cut-width vector, positive witnesses and the complete bounded negative certificate.

Digest-repaired controls alter:

- the negative terminal;
- the accepting-layout count in the insertion obstruction;
- a positive witness order; and
- the forbidden engine `NO_LAYOUT_AT_CAP` flag.

All must be rejected.

## Next constructive obligation

The attack oracle is not the JKO completeness proof. The next engine patch must expose a root-completeness receipt binding:

```text
complete child full sets
complete child Cartesian products
complete Delannoy path sets
complete width-k refinement filter
complete generator deduplication receipts
complete up_k closure
complete root entry inventory
```

For a positive root, the verifier must reconstruct ancestry and exact cut spaces. For an empty accepting root, it must independently replay the entire inventory before issuing `NO_LAYOUT_AT_CAP`.

Every capability refusal remains `OPEN_*` and preserves the exact processed prefix.

## Strict boundary

```text
BOUNDED_ATTACK_ORACLE = IMPLEMENTED
ENGINE_TERMINAL_COMPLETENESS = OPEN
FOUND_LAYOUT = FORBIDDEN_YET
NO_LAYOUT_AT_CAP = FORBIDDEN_YET
CURRENT_GLOBAL_TERMINAL = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
P_VS_NP = OPEN
```

`ROLE = JANUS_LAB_AGENT`

`MODE = DEFENSIVE_SOFTWARE_VERIFICATION`

`RUNTIME_AUTHORITY = NONE`

Draft only. No automatic merge.
