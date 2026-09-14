# C023R — exact one-bit inherited-clause retention criterion

Date: 2026-09-15
Authority: `HQ_SYMBOLIC_LEMMA__NO_SCIENTIFIC_PROMOTION`

Parent preregistration:

`INHERITED_METADATA_RETENTION_ERASED_BITS_PREREG_v1.0.md`

## Setting

Let one MAJ3 block be `(a,b,c)`. Fix target output `z in {0,1}` and compare two equal-pair forcing histories

- `h_ab`: `a=z, b=z`,
- `h_ac`: `a=z, c=z`,

with all assignments outside this block held identical.

Both histories force `MAJ3(a,b,c)=z`; the third coordinate becomes source-semantically irrelevant, so the restricted source relation is identical.

Let `D` be one inherited canonical clause present before applying the pair-specific part of the two histories. First apply all assignments common to both histories, including `a=z` and the identical outside assignment `gamma`.

If `D` is already satisfied by the common assignment, it disappears in both histories and cannot retain the pair identity. Otherwise delete all literals falsified by the common assignment and call the resulting clause `E`.

Define for variable `x`:

- `t_z(x)` = the literal on `x` satisfied by `x=z` (`x` when `z=1`, `-x` when `z=0`);
- `f_z(x)` = the literal on `x` falsified by `x=z` (`-x` when `z=1`, `x` when `z=0`).

Canonical non-tautological clauses contain at most one of `t_z(x),f_z(x)` for each variable.

## Lemma 1 — exact raw restriction operator

For a clause `E` not already satisfied by common assignments, restriction by `x=z` acts exactly as:

- if `t_z(x) in E`, the clause is satisfied and disappears (`DROP`);
- else if `f_z(x) in E`, remove `f_z(x)` from the clause;
- else leave the clause unchanged.

Call this operator `R_{x,z}(E)`.

Therefore

`D|h_ab = R_{b,z}(E)`

and

`D|h_ac = R_{c,z}(E)`.

## Lemma 2 — exact raw equality criterion

Assume `b != c` and `E` is canonical/non-tautological.

Then

`R_{b,z}(E) = R_{c,z}(E)`

(with `DROP=DROP`) iff one of the following holds:

1. `E` contains no literal on either `b` or `c`; or
2. `E` contains both satisfied literals `t_z(b)` and `t_z(c)`, so both restrictions satisfy and drop the clause.

Proof by the exhaustive symbolic cases allowed by a canonical clause:

- mentioning neither variable leaves `E` unchanged on both sides;
- containing both satisfied literals drops on both sides;
- a satisfied literal on exactly one side gives `DROP` versus a surviving clause;
- a falsified literal on one side is deleted there but survives as an unassigned literal on the other side;
- falsified literals on both sides leave different variable-labelled residuals;
- one satisfied and one falsified literal gives `DROP` versus a surviving residual.

Thus every other sign/support pattern is a **raw pair-identity retention pattern**.

## Corollary — direct retention requires asymmetric contact with the swapped coordinates

For the same pre-history inherited clause `D`, a direct raw memory of whether `b` or `c` was the second forcing coordinate is possible only if, after common restriction, `D` still contacts at least one of `b,c` and does not contain the pair of satisfied literals that makes it disappear under both histories.

A clause whose common-restricted support is disjoint from `{b,c}` cannot directly retain the pair identity merely by later restricting `b` versus `c`.

This statement concerns one common ancestor clause. It does not rule out **exported** history information: earlier history-dependent Resolution may have produced different clauses over other variables in the two executions.

## Lemma 3 — canonical-key retention criterion for one candidate clause

Raw clause inequality is not sufficient for cache-key inequality because canonicalization deduplicates byte-identical clauses.

Let `K0` be a clause set that restricts identically under both histories after all other already-accounted common clauses are canonicalized. For candidate `D`, let

- `A` be the empty set if `D|h_ab = DROP`, otherwise the singleton containing the surviving residual clause;
- `A'` be defined analogously for `h_ac`.

The two canonical keys contributed by this common background plus `D` are equal iff

`A \ K0 = A' \ K0`.

Equivalently, this candidate is a **key-level retention witness** exactly when

`A \ K0 != A' \ K0`.

Thus a raw distinguishing residual that is already present in the common key basis carries no additional byte-level information.

For a full collection of inherited clauses, the exact criterion is the symmetric difference of the two complete canonical restricted clause sets. Provenance identities do not matter to the cache: only surviving byte clauses matter.

## Lemma 4 — deterministic future consequence

Historical Policy-0A after cache-key formation is deterministic as a function of the byte-identical key: local Resolution budgets/order, post-UP, branch-variable choice and child generation are all key-determined.

Therefore if the two histories reach one byte-identical key after the forcing-pair difference has been erased, no future transition can recover which pair was used. Pair identity is permanently forgotten from that point onward.

Conversely, persistence of the bit requires at least one byte-level key distinction at every stage until the bit has been exported into another distinguishing clause/key feature.

## Captain Obvious consequence — the true one-bit subgate

The only unresolved way for Policy-0A to remember a forcing-pair identity after source-semantic stifling is **history-bit export**:

> before the swapped block coordinates disappear or their direct distinguishing clauses are dropped/deduplicated, does budget-truncated/inherited Resolution export the pair identity into a surviving clause over other variables?

Complete source-only pivots cannot provide this export: they are already proved stifling-transparent after equal source-semantic restriction.

Therefore the next exact gate is

`C023R_HISTORY_BIT_EXPORT_BEFORE_STIFLING`

and its decisive falsifier is a reachable forcing-pair swap for which every candidate distinguishing inherited clause either drops, canonical-deduplicates, or fails to export the identity before the histories reconverge.

## Verdict

`PASS_EXACT_ONE_BIT_RESTRICTION_AND_KEY_RETENTION_CRITERION__EXPORT_GATE_OPEN`

## Claim ceiling

No assertion of one-bit reachable retention or forgetting is made here. No asymptotic cache-fibre bound follows yet.
