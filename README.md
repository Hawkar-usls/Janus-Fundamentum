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

A finite experiment may falsify a universal algorithmic claim, but it cannot by itself prove a universal asymptotic statement.

## Research states

`PROPOSED -> UNDER_ATTACK -> OPEN -> FORMALIZING -> INDEPENDENT_REPRODUCTION -> PEER_REVIEW -> PROVED`

A hypothesis may move to `DESTROYED` from any state. `OPEN` means only that the registered attacks have not destroyed the exact statement. It does not mean true, likely true, novel, or mutually compatible with every other open entry.

## Machine-readable laboratory

Every major ledger is modular. The validator aggregates the base file and all matching cycle files:

- `registry/hypotheses*.json` — hypotheses that survived their recorded attacks;
- `registry/attacks*.json` — every registered falsification attempt;
- `registry/references*.json` — primary-source literature context and audited boundaries;
- `registry/graveyard*.json` — rejected or destroyed formulations, retained permanently;
- `registry/observations*.json` — reproducible facts and meta-observations;
- `registry/journal*.json` — chronological research cycles;
- `registry/genealogy*.json` — parent/child relations between ideas;
- [`registry/schema.json`](registry/schema.json) — field, status, and cross-reference contract.

Validate the complete organism:

```bash
python tools/validate_registry.py
```

GitHub Actions runs the same validation on every pull request and push.

## Current laboratory status

Cycle `C003` raises the live registry to nineteen hypotheses:

- `H001-H004`: broad exact-lift targets retained with an explicit warning that unrestricted transformers are theorem-equivalent to `P = NP` through solve-and-encode;
- `H005-H008`: literature-grounded proof-complexity lower-bound frontiers;
- `H009-H010`: restricted JANUS mechanisms for local treewidth compilation and extension-enabled polynomial calculus;
- `H011-H015`: mutually incompatible proof-size and proof-search frontiers for Extended Frege, TC0-Frege, and full IPS;
- `H016-H019`: new JANUS mechanisms for bounded-radius d-DNNF compilation, parity-core separation, certified residual quotienting, and proof-carrying variable elimination.

Cycle C003 also records twenty new attacks, eleven primary sources, six observations, and three rejected routes. None of the new hypotheses is a theorem or claimed novelty.

The strongest next falsification target is a closure theorem showing that communication complexity or semantic residual diversity survives the exact local certificate languages of `H016-H019`. The strongest constructive target is a tiny concrete rule grammar for `H016` that can be exhaustively attacked on small CNFs.

## Historical JANUS experiments

The earlier p-n-inspired SAT experiments are preserved under [`experiments/`](experiments/). They are historical evidence about finite algorithms and benchmarks, not asymptotic complexity proofs. Their code, negative results, reports, and manifests remain part of the laboratory record.

## Contribution rule

A contribution should make the registry easier to falsify, reproduce, or verify. Strong counterexamples are as valuable as surviving hypotheses. Literature-frontier entries must cite primary sources and must never be presented as JANUS novelty.

See [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) for the admission protocol and claim boundaries.
