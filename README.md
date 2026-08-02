# JANUS Proof Search Laboratory

> **Generate hypotheses. Attack them. Preserve survivors. Never confuse survival with proof.**

JANUS is a public, machine-readable laboratory for reproducible research around computational complexity, with `P` versus `NP` as its long-term target.

This repository does **not** claim that `P = NP` or `P != NP` has been proved. It preserves hypotheses, attacks, proof attempts, primary sources, descendants, inversion tests, and terminal failures.

## Laboratory laws

1. **Independent reproducibility.** Computational claims require committed code, fixed inputs, expected outputs, seeds where applicable, and hashes.
2. **Proof-directed admission.** From `H030`, every hypothesis names its `proof_role`, `next_gate`, and registered attacks.
3. **Inherited progress.** From `H060`, every child names older parents and a material delta.
4. **Inversion before expansion.** New mathematics first attacks the existing graph.
5. **Terminal honesty.** Pressure is not converted into a graveyard result without a decisive theorem, counterexample, or formulation failure.
6. **Answer-independent observables.** Canonical profiles and exact certificates may not contain SAT labels, exact alpha, or hidden answer-dependent fields.
7. **Verification is not existence.** An exact verifier does not imply that a short certificate exists or can be found efficiently.

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
- `registry/genealogy*.json` — child-to-parent proof routes;
- `registry/lineage-reverse-c011.json` — append-only parent-to-child edges for C011;
- `registry/inversion-tests*.json` — reusable backside tests;
- `registry/inversion-matrix-c011.json` — current cumulative 46×46 matrix;
- `registry/schema.json` — policy and validation contract.

## Validate the organism

```bash
python tools/validate_registry.py
python tools/validate_lineage.py
python tools/validate_inversion_matrix.py
python tools/validate_cycle_pressure.py
python experiments/theta/conflict_graph.py --self-test
python experiments/theta/canonical_profile.py --self-test
python experiments/theta/symmetry_transport.py --self-test
python experiments/theta/rational_gram_verifier.py --self-test
python experiments/theta/rational_ldl.py --self-test
python experiments/theta/lovasz_theta_certificate.py --self-test
python experiments/theta/disjoint_union.py --self-test
python experiments/theta/theta_collision_bundle.py --self-test
```

## Current status — C011

C011 turns the theta branch into an exact finite certificate chain.

- **6 descendants:** `H092-H097`;
- **30 attacks:** `A257-A286`;
- **6 inherited targets re-attacked:** `H070`, `H081`, `H084`, `H085`, `H087`, `H089`;
- **no terminal result**;
- **46×46 inversion matrix:** 2116 logical cells;
- **40 of 46 matrix hypotheses inherited** from earlier cycles.

### Exact-certificate chain

```text
H089 rational verification
  -> H092 rational LDL PSD certificates
  -> H093 exact Lovasz-theta primal/dual certificates
  -> H094 one-sided dual theta-gap UNSAT certificates

H087 canonical level-one twins
  -> H096 finite exact collision seed
  -> H095 disjoint-union amplification

H081 conditioned rational certificates
  -> H097 polynomial-bit reconstruction under explicit margins
```

### H092: rational PSD without square roots

`rational_ldl.py` constructs and verifies exact permuted `LDL^T` decompositions over `fractions.Fraction`. This covers singular rational PSD matrices without requiring a rational ordinary Gram square root.

The algebraic induction is recorded in [`proof_attempts/H092/RATIONAL_LDL.md`](proof_attempts/H092/RATIONAL_LDL.md). The final universal bit-growth bound still awaits independent review.

### H093/H094: exact theta and one-sided UNSAT

`lovasz_theta_certificate.py` verifies one fixed Lovasz-theta primal/dual SDP using exact rational constraints and exact LDL positivity certificates.

For a conflict graph with clause target `m`, a verified dual upper bound `t<m` certifies UNSAT. Failure to find such a gap never certifies SAT.

### H095/H096: finite seed, no fabricated witness

`theta_collision_bundle.py` accepts a collision only when two equal-target graphs have opposite exact alpha labels and equal exact theta certificates. Its self-test deliberately uses a non-collision pair and requires rejection.

No positive collision seed is currently registered. If one is found, H095 attempts to amplify it by disjoint union; theta additivity under the exact H093 normalization remains a written proof obligation.

### H097: certificate existence remains open

Exact replay is solved for the registered format. Existence of polynomial-size rational certificates is isolated under explicit inverse-polynomial Slater and objective margins.

Read [`docs/C011_EXACT_THETA_CERTIFICATES.md`](docs/C011_EXACT_THETA_CERTIFICATES.md).

## Current inventory

After C011, JANUS contains **93 live hypotheses** and **4 terminal historical nodes**. These counts are inventory, not evidence or a completion percentage.

## Terminal results retained

- [`H016 — DESTROYED`](proof_attempts/H016/REFUTATION.md): projected polynomial d-DNNF contradicts unconditional DNNF lower bounds.
- [`H018 — REJECTED`](proof_attempts/H018/FORMULATION_FAILURE.md): missing decision correctness made the statement vacuous.
- [`H048 — DESTROYED`](proof_attempts/H048/REFUTATION.md): ordinary CDCL remains inside Resolution.
- [`H074 — REJECTED`](proof_attempts/H074/FORMULATION_FAILURE.md): the theta observable interface was undefined and answer-dependent.

No JANUS result currently resolves `P` versus `NP`.

## Contribution rule

A contribution must shorten a proof route, expose a falsification mechanism, or improve independent reproducibility. New descendants must inherit from the organism rather than bypass it.
