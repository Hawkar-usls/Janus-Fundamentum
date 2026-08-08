# JANUS Fundamentum

> **Generate hypotheses. Attack them. Preserve survivors. Never confuse survival with proof.**

JANUS Fundamentum is a public, machine-readable proof-search laboratory for reproducible research in computational complexity, proof complexity, matroid/subspace-arrangement algorithms, and adjacent verification problems.

Its long-term target includes `P` versus `NP`, but the repository does **not** claim that `P = NP` or `P != NP` has been proved.

```text
P_VS_NP = OPEN
```

The repository now has two public research fronts that must be kept separate:

1. **A3 publication track** — an admitted scoped endpoint-compression / ternary-DP theorem, now in publication and external-review handoff.
2. **C023 mainline proof-search track** — the active `JANUS-FC_local` Formula-Caching calculus, where the asymptotic lower-bound program remains open.

For the canonical public snapshot, see [`docs/CURRENT_RESEARCH_STATUS.md`](docs/CURRENT_RESEARCH_STATUS.md).

---

## A3 publication track — admitted theorem

The strongest publication-ready mathematical result currently carried by JANUS is the A3 endpoint-compression theorem for finite-field subspace arrangements with `k` distinct geometric subspace classes and arbitrary positive multiplicities.

If `s` classes are singleton and `r` classes are repeated (`s+r=k`), the admitted compressed state count is

```text
2^s * 3^r
```

with exact transition count

```text
s*2^(s-1)*3^r + 2r*2^s*3^(r-1).
```

Using

```text
lambda(P,S) = rho(S) + rho(K\P) - rho(K)
```

and `2^k` subset-rank preprocessing, the admitted combinatorial DP work is

```text
O(k * 3^k).
```

Current classification:

```text
A3_KCLASS_ENDPOINT_COMPRESSION = ES5
A3_KCLASS_ENDPOINT_DP = ES5
ALGORITHMIC_FPT_IN_K = ESTABLISHED_IN_STATED_SCOPE
GENERAL_MATROID_PATHWIDTH_COMPLEXITY = UNCHANGED
P_VS_NP = OPEN
```

### Frozen theorem / publication identities

```text
THEOREM_EVIDENCE_HEAD
= 5ee79fc82613f24e621595afa0119312a2f52660

STRENGTHENED_PROOF_HEAD
= 0e505f460ec63cbb358c7f66cde18ab8a52684d3

ENDPOINT_COMPRESSION_PROOF_HEAD
= 6ca16581eff08103698250b09ea51aeccd9f800b

PUBLICATION_TARGET
= 811d954e52296893898062d9abea7aaf572629be
```

The deterministic publication PDF has SHA-256:

```text
a3a6e87376d38e9336d9e101640ebfaf5f41499a885f0477e2f46b88cf3cd5e4
```

and the publication pipeline records:

```text
PUBLICATION_MANIFEST_V1_0 = FROZEN_VERIFIED
SAME_HEAD_CLEAN_BUILD_REPRODUCIBILITY = PASS
CROSS_RUNNER_REPRODUCIBILITY = PASS
CROSS_ENVIRONMENT_REPRODUCIBILITY = NOT_ESTABLISHED
EXTERNAL_INDEPENDENT_REPLICATION = NOT_ESTABLISHED
```

Publication/review surfaces:

- [PR #159 — A3 Publication Manifest v1.0](https://github.com/Hawkar-usls/Janus-Fundamentum/pull/159)
- [PR #160 — cross-runner reproduction carrier](https://github.com/Hawkar-usls/Janus-Fundamentum/pull/160)
- [PR #161 — external-inquiry / literature-audit handoff](https://github.com/Hawkar-usls/Janus-Fundamentum/pull/161)
- [`docs/A3_PUBLICATION_TRACK.md`](docs/A3_PUBLICATION_TRACK.md)

### Novelty ceiling

The current literature classification is intentionally narrower than a world-priority claim:

```text
NOVELTY = N3_NOVELTY_CANDIDATE
SEARCH_STRENGTH = N3_EXHAUSTIVELY_SEARCHED_WITHIN_DECLARED_PROTOCOL
HISTORICAL_WORLD_PRIORITY = NOT_CLAIMED
UNIVERSAL_LITERATURE_ABSENCE = NOT_PROVED
WORLD_NOVELTY_N4 = NOT_ESTABLISHED
```

The next meaningful gate is independent mathematical review, clean-room reproduction, or a directly subsuming prior result.

---

## Active mainline — C023 JANUS-FC_local

The current default-branch research baseline is:

```text
C023_RESEARCH_BASELINE
= f0ffb9b7afdd1797c4c6648b32f5ee5c5a80a9f0
```

C023 formalizes the exact Formula-Caching interface used by Policy-0A. Its status is:

```text
MACHINE_CHECKABLE_FINITE_CALCULUS
/ REASON_INTERFACE_UNDER_ATTACK
/ ASYMPTOTIC_LOWER_BOUND_OPEN
```

The cached judgement has the form

```text
canonical residual F  =>  Boolean answer b
```

and is reusable only when the current residual is byte-for-byte identical after exhaustive unit propagation and the cached state completed earlier in the deterministic depth-first execution.

Finite evidence currently includes:

- separately replayed serialized certificates;
- explicit cache-diamond controls;
- MAJ3-lifted K4 profiling;
- context-sensitive reason-reuse audits;
- graph-tautology experiments through order 9;
- weakening/subsumption ablations;
- explicit local-Resolution event accounting.

For example, the MAJ3-K4 fixture records:

```text
recursive calls:                 4,117
unique exact residual states:    2,427
cache hits:                        888
local Resolution events:        37,432
charged certificate records:    50,796
```

These are finite machine-checked facts, not an asymptotic separation theorem.

C023 currently does **not** prove that Formula Caching is polynomial or exponential on general SAT, does not transfer the C022 no-cache lower bound to Policy-0A, and does not resolve `P` versus `NP`.

Read [`docs/C023_FORMULA_CACHING_CALCULUS.md`](docs/C023_FORMULA_CACHING_CALCULUS.md).

---

## Research discipline

JANUS uses a few permanent rules.

1. Computational claims require committed code, fixed inputs, expected outputs, and replayable evidence.
2. A hypothesis must name its proof role, parents, attack surface, and next gate.
3. New mathematics attacks the existing graph before expanding it.
4. Positive finite examples do not become asymptotic theorems by accumulation.
5. Exact verification is not the same as efficient discovery.
6. A machine-checked result is not automatically a novelty claim.
7. A scoped theorem is not automatically a result about unrestricted `P` versus `NP`.
8. Publication artifacts are human-readable projections of frozen mathematical authority, not replacements for it.
9. Negative results and counterexamples are preserved as first-class outputs.
10. External review is not simulated by another internally authored PASS.

---

## Repository map

The default branch currently exposes the active proof-search and public-navigation surfaces:

```text
Janus-Fundamentum/
├── README.md
├── CONTRIBUTING.md
├── docs/
│   ├── CURRENT_RESEARCH_STATUS.md
│   ├── A3_PUBLICATION_TRACK.md
│   ├── C023_FORMULA_CACHING_CALCULUS.md
│   └── ... cycle and audit notes
├── experiments/
│   ├── direct/
│   └── theta/
├── proof_attempts/
├── registry/
├── tools/
└── .github/
    ├── ISSUE_TEMPLATE/
    └── workflows/
```

The frozen A3 publication package and theorem/admission objects live on dedicated research/publication branches. The navigation documents on `main` intentionally link to their immutable PR/commit surfaces instead of pretending those branch-only directories are present on the default branch.

---

## Reproduce the active mainline

A compact C023 replay starts with:

```bash
python experiments/direct/janus_tear_policy0a_fc_trace.py
python experiments/direct/janus_tear_policy0a_fc_serialized_verifier.py
python experiments/direct/janus_tear_policy0a_fc_proof_system.py
python experiments/direct/janus_tear_policy0a_reason_reuse_audit_v2.py
python experiments/direct/janus_tear_policy0a_graph_tautology_probe.py
python experiments/direct/janus_tear_policy0a_gt_resolution_ablation.py
```

For the A3 theorem/publication track, review the exact target and evidence surfaces linked from [`docs/A3_PUBLICATION_TRACK.md`](docs/A3_PUBLICATION_TRACK.md) rather than assuming the default branch contains the frozen publication package.

---

## What would be valuable now?

The preferred contribution is not agreement.

It is one of:

- a counterexample to the admitted A3 endpoint-compression argument;
- an independently authored implementation of the A3 DP;
- an earlier theorem that directly subsumes A3;
- a proof or disproof of a C023 open simulation/lower-bound gate;
- a verifier/provenance defect with exact replay instructions;
- a cleaner theorem that narrows or replaces one of the current conjectural routes.

If a result breaks, preserve the break.

That is how JANUS progresses.

---

## Scientific boundary

```text
A3_SCOPED_ALGORITHMIC_THEOREM = ADMITTED
A3_EXTERNAL_REPLICATION = NOT_ESTABLISHED
A3_WORLD_NOVELTY_N4 = NOT_ESTABLISHED
C023_ASYMPTOTIC_LOWER_BOUND = OPEN
P_VS_NP = OPEN
```

**Generate hypotheses. Attack them. Preserve survivors. Never confuse survival with proof.**
