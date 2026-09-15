# TRUMP — Scoped Derived Two-Relation Boundary Factor Theorem Seal

Date: 2026-09-15

Authority class: `SCOPED_THEOREM_AND_IMPLEMENTATION_CHECK__NO_GLOBAL_PROMOTION`

Verdict:

`PASS_SCOPED_BICAMERAL_OVERWIDTH_DERIVED_TWO_RELATION_BOUNDARY_FACTOR_V1_1`

## Frozen scope

Let a canonical explicit Boolean relation instance admit the frozen polynomially discovered variable-only cut `B`, with parent terminal `OPEN_MINCUT_BRANCH_BUDGET` and zero raw `2^|B|` enumeration. After deleting `B`, every constraint-bearing component in this theorem has either one relation or exactly two relations. For every two-relation component `C={R1,R2}`, `scope(R1) union scope(R2)` contains all of `B`. At least one admitted positive component may have no raw relation containing all of `B`.

## Exact derived component relation

For a singleton component with full-cut visibility, define `P_C` by projecting its explicit raw rows to `B`.

For a two-relation component define

`P_C = project_B(R1 natural_join R2)`.

The natural join checks equality on every shared variable. No other compatibility rule is used.

For every `sigma in P_C`, the construction stores one explicit original row witness (singleton) or one explicit compatible row pair `(r1,r2)` (two-relation component).

## Exactness lemma

For every admitted component `C` and cut state `sigma`:

`sigma in P_C` iff the original relations of `C` have a simultaneous extension whose restriction to `B` is `sigma`.

For singleton components this follows directly from projection of an original row. For two-relation components it follows directly from natural-join compatibility on every shared variable plus projection of the merged compatible pair.

After deleting `B`, distinct constraint components have disjoint private-variable sets. Therefore a common cut state can be extended independently inside each component. Hence for

`H = intersection_C P_C`,

we have, within the frozen scope:

`F is SAT iff H is nonempty`.

A member of `H`, together with the stored original row/row-pair witnesses, reconstructs one complete original assignment which is replayed against every raw relation.

## Polynomial envelope

For a two-relation component:

`|P_C| <= number_of_compatible_pairs <= |R1| * |R2|`.

The frozen candidate uses at most `|R1|*|R2|` row-pair compatibility checks. Each explicit row count is bounded by the canonical explicit input length `L`, so each two-relation component has an `O(L^2 * arity)` construction bound and `O(L^2)` output bound.

There are at most `O(L)` encoded relations/components. A conservative whole-gate envelope is therefore one fixed polynomial, e.g. `O(L^3 * arity)`, plus inherited polynomial cut discovery, support intersection, reconstruction and verification.

The theorem explicitly forbids an arbitrary relation-join chain. Any component containing three or more relations returns `OPEN_COMPONENT_RELATION_COUNT_GT_2` before a join chain is attempted.

## Machine evidence

GitHub Actions run: `34919310274`

Job: `104223627451`

Workflow head: `66e8055ad2d5aedf08379decc50e112779bee714`

All v1.1 independent-check obligations passed.

Positive receipt:
- parent: `OPEN_MINCUT_BRANCH_BUDGET`
- canonical cut: variables `0..19`
- predecessor full-anchor join-tree gate: `OPEN_NO_FULL_CUT_ANCHOR`
- components: `[[0],[1,2]]`
- row-pair comparisons: `9`
- maximum component row-pair product bound: `9`
- raw cut-cube enumeration: `0`
- unbounded join chains: `0`
- effective global support size: `1`
- witness replay: PASS

Negative controls:
- empty pair support -> `EXACT_UNSAT_BY_EMPTY_DERIVED_COMPONENT_SUPPORT`
- three-relation component -> `OPEN_COMPONENT_RELATION_COUNT_GT_2`
- incomplete two-relation cut cover unit control -> `OPEN_INCOMPLETE_TWO_RELATION_CUT_COVER`
- injected hint -> `REJECT_RAW_INPUT`
- tampered provenance -> `REJECT_TAMPERED_PROVENANCE`

The immutable first v1 run failure `FAIL_INFRASTRUCTURE_SERIALIZATION_BEFORE_RECEIPT` remains preserved. v1.1 repaired JSON-safe provenance serialization only; frozen v1 mathematical candidate blob `1047351df47ed5f326eef2650da0c9f5ee0f2fda` remained unchanged.

## Claim ceiling

This seal does **not** establish polynomial boundary compression for components of arbitrary relation count, arbitrary cyclic elimination, arbitrary unseen invariant discovery, general SAT in P, or P=NP/P!=NP.

`P_VS_NP = OPEN`

`GENERAL_SAT_IN_P = NOT_PROVED`

`CONNECTED_MIXED_CORE_SOLVED = NO`

`GENERAL_MULTI_RELATION_BOUNDARY_COMPRESSION = NOT_PROVED`
