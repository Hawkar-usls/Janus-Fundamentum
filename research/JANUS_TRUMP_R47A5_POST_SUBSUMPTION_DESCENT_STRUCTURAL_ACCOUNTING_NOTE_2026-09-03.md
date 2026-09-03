# JANUS TRUMP R47A5 — exact post-subsumption accounting identity

Let `F` be a canonical CNF and `v` a bipolar pivot. Define:

- `B_v` = clauses of `F` not containing `v` or `-v`;
- `T_v` = `SUBSUMPTION_MINIMIZE(CANONICAL(B_v ∪ R_v))`, where `R_v` is the exact set of unique non-tautological DP resolvents;
- `d_v = |F| - |B_v|`, the number of parent clauses removed by eliminating `v`;
- `s_v = |T_v| - |B_v|`, the post-subsumption survivor pressure above the unaffected base;
- `g_v = |F| - |T_v|`, the clause-count descent gain.

Then identically:

`g_v = (|F|-|B_v|) - (|T_v|-|B_v|) = d_v - s_v`.

Therefore:

- `g_v > 0` iff `s_v < d_v`: exact DP plus subsumption gives immediate clause descent;
- `g_v = 0` iff `s_v = d_v`: exact replacement balance;
- `g_v < 0` iff `s_v > d_v`: post-subsumption expansion;
- any true all-pivot obstruction must satisfy `s_v >= d_v` for every bipolar pivot.

This is an accounting identity, not a universal existence theorem. R47A5 must still prove that simultaneous `s_v >= d_v` is impossible under the exact R33 lean hypotheses, or produce an explicit counterexample.

Epistemic firewall: `R47A_UNIVERSAL_COVERAGE=OPEN`, `SAT_IN_P=NOT_PROVED`, `P_VS_NP=OPEN`.
