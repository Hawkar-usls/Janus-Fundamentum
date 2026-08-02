# JANUS Proof Search Laboratory

> **Generate hypotheses. Attack them. Preserve survivors. Never confuse survival with proof.**

JANUS is a public, machine-readable laboratory for reproducible research around computational complexity, with `P` versus `NP` as its long-term target.

This repository does **not** claim that `P = NP` or `P != NP` has been proved.

## Laboratory laws

1. **Independent reproducibility.** Computational claims require committed code, fixed inputs, expected outputs, and hashes.
2. **Proof-directed admission.** From `H030`, every hypothesis names its proof role, next gate, and attacks.
3. **Inherited progress.** From `H060`, every child names older parents and a material delta.
4. **Inversion before expansion.** New mathematics first attacks the existing graph.
5. **Terminal honesty.** Pressure is not converted into a graveyard result without a decisive theorem, counterexample, or formulation failure.
6. **Answer-independent observables.** Canonical profiles and exact certificates may not contain hidden SAT labels.
7. **Verification is not existence.** An exact verifier does not imply that a short certificate exists or can be found efficiently.
8. **Historical campaigns stay historical.** Later descendants and terminal shadows do not rewrite earlier attack snapshots.

## Research states

`PROPOSED -> UNDER_ATTACK -> OPEN -> FORMALIZING -> INDEPENDENT_REPRODUCTION -> PEER_REVIEW -> PROVED`

`OPEN` means only that registered attacks have not destroyed the exact statement. `PROVED` requires R5 formal and independent verification.

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
python experiments/theta/complete_3cnf_collision.py --self-test
python experiments/theta/complete_3cnf_family.py --self-test
```

# Current status — C013

C013 attacks the pressured C012 routes until they reach a terminal formulation failure, a narrower descendant, or a named open barrier.

```text
NEW DESCENDANTS             6   H098-H103
CURRENT-CYCLE ATTACKS      44   A287-A330
TERMINAL REJECTIONS         6
LIVE HYPOTHESES            93
TERMINAL HISTORICAL NODES  10
```

## Exact theta breakthrough

The finite collision sought by `H096` now has an explicit rational witness.

### UNSAT side

Take all eight width-three clauses on `x1,x2,x3`. Every assignment falsifies exactly one clause, so the conflict graph has:

```text
clause target = 8
alpha         = 7
theta         = 8
```

### SAT side

Adjoin one shared positive literal `x4` to the same eight sign patterns. Setting `x4=true` gives:

```text
clause target = 8
alpha         = 8
theta         = 8
```

Both theta values are certified by exact rational primal-dual bundles and exact rational permuted `LDL^T` positivity certificates. No floating-point SDP result is trusted.

```bash
python experiments/theta/complete_3cnf_collision.py --self-test
```

Expected result:

```text
JANUS_COMPLETE_3CNF_THETA_COLLISION = PASS
```

The UNSAT primal matrix is generated from 12 orbits of the 48 signed-coordinate automorphisms. Its exact nonzero spectrum is:

```text
1/3  multiplicity 1
1/6  multiplicity 3
1/18 multiplicity 3
```

Read [`proof_attempts/H096/EXACT_COLLISION.md`](proof_attempts/H096/EXACT_COLLISION.md).

## Infinite explicit family

For `r` variable-disjoint copies, the primal matrix is

```text
(1/r) J_r tensor X
```

and the direct dual objective is `8r`. Thus the SAT and UNSAT sides both have exact theta value `8r`, while their alpha labels remain opposite.

```bash
python experiments/theta/complete_3cnf_family.py --self-test
```

This is encoded as `H098-H099`. It is an explicit limitation of the standard first Lovasz-theta SAT relaxation, not a solution of `P` versus `NP`.

## Six terminal formulation failures

C013 rejects:

```text
H001 H002 H003 H004 H019 H070
```

- `H001-H004` and `H070` allow an unrestricted polynomial transformer to solve SAT first and encode only the answer.
- `H019` does not fix the syntax, denotation size, original-variable support, or composition semantics of an interface symbol.

Their useful ideas survive only through restricted descendants:

```text
H001/H009 -> H100 potential-decreasing local compiler
H017      -> H101 restriction-robust mixed residual generator
H019      -> H102 typed bounded-support interface elimination
H070      -> H103 one-pass local theta-gap compiler
```

Read [`proof_attempts/C013/CIRCULARITY_AND_SPECIFICATION.md`](proof_attempts/C013/CIRCULARITY_AND_SPECIFICATION.md).

## Where the attack finally stops

The unresolved frontier is now concentrated in:

1. explicit lower bounds for full Extended Frege, full IPS, TC0-Frege, unrestricted Stabbing Planes/CP, and recursive extension-PC;
2. pseudoexpectation transport through arbitrary fixed local gadgets;
3. a deterministic restriction-robust mixed XOR/non-affine generator;
4. a complete DNNF transfer or escape theorem for typed interface elimination;
5. conditioned existence of polynomial-bit exact SDP certificates.

The five incompatible duels remain unresolved:

```text
H006 vs H011
H007 vs H014
H012 vs H013
H022 vs H023
H024 vs H025
```

## Historical C012 sweep

The 93×12 C012 campaign remains a frozen snapshot. Its validator now checks the declared `H001-H097` historical state rather than incorrectly treating later terminal decisions as retroactive omissions.

Read [`docs/C013_DEEP_ATTACK.md`](docs/C013_DEEP_ATTACK.md).

## Terminal results retained

- `H016 — DESTROYED`: projected polynomial d-DNNF contradicts unconditional DNNF lower bounds.
- `H018 — REJECTED`: missing decision correctness made the formulation vacuous.
- `H048 — DESTROYED`: ordinary CDCL remains inside Resolution.
- `H074 — REJECTED`: the theta observable interface was undefined.
- `H001-H004`, `H019`, `H070 — REJECTED`: C013 circularity or specification failures.

No JANUS result currently resolves `P` versus `NP`.
