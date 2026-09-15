# TRUMP — Fixed-Depth 1→2→2 Residual Separator Portfolio — Scoped Theorem Seal

Date: 2026-09-15

Verdict:

`PASS_SCOPED_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_FIXED_DEPTH_1_2_2_SEPARATOR_PORTFOLIO_V1`

## Frozen scope

This seal applies only after the previously sealed unique-common-core predecessor and only when deterministic raw residual discovery produces the preregistered fixed-depth skeleton:

1. one Boolean residual variable;
2. in each nonempty Boolean branch, one raw residual variable pair;
3. in each first-pair branch, at most one remaining three-relation GT2 component;
4. that remainder has one structurally admissible raw residual pair;
5. every final logical leaf is exact-empty UNSAT or has only residual relation components of size at most two;
6. the leaf is discharged only by the already sealed v3.6 <=2 carrier plus guarded elimination.

No unbounded recursion is authorized.

## Exact statement

For inputs in this strict scope, the fixed-depth plan is semantics-preserving because every split is an exhaustive Boolean restriction on original raw variables. The union of all logical leaves is exactly the original conditioned residual state space. Therefore:

- SAT is admitted only when at least one leaf reconstructs a full assignment that replays every original raw relation row;
- UNSAT is admitted only when every logical leaf has an exact UNSAT certificate from empty restriction, empty sealed <=2 pair join, or complete guarded elimination;
- any leaf outside the sealed <=2 scope keeps the result OPEN.

## Frozen successful instance

The v3.13 K4-style no-pair control is admitted by the deterministic plan:

`92 → [93,94] → [95,96]`

for both values of variable 92 and all four assignments of the first pair. Candidate and independent checker derived the same normalized plan independently.

Maximum logical leaf count: `32`.

## Resource contract

- single-variable scan: `O(V)`;
- pair scan at each fixed pair level: `O(V^2)`;
- separator depth: exactly bounded by `3` levels in this gate;
- maximum logical leaf count: `32`;
- separator sets of size >=3 enumerated: `0`;
- unbounded recursive calls: `0`;
- three-plus relation join chains materialized: `0`;
- global residual Cartesian products materialized: `0`;
- external solver calls: `0`;
- L^2 budget raises: `0`;
- conservative frozen lifecycle envelope: `O(L^12)` with polynomial degree independent of relation count for this fixed-depth scope.

## Falsifier retained

The structural K5 depth-cap control returns:

`OPEN_FIXED_DEPTH_1_2_2_SKELETON_NOT_FOUND`

It is a fail-closed unit control, not evidence of hardness and not a lower bound.

## Independent replay

GitHub Actions:

- run: `35010169968`
- job: `104519853649`

Independent checker uses BFS componentization, its own Boolean restriction implementation, its own unordered-pair scans, and does not use candidate plan-discovery helpers. Full original relation replay verifies the positive witness.

All regressions were green: v3.13 forensic, v3.10 pair separator, v3.6 <=2 portfolio, guarded elimination, and Schaefer mixed-carrier barrier.

## Scientific firewalls

`P_VS_NP = OPEN`

`GENERAL_SAT_IN_P = NOT_PROVED`

`CONNECTED_MIXED_CORE_SOLVED = NO`

`GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY = NOT_PROVED`

`GENERAL_RECURSIVE_SEPARATOR_TRACTABILITY = NOT_PROVED`

`GENERAL_BOUNDED_TREEWIDTH_TRACTABILITY = NOT_PROVED`

No global APMA frontier advance is authorized by this scoped theorem.
