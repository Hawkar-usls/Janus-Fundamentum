# C024 — Post-Unit Same-Cut Birth Dichotomy

## Status

```text
PURE_POST_UNIT_SAME_CUT_NONCREATION = FALSIFIED
THREE_VERTEX_BIRTH_CENSUS = COMPLETE
THREE_VERTEX_SAFE_SOURCE_BIRTH = ABSENT
THREE_VERTEX_NONUNIT_BIRTH = ABSENT
ARBITRARY_N_SAFE_SOURCE_EXCLUSION = OPEN
GT_REACHABLE_T2A = OPEN
P_VS_NP = OPEN
```

## Purpose

The exact GT traces through `GT_8` contain no double-bridge pair created by the
post-unit phase.  That finite fact could have had two explanations:

1. a pure quotient-graph theorem saying that restriction/contraction never
   creates a same-cut double bridge; or
2. a stronger invariant carried by the clauses and reasons reachable in GT.

The first explanation is false.  A one-assignment exhaustive search on the
smallest nontrivial quotient finds same-cut births.  Their form is nevertheless
highly constrained.

## Search space

On three quotient vertices there are three comparison variables and

```text
3^3 - 1 = 26
```

nonempty non-tautological clauses when each variable is absent, positive, or
negative.

The checker exhausts:

```text
every one-comparison assignment;
every surviving ordered clause pair;
every complementary pivot not fixed by the assignment.
```

A birth is counted when the residual clauses form a same-cut complementary
double-bridge pair after the assignment, but their source clauses did not form
such a pair before it.

No GT reachability, frozen-pass provenance, or unit-reason restriction is
imposed.

## Complete three-vertex result

```text
same-cut birth occurrences                    36
opposite-unit conflict births                 36
non-unit births                                0
births with two branch-safe sources             0
births with at least one unsafe source         36
```

Source-class pairs are exactly:

```text
COMPONENT_SPANNING + UNSAFE_ACYCLIC_LOW_RANK   24
UNSAFE_ACYCLIC_LOW_RANK + UNSAFE_ACYCLIC_LOW_RANK 12
```

Every residual pair has widths

```text
(1,1)
```

and roles

```text
BOTH_ENDPOINTS_SINGLETON / BOTH_ENDPOINTS_SINGLETON.
```

Each residual is therefore the immediate contradictory pair

```text
(p), (-p).
```

The six orientations of the assigned comparison each produce six birth
occurrences.

## What is falsified

The following pure statement is false:

> Restriction and quotient contraction cannot create a same-cut
> double-bridge pair.

Even the three-vertex quotient creates 36 such births.

## What survives

The minimum abstract births satisfy two simultaneous properties:

1. at least one source clause is already
   `UNSAFE_ACYCLIC_LOW_RANK` before the assignment;
2. the born pair is an immediate complementary-unit conflict and cannot survive
   unit closure.

This motivates a sharper candidate.

## Candidate T2a theorem

### Safe-Source Post-Unit Birth Exclusion

Let every source clause acted on by a post-unit assignment lie in the
branch-safe dichotomy

```text
DIRECTED_CYCLE
OR COMPONENT_SPANNING
OR INTERNAL_ONLY.
```

Then post-unit restriction/contraction cannot create a surviving same-cut
complementary double-bridge pair.

A stronger possible dichotomy is:

> Every same-cut birth either uses an unsafe source clause or is an immediate
> complementary-unit contradiction.

Neither statement is proved for arbitrary quotient size.

## Relation to the GT trace

The exact GT pre-frontier trace already certifies:

```text
post-unit-created double-bridge pairs  0
```

and the only raw pair destroyed before `P` is the GT_5 fresh/fresh pair

```text
(10), (-10),
```

which closes as `POST_UNIT_CONTRADICTION`.

The abstract census explains why a proof of T2a cannot rely on contraction
alone.  It must use at least one of:

```text
source safety;
GT reachability;
unit-reason provenance;
frozen fresh-side provenance;
immediate contradiction closure.
```

## Next falsification gate

Repeat the optimized birth census on four quotient vertices.

The decisive outcomes are:

```text
BOTH_SAFE_NONUNIT_BIRTH:
  falsifies the safe-source candidate;

NONUNIT_BIRTH_WITH_UNSAFE_SOURCE:
  preserves safe-source exclusion but falsifies the stronger universal
  immediate-conflict pattern;

ONLY_UNSAFE_SOURCE_OPPOSITE_UNITS:
  supports both candidate refinements but does not prove them.
```

## Mechanical artifact

```text
experiments/direct/janus_tear_abstract_post_unit_same_cut_birth.py
.github/workflows/validate-c024-abstract-post-unit-same-cut-birth.yml
```

## Claim boundary

This is an exhaustive theorem only for one assigned comparison on a
three-vertex abstract quotient.  It is not an arbitrary-`n` theorem and is not a
GT reachability theorem.  T2a, the complete local induction, the global cache
lower bound, and `P` versus `NP` remain open.
