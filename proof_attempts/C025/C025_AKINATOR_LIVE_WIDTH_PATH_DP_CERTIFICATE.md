# C025 — Akinator deterministic live-width path-DP certificate lane

Canonical TOPA source:

`Hawkar-usls/TOPA/research/mathematics/p-vs-np/C025_AKINATOR_LIVE_WIDTH_PATH_DP_CERTIFICATE.md`

Claim ceiling: **P_VS_NP = OPEN**

## Core construction

Treat every B2 gate `e := a AND b` as a local Boolean constraint on at most three underlying variables. For the transitive dependency cone of an output macro, use the frozen topological gate order `G_1,...,G_T`.

For every variable `v`, compute exact first/last occurrence indices. Define

`L_t = {v : first(v) <= t <= last(v)}`.

These bags form a valid path decomposition: every gate-local clique is covered and each variable appears on a contiguous interval. The decomposition is recomputed deterministically from the gate trace; no decomposition search or heuristic order is used.

Define live width

`lambda = max_t |L_t| - 1`.

Exact feasibility of output bit `b` under a root restriction is decidable by dynamic programming over bag assignments in

`poly(T, bytes) * 2^O(lambda)`.

Run for `b=0` and `b=1`; both feasible iff the residual macro is nonconstant. Predecessor pointers recover explicit witnesses.

Hence, for polynomial trace bytes and a universal bound `lambda=O(log N)`, exact survival discovery is deterministic polynomial time in original encoded `N`.

## Large support survives

The linear B2 XOR/parity recurrence has constant live width under its natural serialized gate order while final root support is `n`.

Thus `LARGE_ROOT_SUPPORT != LARGE_LIVE_WIDTH`.

## Fixed-architecture barrier

Construct `e_i=x_i AND y_i`, every pair gate `g_ij=e_i AND e_j`, then aggregate all pair gates so they remain in one output cone. DAG size is `O(n^2)`.

For any topological serialization of this fixed architecture, let `e_j` be the last first-layer gate produced. Every earlier `e_i` remains live through that point because child `g_ij` cannot have executed before `e_j` exists. Therefore `lambda=Omega(n)=Omega(sqrt(T))`.

This is a representation-architecture barrier only; the final Boolean function is semantically simpler and may admit a different low-width circuit. Therefore equivalent-representation rewrite discovery is a separate open resource.

## Current frontier

- deterministic live-width path decomposition: PROVED_IN_SCOPE
- exact DP survival cost: `poly(T)*2^O(lambda)`
- `lambda=O(log N)` + poly trace => poly survival discovery: PROVED_IN_SCOPE
- universal low-width equivalent representation: OPEN
- deterministic low-width rewrite discovery: OPEN
- global proof-progress certificate: OPEN
- polynomial Akinator: OPEN
- P vs NP: OPEN
