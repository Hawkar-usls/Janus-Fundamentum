# C024 — Post-Unit Same-Cut Birth Dichotomy

## Status

```text
PURE_POST_UNIT_SAME_CUT_NONCREATION = FALSIFIED
UNIVERSAL_IMMEDIATE_UNIT_CONFLICT_PATTERN = FALSIFIED
SAFE_SOURCE_BIRTH_EXCLUSION = FALSIFIED
ONE_STEP_SINGLETON_QUOTIENT_CENSUS = COMPLETE_THROUGH_N4
TWO_STEP_COMPOUND_COMPONENT_CENSUS = COMPLETE_AT_N4
SPANNING_SPANNING_BIRTH = ABSENT_IN_ALL_CENSUSES
CYCLE_SHIELD_COLLAPSE_ROUTE = ISOLATED
ARBITRARY_N_CYCLE_SHIELD_ROUTE_CLASSIFICATION = FORMALIZING
GT_REACHABLE_CYCLE_SHIELD_EXCLUSION = OPEN
P_VS_NP = OPEN
```

## Purpose

The exact GT traces through `GT_8` contain no double-bridge pair created by the
post-unit phase.  Successive abstract gates were used to determine how much of
that fact follows from quotient geometry alone.

Three increasingly strong pure statements have now been falsified:

1. contraction never creates a same-cut double bridge;
2. every abstract birth is an immediate complementary-unit conflict;
3. two branch-safe source clauses cannot create a same-cut pair.

The surviving structural boundary is narrower:

> every observed birth from two branch-safe sources uses at least one
> `DIRECTED_CYCLE` source whose cycle shield collapses under the contraction.

No `COMPONENT_SPANNING + COMPONENT_SPANNING` birth has been found.

## Gate A — one assignment on three singleton components

The complete clause universe has

```text
3^3 - 1 = 26
```

clauses.  The exhaustive result is:

```text
same-cut births                              36
opposite-unit conflicts                      36
non-unit births                               0
births with two branch-safe sources           0
births with an unsafe source                 36
```

Source classes:

```text
COMPONENT_SPANNING + UNSAFE_ACYCLIC_LOW_RANK  24
UNSAFE + UNSAFE                               12
```

Every residual pair is `(p),(-p)`.

This falsifies pure post-unit noncreation but initially leaves both the
immediate-conflict and safe-source candidates alive.

## Gate B — one assignment on four singleton components

The complete clause universe has

```text
3^6 - 1 = 728
```

clauses.  The optimized exhaustive result is:

```text
same-cut births                         6,336
opposite-unit conflicts                     0
non-unit births                          6,336
births with two branch-safe sources          0
births with an unsafe source              6,336
```

Source classes:

```text
COMPONENT_SPANNING + UNSAFE_ACYCLIC_LOW_RANK  4,608
UNSAFE + UNSAFE                               1,728
```

Residual widths are:

```text
(1,2)  3,456
(2,2)  2,880
```

This falsifies the universal immediate-conflict pattern.  Safe-source exclusion
still appears true when the pre-assignment quotient consists only of singleton
components.

## Gate C — two assignments on four original vertices

The first assignment creates a compound component, giving the pre-step shape

```text
(1,1,2).
```

The second gate exhausts all 120 acyclic assignments joining two distinct
current components.  The post shapes are

```text
(1,3)  96 transitions
(2,2)  24 transitions.
```

The complete result is:

```text
same-cut births                         6,048
opposite-unit conflicts                 1,152
non-unit births                          4,896
births with two branch-safe sources      2,592
both-safe non-unit births                2,592
births with an unsafe source             3,456
```

Source-class pairs:

```text
COMPONENT_SPANNING + DIRECTED_CYCLE       2,304
DIRECTED_CYCLE + DIRECTED_CYCLE             288
COMPONENT_SPANNING + UNSAFE               2,496
DIRECTED_CYCLE + UNSAFE                     576
UNSAFE + UNSAFE                             384
```

Thus every one of the 2,592 both-safe births contains a directed-cycle source.
There are no observed

```text
COMPONENT_SPANNING + COMPONENT_SPANNING
```

births.

## Minimum both-safe witness

Use the standard `GT_4` comparison numbering

```text
1=(0,1), 2=(0,2), 3=(0,3),
4=(1,2), 5=(1,3), 6=(2,3).
```

Take the pre-assignment

```text
x_03 = false,
```

so the current components are

```text
{0,3}, {1}, {2}.
```

The two source clauses are

```text
C = (-5, 6)
D = (-1, -5, -6).
```

Their pre-step classes are

```text
C = COMPONENT_SPANNING
D = DIRECTED_CYCLE.
```

Now assign

```text
x_13 = true.
```

The components become

```text
{0,1,3}, {2}.
```

The false literal `-5` is deleted, and the residuals are

```text
C' = (6)
D' = (-1, -6).
```

Literal `-1` is internal in the merged component.  Externally the residuals are
the complementary bridge pair `6,-6` with the same two-component cut.  The
protecting directed two-cycle of `D` has collapsed under the contraction.

This is a non-unit same-cut birth from two branch-safe sources.  It falsifies
Safe-Source Post-Unit Birth Exclusion.

## Surviving pure graph route

The censuses support the following sharper classification.

### Cycle-Shield Collapse Route

If a same-cut pair is born under a quotient contraction and both source clauses
are branch-safe, then at least one source must be `DIRECTED_CYCLE`, and every
directed-cycle protection responsible for its safe classification must fail to
survive the contraction.

The spanning/spanning subcase is expected to be impossible for a pure graph
reason:

1. contraction preserves connectedness;
2. a residual pivot bridge reflects to a source pivot bridge;
3. the contracted components must lie on the same side of that source bridge
   cut, otherwise identification reconnects the deletion graph;
4. equal residual cuts then lift uniquely to equal source cuts.

Therefore two component-spanning sources cannot create a new same-cut pair;
they can only transmit one already present.

`INTERNAL_ONLY` sources cannot produce a component-spanning residual because
contraction creates no new external edge.

The only remaining branch-safe source class is `DIRECTED_CYCLE`.  A birth can
occur only when the cycle shield is internalized or broken by deletion of the
falsified unit literal.

The arbitrary-quotient proof of this route classification is being separated
from the finite census.  It does not itself exclude the route in GT.

## Relation to exact GT traces

The exact pre-frontier trace through `GT_8` gives:

```text
post-unit-created double-bridge pairs  0
```

The only raw pair destroyed before `P` is the fresh/fresh GT_5 conflict

```text
(10), (-10),
```

which closes as `POST_UNIT_CONTRADICTION`.

The abstract witnesses prove that these finite GT facts cannot be derived from
contraction, source safety, or immediate-conflict closure alone.  An
arbitrary-`n` proof of T2a must exclude reachable cycle-shield collapse using
GT-specific information such as:

```text
unit-reason provenance;
transitive-cycle ancestry;
frozen fresh-side provenance;
lexicographic branch order;
terminal-before-key admission.
```

## Revised T2a target

### GT Post-Unit Cycle-Shield Exclusion

For every reachable pre-frontier post-unit step:

> no directed-cycle clause participating in a potential same-cut birth can
> lose its last protecting directed cycle while the complementary residual
> bridge pair survives into `P`.

Together with the pure spanning/spanning reflection theorem, this would prove
post-unit same-cut noncreation on reachable GT states.

## Mechanical artifacts

```text
experiments/direct/janus_tear_abstract_post_unit_same_cut_birth.py
experiments/direct/janus_tear_abstract_post_unit_same_cut_birth_n4.py
experiments/direct/janus_tear_abstract_post_unit_same_cut_birth_two_step_n4.py
.github/workflows/validate-c024-abstract-post-unit-same-cut-birth.yml
.github/workflows/validate-c024-abstract-post-unit-same-cut-birth-n4.yml
.github/workflows/validate-c024-abstract-post-unit-same-cut-birth-two-step-n4.yml
```

## Claim boundary

The listed counts are exhaustive for their stated finite abstract spaces.  The
cycle-shield route classification and its GT exclusion are separate arbitrary-
`n` obligations.  T2a, T2b, the complete temporal induction, the global cache
lower bound, and `P` versus `NP` remain open.
