# 2026-09-17 — UF20 WL historical closed-control falsifier

## Authority and chronology

- Parent WL discovery result: `8ff915e53d99fdab77ad57c0b965bfbf535bc2d6`
- Blind falsifier preregistration: `835a5f3bc38c73a995e36c85345b73842e418aae`
- Clean review: `7dce25fd0c76ceaf0f541201de3051ba8da728f9`
- Candidate implementation: `c336be6617e01ac6ffaea6003141bda706907de2`
- Independent checker: `5b3a06689f9316b9fc567487122ac3ab6dc09f5b`
- Workflow head: `673d818bbd0396d6c259057fb1cff32c7d7f6b4f`
- Actions run: `35242113659`
- Actions job: `105272899140`
- Frozen result commit: `4654e42f262e41033c7db116352163ddcf7f38f1`
- Frozen result: `research/TRUMP_UF20_WL_POLYTIME_HISTORICAL_CLOSED_CONTROL_FALSIFIER_RESULT_2026-09-17_v1.0.json`

## Result

Verdict: `WL_CANDIDATE_SURVIVOR_SET_FOUND__INDEPENDENT_REPLICATION_REQUIRED`.

The four preregistered provenance-free fixed-dimensional WL features survived all six pre-existing source-authorized connected-mixed closed controls from the v3.23 census:

- `WL1_MAX_VARIABLE_COLOR_CLASS_SIZE` with blocker value `1`
- `WL1_VARIABLE_PARTITION_IS_DISCRETE` with blocker value `true`
- `WL2_MAX_VARIABLE_DIAGONAL_COLOR_CLASS_SIZE` with blocker value `1`
- `WL2_VARIABLE_DIAGONAL_PARTITION_IS_DISCRETE` with blocker value `true`

All 24 frozen feature-by-control comparisons were evaluated. No historical closed control matched a blocker value. The independent checker reproduced the complete matrix and survivor set without importing the candidate implementation.

Historical closed-control maximum variable color-class sizes were `2, 3, 20, 20, 20, 18`; every historical closed control had non-discrete variable partitions under both 1-WL and 2-WL. The three corrected reduced residual blockers in the frozen discovery panel had discrete variable partitions with maximum class size `1`, while the corrected reduced closed control UF20_03 had maximum class size `2` and a non-discrete partition.

## Scientific interpretation

This is a diagnostic survivor result only. It does **not** show that WL discreteness implies SAT hardness, non-tractability, or the need for a new solver. It does **not** provide an exact reduction and does **not** establish general residual-separator tractability.

The next missing obligation is independent source-bound replication or a preregistered fresh holdout gate. No reduction, solver, action rule, carrier mechanism, threshold rescue, feature conjunction, or feature ranking is licensed before that replication.

## Firewalls

- `P_VS_NP = OPEN`
- `GENERAL_SAT_IN_P = NOT_PROVED`
- `CONNECTED_MIXED_CORE_SOLVED = NO`
- `GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY = NOT_PROVED`
