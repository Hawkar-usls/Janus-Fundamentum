# R44AY — Local affine consequence closure on the triple-rigid core

## Construction

For every variable support `S` occurring in the CNF, with `|S|<=3`, let `F_S` be the conjunction of all clauses whose underlying variable set is exactly `S`. Enumerate the at most `2^|S|<=8` assignments to `S` and retain the locally satisfying relation `R_S`.

Compute every affine GF(2) equation `a·x=b` that holds on every point of `R_S`. Since `|S|<=3`, there are at most `2^(|S|+1)<=16` candidate equations per support. Take the union of all valid local equations and row-reduce globally by Gaussian elimination.

Every model of the full formula satisfies every local bundle and therefore every extracted equation. Hence the global linear system is a sound consequence system for `F`.

Authorized exact transitions:

1. Empty local relation or inconsistent global affine system implies `UNSAT`.
2. If the closure forces `x=c`, assign `x=c` and simplify.
3. If the closure forces `x xor y=c`, substitute one literal for the other with the corresponding sign and simplify.

These operations preserve satisfiability exactly and reduce at least one Boolean degree of freedom.

## Why this is not R43A under a new name

R43A recognized local clause bundles whose complete relation was affine (e.g. an exact XOR bundle) and used that exact affine representation. R44AY instead takes an arbitrary non-affine OR-clause bundle and extracts only those affine equations that are consequences of every locally satisfying assignment. It never replaces a non-affine relation by its affine hull as an exact representation.

`AFFINE CONSEQUENCE` is therefore weaker semantically than `EXACT AFFINE COMPILATION`, but sufficient to justify forced assignments/equivalences.

## It consumes the earlier exact-width-3 rigid gadget

Consider the four clauses on support `{x,a,b}`:

- `(x OR a OR b)`
- `(x OR a OR not b)`
- `(x OR not a OR b)`
- `(x OR not a OR not b)`

If `x=0`, the four clauses contain all four possible 2-clauses over `a,b` and are jointly inconsistent. If `x=1`, all four clauses are true. Thus the local relation is exactly `x=1`, with `a,b` free. R44AY extracts the affine equation `x=1` and performs an exact safe assignment.

This directly consumes the exact-width-three rigid obstruction used to show the incompleteness of R44AW/R44AX.

## Universal obstruction

A single 3-clause forbids exactly one of the eight assignments on its support. The seven satisfying assignments have full affine hull `GF(2)^3`. For the positive clause, the four satisfying points `111,110,101,011` are affinely independent because relative to `111` their differences are `001,010,100`. Sign changes are affine translations and preserve affine dimension. Therefore a support carrying only one 3-clause contributes no nontrivial affine equation.

Published constructions of unsatisfiable linear 3-CNF formulas exist, where distinct clauses share at most one variable. In particular every 3-variable support occurs at most once. Hence every support bundle of such a formula is a singleton 3-clause and R44AY extracts no equation at all.

Arbitrarily large UNSAT fixed points are obtained by taking one fixed unsatisfiable linear 3-CNF and adjoining arbitrarily many disjoint fresh satisfiable 3-clauses. Arbitrarily large SAT fixed points are just disjoint unions of fresh single 3-clauses.

Because each support carries a singleton sign pattern, its sign-translation stabilizer is zero. Hence these families are also sign-flip rigid (assuming irrelevant isolated variables are discarded), have no binary clauses, and have no R44AY affine consequence.

## Verdict

`NEW_EXACT_POLYTIME_SAFE_DESCENT_PRIMITIVE__NOT_UNIVERSAL`.

The residual target is now the triple-rigid core:

`H(F)=0` + no explicit binary SCC congruence + no forced unit/equivalence in the global closure of support-local affine consequences.

`TRUMP_finished=false`; `SAT_IN_P=NOT_PROVED`; `P_VS_NP=OPEN`.
