# 2026-09-15 — Bicameral canonical min-variable-cut log-width v1.1

Parent continuity: `registry/TRUMP_CURRENT_STATE_2026-09-15_v2.6.json`.

The first frozen min-cut run (`34915543761`) failed because its preregistered positive control was already ONE_VALID and therefore outside the intended mixed-core scope. That failure is preserved immutably in `research/TRUMP_BICAMERAL_MINCUT_LOGWIDTH_FIRST_RUN_FAILURE_2026-09-15.json`; the min-cut algorithm was not patched in place.

A new v1.1 preregistration was frozen at `5f252316a74cbf431ad81da8528d58669e96ffa8`. The v1.1 candidate is only a source-guarded wrapper around the unchanged v1.0 min-cut engine blob `c0c612676e39241b95026c15823e7af6b3da8f0d`.

The corrected positive is an embedded OR2 relation and an embedded EVEN_XOR3 relation on arity-4 scopes sharing exactly variables `[0,1,2]`. The combined raw language has no common frozen Schaefer basis and the size-2 parent gate remains OPEN.

GitHub Actions run/job `34915753122 / 104212878620` completed `success`. All v1.1 independent checks passed; the workflow also replayed the immutable v1.0 checker and required its original FAIL verdict.

Candidate Edmonds–Karp and independent Dinic agree on canonical variable-only cut `[0,1,2]`, `k=3`. Canonical input bytes `L=230`, so `2^k=8<=L`. Exactly eight simultaneous restrictions were generated after the budget check; all eight independently admitted through sealed exact branch carriers/terminals. Result: `ADMIT_EXACT_LOGWIDTH_MINCUT_EXPLANATION`.

The overwidth control independently has cut size 20, `L=576`, and `2^20=1048576>L`. It returns `OPEN_MINCUT_BRANCH_BUDGET` with zero branch enumeration. This confirms that branch-budget failure is fail-closed before exponential materialization.

Scoped verdict: `PASS_SCOPED_BICAMERAL_CANONICAL_MINCUT_LOGWIDTH_EXPLANATION_INDUCTION_V1_1`.

The theorem is structural and scoped to explicit relation-table input. It establishes polynomial discovery of a growing variable separator through max-flow plus a polynomial branch envelope when `2^k<=L`; it does not solve arbitrary connected mixed cores or arbitrary CNF.

Nearest remaining object: a connected mixed raw core whose canonical minimum variable cut is over budget (`2^k>L`) and which has no simpler sealed explanation. The next useful mechanism should compress/equate cut assignments by an exact downstream quotient/rank/provenance explanation rather than enumerate them raw.

Global firewalls unchanged: `P_VS_NP=OPEN`, `GENERAL_SAT_IN_P=NOT_PROVED`, global APMA frontier unchanged.
