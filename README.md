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

## Current laboratory status — C004

The refutation sweep leaves **17 live hypotheses** and retires two C003 entries:

### H016 — DESTROYED

The promised polynomial-size d-DNNF `D(x,y)` projected exactly to the original CNF. Forgetting `y` preserves ordinary DNNF and does not increase size. Explicit polynomial-size CNF families require exponential DNNF size, yielding a direct contradiction.

Read [`proof_attempts/H016/REFUTATION.md`](proof_attempts/H016/REFUTATION.md).

### H018 — REJECTED

The registered residual-quotient statement did not require complete coverage, acceptance of satisfiable instances, rejection of unsatisfiable instances, or any final decision. An algorithm with no accepting paths satisfied its written witness condition vacuously.

Read [`proof_attempts/H018/FORMULATION_FAILURE.md`](proof_attempts/H018/FORMULATION_FAILURE.md).

### Surviving pressure points

- `H009` and `H017` are weakened because finite local rewrite systems may still simulate general polynomial computation unless a preserved invariant is specified.
- `H010` survives current extension-variable lower bounds because the exact field, dependency, and resource models do not yet match.
- `H019` survives, but its interface language and certificate-composition semantics need stricter formalization.
- `H014` and `H015` remain external literature frontiers rather than JANUS discoveries.

No C004 result proves anything about `P` versus `NP`; it demonstrates that the registry can genuinely kill its own entries.

## Historical JANUS experiments

The earlier p-n-inspired SAT experiments remain under [`experiments/`](experiments/). They are finite algorithmic evidence, not asymptotic complexity proofs.

## Contribution rule

A contribution should make the registry easier to falsify, reproduce, or verify. Strong counterexamples are as valuable as surviving hypotheses. Literature-frontier entries must cite primary sources and must never be presented as JANUS novelty.

See [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) for the admission protocol and claim boundaries.
