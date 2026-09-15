# TRUMP development journal — residual no-single-separator forensic

Date: 2026-09-15
Authority: diagnostic only; no theorem promotion.

After the scoped v3.8 single-variable separator PASS, Captain Obvious required read-only profiling of both frozen OPEN controls before any pair/multi-variable or general join-tree mechanism.

Preregistration froze a maximum separator-size diagnostic cap of two. Singleton and unordered pair variable cuts were structurally enumerated in polynomial O(V^2) time. No pair assignments were branched, no 3plus join chain was materialized, and no global residual Cartesian product was constructed.

Actions run `34996030629`, job `104472358805` passed, including the independent checker and v3.8 regression.

## NO_ARTICULATION

Residual factors `orig:4/5/6` have scopes `[47,48]`, `[47,50]`, `[48,50]`. The relation-overlap graph is a triangle with three distinct overlap variables. There is no singleton variable cut. The minimum cut size up to cap two is exactly two, with cuts `[47,48]`, `[47,50]`, `[48,50]`. Running-intersection fails (witness variable `50`). Each edge has 8 compatible row pairs.

## BRANCH_STILL_GT2

Residual factors `orig:4/5/6/7` have scopes `[47,48,53]`, `[47,50]`, `[48,50]`, `[53,54]`. Variable `53` is a singleton cut, but it only peels the leaf `orig:7`; the cyclic `orig:4/5/6` triangle remains GT2. Running-intersection again fails on variable `50`.

## Captain readout

The nearest exact successor is not a general join-tree carrier because running-intersection fails on the minimal cyclic triangle. It is not another single-variable separator because the main triangle has none. The nearest obligation is therefore a raw-derived two-variable residual separator: discover unordered pairs in O(V^2), choose the frozen lexicographic minimum structurally admissible pair, enumerate exactly four Boolean assignments, recompute residual components per assignment, and reuse only the sealed residual <=2 carriers. Any branch that remains GT2 must return OPEN before a join chain.

Proposed next gate: `TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_TWO_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD_FALSIFIER_GATE`.

Firewalls remain `P_VS_NP=OPEN`, `GENERAL_SAT_IN_P=NOT_PROVED`, and no global APMA frontier advance.
