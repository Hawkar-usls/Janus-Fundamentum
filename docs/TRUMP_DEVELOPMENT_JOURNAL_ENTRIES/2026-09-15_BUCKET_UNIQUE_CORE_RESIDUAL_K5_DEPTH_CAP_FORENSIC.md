# 2026-09-15 — K5 fixed-depth 1→2→2 depth-cap structure forensic

Authority: `DIAGNOSTIC_ONLY`. No scientific promotion.

The frozen `K5_DEPTH_CAP_CONTROL` retained by the scoped fixed-depth `1→2→2` theorem was audited before any attempt to add recursion depth or separator size. The control is a synthetic five-relation K5 overlap graph with ten edge variables `200..209`; each relation contains the full Boolean cube on its four incident edge-variable scope. The frozen control is explicitly `unit_test_only=true` and `raw_reachability_authority=false`.

Candidate and independent checker used different structural derivations. The candidate enumerated bounded edge-variable cut subsets through cardinality four and recomputed relation components with BFS. The independent checker derived crossing-edge cuts from K5 bipartitions and used its own graph/component/path logic. The frozen predecessor source was also checked byte-identically.

GitHub Actions run `35014802264`, job `104535421315`, completed `SUCCESS` on head `f9c6df94580739510ce6f9cc5ac32a1269e8fcdf`.

Machine facts:

- no disconnecting edge-variable cut of cardinality `<=3`;
- minimum structural cut cardinality is exactly `4`;
- exactly five minimum cuts exist, the four-edge stars incident to each K5 relation node;
- every minimum cut produces relation-component sizes `[1,4]`;
- the nontrivial four-relation remainder has K4 relation-overlap shape;
- all `120` distinct three-edge removal paths remain connected;
- candidate and independent checker agree;
- zero Boolean assignment branches, solver calls, carrier calls, unbounded recursion, 3+ join chains, global residual Cartesian products, or budget raises were used.

This explains the narrow structural reason the sealed fixed-depth `1→2→2` skeleton returns `OPEN_FIXED_DEPTH_1_2_2_SKELETON_NOT_FOUND` on this control: three structural edge-variable removals cannot disconnect K5.

It does **not** license branching on the four-variable minimum cut. `SIZE4_BRANCHING_LICENSED=false`. It does not license another recursive separator layer, arbitrary separator depth, a size-3/size-4 separator theorem, bounded-treewidth tractability, hardness, or a lower bound.

Captain Obvious conclusion: before engineering any deeper or wider separator successor around this K5 control, establish whether a semantically nontrivial K5 depth-cap shape is reachable from the actual raw unique-core predecessor surface. The present control has no raw-reachability authority and its five relations are universal full-cube relations, so solving this unit control by a new separator theorem could be scientifically irrelevant. The next preferred action is therefore a diagnostic raw-reachability and semantic-nontriviality forensic, not size-4 Boolean branching.

Frozen diagnostic result: `research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_FIXED_DEPTH_1_2_2_NO_SKELETON_STRUCTURE_FORENSIC_RESULT_2026-09-15.json`.

PR #468 merged as `cb3034db760a4779e916e6908eec280d46894e7e`.

Firewalls remain `P_VS_NP=OPEN`, `GENERAL_SAT_IN_P=NOT_PROVED`, `CONNECTED_MIXED_CORE_SOLVED=NO`; the global APMA frontier did not advance.
