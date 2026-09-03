# R44BW — Congruence quotient collapses unbounded raw transport support

R44BS gives a connected maxdef-critical family with parent rank `13k-11`, both child ranks `11k-10`, and signed-transport support at least `k`. The growing support comes from an explicit equality backbone.

## Equality congruence is exact and polynomial

A pair of binary clauses

`(¬u∨v)` and `(u∨¬v)`

is exactly the relation `u=v`. Hash all binary clauses, detect such opposite implication pairs, and union their variables. This is polynomial and yields a union-find congruence.

Substituting one representative for every equality class is exact: every original model restricts to a quotient model, and every quotient model lifts by copying the representative value to all class members.

## Effect on the R44BS connected family

For each of the five local variable positions, the backbone chains all `k` block copies together by equality. Hence quotienting gives exactly five nonpivot representatives.

After substitution:

1. every backbone equality clause becomes a tautology and is deleted;
2. all `k` local copies of sibling `A` become identical copies of the same base `A` clauses;
3. all `k` local copies of sibling `B` become identical copies of the same base `B` clauses;
4. duplicate-clause deletion leaves exactly the R44AS base sibling pair.

Thus the raw support lower bound `>=k` disappears in quotient coordinates.

## Polynomial transport discovery

R44BQ-K5 deterministically enumerates support-at-most-five signed transports in polynomial time. On the quotient pair it recovers the known R44BP transport. Therefore the original connected family admits polynomial-time safe-delete discovery despite requiring raw signed support growing with `k`.

The discovered quotient transport lifts to an original model map: collapse a source model to the five quotient values, apply the base transport, then copy each target quotient value across its entire equality class. Because the target backbone enforces exactly those equalities, the lifted assignment satisfies every backbone clause and every local target block.

## Rank movement

The safe deletion keeps one original connected child, whose maxdef is `11k-10`, below the parent `13k-11` by `2k-1`. The quotient is a discovery/certificate coordinate system; it does not need to replace the retained state for the rank claim.

## Consequence

`UNBOUNDED_RAW_SUPPORT != UNBOUNDED_QUOTIENT_SUPPORT`.

Connectedness alone is not enough to make a core hard for transport discovery. The next residual must be connected **and** congruence-rigid under the polynomial equality quotient.

## Claim ceiling

This theorem resolves only the explicitly equality-coupled R44BS family. It does not imply that all growing-support transports admit a polynomial quotient, and it does not solve arbitrary critical siblings.

`TRUMP_finished=false`

`SAT_IN_P=NOT_PROVED`

`P_VS_NP=OPEN`
