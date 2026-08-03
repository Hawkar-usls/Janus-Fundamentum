# C024 — GT Temporal Double-Bridge Safety

## Status

```text
RAW_SAME_CUT_NONCREATION = FALSIFIED
POST_UNIT_553_BIRTH_INTERPRETATION = FALSIFIED
FINITE_RAW_SAME_CUT_TRANSIENT = FOUND
FINITE_POST_UNIT_PAIR_STAGE = VACUOUS
FINITE_NEXT_KEY_REFLECTION = CERTIFIED
ARBITRARY_N_FROZEN_ELIGIBILITY_EXCLUSION = OPEN
GLOBAL_CACHE_LOWER_BOUND = OPEN
P_VS_NP = OPEN
```

This note replaces an overstrong stage interpretation with the exact temporal
boundary observed in Policy-0A.

## Four distinct clause stages

For a reached state, write

```text
K  = exact entry key after pre-unit closure
R  = output of the frozen one-pass local-Resolution phase
P  = residual after post-unit closure
K' = a reached child exact key after branch restriction and child pre-units
```

These stages must not be conflated.

A clause freshly added to `R` is not a parent in the frozen pass which created
it.  It can become Resolution-eligible only if it survives into a later exact
key `K'`.

## Exact finite census through GT_8

The pre-frontier exact-key census remains:

```text
exact-key complementary double-bridge occurrences   611
root occurrences                                      80
non-root occurrences                                 531
same-cut exact-key occurrences                         0
different-cut exact-key occurrences                  611
tail/tail exact-key occurrences                      611
```

Every one of the 531 non-root exact-key occurrences has a unique
complementary double-bridge source pair in the immediately preceding parent
`P`.  Branch restriction plus child pre-unit closure creates no new exact-key
pair in the finite trace.

The raw `R=P` census is larger:

```text
raw double-bridge occurrences                       1390
already inherited from K                             611
requiring one fresh local resolvent                   610
requiring two fresh local resolvents                  169
raw different-cut occurrences                       1389
raw same-cut occurrences                               1
raw tail/tail occurrences                            1351
raw non-tail occurrences                               39
```

Thus local Resolution can create raw complementary double bridges, including a
raw same-cut pair.  The correct invariant is not raw non-creation.

## The GT_4 raw same-cut witness

The unique finite raw same-cut occurrence is reached at:

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

Therefore the pure quotient-graph unsafe-route classification is not violated:
the same-cut pair exists only after the pass has frozen its parent set.  The
fresh side cannot be reused during that same pass.

This witness falsifies:

> `K -> R` never creates a raw same-cut double bridge.

It does not falsify the exact parent-eligibility statement:

> No reached pre-frontier exact key contains a co-eligible same-cut
> double-bridge pair.

## Post-unit correction

An earlier draft interpreted extra raw `P` pairs as 553 pairs born under
post-unit contraction.  Exact replay rejects that interpretation.

For every finite state whose `R` or `P` contains a double-bridge pair:

```text
post-unit assignments                    0
R-to-P formula changes                   0
P-pairs without an R double-bridge source 0
```

Hence, on the observed pair-bearing frontier,

```text
R = P.
```

The extra raw pairs are created by frozen local Resolution, not by post-unit
propagation.  This is a finite vacuity result only.  It does not prove that
post-units are absent for arbitrary `n` or in pair-free states.

## Transition reflection

The finite `P -> K'` replay gives:

```text
non-root exact-key pairs                          531
inherited from parent P                           531
created by branch or child pre-units                0
```

The unique raw same-cut transient does not reappear as a same-cut pair in any
reached child exact key.  The dedicated replay records the exact branch-level
elimination cause.

## Correct local theorem target

The remaining arbitrary-`n` statement is temporal.

### GT Frozen Same-Cut Eligibility Exclusion

For every pre-frontier reachable Policy-0A state on `GT_n`:

> no exact entry key contains two component-spanning clauses with
> complementary pivot bridges inducing the same quotient cut.

Equivalently, every raw same-cut pair created in `R` must be extinguished or
structurally separated before either side can become a co-eligible frozen
parent pair in a later exact key.

A proof may be decomposed into the following obligations.

### T0 — Root base

The root exact key contains no complementary same-cut double-bridge pair.

The canonical `N_a` shield is available at this stage.

### T1 — Frozen-pass temporal barrier

If a same-cut pair first appears in `R`, at least one side is fresh and cannot
be selected as a parent during the pass which created it.

This follows definitionally from one-pass frozen eligibility once same-cut
absence in `K` is assumed.

### T2 — Handoff extinction

Every raw same-cut transient in `P` is removed or ceases to be a same-cut
complementary double bridge under every reached transition to `K'`.

This is the substantive open preservation lemma.  Candidate mechanisms are:

```text
lexicographic singleton-tail handoff
canonical root N_a shield
branch restriction on the transient endpoint structure
child pre-unit closure
```

The GT_4 witness shows that T2 must handle mixed
`HEAD_SINGLETON/TAIL_SINGLETON` transients; a tail/tail-only theorem is too
strong at the raw-output layer.

### T3 — Induction

Assuming same-cut absence in `K`, T1 and T2 imply same-cut absence in every
reached child exact key `K'`.

Combined with T0, this yields arbitrary-`n` frozen same-cut eligibility
exclusion.

## Consequence if T0–T3 are proved

The pure quotient-graph classification already proves that an unsafe acyclic
low-rank resolvent can arise only from a spanning/spanning same-cut
double-bridge parent pair.

Therefore frozen same-cut eligibility exclusion would close the local
Resolution obstruction for exact Policy-0A on graph tautologies.

It would not yet prove the global cache lower bound.  The separate global gate
must still transfer the historical `2^(n-2)` novelty frontier into the exact
Policy-0A cache DAG while charging all local proof work, terminal events, and
cache reuse.

It would not resolve unrestricted SAT, unrestricted clause learning, or
`P` versus `NP`.

## Mechanical witnesses

```text
experiments/direct/janus_tear_gt_double_bridge_local_creation_v2.py
experiments/direct/janus_tear_gt_resolution_output_double_bridge_creation.py
experiments/direct/janus_tear_gt_post_unit_double_bridge_creation.py
experiments/direct/janus_tear_gt_double_bridge_transition_birth.py
experiments/direct/janus_tear_gt_same_cut_transient_elimination.py
```

The first two separate exact-key parents from raw fresh clauses.  The third is
a post-unit vacuity regression.  The fourth proves finite transition
reflection.  The fifth follows every raw same-cut transient through the next
exact-key boundary.
