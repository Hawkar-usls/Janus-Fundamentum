# JANUS P–N Junction Distributed Swarm v2.0

**Status:** `PASS_DISTRIBUTED_WALL_ROUNDS_WITH_EXPLICIT_WORK_COST`  
**Holdout seed:** `440225`  
**Parameter policy:** frozen before the official holdout  
**Scope:** planted random 3-SAT near α≈4.26, planted 5-SAT near α≈6.1, narrow proven UNSAT cores, an UNSAT instance outside the implemented proof witness, and a synthetic local-depletion trap.

## What changed after v0.3

1. Removed the oscillation term from the Gladius depletion-depth equation.
2. Retained clause charge across improvements and memory restores.
3. Fixed negative fall-through: when no permitted move exists, the lane enters `HOLD` instead of silently choosing another harmful flip.
4. Fixed no-op `SURVIVE`: restoring the same state no longer resets stagnation and blocks the packet gate forever.
5. Added a two-part CHAOS gate: measured depth plus a reversible probe showing packet utility.
6. Added explicit states `RECOMBINATION_FOUND`, `PROVEN_NO_RECOMBINATION`, and `SEARCH_EXHAUSTED_NO_PROOF`.
7. Restored Project JANUS v7.2 ideas as bounded engineering mechanisms: control modes, hunger, memory injection, survival rollback and a quarantined scout.
8. Replaced process-dependent Python string hashing with SHA-256-derived Gladius seeds.
9. Preserved an untouched Anchor control lane and logged aggregate work separately from parallel rounds.

## Distributed architecture

- **Anchor:** stable baseline/control lane.
- **Gladius:** Selective Field v2.0 active lane.
- **Zim:** quarantined historical v0.3 scout, enabled for 3-SAT n≥64.
- **Holocron:** observer/arbitrator semantics; first verified recombination ends the parallel race. A dedicated public Holocron firmware is not claimed yet.

## Official holdout

The v2.0 swarm solved **117/117 SAT instances**. WalkSAT solved **116/117**. At every tested size, v2.0's median parallel rounds were no worse than the better standalone constituent (Anchor or v0.3); it improved at 9 of 12 size points and tied at 3.

### 3-SAT

| k | n | trials | v2.0 median rounds | best constituent | gain vs best | WalkSAT | gain vs WalkSAT | work ratio |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3 | 32 | 12 | 17.0 | 18.0 | 5.6% | 45.5 | 62.6% | 1.63× |
| 3 | 48 | 12 | 24.0 | 28.0 | 14.3% | 44.0 | 45.5% | 1.20× |
| 3 | 64 | 12 | 41.5 | 52.0 | 20.2% | 143.0 | 71.0% | 2.09× |
| 3 | 96 | 12 | 100.0 | 111.5 | 10.3% | 556.0 | 82.0% | 1.77× |
| 3 | 128 | 12 | 125.5 | 130.5 | 3.8% | 530.0 | 76.3% | 2.88× |
| 3 | 160 | 12 | 158.0 | 202.0 | 21.8% | 480.0 | 67.1% | 2.24× |
| 3 | 192 | 8 | 221.5 | 262.5 | 15.6% | 843.5 | 73.7% | 1.79× |
| 3 | 240 | 4 | 238.0 | 292.5 | 18.6% | 771.5 | 69.2% | 1.96× |
| 3 | 320 | 3 | 356.0 | 356.0 | 0.0% | 2050.0 | 82.6% | 3.01× |

### 5-SAT

| k | n | trials | v2.0 median rounds | best constituent | gain vs best | WalkSAT | gain vs WalkSAT | work ratio |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 | 64 | 10 | 8.0 | 8.0 | 0.0% | 11.0 | 27.3% | 1.98× |
| 5 | 96 | 10 | 10.0 | 12.0 | 16.7% | 25.5 | 60.8% | 1.85× |
| 5 | 128 | 10 | 15.0 | 15.0 | 0.0% | 28.0 | 46.4% | 1.96× |

Across the 12 tested size points, the unweighted mean median-round improvement was **10.57%** versus the best standalone constituent and **63.71%** versus WalkSAT. This point-average is descriptive, not a confidence interval.

## NO_RECOMBINATION gates

- **40/40** complete-sign contradiction cores returned `PROVEN_NO_RECOMBINATION` immediately with a machine-readable witness.
- The pigeonhole formula PHP(3,2), which is UNSAT but outside that narrow witness, returned `SEARCH_EXHAUSTED_NO_PROOF` in **12/12** runs.
- No UNSAT test produced a false recombination or an unsupported proof claim.

## Local depletion trap

The synthetic trap makes each useful individual flip look harmful while a coordinated two-variable packet improves the state. With single uphill moves disabled, Gladius solved **32/32** trap runs. All **72/72** accepted CHAOS packets had first passed the reversible utility probe. The test used **3,888 probe flips**, which are published as work rather than hidden.

## Cost accounting

The median aggregate-work ratio across size points was **1.96×** the cheaper standalone constituent. The observed range was **1.20×–3.01×**. Therefore v2.0 is a distributed wall-round improvement, not a claim of lower total computation or energy.

Python wall time is also not favorable because the reference simulator executes lanes serially and performs expensive field bookkeeping. Physical ESP32 testing must measure energy, radio cost, synchronization and real concurrent elapsed time.

## Reproducibility and tests

- Same formula, initial assignment and solver seed were shared across methods.
- SHA-256-derived internal seed removes process hash randomization.
- Release smoke tests cover SAT, proven UNSAT, unknown UNSAT and the packet trap.
- A cross-process test with different `PYTHONHASHSEED` values produced identical algorithmic output.
- The chat release bundle contains `final_results.json`. The repository stores deterministic benchmark code, the frozen configuration, summaries and SHA-256 hashes so the full record can be regenerated.

## Claim boundary

This release does **not** prove `P=NP`, does not establish polynomial worst-case scaling, and does not show that semiconductor p–n physics is mathematically equivalent to complexity classes. It establishes a reproducible software architecture in which multiple complementary search fields reduce parallel decision rounds on the tested distributions while exposing their extra work.

The `n=240` and especially `n=320` rows have small trial counts and are exploratory. Standard SAT Competition benchmarks, crafted hard families, larger independent samples, incremental clause bookkeeping and physical energy measurements remain required.
