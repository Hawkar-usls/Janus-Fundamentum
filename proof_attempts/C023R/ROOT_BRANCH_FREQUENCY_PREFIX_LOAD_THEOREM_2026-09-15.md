# C023R — exact root branch-frequency / prefix-load theorem

Date: 2026-09-15
Authority: `HQ_SYMBOLIC_LEMMA__NO_SCIENTIFIC_PROMOTION`

This theorem concerns the root of the frozen degree-5 MAJ3-lifted q=4 family before any branch assignment. It uses the canonical numbering contract and historical Policy-0A budgets exactly.

## Root source counts

Let the base graph have `N` vertices and degree 5. Each vertex relation has 15 lifted variables and its exact truth-table CNF contains

`2^14`

falsifying-row blockers, each of width 15.

Every lifted variable belongs to exactly two endpoint vertex factors. Hence its root source occurrence frequency is

`F0 = 2 * 2^14 = 2^15`.

For either truth value of one lifted variable inside one vertex factor, exactly `2^13` falsifying rows have that value. Therefore across its two endpoint factors the root pass index contains

`2^14` positive clauses and `2^14` negative clauses

for every pivot variable. A completely processed root pivot therefore consumes exactly

`2^28`

complementary-pair attempts.

## Root attempt budget and exact full-pivot prefix

The root literal count is

`15 * N * 2^14`.

Historical attempt budget is four times that value:

`B_attempt = 60 * N * 2^14 = 15 * N * 2^16`.

Thus the number of fully processed root pivots is exactly

`k = floor(B_attempt / 2^28) = floor(15N/4096)`.

If the remainder is nonzero, variable ID `k+1` is the unique partially processed pivot; otherwise there is no partial pivot. No later pivot is attempted.

The addition budget is not the binding root budget on this family. A full pivot adds exactly `2^12` unique within-factor resolvents at each of its two endpoint factors, hence `2^13` additions total. Therefore all `k` full pivots contribute at most about `30N` additions, plus fewer than `2^13` additions from the partial pivot, far below the root addition cap `N*2^12` for the frozen family sizes.

## Exact additions from one fully processed pivot

Fix pivot variable `p` on base edge `(r,s)`.

Inside one endpoint vertex factor, a non-tautological source-source resolvent exists exactly when the two other coordinates of `p`'s MAJ3 block are equal, making the vertex relation independent of `p`, and the remaining block assignment has the wrong parity.

There are exactly

`2^12`

such assignments per endpoint factor. Every resulting resolvent has width 14 and contains every other variable in that endpoint's 15-variable scope.

Root cross-endpoint resolvents have width 26 and are rejected by the root width limit 16, as established separately by the root-prefix locality theorem.

Hence a fully processed pivot adds exactly `2^12` clauses to each endpoint factor and no accepted cross-factor clause.

## Prefix load

For each graph vertex `v`, define

`q_v = number of fully processed pivot variables contained in the 15-variable scope of v`.

Equivalently, count the variable IDs among `1,...,k` whose MAJ3 edge block is incident to `v`.

Let lifted variable `y` lie on base edge `(u,v)`.

Every fully processed pivot `p != y` lying in endpoint factor `u` contributes `2^12` new occurrences of `y`; similarly for endpoint `v`.

If `y` itself is fully processed, its own `2^12` resolvents at each endpoint omit `y`, so the naive `q_u+q_v` count includes two contributions that must be removed.

Therefore the exact frequency after all fully processed pivots, before the partial-pivot contribution, is

`freq_full(y) = 2^15 + 2^12 * (q_u + q_v - 2 * I[y is fully processed])`.

## Partial-pivot correction

If a partial pivot `p*` exists on edge `(r,s)`, let

- `A_r` be the number of unique accepted width-14 additions produced inside factor `r` before the attempt budget stops;
- `A_s` be the corresponding number inside factor `s`.

Then `0 <= A_r,A_s <= 2^12`.

Because every such addition contains all other variables of its endpoint factor, define

`delta(y) = A_r * I[y in scope(r) and y != p*] + A_s * I[y in scope(s) and y != p*]`.

No other variable receives a partial-pivot occurrence increment.

Thus the exact root post-Resolution frequency is

`freq(y) = 2^15 + 2^12 * (q_u + q_v - 2 * I[y fully processed]) + delta(y)`.

## Root post-unit phase

Root source clauses have width 15 and accepted root additions have width 14. Therefore no root unit clause is created by this one-pass source-only Resolution stage, and root post-unit propagation performs no assignment.

Hence the historical branch selector chooses exactly

`argmin_ID { y : freq(y) is maximal }`.

## Graph-combinatorial reduction

The first Policy-0A branch on the frozen q=4 family is therefore reduced exactly to:

1. the lexicographic edge/coordinate prefix encoded by `k=floor(15N/4096)`;
2. the endpoint prefix loads `q_v`;
3. the at-most-one partial-pivot local corrections `A_r,A_s`;
4. the historical minimum-ID tie-break.

No SAT search simulation or asymptotic timing measurement is needed to determine the first branch once these graph-prefix quantities are known.

Because edge `e_j` owns variable IDs `(3j+1,3j+2,3j+3)`, the full-pivot prefix consists of `floor(k/3)` complete lexicographic base edges plus `k mod 3` coordinates of the next edge.

## Scientific consequence

This theorem does not yet decide whether the first branch lies inside or outside the single partial-pivot asymmetry neighborhood. It converts that question to an explicit frozen graph-ordering problem.

The next exact gate is therefore:

`C023R_Q4_PREFIX_LOAD_BRANCH_CAPTURE_GATE`

Question: under the frozen q=4 matrix/edge lexicographic numbering, does the maximizing endpoint-load score force the first branch variable into the partial-pivot causal neighborhood, or is there a maximizing branch outside it?

A proof either way materially changes the fingerprint-vs-diamond route.

## Verdict

`PASS_EXACT_ROOT_BRANCH_SCORE_REDUCTION__Q4_PREFIX_LOAD_COMBINATORICS_OPEN`

No finite asymptotic fitting is authorized.
