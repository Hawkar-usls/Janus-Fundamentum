# C025-E2R-L1G-F3 — Negative-frontier width × inversion depth

**Status:** `ANALYTICAL_BARRIER_AND_REPRESENTATION_BOUND_PENDING_PROVIDER_REPLAY`.

Define `d(e)` as the maximum number of negative crossing dependency edges on a path to `e`. Define `frontier_-(u)` by following positive crossing edges from `u` and stopping at negative crossing edges; `b(e)` is the maximum size of such a frontier over macros in the cone of `e`.

Depth alone is insufficient. For disjoint crossing-monotone `G_j=x_j AND y_j`, build `F=AND_j (~G_j)` as a binary chain whose aggregate is always reused positively. Then `d(F)=1`, explicit gate count is `O(k)`, but `CNFEXP(~F)` contains exactly `2^k` Cartesian clauses. Hence `BOUNDED_INVERSION_DEPTH != POLYNOMIAL_EXPANSION`.

For explicit macro-DAG volume `S>=2`, frontier width `b` and inversion depth `d`, the positive-closure recurrence gives the safe structural bound

`|CNFEXP(±e)| <= S^((b+2)^(d+1))`.

Base `d=0`: positive closure is a conjunction of at most `S` local literals. Step: `F=L AND (~F_1)...AND(~F_k)`, `k<=b`, each child depth <=d-1, so `P_d<=S+b*N_(d-1)` and `N_d<=(P_(d-1))^b`. The exponent `E_d=(b+2)^(d+1)` deliberately dominates both recurrences. No disjointness of child cones is assumed.

This is representation-only. A proof-level macro cut-elimination theorem in `(b,d)` and NW restriction-survival analysis remain open.

```text
F3_DEPTH_METRIC                   = FROZEN
F3_FRONTIER_WIDTH_METRIC          = FROZEN
F3_DEPTH_ALONE_POLY_ROUTE         = REFUTED_ANALYTICALLY
F3_BD_REPRESENTATION_BOUND        = PROVED_ANALYTICALLY
F3_PROVIDER_REPLAY                = PENDING
F3_BD_MACRO_CUT_ELIMINATION       = OPEN
F3_NW_RESTRICTION_SURVIVAL        = OPEN
ISSUE_217_FULL_ER3                = OPEN
P_VS_NP                           = OPEN
```
