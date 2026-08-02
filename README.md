# JANUS Proof Search Laboratory

> **Generate hypotheses. Attack them. Preserve survivors. Never confuse survival with proof.**

JANUS is a public, machine-readable laboratory for reproducible research around computational complexity, with `P` versus `NP` as its long-term target.

This repository does **not** claim that `P = NP` or `P != NP` has been proved. It maintains an auditable history of hypotheses, attacks, proof attempts, primary sources, descendants, inversion tests, and terminal failures.

## Laboratory laws

1. **Independent reproducibility.** Computational claims require committed code, inputs, seeds, expected outputs, and hashes.
2. **Proof-directed admission.** From `H030`, every hypothesis names its `proof_role`, `next_gate`, and at least two attacks.
3. **Inherited progress.** From `H060`, every child names `derived_from` parents and a material `delta_from_parents`.
4. **Inversion before expansion.** New mathematics must first attack the existing proof graph rather than replace it.
5. **Terminal honesty.** Destroyed and rejected nodes remain addressable; descendants must remove the exact recorded failure.

## Research states

`PROPOSED -> UNDER_ATTACK -> OPEN -> FORMALIZING -> INDEPENDENT_REPRODUCTION -> PEER_REVIEW -> PROVED`

`OPEN` means only that registered attacks have not destroyed the exact statement. `FORMALIZING` is not proof. `PROVED` requires R5 formal and independent verification.

## Machine-readable organism

- `registry/hypotheses*.json` — historical hypothesis snapshots;
- `registry/attacks*.json` — falsification attempts;
- `registry/references*.json` — primary-source context;
- `registry/graveyard*.json` — permanent terminal records;
- `registry/observations*.json` — reductions and methodological findings;
- `registry/journal*.json` — chronological cycles;
- `registry/genealogy*.json` — parent/child proof routes;
- `registry/inversion-tests*.json` — reusable backside tests;
- `registry/inversion-matrix-c009.json` — current 30×30 inherited attack matrix.

Validate the organism:

```bash
python tools/validate_registry.py
python tools/validate_lineage.py
python tools/validate_inversion_matrix.py
python tools/validate_cycle_pressure.py
python experiments/theta/canonical_profile.py --self-test
```

## Current laboratory status — C009

C009 maximizes pressure on existing routes before admitting new nodes.

- **9 descendants:** `H075-H083`;
- **41 attacks:** `A176-A216`;
- **7 inherited targets re-attacked:** `H045`, `H062`, `H070-H074`;
- **1 terminal result:** `H074 — REJECTED`;
- **30×30 inversion matrix:** 900 logical cells, with 21 inherited hypotheses and 9 C009 descendants.

### Terminal result: H074

H074 used an undefined, open-ended theta profile. A preprocessing grammar could expose an answer-dependent statistic, including the SAT decision bit itself, so the statement had no stable falsification semantics. It is rejected and replaced by the finite canonical interface of `H078`, `H081`, and `H082`.

Read [`proof_attempts/H074/FORMULATION_FAILURE.md`](proof_attempts/H074/FORMULATION_FAILURE.md).

### Main surviving fork

- `H076` searches for an explicit constant-scope auxiliary extension that collapses theta rank.
- `H077` proposes the opposite bounded-depth stability theorem.
- `H078` seeks explicit SAT/UNSAT families indistinguishable by one fixed bounded-level theta profile.

Whichever side falls first removes a major ambiguity in `H045`, `H071`, and `H072`.

### Narrow formalization targets

- `H075` isolates coordinate permutations and complementations as degree-preserving Boolean-cube isomorphisms.
- `H081` adds explicit Slater and threshold margins before promising rational SDP certificates.
- `H082` narrows theta/SoS translation to fixed level, fixed encoding, and charged bit complexity.

Read [`docs/C009_MAXIMUM_INHERITANCE.md`](docs/C009_MAXIMUM_INHERITANCE.md).

## Current inventory

After rejecting `H074` and adding `H075-H083`, JANUS contains **79 live hypotheses**. This is inventory, not evidence or a percentage of completion.

## Prior terminal results

- [`H016 — DESTROYED`](proof_attempts/H016/REFUTATION.md): projected polynomial d-DNNF contradicts unconditional DNNF lower bounds.
- [`H018 — REJECTED`](proof_attempts/H018/FORMULATION_FAILURE.md): missing decision correctness made the statement vacuous.
- [`H048 — DESTROYED`](proof_attempts/H048/REFUTATION.md): ordinary CDCL remains inside Resolution.
- [`H074 — REJECTED`](proof_attempts/H074/FORMULATION_FAILURE.md): the observable theta interface was undefined and answer-dependent.

No JANUS result currently resolves `P` versus `NP`.

## Theta experiment tools

- `experiments/theta/conflict_graph.py` builds the standard clause-literal conflict graph and computes exact independence only for tiny fixtures.
- `experiments/theta/canonical_profile.py` freezes a finite monomial/objective/certificate schema for H078. It does **not** compute the Lovasz theta number.

## Contribution rule

A contribution must shorten a proof route, expose a falsification mechanism, or improve independent reproducibility. New hypotheses must inherit from the organism rather than bypass it.
