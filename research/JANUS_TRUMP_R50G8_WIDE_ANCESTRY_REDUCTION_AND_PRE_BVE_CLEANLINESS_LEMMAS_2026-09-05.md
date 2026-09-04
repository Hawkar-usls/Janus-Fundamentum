# JANUS TRUMP R50G8 — Wide-survivor ancestry reduction

## Goal

For an input formula `F` with `W(F) <= 4` whose first frozen R33 microstep is an immediate BVE escape on pivot `x`, R50G5 reduced same-pivot machine safety to

`R47J_SAFE(F,x) <=> TERMINAL(J_x(F)) OR W(J_x(F)) <= 4`.

R50G6 refuted the stronger local claim `IMMEDIATE_BVE => TERMINAL`, while its exact witness re-entered W<=4. R50G7 found no nonterminal wide survivor in its frozen algebraic family, but finite no-find has no theorem authority.

The R50G8 target is therefore the exact remaining failure mode:

`IMMEDIATE_BVE(F,x) AND J_x(F) nonterminal AND W(J_x(F)) > 4`.

No new inference rule, heuristic authority, learned selector, probabilistic selector, or corpus growth is introduced here.

## Lemma L1 — post-DP origin of initial wide clauses

Let `D_x(F)` be exact Davis–Putnam elimination of `x`. Every clause of `F` not containing `x` or `-x` is copied unchanged into `D_x(F)`, hence has width at most 4. Every other clause of `D_x(F)` is a non-tautological cross-polarity resolvent

`(P \ {x}) union (N \ {-x})`.

Therefore, because `W(F)<=4`, every clause of width greater than 4 immediately after the same-pivot DP is a DP resolvent. This is a source-definition theorem.

## Lemma L2 — all non-BVE normalization rules are width non-increasing

Inside frozen R47J normalization:

- R33 tautology deletion deletes a clause;
- unit propagation deletes satisfied clauses and removes one falsified literal;
- pure-literal autarky deletes clauses;
- subsumption deletes a clause;
- BCE deletes a clause;
- RUP vivification replaces a clause by a proper subclause;
- affine recognition is terminal and does not create a successor formula.

Hence none of these mechanisms can create a new clause whose width exceeds the maximum width present immediately before that mechanism.

The only frozen normalization operation capable of creating a wider clause is R33 BVE, through a cross-polarity resolvent.

## Lemma L3 — wide ancestry certificate

Consider the exact R47J normalization trace beginning at `D_x(F)`. If the final state is nonterminal and contains any clause `C` with `|C|>4`, then `C` admits a finite replayable ancestry certificate obtained by walking backwards through the normalization trace:

1. if `C` was already present before the most recent changing step, continue backwards unchanged;
2. a non-BVE R33 step or RUP step cannot be the creator of `C` by L2;
3. if the creator is BVE on pivot `y`, record the positive and negative parent clauses whose non-tautological resolvent is `C`, then continue ancestry through those parents;
4. the backward walk terminates at the post-DP formula; by L1, any width>4 root there is an exact resolvent of the original pivot `x`.

Thus every nonterminal final wide survivor is not an opaque event: it is either

- `DIRECT_DP_WIDE_SURVIVOR_TO_FIXPOINT`, where a width>4 DP resolvent survives without any later BVE being needed to create its final wide lineage, or
- `NORMALIZATION_BVE_DESCENDANT_WIDE_SURVIVOR_TO_FIXPOINT`, where at least one later BVE lies on the ancestry path.

## Lemma L4 — terminal/fixpoint boundary

If R47J returns nonterminal, then its final state has passed the following frozen boundary:

- R33 returned `STALLED_STACK_LEAN_CORE` with no changing R33 rule;
- complete affine recognition was negative;
- RUP returned `STALLED_RUP_CORE` with no strengthening;
- no restart remained pending.

Therefore a final wide survivor would be a certified normalization fixpoint, not merely an intermediate wide clause.

## What these lemmas do and do not prove

L1–L4 are enough to reduce universal same-pivot W4 safety to one exact obstruction theorem:

`NO_PRE_BVE_CLEAN_W4_SOURCE_CAN_GENERATE_A_WIDE_ANCESTRY_CERTIFICATE_ENDING_AT_A_NONTERMINAL_CERTIFIED_NORMALIZATION_FIXPOINT`.

They do **not** yet prove that obstruction impossible. In particular, pre-BVE cleanliness is a predicate of the source `F`; after DP, a later BVE can become applicable and is allowed to create a wider resolvent. Therefore any proof that simply says "the input was clean, so later width cannot grow" is invalid under the frozen source definitions.

This is the R50G8 critical proof step. The executable lane is only a mechanical checker/classifier for L1–L4 and the already-frozen R50G7/reachable witnesses. It has no authority to turn finite no-find into the universal theorem.

## Consequence if the critical step is later proved

If the obstruction theorem is proved for the relevant reachable W4 domain, then

`IMMEDIATE_BVE(F,x) => R47J_SAFE(F,x)`

for the same pivot. Together with R50G4 prefix closure, the immediate-BVE branch of a minimal reachable guarded-open counterexample is eliminated, leaving only the R33 fixed-point case.
