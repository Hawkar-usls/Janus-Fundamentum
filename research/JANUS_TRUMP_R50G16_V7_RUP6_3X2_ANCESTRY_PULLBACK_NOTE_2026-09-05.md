# JANUS TRUMP R50G16 — V7 RUP6 3x2 ancestry pullback and door audit

## Frozen question

R50G15 proved a necessary local condition for a V7 `RUP6_DROP_HUB` edge: immediately before the certified RUP deletion of the hub literal, the six-variable state must carry a hub BVE blockade with at least a `3 x 2` incidence pattern. The minimum five hub-containing clauses are not themselves impossible: an exact local `3 x 2` blocker exists.

R50G16 asks the next narrower question: can that exact saturation pattern be pulled back through a seven-variable, width-at-most-four, pre-BVE-clean source whose first frozen R33 microstep is the distinguished immediate BVE escape?

The canonical lift fixes the distinguished pivot to `x=1`, hub to `z=7`, and uses the mandatory 4x4-disjoint parent pair

```
(1,2,3,4)
(-1,5,6,7)
```

which generates

```
R=(2,3,4,5,6,7).
```

The R50G15 minimal hub fan is lifted as base clauses

```
(-5,6,7)
(-4,5,7)
(2,-7)
(3,-7).
```

The source still needs exact opposite-polarity support for variables 2, 3 and 6 to pass pre-BVE cleanliness and BCE. Rather than hand-selecting one augmentation after seeing the result, the preregistration freezes a small deterministic lexicographic family of support clauses and at most one optional blocker.

## What a positive realizer means

A positive source must satisfy all of the following under frozen code:

1. `W(F)<=4` and exactly seven variables.
2. No tautology, unit, pure literal, subsumption or BCE before the distinguished BVE.
3. The first frozen R33 microstep is BVE on `x=1`, and its exact proposal escapes width four.
4. Exact DP on `x=1` contains `R=(2,3,4,5,6,7)`.
5. The post-DP R33 phase does not eliminate any further variable before RUP.
6. The pre-RUP state has at least three clauses of one hub polarity and two of the opposite polarity, with hub BVE rejected by the frozen measure.
7. Frozen RUP contains the exact strengthening

   `R -> (2,3,4,5,6)` by deleting literal `7`,

   and independent RUP replay succeeds.

If such a source exists, then **local V7 ancestry impossibility for the RUP6 3x2 boundary is refuted**. That does not refute the reachable alternate-door theorem and does not prove an all-doors-closed obstruction.

## Door audit

For the first exact realizer, R50G16 then runs the existing frozen door machinery on every alternate pivot `y != 1`:

- R49H is open exactly when `chi_star(y) <= 4`.
- R47J_SAFE is open exactly when the independently replayed R47J successor is terminal or has final width at most four.

The distinguished pivot is separately checked for same-pivot safety.

Therefore the strongest possible R50G16 outcome would be an explicit seven-variable source with:

```
same-pivot nonterminal W>4
AND
for every y != 1: chi_star(y)>=5 and R47J_y nonterminal W>4.
```

That would be a genuine local all-doors-closed counterexample. Any weaker source remains useful because its first open door identifies the structural seam that a universal theorem must exploit.

## Epistemic boundary

The augmentation family is finite and frozen for counterexample discovery and mechanism diagnosis only. Failure to find a source in this family is not a universal impossibility proof. No theorem is promoted from finite no-find. `V7`, full immediate-BVE, `U_mu`, `SAT in P`, and `P vs NP` remain open/not proved unless a separate universal proof closes their obligations.
