# JANUS Proof Search Laboratory

> **Generate hypotheses. Attack them. Preserve survivors. Never confuse survival with proof.**

JANUS is a public, machine-readable laboratory for reproducible research around computational complexity, with `P` versus `NP` as its long-term target.

This repository does **not** claim that `P = NP` or `P != NP` has been proved. It maintains an auditable history of formal hypotheses, attacks, counterexamples, primary sources, proof attempts, surviving candidates, and terminal failures.

## Law 0 — independent reproducibility

Any computational claim must be reproducible by an independent person on an independent machine from committed code, fixed inputs, seeds, expected outputs, and hashes.

A finite experiment may falsify a universal algorithmic claim, but it cannot by itself prove a universal asymptotic statement.

## Law 1 — proof-directed admission

Beginning with `H030`, survival is not enough. Every admitted hypothesis must state:

- its exact `proof_role` in a route toward `P = NP`, `P != NP`, `NP != coNP`, a required circuit lower bound, or the destruction of a central JANUS mechanism;
- its `next_gate`: the next theorem, construction, implementation, or counterexample that advances or kills the route;
- at least two registered attacks.

The validator enforces these requirements automatically.

## Research states

`PROPOSED -> UNDER_ATTACK -> OPEN -> FORMALIZING -> INDEPENDENT_REPRODUCTION -> PEER_REVIEW -> PROVED`

A hypothesis may move to `DESTROYED` or `REJECTED` from any state. `OPEN` means only that the registered attacks have not destroyed the exact statement. It does not mean true, likely true, novel, or compatible with every other open entry.

## Machine-readable organism

Every major ledger is modular:

- `registry/hypotheses*.json` — historical hypothesis snapshots;
- `registry/attacks*.json` — falsification attempts;
- `registry/references*.json` — primary-source context;
- `registry/graveyard*.json` — terminal records and pre-admission rejections retained permanently;
- `registry/observations*.json` — proved reductions and methodological findings;
- `registry/journal*.json` — chronological research cycles;
- `registry/genealogy*.json` — parent/child proof routes;
- [`registry/schema.json`](registry/schema.json) — field and status contract.

Validate the complete organism:

```bash
python tools/validate_registry.py
```

GitHub Actions runs the same validation on every pull request and push.

## Current laboratory status — C006

Cycle C006 screened **42 candidate formulations**. Twelve were rejected before admission, and exactly **30 proof-directed hypotheses `H030-H059`** survived **60 immediate attacks `A077-A136`**.

After the earlier destruction of `H016` and rejection of `H018`, the laboratory contains **57 live hypotheses**. This number is an inventory, not evidence.

### Direct separation routes

- `H030-H032` target explicit NP circuit lower bounds through general circuits, certified SAT anti-checkers, and witnessing formulas.
- `H033-H036` target `NP != coNP` or `P != NP` through Nisan-Wigderson/strong proof generators, Extended-Frege circuit rewriting, and canonical disjoint NP pairs.
- `H037-H039` connect full IPS, PIT axioms, and deterministic PIT to explicit algebraic or Boolean lower bounds.

### Complete constructive routes to `P = NP`

- `H040-H042` repair residual quotienting, proof-carrying elimination, and parity-core compilation by requiring complete two-sided correctness and explicit semantics.
- `H043-H045` restrict broad optimization lifts to finite local submodular, totally-unimodular, and constant-level SoS gadget grammars.
- `H046-H049` target deterministic proof search, deterministic isolation into a tractable residual class, one canonical CDCL policy, and certified exact model-counting decomposition.

### Hypotheses designed to destroy hypotheses

- `H050-H054` attempt to translate elimination into DNNF, extract communication protocols from local lifts, choose an explicit hard algebraic family, preserve mixed residual expansion, and prove fixed-policy CDCL lower bounds.
- `H055-H056` test whether constructive range avoidance can produce strong proof generators or certified SAT anti-checkers.

### Barrier-breaking routes

- `H057` asks for a self-improving Circuit-SAT speedup with lower-bound consequences.
- `H058` seeks a sparse constructive useful property that deliberately avoids the largeness condition of natural proofs.
- `H059` uses explicit linear-map lower bounds as a clean precursor for non-natural general-circuit methods.

Every C006 survivor has two attacks and a recorded next gate. No survivor is called probable, novel, or proved.

Read the full screening record: [`docs/C006_SCREENING.md`](docs/C006_SCREENING.md).

## Prior terminal results

- [`H016 — DESTROYED`](proof_attempts/H016/REFUTATION.md): projected polynomial d-DNNF would contradict unconditional DNNF lower bounds.
- [`H018 — REJECTED`](proof_attempts/H018/FORMULATION_FAILURE.md): the statement omitted complete decision correctness and was vacuously satisfiable.
- `H000-G10` through `H000-G21`: twelve C006 candidates rejected before admission for circularity, invalid consequences, hidden computation, missing explicitness, or absence of a proof-directed role.

No JANUS result currently resolves `P` versus `NP`.

## Historical JANUS experiments

The earlier p-n-inspired SAT experiments remain under [`experiments/`](experiments/). They are finite algorithmic evidence, not asymptotic complexity proofs.

## Contribution rule

A contribution should make the proof graph shorter, the statements easier to falsify, or the results easier to reproduce. Strong counterexamples are as valuable as survivors. Literature-frontier entries must cite primary sources and must never be presented as JANUS novelty.

See [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) for the admission protocol and claim boundaries.
