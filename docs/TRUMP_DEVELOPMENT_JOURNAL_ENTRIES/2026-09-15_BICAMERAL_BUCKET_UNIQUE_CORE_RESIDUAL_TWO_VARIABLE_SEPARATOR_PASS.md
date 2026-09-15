# 2026-09-15 — Bicameral Bucket Unique-Core Residual Two-Variable Separator PASS

## Outcome

Frozen verdict:

`PASS_SCOPED_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_TWO_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD_V1`

Actions run/job: `34997650364 / 104477846188` — full SUCCESS.

## Why this successor was selected

The v3.9 diagnostic established that the smallest no-single-separator residual triangle has no running-intersection witness and has minimum raw residual variable cut size two. Captain Obvious therefore selected the narrow successor: deterministic unordered pair discovery in `O(V^2)`, exact four-value conditioning on the selected pair, recomputation of residual components, and reuse only of the already sealed residual `<=2` carriers.

This is a successor repair, not a new generic separator theory. The older pair-separator semantics are reused inside the unique-common-core residual bucket surface.

## Machine receipt

The candidate and an independent checker agree on the canonical positive pair `[47,48]`.

Positive control:
- four exact branches;
- all four SAT;
- terminal `ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_TWO_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD`;
- full original witness replay PASS.

Leaf-extended frozen control:
- pair `[47,48]`;
- all four exact branches SAT.

One-survivor control:
- three branches exact UNSAT by empty pair restriction;
- one branch exact SAT;
- terminal SAT admission.

All-four-UNSAT control:
- all four branches exact UNSAT;
- terminal `EXACT_UNSAT_BY_ALL_PAIR_SEPARATOR_BRANCHES`.

Negative/fail-closed controls:
- raw K4 distinct-edge-variable residual: `OPEN_NO_ADMISSIBLE_RESIDUAL_TWO_VARIABLE_SEPARATOR` in both candidate and independent checker;
- injected pair hint: `REJECT_RAW_INPUT`;
- tampered provenance: `REJECT_TAMPERED_PROVENANCE`.

Resource receipt:
- pair discovery `O(V^2)`;
- exactly 4 assignments for the selected pair;
- separator sets of size >=3: 0;
- three-plus join chains: 0;
- global residual Cartesian products: 0;
- budget raise: false;
- alternative-order search: 0.

## Regressions

Green in the same frozen workflow:
- v3.8 single-variable separator;
- v3.6 residual `<=2` portfolio;
- v3.5 conditioned payload;
- guarded bounded-output elimination;
- Schaefer mixed-carrier barrier.

## Scientific boundary

This closes only the scoped unique-common-core residual surface where a raw-derived variable pair has four branches that each reduce to exact UNSAT or residual relation components of size at most two. It does not cover residuals requiring separators of size three or larger, unbounded separator depth, general join trees, multiple common-core states, or arbitrary connected mixed SAT.

Firewalls remain:

- `P_VS_NP = OPEN`
- `GENERAL_SAT_IN_P = NOT_PROVED`
- `CONNECTED_MIXED_CORE_SOLVED = NO`
- `GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY = NOT_PROVED`
- `GLOBAL_APMA_FRONTIER_ADVANCE = NONE_PENDING_HQ_REVIEW`
