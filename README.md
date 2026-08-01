# JANUS P–N Junction Experiments

A falsifiable research repository for testing an **information-junction** model of SAT search inspired by p–n semiconductor dynamics.

The project maps candidate assignments to an N-region, persistent unsatisfied clauses to information holes in a P-region, variable flips to carrier motion, and full satisfaction to recombination. This is a computational model implemented on ordinary hardware. It is **not** direct control of transistor p–n junctions and does **not** prove `P = NP`.

## Current experiments

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

Selected result: on planted 3-SAT with `n=64`, `m=273`, sixteen trials and a budget of `28n`, WalkSAT solved `15/16` with median `155` steps among solved runs; Junction base solved `16/16` with median `55`; Junction Tunnel solved `16/16` with median `42`.

Negative result retained: at 3-SAT `n=32`, the tunnel variant regressed from median `38` to `48` steps because escape activation was too aggressive.

## Reproduce

```bash
python experiments/v0.1-junction/junction_sim.py
python experiments/v0.2-tunnel/junction_tunnel_sim.py
```

The scripts currently write their outputs to `/mnt/data/...` because they were produced in the original experiment runtime. For local use, change those output paths to paths inside this repository. The committed CSV and JSON files preserve the original run outputs and seeds.

## Research boundary

These runs use small planted satisfiable instances and are exploratory. They do not establish asymptotic complexity. A serious next gate must include matched initial assignments, known UNSAT cases, standard SAT benchmarks, stronger baselines, incremental implementations, confidence intervals, ablations, and resource-normalized accounting for time, primitive operations, memory, energy, and swarm communication.

See `experiment_manifest.json` for machine-readable provenance, hashes, limitations, and the next falsification gate.

## Lineage

This work extends the SAT-swarm and evolutionary-search line from [Janus-Demiurge](https://github.com/Hawkar-usls/Janus-Demiurge) and is registered in [janus-meta-registry](https://github.com/Hawkar-usls/janus-meta-registry).
