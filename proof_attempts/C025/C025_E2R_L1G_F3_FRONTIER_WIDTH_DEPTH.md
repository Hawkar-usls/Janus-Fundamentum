# C025-E2R-L1G-F3 — Negative-frontier width × inversion depth

**Status:** `ANALYTICAL_F3_BC_COMPLETE_PENDING_PROVIDER_REPLAY`.

Define `d(e)` as the maximum number of negative crossing dependency edges on a path to `e`. Define `frontier_-(u)` by following positive crossing edges and stopping at negative crossing edges; `b(e)` is the maximum frontier size over macros in the cone.

## Depth-alone barrier

For disjoint crossing-monotone `G_j=x_j AND y_j`, build `F=AND_j (~G_j)` as a binary chain with the aggregate reused only positively. Then `d(F)=1` and gate count is `O(k)`, while exact structural `CNFEXP(~F)` has `2^k` Cartesian clauses. Therefore bounded inversion depth alone does not imply polynomial expansion. The family has `b(F)=k`.

## Paired representation

Let explicit macro volume be `S>=2`, frontier width at most `b`, inversion depth at most `d`, and

`E_d=(b+2)^(d+1)`.

The positive-closure normal form `F=L AND (~F_1)...AND(~F_k)`, `k<=b`, gives

`P_d<=S+b*N_(d-1)` and `N_d<=(P_(d-1))^b`,

hence

`|CNFEXP(±e)| <= S^E_d`.

## Paired pure-Resolution cut elimination

Use the F2 pure `restrict -> refute -> lift` context lemma. Let `R_d` bound a pure Resolution refutation of `P(F) union N(F)`.

After resolving local complement literals, eliminate at most `b` frontier children by lifted inductive complement refutations:

`R_d <= S^(E_d+1) + b*S^E_d*R_(d-1)`.

The deliberately loose induction `R_d<=S^(3E_d)` holds because `E_d=(b+2)E_(d-1)` and `b<=S`.

An ER3 source line expands into at most `S^(3E_d)` local clauses. Simulating each macro pivot with the complement refutation and multiplying by at most `S` source proof nodes yields

`S_local <= S^(7 (b+2)^(d+1))`.

## NW hard-family consequence

For the established polynomial-input existential NW-parity family, local-functional Resolution requires `L(N)>=exp(N^eta)` for some fixed `eta>0` on sufficiently large family members. If `S<=N^c`, then the paired simulation forces

`(b+2)^(d+1) * O(log N) >= N^eta`,

hence

`(d+1) log(b+2) = Omega(log N)`.

Thus every polynomial-size escape must be either sufficiently broad in negative-frontier width or sufficiently deep in serial polarity inversion. This does not imply a superpolynomial total-extension lower bound.

```text
F3_DEPTH_METRIC                    = FROZEN
F3_FRONTIER_WIDTH_METRIC           = FROZEN
F3_DEPTH_ALONE_POLY_ROUTE          = REFUTED_ANALYTICALLY
F3_BD_REPRESENTATION_BOUND         = PROVED_ANALYTICALLY
F3_BD_COMPLEMENT_REFUTATION        = PROVED_ANALYTICALLY
F3_BD_MACRO_CUT_ELIMINATION        = PROVED_ANALYTICALLY
F3_WIDTH_DEPTH_TRADEOFF            = DERIVED_FROM_SOURCE_LOWER_BOUND
F3_PROVIDER_REPLAY                 = PENDING
F3_NW_RESTRICTION_SURVIVAL         = OPEN / NEXT
ISSUE_217_FULL_ER3                 = OPEN
P_VS_NP                            = OPEN
```
