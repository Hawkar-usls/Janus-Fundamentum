# TRUMP Bicameral Bucket Common-Core Semijoin Prefilter — Scoped Theorem v1.1

Authority: `SCOPED_THEOREM_AND_IMPLEMENTATION_CHECK__NO_GLOBAL_PROMOTION`

Verdict:

`PASS_SCOPED_BICAMERAL_BUCKET_COMMON_CORE_SEMIJOIN_PREFILTER_V1_1`

Frozen lineage:

- v1 preregistration: `3052c66fa2a95871ebf4cd7f145e9582e71a6c24`
- frozen v1 candidate: `196a5594b8b0fc2ac225cb456e8936315cda7458`
- immutable v1 first failure: `2fd0d96823fc7f752808f0d7bd4204dba4f255e0`
- v1 control diagnostic result: `471f30b519c6c42648e28dd98ca1a69005702980`
- v1.1 preregistration: `2aaaf5c8cdea020a36bdd1a7ecb86ce65015bfae`
- v1.1 wrapper: `223f04ff99893fd326f75c8ee51691800ab342bc`
- v1.1 independent checker: `3a1c38a6ec3bdf472e8311ce8c42bf351e1bcf17`
- frozen successful workflow head: `b9e7275d56d5b7cb0c8297c6cc92848acf0aa129`
- Actions run/job: `34973121868 / 104394027076`

## Scoped statement

Let `F_1,...,F_t` be exactly the original explicit Boolean relation factors in the first overbudget private-variable bucket of one cut-separated target component under the frozen canonical order. Prior exact work in *other* cut-separated components is allowed. The failed bucket itself must have been rejected by the sealed v3.2 `L^2` pre-expansion guard with zero failed-bucket combinations enumerated.

Let

`C = intersection_i scope(F_i)`

be the raw-derived common variable core of the bucket. Define

`P_i = pi_C(F_i)`

and

`S = intersection_i P_i`.

`S` is constructed only by scanning explicit rows and intersecting projection supports; the Cartesian row product of the bucket is not materialized.

### Exact empty-support case

If `S = empty`, then the bucket conjunction is unsatisfiable.

Proof: any assignment satisfying every `F_i` has one restriction to the common variables `C`. That restriction must occur in every `P_i`, hence in `S`. If `S` is empty no such assignment exists.

The admissible terminal is therefore:

`EXACT_UNSAT_BY_EMPTY_COMMON_CORE_SUPPORT_INTERSECTION`.

### Exact semijoin case

If `S` is nonempty, replace each factor `F_i` by the subset

`F_i' = { r in F_i : pi_C(r) in S }`.

No non-`C` coordinate is projected away. Every retained row remains an original row.

The replacement is solution-equivalent for the bucket conjunction:

- every satisfying assignment of the original bucket has a common-core state in `S`, so every row used by that assignment survives the semijoin filter;
- each filtered factor is a subset of the corresponding original factor, so the filter introduces no new satisfying assignment.

Thus the filter removes only rows that cannot participate in any satisfying bucket assignment.

After filtering, the unchanged sealed v3.2 guarded-elimination engine is invoked in the same canonical order and with the same frozen `L^2` pre-expansion budget.

If the filtered instance is admitted by v3.2 and its reconstructed assignment verifies against the **original unfiltered explicit relations**, the combined terminal is:

`ADMIT_EXACT_COMMON_CORE_SEMIJOIN_THEN_GUARDED_ELIMINATION`.

If the filtered first target bucket still exceeds `L^2`, the gate returns:

`OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2`

before enumerating that failed bucket. This OPEN is not negative complexity evidence.

## Complexity

For explicit relation-table input, computing `C`, projecting each input row to `C`, hashing/intersecting the supports and semijoin-filtering rows is polynomial in the explicit tuple-cell input size and is non-expanding: no filtered factor has more rows than its source factor.

The prefilter performs zero bucket Cartesian-product enumeration. If it hands off to v3.2, the remainder inherits the sealed conservative `O(L^6)` original-input lifecycle. Since the filtered input is no larger than the original input, the composition remains inside one fixed original-`L` polynomial envelope for this scoped gate.

No budget exponent is raised and no alternative elimination order is searched.

## Frozen controls

The independent v1.1 checker passed all obligations.

Positive control:

- predecessor v3.2 terminal: `OPEN_BUCKET_PRODUCT_BUDGET`;
- raw failed-bucket product: `557256278016`;
- exact common support size: `1`;
- semijoin-filtered bucket product: `1`;
- prior exact combinations in another cut-separated component: `30`;
- terminal: `ADMIT_EXACT_COMMON_CORE_SEMIJOIN_THEN_GUARDED_ELIMINATION`;
- reconstructed witness verifies against the original unfiltered relations.

Hostile forensic control:

- exact common support is empty;
- terminal: `EXACT_UNSAT_BY_EMPTY_COMMON_CORE_SUPPORT_INTERSECTION`;
- no failed bucket Cartesian product is enumerated.

Sticky control:

- common support is nonempty;
- filtered bucket product remains `1099511627776`;
- terminal: `OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2`;
- failed-bucket enumeration remains zero.

Injected hint: `REJECT_RAW_INPUT`.

Tampered provenance: `REJECT_TAMPERED_PROVENANCE`.

Regressions: sealed v3.2 guarded elimination, Captain first-overbudget forensic diagnostic and Schaefer mixed-carrier barrier all remain PASS.

## Claim ceiling

This theorem does **not** prove a general overbudget-bucket solver. It only closes the exact common-core semijoin subclass where the support intersection either proves contradiction or reduces the explicit row product sufficiently for the already sealed v3.2 guarded engine to proceed.

A nonempty common support with filtered product still above the frozen budget remains OPEN.

Permanent firewalls:

- `P_VS_NP = OPEN`
- `GENERAL_SAT_IN_P = NOT_PROVED`
- `CONNECTED_MIXED_CORE_SOLVED = NO`
- `GENERAL_EFFECTIVE_BUCKET_COMPRESSION = NOT_PROVED`
- `GLOBAL_APMA_FRONTIER_ADVANCE = NONE_PENDING_HQ_REVIEW`
