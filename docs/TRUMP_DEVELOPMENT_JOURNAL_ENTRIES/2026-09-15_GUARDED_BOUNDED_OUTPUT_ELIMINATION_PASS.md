# TRUMP — Guarded Bounded-Output Elimination — PASS

Date: 2026-09-15

Verdict: `PASS_SCOPED_BICAMERAL_GUARDED_BOUNDED_OUTPUT_ELIMINATION_V1`.

This closes the next v3.1 downward subproblem for predecessor-open mixed/non-affine 3+ relation components **only when** every bucket encountered by one preregistered canonical elimination order has an explicit row-count product no greater than `L^2` before expansion.

The mechanism is a successor repair of the historical R27/R29 local-bucket line. R27 showed that localizing elimination to a bucket did not by itself prevent a finite one-million-node resource wall, and R29 localized the dominant cost inside exact restriction of an already-large message. Those results were resource forensics, not asymptotic theorems. The present gate adds a different contract: no bucket is materialized at all unless its explicit pre-expansion product is already bounded by a fixed polynomial of the original input size.

Frozen candidate backend uses the full explicit Cartesian row product only after the `L^2` guard. Independent checker uses incremental hash-indexed natural joins and shares no candidate join helper.

Actions `34921796167`, job `104231342652`, workflow head `9537c1764f0a97ee5edf47eb371253944e86659b`: SUCCESS.

Positive control is the existing v3.0 mixed 3-relation no-anchor control. It remains outside the sealed common Schaefer basis portfolio (`OPEN_COMPONENT_WITHOUT_SCHAEFER_BASIS`), canonical mincut remains overwidth with cut variables `0..19`, the two-relation predecessor remains `OPEN_COMPONENT_RELATION_COUNT_GT_2`, and components are `[[0],[1,2,3]]`. Candidate and independent checker both return `ADMIT_EXACT_GUARDED_BOUNDED_OUTPUT_ELIMINATION`. Candidate enumerated 52 row combinations across the complete admitted lifecycle, materialized at most 2 output rows at any successful bucket, reconstructed a witness and replayed every original relation tuple.

The preregistered exact-UNSAT control is independently reproduced as `EXACT_UNSAT_BY_COMPLETE_GUARDED_ELIMINATION`.

The hostile overbudget control is more important for the theorem ceiling. Candidate and independent checker both stop at variable `20` with `OPEN_BUCKET_PRODUCT_BUDGET`; the frozen `L^2` budget for that input is `40,793,769`, and the failed bucket has row counts `[3,3,1,3,4,3,4,3,4,3,4,3,4,3,4,3,4,3,4,3,4,3,4]`. The failed bucket enumerates exactly zero combinations. No alternate elimination order is attempted. `OPEN` is not negative evidence.

All predecessor regressions passed, including the Schaefer connected mixed-carrier barrier. Therefore the result is not a generic polynomial closure theorem for mixed languages.

Refined blocker:

`PREDECESSOR_OPEN_MIXED_3PLUS_RELATION_OVERWIDTH_COMPONENT_WITH_FIRST_FROZEN_ORDER_BUCKET_PRODUCT_GREATER_THAN_L2_AND_NO_OTHER_SEALED_STRUCTURE`

The next attack must reduce the **effective** bucket complexity before materialization — e.g. exact factorization, typed/reverse-morph escape, finite exact congruence, a provably smaller canonical representation, or another preregistered mechanism. Simply raising the polynomial degree or retrying many elimination orders is forbidden.

Permanent firewalls remain:

- `P_VS_NP = OPEN`
- `GENERAL_SAT_IN_P = NOT_PROVED`
- `CONNECTED_MIXED_CORE_SOLVED = NO`
- `GENERAL_BUCKET_ELIMINATION_POLYNOMIAL = NOT_PROVED`
- `GENERAL_MULTI_RELATION_BOUNDARY_COMPRESSION = NOT_PROVED`
- `GLOBAL_APMA_FRONTIER_ADVANCE = NONE`
