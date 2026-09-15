# TRUMP Bicameral Guarded Bounded-Output Elimination — Scoped Theorem

Date: 2026-09-15

Authority: `SCOPED_THEOREM_AND_IMPLEMENTATION_CHECK__NO_GLOBAL_PROMOTION`

Verdict:

`PASS_SCOPED_BICAMERAL_GUARDED_BOUNDED_OUTPUT_ELIMINATION_V1`

## Frozen scope

Let the canonical explicit Boolean relation input have encoded length `L`. Assume the already sealed predecessor stack establishes:

1. the raw/compositional Schaefer-basis inducer does **not** already admit the whole instance;
2. canonical min-variable-cut discovery returns an overwidth cut `B` and `OPEN_MINCUT_BRANCH_BUDGET` with zero raw cut assignments enumerated;
3. at least one cut-separated component contains three or more interacting relations;
4. the two-relation derived-boundary predecessor returns `OPEN_COMPONENT_RELATION_COUNT_GT_2`;
5. exact elimination uses the single frozen order: increasing private variables within each cut component, followed by increasing variables of `B` globally.

At every elimination variable `x`, collect the current factors containing `x`. Before constructing any row combination, compute the product of their explicit row counts with early stopping. The bucket is admitted only if

`product_i |F_i| <= L^2`.

If the product exceeds `L^2`, the algorithm returns `OPEN_BUCKET_PRODUCT_BUDGET` **before** enumerating a combination from that bucket.

## Exact bucket replacement

For an admitted bucket, enumerate only its at-most-`L^2` explicit row combinations, retain exactly the mutually compatible combinations, existentially project the eliminated variable, and deduplicate the resulting rows. For every resulting row, retain one content-bound witness value for the eliminated variable.

This replacement is exactly

`exists x  AND_i F_i`

on the remaining bucket variables. All factors outside the bucket remain unchanged.

Repeated exact replacements therefore preserve the complete existential semantics of the original frozen-scope relation instance. After private-variable elimination, the remaining factors form a portfolio over subsets of the canonical cut; no full `2^|B|` boundary relation is materialized. The same guarded elimination then removes cut variables.

If an admitted elimination creates an empty factor, the instance is exactly UNSAT in this scoped route. If elimination reaches a nonempty zero-arity factor, reverse replay of the stored bucket witnesses reconstructs a full assignment, which is then checked against every original explicit relation tuple.

## Uniform polynomial envelope

Every successful bucket materializes at most `L^2` candidate combinations and at most `L^2` output rows. The input has at most `O(L)` variables/factors/tuple cells. Compatibility, merge, projection, deduplication, witness bookkeeping, reverse reconstruction and original-tuple verification therefore admit one conservative fixed original-input polynomial envelope, recorded as `O(L^6)`. Its exponent does not depend on relation count.

Crucially, an overbudget bucket is not processed. Thus no hidden exponential bucket is paid before returning `OPEN`.

This proves polynomiality only for the frozen route in which **every bucket encountered by the one frozen order passes the `L^2` pre-expansion guard**. It does not prove that another order exists, that every mixed component is tractable, or that general bucket elimination is polynomial.

## Independent implementation evidence

Frozen candidate backend: full explicit bucket Cartesian row product **only after** the pre-expansion guard.

Independent checker backend: incremental hash-indexed natural joins in the same frozen order, with an independently implemented budget guard.

GitHub Actions `34921796167`, job `104231342652`, frozen workflow head `9537c1764f0a97ee5edf47eb371253944e86659b` passed all independent obligations and all predecessor regressions.

Machine controls:

- positive raw basis: `OPEN_COMPONENT_WITHOUT_SCHAEFER_BASIS`;
- positive parent: `OPEN_MINCUT_BRANCH_BUDGET`;
- canonical cut: variables `0..19`;
- components: `[[0],[1,2,3]]`;
- two-relation predecessor: `OPEN_COMPONENT_RELATION_COUNT_GT_2`;
- positive candidate and independent terminal: `ADMIT_EXACT_GUARDED_BOUNDED_OUTPUT_ELIMINATION`;
- positive total candidate row combinations: `52`;
- positive maximum materialized output rows: `2`;
- positive original witness replay: PASS;
- scoped UNSAT candidate and independent terminal: `EXACT_UNSAT_BY_COMPLETE_GUARDED_ELIMINATION`;
- hostile overbudget candidate and independent terminal: `OPEN_BUCKET_PRODUCT_BUDGET`;
- first failed overbudget variable: `20` in both implementations;
- failed-bucket combinations enumerated: `0`;
- frozen failed-bucket budget: `40,793,769`;
- hint input: `REJECT_RAW_INPUT`;
- tampered proposal: `REJECT_TAMPERED_PROVENANCE`.

The Schaefer connected mixed-carrier barrier regression remains PASS. Therefore this theorem is an additional-structure theorem, not a generic closure theorem for mixed tractable languages.

## Historical anti-loop relation

This is a successor repair of the R27/R29 local-bucket line, not a rediscovery. R27 localized an exact local bucket resource wall under a finite node cap; R29 localized the growth inside restriction of an already-large message. Neither supplied an asymptotic polynomial admission rule. The new contribution is the frozen original-`L` pre-expansion guard and fail-closed `OPEN` before any overbudget bucket is materialized.

## Scientific firewalls

- `P_VS_NP = OPEN`
- `GENERAL_SAT_IN_P = NOT_PROVED`
- `CONNECTED_MIXED_CORE_SOLVED = NO`
- `GENERAL_BUCKET_ELIMINATION_POLYNOMIAL = NOT_PROVED`
- `GENERAL_MULTI_RELATION_BOUNDARY_COMPRESSION = NOT_PROVED`
- `OVERBUDGET_BUCKETS = OPEN_NOT_NEGATIVE_EVIDENCE`
- `GLOBAL_APMA_FRONTIER_ADVANCE = NONE`
