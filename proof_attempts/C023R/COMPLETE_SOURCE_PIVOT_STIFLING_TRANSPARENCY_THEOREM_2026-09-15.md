# C023R P2 — complete source-pivot stifling transparency theorem

Date: 2026-09-15
Authority: `HQ_SYMBOLIC_LEMMA__NO_SCIENTIFIC_PROMOTION`

Parent preregistration:

`DESCENDANT_DERIVED_CLAUSE_FINGERPRINT_PROPAGATION_PREREG_v1.0.md`

## Setting

Let `P` be any Boolean relation on variable set `X`, and let `C(P)` be the JANUS exact truth-table CNF: one full blocking clause for every falsifying total assignment of `P`.

For a pivot `x in X`, let `FullRes_x(C(P))` denote the complete set of non-tautological ordinary resolvents obtained from every `x`-positive / `x`-negative parent pair in `C(P)`, with no budget truncation. Because all source blockers have the same full scope, every non-tautological such resolvent has width `|X|-1`, so the historical local width limit `max_width+1` does not reject it.

The historical pass does not re-index additions in the same pass, so a set of fully processed source-only pivots is exactly a union of independent one-pivot additions from the pass-entry source clauses.

## Lemma 1 — exact form of a complete source pivot

Fix an assignment `y` to `X \ {x}`.

There is a non-tautological resolvent blocking exactly `y` iff **both** total extensions

`y union {x=0}` and `y union {x=1}`

falsify `P`.

Proof.

A source blocker is uniquely indexed by one falsifying total assignment. Two blockers containing complementary literals on `x` produce a non-tautological resolvent only when their assignments agree on every other variable; otherwise some other variable appears with complementary signs and the candidate is tautological. Thus a legal non-tautological pair is exactly the pair of falsifying extensions of one `y`. Resolving deletes the complementary `x` literals and leaves the blocker of `y`. QED.

Equivalently, `FullRes_x(C(P))` is the exact blocker family for the set

`{ y : P(y,x=0)=0 and P(y,x=1)=0 }`.

## Lemma 2 — restriction when the pivot remains live

Let `alpha` be a partial assignment not fixing `x`. Restrict and canonicalize the union

`C(P) union FullRes_x(C(P))`.

By the exact truth-table restriction lemma, the source part becomes `C(P|alpha)`.

By Lemma 1, a surviving pivot resolvent is indexed by a remaining assignment `z` for which both `x` extensions falsify `P|alpha`. Therefore its restricted form is exactly a member of `FullRes_x(C(P|alpha))`, and every such member has a unique extension consistent with `alpha`.

Hence

`(C(P) union FullRes_x(C(P))) | alpha`

canonicalizes to

`C(P|alpha) union FullRes_x(C(P|alpha))`.

So complete source-pivot Resolution commutes exactly with restriction while the pivot remains live.

## Lemma 3 — restriction when the pivot is already fixed

Now let `alpha` fix `x=t`.

Take any source-pivot resolvent indexed by `y` such that both `x` extensions falsify `P`.

- if `y` is inconsistent with the other assignments in `alpha`, its blocker is satisfied and disappears;
- if `y` is consistent, then the chosen extension `y union {x=t}` falsifies `P`, so after restriction the resolvent becomes exactly the blocker of the corresponding falsifying row of `P|alpha`.

Therefore every surviving complete `x`-pivot resolvent is already present in `C(P|alpha)` and contributes no new canonical clause.

## Theorem — semantic-equal restrictions erase complete source-only pivot fingerprints

Let `alpha` and `alpha'` assign the same variable set (possibly with different values) and suppose

`C(P|alpha) = C(P|alpha')`

byte-for-byte after the frozen canonicalization.

Let `S` be any set of pivots that are fully processed using **only the pass-entry exact source clauses**. Define

`Q = C(P) union Union_{x in S} FullRes_x(C(P))`.

Then

`canonical(Q|alpha) = canonical(Q|alpha')`.

Proof: apply Lemma 2 to pivots that remain live and Lemma 3 to pivots fixed by the histories. For live pivots, the complete resolver family is a deterministic function of the identical restricted relation; for fixed pivots it adds nothing beyond the identical source residual. Union and canonicalization preserve equality. QED.

## MAJ3 stifling corollary

For one MAJ3 block `(a,b,c)`, the histories

`a=0,b=1`

and

`a=1,b=0`

leave exactly the same restricted gadget function: the remaining coordinate `c`.

Therefore, inside any exact vertex truth-table factor, **all fully processed source-only pivot resolvents** are transparent to this `01/10` versus `10/01` collision after both assigned coordinates are removed.

In particular:

- complete pivots on `a` or `b` may leave surviving resolvents, but after the stifling restriction those clauses are duplicates of exact source-residual blockers;
- complete pivots on `c` or on another source coordinate commute with the two semantically equal restrictions and yield the same canonical restricted addition set.

Thus the earlier intuition that a complete local Resolution pivot automatically fingerprints a MAJ3 history bit is false.

## Historical finite-budget consequence

In one historical `resolution_trace` pass, pivots are processed in a fixed sequence until a global attempt/addition budget terminates the pass. Therefore there can be:

- zero or more **fully processed** pivots;
- at most **one partially processed** pivot where the budget stops;
- no processed pivots after that point.

For pass-entry clauses that are still exact source-factor clauses, the theorem proves that fully processed source-only pivots cannot distinguish two histories once those histories induce the same restricted source relation.

Hence any fresh non-semantic fingerprint created by the current pass must come from at least one of:

1. the single budget-truncated partial pivot;
2. a resolvent involving inherited/previously-derived clauses rather than only exact source blockers;
3. a cross-factor interaction whose parents are not one exact relation table;
4. a deterministic unit/branch consequence caused by such asymmetric clauses.

## Root q=4 strengthening

The separately proved root-prefix locality theorem shows that accepted root cross-endpoint resolvents are rejected by width and all accepted full-pivot root additions are endpoint-vertex-local source-source resolvents.

Therefore, at the **root** of the frozen degree-5 MAJ3-Tseitin family, complete processed pivots are stifling-transparent. Before any inherited clauses exist, the only possible current-pass source of a non-semantic history fingerprint is the at-most-one partially processed budget-stop pivot (plus consequences of its incomplete addition prefix).

This does not yet prove that a cache diamond exists: the actual branch variables must still align with a stifling pair, and the partial-pivot clauses may distinguish them.

## P2 verdict

`PASS_COMPLETE_SOURCE_PIVOTS_ARE_STIFLING_TRANSPARENT__FINGERPRINT_SOURCES_LOCALIZED`

The positive `NEAR_INJECTIVE_INHERITED_RESOLUTION_FINGERPRINT` route is therefore substantially narrowed: full source-only local Resolution is not the missing fingerprint mechanism.

## Next exact obligation

`C023R_PARTIAL_PIVOT_AND_INHERITED_CLAUSE_FINGERPRINT_GATE`

Determine whether the single partial-pivot clause prefix and its descendant inherited closure can preserve a linear number of otherwise-stifled history bits, or whether its influence remains too limited and exact merge cells compose.

No finite asymptotic fitting is authorized.
