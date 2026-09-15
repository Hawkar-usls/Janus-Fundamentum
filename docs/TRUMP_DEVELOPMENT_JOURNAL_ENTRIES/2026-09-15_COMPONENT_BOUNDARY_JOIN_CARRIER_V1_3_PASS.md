# 2026-09-15 — component-boundary join carrier v1.3 PASS

The overwidth multi-relation cut-component line reached a scoped PASS after preserving two earlier failed runs and one diagnostic successor.

Canonical PASS: `PASS_SCOPED_BICAMERAL_OVERWIDTH_COMPONENT_JOIN_TREE_BOUNDARY_CARRIER_V1_3`.

GitHub Actions: run `34918226829`, job `104220378252`, workflow head `d3edb4041d1fa3d1e8886c81f06a3429d1758ed2`.

The mechanism is admission-first. The frozen polynomial min-cut parent discovers an overwidth cut B and refuses raw `2^|B|` enumeration. Each cut-separated component must expose B through at least one explicit raw relation. The canonical anchor's input rows provide at most O(L) candidate cut states. For each candidate state, the component relation scopes must admit a deterministic relation tree that independently passes running intersection. Exact tree semijoin/DP checks whether the candidate state extends through the component without materializing a full natural join. Component boundary supports are then intersected, and an accepted state reconstructs one original row per relation and a replayed global witness.

The positive k=20 control was admitted with one effective global cut state and exact witness. No raw cut cube, full join, tree backtracking, generic transfer or external SAT solver was used.

The hostile cycle was repaired into a genuine predecessor-admitted mixed-language overwidth object. Parent status was `OPEN_MINCUT_BRANCH_BUDGET`, branch enumerations zero, canonical cut was variables 0..19, and the post-cut components had sizes 3 and 1. Both the candidate Kruskal construction and independent Prim/tree-DP checker rejected it as `OPEN_NO_VERIFIED_COMPONENT_JOIN_TREE`.

Preserved history:
- v1: candidate crashed before receipt because singleton trivial trees lacked `tree_sha256`; frozen as infrastructure failure.
- v1.1 diagnostic: localized the exact KeyError without modifying v1 candidate bytes.
- v1.2: provenance-only singleton receipt repair succeeded on the core, but the original alpha-cycle negative control was outside parent scope; frozen as control failure.
- v1.3: only the hostile cycle raw control changed; candidate semantics and v1.2 singleton receipt repair stayed frozen.

This closes only the subclass with a raw full-cut anchor and a verified running-intersection relation tree. Remaining blockers include components without a raw full-cut anchor and components whose relation scopes have no verified join tree; those require a different exact boundary quotient/message such as a derived affine syndrome, bounded elimination, finite congruence, or another preregistered carrier.

Firewalls: `P_VS_NP=OPEN`; `GENERAL_SAT_IN_P=NOT_PROVED`; `CONNECTED_MIXED_CORE_SOLVED=NO`; `GENERAL_MULTI_RELATION_BOUNDARY_COMPRESSION=NOT_PROVED`.
