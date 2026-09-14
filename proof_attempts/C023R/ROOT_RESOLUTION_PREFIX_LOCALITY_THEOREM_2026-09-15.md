# C023R theorem note — root Resolution prefix locality

Authority: `HQ_SYMBOLIC_THEOREM_NOTE__NO_GLOBAL_PROMOTION`

## Setting

Let `G` be any simple 5-regular graph on `N` vertices. Replace every edge variable by one MAJ3 block of three Boolean variables and encode each degree-5 vertex relation by its complete truth-table CNF. Use the exact frozen Policy-0A root local-Resolution pass.

The root CNF has one 15-variable factor per vertex.

## Lemma 1 — exact root clause count

For a fixed vertex, `XOR` of five independent MAJ3 outputs is balanced. Therefore exactly half of the `2^15` local assignments falsify either charge, so each vertex factor contributes exactly

`2^14`

width-15 clauses.

Different vertex factors have different 15-variable scopes in a simple graph, hence the root CNF has

`C = N * 2^14`

clauses and literal count

`L_lit = 15 * N * 2^14`.

## Lemma 2 — exact sign count of every lifted variable

Fix one coordinate `x` of one edge MAJ3 block. The edge has exactly two endpoint vertex factors.

Within either endpoint factor, after fixing `x` to either Boolean value, at least one of the other four complete MAJ3 blocks remains free and balanced. Hence exactly half of the remaining `2^14` assignments falsify the vertex relation.

Thus in each endpoint factor `x` occurs in exactly `2^13` blockers with positive sign and `2^13` blockers with negative sign. Across the two endpoint factors:

`|positive[x]| = |negative[x]| = 2^14`.

Therefore one completely processed pivot requires exactly

`P = 2^14 * 2^14 = 2^28`

complementary-pair attempts.

## Lemma 3 — root attempt budget

The frozen pass uses

`attempt_budget = max(64, 4 * literal_count)`.

Here

`B = 4 * 15 * N * 2^14 = 15 * N * 2^16 = 983040 N`.

Newly added resolvents are not re-indexed during the same pass, so the positive/negative lists and the `2^28` pair count per original pivot stay frozen throughout the root pass.

Pivots are traversed in increasing variable ID. Consequently the pass can fully process at most

`q = floor(B / 2^28) = floor(15 N / 4096)`

pivots and can enter at most one additional pivot before the attempt budget stops the pass. The addition budget can only stop it earlier.

Hence every attempted root pivot lies among the first

`floor(15 N / 4096) + 1`

lifted variable IDs.

Since a 5-regular graph has `15N/2` lifted variables, this is at most an asymptotic `1/2048` fraction of the variable IDs, plus the final partial pivot.

## Lemma 4 — accepted root resolvents are vertex-local

At root the maximum input width is 15, so the frozen width limit is 16.

Consider two width-15 root clauses resolved on pivot `x`.

### Same endpoint factor

Both clauses have the same 15-variable scope. After deleting the pivot literals, any opposite-sign occurrence on another variable makes the resolvent tautological and it is rejected. A non-tautological accepted pair must agree on every other sign, giving a width-14 resolvent supported on the same vertex factor minus `x`.

### Different endpoint factors

The two endpoint vertex scopes intersect exactly in the three variables of the shared edge block. After removing pivot `x`, a non-tautological resolvent has support size

`15 + 15 - 3 - 1 = 26`.

Since `26 > 16`, it is rejected by the frozen width limit. If another shared block literal appears with opposite signs, the candidate is tautological and is rejected even earlier.

Therefore every accepted root derived clause is supported entirely inside one endpoint vertex factor of an attempted pivot edge.

## Corollary — exact root fingerprint footprint

The first `p = floor(15N/4096)+1` variable IDs occupy at most `ceil(p/3)` earliest edge blocks, because variables are assigned in triples per normalized edge.

Thus all newly derived root clauses are contained in the stars of at most

`2 * ceil((floor(15N/4096)+1)/3)`

vertices.

This is at most `(5/2048)N + O(1)` vertices.

The theorem does NOT imply a subexponential cache fiber: the footprint is still linear in `N`, and later search levels may propagate derived-clause provenance farther. It only rules out treating the root Resolution pass as an already-global history fingerprint.

## Next obligation

The exact successor question is descendant propagation:

`C023R_DESCENDANT_DERIVED_CLAUSE_FINGERPRINT_PROPAGATION`

Determine whether repeated frozen one-pass Resolution can propagate enough history information fast enough to make cache fibers subexponential, or whether one can isolate a repeatable exact diamond cell outside the causal fingerprint cone.

No finite timing or multiplicity curve is used in this theorem.