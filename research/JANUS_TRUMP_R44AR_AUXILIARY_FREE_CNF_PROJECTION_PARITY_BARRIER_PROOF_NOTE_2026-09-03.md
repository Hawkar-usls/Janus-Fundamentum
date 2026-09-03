# JANUS TRUMP R44AR — Auxiliary-free CNF projection parity barrier

## Polynomial 3CNF source

Encode `z=a XOR b` by the four width-3 clauses

- `(a ∨ b ∨ ¬z)`
- `(a ∨ ¬b ∨ z)`
- `(¬a ∨ b ∨ z)`
- `(¬a ∨ ¬b ∨ ¬z)`.

A truth-table check shows these clauses hold exactly when `z=a XOR b`.

Chain these gadgets as `z_2=x_1 XOR x_2` and `z_i=z_{i-1} XOR x_i` for `i=3,...,n`. Enforce `z_n=0` with fresh `p,q` and

- `(¬z_n ∨ p ∨ q)`
- `(¬z_n ∨ p ∨ ¬q)`
- `(¬z_n ∨ ¬p ∨ q)`
- `(¬z_n ∨ ¬p ∨ ¬q)`.

If `z_n=0` all four are true. If `z_n=1`, they reduce to all four possible two-literal clauses on `p,q`, which are jointly unsatisfiable. Hence existentially quantifying the chain and enforcement auxiliaries leaves exactly the even-parity relation on `x_1,...,x_n`.

The source CNF has `O(n)` clauses and variables and maximum width 3.

## Exponential lower bound for auxiliary-free CNF parity

Let `G(x_1,...,x_n)` be a CNF equivalent to even parity and containing no auxiliary variables.

Take any non-tautological clause `C` of `G`. Suppose `C` omits some variable. Set every variable mentioned in `C` so that its literal in `C` is false. Because at least one variable remains free, choose the remaining variables so the resulting total assignment has even parity. This even-parity assignment falsifies `C`, contradicting that `C` is implied by even parity.

Therefore every non-tautological clause implied by even parity must mention all `n` variables. Such a full-width clause is falsified by exactly one total assignment. Since an exact CNF for even parity must exclude all `2^(n-1)` odd assignments, at least `2^(n-1)` clauses are necessary.

Thus a linear-size width-3 CNF can have an existential projection whose exact auxiliary-free CNF representation is exponentially large.

## TRUMP boundary

This blocks only the fixed route `equivalent auxiliary-free CNF projection`. It does not block richer representations or SAT-only summaries. Allowing auxiliaries may restore succinctness, but R44AQ shows that a fresh selector can merely reify the eliminated branch; a successful successor must prove that its auxiliary state is a genuine compression and that a fixed global rank still strictly descends.

Scientific status: `TRUMP_finished=false`, `SAT_IN_P=NOT_PROVED`, `P_VS_NP=OPEN`.
