# 2026-09-15 — Unique-core residual remainder structure forensic

Authority: `DIAGNOSTIC_ONLY`.

Verdict: `PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_SINGLE_THEN_PAIR_THEN_REMAINDER_STRUCTURE_FORENSIC`.

The frozen K4 control was profiled at the exact structural depth selected by Captain Obvious: one exact residual-variable condition, then the lexicographically first raw pair cut, then only the structure of any remaining GT2 component.

Across 12 single conditions and all four assignments of the selected first pair, there were exactly 48 first-level pair branch cases. Every nonempty branch split into relation-component sizes `[1,3]` or `[3,1]`. Thus every branch contained exactly one three-relation GT2 remainder and one singleton component.

All 48/48 three-relation remainders independently possessed an admissible residual pair under the sealed v3.10 structural contract; each remainder pair has four exact restrictions that reduce to residual components of size <=2 or exact empty UNSAT. Candidate and independent BFS backends agreed exactly. Observed lexicographic remainder pairs were `[92,94]`, `[93,94]`, or `[95,96]` depending on the preceding path.

No SAT branch was executed, no solver was invoked, no pair carrier was invoked, no 3+ join chain or global residual Cartesian product was materialized, and recursion depth was not grown dynamically.

Captain conclusion: the frozen K4 control now has a machine-backed **fixed-depth** structural skeleton: one Boolean variable -> one raw pair cut -> one pair-admissible K3 remainder -> sealed <=2 leaves. This licenses only a scoped preregistered fixed-depth `1-2-2` successor with at most `2*4*4 = 32` Boolean leaves. It does not license a general recursive separator theorem, arbitrary-depth search, a triple-separator theorem, or general bounded-treewidth tractability.

Actions: `35006025486 / 104505866953` — full SUCCESS including v3.12 regression.

Firewalls remain `P_VS_NP=OPEN`, `GENERAL_SAT_IN_P=NOT_PROVED`, no global APMA frontier advance.
