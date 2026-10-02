# R5 E9 — Local Bond-Dimension Barrier for Exact Boben Semantic Lifts

Date: 2026-09-27

Status:
`EXACT_LOCAL_STATE_LOWER_BOUND__GLOBAL_GROWTH_OPEN`

Scientific ceiling:

```text
ordinary 2-state Boben semantic lift = IMPOSSIBLE already locally
adjacent local hidden-state minimum  = 3
nonadjacent local hidden-state minimum = 4 for a 1|2 paired-edge split
bounded global state algebra         = OPEN
P_VS_NP                              = OPEN
```

Parent:
- `R5_E9_BOBEN_REDUCTION_EXACTONE_SEMANTIC_AUDIT_2026-09-27_v1.0.md`

Checker:
- `experiments/r5_e9_boben_local_bond_dimension.py`

## 1. Factor language

In the Levi / General-Factor representation the two local Boolean relations are

```text
EQ3(a,b,c)       : a=b=c
EXACT1_3(a,b,c) : a+b+c=1.
```

A semantically exact Boben contraction must preserve the relation induced on the dangling incidences of the removed point/line pair.

A factorization through one hidden state `h in H` across a bipartition of the boundary has the form

```text
R(x,y) = exists h in H: L(x,h) AND R'(h,y)
```

for decision semantics, or the analogous sum/product factorization over a field for counting/linear tensor semantics.

For a Boolean relation matrix `M`, such a relational factorization needs at least the Boolean rank of `M` hidden states. For a linear tensor factorization it needs at least the ordinary matrix rank. The frozen matrices below have the same required lower bound under both notions.

## 2. Adjacent Boben reduction requires 3 states

If the removed point and line are adjacent, let `s` be their shared incidence bit; let `a,b` be the other point-side dangling bits and `c,d` the other line-side dangling bits.

The contracted boundary relation is

```text
R_adj(a,b,c,d)
= exists s: EQ3(a,b,s) AND EXACT1_3(c,d,s).
```

Its tuples are exactly

```text
(0,0,0,1)
(0,0,1,0)
(1,1,0,0).
```

Take either legal Boben pairing, for example group boundary coordinates as

```text
left  = (a,c)
right = (b,d).
```

In state order `00,01,10,11`, the relation matrix is

```text
M_adj =
[0 1 0 0
 1 0 0 0
 0 0 1 0
 0 0 0 0].
```

This is a partial permutation matrix with three isolated ones. Therefore

```text
rank_R(M_adj)=3
Boolean-rank(M_adj)=3.
```

The other Boben pairing `(a,d)|(b,c)` gives the same matrix up to row/column permutation.

Hence any exact one-hidden-variable factorization across either ordinary Boben reconnection needs

```text
|H| >= 3.
```

An ordinary Boolean equality edge has only two states, so the original two-state edge alphabet is not closed under one adjacent Boben semantic contraction.

## 3. Nonadjacent Boben reduction requires 4 states

If the removed point and line are nonadjacent, write the three point-side bits as

```text
a1,a2,a3
```

and the three line-side bits as

```text
b1,b2,b3.
```

The exact local relation is

```text
R_nonadj
= EQ3(a1,a2,a3) AND EXACT1_3(b1,b2,b3).
```

After any Boben pairing, combine each paired dangling incidence into a two-bit edge symbol

```text
si=(ai,b_pi(i)) in {00,01,10,11}.
```

The allowed triples of symbols are exactly

```text
(00,00,01)
(00,01,00)
(01,00,00)
(10,10,11)
(10,11,10)
(11,10,10).
```

Flatten one paired edge against the other two. With row order

```text
00,01,10,11
```

all four rows are nonzero and their one-supports are pairwise disjoint. Consequently

```text
rank_R(M_nonadj)=4
Boolean-rank(M_nonadj)=4.
```

Thus any exact factorization of this three-edge relation across a `1 | 2` split requires

```text
|H| >= 4.
```

This is a strict local state expansion from the original Boolean alphabet size two.

## 4. What this proves — and does not prove

Proved:

```text
A. ordinary unlabeled Boben edges do not preserve Exact-One semantics;
B. a 2-state hidden annotation cannot repair even one generic adjacent step;
C. a nonadjacent step requires at least four hidden states across a natural 1|2 split;
D. any proposed universal Boben semantic lift must explicitly account for state-alphabet enlargement.
```

Not proved:

```text
A. that bond dimension grows without bound along every reduction sequence;
B. that no clever basis/holographic transformation yields a uniformly bounded alphabet;
C. any superpolynomial lower bound for Exact-One or SAT;
D. P != NP.
```

The next legitimate question is therefore not whether the first contraction has a finite signature — it does — but whether the exact signature algebra is closed under arbitrary Boben sequences with polynomial total representation size.

## 5. Next gate

```text
R5_E9_BOBEN_SIGNATURE_CLOSURE_GATE_V1
```

Required attack:

1. choose an explicit representation class for edge/boundary signatures;
2. compute closure under adjacent and nonadjacent Boben contractions;
3. after every contraction perform exact canonical compression (Boolean relation equivalence / tensor rank where justified);
4. measure worst-case alphabet/rank growth on hostile reduction sequences;
5. either prove a polynomial bound plus reconstruction, or freeze a concrete growing counterfamily for the proposed representation.

A finite check on small instances is diagnostic only; a universal bounded-state theorem requires symbolic proof.

## 6. Frozen status

```text
ADJACENT MIN LOCAL HIDDEN STATES    = 3
NONADJACENT MIN LOCAL HIDDEN STATES = 4
2-STATE BOBEN SEMANTIC LIFT         = FALSIFIED
GLOBAL SIGNATURE CLOSURE             = OPEN
UNIVERSAL EXACT-ONE SOLVER           = OPEN
E8_D1                                = EMPTY
P_VS_NP                              = OPEN
```
