# C024 — GT Post-Unit Total-Component Collapse Barrier

## Status

```text
THEOREM = PROVED
SCOPE = ARBITRARY_N_CONDITIONAL_ON_EXACT_KEY_LOCAL_INVARIANT
T2A_POST_UNIT_EXTINCTION_NONCREATION = PROVED
FIRST_COMPONENT_MERGING_POST_UNIT = TOTAL_COMPONENT_COLLAPSE
SURVIVING_POST_UNIT_SAME_CUT_BIRTH = IMPOSSIBLE
T2B_BRANCH_HANDOFF = OPEN
GLOBAL_CACHE_LOWER_BOUND = OPEN
P_VS_NP = OPEN
```

## Purpose

The pure quotient analysis proves that a same-cut double-bridge pair can be
born under contraction only through collapse of a directed-cycle shield; two
component-spanning sources cannot create a new same-cut pair.

Abstract two-step examples show that cycle-shield collapse is real.  Exact GT
traces nevertheless show no post-unit same-cut birth.  The reason is stronger
than a special ancestry pattern:

> before the first component-merging post-unit, all earlier units are internal
> to the current quotient and cannot change any surviving clause's external
> graph; therefore an external unit can arise from a branch-safe clause only
> when exactly two quotient components remain.

The first component-merging unit consequently collapses the entire quotient to
one component, where no external bridge cut exists.

## Assumptions at one exact state

Let

```text
K = exact entry key after pre-unit closure
R = output of the frozen one-pass local-Resolution phase
```

Assume the inductive local invariant on `K`:

1. every clause of `K` is branch-safe, meaning its quotient external graph is
   `DIRECTED_CYCLE`, `COMPONENT_SPANNING`, or `INTERNAL_ONLY`;
2. `K` contains no co-eligible same-cut complementary double-bridge pair;
3. the frozen pass uses parents only from `K`.

The proved unsafe-route classification says that an unsafe acyclic low-rank
fresh resolvent can arise from branch-safe parents only through a same-cut
spanning/spanning double-bridge pair.  Assumption 2 excludes that route.

Therefore every clause in

```text
R = K union F
```

is branch-safe.

## Lemma 1 — internal unit assignments preserve external graphs

Call a propagated comparison unit internal when its two original endpoints
already lie in one current relation component.

Assigning such a unit does not merge quotient components.  For any clause which
survives the assignment:

- a satisfied internal literal removes the whole clause, so that clause cannot
  be a later unit reason;
- a falsified internal literal is deleted, but it was not an external quotient
  edge;
- every external literal, its orientation, and its quotient endpoints remain
  unchanged.

Hence the external directed multigraph of every surviving clause is unchanged
by an internal unit assignment.  In particular:

```text
directed-cycle protection persists;
component-spanning connectedness persists;
internal-only remains internal-only;
bridge cuts among external edges are unchanged.
```

The same conclusion holds for any sequence of internal unit assignments.

## Lemma 2 — a branch-safe external unit requires two components

Consider a surviving clause whose current residual is the unit `(l)`, and
suppose `l` joins two distinct current relation components.

Its external graph consists of exactly one edge.

It cannot be `INTERNAL_ONLY`, because `l` is external.  It cannot contain a
directed cycle.  Thus branch safety requires it to be
`COMPONENT_SPANNING`.

A one-edge graph spans the quotient if and only if the quotient has exactly two
vertices.  Therefore:

```text
external branch-safe unit
implies current relation-component count = 2.
```

## Theorem — Total-Component Collapse Barrier

Process the post-unit closure of `R` sequentially.  If no unit merges relation
components, no quotient contraction occurs and post-unit closure cannot create
a new external same-cut pair.

Otherwise let `l` be the first propagated unit which joins two distinct
relation components.

Every earlier propagated unit is internal by minimality of `l`.  By Lemma 1,
the external graph of the clause producing `l` is unchanged from its graph in
`R`.  Since every clause of `R` is branch-safe, the unit source is branch-safe
at the moment `l` is propagated.

Lemma 2 now implies that exactly two relation components remain.  Assigning `l`
merges those final two components into the single total component.

After this assignment:

```text
relation-component count = 1;
all comparison literals are quotient-internal;
no external bridge exists;
no nontrivial quotient cut exists;
no same-cut complementary double-bridge pair exists.
```

Any subsequent unit is internal.  If opposite units or an empty clause are
detected, the state terminates before a surviving post-result is admitted.

Therefore post-unit closure cannot create a same-cut pair which survives into
`P`.  QED.

## Corollary — T2a is closed

Under the exact-key induction hypothesis and the frozen-pass unsafe-route
classification:

```text
T2a_POST_UNIT_EXTINCTION_NONCREATION = PROVED.
```

The post-unit stage has only three possibilities:

```text
1. no component merge:
   external graphs and cuts are transmitted unchanged;

2. first component merge:
   exactly two components remain and the quotient collapses to one;

3. contradiction:
   no surviving P is admitted.
```

None can create a surviving same-cut pair.

## Immediate fresh-unit corollary

The exact key `K` is unit-closed.  If one frozen Resolution inference directly
emits a fresh unit `(l)` by resolving on pivot `p`, its parents must be exactly

```text
(p,l)
and
(-p,l).
```

Indeed the resolvent is the union of both parents after deleting `p,-p`.  For
that union to be the singleton `{l}`, each non-unit parent can contain no other
literal and must contain `l`.

This narrow immediate-unit statement is valid.  It must not be confused with
the previously falsified broad binary-origin reduction for arbitrary conflict
closures and inherited reason ancestry.

## Exact implementation certificate through GT_8

The all-reason provenance replay gives ten component-merging post-units:

```text
n=4: 0
n=5: 4
n=6: 1
n=7: 2
n=8: 3
```

Every event satisfies:

```text
novelty level                         n-2
current relation components             2
post relation components                1
unit position in post batch             1
reason candidates                       1
reason origin             LOCAL_RESOLVENT
reason width                              1
producing Resolution events              1
parent widths                         (2,2)
parent safety       SPANNING + DIRECTED_CYCLE
inference pivot                  EXTERNAL
inference pivot equals unit variable    false
```

The exact root replay retains one non-minimality owner in every unit reason,
with one to three transitivity ancestors depending on the reached lineage.
This ancestry profile is evidence, not an assumption of the theorem.

The independent cycle-shield census gives:

```text
post-unit events                            33
component-merging events                    10
internal/redundant events                   23
total-component collapses                   10
non-total component merges                   0
directed-cycle shield collapses            385
collapsed residuals with an external bridge  0
new same-cut births                          0
```

All 385 cycle-shield collapses occur when the quotient is collapsed to one
component, so their residuals have no external bridge.

## Relation to the novelty frontier

The ten component-merging units occur exactly at novelty level `n-2`; none
occurs before the historical frontier in the finite traces.

The theorem explains the geometric half of this localization: any first
external post-unit can occur only with two relation components remaining.  To
identify that condition with novelty `n-2` globally, the novelty induction must
also preserve the relation-component accounting before post-unit collapse.
That accounting belongs to the global frontier-transfer proof, not to T2a.

## Remaining local obligation

Only branch handoff remains:

```text
T0 root same-cut absence                 available
T1 frozen fresh-side barrier             PROVED
T2a post-unit total-collapse barrier     PROVED
T2b branch/child-preunit handoff          OPEN
T3 temporal exact-key induction          pending T2b
```

A branch assignment is not covered by this theorem: it may deliberately join
components while more than two remain, and abstract cycle-shield-collapse
counterexamples exist.  T2b must use the selected branch order, singleton-tail
handoff, terminal-before-key admission, or a stronger GT reachability invariant.

## Mechanical artifacts

```text
experiments/direct/janus_tear_gt_total_component_collapse_reason_profile.py
experiments/direct/janus_tear_gt_post_unit_cycle_shield_collapse.py
experiments/direct/janus_tear_gt_unit_merge_timing.py
proof_attempts/C024/GT_POST_UNIT_CYCLE_SHIELD_ROUTE_CLASSIFICATION.md
```

## Claim boundary

The theorem closes the post-unit stage conditional on the exact-key local
induction hypothesis and the already proved unsafe-route classification.  It
does not prove branch handoff extinction, the completed local induction, the
global cache-DAG lower bound, or `P` versus `NP`.
