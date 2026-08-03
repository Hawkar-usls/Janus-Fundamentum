# C024 — GT Temporal Double-Bridge Safety

## Status

```text
RAW_SAME_CUT_NONCREATION = FALSIFIED
POST_UNIT_553_BIRTH_INTERPRETATION = FALSIFIED
FINITE_RAW_SAME_CUT_TRANSIENTS = TWO_CLASSIFIED
FINITE_POST_UNIT_PAIR_CREATION = ABSENT
FINITE_POST_UNIT_CONFLICT_EXTINCTION = CERTIFIED
FINITE_BRANCH_HANDOFF_EXTINCTION = CERTIFIED
FINITE_EXACT_KEY_SAME_CUT = ABSENT_THROUGH_GT_8
ARBITRARY_N_FROZEN_ELIGIBILITY_EXCLUSION = OPEN
GLOBAL_CACHE_LOWER_BOUND = OPEN
P_VS_NP = OPEN
```

This note records the exact temporal boundary observed in Policy-0A after two
overstrong stage interpretations were mechanically falsified.

## Four distinct clause stages

For a reached state, write

```text
K  = exact entry key after pre-unit closure
R  = output of the frozen one-pass local-Resolution phase
P  = residual after post-unit closure
K' = a reached child exact key after branch restriction and child pre-units
```

These stages must not be conflated.  A clause freshly added to `R` is not a
parent in the frozen pass which created it.  It can become Resolution-eligible
only if it survives into a later exact key `K'`.

## Exact finite census through GT_8

### Frozen exact keys K

```text
complementary double-bridge occurrences      611
root occurrences                              80
non-root occurrences                         531
same-cut occurrences                           0
different-cut occurrences                    611
tail/tail occurrences                        611
```

Every one of the 531 non-root exact-key occurrences has a unique complementary
double-bridge source pair in the immediately preceding parent `P`.  Branch
restriction plus child pre-unit closure creates no new exact-key pair in the
finite trace.

### Raw frozen-pass output R

```text
raw double-bridge occurrences               1391
already inherited from K                     611
requiring one fresh local resolvent           611
requiring two fresh local resolvents          169
raw different-cut occurrences               1389
raw same-cut occurrences                       2
raw tail/tail occurrences                    1352
raw non-tail occurrences                       39
```

Local Resolution can therefore create raw complementary double bridges,
including raw same-cut pairs.  Raw noncreation is false.

### Post-unit residual P

```text
post-result double-bridge occurrences        1390
post-result different-cut occurrences        1389
post-result same-cut occurrences                1
pairs created by post-units                      0
raw pairs extinguished before P                  1
```

The exact finite stage map is:

```text
K:   611 pairs / 0 same-cut
R:  1391 pairs / 2 same-cut transients
P:  1390 pairs / 1 same-cut survivor
K':             / 0 same-cut eligible pairs
```

## Raw same-cut transient A — GT_4 branch extinction

```text
n          = 4
state_id   = 1
call_id    = 1
novelty    = 1
pivot      = 5
left       = (5, 6)       [ENTRY_KEY]
right      = (-2, -5)     [LOCAL_RESOLVENT]
roles      = HEAD_SINGLETON / TAIL_SINGLETON
cut        = same
resolvent  = (-2, 6)      [legal, non-tautological]
```

The fresh clause `(-2,-5)` is created by resolving on a different inference
pivot.  Its frozen parents have classes

```text
COMPONENT_SPANNING + DIRECTED_CYCLE.
```

The pair survives into `P`, where no post-unit assignment is made.  Its two
reached transitions extinguish it by distinct routes:

```text
branch -4:
  child pre-unit 6=false
  residuals (5) and (-2,-5) both remain
  child is terminal before an exact key is admitted

branch +4:
  child pre-unit 5=false
  the fresh right clause is removed
  child is terminal
```

No same-cut pair appears in either next exact-key boundary.

## Raw same-cut transient B — GT_5 post-unit conflict extinction

```text
n          = 5
state_id   = 8
call_id    = 10
novelty    = 3 = n-2
pivot      = 10
left       = (10)         [LOCAL_RESOLVENT]
right      = (-10)        [LOCAL_RESOLVENT]
roles      = BOTH_ENDPOINTS_SINGLETON / BOTH_ENDPOINTS_SINGLETON
cut        = same
resolvent  = ()           [legal empty clause]
terminal   = POST_UNIT_CONTRADICTION
```

Both sides are fresh in the same frozen pass, so neither can be reused as a
parent during that pass.  Their complementary unit conflict closes before `P`.
The state has no post-result and no reached child transition.

## What the witnesses prove and refute

They falsify:

> `K -> R` never creates a raw same-cut double bridge.

They also falsify broad post-unit vacuity on every pair-bearing `R`: transient B
is eliminated there.

They do not falsify frozen parent eligibility:

> No reached pre-frontier exact key contains a co-eligible same-cut
> double-bridge pair.

If `K` contains no same-cut pair, every same-cut pair first appearing in `R` has
at least one fresh side.  Frozen one-pass eligibility therefore prevents its
reuse during the pass which created it.

## Correct post-unit statement

The earlier interpretation of 553 post-unit births was a stage-counting error.
Exact replay gives:

```text
post-unit-created double-bridge pairs                     0
raw pair occurrences extinguished before P                1
surviving pair-stage states with nonempty post-unit batch  0
surviving pair-stage states with R != P                    0
```

Post-units create no double-bridge pair on the finite frontier.  They perform
one useful extinction: the GT_5 complementary-unit transient.  Every pair-
bearing state with a surviving `P` has an empty post-unit batch and `R=P`.

This is a finite result only.

## Transition reflection

The finite `P -> K'` replay gives:

```text
non-root exact-key pairs                          531
inherited from parent P                           531
created by branch or child pre-units                0
```

Transient A is extinguished on both reached transitions by the two mechanisms
listed above.  Transient B never reaches `P`.  Neither becomes a frozen
same-cut parent pair.

## Correct local theorem target

### GT Frozen Same-Cut Eligibility Exclusion

For every pre-frontier reachable Policy-0A state on `GT_n`:

> no exact entry key contains two component-spanning clauses with
> complementary pivot bridges inducing the same quotient cut.

Equivalently, every raw same-cut pair created in `R` must be extinguished or
structurally separated before its sides can become co-eligible frozen parents
in a later exact key.

A proof may be decomposed into the following obligations.

### T0 — Root base

The root exact key contains no complementary same-cut double-bridge pair.  The
canonical `N_a` shield is available at this stage.

### T1 — Frozen-pass temporal barrier

Assume same-cut absence in `K`.  If a same-cut pair first appears in `R`, at
least one side is fresh and cannot be selected as a parent during the pass which
created it.

This is definitional once the frozen parent set and the induction hypothesis on
`K` are fixed.

### T2a — Post-unit extinction/noncreation

Post-unit closure cannot turn an `R` configuration into a new surviving
same-cut pair in `P`.  Complementary-unit transients close immediately.

Finite evidence: zero created pairs and one GT_5 terminal extinction through
`GT_8`.

### T2b — Branch handoff extinction

Every same-cut transient surviving into `P` is removed, reaches a terminal
child before exact-key admission, or ceases to be a same-cut complementary
double bridge under every reached transition to `K'`.

The GT_4 witness proves that this obligation must handle mixed
`HEAD_SINGLETON/TAIL_SINGLETON` transients and at least two extinction routes.
A raw tail/tail-only theorem is false.

Candidate supporting mechanisms are:

```text
lexicographic singleton-tail handoff
canonical root N_a shield
frozen one-pass parent eligibility
branch restriction and child pre-unit closure
terminal-before-key admission
```

### T3 — Induction

Assuming same-cut absence in `K`, T1, T2a, and T2b imply same-cut absence in
every reached child exact key `K'`.  Combined with T0, this yields arbitrary-`n`
frozen same-cut eligibility exclusion.

## Consequence if T0–T3 are proved

The quotient-graph classification proves that an unsafe acyclic low-rank
resolvent can arise only from a spanning/spanning same-cut double-bridge parent
pair.  Frozen same-cut eligibility exclusion would therefore close the local
Resolution obstruction for exact Policy-0A on graph tautologies.

It would not prove the global cache lower bound.  The separate global gate must
still transfer the historical `2^(n-2)` novelty frontier into the exact
Policy-0A cache DAG while charging local proof work, terminal events, and cache
reuse.  It would not resolve unrestricted SAT, unrestricted clause learning,
or `P` versus `NP`.

## Mechanical witnesses

```text
experiments/direct/janus_tear_gt_double_bridge_local_creation_v2.py
experiments/direct/janus_tear_gt_resolution_output_double_bridge_creation.py
experiments/direct/janus_tear_gt_post_unit_double_bridge_creation.py
experiments/direct/janus_tear_gt_double_bridge_transition_birth.py
experiments/direct/janus_tear_gt_same_cut_transient_elimination.py
```

The raw-output census separates exact-key parents from fresh clauses.  The
post-unit regression proves finite noncreation and terminal conflict extinction.
The transition audit proves finite reflection.  The transient replay follows
both raw same-cut witnesses through their complete temporal lifetimes.
