# JANUS TRUMP R44BN — auxiliary-free projection-faithful sibling CNF lower bound

R44AS supplies the fixed six-variable parent

`G =`

- `(x2 ∨ x3 ∨ ¬x4)`
- `(¬x1 ∨ x2 ∨ x4)`
- `(¬x2 ∨ ¬x5 ∨ ¬x6)`
- `(x1 ∨ ¬x3 ∨ ¬x4)`
- `(x1 ∨ ¬x5 ∨ x6)`
- `(¬x3 ∨ x5 ∨ ¬x6)`
- `(¬x2 ∨ x3 ∨ x6)`
- `(¬x1 ∨ x4 ∨ x5)`.

R44AS already verifies

`delta*(G)=2`,

both cofactors on `x2` have maximum deficiency `1`, and every proper clause subset has deficiency below `2`. Thus this is a fixed critical sibling instance with exact branchwise rank descent.

R44AS further shows that ordinary Davis-Putnam projection rebounds to rank `3`. R44BN asks the stronger representation question:

> Could some *other* auxiliary-free CNF over the five remaining original variables represent the exact existential projection function with fewer clauses and lower maximum deficiency?

Let

`f(x1,x3,x4,x5,x6) = exists x2 G`.

The answer for this fixed function is no.

## Exact finite clause-complexity certificate

There are only

`3^5 - 1 = 242`

nonempty non-tautological clauses over five variables: each variable is absent, positive, or negative.

The deterministic verifier evaluates all `2^5=32` assignments and obtains exactly

- `11` models of `f`;
- `21` nonmodels.

A clause is an implicate of `f` iff all eleven models satisfy it. Exhaustive enumeration of the 242 possible clauses followed by literal-minimality leaves exactly thirteen prime implicates:

1. `(x3 ∨ ¬x5 ∨ x6)`
2. `(x3 ∨ ¬x4 ∨ x6)`
3. `(x3 ∨ ¬x4 ∨ ¬x5)`
4. `(¬x3 ∨ x5 ∨ ¬x6)`
5. `(x1 ∨ ¬x5 ∨ x6)`
6. `(x1 ∨ ¬x4 ∨ x6)`
7. `(x1 ∨ ¬x4 ∨ ¬x5)`
8. `(x1 ∨ ¬x3 ∨ ¬x4)`
9. `(¬x1 ∨ x4 ∨ ¬x6)`
10. `(¬x1 ∨ x4 ∨ x5)`
11. `(¬x1 ∨ x3 ∨ x6)`
12. `(¬x1 ∨ x3 ∨ ¬x5)`
13. `(¬x1 ∨ x3 ∨ x4)`.

Every clause appearing in a CNF equivalent to `f` is itself an implicate of `f`. By repeatedly deleting literals while implicatehood remains true, that clause contains a prime implicate. Replacing each clause by such a contained prime implicate cannot increase the number of clauses and preserves equivalence:

- every model of `f` satisfies every replacement prime implicate;
- each replacement prime implicate implies the original clause, so the strengthened CNF implies the original CNF, which equals `f`.

Therefore, if an equivalent CNF with at most seven clauses existed, an equivalent subset of at most seven of the thirteen prime implicates would exist.

The verifier checks every subset of sizes `0,...,7` of the thirteen prime implicates. Every such subset leaves at least one of the 21 nonmodels uncovered.

An eight-prime subset does cover all 21 nonmodels, for example:

- `(x3 ∨ ¬x5 ∨ x6)`
- `(x3 ∨ ¬x4 ∨ x6)`
- `(x3 ∨ ¬x4 ∨ ¬x5)`
- `(¬x3 ∨ x5 ∨ ¬x6)`
- `(x1 ∨ ¬x5 ∨ x6)`
- `(x1 ∨ ¬x3 ∨ ¬x4)`
- `(¬x1 ∨ x4 ∨ ¬x6)`
- `(¬x1 ∨ x4 ∨ x5)`.

Hence the exact auxiliary-free CNF clause complexity of this projection function is

`boxed(min clauses = 8)`.

## Maximum-deficiency consequence

Any auxiliary-free representation uses at most the five remaining original variables. Therefore every exact projection-faithful CNF `Q` has

`|C(Q)| >= 8`

and

`|Var(Q)| <= 5`.

Its whole-formula ordinary deficiency is therefore at least

`8-5=3`.

Since maximum deficiency dominates the deficiency of the whole clause set,

`boxed(delta*(Q) >= 3)`.

Thus, for this fixed R44AS critical parent,

- parent rank: `2`;
- both sibling ranks: `1`;
- every auxiliary-free CNF preserving the full existential projection function: rank at least `3`.

This strengthens the old raw-DP result. The barrier is not about one resolution schedule; it covers *every* auxiliary-free CNF representation of the same projection function.

## Scope firewall

R44BD requires SAT-OR plus polynomial replay, not necessarily preservation of the entire remaining-variable projection function. Therefore R44BN does **not** refute a merge that deliberately keeps only a polynomially liftable subset of models, transforms witnesses, uses auxiliary variables, or leaves CNF.

So the exact conclusion is:

`AUXILIARY_FREE_PROJECTION_FAITHFUL_SIBLING_CNF -> M2 FAILS ON THIS CRITICAL PARENT`.

Not:

`ALL SIBLING MERGES FAIL`.

`TRUMP_finished=false`

`SAT_IN_P=NOT_PROVED`

`P_VS_NP=OPEN`.
