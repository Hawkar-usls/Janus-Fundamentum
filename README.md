# JANUS Proof Search Laboratory

> **Generate hypotheses. Attack them. Preserve survivors. Never confuse survival with proof.**

JANUS is a public, machine-readable laboratory for reproducible research around computational complexity, with `P` versus `NP` as its long-term target.

This repository does **not** claim that `P = NP` or `P != NP` has been proved. It maintains an auditable history of formal hypotheses, attacks, counterexamples, primary sources, proof attempts, descendants, inversion tests, and terminal failures.

## Law 0 — independent reproducibility

Any computational claim must be reproducible by an independent person on an independent machine from committed code, fixed inputs, seeds, expected outputs, and hashes.

A finite experiment may falsify a universal algorithmic claim, but it cannot by itself prove a universal asymptotic statement.

## Law 1 — proof-directed admission

Beginning with `H030`, every admitted hypothesis must state its `proof_role`, its `next_gate`, and at least two registered attacks.

## Law 2 — inherited progress

Beginning with `H060`, every new hypothesis must state:

- `derived_from`: the older hypotheses from which it descends;
- `delta_from_parents`: the material new obligation introduced by the descendant.

`tools/validate_lineage.py` verifies that the parents exist, are older than the child, and match the genealogy ledger.

## Law 3 — inversion before expansion

A new research direction does not replace existing hypotheses. It is first applied as a backside test to the current proof graph.

The C008 inversion matrix enforces this principle: at least 70% of its selected hypotheses must predate C008. The current 20×20 seed contains **15 inherited hypotheses and 5 theta descendants**.

## Research states

`PROPOSED -> UNDER_ATTACK -> OPEN -> FORMALIZING -> INDEPENDENT_REPRODUCTION -> PEER_REVIEW -> PROVED`

A hypothesis may move to `DESTROYED` or `REJECTED` from any state. `OPEN` means only that the registered attacks have not destroyed the exact statement.

## Machine-readable organism

- `registry/hypotheses*.json` — historical hypothesis snapshots;
- `registry/attacks*.json` — falsification attempts;
- `registry/references*.json` — primary-source context;
- `registry/graveyard*.json` — terminal records and pre-admission rejections;
- `registry/observations*.json` — proved reductions and methodological findings;
- `registry/journal*.json` — chronological research cycles;
- `registry/genealogy*.json` — parent/child proof routes;
- `registry/inversion-tests-c008.json` — shared backside tests;
- `registry/inversion-matrix-c008.json` — inherited 20×20 attack matrix;
- `registry/schema.json` — field and status contract.

Validate the organism:

```bash
python tools/validate_registry.py
python tools/validate_lineage.py
python tools/validate_inversion_matrix.py
```

GitHub Actions runs all three validations on every relevant pull request and push.

## Current laboratory status — C008

C008 seeds the path toward the requested 100×100 inversion laboratory with a validated **20 hypotheses × 20 tests = 400 logical cells** matrix.

The matrix deliberately reuses these earlier routes:

- direct targets and certificates: `H030`, `H031`, `H040`, `H046`, `H049`;
- structural compilers: `H041-H045`;
- adversarial transfers: `H050`, `H051`, `H053`, `H062`, `H067`.

It adds only five descendants:

- `H070` — certified Lovasz-theta gap SAT compiler;
- `H071` — finite-lift theta-rank obstruction;
- `H072` — affine-stable theta-rank residual;
- `H073` — theta-certificate/proof-system transfer;
- `H074` — bounded-theta SAT/UNSAT indistinguishability.

The five descendants received fifteen immediate attacks `A161-A175`. None is proved. `H070` and `H072` are already weakened by known failure regimes or missing explicitness, but their exact narrowed statements remain open.

Read [`docs/C008_THETA_INVERSION.md`](docs/C008_THETA_INVERSION.md).

## C007 terminal result retained

`H048` remains destroyed: polynomially many ordinary CDCL conflicts with a Resolution trace would give polynomial Resolution refutations, contradicting explicit exponential lower bounds.

The salvage route `H063` changes the proof system to parity-aware CDCL rather than merely changing its policy.

## Current inventory

After retiring `H048` and adding `H070-H074`, JANUS contains **71 live hypotheses**. This count is an inventory, not evidence of progress toward the final separation.

## Prior terminal results

- [`H016 — DESTROYED`](proof_attempts/H016/REFUTATION.md): projected polynomial d-DNNF contradicts unconditional DNNF lower bounds.
- [`H018 — REJECTED`](proof_attempts/H018/FORMULATION_FAILURE.md): missing complete decision correctness made the statement vacuous.
- [`H048 — DESTROYED`](proof_attempts/H048/REFUTATION.md): ordinary CDCL remains inside Resolution.
- `H000-G10` through `H000-G21`: twelve C006 candidates rejected before admission.

No JANUS result currently resolves `P` versus `NP`.

## Theta experiment seed

`experiments/theta/conflict_graph.py` constructs the standard clause-literal conflict graph and can compute exact independence number only for tiny fixtures. It does **not** compute theta and is not a polynomial SAT solver.

## Contribution rule

A contribution should shorten the proof graph, expose a new falsification mechanism, or improve independent reproducibility. New hypotheses must build on the existing organism rather than bypass it.
