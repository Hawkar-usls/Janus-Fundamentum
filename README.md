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
8. **Total means total.** A total-attack campaign must cover every current live hypothesis and exclude every terminal shadow.

## Research states

`PROPOSED -> UNDER_ATTACK -> OPEN -> FORMALIZING -> INDEPENDENT_REPRODUCTION -> PEER_REVIEW -> PROVED`

`OPEN` means only that registered attacks have not destroyed the exact statement. `FORMALIZING` is not proof. `PROVED` requires R5 formal and independent verification.

## Machine-readable organism

- `registry/hypotheses*.json` — historical hypothesis snapshots;
- `registry/attacks*.json` — theorem-specific falsification attempts;
- `registry/attack-protocols-c012.json` — reusable total-sweep attacks;
- `registry/total-attack-sweep-c012.json` — the current 93×12 campaign;
- `registry/references*.json` — primary-source context;
- `registry/graveyard*.json` — permanent terminal records;
- `registry/observations*.json` — reductions and methodological findings;
- `registry/journal*.json` — chronological cycles;
- `registry/genealogy*.json` — child-to-parent proof routes;
- `registry/lineage-reverse-c011.json` — append-only parent-to-child edges for C011 descendants;
- `registry/inversion-tests*.json` — reusable backside tests;
- `registry/inversion-matrix-c011.json` — cumulative 46×46 focused matrix;
- `registry/schema.json` — policy and validation contract.

## Validate the organism

```bash
python tools/validate_registry.py
python tools/validate_lineage.py
python tools/validate_inversion_matrix.py
python tools/validate_cycle_pressure.py
python tools/validate_total_attack_sweep.py
python experiments/theta/conflict_graph.py --self-test
python experiments/theta/canonical_profile.py --self-test
python experiments/theta/symmetry_transport.py --self-test
python experiments/theta/rational_gram_verifier.py --self-test
python experiments/theta/rational_ldl.py --self-test
python experiments/theta/lovasz_theta_certificate.py --self-test
python experiments/theta/disjoint_union.py --self-test
python experiments/theta/theta_collision_bundle.py --self-test
```

## Current status — C012

C012 pauses expansion and attacks every live hypothesis.

```text
LIVE HYPOTHESES ATTACKED   93
ATTACK PROTOCOLS           12
LOGICAL ATTACK CELLS     1116
CLEAN SURVIVORS             73
CONFLICTED SURVIVORS         10
PRESSURED SURVIVORS          10
DESTROYED OR REJECTED         0
```

### Pressured survivors

```text
H001 H002 H003 H004 H009 H017 H019 H070 H081 H089
```

The active pressure is concentrated in solve-and-encode circularity, locality that may still simulate global computation, underspecified residual/interface languages, failure of the ordinary first-theta route, and the gap between exact certificate verification and short-certificate existence.

### Mutually incompatible survivors

```text
H006  vs H011
H007  vs H014
H012  vs H013
H022  vs H023
H024  vs H025
```

At least one member of every pair must eventually fail. C012 did not determine which member.

### What survived means

A clean `SURVIVED` cell means only that one standardized audit did not produce a decisive contradiction. It is not evidence that the hypothesis is true, likely, or novel.

Read [`docs/C012_TOTAL_ATTACK_SWEEP.md`](docs/C012_TOTAL_ATTACK_SWEEP.md).

## Strongest focused branch retained from C011

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

The executable theta tools use exact rational arithmetic. No positive theta-collision seed is currently registered, and exact verification does not imply efficient discovery.

## Current inventory

After C012, JANUS contains **93 live hypotheses** and **4 terminal historical nodes**. These counts are inventory, not evidence or a completion percentage.

## Terminal results retained

- [`H016 — DESTROYED`](proof_attempts/H016/REFUTATION.md): projected polynomial d-DNNF contradicts unconditional DNNF lower bounds.
- [`H018 — REJECTED`](proof_attempts/H018/FORMULATION_FAILURE.md): missing decision correctness made the statement vacuous.
- [`H048 — DESTROYED`](proof_attempts/H048/REFUTATION.md): ordinary CDCL remains inside Resolution.
- [`H074 — REJECTED`](proof_attempts/H074/FORMULATION_FAILURE.md): the theta observable interface was undefined and answer-dependent.

No JANUS result currently resolves `P` versus `NP`.

## Contribution rule

A contribution must shorten a proof route, expose a falsification mechanism, or improve independent reproducibility. New descendants must inherit from the organism rather than bypass it.
