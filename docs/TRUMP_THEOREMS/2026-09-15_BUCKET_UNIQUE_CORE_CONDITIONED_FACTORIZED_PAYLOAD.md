# TRUMP Scoped Theorem — Unique-Core Conditioned Factorized Payload Portfolio

Date: 2026-09-15

Verdict: `PASS_SCOPED_BICAMERAL_BUCKET_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD_V1_2`

Authority class: scoped theorem and implementation check only. No global SAT/P-vs-NP promotion.

## Anti-loop classification

`SUCCESSOR_REPAIR__CONDITIONALIZATION_OF_EXISTING_FACTORIZED_FEEDBACK_PORTFOLIO_AFTER_COMMON_CORE_SEMIJOIN`

This is not a new universal factorization theorem. It combines the already sealed factorized-feedback principle with the v3.4 common-core semijoin result in one narrower conditioned setting.

## Frozen theorem scope

Let a target overbudget bucket arise from the v3.4 predecessor with terminal `OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2`. Let

- `C` be the exact common core derived as the intersection of the raw scopes of all target bucket factors;
- `S = intersection_i projection_C(F_i)` be the exact common-core support;
- `|S| = 1`, with unique state `s`;
- the failed bucket cover every relation in the target cut-component;
- after conditioning every target factor on `s` and removing `C` from its scope, the residual scopes be pairwise disjoint.

Then the conditioned target conjunction can be represented exactly as an additive portfolio of per-factor boundary projections, without materializing their Cartesian product.

## Exact construction

For each target relation `R_i`:

1. Keep exactly rows whose projection to `C` equals `s`.
2. Preserve the original row as reconstruction provenance.
3. Let `D_i = scope(R_i) \ C`.
4. Require `D_i` to be pairwise disjoint across target factors. Any residual shared variable returns `OPEN_RESIDUAL_CROSS_COUPLING`.
5. Existentially project factor-local private variables `D_i \ B`, leaving the exact boundary relation on `B_i = D_i ∩ B`.
6. Store all resulting boundary factors as a list/portfolio, never as a Cartesian product.

Replace the target component by these derived boundary factors, preserve every other cut-separated component, and invoke the unchanged sealed guarded-elimination engine with the same canonical cut and frozen budget policy.

## Exactness

Every satisfying assignment of the admitted target component must use the unique common-core state `s`. Conditioning on `s` therefore loses no satisfying assignment. Pairwise disjoint residual scopes imply that the conditioned conjunction is exactly the conjunction of independent residual factors. Each residual factor's boundary projection is exact existential elimination of only factor-local variables.

For SAT reconstruction, take the transformed witness, restore `C=s`, independently choose the stored original row matching each target boundary tuple, and replay the completed assignment against every original raw relation.

For the frozen positive control, both the candidate and independently written checker returned:

`ADMIT_EXACT_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD_PORTFOLIO`

The predecessor filtered row-product was `1099511627776 = 4^20`, yet the exact carrier stored only 23 additive portfolio records and 23 total boundary rows, with zero target Cartesian-product materialization and exact original-witness replay.

## Fail-closed boundaries

- More than one surviving common-core state: `OPEN_NONUNIQUE_COMMON_CORE_SUPPORT`.
- Residual cross-coupling: `OPEN_RESIDUAL_CROSS_COUPLING`.
- Incomplete target-component coverage: `OPEN_INCOMPLETE_TARGET_COMPONENT_COVERAGE`.
- Injected trusted hint: `REJECT_RAW_INPUT`.
- Tampered provenance: `REJECT_TAMPERED_PROVENANCE`.

Complete target-component coverage is a theorem admission precondition. Two preregistered attempts to create an end-to-end raw negative fixture for an incomplete-coverage state changed the frozen upstream predecessor before reaching this guard. Those v1 and v1.1 failures remain immutable. The v1.2 repair therefore tests the already-frozen complete-coverage guard with a forged READY-receipt unit falsifier derived from a valid sticky predecessor receipt. This unit falsifier is implementation fail-closed evidence only and is **not** evidence that such a forged receipt is reachable through canonical raw discovery.

The v1 mathematical candidate remained byte-frozen throughout v1.1 and v1.2.

## Complexity

For the admitted scope, construction scans explicit tuple cells, computes exact projections, audits residual scope intersections, stores additive boundary factors, invokes the already sealed guarded-elimination lifecycle, and reconstructs/replays one original witness. No target-factor Cartesian product is constructed or enumerated. Portfolio encoded size is additive in the explicit conditioned factor sizes and therefore polynomial in original encoded input length `L`.

No budget exponent is raised and no alternative elimination-order search is performed.

## Machine authority

- v1 preregistration: `f4531a3a5560394877d6123bffe8bb3a90be3576`
- frozen v1 candidate: `dce508a8db9c2564e3f35a2b512d12303826bc96`
- frozen v1 candidate blob: `c07cc8c12fa6f7a9b8f2560095caa4bdcc235480`
- v1 first run/job: `34976286395 / 104404709206`
- v1 first failure receipt: `7181ac04f8f29a8f96de910ab4bda5abfd7ba0e8`
- v1.1 preregistration: `70d7361aa1dc51d01e058e2d631b552d710755df`
- v1.1 run/job: `34977105951 / 104407510118`
- v1.1 failure receipt commit: `36046757c4f75559f1075f6ef17c8ba087a3943f`
- v1.2 preregistration: `d04b59b908a71971406eded2b778db775f882d64`
- v1.2 wrapper: `64af0b1f6a55311aad87ebf11339e5d0049dfba4`
- v1.2 independent checker: `b61be70ba1907b3ab832ecea3e869197e51087e7`
- v1.2 workflow head: `5d9fab407050ee7e121f7e1b74c492b0d7457784`
- v1.2 Actions run/job: `34977762886 / 104409787489`

All v1.2 checker obligations passed. Regressions remained green for common-core v1.1, factorized feedback, guarded elimination, and the Schaefer mixed-carrier barrier.

## Scientific firewall

- `P_VS_NP = OPEN`
- `GENERAL_SAT_IN_P = NOT_PROVED`
- `CONNECTED_MIXED_CORE_SOLVED = NO`
- `GENERAL_CONDITIONED_FACTORIZATION = NOT_PROVED`
- `GENERAL_BUCKET_ELIMINATION_POLYNOMIAL = NOT_PROVED`
- `GLOBAL_APMA_FRONTIER_ADVANCE = NONE`
