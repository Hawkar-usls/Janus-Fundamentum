# TRUMP — Raw Relation Schaefer Basis Induction

Date: 2026-09-15

Authority class: `SCOPED_THEOREM_AND_IMPLEMENTATION_CHECK__NO_GLOBAL_PROMOTION`

Verdict:

`PASS_SCOPED_RAW_RELATION_SCHAEFER_BASIS_INDUCTION`

## Scope

Input is an explicit finite Boolean constraint language presented only by raw relation tables:

- a finite list of Boolean variables;
- constraints with `id`, `scope`, and the complete list `allowed` of satisfying tuples;
- no trusted carrier/class/kind label.

The basis library is frozen to exactly six Boolean Schaefer predicates:

1. `ZERO_VALID`;
2. `ONE_VALID`;
3. `HORN` via coordinatewise AND closure;
4. `DUAL_HORN` via coordinatewise OR closure;
5. `BIJUNCTIVE` via coordinatewise majority closure;
6. `AFFINE` via coordinatewise minority/XOR3 closure.

## Theorem

Let the distinct explicit raw relations be `R_1,...,R_m`. Let `s_i=|R_i|` and let `a_i` be the arity of `R_i`.

There is a deterministic label-blind algorithm that:

1. canonicalizes and content-binds the complete explicit relation surface;
2. computes the six frozen closure predicates directly from the allowed tuples;
3. emits a replayable per-relation and whole-language fingerprint;
4. admits one frozen basis iff its defining predicate holds for every relation in the complete bound language;
5. otherwise returns `OPEN_NO_SCHAEFER_BASIS` before any SAT solver or carrier execution.

Its discovery and replay cost is bounded by

`O(sum_i s_i^3 a_i)`

for this frozen six-predicate library, hence polynomial in the explicit raw relation-table input size.

No enumeration of the global variable-assignment cube is required.

## Exactness argument

The closure predicates are definitions over the complete explicit relation tables, not learned labels. For each relation:

- 0-validity/1-validity are direct membership checks;
- Horn/dual-Horn are exhaustively checked over all tuple pairs under AND/OR;
- bijunctive/affine are exhaustively checked over all tuple triples under majority/minority.

Therefore a positive basis certificate is adequate for the entire bound explicit relation surface, and an independent checker can replay the same finite closure definitions from source bytes alone.

The semantic-surface identity intentionally ignores relation IDs, constraint ordering and tuple ordering. Those changes therefore cannot alter the induced basis fingerprint.

## Fail-closed rule

If no single frozen basis predicate holds for the complete language, execution is unauthorized and the gate returns:

`OPEN_NO_SCHAEFER_BASIS`.

This was exercised on the fixed mixed language `{OR2, EVEN_XOR3}`. It remains outside all six frozen classes, consistent with the previously sealed Schaefer mixed-carrier barrier.

## Source-bound implementation evidence

Preregistration commit:

`42c2929a9bfc3557ac1b2684ee1957ac0a94d398`

Candidate commit:

`985c168801b1762fa736ae11d87becb0e33ebbb3`

Independent checker commit:

`ff8c56f966cba529823bbc936fa411734875f308`

Workflow head:

`d08ad24111e321c75c7a5bf1d00f51ae595b5a26`

GitHub Actions run:

`34913060164`

Job:

`104204627041`

Implementation crosschecks included all 15 nonempty binary Boolean relations and 12 preregistered ternary samples. These finite checks are implementation/falsifier evidence only; the scoped theorem follows from the explicit closure definitions and polynomial operation count above.

## Imported architectural mechanics

The development contract was informed by source-bound mechanics harvested from:

- AIFC: semantic abstraction adequacy must precede authority/execution;
- Janus_Genesis: complete input binding before routing/mode split;
- janus-io-public: provenance/claim separation for the evidence ledger;
- Janus-Demiurge: adaptive difficulty only as a falsifier curriculum, never scientific authority.

The exact algebraic closure primitives themselves are reused from the already sealed Fundamentum Schaefer barrier implementation.

## What this closes

Within the frozen six-class library and explicit relation-table representation, `carrier labels` are no longer required. Membership recognition and exact admission are automatically derived from semantics in polynomial time.

In other words, this closes the subproblem:

`RAW_EXPLICIT_RELATION_SEMANTICS -> RECOGNIZE_ONE_OF_FIXED_SIX_EXACT_BASES`

## What remains open

This theorem does **not** synthesize a new basis outside the frozen library and does not find arbitrary decompositions, quotients, backdoors, provenance morphisms or novel invariants.

For general raw CNF, especially a connected mixed language outside all six classes, the remaining problem is to synthesize a compositional exact explanation from known primitives or discover a genuinely new exact carrier without hiding exponential work.

Recommended successor surface:

`RAW_STRUCTURE_TO_COMPOSITIONAL_BASIS_EXPLANATION`

followed, if that fails on a connected mixed core, by:

`UNSEEN_BASIS_SYNTHESIS_BEYOND_FIXED_LIBRARY_FALSIFIER_GATE`.

## Scientific firewall

`P_VS_NP = OPEN`

`GENERAL_SAT_IN_P = NOT_PROVED`

`ARBITRARY_UNSEEN_INVARIANT_DISCOVERY = NOT_PROVED`

`GLOBAL_APMA_FRONTIER_ADVANCE = NONE`
