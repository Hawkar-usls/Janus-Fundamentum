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
6. **Answer-independent observables.** Canonical experimental profiles may not contain SAT labels, exact alpha, or other answer-dependent diagnostics.

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
- `registry/lineage-reverse-c010.json` — append-only parent-to-child edges for C010;
- `registry/inversion-tests*.json` — reusable backside tests;
- `registry/inversion-matrix-c010.json` — current cumulative 40×40 matrix;
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
```

## Current status — C010

C010 compresses broad theta claims into narrower algebraic obligations and hardens the experimental interface.

- **8 descendants:** `H084-H091`;
- **40 attacks:** `A217-A256`;
- **8 inherited targets re-attacked:** `H075-H079`, `H081-H083`;
- **no terminal result**;
- **40×40 inversion matrix:** 1600 logical cells;
- **32 of 40 matrix hypotheses inherited** from earlier cycles.

### Main proof-compression chain

```text
H075 coordinate symmetries
  -> H084 exact monomial transport
  -> H085 bounded-depth functional pullback
  -> H086 projection-resource classification

H078 canonical bounded-level twins
  -> H087 exact level-one target

H079 local theta barrier
  -> H088 pseudoexpectation gadget transport

H083 restriction-robust mixed family
  -> H090 explicit generator
  -> H091 bounded-degree parity-proof transfer
```

### H084: checkable algebraic core

`proof_attempts/H075/SYMMETRY_TRANSPORT.md` derives the exact change-of-basis matrix for coordinate permutations and complementations. `symmetry_transport.py` checks inverse identities over the integers for deterministic finite fixtures.

This does not promote H075 or H084 to `PROVED`; the universal proof still awaits independent review and final bit accounting.

### H085/H086: functional definitions versus projection

C010 now separates two operations that earlier language risked conflating:

- bounded-depth **functional substitution**, where certificate pullback may be proved compositionally;
- **existential projection**, where nonfunctional fibers can erase structure.

This split is the main route toward resolving H076 versus H077.

### H087: canonical level-one twin target

The canonical profile now:

- validates DIMACS semantics, including empty clauses;
- performs exact variable relabeling only for at most eight used variables;
- refuses larger unsupported canonicalization claims;
- excludes exact alpha and SAT labels.

Answer-dependent diagnostics live only in `experiments/theta/diagnostics.py`.

### H089: exact verification, not discovery

`rational_gram_verifier.py` checks supplied rational Gram factors and threshold margins with exact arithmetic. It does not solve an SDP or imply that short rational certificates exist.

Read [`docs/C010_PROOF_COMPRESSION.md`](docs/C010_PROOF_COMPRESSION.md).

## Current inventory

After C010, JANUS contains **87 live hypotheses** and **4 terminal historical nodes**. These counts are inventory, not evidence or a completion percentage.

## Terminal results retained

- [`H016 — DESTROYED`](proof_attempts/H016/REFUTATION.md): projected polynomial d-DNNF contradicts unconditional DNNF lower bounds.
- [`H018 — REJECTED`](proof_attempts/H018/FORMULATION_FAILURE.md): missing decision correctness made the statement vacuous.
- [`H048 — DESTROYED`](proof_attempts/H048/REFUTATION.md): ordinary CDCL remains inside Resolution.
- [`H074 — REJECTED`](proof_attempts/H074/FORMULATION_FAILURE.md): the theta observable interface was undefined and answer-dependent.

No JANUS result currently resolves `P` versus `NP`.

## Contribution rule

A contribution must shorten a proof route, expose a falsification mechanism, or improve independent reproducibility. New descendants must inherit from the organism rather than bypass it.
