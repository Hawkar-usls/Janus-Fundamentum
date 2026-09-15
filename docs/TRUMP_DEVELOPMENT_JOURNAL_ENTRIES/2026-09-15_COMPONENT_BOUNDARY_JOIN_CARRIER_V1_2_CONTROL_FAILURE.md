# 2026-09-15 — component-boundary join carrier v1.2 control failure

Run `34918051333`, job `104219859638`, evaluated the scoped successor after the singleton join-tree receipt repair.

The positive overwidth multi-relation component passed its semantic checks: parent overwidth, k=20, component sizes 2+1, independent join-tree verification, effective support size 1, exact witness reconstruction, and zero raw cut-cube/full-join/backtracking/external-solver usage. Empty conditional support produced exact scoped UNSAT; no-anchor, hint and tamper controls also behaved correctly.

The only failed obligation was the hostile alpha-cycle end-to-end control. The independent local structural checker rejected the three-relation cycle as `OPEN_NO_VERIFIED_COMPONENT_JOIN_TREE`, but the candidate returned `OUT_OF_SCOPE_PARENT_NOT_OVERWIDTH`. Therefore the raw control did not survive the predecessor admission stack and could not test this successor gate.

Classification: `NEGATIVE_CONTROL_OUT_OF_PARENT_OVERWIDTH_SCOPE__CORE_POSITIVE_CARRIER_SURVIVED`.

No PASS is promoted. The allowed successor repair is limited to changing the alpha-cycle raw control so it remains a genuine three-relation private-variable cycle while mixing relation semantics strongly enough to stay inside the parent connected-mixed overwidth surface. Candidate semantics and the v1.2 singleton receipt repair are frozen.

Firewalls unchanged: `P_VS_NP=OPEN`, `GENERAL_SAT_IN_P=NOT_PROVED`, `CONNECTED_MIXED_CORE_SOLVED=NO`.
