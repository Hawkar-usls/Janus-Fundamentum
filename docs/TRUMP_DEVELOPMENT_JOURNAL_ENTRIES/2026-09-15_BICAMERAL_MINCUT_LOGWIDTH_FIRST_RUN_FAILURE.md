# 2026-09-15 — Canonical min-variable-cut log-width first frozen run

Run `34915543761`, job `104212241471`, workflow head `34972a5e76d3b474d5a55ec217fc97b7a859895d`.

Frozen verdict: `FAIL_BICAMERAL_CANONICAL_MINCUT_LOGWIDTH_EXPLANATION_INDUCTION`.

The failure is **not** a min-cut discovery failure. Candidate Edmonds–Karp and independent Dinic both found the preregistered positive structural cut `[0,1,2]` with value/size 3. The log-width budget also held: `2^3=8 <= L=372`.

The frozen positive control itself violated its preregistered premise: `OR4` and `EVEN_XOR4` are both `ONE_VALID`, because tuple `1111` belongs to both relations. The already-sealed raw compositional basis therefore correctly returned `ADMIT_COMPOSITIONAL_BASIS_PORTFOLIO`, and the min-cut candidate correctly stopped as `OUT_OF_SCOPE_GLOBAL_OR_DISCONNECTED_BASIS_ALREADY_EXISTS` rather than manufacturing a more complex explanation.

The frozen overwidth control behaved as intended: independent min-cut size 20, `L=576`, branch budget `2^20=1048576>L`, terminal `OPEN_MINCUT_BRANCH_BUDGET`, and zero branch enumeration.

The v1.0 run is immutable. Any control repair must use a new preregistered successor lineage. No global frontier movement.
