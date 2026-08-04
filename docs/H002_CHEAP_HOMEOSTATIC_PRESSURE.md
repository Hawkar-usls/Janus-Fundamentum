# H002 — cheap homeostatic pressure without branch probes

## Purpose

H001 showed that entropy-guided delayed collapse reduced the exact DPLL search tree, but its recursive branch probes more than doubled charged work. H002 tests the narrow surviving hypothesis:

```text
the useful ordering signal may live in unresolved-clause pressure itself
and may not require speculative child execution
```

H002 remains a search-order experiment. It does not prune either Boolean child and does not alter the exact SAT/UNSAT acceptance conditions.

## Cheap pressure estimator

For a partial assignment, every unresolved clause `C` with `r(C)` remaining literals contributes weight

```text
w(C) = 1 / r(C).
```

For each unassigned variable `v`, H002 accumulates:

```text
P+(v) = sum w(C) over positive residual occurrences of v
P-(v) = sum w(C) over negative residual occurrences of v
q(v)  = P+(v) / (P+(v) + P-(v))
H(v)  = -q log2(q) - (1-q) log2(1-q)
```

The deterministic variable score is:

```text
1.20 * polarity_entropy
+ 0.90 * normalized_total_pressure
+ 0.40 * normalized_conflict_activity
+ 0.25 * normalized_tight_clause_occurrence
+ 0.15 * polarity_contrast
```

All quantities are computed in one charged pass over unresolved clauses. H002 performs no recursive branch probes.

The frontier-state scheduler remains the H001 delayed-collapse scheduler: it combines normalized unresolved pressure, diversity from the other live hypotheses, and depth. Both children of every expanded node remain in the exact frontier unless deterministic unit propagation closes them.

## Proof-carrying package

The producer freezes every node, propagation reason, conflict reason, frontier transition, state score, cheap polarity-pressure vector, selected variable, both children, cumulative work counter, SAT witness, and complete UNSAT tree.

The producer reuses the already frozen H001 DPLL state engine. The H002 verifier does not import the H002 producer; it reuses the independently authored H001 verifier primitives for propagation and node semantics, then independently reconstructs the new cheap-pressure scheduler and all H002 receipts.

The independent verifier imports neither producer nor its functions. It recomputes:

```text
canonical unit propagation
residual clause profiles
frontier diversity and selection
P+(v), P-(v), q(v), H(v)
all score normalizations
conflict activity
binary branch coverage
cumulative operation accounting
SAT witnesses and UNSAT exhaustion
```

Digest-repaired controls alter a witness, selected scheduler node, propagated child assignment, and charged work total. All are rejected.

## Benchmark protocol

The score weights were fixed on the calibration suite before the holdout ranges were executed.

```text
CALIBRATION  20 planted 3-SAT instances, n=14, m=60, seeds 1..20
HOLDOUT_A   100 planted 3-SAT instances, n=14, m=60, seeds 101..200
HOLDOUT_B    50 planted 3-SAT instances, n=16, m=68, seeds 201..250
STRUCTURAL    3 UNSAT controls: pigeonhole 4->3, pigeonhole 5->4,
              and a 20-variable unit contradiction chain
```

Every one of the 173 paired runs closed with the same exact SAT/UNSAT result in baseline and H002 modes.

## Frozen result

Overall:

```text
baseline nodes     3,263
H002 nodes         1,825
node change       -1,438  (-44.07%)

baseline work      2,806,816
H002 work          1,907,668
work change         -899,148  (-32.03%)
```

Per suite:

```text
CALIBRATION  nodes -30.72%   work -15.72%
HOLDOUT_A    nodes -45.57%   work -33.15%
HOLDOUT_B    nodes -48.44%   work -37.51%
STRUCTURAL   nodes  +6.78%   work +16.15%
```

Frozen integrity:

```text
artifact bytes             5,995,059
artifact semantic digest   840c4a0cb327002f733b21bdcc6cbff4ac178ecd7e23d902c0815cab9d004afe
artifact SHA-256           d15d8e5ca4d137403ab6aff2f3647b65ce7fa7bb07c1f76b48ea3ad893bd28df
producer SHA-256           5174e4d3a707c7edf8181a172df03e8664bccffcdcc4c80fe9c5310501bc1d4e
verifier SHA-256           c2292baa42470898204e7a0ae2525a9d2017d5020f32c8d5ec9af855a39da108
```

## Interpretation

H002 passes its empirical gate on two untouched planted-SAT holdouts: the delayed-collapse ordering signal survives without child probes and reduces both the search tree and the fully charged operation total.

The structural UNSAT controls worsen. Therefore H002 is not a universal dominance theorem and cannot be promoted into a worst-case complexity result. It is a candidate portfolio component whose activation must itself be certified or safely compared against another exact schedule.

The most relevant next experiment is no longer generic SAT tuning. It is direct transfer to the active constructor:

```text
H003_B4_6_2_ROOT_TRAJECTORY_PRESSURE_ABLATION
```

There, residual-clause pressure must be replaced by proof-state pressure defined over competing B4.6.2 ancestry/refinement obligations. The exact full-set semantics, every failed refinement, and all certificate volume must remain unchanged.

## Strict boundary

```text
H002_EXACTNESS                     = VERIFIED_CANDIDATE
H002_HOLDOUT_TREE_REDUCTION        = OBSERVED
H002_HOLDOUT_TOTAL_WORK_REDUCTION  = OBSERVED
H002_STRUCTURAL_DOMINANCE          = FALSE
H002_POLYNOMIAL_WORST_CASE         = NOT_PROVED
C049_1_TERMINAL                    = UNCHANGED
P_VS_NP                            = OPEN
```

Draft only. No automatic merge.
