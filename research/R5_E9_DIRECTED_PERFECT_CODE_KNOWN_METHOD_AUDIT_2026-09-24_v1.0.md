# R5 E9 — Directed Perfect Code Known-Method Audit

Date: 2026-09-24

Authority: SOURCE_AUDIT_ONLY__HOLD_NEW_MATH

Governance parent:
`JANUS_GLOBAL_PREMATH_NO_DUPLICATION_GATE_2026-09-24_v1.0`

## G0 — Exact frozen object

Current JANUS residual object:

Input:
- a connected finite coordinate set Omega;
- two permutations P,Q generating a transitive action;
- directed 2-valent permutation/Schreier digraph with arcs induced by P,Q;
- phase-inconsistent residual after cheap JANUS preprocessing.

Decision problem:

find S subset Omega such that

Omega = S disjoint-union P^{-1}S disjoint-union Q^{-1}S.

Equivalent language:
- directed perfect code;
- efficient domination / exact domination;
- exact tiling/factorization by the three-element neighborhood shape;
- Boolean equation (I+P+Q)x=1;
- cubic exact-cover normal form.

Current residual promises include:
- noncommuting P,Q;
- Z3 gain/phase test fails;
- no one-dimensional zero-mode sector;
- low-nullity and known-P preprocessing already removed.

## G1 — Internal anti-duplication audit

Relevant internal predecessors reviewed:

- R5_B1B1C5B2B2_E8_CORPUS_FIRST_MECHANISM_SYNTHESIS_DOCTRINE;
- R5_B1B1C5B2B2_E8_AIG_QE_AND_INTERNAL_ANTI_DUPLICATION_SOURCE_AUDIT;
- R5_E9_THREE_TRANSLATE_TILING_NORMAL_FORM;
- R5_E9_COMMUTING_TWO_PERMUTATION_KERNEL_ISLAND;
- R5_E9_Z3_PHASE_COBBOUNDARY_ISLAND;
- R5_E9_CUBIC_KERNEL_WORD_NORMAL_FORM.

Internal conclusion:

there is no older separate JANUS perfect-code program found in the reviewed corpus;
however the latest E9 objects themselves independently rederive several known external mechanisms and must be reclassified/source-bound rather than treated as novelty.

## G2 — Canonical external naming

Canonical names:

1. directed perfect code;
2. efficient dominating set in a digraph;
3. perfect code in a 2-valent Cayley/permutation/Schreier digraph;
4. group tiling / factorization;
5. gain/voltage graph potential for the Z3 phase subsystem.

Adjacent fields:
- domination/perfect codes;
- Cayley and Schreier graphs/digraphs;
- finite group factorizations/tilings;
- gain graphs;
- permutation representations.

## G3 — Sources already checked

### S1 — Yu, Yang, Fan, Ma (2024)

Shilong Yu, Yuefeng Yang, Yushuang Fan, Xuanlong Ma,
`Perfect codes in 2-valent Cayley digraphs on abelian groups`,
Discrete Applied Mathematics 357 (2024), 236-240,
DOI 10.1016/j.dam.2024.06.002; arXiv:2310.19017.

Source claim:
strongly connected 2-valent Cayley digraphs on abelian groups admitting a perfect code are completely classified, and all perfect codes are determined.

JANUS consequence:
`PQ=QP / transitive abelian quotient` is SOURCE-BOUND territory; JANUS character/Fourier proof is an independent rederivation/corollary, not novelty.

### S2 — Wang and Zhang (2023)

`Perfect codes in vertex-transitive graphs`,
Journal of Combinatorial Theory, Series A 196 (2023), 105737,
DOI 10.1016/j.jcta.2023.105737.

Source scope:
perfect codes in vertex-transitive graphs through coset-graph / pair (G,H) formulations, with emphasis on subgroup perfect codes.

JANUS consequence:
coset/Schreier language is established prior art; this source does not by itself close arbitrary non-subgroup directed two-permutation existence.

### S3 — Cameron, Yap, Zhou (2026)

`Perfect codes in Cayley graphs of abelian groups`,
Designs, Codes and Cryptography 94 (2026), article 87,
DOI 10.1007/s10623-026-01821-1.

Source scope:
perfect codes in Cayley graphs are explicitly related to group factorizations and tilings.

JANUS consequence:
`three-translate tiling` is canonical perfect-code/factorization language, not a novel JANUS problem class.

### S4 — Rybnikov and Zaslavsky (2002)

`Criteria for Balance in Abelian Gain Graphs, with Applications to Piecewise-Linear Geometry`,
arXiv:math/0210052.

Source scope:
gain-graph balance is characterized through closed-walk gains / potentials in abelian gain groups.

JANUS consequence:
the Z3 phase closed-walk / vertex-potential mechanism is standard gain-graph machinery; the JANUS specialization is a corollary/preprocessor.

## G4 — Collision matrix

| JANUS object | Canonical external object | Audit classification | Required action |
| --- | --- | --- | --- |
| Three-translate tiling | Perfect code / efficient domination / group tiling | EXACT_LANGUAGE_COLLISION | Rename/source-bind |
| Connected commuting P,Q | Strongly connected 2-valent abelian Cayley digraph perfect code | STRONG_KNOWN_CLASSIFICATION | Source-bind Yu et al.; no novelty |
| Z3 phase BFS | Abelian gain-graph potential/balance | KNOWN_DONOR | Keep as cheap preprocessor; no novelty |
| Phase to 1D character | Standard 1D representation / abelianization ingredient | JANUS_COROLLARY_OF_STANDARD_THEORY | Keep firewall/corollary only |
| General nonabelian phase-inconsistent 2-permutation directed perfect code | No complete closure located in sources checked so far | AUDIT_INCOMPLETE | HOLD NEW MATH |

## Remaining required source exhaustion

Before any new theorem on the residual class, complete searches in all five directions:

1. directed perfect codes / efficient domination complexity on low in/out-degree digraphs;
2. perfect codes in nonabelian 2-valent Cayley digraphs;
3. perfect codes in directed Schreier/coset digraphs with non-normal stabilizer;
4. arbitrary/non-subgroup perfect codes in vertex-transitive graphs;
5. complexity classifications for perfect code on permutation digraphs / unions of two permutations.

Also search terminology variants:
- efficient domination;
- independent perfect domination;
- exact domination;
- perfect dominating set;
- 1-perfect code;
- efficient closed domination;
- Cayley/Schreier exact tiling/factorization.

## Audit verdict

`CANONICAL_OBJECT = DIRECTED_PERFECT_CODE / EFFICIENT_DOMINATION`

`COMMUTING_ABELLAN_CASE = SOURCE_BOUND_CLASSIFIED`

`THREE_TRANSLATE_TILING = KNOWN_LANGUAGE`

`Z3_PHASE = KNOWN_GAIN_GRAPH_MECHANISM`

`NONABELIAN_PHASE_INCONSISTENT_RESIDUAL = NOT_FOUND_CLOSED_YET`

`AUDIT_STATUS = HOLD_NEW_MATH`

`NEW_MATH_AUTHORIZED = NO`

`NEXT_ALLOWED_WORK = SOURCE_EXHAUSTION_ONLY`

`D1 = EMPTY`

`P_VS_NP = OPEN`
