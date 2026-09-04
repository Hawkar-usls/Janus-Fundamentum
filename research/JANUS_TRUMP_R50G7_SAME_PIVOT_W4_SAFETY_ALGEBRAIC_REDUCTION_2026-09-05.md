# JANUS TRUMP R50G7 — Same-pivot W4 safety algebraic reduction

## Target

For a W<=4 state F whose first R33 micro-proposal is BVE on x and whose raw BVE proposal leaves W4, attack the exact machine theorem

`IMMEDIATE_BVE_W4_ESCAPE(F,x) => R47J_SAFE(F,x)`.

By R50G5, for the same pivot x the following are already source-level consequences: exact DP exists, independent DP replay passes, no fresh variables are introduced, x is eliminated, strict variable descent holds, and legacy R47J acceptance holds. Therefore

`R47J_SAFE(F,x) <=> TERMINAL(J_x(F)) OR W(J_x(F)) <= 4`.

R50G6 refuted the stronger all-W4 theorem `IMMEDIATE_BVE => TERMINAL`: a disjoint normalization-fixed component survives exactly, producing a nonterminal but W<=4-safe same-pivot result. Therefore terminality is not the correct universal target.

## Exact remaining obstruction

A same-pivot failure can only have the form

`IMMEDIATE_BVE_W4_ESCAPE(F,x)`

and

`J_x(F) is nonterminal`

and

`W(J_x(F)) >= 5`.

Call this a SAME_PIVOT_WIDE_SURVIVOR.

No exactness, reconstruction, fresh-variable, variable-descent, or per-transition polynomiality debt remains inside this local implication. The only open predicate is final width after certified normalization.

## Algebraic falsifier family

Let K be the frozen R47I residual fixpoint, independently known to be unchanged and nonterminal under the R47J normalization stack. Shift all variables of K above a fresh pivot x=1. Choose five distinct signed literals a,b,c,d,e from K's variables and form

P = (x,a,b,c)

N = (-x,d,e).

When the residual literal sets are compatible, exact DP on x generates the width-5 resolvent

R = (a,b,c,d,e).

If P and N introduce no earlier tautology/unit/pure/subsumption/BCE rule and x is the first BVE candidate, then F = K ∧ P ∧ N is an immediate W4 BVE-escape state. Since x occurs only in P,N, exact DP_x(F) is K ∧ R up to exact canonical subsumption.

Therefore, if R survives the complete certified R47J normalization and K ∧ R remains nonterminal, then

`W(J_x(F)) = 5`

and F is an explicit exact counterexample to the stronger all-W4 same-pivot safety theorem.

This construction is algebraic: the search does not rank formulas by a score. It lexicographically enumerates the finite parameter family and uses only proof-preserving exact precondition filters. Stopping at a frozen finite cap has no theorem authority if no witness is found.

## Reachability firewall

Even if such an F is found, it does not refute the reachability-scoped theorem needed by U_mu unless F is separately proved reachable from the 3CNF input domain under the frozen controller. A local counterexample would instead prove that any successful theorem must use a reachability-specific invariant.

## Desired dichotomy

1. Explicit local wide survivor found: local universal same-pivot W4 safety is REFUTED; isolate the missing reachability invariant.
2. No witness in the frozen algebraic family: no promotion; both local and reachable universal claims remain OPEN.

The experiment is a theorem falsifier, not theorem evidence by counting successes.
