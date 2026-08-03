# C024 — GT Temporal Double-Bridge Safety

## Status

```text
RAW_SAME_CUT_NONCREATION = FALSIFIED
POST_UNIT_553_BIRTH_INTERPRETATION = FALSIFIED
FINITE_RAW_SAME_CUT_TRANSIENTS = TWO_CLASSIFIED
FINITE_EXACT_KEY_SAME_CUT = ABSENT_THROUGH_GT_8
T1_FROZEN_FRESH_SIDE_BARRIER = PROVED
T2A_POST_UNIT_TOTAL_COMPONENT_COLLAPSE = PROVED
T2B_BRANCH_HANDOFF_EXTINCTION = OPEN
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
K' = reached child exact key after branch restriction and child pre-units
```

A fresh clause in `R` is not a parent in the frozen pass which created it.  It
can become Resolution-eligible only if it survives into a later exact key.

## Exact finite stage map through GT_8

```text
K:   611 double-bridge pairs / 0 same-cut
R:  1391 double-bridge pairs / 2 same-cut transients
P:  1390 double-bridge pairs / 1 same-cut survivor
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
preceding parent `P`.  No branch/child-preunit transition creates a new
exact-key pair in the finite trace.

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

## Transient A — GT_4 branch handoff

```text
state/call/novelty = 1 / 1 / 1
pivot              = 5
left               = (5,6)       [ENTRY_KEY]
right              = (-2,-5)     [LOCAL_RESOLVENT]
roles              = HEAD_SINGLETON / TAIL_SINGLETON
resolvent          = (-2,6)
```

The pair survives to `P`.

```text
branch -4:
  both residual clauses remain;
  the child terminates before exact-key admission.

branch +4:
  child pre-unit 5=false removes the fresh right clause;
  the child terminates.
```

No same-cut pair reaches `K'`.

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

This is a set-theoretic arbitrary-`n` proof.

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

## Pure post-unit birth route

Pure contraction can create same-cut pairs.  The complete abstract gates give:

```text
one-step n=3:
  births 36 / both-safe 0 / all opposite-unit conflicts

one-step n=4:
  births 6336 / both-safe 0 / all non-unit

two-step n=4 with compound components:
  births 6048 / both-safe 2592 / both-safe non-unit 2592
```

The two-step gate falsifies universal safe-source exclusion.  Every both-safe
birth, however, contains at least one `DIRECTED_CYCLE` source.  No
`COMPONENT_SPANNING + COMPONENT_SPANNING` birth occurs.

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

The unsafe-route theorem then implies every clause in `R` is branch-safe.

Consider the first post-unit which joins two distinct relation components.
Every earlier unit is internal.  Internal unit assignments do not change the
external graph of any surviving clause.  Therefore the source of the first
external unit already has the same one-edge external graph in `R`.

A branch-safe clause with exactly one external edge can be component-spanning
only when exactly two quotient components remain.  Thus the first
component-merging unit joins the last two components and collapses the entire
quotient to one component.

Afterward:

```text
no external edge exists;
no bridge cut exists;
no same-cut pair can survive.
```

If unit closure finds opposite units or an empty clause, the state terminates
before `P` is admitted.

Therefore post-unit closure cannot create a surviving same-cut pair.

```text
T2A_POST_UNIT_TOTAL_COMPONENT_COLLAPSE = PROVED
```

Exact support through GT_8:

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

All ten merge reasons have the same exact finite profile:

```text
novelty                         n-2
reason candidates                 1
reason origin       LOCAL_RESOLVENT
reason width                       1
producing events                   1
parents                         (2,2)
parent safety     SPANNING + DIRECTED_CYCLE
inference pivot            EXTERNAL
pivot equals unit                 no
post-unit position                 1
components                     2 -> 1
```

The binary immediate-reason profile is finite evidence, not an assumption of
the total-collapse proof.

## T2b — remaining branch handoff theorem

Only the branch transition remains:

> Every raw same-cut transient which survives into `P` must be removed, become
> structurally safe, or reach a terminal child before exact-key admission.

A branch assignment may intentionally join components while more than two
remain, so the post-unit total-collapse argument does not apply.  Abstract
cycle-shield-collapse counterexamples exist.

The GT_4 transient proves that T2b must handle:

```text
mixed HEAD_SINGLETON / TAIL_SINGLETON roles;
terminal-before-key admission;
child pre-unit removal;
more than one extinction route.
```

Candidate mechanisms are:

```text
lexicographic singleton-tail handoff;
canonical root N_a shield;
frozen fresh-side provenance;
branch restriction and child pre-unit closure;
terminal-before-key admission.
```

## Remaining induction

```text
T0 root same-cut absence                 available
T1 frozen fresh-side barrier             PROVED
T2a post-unit total-collapse barrier     PROVED
T2b branch handoff extinction            OPEN
T3 exact-key temporal induction          pending T2b
```

If T2b is proved, T0–T2 preserve same-cut absence in every reached exact key.
The unsafe-route classification would then close the complete local Resolution
obstruction for exact Policy-0A on graph tautologies.

The global cache lower bound would still remain separate: the historical
`2^(n-2)` novelty frontier must be transferred to the exact cache DAG while
charging local proof events, terminals, and cache reuse.

## Principal artifacts

```text
proof_attempts/C024/GT_FROZEN_FRESH_SIDE_BARRIER.md
proof_attempts/C024/GT_POST_UNIT_CYCLE_SHIELD_ROUTE_CLASSIFICATION.md
proof_attempts/C024/GT_POST_UNIT_TOTAL_COMPONENT_COLLAPSE_BARRIER.md
experiments/direct/janus_tear_gt_same_cut_transient_elimination.py
experiments/direct/janus_tear_gt_total_component_collapse_reason_profile.py
experiments/direct/janus_tear_gt_post_unit_cycle_shield_collapse.py
experiments/direct/janus_tear_gt_double_bridge_transition_birth.py
```

## Claim boundary

T1 and T2a are proved for arbitrary `n` under the stated exact-key induction
hypothesis and frozen-pass semantics.  T2b, the completed local induction, the
global cache-DAG lower bound, unrestricted SAT lower bounds, and `P` versus
`NP` remain open.
