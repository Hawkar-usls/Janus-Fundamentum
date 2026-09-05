# JANUS TRUMP R50G18 — explicit V7 full sixfold-cage ancestry and door audit

R50G17 proves that any genuinely unsafe V7 `RUP6` trace must pass through a six-variable state containing an all-variable width-6 clause whose **every variable** is BVE-blocked with at least the oriented `3 x 2` incidence pattern. The natural next question is whether this simultaneous cage is itself impossible.

R50G18 does not assume that. It freezes one explicit construction and lets the existing exact machinery decide what it really does.

## The six-variable cage

Relabel the six remaining variables as `2..7` and define

```
R = (2,3,4,5,6,7)
```

with six single-flip cyclic supports

```
(-2,3,4)
(-3,4,5)
(-4,5,6)
(-5,6,7)
(2,-6,7)
(2,3,-7)
```

and three opposite-pair clauses

```
(-2,-5)
(-3,-6)
(-4,-7).
```

Together with `R`, this is a 10-clause, 30-literal, six-variable formula. Each variable occurs exactly five times, oriented relative to its literal in `R` as

```
p = 3, n = 2.
```

For every variable the exact BVE resolvent count is five, equal to the five removed clauses, while the literal measure grows. Thus each variable sits exactly on the R50G17 minimal BVE-blockade boundary.

This gives a local realization of the entire **sixfold saturation cage**, not merely one hub fan.

## Exact V7/W4 ancestry

Replace `R` by two width-4 parents using a fresh distinguished pivot `x=1`:

```
(1,2,3,4)
(-1,5,6,7).
```

Their residual sets are disjoint and exact DP on `1` produces exactly `R`. Keeping the nine support clauses unchanged gives the frozen V7 source:

```
(-4,-7)
(-3,-6)
(-2,-5)
(-5,6,7)
(-4,5,6)
(-3,4,5)
(-2,3,4)
(2,-6,7)
(2,3,-7)
(-1,5,6,7)
(1,2,3,4)
```

All source clauses have width at most four. R50G18 requires the frozen R33 implementation itself to verify that this source is pre-BVE clean and that its first microstep is BVE on variable `1`, with a width-6 escaped proposal.

If those checks pass, then `FULL_CAGE_ANCESTRY_IMPOSSIBILITY` is refuted locally: a width-four V7 source can generate the complete sixfold cage in one exact DP step.

## The decisive test is not ancestry but safety

The existence of the cage does **not** tell us whether it survives the complete R47J normalization fixpoint. RUP may strengthen its clauses, trigger an R33 restart, terminate the state, or return to width at most four.

Therefore the fixed source is passed unchanged into the existing frozen door machinery:

- same-pivot `R47J_1` is independently replayed;
- every alternate pivot `y != 1` is audited for R49H and R47J_SAFE;
- an all-doors-closed local counterexample is reported only if same-pivot R47J is nonterminal/wide and every alternate certified door is also closed.

This is a theorem-or-counterexample gate. No result is promoted to reachable-domain failure unless reachability is independently certified.
