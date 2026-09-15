# 2026-09-15 — Unique-core residual single-condition then pair-admissibility forensic

Authority: `DIAGNOSTIC_ONLY`.

Verdict: `PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_SINGLE_CONDITION_THEN_PAIR_ADMISSIBILITY_FORENSIC`.

This diagnostic followed v3.11, which showed that every exact Boolean conditioning of any K4 residual variable lowers the raw residual minimum cut from 3 to 2. The missing obligation was whether those newly visible pair cuts satisfy the sealed v3.10 structural admission rule.

Result: **no**. For all twelve single conditions `(variable 92..97) × (0,1)`, both candidate and an independent BFS/restriction backend found exactly two raw pair cuts and zero structurally admissible pairs. Hence `pair cut exists` is strictly weaker than `v3.10 pair carrier admissible` on the frozen K4 control.

No pair carrier was executed, no solver was executed, no separator of size >=3 was executed for SAT, and no 3+ join/global residual Cartesian product was materialized.

Captain Obvious therefore forbids a general recursive separator or triple-separator promotion. The nearest missing obligation is to inspect the GT2 remainder behind a canonical post-single pair cut: determine its exact component shape and whether that remainder itself is a sealed v3.10 pair-admissible K3-style component. Only that can justify a fixed-depth successor.

Actions: `35005118012 / 104502835363` — full SUCCESS, including v3.11 regression.

Firewalls remain `P_VS_NP=OPEN`, `GENERAL_SAT_IN_P=NOT_PROVED`, no global APMA frontier advance.
