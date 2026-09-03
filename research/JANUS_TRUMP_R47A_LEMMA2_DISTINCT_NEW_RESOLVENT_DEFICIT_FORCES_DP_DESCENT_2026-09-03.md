# R47A Lemma 2 — Distinct-new-resolvent deficit forces exact-DP clause descent

Status: **SYMBOLIC SUFFICIENT CASE PROVED** (not universal coverage)

Let `F` be a canonical CNF with `C` clauses and let variable `v` occur in `p>=1` positive clauses and `n>=1` negative clauses. Let `B_v` be the set of clauses of `F` not containing `v` or `-v`, so `|B_v| = C-p-n`. Let `R_v` be the set of all distinct non-tautological exact-DP resolvents produced from one positive and one negative parent, exactly as in the frozen R42/R45A implementation.

Define the **new-resolvent count**

`a_v := |R_v \ B_v|`.

Because the DP pool is canonicalized as the union `B_v ∪ R_v`, its exact clause count before subsumption is

`C_pool = C - p - n + a_v`.

Therefore, if

`a_v < p+n`,

then

`C_pool < C`.

The frozen subsumption minimizer can only delete clauses from that pool, hence the exact-DP transformed formula also satisfies

`C_DP < C`.

Since the TRUMP progress measure is lexicographic `(clauses, literal_mass, variables)`, strict clause decrease alone proves strict progress. No downstream R33/affine/RUP effect is needed for the descent proof in this case.

Hence:

> For every canonical nonterminal formula `F`, if there exists a bipolar variable `v` whose number of distinct non-tautological resolvents that are genuinely new relative to the unaffected base is smaller than the number of removed parent clauses, exact DP on `v` is a certified strict descent.

## Polynomial discoverability

The predicate is polynomially decidable. For each variable `v`, enumerate at most `p*n <= C^2/4` parent pairs, build each resolvent in polynomial time, discard tautologies, canonicalize/deduplicate with hashing/sorting, and test membership in the base clause set. Thus `a_v` is computable in polynomial time. Scanning all variables remains polynomial.

This is stronger than Lemma 1. Lemma 1 follows immediately because if `min(p,n)=1`, then `|R_v| <= p*n = max(p,n) < p+n`, hence `a_v <= |R_v| < p+n`.

## Residual obstruction after Lemmas 1–2

Any normalized state not covered by these exact-DP descent lemmas must satisfy, for every bipolar variable `v`,

`p_v >= 2`, `n_v >= 2`, and `a_v >= p_v+n_v`.

Because `a_v <= |R_v| <= p_v*n_v`, such a residual variable must also satisfy

`p_v*n_v >= p_v+n_v`, equivalently `(p_v-1)(n_v-1) >= 1`.

For the smallest residual case `p_v=n_v=2`, escaping the lemma requires `a_v=4`: all four parent pairs must yield four distinct non-tautological resolvents, and all four must be absent from the unaffected base before subsumption. Any tautological pair, duplicate resolvent, or resolvent already present in the base immediately gives `a_v<=3` and therefore strict clause descent.

This isolates a concrete local obstruction class instead of an unspecified dense core.

## What this does not prove

It does not prove that every reachable nonterminal TRUMP state contains a variable with `a_v < p_v+n_v`. States with `a_v >= p_v+n_v` for every bipolar variable remain the universal-coverage frontier. Subsequent normalization may still create an accepted descent even when immediate DP does not; this lemma intentionally makes only the stronger immediate-DP statement.

## Firewall

- `R47A_UNIVERSAL_COVERAGE = OPEN`
- `SAT_IN_P = NOT_PROVED`
- `P_VS_NP = OPEN`
