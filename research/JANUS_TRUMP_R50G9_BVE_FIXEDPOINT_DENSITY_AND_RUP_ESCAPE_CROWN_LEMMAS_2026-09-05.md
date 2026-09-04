# JANUS TRUMP R50G9 — BVE fixed-point density + RUP escape crown

## Scope

R50G8 reduced the immediate-BVE same-pivot safety problem to one obstruction: a nonterminal certified normalization fixpoint containing a wide clause whose ancestry begins in same-pivot DP and can pass only through later BVE width-creating steps.

R50G9 does not grow the corpus and does not add a rule. It derives additional necessary structure from the *existing frozen definitions* of R33 BVE, BCE, and R35B RUP vivification.

## Lemma S1 — BVE fixed-point resolvent-count lower bound

Let `K` be an R33 fixed point. For a remaining variable `v`, let

- `p(v)` be the number of clauses containing `v`,
- `n(v)` be the number of clauses containing `-v`,
- `r(v)` be the number of distinct non-tautological cross-polarity resolvents used by frozen `bve_candidate`.

Because the same R33 fixed point is pure-literal free, `p(v)>=1` and `n(v)>=1`.

Frozen BVE removes exactly the union of those `p(v)+n(v)` parent clauses and inserts at most `r(v)` distinct resolvents. If

`r(v) < p(v)+n(v)`,

then the transformed formula has strictly fewer clauses even before considering possible duplicates with inherited clauses. Hence the frozen lexicographic measure

`measure(F) = (#clauses, #literal_occurrences, #variables)`

strictly decreases, and `bve_candidate` must accept `v`.

Therefore an R33 BVE fixed point necessarily satisfies

`r(v) >= p(v)+n(v)`

for every remaining variable.

Since trivially `r(v) <= p(v)n(v)`, we obtain

`p(v)n(v) >= p(v)+n(v)`.

For positive integers this is impossible when either polarity occurs only once. Therefore

`p(v) >= 2 AND n(v) >= 2`

for every variable in an R33 fixed point.

This is an exact source-definition theorem, not an empirical regularity.

## Lemma S2 — equality case must pay literal inflation

Assume at an R33 BVE fixed point that

`r(v) = p(v)+n(v)`.

If any generated resolvent is already present among inherited clauses, the transformed formula has fewer clauses and BVE would be accepted. Therefore fixedness forces every generated resolvent to be new relative to the inherited formula.

The transformed and original formulas then have equal clause count. If the total number of literal occurrences in generated resolvents were less than the total number of literal occurrences in the removed parents, the second component of the frozen measure would decrease and BVE would be accepted.

If those literal totals were equal, the first two measure components would tie while the variable `v` disappears, so the third component would decrease and BVE would again be accepted.

Hence the only way equality in clause count can reject BVE is

`sum_resolvent_literals > sum_parent_literals`.

Thus every BVE-fixed variable carries one of two exact rejection certificates:

1. **resolvent surplus:** `r(v) > p(v)+n(v)`; or
2. **literal-inflation equality:** `r(v)=p(v)+n(v)` and generated literal total is strictly larger than removed-parent literal total, with no inherited resolvent duplicate.

## Lemma S3 — wide clause occurrence crown

Let `C` be any clause in such a fixed point. For every literal `l in C`, Lemma S1 implies that the variable `abs(l)` occurs at least twice in the polarity of `l` and at least twice in the opposite polarity.

Therefore every literal of a surviving wide clause has, outside its occurrence in `C`, at least

- one additional same-polarity occurrence, and
- two opposite-polarity occurrences.

This is stronger than the single opposite witness required merely to prevent BCE.

## Lemma S4 — BCE support crown

R50G8 already established that if `C` survives in an R33 fixed point, then for every `l in C` there exists a clause `D_l` containing `-l` such that the resolvent of `C` and `D_l` on `l` is non-tautological. Otherwise `C` would be blocked on `l` and BCE would apply.

Moreover, the same `D` cannot serve two different literals of `C`: if it contained both `-l_i` and `-l_j`, then resolving on `l_i` would retain the complementary pair `l_j,-l_j`, making that resolvent tautological.

Hence a width-`k` survivor has at least `k` distinct BCE non-blocking support witnesses.

## Lemma S5 — RUP escape crown

Frozen R35B considers every clause `C` and every literal `l in C`. It proposes the proper subclause

`C' = C \ {l}`

and runs unit propagation under assumptions negating every literal of `C'`.

If unit propagation conflicts, `C'` is accepted as a RUP strengthening. Therefore at a certified `STALLED_RUP_CORE`, for every pair `(C,l)` the exact UP replay under

`{-q : q in C\{l}}`

must be conflict-free.

So a width-`k` final survivor carries `k` independent single-literal-deletion *non-conflict* receipts in addition to its `k` BCE support witnesses.

## Double-witness crown

Combining S1–S5, every final nonterminal wide clause of width `k>4` must live in a core satisfying all of the following simultaneously:

- every variable is at least `2+2` bipolar by occurrence count;
- every variable has a frozen BVE rejection certificate (resolvent surplus or literal-inflation equality);
- the wide clause has at least `k` distinct BCE non-blocking support clauses;
- every single-literal deletion of the wide clause has an independently replayable conflict-free UP receipt;
- the whole state is R33-fixed, affine-negative, and RUP-fixed.

Call this a **DOUBLE_WITNESS_CROWN_FIXPOINT**.

The remaining theorem is therefore no longer merely `no wide clause survives`. It is:

`NO_DP_OR_BVE_WIDE_ANCESTRY_CAN_TERMINATE_IN_A_NONTERMINAL_DOUBLE_WITNESS_CROWN_FIXPOINT_REACHABLE_FROM_A_PRE_BVE_CLEAN_W4_SOURCE`.

R50G9 does not prove that final impossibility. It proves the necessary crown structure and makes any future counterexample carry a mechanically checkable obstruction certificate.

## Why this matters for the immediate-BVE branch

If the double-witness-crown obstruction is proved impossible on the relevant reachable W4 domain, then R50G5 gives

`IMMEDIATE_BVE(F,x) => R47J_SAFE(F,x)`

for the same pivot. Combined with R50G4 prefix closure, the immediate-BVE alternative for a minimal reachable `U_mu` OPEN state disappears, leaving only the R33 fixed-point branch.
