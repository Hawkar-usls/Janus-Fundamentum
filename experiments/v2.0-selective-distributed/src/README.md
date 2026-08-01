# v2.0 source

Pure-Python reference implementation for the frozen JANUS P–N Junction v2.0 holdout.

## Files

- `sat_core.py` — incremental SAT state, planted SAT generator and guaranteed complete sign-core UNSAT generator.
- `solvers.py` — WalkSAT, stable Junction Base and v0.2 Tunnel baselines.
- `adaptive.py` — preserved v0.3 adaptive depletion detector.
- `selective_swarm_v20.py` — Selective Field, untouched v0.3 control lane, Anchor fallback, Scout and no-recombination states.
- `run_holdout.py` — seed `440224`, matched formula/initial-assignment evaluation.

## Run

```bash
cd experiments/v2.0-selective-distributed/src
python run_holdout.py
```

Only the Python standard library is required. The full run is intentionally non-trivial because it evaluates multiple stateful lanes and counts hidden avalanche probes as work.

## Output

The runner writes:

```text
../reproduced_holdout_results.json
```

Compare the aggregate fields with `../release_summary.json`. Python wall time depends on the machine; logical transition counts and seeded task generation are the reproducibility targets.

## Claim boundary

`LEGACY_V03` is preserved as an untouched control lane. Therefore the distributed portfolio's first-solution latency cannot regress beyond that lane under the matched seed, but aggregate work can and does increase. This is a portfolio latency result, not a proof of polynomial complexity or P=NP.
