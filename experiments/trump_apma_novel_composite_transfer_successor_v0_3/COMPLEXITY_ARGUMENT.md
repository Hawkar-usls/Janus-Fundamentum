# Symbolic complexity obligation — successor v0.3 freeze preparation

Let `N` be the original encoded input length, `M` the number of normalized clauses, `V` the number of variables, and `K` the number of discovered leaves. Thus `M,V,K <= N`.

## Construction and discovery

Frozen canonicalization is polynomial and the source-to-normalized audit is `O(N log N)` including deterministic sorting.

For fixed `rho <= 3`, separator candidates at any decomposition node are bounded by
`C(V,1)+C(V,2)+C(V,3) <= V^3 <= N^3`.

Each candidate separator is evaluated by a deterministic DSU pass over the node's literal occurrences. No partition of private islands is enumerated. A conservative bound per candidate is `O(N alpha(N))`.

Every accepted split partitions the current normalized clauses into at least two nonempty proper children. Therefore `K <= M`, the number of internal nodes is at most `K-1`, and total recursive nodes are at most `2M-1 <= 2N-1`.

Hence a conservative discovery bound is `T_discover = O(N^5 alpha(N))`.

## Boundary scopes and GYO

Because leaf clauses form an exact partition of the normalized clauses, total leaf literal occurrences are `O(N)`. Building variable-to-leaf incidence and complete shared-variable scopes is `O(N log N)` conservatively; any leaf boundary above 3 is rejected before relation enumeration.

There are at most `K <= N` relation identities and each accepted scope has size at most 3. Deterministic GYO performs at most `3K` vertex removals and `K-1` relation-edge removals. The implementation's conservative repeated subset scan is `O(K^3) = O(N^3)`.

Join-tree reconstruction records exactly `K-1` parent links and uses the exact original-scope intersection for each tree separator. Running-intersection verification is `O(N^2)` conservatively.

## Frozen local relation work

Each boundary has at most three variables, so unchanged `leaf_relation` enumerates at most `2^3 = 8` boundary tuples per leaf.

The frozen local path performs unit conditioning plus a fixed finite primitive portfolio. From the historical implementation, a conservative per-leaf bound is `O(s^3)` for leaf encoded size `s` (the dominant primitive is bounded matching/graph work). Since leaf clause/literal content partitions the normalized input, `sum s_i <= O(N)`, hence `sum s_i^3 <= O(N^3)`.

Therefore `T_relation = O(N^3)` with at most `8K <= 8N` tuple records.

## Frozen transfer, reconstruction, verifier, certificate

Each relation has at most 8 allowed tuples and every join-tree separator has width at most 3. With `K-1` tree edges, unchanged bottom-up `transfer_join` has conservative `T_join = O(N^2)` under its list-based adjacency lookup.

On a valid running-intersection tree, a feasible parent tuple guarantees independently feasible child subtrees. The unchanged witness reconstruction therefore examines at most the constant-size relation table per node rather than performing unbounded global assignment search; conservatively `T_reconstruct = O(N^2)`. Final normalized and source replay are `O(N)`.

The candidate verifier recomputes deterministic discovery, exact scopes, GYO, running intersection, every frozen leaf relation, frozen transfer, and SAT source replay. Therefore `T_verify = O(N^5 alpha(N))`, dominated by discovery replay.

The certificate stores source-normalization provenance, a clause-partition leaf list, at most 3 boundary variables per leaf, at most 8 relation tuples/certificates per leaf, `O(N)` GYO operations, one tree, and witnesses. With encoded identifiers, a conservative byte bound is `O(N log N)`; there is no exponential assignment table.

Thus
`T_construct + T_discover + T_relation + T_join + T_reconstruct + T_verify = O(N^5 alpha(N))`.

This bound assumes only the already-frozen finite local primitive portfolio and fixed `rho <= 3`; it uses no blind population property, no private-island partition enumeration, no unbounded separator backtracking, and no exhaustive assignment enumeration over the union of shared variables.
