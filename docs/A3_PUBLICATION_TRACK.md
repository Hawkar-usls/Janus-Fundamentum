# A3 Publication Track — Endpoint Compression and Ternary Dynamic Programming

This document is a public navigation layer for the admitted A3 theorem carried in the publication branches of `Janus-Fundamentum`.

It is **not** a new source of mathematical authority. The frozen theorem/proof objects and their admission receipts remain authoritative for the admitted result.

## Scientific scope

The admitted theorem applies to finite-field subspace arrangements with `k` distinct geometric subspace classes and arbitrary positive multiplicities.

Let:

- `s` = number of singleton geometric classes;
- `r` = number of repeated geometric classes;
- `s + r = k`.

The compressed endpoint state space has exact size

```text
2^s * 3^r.
```

The exact transition count is

```text
s*2^(s-1)*3^r + 2r*2^s*3^(r-1).
```

The boundary-rank identity used by the dynamic program is

```text
lambda(P,S) = rho(S) + rho(K\P) - rho(K).
```

After `2^k` subset-rank preprocessing, the admitted combinatorial dynamic-programming work is

```text
O(k * 3^k).
```

The result is therefore fixed-parameter tractable in the number `k` of distinct geometric subspace classes, within the stated scope.

## Why ternary states appear

A singleton class has only two endpoint-relevant conditions:

```text
unused / used
```

A repeated class has three endpoint-relevant conditions:

```text
none / partial / all
```

This gives the mixed state count `2^s 3^r` and, in the all-repeated case, the familiar `3^k` frontier.

The theorem does not say that arbitrary matroid path-width is polynomial-time solvable. It says that this repeated-class structure admits an exact endpoint compression parameterized by the number of distinct geometric classes.

## Frozen authority and publication identities

```text
THEOREM_EVIDENCE_HEAD
= 5ee79fc82613f24e621595afa0119312a2f52660

STRENGTHENED_PROOF_HEAD
= 0e505f460ec63cbb358c7f66cde18ab8a52684d3

ENDPOINT_COMPRESSION_PROOF_HEAD
= 6ca16581eff08103698250b09ea51aeccd9f800b

PUBLICATION_CONTENT_HEAD
= 86a3262f9c157acb6ae795325f3c7ba6235f1480

PROVENANCE_PDF_VERIFIER_HEAD
= cea202d74d65c8b617ea05f721617b575908f30b

FREEZE_RECEIPT_HEAD
= 7bf7c618ec377418c5f69718b7b9c4df4cf5d643

DETERMINISTIC_BUILD_VERIFIER_HEAD
= 811d954e52296893898062d9abea7aaf572629be
```

Current publication target:

```text
811d954e52296893898062d9abea7aaf572629be
```

Publication PR:

https://github.com/Hawkar-usls/Janus-Fundamentum/pull/159

## Reproducibility receipt

On the immutable publication target:

```text
PUBLICATION_MANIFEST_V1_0 = FROZEN_VERIFIED
PAPER_DRAFT_V0_2 = PDF_BUILD_AND_PROVENANCE_BINDING_VERIFIED
SAME_HEAD_CLEAN_BUILD_REPRODUCIBILITY = PASS
```

Canonical PDF SHA-256:

```text
a3a6e87376d38e9336d9e101640ebfaf5f41499a885f0477e2f46b88cf3cd5e4
```

A separate cross-runner harness reproduced the same PDF on two distinct GitHub-hosted Ubuntu 24.04 workers in different Azure regions:

```text
CROSS_RUNNER_REPRODUCIBILITY = PASS
CROSS_ENVIRONMENT_REPRODUCIBILITY = NOT_ESTABLISHED
EXTERNAL_INDEPENDENT_REPLICATION = NOT_ESTABLISHED
```

Verification carrier:

https://github.com/Hawkar-usls/Janus-Fundamentum/pull/160

Cross-runner reproducibility is a build-reproducibility statement. It is not independent scientific reproduction of the theorem.

## Literature / novelty boundary

The current publication protocol records:

```text
NOVELTY = N3_NOVELTY_CANDIDATE
SEARCH_STRENGTH = N3_EXHAUSTIVELY_SEARCHED_WITHIN_DECLARED_PROTOCOL
EXACT_EQUIVALENT_RESULT_FOUND_IN_DECLARED_PROTOCOL = FALSE
DIRECT_DEFINITIONAL_COROLLARY_FOUND = FALSE
UNIVERSAL_LITERATURE_ABSENCE_PROVED = FALSE
HISTORICAL_WORLD_PRIORITY = NOT_CLAIMED
WORLD_NOVELTY_N4 = NOT_ESTABLISHED
```

The external-inquiry supplement expands the targeted literature matrix and preserves this ceiling rather than promoting it.

External inquiry / literature handoff:

https://github.com/Hawkar-usls/Janus-Fundamentum/pull/161

A contacted expert reporting that they have not seen the result would be useful bibliographic evidence, but it would not by itself establish historical world priority.

## Claim ceiling

The publication-safe status is:

```text
A3_KCLASS_ENDPOINT_COMPRESSION = ES5
A3_KCLASS_ENDPOINT_DP = ES5
ALGORITHMIC_FPT_IN_K = ESTABLISHED_IN_STATED_SCOPE
GENERAL_MATROID_PATHWIDTH_COMPLEXITY = UNCHANGED
KNOWN_GENERAL_NP_HARDNESS = NOT_OVERTURNED
EXTERNAL_INDEPENDENT_REPLICATION = NOT_ESTABLISHED
WORLD_NOVELTY_N4 = NOT_ESTABLISHED
P_VS_NP = OPEN
```

Forbidden public upgrades without new evidence include:

```text
"P vs NP solved"
"general matroid path-width solved"
"world first"
"historical priority proved"
"externally replicated"
```

## What external reviewers should try to break

A useful review should attack the mathematical content rather than the presentation layer. In particular:

1. find two multiplicity profiles that the endpoint compression incorrectly identifies;
2. produce a counterexample to the endpoint sufficiency argument;
3. find a transition omitted by the exact transition formula;
4. challenge the rank-identity use in the stated subspace-arrangement scope;
5. independently implement the DP from the theorem statement and compare against exhaustive small instances;
6. identify a directly subsuming prior theorem;
7. distinguish a theorem/proof defect from a publication-build or provenance defect.

The preferred next evidence is external falsification or clean-room reproduction.
