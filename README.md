# JANUS Proof Search Laboratory

> **Generate hypotheses. Attack them. Preserve survivors. Never confuse survival with proof.**

JANUS is a public, machine-readable laboratory for reproducible research around computational complexity, with `P` versus `NP` as its long-term target.

This repository does **not** claim that `P = NP` or `P != NP` has been proved. Its purpose is to maintain an auditable history of:

- formal hypotheses;
- explicit falsification conditions;
- attacks and counterexamples;
- reproducible experiments;
- surviving open candidates;
- destroyed ideas and the exact reason they failed;
- observations, literature boundaries, lemmas, and proof attempts.

## Law 0 — independent reproducibility

Any computational claim must be reproducible by an independent person on an independent machine from committed code, fixed inputs, seeds, expected outputs, and hashes.

A finite experiment may falsify a universal claim, but it cannot by itself prove a universal asymptotic statement.

## Research states

`PROPOSED -> UNDER_ATTACK -> OPEN -> FORMALIZING -> INDEPENDENT_REPRODUCTION -> PEER_REVIEW -> PROVED`

A hypothesis may move to `DESTROYED` from any state. `OPEN` means only that the registered attacks have not destroyed the exact statement. It does not mean true, likely true, novel, or mutually compatible with every other open entry.

## Machine-readable laboratory

- [`registry/hypotheses.json`](registry/hypotheses.json) — hypotheses that survived the currently recorded attacks.
- [`registry/attacks.json`](registry/attacks.json) and `registry/attacks-*.json` — modular ledgers of every registered falsification attempt.
- [`registry/references.json`](registry/references.json) — primary-source literature context and audited boundaries.
- [`registry/graveyard.json`](registry/graveyard.json) — rejected or destroyed formulations, retained permanently.
- [`registry/observations.json`](registry/observations.json) — reproducible facts and meta-observations.
- [`registry/journal.json`](registry/journal.json) — chronological research cycles.
- [`registry/genealogy.json`](registry/genealogy.json) — parent/child relations between ideas.
- [`registry/schema.json`](registry/schema.json) — field, status, and cross-reference contract.

Validate the complete registry:

```bash
python tools/validate_registry.py
```

GitHub Actions runs the same validation on every pull request and push.

## Current laboratory status

Cycle `C002` contains eleven live hypotheses:

- `H001-H004`: broad exact-lift targets, now explicitly marked as theorem-equivalent to `P = NP` as stated because an unrestricted transformer can solve first and encode later;
- `H005-H008`: literature-grounded proof-complexity lower-bound frontiers;
- `H009-H010`: JANUS-generated algorithmic mechanisms whose allowed operations are restricted independently of a general SAT oracle;
- `H011`: the polynomial-boundedness counterfrontier for Extended Frege, retained alongside its mutually incompatible lower-bound hypothesis.

None is a theorem. The most important next gates are to instantiate H009 with a concrete finite rewrite grammar, build a proof checker for H010, and choose explicit hard families for H005-H008.

## Historical JANUS experiments

The earlier p–n-inspired SAT experiments are preserved under [`experiments/`](experiments/). They are historical evidence about finite algorithms and benchmarks, not asymptotic complexity proofs. Their code, negative results, reports, and manifests remain part of the laboratory record.

## Contribution rule

A contribution should make the registry easier to falsify, reproduce, or verify. Strong counterexamples are as valuable as surviving hypotheses. Literature-frontier entries must cite primary sources and must never be presented as JANUS novelty.

See [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) for the admission protocol and claim boundaries.
