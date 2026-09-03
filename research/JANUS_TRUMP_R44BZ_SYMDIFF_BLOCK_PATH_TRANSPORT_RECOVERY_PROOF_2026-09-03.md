# JANUS TRUMP R44BZ — symmetric-difference block/path transport recovery

## Claim ceiling

R44BZ gives a deterministic polynomial safe-delete primitive on one explicitly defined sibling class. It does **not** solve arbitrary signed-transport discovery and does not imply `P=NP`.

## 1. Generic fixed-block/path theorem

Let sibling CNFs `A,B` use the same active variables. Let `D=A triangle B` be the symmetric difference of their canonical clause sets.

Assume:

1. the variable co-occurrence graph of `D` has connected components `V_1,...,V_r`, each of size at most a fixed constant `b`;
2. these components cover the active variables;
3. every clause outside one component intersects exactly two components;
4. the component interaction graph induced by such clauses is a path.

We search only for **block-preserving signed transports**: a target variable in `V_i` must map to a signed source variable in the same `V_i`.

For each block there are at most

`C_b=b!*2^b`

signed permutations. For each candidate we exactly verify every target clause wholly inside the block. Thus the valid local candidate set is computed in polynomial time for fixed `b`.

For adjacent blocks `V_i,V_j`, declare candidates `p_i,p_j` compatible iff every target clause spanning those two blocks, after applying `p_i union p_j`, is tautological or contains an actual source clause. This is an exact polynomial test.

Because the interaction graph is a path, global consistency is a finite-state path CSP. Standard dynamic programming retains for each candidate on block `i` whether it has a compatible predecessor. Complexity is

`O(r*C_b^2*poly(S))`,

hence polynomial for fixed `b`.

A successful DP path gives a global signed permutation because the blocks are disjoint and every local map is bijective inside its block. A final global transport verification is performed before any deletion.

If source models transport to target models, then

`SAT(source) => SAT(target)`.

Therefore in the sibling OR the source branch can be deleted. Rank/terminality is independently checked after deletion.

If any structural condition or verification fails, the rule returns `NO_RULE_APPLICABLE`; it never returns UNSAT from failure.

## 2. Why R44BX exposes its blocks through A triangle B

In one R44AS block, with pivot removed, the two siblings differ exactly in four binary clauses:

- target-side `(x3 OR -x4)` and `(-x1 OR x4)`,
- source-side `(-x5 OR -x6)` and `(x3 OR x6)`,

up to orientation/local renaming.

Their undirected variable graph is the connected path/tree

`x1 - x4 - x3 - x6 - x5`,

so all five local variables lie in one connected component.

In R44BX:

- every orbit connector is independent of the pivot and is therefore present in both siblings;
- every common local clause is also present in both siblings;
- no pivot-dependent clause crosses blocks.

Hence all common material cancels in `A triangle B`, and the connected components of `D` are **exactly** the five-variable blocks.

No construction labels or pre-supplied `pi` are required for this recovery.

## 3. The interaction graph is recovered as a path

After block recovery, inspect clauses containing variables from more than one recovered block. R44BX creates such clauses only between consecutive blocks `i,i+1`, using the complete 12-clause orbit connector.

Thus the component interaction graph is exactly a path.

## 4. Local generator discovery is constant work

For each recovered five-variable block, enumerate all

`5!*2^5=3840`

signed maps inside that block. Verify the local target/source clauses exactly.

The R44BP map is among the accepted candidates in the `B -> A` direction. Importantly, the algorithm does not know or assume that map in advance.

## 5. Connector compatibility DP

For each adjacent block pair and each pair of accepted local candidates, verify all cross-block target connector clauses against the source formula.

The true R44BP local map used on each block is compatible because the connector set is a complete orbit under that map. Therefore the DP has at least one accepting path for every `k>=2`.

The assembled map can have support `5k`, but discovery never enumerates `5k`-variable signed permutations. It enumerates only a constant local state set and composes them by path DP.

Thus

`UNBOUNDED_RAW_TRANSPORT_SUPPORT != UNBOUNDED_TRANSPORT_DISCOVERY`.

## 6. Exact descent

For the R44BX family the already proved rank values are

`delta*(parent)=15k-13`,

`delta*(A)=delta*(B)=13k-12`.

After a verified `B -> A` transport, deleting `B` is exact for SAT decision and retains rank `13k-12`, giving strict drop

`2k-1`.

For sufficiently large `k` this rank grows linearly while current encoded size also grows linearly, so it is not rescued merely by the R44BC logarithmic maxdef terminal.

## 7. Remaining frontier

R44BZ removes the repeated-generator #312 family as a search barrier. A stronger obstruction must destroy at least one of the properties that made the DP possible, for example:

- unbounded connected components in `A triangle B`, or
- unbounded interaction width/treewidth between recovered components, or
- absence of any block-preserving transport even though a more global safe deletion might exist.

`R44BZ_POLYTIME_ON_BLOCK_PATH_CLASS != UNIVERSAL_CRITICAL_SIBLING_COVERAGE`

`TRUMP_finished=false`

`SAT_IN_P=NOT_PROVED`

`P_VS_NP=OPEN`
