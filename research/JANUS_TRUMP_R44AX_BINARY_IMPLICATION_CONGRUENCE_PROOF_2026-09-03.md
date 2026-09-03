# R44AX — Binary implication congruence on the sign-flip-rigid core

## The exact polynomial primitive

Let `B(F)` be the set of all clauses of `F` of width at most two. Build the ordinary 2-SAT implication graph of `B(F)`.

For every binary clause `(a OR b)` add edges `not a -> b` and `not b -> a`. Unit clauses are treated as `(a OR a)`.

If some literal `l` and its complement `not l` lie in one SCC, then `B(F)` is unsatisfiable, hence the full formula `F` is unsatisfiable.

Otherwise, if literals `l,r` lie in the same SCC, there are implication paths both ways. Hence every satisfying assignment of `B(F)` satisfies `l <-> r`. Since every satisfying assignment of `F` also satisfies `B(F)`, the equivalence is valid in every model of `F`. Therefore replacing all members of one SCC equivalence class by a deterministic representative preserves satisfiability exactly.

Tarjan/Kosaraju SCC computation and the resulting substitution are polynomial, and any equivalence class containing two distinct underlying variables yields strict variable-count descent.

## This really acts after R44AW

Consider

`F = (not x OR y) AND (x OR not y) AND (x OR a OR b)`.

The support `{x,y}` has sign patterns `(-,+)` and `(+,-)`, whose translation stabilizer is `{00,11}`. The singleton sign pattern on support `{x,a,b}` has only the zero translation stabilizer. Their intersection forces all four flip coordinates to zero, so the R44AW group satisfies `H(F)={0}`.

Nevertheless the two binary clauses give `x -> y`, `y -> x`, `not x -> not y`, and `not y -> not x`. Hence `x` and `y` are equivalent and one variable may be removed exactly. Thus sign-flip rigidity does not imply logical congruence rigidity.

## Why this is still not universal

The exact-width-three rigid SAT and UNSAT obstruction families already recorded for R44AW contain no width-one or width-two clauses. Their binary implication graph is empty. Therefore R44AX has arbitrarily large SAT and UNSAT fixed points.

## Why not simply compute every semantic equivalence?

Given an arbitrary CNF `G` and fresh variables `x,y`, ask whether `G |= (x <-> y)`.

- If `G` is UNSAT, the entailment holds vacuously.
- If `G` is SAT, take any model of `G` and extend it with `x != y`; this is a countermodel.

Thus `G |= (x <-> y)` iff `G` is UNSAT. Consequently complete semantic equivalence detection is coNP-hard. The polynomial SCC primitive is a sound explicit-consequence system, not a hidden complete semantic oracle.

## Verdict

`NEW_EXACT_POLYTIME_SAFE_DESCENT_PRIMITIVE__NOT_UNIVERSAL`.

`TRUMP_finished=false`; `SAT_IN_P=NOT_PROVED`; `P_VS_NP=OPEN`.
