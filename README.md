# JANUS Proof Search Laboratory

> **Generate hypotheses. Attack them. Preserve survivors. Never confuse survival with proof.**

JANUS is a public, machine-readable laboratory for reproducible research around computational complexity, with `P` versus `NP` as its long-term target.

This repository does **not** claim that `P = NP` or `P != NP` has been proved. It maintains an auditable history of formal hypotheses, attacks, counterexamples, primary sources, proof attempts, surviving candidates, descendants, and terminal failures.

## Law 0 — independent reproducibility

Any computational claim must be reproducible by an independent person on an independent machine from committed code, fixed inputs, seeds, expected outputs, and hashes.

A finite experiment may falsify a universal algorithmic claim, but it cannot by itself prove a universal asymptotic statement.

## Law 1 — proof-directed admission

Beginning with `H030`, survival is not enough. Every admitted hypothesis must state:

- its exact `proof_role`;
- its `next_gate`;
- at least two registered attacks.

## Law 2 — inherited progress

Beginning with `H060`, every new hypothesis must also state:

- `derived_from`: the older hypotheses from which it descends;
- `delta_from_parents`: the material new obligation introduced by the descendant.

`tools/validate_lineage.py` verifies that the parents exist, are older than the child, match the genealogy ledger exactly, and are not merely decorative references.

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
python tools/validate_lineage.py
```

GitHub Actions runs both validations on every relevant pull request and push.

## Current laboratory status — C007

Cycle C007 is the first inherited cycle. It derives **10 child hypotheses `H060-H069`** from earlier nodes and attacks both ancestors and descendants with **24 attacks `A137-A160`**.

The cycle also records a decisive terminal result:

### H048 — DESTROYED

A polynomial number of ordinary first-UIP CDCL conflicts with a Resolution proof trace expands into a polynomial-size Resolution refutation. Explicit expander-based Tseitin contradictions require exponential general-Resolution refutations. Therefore no fixed ordinary-CDCL policy can satisfy H048 on every CNF.

Read [`proof_attempts/H048/REFUTATION.md`](proof_attempts/H048/REFUTATION.md).

### H054 — substantially strengthened

The same explicit Resolution-hard family works against every fixed standard-CDCL policy covered by the model; policy-by-policy diagonalization is unnecessary. JANUS records this as a proved reduction, but does not promote H054 to `PROVED` without R5 formalization and independent review.

Read [`proof_attempts/H054/RESOLUTION_TRANSFER.md`](proof_attempts/H054/RESOLUTION_TRANSFER.md).

### New inherited branches

- `H060`, `H066`, `H068`, `H069` connect certified SAT-circuit errors, range avoidance, canonical disjoint pairs, and sparse non-natural properties.
- `H061` and `H067` inherit the DNNF lower-bound attack and identify the exact overlap, nondeterminism, or cancellation resources needed to escape it.
- `H062` and `H064` seek one explicit mixed XOR/non-affine family that is simultaneously stable under affine compilation and hard for unrestricted `Res(XOR)`.
- `H063` is the salvage descendant of destroyed H048: it changes the proof system to parity-aware CDCL rather than merely changing the policy.
- `H065` selects the hard-DNF candidate of H026 as explicit endpoints for the Extended-Frege rewriting route H035.

After retiring H048 and adding ten descendants, the laboratory contains **66 live hypotheses**. This number is an inventory, not evidence.

## Prior terminal results

- [`H016 — DESTROYED`](proof_attempts/H016/REFUTATION.md): projected polynomial d-DNNF would contradict unconditional DNNF lower bounds.
- [`H018 — REJECTED`](proof_attempts/H018/FORMULATION_FAILURE.md): the statement omitted complete decision correctness and was vacuously satisfiable.
- [`H048 — DESTROYED`](proof_attempts/H048/REFUTATION.md): ordinary CDCL cannot universally have polynomially many conflicts while remaining inside Resolution.
- `H000-G10` through `H000-G21`: twelve C006 candidates rejected before admission.

No JANUS result currently resolves `P` versus `NP`.

## Historical JANUS experiments

The earlier p-n-inspired SAT experiments remain under [`experiments/`](experiments/). They are finite algorithmic evidence, not asymptotic complexity proofs.

## Contribution rule

A contribution should make the proof graph shorter, the statements easier to falsify, or the results easier to reproduce. Strong counterexamples are as valuable as survivors. Literature-frontier entries must cite primary sources and must never be presented as JANUS novelty.

See [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) and [`docs/C006_SCREENING.md`](docs/C006_SCREENING.md) for the admission protocol and earlier screening record.
