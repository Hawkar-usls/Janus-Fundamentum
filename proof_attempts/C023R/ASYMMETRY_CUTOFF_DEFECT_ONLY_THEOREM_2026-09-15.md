# C023R — asymmetry can enter only through partial-pivot cutoff defects

Date: 2026-09-15
Authority: `HQ_SYMBOLIC_LEMMA__NO_SCIENTIFIC_PROMOTION`

Parent object:

`SIBLING_MERGE_TAIL_BALANCE_CRITERION_2026-09-15.md`

## Sign-flip involution

Fix a live variable `x`. Define `sigma_x` on canonical clauses by flipping only the sign of the literal on `x`:

- `x` becomes `-x`;
- `-x` becomes `x`;
- clauses not containing `x` are fixed.

Extend `sigma_x` pointwise to clause sets.

Call a CNF `x-sign-symmetric` when

`sigma_x(S)=S`.

This is stronger than the previously defined tail-balance condition `A_x=empty`, but it is easy to propagate exactly and is sufficient for sibling equality when branching on `x`.

## Lemma 1 — an irrelevant coordinate in an exact truth-table CNF is sign-symmetric

If Boolean relation `P(x,Y)` is independent of `x`, every falsifying row `y` of the reduced relation contributes the pair of blockers

`B_y union {x}` and `B_y union {-x}`.

Therefore its exact truth-table CNF is exactly `x-sign-symmetric`.

This is the correct representation-level form of semantic irrelevance: `x` is retained syntactically, but in perfect sign-paired form.

## Lemma 2 — complete Resolution on a pivot `y != x` preserves sign symmetry

Assume pass-entry clause set `S` is `x-sign-symmetric`. Consider one complete Resolution pivot `y != x` over all complementary parent pairs indexed at pass entry.

Map every attempted pair `(C,D)` to

`(sigma_x(C), sigma_x(D))`.

Because `S` is invariant, this is a bijection on the complete set of `y`-complementary parent pairs.

Ordinary Resolution on pivot `y` commutes with `sigma_x`:

`Res_y(sigma_x(C),sigma_x(D)) = sigma_x(Res_y(C,D))`.

The historical acceptance filters are also invariant under `sigma_x`:

- tautology status is preserved;
- clause width is preserved;
- canonical duplicate status is paired under the involution when the full pivot is completed.

Hence the complete set of accepted new `y`-resolvents is `x-sign-symmetric`.

## Lemma 3 — Resolution on pivot `x` cannot create x-asymmetry

Every legal resolvent on pivot `x` contains neither `x` nor `-x` and is therefore fixed by `sigma_x`.

Adding any number of such neutral clauses to an `x-sign-symmetric` CNF preserves `x-sign-symmetry`.

## Lemma 4 — restriction by another variable preserves sign symmetry

Let `y != x`. Simplification by `y=b` commutes with `sigma_x` because the involution does not alter literals on `y`.

Therefore, if `S` is `x-sign-symmetric`, then every noncontradictory restricted child

`S|_{y=b}`

is also `x-sign-symmetric` after canonicalization.

## Lemma 5 — noncontradictory unit propagation preserves sign symmetry

Suppose current CNF is `x-sign-symmetric`.

A unit clause on a variable `y != x` has a sign-flipped partner that is identical because `sigma_x` fixes clauses not containing `x`; restricting that unit assignment preserves symmetry by Lemma 4.

A unit `(x)` would imply the partner unit `(-x)` by sign symmetry, giving immediate contradiction. Therefore a noncontradictory unit-propagation sequence cannot assign `x` from an `x-sign-symmetric` state.

Repeated noncontradictory unit propagation on other variables preserves `x-sign-symmetry`.

## Lemma 6 — branching on x from a sign-symmetric state gives exact sibling equality

If the post-UP state `S` is `x-sign-symmetric`, positive and negative clauses occur in exact sign-flip pairs with identical tails. Thus

`T_+(x)=T_-(x)`

and the branch asymmetry basis `A_x` is empty.

By the tail-balance theorem, raw children under `x=0` and `x=1` are byte-identical. Their deterministic recursive pre-UP therefore produces the same cache key or the same terminal result.

Hence selecting `x` in an `x-sign-symmetric` state creates an exact sibling merge edge pair.

## Theorem — first-entry asymmetry source

Assume a historical Policy-0A state begins a local Resolution pass with a CNF that is `x-sign-symmetric`.

Historical pivots are processed sequentially. Any number of fully completed pivots preserve `x-sign-symmetry` by Lemmas 2 and 3.

If the finite attempt/addition budget stops the pass:

- there is at most one partially processed pivot `p*`;
- if `p*=x`, every accepted addition is x-neutral and symmetry remains;
- if `p*!=x`, the processed **prefix** of the complete `p*` pair set need not be closed under the `sigma_x` pairing from Lemma 2, because numeric clause/pair ordering plus budget cutoff may include one member of a sign-flip orbit without its partner.

Therefore the only way this pass can create a new x-sign asymmetry from an x-sign-symmetric entry state is:

`PARTIAL_PIVOT_CUTOFF_ON_p* != x`.

Post-UP cannot create a new defect by Lemma 5.

All x-asymmetry seen later in descendants must therefore be either:

1. inherited from an earlier partial-pivot cutoff defect; or
2. newly injected by the current state's single partial pivot on a variable other than x.

Complete pivots, ordinary restrictions on other variables and noncontradictory UP cannot spontaneously create the defect.

## Defect lineage interpretation

For each candidate stifled irrelevant variable `x`, its byte-level asymmetry basis has an exact causal provenance:

`A_x != empty`

must descend from one or more historical budget-cutoff defects on pivots distinct from `x`.

Thus the vague phrase "inherited clauses may remember history" is sharpened to:

> all value-asymmetric memory of a semantically irrelevant `x` is carried by descendants of partial-pivot cutoff defects.

This theorem does not bound how much information one cutoff defect can ultimately encode. A single partial prefix may create many clauses, and later Resolution can propagate their influence through a connected provenance cone.

## Captain Obvious next missing link

`C023R_PARTIAL_PIVOT_DEFECT_INFORMATION_CAPACITY`

Exact target:

Bound, or constructively lower-bound, the number of independent stifled-variable asymmetry bits that can be supported by descendants of the sequence of historical partial-pivot cutoff defects along one reachable execution ancestry.

Positive route needed for cache-fibre ceiling:

`independent_asymmetry_bits = o(L)`.

Decisive falsifier route:

an exact infinite reachable construction in which `Omega(L)` independently branch-relevant variables have nonzero asymmetry bases generated by cutoff-defect lineages, or alternatively `Omega(L)` variables remain defect-free and are actually selected, yielding serial sibling merges.

## Verdict

`PASS_ASYMMETRY_SOURCE_LOCALIZATION_TO_PARTIAL_PIVOT_CUTOFF_DEFECTS__INFORMATION_CAPACITY_OPEN`

## Claim ceiling

No subexponential cache-fibre theorem and no exponential-fibre theorem follows yet. C022/C023/global APMA authority is unchanged; `P_VS_NP = OPEN`.
