# JANUS Fundamentum — Current Public Research Status

This file is the public status entry point for the repository. It separates the active proof-search mainline from the admitted A3 publication track so that research progress is not confused with a claim that `P` versus `NP` has been resolved.

## Global claim ceiling

```text
P_VS_NP = OPEN
P_EQ_NP_PROVED = FALSE
P_NE_NP_PROVED = FALSE
GLOBAL_WORLD_PRIORITY = NOT_CLAIMED
```

JANUS is a proof-search laboratory. A surviving hypothesis is not a theorem until it crosses its declared proof/admission gates, and an admitted theorem is not automatically a result about unrestricted `P` versus `NP`.

---

## Track A — admitted A3 endpoint-compression / ternary-DP theorem

The strongest publication-ready mathematical result currently carried by the repository is the A3 theorem track.

### Frozen theorem authority

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

The theorem concerns finite-field subspace arrangements with `k` distinct geometric subspace classes and arbitrary positive multiplicities. If `s` classes are singleton and `r` classes are repeated (`s+r=k`), the admitted exact compressed state count is

```text
2^s * 3^r
```

and the admitted exact transition count is

```text
s*2^(s-1)*3^r + 2r*2^s*3^(r-1).
```

Using the rank identity

```text
lambda(P,S) = rho(S) + rho(K\P) - rho(K),
```

with `2^k` subset-rank preprocessing, the combinatorial dynamic-programming work is

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

### Publication reproducibility

The current immutable publication target is `811d954e52296893898062d9abea7aaf572629be`.

```text
PUBLICATION_MANIFEST_V1_0 = FROZEN_VERIFIED
SAME_HEAD_CLEAN_BUILD_REPRODUCIBILITY = PASS
CROSS_RUNNER_REPRODUCIBILITY = PASS
CROSS_ENVIRONMENT_REPRODUCIBILITY = NOT_ESTABLISHED
EXTERNAL_INDEPENDENT_REPLICATION = NOT_ESTABLISHED
```

Canonical deterministic PDF SHA-256:

```text
a3a6e87376d38e9336d9e101640ebfaf5f41499a885f0477e2f46b88cf3cd5e4
```

Publication and review carriers:

- PR #159 — publication manifest / immutable publication target: https://github.com/Hawkar-usls/Janus-Fundamentum/pull/159
- PR #160 — verification-only cross-runner reproduction: https://github.com/Hawkar-usls/Janus-Fundamentum/pull/160
- PR #161 — external-inquiry / literature-audit handoff: https://github.com/Hawkar-usls/Janus-Fundamentum/pull/161

These PRs have intentionally separate roles. PR #159 is open and ready for review; #160 and #161 are draft evidence/review carriers and are not part of the theorem authority itself.

### Novelty ceiling

```text
NOVELTY = N3_NOVELTY_CANDIDATE
SEARCH_STRENGTH = N3_EXHAUSTIVELY_SEARCHED_WITHIN_DECLARED_PROTOCOL
HISTORICAL_WORLD_PRIORITY = NOT_CLAIMED
UNIVERSAL_LITERATURE_ABSENCE = NOT_PROVED
WORLD_NOVELTY_N4 = NOT_ESTABLISHED
```

The next meaningful scientific step is external mathematical review, independent reproduction, and bibliographic challenge—not another internally generated novelty promotion.

See [`A3_PUBLICATION_TRACK.md`](A3_PUBLICATION_TRACK.md).

---

## Track B — active mainline proof search: C023 JANUS-FC_local

The default `main` research content currently terminates at the C023 Formula-Caching calculus baseline:

```text
C023_RESEARCH_BASELINE
= f0ffb9b7afdd1797c4c6648b32f5ee5c5a80a9f0

C023_STATUS
= MACHINE_CHECKABLE_FINITE_CALCULUS
  / REASON_INTERFACE_UNDER_ATTACK
  / ASYMPTOTIC_LOWER_BOUND_OPEN

C023_ASYMPTOTIC_LOWER_BOUND = OPEN
```

C023 formalizes the exact `JANUS-FC_local` cached-policy proof interface around Policy-0A. The current finite evidence includes exact serialized replay, cache-context attacks, MAJ3-K4 profiling, graph-tautology probes, and explicit reason-reuse measurements.

What C023 does **not** establish:

```text
FORMULA_CACHING_GENERAL_POLYNOMIALITY = NOT_PROVED
FORMULA_CACHING_GENERAL_EXPONENTIAL_LOWER_BOUND = NOT_PROVED
C022_NO_CACHE_LOWER_BOUND_TRANSFER_TO_POLICY_0A = NOT_PROVED
C023_ASYMPTOTIC_LOWER_BOUND = OPEN
P_VS_NP = OPEN
```

The current open gates are theorem-level: simulation/robustness of the local Resolution pass, reusable-reason extraction, and asymptotic lower bounds for the exact calculus.

See [`C023_FORMULA_CACHING_CALCULUS.md`](C023_FORMULA_CACHING_CALCULUS.md).

---

## How the two tracks relate

They must not be conflated.

```text
A3 publication track
= admitted scoped algorithmic theorem
= publication/review phase

C023 mainline track
= active proof-search calculus
= unresolved asymptotic lower-bound program

P vs NP
= OPEN
```

The A3 theorem is a surviving, admitted result that emerged from the broader JANUS research program. C023 remains an active attack surface for direct proof-complexity routes. Neither track is licensed to inherit claims from the other without an explicit theorem and verification boundary.

---

## Public contribution priorities

The most valuable external contributions are:

1. a mathematical counterexample or hidden assumption in the A3 theorem/proof;
2. an independently authored clean-room reproduction of the A3 endpoint DP;
3. an earlier theorem that directly subsumes the admitted A3 result;
4. a counterexample or simulation theorem for `JANUS-FC_local`;
5. a rigorous asymptotic lower bound or a proof that a proposed lower-bound route fails;
6. verifier, provenance, or reproducibility defects with concrete replay instructions.

Negative results are first-class research outputs.
