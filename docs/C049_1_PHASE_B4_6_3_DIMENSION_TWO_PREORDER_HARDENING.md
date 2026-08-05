# C049.1 B4.6.3 — dimension-two preorder minimization hardening

## Binding obstruction

PR #86 reaches node `6` of the frozen genuine negative fixture with all B3
refinements retained, but the generic B2 minimizer exhausts its work capability
while comparing `468` distinct compact generators over a two-dimensional
boundary. The engine therefore returns `OPEN_TRAJECTORY_ENGINE_INCOMPLETE`.
Increasing the cap is not accepted as a proof.

## Structural lemma

For an extension-preorder witness, every visited lattice cell has identical
`(left,right)` boundary subspaces. Consequently two trajectories can be related
only when their sequences of `(left,right)` symbols agree after consecutive
repetitions are collapsed. This is the **stutter skeleton signature**.

The frozen family splits exactly into three signatures:

```text
216 generators
216 generators
 36 generators
```

Each bucket contains one unique all-zero trajectory with one statistic per
skeleton run. Because all trajectory values are nonnegative, that zero envelope
is a direct strict predecessor of every other trajectory in its bucket and has
no strict predecessor itself. Cross-bucket domination is impossible by the
stutter-signature invariant.

Therefore exact minimization is:

```text
468 input generators
  3 retained zero envelopes
465 direct deletion witnesses
```

No transitive-only deletion is admitted. Every removed generator points
directly to its retained predecessor and carries the deterministic JKO lattice
path.

## Exact reachable closure

At `k=1`, exhaustive scalar typical-sequence reduction through the published
length bound tests all `65,534` nonempty binary sequences of lengths `1..15`.
Exactly six compact run patterns remain:

```text
0
01
010
1
10
101
```

The three frozen skeleton signatures contain no repeated run symbol. Hence their
complete reachable catalogs are the Cartesian products of these six run
patterns:

```text
6^3 + 6^3 + 6^2 = 468
```

This catalog is exactly the original `468`-generator set. Thus

```text
up_k(original generators) = up_k(three retained generators)
```

is checked without enumerating unrelated dimension-two trajectories and without
accepting a supplied full-set table.

## Eight machine invariants

```text
INV-01 canonical_preorder_unique           PASS
INV-02 dominance_only_from_certificates    PASS
INV-03 every_removed_has_direct_witness    PASS
INV-04 reachable_witness_set_unchanged     PASS
INV-05 independent_replay_identical        PASS
INV-06 proof_layer_frozen_and_hashable     PASS
INV-07 deterministic_output_byte_identical PASS
INV-08 every_deletion_fully_traceable      PASS
```

The independent verifier does not import the producer. It rebuilds canonical
RREF, all generator trajectories, every skeleton bucket, all direct and reverse
preorder tests, the complete binary run catalog, every reachable closure entry,
all charged counters, fixed-point bytes and the strict terminal boundary. Five
semantic modifications are rejected after all affected digests are repaired.

## Strict boundary

This closes preorder minimization and the exact reachable `up_k` set at node 6.
It does not yet inject that closure into the bottom-up engine, execute the parent
refinements, reach the empty root or prove terminal completeness.

```text
DIMENSION_TWO_PREORDER_MINIMIZATION = COMPLETE
NODE_6_REACHABLE_UP_K_SET           = COMPLETE
NEGATIVE_ROOT_REACHED               = FALSE
FOUND_LAYOUT                        = FORBIDDEN_YET
NO_LAYOUT_AT_CAP                    = FORBIDDEN_YET
CURRENT_GLOBAL_TERMINAL             = OPEN_TRAJECTORY_ENGINE_INCOMPLETE
NEXT_GATE                           = C049.1_B4.6.3_NEGATIVE_NODE_6_UP_K_INTEGRATION_AND_PARENT_REFINEMENT
P_VS_NP                             = OPEN
```

Draft only. No automatic merge.
