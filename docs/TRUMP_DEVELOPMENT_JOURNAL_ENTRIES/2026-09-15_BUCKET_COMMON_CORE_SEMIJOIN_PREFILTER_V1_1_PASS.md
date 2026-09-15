# TRUMP bucket common-core semijoin prefilter v1.1 — PASS

Verdict: `PASS_SCOPED_BICAMERAL_BUCKET_COMMON_CORE_SEMIJOIN_PREFILTER_V1_1`.

Actions: run `34973121868`, job `104394027076` — full SUCCESS.

This line originated from Captain Obvious forensic work on the first v3.2 overbudget bucket. The raw product was `557256278016`, but exact compatibility on the frozen hostile control collapsed as `3 -> 3 -> 1 -> 0`. All 23 failed-bucket factors share the raw common core `Y={20..39}`.

The v1 theorem attempt preserved an immutable pre-verdict failure because it incorrectly required the failed bucket to be globally first. A dedicated diagnostic showed that another cut-separated component is processed first; variable 20 is nevertheless the first private variable of the target component. v1.1 repaired only that admission condition. The v1 projection/intersection/semijoin mathematics remained frozen.

Scoped theorem: for original explicit bucket factors `F_i`, derive `C=intersection scope(F_i)`, supports `P_i=pi_C(F_i)` and `S=intersection P_i`. Empty `S` is exact bucket UNSAT. Otherwise semijoin each original factor to rows whose `C` projection lies in `S`, preserving all non-core coordinates, then hand off to the unchanged v3.2 `L^2` guarded engine. No raw bucket Cartesian product is materialized by the prefilter.

Controls:

- SAT positive: raw product `557256278016` -> common support size `1` -> filtered product `1` -> sealed v3.2 admits -> witness verifies against ORIGINAL unfiltered rows.
- Hostile forensic: common support empty -> `EXACT_UNSAT_BY_EMPTY_COMMON_CORE_SUPPORT_INTERSECTION`.
- Sticky: common support nonempty but filtered product `1099511627776` -> `OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2`, failed enumeration zero.
- hint -> `REJECT_RAW_INPUT`.
- tamper -> `REJECT_TAMPERED_PROVENANCE`.

Regressions: v3.2 guarded elimination PASS, Captain forensic PASS, Schaefer mixed-carrier barrier PASS.

New nearest blocker: an overbudget target bucket for which exact common-core semijoin leaves nonempty support and the filtered row product is still greater than the frozen `L^2` envelope. The next mechanism must exploit exact factorization/congruence/partial-overlap structure before materialization; raising the exponent or searching many orders remains forbidden.

Firewalls unchanged: `P_VS_NP=OPEN`, `GENERAL_SAT_IN_P=NOT_PROVED`, `CONNECTED_MIXED_CORE_SOLVED=NO`, `GENERAL_EFFECTIVE_BUCKET_COMPRESSION=NOT_PROVED`.
