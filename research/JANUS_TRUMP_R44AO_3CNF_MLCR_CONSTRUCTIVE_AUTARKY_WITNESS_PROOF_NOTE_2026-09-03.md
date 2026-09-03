# JANUS TRUMP R44AO — Constructive MLCR witness theorem for width <= 3

Let `F` be a Boolean clause-set in `MLCR`, with maximum clause size at most 3. Put

- `n = n(F)`,
- `m = c(F)`,
- `k = delta(F) = sigma(F) >= 1`.

By the definition of `MLCR`,

`mu_vd(F) > nM(k)`.

Since variable degrees are integers,

`mu_vd(F) >= nM(k)+1`.

The total number of literal occurrences is at most `3m=3(n+k)`, so

`n * (nM(k)+1) <= n*mu_vd(F) <= 3(n+k)`.

## Case 1: k >= 2

For `k>=2`, the non-Mersenne sequence satisfies `nM(k)>=k+2`. Therefore

`n(k+3) <= 3(n+k)`,

hence `nk<=3k` and thus `n<=3`.

So all width-3 MLCR instances with deficiency at least two have at most three variables. A satisfying assignment can therefore be found by testing at most eight Boolean assignments and scanning all clauses.

## Case 2: k = 1

`F` is matching-lean and `delta(F)=1`. For matching-lean clause-sets, Corollary 4.21 in Kullmann's clausal-form development gives

`delta*(F)=delta(F)=1`.

Kullmann-Zhao Lemma 10.6 gives `F in SAT`.

Corollary 4.9/4.10 in the clausal-form development states that for every satisfiable clause-set there exists a partial assignment using at most `delta*(F)` variables whose residual is matching satisfiable; moreover matching satisfiability and a corresponding matching-satisfying assignment are computable by maximum bipartite matching.

Thus enumerate the empty assignment and all `2n` one-variable assignments. For each candidate `phi`, simplify `F` and test whether `phi*F` is matching satisfiable. Because `delta*(F)=1` and `F` is satisfiable, at least one candidate succeeds. Compute a matching-satisfying assignment `psi` for the residual and return `phi composed with psi`.

This is polynomial time.

## Consequence for Kullmann-Zhao Conjecture 10.3 on width <= 3

Given a Boolean `F` of width at most 3 with `sigma(F)>=1` and `mu_vd(F)>nM(sigma(F))`, Lemma 10.8 computes a minimal nonempty `V` with `delta(F[V])=sigma(F)`, and Theorem 10.9 gives `F[V] in MLCR`. Clause width is not increased because `F[V]` is a sub-clause-set of `F`. Apply the theorem above to construct a satisfying assignment of `F[V]`; by the autarky correspondence in Lemma 10.1/Theorem 10.2 this assignment is a nontrivial autarky of `F`.

Hence Conjecture 10.3 is constructively true for Boolean clause-sets of maximum width at most 3.

## TRUMP boundary

This gives a new exact polynomial proof-carrying autarky transition whenever the surplus/min-degree trigger fires. It does **not** show that the trigger fires on every nonterminal 3CNF and therefore does not prove `SAT in P` or `P=NP`.

Scientific status: `TRUMP_finished=false`, `SAT_IN_P=NOT_PROVED`, `P_VS_NP=OPEN`.
