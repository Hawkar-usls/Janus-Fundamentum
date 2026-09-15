# JANUS P–N Junction — Complete SAT/UNSAT Gate v1.1

## Status

- Internal local-search gate v0.4: TRUE
- Complete DPLL gate v1.1: TRUE
- General scientific breakthrough: NOT YET ESTABLISHED

## Frozen holdout

- Seed: `550004`
- Cases: `148`
- Families: phase-transition planted 3-SAT, satisfiable graph coloring, unsatisfiable complete-graph coloring, pigeonhole, exactly-one SAT/UNSAT.
- Same complete DPLL engine for all branching heuristics.
- Baselines: MOMS and Jeroslow–Wang (JW).
- P–N parameters were fixed before this holdout.

## Correctness

P–N Complete v1.1 returned the correct SAT/UNSAT status on `148/148` cases, with `0` UNKNOWN results.

## Search-tree results

| Heuristic | Total nodes | Median nodes | Total Python time, ms |
|---|---:|---:|---:|
| MOMS | 6270 | 11.0 | 956.081 |
| JW | 5841 | 10.5 | 907.122 |
| P–N Complete v1.1 | **5572** | **9.0** | 1144.941 |

P–N reduced total search nodes by `11.13%` versus MOMS and `4.61%` versus JW.

## Paired comparisons

- Against MOMS: 87 wins, 29 ties, 32 losses.
- Against JW: 82 wins, 31 ties, 35 losses.

## Family behavior

- Complete graph coloring UNSAT: strongest result; median tree ratio `0.761` against the per-case better conventional baseline.
- Satisfiable graph coloring: median ratio `0.894`.
- Exactly-one: neutral.
- Pigeonhole: currently weaker, mean ratio `1.138`.
- Random planted 3-SAT: mixed; aggregate improvement against each fixed baseline, but some instances remain worse.

## Runtime boundary

The current Python P–N scoring is `26.22%` slower than JW in aggregate despite the smaller tree. Incremental scores and watched clauses are required before claiming a practical speed breakthrough.

## Scientific interpretation

This holdout supports the claim that persistent conflict charge plus junction-bridge branching can reduce complete DPLL search trees over this mixed SAT/UNSAT synthetic suite.

It does not establish a general SAT breakthrough, `P = NP`, or superiority over modern CDCL solvers. Standard public benchmarks, equal-resource compiled implementations, proof checking for UNSAT, and independent replication remain required.