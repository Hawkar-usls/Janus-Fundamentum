# R44BQ — Signed transport discovery is NP-complete on sibling pairs

## Problem

Given CNFs `A,B` over the same variable set, decide whether there is a signed variable permutation `pi` such that for every clause `C` of `A` some clause `D` of `B` satisfies `D subseteq pi(C)`.

A supplied `pi` plus the clause witnesses is checkable in polynomial time, so the problem is in NP.

## Reduction from Hamiltonian Cycle

Let `G=(V,E)` be a simple graph with `V={1,...,n}`, `n>=3`.

Define a monotone 2CNF `A_n` from the fixed cycle `C_n`:

`A_n = { (x_i OR x_{i+1}) : i=1,...,n }`, indices modulo `n`.

Define a monotone 2CNF `B_G` from `G`:

`B_G = { (x_u OR x_v) : {u,v} in E }`.

### If G has a Hamiltonian cycle

A Hamiltonian ordering gives a bijection of the variables that maps every cycle edge of `C_n` to an edge of `G`. With all signs positive, every clause of `A_n` maps exactly to a clause of `B_G`. Hence a transport certificate exists.

### If a transport certificate exists

Every clause of `A_n` has width two, every clause of `B_G` has width two, and `B_G` has no unit clauses. Thus `D subseteq pi(C)` implies `D=pi(C)`.

All clauses of `B_G` are monotone. Every variable occurs in `A_n`. Hence no variable can be sent with negative sign: a negative image would occur in some width-two `pi(C)`, which then could not equal a monotone clause of `B_G`.

Therefore `pi` is an ordinary permutation of vertices and maps every edge of the fixed `n`-cycle into an edge of `G`. Its image is a Hamiltonian cycle in `G`.

So the transport-discovery problem is NP-hard and, with membership in NP, NP-complete.

## Genuine 3CNF sibling lift

Introduce a fresh pivot variable `z` and define

`P_G = { (z OR C) : C in A_n } union { (NOT z OR D) : D in B_G }`.

All clauses have width three. Simplification gives

`P_G[z=0] = A_n`,

`P_G[z=1] = B_G`.

Thus NP-completeness already holds when the pair to be compared are genuine siblings of one 3CNF parent.

## Scope ceiling

This theorem does **not** show hardness when the parent is maximum-deficiency-critical. It blocks only generic R44BP-style discovery on arbitrary sibling pairs. Any remaining positive route must exploit additional critical-parent structure in a way absent from the Hamiltonian-cycle embedding.

`TRUMP_finished=false`  
`SAT_IN_P=NOT_PROVED`  
`P_VS_NP=OPEN`
