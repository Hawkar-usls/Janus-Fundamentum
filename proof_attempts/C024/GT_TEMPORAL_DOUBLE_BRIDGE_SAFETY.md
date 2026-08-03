# C024 — GT Temporal Double-Bridge Safety

## Status

```text
RAW_SAME_CUT_NONCREATION = FALSIFIED
FINITE_RAW_SAME_CUT_TRANSIENTS = TWO_CLASSIFIED
FINITE_EXACT_KEY_SAME_CUT = ABSENT_THROUGH_GT_8
T1_FROZEN_FRESH_SIDE_BARRIER = PROVED
T2A_POST_UNIT_TOTAL_COMPONENT_COLLAPSE = PROVED
T2B_BRANCH_ROUTE_CLASSIFICATION = PROVED
T2B_TWO_NODE_TAIL_WING_HANDOFF = PROVED
T2B_ROOT_ROUTE_ARBITRARY_N = OPEN
T2B_NONROOT_WING_REACHABILITY = OPEN
T3_EXACT_KEY_TEMPORAL_INDUCTION = PENDING_T2B
GLOBAL_CACHE_LOWER_BOUND = OPEN
P_VS_NP = OPEN
```

## Operational stages

```text
K  exact entry key after pre-unit closure
R  frozen one-pass Resolution output
P  post-unit residual
B  raw child after the selected branch
K' reached child exact key after child pre-units
```

Fresh clauses in `R` are not parents in the frozen pass which created them. The explicit `B` stage separates branch contraction from later child pre-unit effects.

## Exact finite stage map through GT_8

```text
K:   611 double-bridge pairs / 0 same-cut
R:  1391 double-bridge pairs / 2 same-cut transients
P:  1390 double-bridge pairs / 1 same-cut survivor
B:  1208 executed children     / 0 same-cut pairs
K':                              0 same-cut eligible pairs
```

The two raw same-cut transients are completely classified:

1. `GT_4`, pivot `5`, pair `(5,6)` / `(-2,-5)`: survives to `P`, but under both selected branch polarities pivot `5` becomes non-bridge in the left residual and the right residual is `DIRECTED_CYCLE`; the pair is absent already in `B`.
2. `GT_5`, pair `(10)` / `(-10)`: both sides are fresh local resolvents and close as `POST_UNIT_CONTRADICTION` before `P`.

## T1 — Frozen Fresh-Side Barrier

If

```text
R = K union F
```

and `K` contains no same-cut pair, every same-cut pair first appearing in `R` contains at least one side from the fresh set `F`. The frozen parent universe remains `K`, so the pair cannot be co-eligible in its birth pass.

```text
T1_FROZEN_FRESH_SIDE_BARRIER = PROVED
```

Implementation conformance:

```text
states                         615
frozen Resolution events   14,509
fresh parent reuse              0
raw same-cut pairs              2
fresh sides             one:1 / two:1
```

## T2a — Post-Unit Total-Component Collapse

Abstract contraction gates prove that pure contraction can create same-cut pairs, including branch-safe non-unit births after compound components are available. The arbitrary quotient classification nevertheless shows:

```text
spanning + spanning birth = impossible;
internal-only source birth = impossible;
branch-safe birth requires DIRECTED_CYCLE shield collapse.
```

Under the exact-key induction hypothesis, every clause in `R` is branch-safe. Before the first component-merging post-unit, earlier units are internal and preserve surviving external graphs. The first external unit therefore has a one-edge spanning external graph already in `R`, which is possible only with exactly two relation components. That unit collapses the last two components to one; no external bridge or cut survives.

```text
T2A_POST_UNIT_TOTAL_COMPONENT_COLLAPSE = PROVED
```

Finite support:

```text
post-unit events                            33
component-merging events                    10
all component merges                     2 -> 1
cycle-shield collapses                     385
collapsed residuals with bridge              0
new same-cut births                           0
```

## T2b — Pure branch route classification

Every branch threat belongs to one of two routes.

### Route A — inherited pair

An inherited same-cut pair can survive only if both parents survive, the selected branch does not assign the pivot, and its endpoints lie on the same side of the common bridge cut. A branch crossing the cut identifies the two sides and destroys bridgehood.

### Route B — newly born pair

A new same-cut pair from branch-safe sources requires collapse of a directed-cycle shield and simultaneous exposure of two complementary bridges with the identical cut. Two spanning sources can transmit a pair but cannot create one; bridge reflection would lift a child pair to its source.

```text
T2B_BRANCH_ROUTE_CLASSIFICATION = PROVED
```

Finite branch census:

```text
executed children                         1,208
acyclic branch assignments                1,208
same-cut pairs in P                           1
same-cut pairs in B                           0
new branch births                             0
branch cycle-shield collapses             42,966
bridge-bearing collapses                       2
same-cut complementary bridge partners         0
```

The two bridge exposures occur in one `GT_8` lineage. They expose tail-singleton edge `-17`; among 44 complementary `+17` occurrences, 42 remain `DIRECTED_CYCLE` and two are component-spanning non-bridges supplied by the canonical root clause `N_6`.

## Complete finite unshielded fate partition

To avoid filtering only successful lineages, every immediate-local unshielded non-tail bridge occurrence in `P` was replayed through every executed child:

```text
unshielded P-occurrences                  19
root                                      16
non-root                                   3
branch-polarity transitions               38

CANONICALLY_SHIELDED                      12
CLAUSE_EXTINCT                            20
SPANNING_NONBRIDGE                         2
TAIL_SINGLETON_SAFE                        4
UNSAFE_UNSHIELDED                          0
```

Every canonical shield is independently verified through the exact residual of the original non-minimality clause `N_a`, including an explicit parallel quotient edge.

## Root route

A root-only exact execution avoids the recursive search explosion and extends the handoff analysis through `GT_12`:

```text
root unshielded local occurrences          62
endpoint-touching selected branches        49
disjoint selected branches                 13
canonical-shield descendants               40
unsafe child descendants                    0
disjoint unsafe descendants                 0
```

Disjoint choices occur at `GT_4`, `GT_11`, and `GT_12`, but under both polarities they destroy bridgehood and yield `SPANNING_NONBRIDGE`. Endpoint choices yield clause extinction, tail-singleton safety, or a mechanically verified canonical shield.

The remaining GT-specific theorem is:

### Root Endpoint-or-Shield-or-Destruction

For arbitrary `n`, every root immediate-local unshielded occurrence must, under each selected branch polarity, become terminal/extinct, component-spanning non-bridge, tail-singleton safe, or canonically `N_a`-shielded.

This is finite-certified through `GT_12`, not proved asymptotically.

## Non-root route and proved tail-wing lemma

Exactly three non-root unshielded P-occurrences occur through `GT_8`, all in one depth-two `GT_8` state:

```text
(-5,-6,-7,-8,11)
(-5,-6,-7,-8,12)
(-5,-6,-7,-8,13)
```

For each bad pivot:

```text
bridge tail side                  two quotient nodes
selected literal                  -8
selected edge                     unique internal tail-wing edge
satisfying polarity               CLAUSE_EXTINCT
falsifying polarity               wing contraction -> TAIL_SINGLETON_SAFE
```

The underlying graph statement is proved:

### Two-Node Tail-Wing Handoff

If a bad bridge separates a two-node tail wing and the selected clause literal is its unique internal edge, then one polarity satisfies and removes the clause, while the other removes the selected literal, contracts the complete wing to one quotient node, and makes the bad pivot tail-singleton safe.

```text
T2B_TWO_NODE_TAIL_WING_HANDOFF = PROVED
```

What remains is GT reachability:

### Non-Root Wing Reachability

Prove that every arbitrary-`n` reachable non-root unshielded P-occurrence is already handled by another safe route or satisfies the proved two-node tail-wing hypotheses.

## Falsified selector shortcuts

The selected branch frequency does not factor through unordered quotient-component pairs:

```text
component-pair groups                     1,851
nonuniform groups                         1,133
selected groups nonuniform                  463 / 604
```

The clause-origin contribution profile is also heterogeneous. Therefore component-size or origin-class monotonicity cannot be silently substituted for the actual route proof. Frequency accounting remains a fallback diagnostic rather than the primary theorem.

## Remaining induction

```text
T0 root same-cut absence                   available
T1 frozen fresh-side barrier               PROVED
T2a post-unit total collapse               PROVED
T2b pure branch routes                     PROVED
T2b two-node tail-wing implication         PROVED
T2b root route reachability                OPEN
T2b non-root wing reachability             OPEN
T3 exact-key temporal induction            pending those two reachability lemmas
```

If the two GT-specific reachability statements are proved, T3 preserves same-cut absence through every `K -> R -> P -> B -> K'` transition and closes the local Resolution obstruction for exact Policy-0A on graph tautologies.

The global cache lower bound remains separate: the historical `2^(n-2)` novelty frontier must still be transferred to the exact cache DAG while charging local proof work, terminal events, and cache reuse.

## Principal artifacts

```text
proof_attempts/C024/GT_FROZEN_FRESH_SIDE_BARRIER.md
proof_attempts/C024/GT_POST_UNIT_TOTAL_COMPONENT_COLLAPSE_BARRIER.md
proof_attempts/C024/GT_BRANCH_HANDOFF_ROUTE_CLASSIFICATION.md
proof_attempts/C024/GT_UNSHIELDED_ROOT_LOCALIZATION.md
proof_attempts/C024/GT_NONROOT_TWO_NODE_TAIL_WING_LEMMA.md
experiments/direct/janus_tear_gt_root_unshielded_handoff_probe.py
experiments/direct/janus_tear_gt_unshielded_birth_handoff_census.py
experiments/direct/janus_tear_gt_nonroot_unshielded_wing_profile.py
```

## Claim boundary

T1, T2a, the pure branch-route classification, and the two-node tail-wing implication are proved under their explicit hypotheses. The complete finite handoff is certified through `GT_8`, and the root-only route is extended through `GT_12`. Root-route reachability for arbitrary `n`, non-root wing reachability for arbitrary `n`, T3, the global cache-DAG lower bound, unrestricted SAT lower bounds, and `P` versus `NP` remain open.
