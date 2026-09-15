# TRUMP Bicameral Canonical Minimum Variable-Cut Log-Width Explanation — v1.1 scoped theorem

Authority: `SCOPED_THEOREM__NO_GLOBAL_PROMOTION`

## Immutable predecessor failure

The first frozen run remains immutable:

- preregistration `80244eba21a7965733f6c705678fca88b4dc2c25`
- workflow head `34972a5e76d3b474d5a55ec217fc97b7a859895d`
- Actions run/job `34915543761 / 104212241471`
- verdict `FAIL_BICAMERAL_CANONICAL_MINCUT_LOGWIDTH_EXPLANATION_INDUCTION`
- failure class `PREREGISTERED_POSITIVE_CONTROL_OUT_OF_SCOPE__NOT_MINCUT_DISCOVERY_FAILURE`

The v1.0 positive `OR4 + EVEN_XOR4` was already ONE_VALID and therefore correctly admitted by a simpler sealed basis before min-cut execution.

## v1.1 frozen lineage

- preregistration: `5f252316a74cbf431ad81da8528d58669e96ffa8`
- frozen v1 engine: `dd9f6d0196aa5d4189ef7d8dd674dbe10e7a392d` / blob `c0c612676e39241b95026c15823e7af6b3da8f0d`
- v1.1 wrapper: `1d6e931cca17716efdd9c6fa9e109fdf56edae62`
- v1.1 independent checker: `4531176d5311605be6ffa14d187e5ef5a3f0921c`
- workflow head: `bafdec651689d5ba459cbb150f7603c07e920360`
- Actions run/job: `34915753122 / 104212878620`

## Scoped theorem

Let `F` be a canonical raw explicit Boolean-relation object with canonical byte length `L`. Construct its bipartite variable–constraint incidence graph. For each unordered pair of constraint nodes `(c_i,c_j)`, form a node-split directed network in which variable nodes have split capacity 1, constraint nodes have split capacity `INF=V+1`, and incidence arcs have capacity `INF`. Compute a deterministic minimum `c_i-c_j` flow/cut and retain only cuts whose variable set actually separates constraint-bearing incidence.

Choose the canonical record by:

`(cut_size, sorted_cut_variables, source_constraint_index, target_constraint_index)`.

This procedure is polynomial because it performs `O(C^2)` polynomial max-flow computations on a graph polynomial in the explicit input size. It does not enumerate variable subsets.

Let the discovered canonical cut be `S`, `k=|S|`. Before any Boolean assignment enumeration, require:

`2^k <= L`.

If the budget fails, return `OPEN_MINCUT_BRANCH_BUDGET` with zero branch enumeration.

If the budget passes, enumerate exactly the `2^k` assignments `sigma in {0,1}^S`. For every `sigma`, construct the exact simultaneous relational restriction `F|S=sigma` by filtering explicit allowed tuples and deleting assigned coordinates. Each branch must independently replay through a previously sealed exact compositional-basis carrier or terminate as exact SAT/UNSAT.

If every branch admits, then:

`SAT(F) <=> OR_{sigma in {0,1}^S} SAT(F|S=sigma)`

and the complete discovery + restriction + replay lifecycle is polynomial in `L`: cut discovery is polynomial, the number of branches is at most `L`, and each branch performs only polynomial explicit-table work already sealed in predecessor theorems.

## v1.1 controls

The corrected positive is a connected mixed pair of arity-4 relations: an embedded OR2 carrier and an embedded EVEN_XOR3 carrier sharing variables `[0,1,2]` with separate leaf variables. The combined language has no single frozen Schaefer basis and the size-2 parent gate remains OPEN.

Independent Dinic and candidate Edmonds–Karp agree on canonical cut `[0,1,2]`, `k=3`. Canonical input length is `L=230`, hence branch budget `8<=230`. Exactly 8 branches are replayed and all admit. Terminal: `ADMIT_EXACT_LOGWIDTH_MINCUT_EXPLANATION`.

The overwidth control has independent canonical cut size 20, `L=576`, and branch budget `2^20=1048576>576`; it returns `OPEN_MINCUT_BRANCH_BUDGET` before assignment enumeration.

## Verdict

`PASS_SCOPED_BICAMERAL_CANONICAL_MINCUT_LOGWIDTH_EXPLANATION_INDUCTION_V1_1`

This establishes a scoped growing-separator mechanism for explicit-table raw cores; it does not establish a solver for arbitrary connected mixed cores or arbitrary CNF.

## Firewalls

- `P_VS_NP = OPEN`
- `GENERAL_SAT_IN_P = NOT_PROVED`
- `CONNECTED_MIXED_CORE_SOLVED = NO`
- `ARBITRARY_UNSEEN_INVARIANT_DISCOVERY = NOT_PROVED`
- `GLOBAL_APMA_FRONTIER_ADVANCE = NONE_PENDING_HQ_REVIEW`
