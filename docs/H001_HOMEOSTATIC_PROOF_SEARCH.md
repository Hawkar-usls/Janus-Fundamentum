# H001 — homeostatic proof search with delayed collapse

## Purpose

H001 extracts a testable computational principle from the “goosebumps” dialogue without importing its speculative quantum or consciousness claims.

The operational hypothesis is:

```text
retain competing proof hypotheses
-> measure unresolved pressure and branch entropy
-> spend additional work where alternatives disagree
-> preserve every rejected branch as evidence
-> collapse only through an exact SAT witness or complete UNSAT tree
```

H001 is a side experiment stacked on C049.1 B4.6.1. It does not replace the active fixed-width layout constructor and does not change any C049.1 terminal.

## Exact search core

Both compared solvers use the same proof-carrying DPLL frontier and deterministic unit propagation.

The baseline uses:

```text
lowest frontier node id
lowest unassigned variable
```

The homeostatic scheduler changes only search order:

1. Every open decision creates both Boolean children. Neither child is heuristically deleted.
2. Frontier states receive a pressure/diversity score from unresolved clauses, depth, and distance from the other live hypotheses.
3. Candidate variables receive two charged branch probes.
4. Their residual energies define a binary Gibbs distribution and Shannon entropy.
5. Higher clause pressure permits a larger probe budget.
6. Every conflict clause updates a charged variable-activity map; rejected hypotheses therefore become future search information.
7. SAT is accepted only with a clause-by-clause witness. UNSAT is accepted only when the exact binary frontier is exhausted.

The “energy”, “stress”, and “collapse” terms are algorithmic names for explicit scalar functions and state transitions. They are not claims that the program is conscious or that biological decoherence solves SAT.

## Proof-carrying transcript

For every run the producer records:

```text
complete CNF
all created nodes
input and propagated assignments
unit-clause reasons
conflict-clause reasons
frontier before and after every expansion
all state-priority receipts
all branch-probe receipts
entropy, contrast, pressure, and activity values
both children of every expanded node
cumulative operation ledger
SAT witness or complete UNSAT frontier exhaustion
```

The independent verifier imports neither producer nor its functions. It reconstructs deterministic unit propagation, every node profile, scheduler choice, adaptive probe cap, Gibbs entropy, conflict activity, frontier evolution, binary branch coverage, work accounting, SAT witnesses, and UNSAT trees.

Digest-repaired self-tests alter:

```text
SAT witness
selected scheduler node
propagated child assignment
charged work total
```

All four are rejected.

## Frozen experiment

The deterministic suite contains:

```text
20 planted 3-SAT instances: 14 variables, 60 clauses
pigeonhole 4 -> 3: UNSAT
pigeonhole 5 -> 4: UNSAT
20-variable unit contradiction chain: UNSAT
```

Results:

```text
cases closed                         23 / 23 in both modes
baseline search nodes                391
homeostatic search nodes             301
node change                          -90 (-23.02%)
baseline charged work                327,383
homeostatic charged work             624,299
charged-work change                  +296,916 (+90.69%)
artifact bytes                       645,617
artifact semantic digest             c631f83a220992db54fc9b9be1d46de153a883cd88fd56d0684fba34c1fb104b
artifact file SHA-256                 b8d00288f98f3130f000ecf6a07c2a64a6f4c087a71c7de16723227a483848f7
```

## Interpretation

The hypothesis survives only in a narrow form:

```text
HOMEOSTATIC_ORDERING_REDUCES_SEARCH_TREE_ON_THIS_SUITE
```

It does **not** yet survive as a computational speedup. The extra probes cost more than the saved nodes. This is a useful obstruction: entropy-guided attention can improve branching while still lose after honest accounting.

The next admissible gate is therefore not “scale it up blindly”. It is:

```text
H002_CHEAP_PRESSURE_ESTIMATOR_OR_B4_6_2_TRAJECTORY_ENSEMBLE_ABLATION
```

A successful next stage must preserve the exact branch tree while reducing probe overhead, or show that B4.6.2 ancestry disagreement contains enough reusable structure to amortize the probes.

## Strict boundary

```text
H001_EXACTNESS                    = VERIFIED_CANDIDATE
H001_SEARCH_TREE_REDUCTION        = OBSERVED_ON_FROZEN_SUITE
H001_TOTAL_WORK_REDUCTION         = FALSE_ON_FROZEN_SUITE
H001_POLYNOMIAL_WORST_CASE        = NOT_PROVED
C049_1_TERMINAL                   = UNCHANGED
P_VS_NP                           = OPEN
```

Draft only. No automatic merge.
