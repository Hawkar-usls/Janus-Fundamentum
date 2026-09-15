# 2026-09-15 — Bucket unique-core residual no-single-separator structure forensic

## Status

`PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_NO_SINGLE_SEPARATOR_STRUCTURE_FORENSIC`

Diagnostic only. No theorem promotion.

Actions: `34996627394 / 104474384224` — full SUCCESS, including v3.8 single-separator regression.

## Why this diagnostic was run

v3.8 closed the raw-derived single Boolean residual separator case and left two frozen OPEN controls:

1. no admissible single-variable articulation;
2. a candidate single separator whose branch still contains a residual component larger than two.

Captain Obvious forbade jumping directly to arbitrary pair branching, general join-tree theory, bounded-width DP, or congruence. The preregistered diagnostic therefore searched raw residual variable cuts only up to fixed cap two, in cardinality/lexicographic order, and profiled branch-specific structure after one exact Boolean conditioning. The cap-two search is polynomial `O(V^2 * poly(input incidence))` and is diagnostic only.

## Control A — no single articulation

Target factors:

`orig:4, orig:5, orig:6`

Residual scopes:

- `orig:4 = {47,48}`
- `orig:5 = {47,50}`
- `orig:6 = {48,50}`

The relation-overlap graph is a triangle. Every edge is labeled by a distinct single variable: 47, 48, 50.

There is no size-one raw residual variable cut that reduces every component to size <=2. The minimum cut size is exactly two. All minimum cuts within the frozen cap are:

- `{47,48}`
- `{47,50}`
- `{48,50}`

Running-intersection fails; the independent checker agrees. Pairwise compatibility remains nonempty on all three edges (8 compatible pairs of 16 on each edge), so there is no pairwise contradiction shortcut.

Most important branch-specific observation: after exact conditioning on any one of 47, 48, or 50, every nonempty Boolean branch exposes a new size-one raw residual cut. Thus the minimum pair has a sequential interpretation rather than requiring an immediate opaque four-way carrier.

## Control B — branch still GT2

Target factors:

`orig:4, orig:5, orig:6, orig:7`

Residual scopes:

- `orig:4 = {47,48,53}`
- `orig:5 = {47,50}`
- `orig:6 = {48,50}`
- `orig:7 = {53,54}`

The minimum raw residual variable cut is exactly two and is unique:

`{47,48}`.

Running-intersection again fails. Pairwise compatibility stays nonempty.

Conditioning first on 47 exposes 48 as a size-one cut in both Boolean branches. Conditioning first on 48 exposes 47 in both branches. Conditioning on unrelated residual variables does not necessarily achieve this reduction.

This identifies a canonical ordered successor: discover the lexicographically minimum minimum cut pair under the fixed cap, condition on its first member, then rediscover a size-one separator independently inside each nonempty branch.

## Independent methods

Profiler:
- union-find relation components;
- lexicographic cap-two subset cut scan;
- Kruskal maximum-overlap tree;
- nested pair compatibility.

Independent checker:
- BFS relation components;
- separate cap-two subset cut scan;
- Prim maximum-overlap tree;
- hash-signature pair compatibility.

All comparisons agreed. No three-plus join chain, global residual Cartesian product, solver call, or theorem promotion occurred.

## Captain Obvious readout

Nearest missing exact obligation:

`CANONICAL_RAW_DERIVED_SIZE_TWO_RESIDUAL_CUT_EXECUTED_AS_TWO_SEQUENTIAL_SINGLE_VARIABLE_CONDITIONING_STAGES`

Next gate:

`TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_DEPTH2_SEQUENTIAL_SINGLE_SEPARATOR_FACTORIZED_PAYLOAD_FALSIFIER_GATE`

The proposed successor is narrower than a general pair-separator theorem:

1. discover a canonical size-two residual cut with a fixed polynomial cap-two search;
2. condition on the first member only;
3. in each nonempty branch rediscover a size-one separator from branch raw scopes;
4. condition on that separator;
5. require every leaf to reduce to already sealed residual components of size <=2;
6. reuse only sealed v3.6 carriers at leaves;
7. SAT only after full original relation replay; exact UNSAT only if every exhaustive leaf is exact UNSAT;
8. otherwise OPEN.

## Firewalls

`P_VS_NP=OPEN`

`GENERAL_SAT_IN_P=NOT_PROVED`

`CONNECTED_MIXED_CORE_SOLVED=NO`

`GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY=NOT_PROVED`
