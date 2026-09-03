# JANUS TRUMP R44AM — Linear-autarky surrogate collision

The general lean kernel `N_a(F)` is semantically complete but polynomial computation is equivalent to `P=NP`. A natural polynomial surrogate is the linearly-lean kernel `N_lin(F)`, obtained from linear autarkies via linear programming.

For a Boolean CNF `F`, let `M(F)` be its signed clause-variable matrix. A nonzero vector `x` with `M(F)x >= 0` yields a linear autarky by taking the signs of the nonzero coordinates.

## SAT formula that is already linearly lean

Consider the 3-variable formula with clauses

- `(a ∨ b ∨ c)`
- `(a ∨ ¬b ∨ ¬c)`
- `(¬a ∨ b ∨ ¬c)`
- `(¬a ∨ ¬b ∨ c)`
- `(a ∨ b ∨ ¬c)`

The all-true assignment satisfies it.

The first four rows of its signed matrix are

```
[ 1,  1,  1]
[ 1, -1, -1]
[-1,  1, -1]
[-1, -1,  1]
```

Let `x=(x1,x2,x3)` satisfy these four inequalities. The first row gives `s=x1+x2+x3 >= 0`. Summing the other three gives `-s >= 0`, so `s=0`. Then each of the latter inequalities equals `2xi >= 0`, hence all `xi>=0`; together with `s=0`, this forces `x=0`. Thus there is no nontrivial linear autarky. Adding the fifth clause cannot create a nonzero feasible vector, so the full formula is linearly lean and SAT.

Taking variable-disjoint copies preserves linear leanness by block-diagonality. Adding connector clauses satisfied by the all-true assignment preserves SAT and cannot create a nonzero solution to the old core inequalities, so arbitrarily large connected SAT linearly-lean formulas exist.

## UNSAT collision side

Every minimally unsatisfiable formula is general-lean and therefore linearly lean. Hence the implication-chain family `U_n` from R44AI/R44AK also has `N_lin(U_n)=U_n != EMPTY`.

Thus the same polynomial surrogate output, `N_lin(F) != EMPTY`, occurs on arbitrarily large SAT and UNSAT formulas.

Therefore `N_lin` cannot exactly recover the empty-vs-nonempty distinction of the general lean kernel.

Scientific status: `TRUMP_finished=false`, `SAT_IN_P=NOT_PROVED`, `P_VS_NP=OPEN`.
