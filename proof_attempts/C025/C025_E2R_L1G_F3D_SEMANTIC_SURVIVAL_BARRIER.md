# C025-E2R-L1G-F3-D — Semantic Restriction Survival Barrier

**Status:** `F3D_D0_BD_AND_RESTRICTION_SIZE_ALONE_REFUTED`.

**Provider role:** mirror of the canonical TOPA proof note. Global ER3/ER/EF and `P vs NP` remain open.

Canonical source:
`Hawkar-usls/TOPA/research/mathematics/p-vs-np/C025_E2R_L1G_F3D_SEMANTIC_SURVIVAL_BARRIER.md`

## Theorem D0

For every `B>=2`, `D>=1`, there exists an `O(BD)` frozen-B2 `AND`-extension DAG over an abstract locality hypergraph with pre-restriction negative-frontier width `b>=B` and inversion depth `d>=D`, but a one-root-variable restriction makes every crossing macro constant.

Construction:

```text
g[j,1] := z AND y_j
g[j,t] := z AND NOT g[j,t-1]       (t=2,...,D)

top_j := g[j,D]
A_2 := (NOT top_1) AND (NOT top_2)
A_k := A_(k-1) AND (NOT top_k)     (k=3,...,B)
```

Choose the locality hypergraph so no one neighborhood contains `{z,y_j}`. Then each branch is crossing. The positive aggregate closure exposes `B` negative top edges, while a path through a branch plus its aggregate edge has at least `D` negative crossing edges.

Gate count:

```text
B*D + (B-1) = O(BD).
```

Under `rho(z)=0`, every `g[j,t]` is `0` and every aggregate `A_k` is `1`. Hence the semantic crossing skeleton vanishes:

```text
|rho|=1,
b_rho=0,
d_rho=0.
```

Therefore original `(b,d)` plus restriction size alone cannot lower-bound surviving semantic `(b_rho,d_rho)`.

## Exact consequence

```text
ORIGINAL_BD != RESTRICTION_ROBUST_BD
SMALL_RESTRICTION_SIZE != SMALL_SEMANTIC_DAMAGE
```

This is an abstract locality-hypergraph barrier only. It does **not** prove that the exact Sokolov self-reduction on the frozen NW hard family collapses the real proof structure.

The next exact object is distributional semantic survival under the source self-reduction:

```text
SURV_P(B0,D0;D)
 := Pr_{rho<-D}[
      b_sem(P|rho)>=B0 AND d_sem(P|rho)>=D0
    ].
```

Here `D` must be tied to the exact self-reduction semantics; no heuristic robustness/confidence score is admitted.

Primary source boundary: Dmitry Sokolov, *Pseudorandom Generators, Resolution and Heavy Width*, CCC 2022, DOI `10.4230/LIPIcs.CCC.2022.15`, especially functional encoding / normal partial assignments and Definition 20 / Remark 21 / Algorithm 1.

## Gates

```text
F3D_D0_BD_PLUS_RESTRICTION_SIZE_ROUTE = REFUTED
F3D_D1_SEMANTIC_RESIDUAL_CLASSIFIER   = NEXT
F3D_D2_SOURCE_SELF_REDUCTION_MODEL    = NEXT
F3D_D3_RESTRICTION_RESILIENCE_THEOREM = OPEN
F3D_D4_EXPLICIT_COLLAPSE_ESCAPE       = OPEN
ISSUE_217_FULL_ER3                    = OPEN
P_VS_NP                               = OPEN
```
