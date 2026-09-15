# TRUMP common-core semijoin v1 control diagnostic

Run `34972746081`, job `104392774692`.

The diagnostic content itself completed successfully. The workflow concluded failure only in a later shell-only source-check step whose heredoc was malformed; that post-step did not alter or invalidate the diagnostic output.

All positive/sticky/hostile controls reach sealed `OPEN_BUCKET_PRODUCT_BUDGET` at failed variable `20` with zero failed-bucket enumeration. However, the v1 helper rejected them because it required **zero successful combinations globally before the failure**. Machine values were `30`, `30`, and `2` respectively.

Root cause: another cut-separated component is processed before the target left component. Within the target component, variable `20` remains its first canonical private variable and the failed bucket consists of original relations.

Allowed successor repair: relax only this over-strong global-first condition. v1.1 may allow prior work in other cut-separated components but must require the failed variable to be the minimum private variable of the target component and the failed bucket IDs to match original relation factors exactly.

No common-core mathematical primitive is repaired in place. `P_VS_NP=OPEN`, `GENERAL_SAT_IN_P=NOT_PROVED`.
