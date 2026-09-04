# JANUS TRUMP R50G9 — local wide-fixpoint counterexample and reachability pivot

## Why R50G9 exists

R50G8 reduced same-pivot failure to a very specific object: a pre-BVE-clean W<=4 source whose immediate exact DP escape eventually ends at a nonterminal certified normalization fixpoint containing a width>4 clause.

Before trying to prove that object impossible, R50G9 attacks the local theorem constructively. The goal is fail-fast mathematics: if the theorem is false on arbitrary W4 states, refute it exactly and move the proof burden to the U_mu-reachable subset.

## Source-definition incidence consequences at an R33 fixed point

Let H be R33-fixed and let y be bipolar in H. Write p_y for the number of clauses containing y, n_y for the number containing -y, and R_y for the number of **unique non-tautological** DP resolvents on y.

Frozen R33 BVE accepts y whenever `R_y <= p_y+n_y` and the canonical transformed measure strictly decreases. Since tautologies have already been deleted, the positive and negative parent sets are disjoint. Therefore if

`R_y < p_y+n_y`,

the transformed clause count strictly decreases and BVE must be applicable. Hence every bipolar variable of an R33 fixed point necessarily satisfies

`R_y >= p_y+n_y`.

Since always `R_y <= p_y*n_y`, every bipolar variable in such a fixed point has

`p_y >= 2` and `n_y >= 2`.

In the extremal case p_y=n_y=2, all four cross-polarity pairs must produce four distinct non-tautological resolvents; otherwise R_y<4 and BVE would apply. If any one of those four resolvents canonicalizes onto an inherited clause, the transformed clause count drops and BVE again applies. Thus the 2x2 boundary is maximally rigid.

These are exact necessary conditions, but they are not a contradiction. A finite support graph can satisfy them.

## Frozen constructive witness

Use a 3-regular prism graph on 12 vertices. At every vertex impose the even-parity XOR constraint on its three incident edge variables, encoded as the complete four-clause width-3 CNF bundle. Because all vertex charges are zero, the system is satisfiable. The resulting core K is a complete affine CNF, but it is also R33-fixed and RUP-fixed before the extra clause is introduced.

Shift all variables of K upward by 100. Introduce a fresh pivot x=1 and exactly two pivot parents:

- P = `(1, -101, -102, -103)`
- N = `(-1, -104, -107)`

Their unique non-tautological x-resolvent is

C = `(-101, -102, -103, -104, -107)`.

The source F = K_shifted AND P AND N has width at most 4. The frozen execution must verify directly that F has no earlier tautology/unit/pure/subsumption/BCE rule and that its first R33 microstep is BVE on x.

Exact DP on x removes P,N and inserts C. Thus the post-DP state is

H = K_shifted AND C.

This breaks **whole-CNF affine recognition**: the prism bundles remain complete width-3 XOR bundles, but the single width-5 variable-set group contains one clause rather than the 16 clauses required for a complete width-5 parity bundle. Therefore R34 must be negative on H.

The decisive executable checks are then whether H is unchanged by R33 and RUP and remains width 5. If so, H is precisely the R50G8 obstruction:

`DIRECT_DP_WIDE_SURVIVOR_TO_FIXPOINT`.

## Epistemic boundary

Even if the witness verifies perfectly, it refutes only the **all-W4/local** theorem. It is not automatically a counterexample to the theorem actually needed for U_mu, because reachability of this constructed F from the frozen initial-domain/controller has not been established.

Therefore a successful R50G9 changes the proof target from

`NO_PRE_BVE_CLEAN_W4_SOURCE_CAN_GENERATE_WIDE_FIXPOINT_ANCESTRY`

to the strictly narrower

`NO_U_MU_REACHABLE_PRE_BVE_CLEAN_W4_SOURCE_CAN_GENERATE_WIDE_FIXPOINT_ANCESTRY`

or, equivalently, forces us to construct an explicit U_mu reachability certificate for the frozen R50G9 witness.

No SAT-in-P or P=NP claim follows from either outcome.
