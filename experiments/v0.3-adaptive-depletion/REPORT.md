# JANUS P–N Junction v0.3 — Adaptive Depletion-Depth Detector

## Experiment identity

- Holdout seed: `440223`
- Budget: `28 × n` variable transitions
- Main SAT trials: 16 per point
- Guaranteed-UNSAT contradiction-core stress: 4 per point
- Ablation trials: 10 per point
- Fairness control: every method received the same generated formula and the same initial assignment in each trial.
- Parameter freeze: detector weights and thresholds were fixed in source before the holdout suite.

## Adaptive depth model

The detector combines normalized stagnation, recurrence/overlap of unsatisfied-clause maps, charged-clause pressure, flip oscillation, and recent positive progress. Small instances require a stronger threshold. Candidate avalanche packets are tested before application; at moderate depth only positive-merit packets are allowed.

## Main 3-SAT holdout

| n | Method | Solve rate | Median solved steps | Mean steps incl. failures | Mean accepted escapes | Mean ms |
|---:|---|---:|---:|---:|---:|---:|
| 32 | WalkSAT | 100.00% | 36.5 | 92.50 | 0.00 | 0.88 |
| 32 | Junction Base | 100.00% | 18 | 24.94 | 0.31 | 1.76 |
| 32 | Tunnel v0.2 | 100.00% | 17 | 21.81 | 0.31 | 2.08 |
| 32 | Adaptive v0.3 | 100.00% | 15.5 | 19.88 | 0.00 | 3.61 |
| 48 | WalkSAT | 100.00% | 117 | 176.12 | 0.00 | 1.63 |
| 48 | Junction Base | 100.00% | 59 | 75.94 | 1.44 | 7.23 |
| 48 | Tunnel v0.2 | 100.00% | 44 | 60.19 | 1.50 | 7.56 |
| 48 | Adaptive v0.3 | 100.00% | 52.5 | 61.38 | 0.31 | 12.92 |
| 64 | WalkSAT | 100.00% | 184 | 248.56 | 0.00 | 2.58 |
| 64 | Junction Base | 100.00% | 116.5 | 124.06 | 1.75 | 13.10 |
| 64 | Tunnel v0.2 | 93.75% | 62 | 207.12 | 7.12 | 24.01 |
| 64 | Adaptive v0.3 | 93.75% | 54 | 180.12 | 1.62 | 34.38 |
| 96 | WalkSAT | 93.75% | 245 | 508.12 | 0.00 | 5.01 |
| 96 | Junction Base | 100.00% | 102.5 | 220.12 | 2.50 | 31.60 |
| 96 | Tunnel v0.2 | 100.00% | 123 | 237.50 | 4.44 | 41.51 |
| 96 | Adaptive v0.3 | 100.00% | 86.5 | 177.69 | 0.88 | 60.21 |
| 128 | WalkSAT | 87.50% | 428 | 916.12 | 0.00 | 8.86 |
| 128 | Junction Base | 100.00% | 173.5 | 213.31 | 1.00 | 50.83 |
| 128 | Tunnel v0.2 | 100.00% | 139.5 | 341.06 | 5.19 | 71.05 |
| 128 | Adaptive v0.3 | 100.00% | 140 | 170.56 | 0.25 | 75.64 |

## Main findings

- **Small-instance false-breakdown problem was removed in the main holdout.** At 3-SAT `n=32`, Adaptive v0.3 solved 16/16 with median 15.5 steps and **zero avalanche escapes**, versus Tunnel v0.2 median 17 with 0.3125 escapes per run.
- At `n=48`, v0.3 regressed against v0.2: median 52.5 versus 44 steps, although it remained better than Junction Base (59) and WalkSAT (117).
- At `n=64`, v0.3 improved solved-run median from 62 to 54 and reduced accepted escapes from 7.125 to 1.625 per run. However, both v0.2 and v0.3 failed the same one of 16 instances, while Junction Base solved 16/16. This is a robustness failure gate.
- At `n=96`, v0.3 was strongest: 16/16 solved, median 86.5 steps versus 123 for v0.2, 102.5 for Base, and 245 for WalkSAT.
- At `n=128`, v0.3 and v0.2 had almost identical solved-run medians (140 vs 139.5), but v0.3 cut mean steps including long tails from 341.06 to 170.56 and accepted only 0.25 escapes per run instead of 5.19.
- Across all 80 3-SAT runs, v0.3 reduced mean transition count by **29.7%** versus v0.2 and accepted **83.5% fewer** avalanche escapes (49 vs 297).
- Wall-clock performance did not win: the Python v0.3 implementation spent more time computing depth, packet merit, and diagnostics. This test supports a transition-count advantage, not yet a time/energy advantage.

## Aggregate 3-SAT

| Method | Solved | Mean steps | Median steps | Mean ms | Accepted escapes |
|---|---:|---:|---:|---:|---:|
| Adaptive v0.3 | 79/80 | 121.92 | 59.0 | 37.35 | 49 |
| Junction Base | 80/80 | 131.68 | 86.0 | 20.90 | 112 |
| Tunnel v0.2 | 79/80 | 173.54 | 72.0 | 29.24 | 297 |
| WalkSAT | 77/80 | 388.29 | 192.0 | 3.79 | 0 |

## 5-SAT legacy line

All methods solved every tested 5-SAT instance at n=48, 64, and 96. Adaptive v0.3 triggered no avalanche escapes. Its transition counts were approximately tied with the other Junction variants, but its extra detector accounting increased runtime. The tested 5-SAT distribution remains too easy to discriminate the mechanisms strongly.

## Guaranteed-UNSAT contradiction-core stress

No method falsely reported SAT. These instances contain a deliberately embedded complete contradictory k-CNF core; they test behavior when recombination is impossible, not general UNSAT certification.

- v0.3 accepted fewer avalanche pulses than v0.2, but attempted many rejected packets, especially on 5-SAT.
- Because the solver has no UNSAT proof system, barrier depth keeps rising and the detector continues searching. A separate **no-recombination / proof-exhaustion gate** is required.

## Ablation result

- Removing the oscillation term improved the median at n=64 (45.5 versus 70) and was essentially neutral at n=96 (76 versus 77). The current oscillation coefficient is not justified.
- Removing avalanche worsened n=96 from median 77 to 102.5, so controlled packet crossing contributes on deeper instances.
- Removing charge worsened n=96 to median 100, supporting persistent-clause charge as a useful component.
- Recurrence was mixed: useful at n=96, but apparently over-sensitive on the small n=32 ablation sample.

## Verdict

**Partial pass.** v0.3 achieved its primary small-instance goal and improved deep-basin behavior at n=96 and the long tail at n=128. It did not establish universal superiority: n=48 regressed, n=64 retained a failure that Base avoided, runtime overhead remains large, and the oscillation term failed ablation.

The next version should be `v0.4 Selective Field`: remove or scale down oscillation at small/medium n, preserve charge, retain avalanche only when tested merit and depth agree, and add a no-recombination state for UNSAT-like behavior.

## Reproducibility files

- `junction_adaptive_v03.py` — SHA-256 `88b7c37ea0e5d68f7b0919cdb801c3c4bc55b6a47a263266452fa17ff1ac9149`
- `junction_adaptive_v03_results.json` — SHA-256 `00421ac79102be3d2e884c5384f012bf4db53df060ca48f1b1ff4246af70abc6`
- `junction_adaptive_v03_main.csv` — SHA-256 `f0e51acbb3072d89be30933830769a8382111ab8230aac04d9f2c631a57c2bb8`
- `junction_adaptive_v03_unsat.csv` — SHA-256 `3eceac2af522e13a513e745abe1738b4e13f033ed85010afcb37e6ff978b20ff`
- `junction_adaptive_v03_ablation.csv` — SHA-256 `c2bd0636da5f343807105895b00ce570084cc816102ae1c3c2d4db6f9630ee28`
