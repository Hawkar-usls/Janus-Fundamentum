# JANUS P–N Junction Experiments

A falsifiable research repository for testing an **information-junction** model of SAT search inspired by p–n semiconductor dynamics.

The project maps candidate assignments to an N-region, persistent unsatisfied clauses to information holes in a P-region, variable flips to carrier motion, and full satisfaction to recombination. This is a computational model implemented on ordinary hardware. It is **not** direct control of transistor p–n junctions and does **not** prove `P = NP`.

## Current release: v2.0 Selective Distributed Field

Path: [`experiments/v2.0-selective-distributed/`](experiments/v2.0-selective-distributed/)

v2.0 fixes the main v0.3 failure mode: a single adaptive field could overheat, accept too many uphill moves, and repeatedly test avalanches on one hard basin. The new release is a distributed controller with explicit roles:

- `GLADIUS_SELECTIVE` — weakened oscillation term, persistent clause charge and a double-gated tested avalanche;
- `LEGACY_V03` — untouched shadow/control lane, never modified by experimental memory;
- `ANCHOR_STABLE` — selectively activated fallback field after measured stagnation;
- `SCOUT_CHAOS` — bounded last-resort lane, not needed during the final holdout;
- `HOLOCRON` — coordinator, verifier and witness layer for the future physical deployment.

The controller separates **latency** from **total work**. The first physical lane to solve determines latency; all committed flips, memory reconstruction and avalanche probes are counted as work.

### Frozen holdout result

Seed: `440224`  
Test: 64 new planted random 3-SAT instances near α≈4.26, `n=32…240`, eight trials per size, matched formula and starting assignment.

| metric | v0.3 | v2.0 |
|---|---:|---:|
| solved | 64/64 | 64/64 |
| median latency | 116.5 | **87.0** |
| mean latency | 155.97 | **137.38** |
| p90 latency | 334 | **316** |
| mean total work | 155.97 | 329.19 |

Paired comparison: v2.0 was faster on `25` instances, tied on `39`, and slower on `0`. Median distributed latency improved by **25.3%**, while aggregate work increased by **2.11×**. This is therefore a distributed-latency result, not free computation.

On 18 guaranteed contradictory sign-core instances, v2.0 produced `18/18` sound `PROVEN_NO_RECOMBINATION` witnesses and zero false SAT results. The witness is intentionally narrow; ordinary search exhaustion remains `SEARCH_EXHAUSTED_NO_PROOF`.

Read:

- [`REPORT.md`](experiments/v2.0-selective-distributed/REPORT.md)
- [`release_summary.json`](experiments/v2.0-selective-distributed/release_summary.json)
- [`latency_comparison.csv`](experiments/v2.0-selective-distributed/latency_comparison.csv)
- [`SWARM_INTEGRATION.md`](experiments/v2.0-selective-distributed/SWARM_INTEGRATION.md)
- [`sha256.json`](experiments/v2.0-selective-distributed/sha256.json)

## Earlier experiments

### v0.1 — Charged Junction

Path: `experiments/v0.1-junction/`

Mechanisms:

- charge accumulation on persistent unsatisfied clauses;
- pressure on variables touching those clauses;
- weighted flip delta;
- momentum;
- simple stagnation breakdown.

Selected result: on planted 3-SAT with `n=48`, `m=202`, eight trials and a budget of `35n`, median solved steps were `128` for WalkSAT and `36.5` for Junction. Both solved `8/8`.

### v0.2 — Junction Tunnel

Path: `experiments/v0.2-tunnel/`

Added mechanisms:

- adaptive barrier energy;
- controlled thermal uphill moves;
- tabu memory;
- coherent multi-flip avalanche pulse;
- partial discharge preserving clause history.

Selected result: on planted 3-SAT with `n=64`, `m=273`, sixteen trials and a budget of `28n`, WalkSAT solved `15/16` with median `155` steps; Junction Base solved `16/16` with median `55`; Junction Tunnel solved `16/16` with median `42`.

Negative result retained: at 3-SAT `n=32`, the tunnel variant regressed from median `38` to `48` steps because escape activation was too aggressive.

### v0.3 — Adaptive depletion depth

The v0.3 runtime experiment introduced a learned depletion-depth score and removed most false breakdowns. It produced the control lane preserved inside v2.0. Its critical negative result was a hard `n=64` instance with excessive uphill acceptance and repeated avalanche probing; v2.0 was designed specifically around that failure.

## Lineage

This work extends two earlier JANUS lines:

1. the SAT swarm and evolutionary search in [Janus-Demiurge](https://github.com/Hawkar-usls/Janus-Demiurge);
2. Project JANUS v7.2, which combined clause weighting, WalkSAT, hill climbing, memory injection, adaptive timeout and controller modes `EXPLORE`, `EXPLOIT`, `HUNT`, `SURVIVE`, and `CHAOS`.

The physical deployment target is the prepared [JANUS Distributed AI Swarm](https://github.com/Hawkar-usls/janus-distributed-ai-swarm). Existing mining packet ABIs remain untouched; the SAT experiment receives a separate versioned `J/P v2` packet family.

## Reproduce

The complete v2.0 source/results bundle is distributed with the release artifact and SHA-256 manifest. Earlier scripts can be run directly:

```bash
python experiments/v0.1-junction/junction_sim.py
python experiments/v0.2-tunnel/junction_tunnel_sim.py
```

## Research boundary

These experiments do not establish asymptotic complexity or superiority over CDCL/state-of-the-art SAT solvers. The next gate requires physical parallel execution, standard DIMACS and crafted benchmarks, confidence intervals, incremental bookkeeping, energy measurement, packet-loss accounting and comparison against stronger baselines.

See [`experiment_manifest.json`](experiment_manifest.json) for machine-readable provenance, limitations and the next falsification gate. The project is also registered in [janus-meta-registry](https://github.com/Hawkar-usls/janus-meta-registry).
