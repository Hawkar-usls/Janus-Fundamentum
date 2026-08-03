# C024 — GT Temporal Double-Bridge Safety

## Status

```text
RAW_SAME_CUT_NONCREATION = FALSIFIED
POST_UNIT_553_BIRTH_INTERPRETATION = FALSIFIED
FINITE_RAW_SAME_CUT_TRANSIENTS = TWO_CLASSIFIED
FINITE_EXACT_KEY_SAME_CUT = ABSENT_THROUGH_GT_8
T1_FROZEN_FRESH_SIDE_BARRIER = PROVED
T2A_POST_UNIT_TOTAL_COMPONENT_COLLAPSE = PROVED
T2B_BRANCH_ROUTE_CLASSIFICATION = PROVED
T2B_SELECTED_BRANCH_CUT_OR_SHIELD = OPEN
T3_EXACT_KEY_TEMPORAL_INDUCTION = PENDING_T2B
GLOBAL_CACHE_LOWER_BOUND = OPEN
P_VS_NP = OPEN
```

## Operational stages

For a reached Policy-0A state, write

```text
K  = exact entry key after pre-unit closure
R  = frozen one-pass local-Resolution output
P  = post-unit residual
B  = raw child input after the selected branch literal
K' = reached child exact key after child pre-units
```

The explicit `B` stage is necessary.  It distinguishes geometry changed by the
selected branch from extinction or contraction caused later by child pre-units.

A fresh clause in `R` is not a parent in the frozen pass which created it.  It
can become Resolution-eligible only if it survives into a later exact key.

## Exact finite stage map through GT_8

```text
K:   611 double-bridge pairs / 0 same-cut
R:  1391 double-bridge pairs / 2 same-cut transients
P:  1390 double-bridge pairs / 1 same-cut survivor
B:  1208 executed children     / 0 same-cut pairs
K':                              0 same-cut eligible pairs
```

### Frozen exact keys K

```text
root occurrences                              80
non-root occurrences                         531
tail/tail occurrences                        611
different-cut occurrences                    611
same-cut occurrences                           0
```

Every non-root exact-key pair has a unique source pair in the immediately
preceding parent `P`.

### Raw frozen-pass output R

```text
pairs inherited from K                       611
pairs requiring one fresh side               611
pairs requiring two fresh sides              169
different-cut pairs                         1389
same-cut transients                            2
tail/tail pairs                              1352
non-tail pairs                                 39
```

Raw same-cut noncreation is false.

### Post-unit residual P

```text
post-unit-created pairs                        0
raw pairs extinguished before P                1
different-cut pairs                         1389
same-cut survivors                              1
```

### Raw branch child B

Across all pre-frontier branch states:

```text
branch child records                        1208
executed children                           1208
acyclic branch assignments                  1208
cyclic branch assignments                      0
component-joining branch states              436
internal branch states                       168

same-cut pairs in P                            1
same-cut pairs in B                            0
transmitted same-cut pairs                     0
new branch same-cut births                     0
```

Thus the unique `P` transient disappears already under the selected branch.
Child pre-units are not needed to establish raw same-cut absence in the finite
trace.

## Transient A — GT_4 branch extinction

```text
state/call/novelty = 1 / 1 / 1
pivot              = 5
left               = (5,6)       [ENTRY_KEY]
right              = (-2,-5)     [LOCAL_RESOLVENT]
roles              = HEAD_SINGLETON / TAIL_SINGLETON
resolvent          = (-2,6)
```

The pair survives to `P`.  The selected branch variable is `4`.  It is absent
from both clauses, so both clauses survive syntactically under either polarity.
Nevertheless the quotient geometry changes immediately:

```text
branch -4:
  left residual  (5,6)     = COMPONENT_SPANNING, pivot 5 non-bridge
  right residual (-2,-5)   = DIRECTED_CYCLE

branch +4:
  left residual  (5,6)     = COMPONENT_SPANNING, pivot 5 non-bridge
  right residual (-2,-5)   = DIRECTED_CYCLE
```

Therefore the same-cut pair is absent in raw `B` for both children.  Later child
pre-unit/terminal behavior is secondary.

## Transient B — GT_5 post-unit conflict

```text
state/call/novelty = 8 / 10 / 3 = n-2
pivot              = 10
left/right         = (10),(-10) [both LOCAL_RESOLVENT]
roles              = BOTH_ENDPOINTS_SINGLETON / BOTH_ENDPOINTS_SINGLETON
terminal           = POST_UNIT_CONTRADICTION
```

The fresh/fresh complementary units close before a post-result exists.

## T1 — Frozen Fresh-Side Barrier

Let

```text
R = K union F,
```

where `F` is the set of fresh frozen-pass outputs.  If `K` contains no same-cut
pair, every same-cut pair first appearing in `R` contains at least one side in
`F`.  Since the parent universe remains frozen at `K`, that pair cannot be
co-eligible in the pass which creates it.

```text
T1_FROZEN_FRESH_SIDE_BARRIER = PROVED
```

Exact implementation conformance:

```text
states                         615
frozen Resolution events   14,509
fresh parent reuse              0
entry-key same-cut pairs        0
raw same-cut pairs              2
fresh sides             one:1 / two:1
```

## Pure contraction birth route

Pure contraction can create same-cut pairs.  The complete abstract gates give:

```text
one-step n=3:
  births 36 / both-safe 0 / all opposite-unit conflicts

one-step n=4:
  births 6336 / both-safe 0 / all non-unit

two-step n=4 with compound components:
  births 6048 / both-safe 2592 / both-safe non-unit 2592
```

The arbitrary quotient proof establishes:

```text
spanning + spanning birth = impossible;
internal-only source birth = impossible;
branch-safe birth requires collapse of a directed-cycle shield.
```

## T2a — Post-Unit Total-Component Collapse Barrier

Assume the exact-key induction hypothesis:

```text
all K clauses are branch-safe;
K has no same-cut co-eligible parent pair.
```

The unsafe-route theorem makes every clause in `R` branch-safe.  Before the
first component-merging post-unit, all earlier units are internal and preserve
the external graph of every surviving clause.

The source of the first external unit therefore already has a one-edge external
graph in `R`.  A branch-safe one-edge graph spans the quotient only when exactly
two relation components remain.  The first component-merging post-unit thus
merges the last two components into one.

Afterward no external edge, bridge, or nontrivial cut exists.  Contradictions
terminate before `P`.

```text
T2A_POST_UNIT_TOTAL_COMPONENT_COLLAPSE = PROVED
```

Exact support:

```text
post-unit events                            33
component-merging events                    10
internal/redundant events                   23
total-component collapses                   10
non-total component merges                   0
cycle-shield collapses                     385
collapsed residuals with a bridge             0
new same-cut births                           0
```

## T2b — proved pure branch routes

A branch same-cut threat belongs to exactly one of two routes.

### Route A — inherited pair

Suppose two source pivot bridges induce the same cut `S|T`.  If the branch
identifies one component of `S` with one component of `T`, then after deleting
the pivot the two former bridge sides share the contracted vertex.  The pivot
is no longer a bridge in either residual parent.

Assigning the pivot itself also destroys the complementary pair.

Therefore an inherited pair can survive only if both clauses survive and the
selected branch endpoints lie on the same side of the common cut.

### Route B — newly born pair

If no source pair exists but a same-cut pair appears in `B`, two spanning
sources cannot be responsible: bridge reflection and cut lifting would imply
that the source pair already existed.  An internal source cannot become
spanning.

Hence every new branch-safe pair requires at least one directed-cycle source
whose last external cycle shield collapses under the selected branch.  It must
expose a bridge and simultaneously obtain a complementary exposed bridge with
the identical cut.

```text
T2B_BRANCH_ROUTE_CLASSIFICATION = PROVED
```

## Finite Route B isolation

The branch stage collapses

```text
42,966
```

directed-cycle shields.  Only two residuals expose any bridge.  They are the
two polarities of one GT_8 lineage:

```text
source       = (-9,11,-14,-16,-17,-18,-23)
source class = DIRECTED_CYCLE
residuals    = (-9,11,-14,-17,-18,-23)
               (-9,11,-14,-16,-17,-18)
exposed edge = -17
role         = TAIL_SINGLETON
root ancestry = N_6 + four transitivity axioms
```

For the complementary literal `+17`, the two children contain 44 candidate
occurrences:

```text
DIRECTED_CYCLE         42
COMPONENT_SPANNING      2
SPANNING_NONBRIDGE      2
SAME_CUT_BRIDGE         0
```

The sole acyclic spanning candidate in each child is the canonical root clause

```text
N_6 = (6,12,17,21,24,26,-28).
```

Parallel entry edges from the merged head component keep `+17` non-bridge.
Every other complementary candidate retains a directed cycle.

Therefore both finite bridge exposures are isolated and no Route B birth
occurs.

## Remaining T2b theorem

The open GT-specific statement is now exact.

### Selected-Branch Cut-or-Shield Dichotomy

For every reachable pre-frontier branch state:

1. every inherited raw same-cut pair is crossed by the selected branch, has its
   pivot assigned, or loses one parent before exact-key admission; and
2. every cycle-shield collapse exposing a bridge has no complementary exposed
   bridge with the same cut.  Complementary occurrences remain cycle-protected,
   internal, terminally unsafe, or carry a pivot-avoiding alternate path.

Existing finite support:

```text
42 immediate-local lineages reaching a later exact key
selected branch touching bad tail                    0
selected branch joining head to another component   39
disjoint branch after head already merged             3

62 exact-key non-tail bridges
component-spanning complementary occurrences        119
explicit pivot-avoiding alternate paths             119
complementary bridge occurrences                      0
```

The expected temporal mechanism is:

```text
branch crosses an inherited common cut -> pair destroyed;
branch avoids singleton tail and merges head -> canonical N_tail shield gains
                                                 parallel edges;
disjoint branch after head merge -> existing shield is preserved.
```

Converting the exact lexicographic frequency rule and the 119 path witnesses
into an arbitrary-`n` induction is the remaining local task.

## Remaining induction

```text
T0 root same-cut absence                   available
T1 frozen fresh-side barrier               PROVED
T2a post-unit total-collapse barrier       PROVED
T2b pure branch route classification       PROVED
T2b selected-branch cut-or-shield          OPEN
T3 exact-key temporal induction            pending that theorem
```

If Selected-Branch Cut-or-Shield is proved, the temporal induction closes the
local Resolution obstruction for exact Policy-0A on graph tautologies.

The global cache lower bound remains separate: the historical `2^(n-2)`
novelty frontier must still be transferred to the exact cache DAG while
charging local proof events, terminals, and cache reuse.

## Principal artifacts

```text
proof_attempts/C024/GT_FROZEN_FRESH_SIDE_BARRIER.md
proof_attempts/C024/GT_POST_UNIT_CYCLE_SHIELD_ROUTE_CLASSIFICATION.md
proof_attempts/C024/GT_POST_UNIT_TOTAL_COMPONENT_COLLAPSE_BARRIER.md
proof_attempts/C024/GT_BRANCH_HANDOFF_ROUTE_CLASSIFICATION.md
experiments/direct/janus_tear_gt_branch_handoff_stage_census.py
experiments/direct/janus_tear_gt_branch_bridge_exposure_profile.py
experiments/direct/janus_tear_gt_bridge_shield_path_witness.py
experiments/direct/janus_tear_gt_surviving_branch_frequency_certificate.py
```

## Claim boundary

T1, T2a, and the pure branch-route classification are proved for arbitrary
`n` under the stated exact-key induction hypothesis and frozen-pass semantics.
Selected-Branch Cut-or-Shield, the completed local induction, the global
cache-DAG lower bound, unrestricted SAT lower bounds, and `P` versus `NP`
remain open.
