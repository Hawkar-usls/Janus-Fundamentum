# R44BX — Orbit-coupled congruence-rigid growing-support family

Start from the R44BR shared-pivot family of `k` R44AS blocks. The parent is maxdef-critical with rank `3k-1`; each raw sibling has rank `k`.

Let `pi` be the R44BP signed permutation on local variables:
`1->-3, 3->-5, 4->6, 5->-1, 6->-4`.

For each adjacent block pair `i,i+1`, add the complete `pi`-orbit of the seed 3-clause

`C_i^(0) = (x1_i ∨ ¬x3_(i+1) ∨ x4_i)`.

Because the signed literal orbit of `x1` has period 6 while that of `x4` has period 4, and the corresponding variable sets are disjoint, the clause orbit has exact period `lcm(6,4)=12`. Thus there are exactly `12(k-1)` connector clauses and no new variables.

## SAT

Both base siblings share the local model

`x1=x3=x4=x5=0, x6=1`.

The orbit of literal `x1` is

`x1, ¬x3, x5, ¬x1, x3, ¬x5`,

whose truth pattern under the common model is

`F,T,F,T,F,T`.

The second literal of the seed is `¬x3 = pi(x1)`. Therefore in every orbit clause the first two literals are consecutive phases of this alternating sequence and at least one is true. Repeating the common local model in all blocks satisfies every connector. Hence both siblings are SAT.

## Connectedness

Every connector contains variables from blocks `i` and `i+1`, and every adjacent pair receives a connector orbit. Each local sibling is internally connected. Hence each global sibling is connected.

## Rank

R44BR parent rank is `3k-1`. Adding any clause whose variables are already present in a maxdef-critical formula preserves criticality and raises maxdef by exactly one. Repeating for all `12(k-1)` connectors yields

`delta*(G_k^orbit)=3k-1+12(k-1)=15k-13`,

and the parent remains maxdef-critical.

Each raw child has maxdef and full deficiency `k`. Adding `c=12(k-1)` clauses can raise maxdef by at most `c`, while the full connected child has deficiency `k+c`. Therefore

`delta*(A_k^orbit)=delta*(B_k^orbit)=13k-12`.

The branchwise rank drop is

`(15k-13)-(13k-12)=2k-1`.

## Binary-congruence rigidity

All new connectors have width exactly 3 and therefore create no new edges in the binary implication graph. The two R44AS base siblings have no nontrivial literal equivalence SCCs in their binary implication graphs. Consequently every variable class remains singleton under the R44AX/R44BW polynomial binary-congruence quotient.

Thus R44BW's equality collapse does nothing on this family.

## Transport and support

Applying `pi` independently in every block transports local `B` clauses into local `A` clauses. The connector set is a complete `pi`-orbit, so `pi` maps each connector to the next connector in the orbit. Hence a global signed transport exists with support `5k`.

For the lower bound, suppose some target block is identity on all five of its local variables. A local target clause then remains a clause over that block only. A source connector contains variables from two blocks and cannot be a subset of that image. A source local clause from another block uses disjoint variables. Therefore the local target clauses would need same-block local source witnesses, yielding the forbidden identity transport on the R44AS base pair. Contradiction.

Hence every target block contributes at least one changed variable and support is at least `k`.

The same untouched-block argument does not use injectivity, so it also lower-bounds deviation support by `k` for the many-to-one signed-literal substitution class when identity is required outside the deviation set.

## Claim ceiling

This family defeats constant-support enumeration and survives exhaustive binary-congruence quotienting. It does not establish search hardness: the connector orbit is itself globally structured and may admit polynomial generator recovery.

`TRUMP_finished=false`

`SAT_IN_P=NOT_PROVED`

`P_VS_NP=OPEN`
