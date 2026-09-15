# 2026-09-15 — K5 fixed-depth no-skeleton structure forensic

Authority: `DIAGNOSTIC_ONLY__NO_SCIENTIFIC_PROMOTION`

Verdict:

`PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_FIXED_DEPTH_1_2_2_NO_SKELETON_STRUCTURE_FORENSIC`

## Frozen parent

The parent scoped scientific result remains:

`PASS_SCOPED_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_FIXED_DEPTH_1_2_2_SEPARATOR_PORTFOLIO_V1`

with frozen Actions `35010169968 / 104519853649`, theorem seal `de25e0263144ba0b8d94e46909c8ecb2d75f6e3d`, and scientific merge `52356413943888805eeb17b76a4b1901ee1d7c1f`.

No parent scientific code was modified by this diagnostic.

## Diagnostic lineage

- preregistration: `d08126680774b471df415a91ae1a99883386fe14`
- candidate profiler: `200dc0cf81bb52c6857a450a158a6611078b36c8`
- frozen candidate blob: `517df2e4fe8e364b7149627ca018bc09cac6d0d2`
- independent checker: `4b27c555f0276c2ea47539ba6d37d6f3d39e99f5`
- workflow head: `f9c6df94580739510ce6f9cc5ac32a1269e8fcdf`
- Actions: `35014802264 / 104535421315` — SUCCESS
- PR: `#468`
- diagnostic merge: `cb3034db760a4779e916e6908eec280d46894e7e`

## Exact structural receipt

The frozen depth-cap control consists of five relation nodes and ten residual edge variables `200..209`. Each relation is the complete Boolean cube on its four incident edge variables. It remains a unit-test-only control with `raw_reachability_authority = false`.

Candidate and independent checker used different derivations: edge-subset enumeration plus BFS versus relation-vertex bipartition cuts plus independent componentization. They agreed exactly.

The relation-overlap K5 has minimum disconnect cut size `4`. There are exactly five minimum cuts, all stars:

- `[200,201,202,203]` isolates relation `0`;
- `[200,204,205,206]` isolates relation `1`;
- `[201,204,207,208]` isolates relation `2`;
- `[202,205,207,209]` isolates relation `3`;
- `[203,206,208,209]` isolates relation `4`.

Every minimum cut yields component sizes `[1,4]`, and every nontrivial four-relation remainder is structurally K4.

All `120` distinct removals of three edge variables remain connected. Therefore the frozen first `1+2` structural stage cannot disconnect this K5 control: it removes only three distinct overlap edges, while the graph edge-connectivity is four.

No Boolean separator assignments were enumerated. No solver or sealed carrier was executed. No 3+ join chain, global residual Cartesian product, recursion-depth extension, separator-size extension, or budget raise occurred.

## Captain Obvious anti-loop conclusion

The structural reason for `OPEN_FIXED_DEPTH_1_2_2_SKELETON_NOT_FOUND` is now explained for the frozen K5 unit control. This does **not** license a size-4 separator solver.

The earlier v2.7 lineage already contains canonical polynomial minimum-variable-cut discovery for its own raw connected mixed-core scope. Re-inventing a new size-4 separator mechanism directly from this unit control would be a rediscovery/authority error.

More importantly, this K5 control is not raw-reachability evidence. Its factors are full cubes and it was frozen only as a structural depth-cap unit falsifier. The next missing obligation is therefore not another separator level. It is whether any predecessor-admitted raw instance actually reaches a no-`1->2->2` residual of this kind after all earlier admissions and exact conditioning.

## Next blocker

`OPEN_NO_SKELETON_RAW_REACHABILITY_NOT_ESTABLISHED`

Next allowed gate:

`TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_NO_SKELETON_RAW_REACHABILITY_FORENSIC`

Classification: `DIAGNOSTIC_ONLY`.

Directive: establish raw reachability — or preserve failure to establish it as diagnostic evidence only — before any size-4 branching, extra recursion depth, or new separator theorem is licensed.

## Firewalls

- `P_VS_NP = OPEN`
- `GENERAL_SAT_IN_P = NOT_PROVED`
- `GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY = NOT_PROVED`
- `K5_UNIT_CONTROL_IS_GENERAL_INPUT_EVIDENCE = false`
- `SIZE4_BRANCHING_LICENSED = false`
- `GLOBAL_APMA_FRONTIER_ADVANCE = NONE`
