# JANUS TRUMP R44AL — General lean kernel as a complete exact invariant

Let `N_a(F)` denote the general autarky lean kernel of a CNF formula `F`.

## Exact semantic theorem

`N_a(F)=EMPTY` iff `F` is satisfiable.

- If `F` is satisfiable, a complete satisfying assignment on `var(F)` is a general autarky touching and satisfying every clause. Hence the maximal autark subset is all of `F`, leaving empty lean kernel.
- If `N_a(F)=EMPTY`, a maximal autarky removes every clause. By the definition of autarky, every touched clause is satisfied; since all clauses are touched, the autarky is a satisfying assignment for `F`.

Thus `N_a(F) != EMPTY` iff `F` is unsatisfiable.

## Why this does not yet solve P vs NP

The invariant is semantically complete but general autarky computation is not known polynomial. General AUTARKY EXISTENCE is NP-complete and LEAN recognition is coNP-complete in the cited autarky literature.

If `N_a(F)` were computable in deterministic polynomial time on arbitrary CNF, testing whether the result is empty would put SAT in P. Conversely, under `P=NP`, SAT and the standard oracle/self-reduction machinery for computing maximal autarkies become polynomial-time, so the general lean kernel is polynomial-time computable.

Hence:

`POLYTIME_COMPUTABLE_GENERAL_LEAN_KERNEL <=> P=NP`.

## TRUMP interpretation

This is the first invariant in the current line whose **semantic completeness is already perfect**. The missing obligation is computational: construct the exact empty/nonempty lean-kernel distinction in charged polynomial time and provide the required replay boundary.

The next admissible candidate is therefore a fixed polynomially computable surrogate `J(F)` with a theorem that `J(F)` exactly determines whether `N_a(F)` is empty for every 3CNF. Any full proof of such a surrogate is already a P=NP proof.

Scientific status: `TRUMP_finished=false`, `SAT_IN_P=NOT_PROVED`, `P_VS_NP=OPEN`.
