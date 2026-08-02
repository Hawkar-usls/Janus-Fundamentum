# JANUS Proof Search Laboratory

> **Generate hypotheses. Attack them. Preserve survivors. Never confuse survival with proof.**

JANUS is a public, machine-readable laboratory for reproducible research around computational complexity, with `P` versus `NP` as its long-term target.

This repository does **not** claim that `P = NP` or `P != NP` has been proved. It maintains an auditable history of formal hypotheses, attacks, counterexamples, primary sources, proof attempts, surviving candidates, and terminal failures.

## Law 0 — independent reproducibility

Any computational claim must be reproducible by an independent person on an independent machine from committed code, fixed inputs, seeds, expected outputs, and hashes.

A finite experiment may falsify a universal algorithmic claim, but it cannot by itself prove a universal asymptotic statement.

## Research states

`PROPOSED -> UNDER_ATTACK -> OPEN -> FORMALIZING -> INDEPENDENT_REPRODUCTION -> PEER_REVIEW -> PROVED`

A hypothesis may move to `DESTROYED` or `REJECTED` from any state. `OPEN` means only that the registered attacks have not destroyed the exact statement. It does not mean true, likely true, novel, or compatible with every other open entry.

## Machine-readable organism

Every major ledger is modular:

- `registry/hypotheses*.json` — historical hypothesis snapshots;
- `registry/attacks*.json` — falsification attempts;
- `registry/references*.json` — primary-source context;
- `registry/graveyard*.json` — terminal records that shadow earlier live snapshots without deleting history;
- `registry/observations*.json` — proved reductions and methodological findings;
- `registry/journal*.json` — chronological research cycles;
- `registry/genealogy*.json` — parent/child relations;
- [`registry/schema.json`](registry/schema.json) — field and status contract.

Validate the complete organism:

```bash
python tools/validate_registry.py
```

GitHub Actions runs the same validation on every pull request and push.

## Current laboratory status — C005

After the C004 destruction of `H016` and rejection of `H018`, cycle C005 adds exactly ten attacked survivors `H020-H029`. The laboratory now contains **27 live hypotheses**.

### Cutting Planes and Stabbing Planes

- `H020` asks whether the proved general dag-like Cutting Planes lower bound for concise pigeonhole formulas can be strengthened to `2^(Omega(n))`.
- `H021` asks for a superpolynomial unrestricted Stabbing Planes size lower bound.
- `H022` proposes a polynomial Cutting Planes simulation of unrestricted Stabbing Planes.
- `H023` proposes the incompatible counterfrontier: a superpolynomial Stabbing Planes-versus-Cutting-Planes separation.

### Recursive extension Polynomial Calculus

- `H024` proposes a lower bound against recursively global fan-in-two extension Polynomial Calculus over `GF(2)`.
- `H025` proposes the incompatible polynomial-boundedness counterfrontier for the same exact proof system.
- `H029` asks whether recursively global extension proofs can be normalized into the bounded-support regime reached by current lower-bound theorems.

### Explicit and adversarial frontiers

- `H026` isolates the open tautologicity branch of the explicit hard-DNF family from the 2026 `AC0[p]`-Frege metacomplexity result.
- `H027` is designed to destroy `H009` through an expander separator obstruction for every allowed local grammar.
- `H028` is designed to destroy `H017` through a mixed formula whose non-affine residual remains wide after all certified parity elimination.

C005 records twenty immediate attacks `A057-A076`. All ten hypotheses remain `OPEN` only because those exact attacks were not decisive. Two pairs are intentionally incompatible: `H022` versus `H023`, and `H024` versus `H025`.

The most valuable next targets are not new constructive promises but the adversarial bridges `H027-H029`, because proving any of them would eliminate or sharply constrain existing JANUS mechanisms.

## Prior terminal results

- [`H016 — DESTROYED`](proof_attempts/H016/REFUTATION.md): projected polynomial d-DNNF would contradict unconditional DNNF lower bounds.
- [`H018 — REJECTED`](proof_attempts/H018/FORMULATION_FAILURE.md): the statement omitted complete decision correctness and was vacuously satisfiable.

No JANUS result proves anything about `P` versus `NP`.

## Historical JANUS experiments

The earlier p-n-inspired SAT experiments remain under [`experiments/`](experiments/). They are finite algorithmic evidence, not asymptotic complexity proofs.

## Contribution rule

A contribution should make the registry easier to falsify, reproduce, or verify. Strong counterexamples are as valuable as surviving hypotheses. Literature-frontier entries must cite primary sources and must never be presented as JANUS novelty.

See [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) for the admission protocol and claim boundaries.
