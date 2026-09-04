# JANUS TRUMP R48I — Cyclic Bipolar r×r Raw Pressure Law

Date: 2026-09-04

Status: **SYMBOLIC RAW-EXACT-DP FAMILY LEMMA; FULL NORMALIZED PRESSURE REMAINS EMPIRICAL/OPEN**

## Construction

Let `r=3q` and let `n=8r+1`. Work in the cyclic group `Z_n`.

Choose `2q` starter triples

`A_j = {0,a_j,b_j}`

such that:

1. each starter has six distinct directed nonzero differences modulo `n`;
2. the directed-difference sets of all `2q` starters are pairwise disjoint.

Use the first `q` starters as positive clause orbits and the remaining `q` starters as negative clause orbits. For every starter and every cyclic shift `i in Z_n`, include the translated 3-clause. Negate every literal in the negative orbits.

Because `r` is divisible by three, `n=8r+1` satisfies `n ≡ 1 (mod 3)`.

## Lemma 1 — exact clause count and bipolar degree

A 3-element starter has no nontrivial translational stabilizer in `Z_n`: a nontrivial stabilizer of a 3-set would force an orbit size dividing 3, impossible because `3` does not divide `n`.

Therefore each starter contributes exactly `n` distinct translated clauses.

Different starters cannot produce the same translated 3-set, because equal translated sets have equal directed-difference sets, contradicting pairwise difference-set disjointness.

Hence

`C = 2 q n = 2nr/3`.

Fix any variable `x`. For one starter triple, exactly three translations contain `x`, one for each position of the starter. Consequently each variable occurs

`3q = r`

times positively and `r` times negatively.

Thus every pivot has exactly `r` positive and `r` negative parent clauses.

## Lemma 2 — every cross-polarity parent pair intersects only at the pivot

Fix pivot `x`, a positive parent `P`, and a negative parent `N` containing `x`.

Suppose they shared another variable `y != x`. Then the directed offset `y-x mod n` would occur as a directed difference in the positive starter that generated `P` and also in the negative starter that generated `N`.

That contradicts pairwise disjointness of all starter directed-difference sets.

Therefore

`support(P) ∩ support(N) = {x}`.

## Lemma 3 — all r² resolvents are non-tautological and distinct

There are `r*r = r²` positive-negative parent pairs.

After deleting the pivot literals, a resolvent contains the two positive literals from `P \ {x}` and the two negative literals from `N \ {¬x}`.

A tautology would require some nonpivot variable to occur in both parents. Lemma 2 forbids this. Hence all `r²` parent pairs produce non-tautological resolvents.

Now suppose two parent pairs produced the same resolvent. The positive literals of that resolvent uniquely recover the positive parent minus `x`, and the negative literals uniquely recover the negative parent minus `¬x`. Thus both parents are identical, so the two parent pairs were the same.

Therefore there are exactly `r²` distinct non-tautological resolvents.

## Lemma 4 — exact raw clause pressure

Exact DP removes the `2r` parent clauses containing the pivot and retains all other clauses.

Before subsumption, the `r²` new resolvents are canonical 4-clauses, while every original unaffected clause is a 3-clause. Therefore no resolvent is identical to an unaffected base clause.

Thus the canonical pre-subsumption pool has

`C' = C - 2r + r²`,

so

\[
\boxed{\Delta C_{raw}=r^2-2r=r(r-2).}
\]

For literal mass, the removed parents contribute `2r*3=6r` literals and the new resolvents contribute `4r²` literals. Hence

\[
\boxed{\Delta L_{raw}=4r^2-6r=2r(2r-3).}
\]

## What this proves

For every member of the construction satisfying the frozen starter conditions, **raw exact Davis–Putnam projection has a rigorously growing local representation pressure** on every pivot.

For `r>2`, every pivot increases raw clause count before subsumption.

## What this does NOT prove

This lemma does **not** prove that the pressure survives:

- subsumption minimization;
- R33 reductions;
- affine recognition;
- RUP vivification;
- SA-BVE closure;
- semantic terminal recognition.

Therefore it does not establish any lower bound on the full frozen TRUMP grammar by itself.

In particular,

`RAW r(r-2) PRESSURE != FULL NORMALIZED a_star`.

R48I's executable gate is responsible only for measuring the latter on the preregistered finite ladder.

## Firewalls

- `UNIVERSAL_POLYNOMIAL_a_EXISTS = NOT_PROVED`.
- `UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE = OPEN`.
- `O4_UNIVERSAL_COVERAGE = OPEN`.
- `SAT_IN_P = NOT_PROVED`.
- `P_EQ_NP = NOT_PROVED`.
- `P_NE_NP = NOT_PROVED`.
- `P_VS_NP = OPEN`.
- `TRUMP_finished = false`.
