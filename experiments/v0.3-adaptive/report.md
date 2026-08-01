# JANUS P–N Junction v0.3 — Holdout Report

- Status: **completed**
- Holdout seed: `440223`
- Detailed records: `726`
- Budget: `28 × n` transitions
- Fairness: same formula and initial assignment for every method in each trial.

## 3-SAT holdout

| n | Method | Solve rate | Median solved steps | Mean steps incl. failures | Accepted escapes/run | Mean ms |
|---:|---|---:|---:|---:|---:|---:|
| 32 | WalkSAT | 100.00% | 36.5 | 92.50 | 0.000 | 0.92 |
| 32 | Junction Base | 100.00% | 18.0 | 24.94 | 0.312 | 1.98 |
| 32 | Tunnel v0.2 | 100.00% | 17.0 | 21.81 | 0.312 | 2.37 |
| 32 | Adaptive v0.3 | 100.00% | 15.5 | 19.88 | 0.000 | 4.01 |
| 48 | WalkSAT | 100.00% | 117.0 | 176.12 | 0.000 | 1.72 |
| 48 | Junction Base | 100.00% | 59.0 | 75.94 | 1.438 | 8.15 |
| 48 | Tunnel v0.2 | 100.00% | 44.0 | 60.19 | 1.500 | 8.22 |
| 48 | Adaptive v0.3 | 100.00% | 52.5 | 61.38 | 0.312 | 15.52 |
| 64 | WalkSAT | 100.00% | 184.0 | 248.56 | 0.000 | 2.56 |
| 64 | Junction Base | 100.00% | 116.5 | 124.06 | 1.750 | 13.30 |
| 64 | Tunnel v0.2 | 93.75% | 62 | 207.12 | 7.125 | 24.55 |
| 64 | Adaptive v0.3 | 93.75% | 54 | 180.12 | 1.625 | 43.07 |
| 96 | WalkSAT | 93.75% | 245 | 508.12 | 0.000 | 5.53 |
| 96 | Junction Base | 100.00% | 102.5 | 220.12 | 2.500 | 33.09 |
| 96 | Tunnel v0.2 | 100.00% | 123.0 | 237.50 | 4.438 | 43.95 |
| 96 | Adaptive v0.3 | 100.00% | 86.5 | 177.69 | 0.875 | 60.42 |
| 128 | WalkSAT | 87.50% | 428.0 | 916.12 | 0.000 | 9.48 |
| 128 | Junction Base | 100.00% | 173.5 | 213.31 | 1.000 | 47.72 |
| 128 | Tunnel v0.2 | 100.00% | 139.5 | 341.06 | 5.188 | 69.27 |
| 128 | Adaptive v0.3 | 100.00% | 140.0 | 170.56 | 0.250 | 81.14 |

## Verdict

**Partial pass.** Adaptive v0.3 removed the false-breakdown problem at n=32, improved deep-basin behavior at n=96, and cut the n=128 long tail. It did not dominate everywhere: n=48 regressed, n=64 retained one failure, and Python runtime overhead increased.

Across all 80 3-SAT runs, v0.3 reduced mean transitions by **29.7%** and accepted **83.5% fewer avalanche escapes** than v0.2.

## Negative results retained

- At `n=48`, v0.3 regressed against Tunnel v0.2: median `52.5` versus `44` transitions.
- At `n=64`, v0.3 and v0.2 each failed one of 16 instances, while Junction Base solved all 16.
- The Python implementation did not win on wall-clock time.
- Ablation did not justify the oscillation term.
- Guaranteed-UNSAT contradiction-core stress showed the need for a no-recombination/proof-exhaustion state.

## Next gate

`v0.4 Selective Field`: remove or scale down oscillation, preserve persistent clause charge, allow avalanche only when depth and tested merit agree, and add a no-recombination/proof-exhaustion state.
