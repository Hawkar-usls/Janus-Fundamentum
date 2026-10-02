# R5 E50 — E12 Multiclaw Ambiguity Firewall

Date: 2026-10-02

Status:
`CORRECTED_COLUMN_CONFLICT_ORIENTATION__EVERY_E12_VARIABLE_COLUMN_HAS_2_4_OR_8_CLAW_TRIPLES__E49_BACKDOOR_LINEAR`

Scientific ceiling:

```text
R5 E49 SOLVES THE CONFLICT-STATE CSP BY 2-SAT WHEN EVERY VARIABLE-COLUMN
HAS AT MOST ONE CLAW-LEAF TRIPLE, AND BY O(21^t poly(n)) WHEN ONLY t
VARIABLE-COLUMNS HAVE TWO OR MORE CLAW TRIPLES.

FOR THE R5 E12 NP-COMPLETE HARDNESS BRIDGE, THE RELEVANT CONFLICT GRAPH IS
THE GRAPH ON TARGET TRIPLES / MATRIX COLUMNS: TWO TARGET TRIPLES ARE
ADJACENT IFF THEY SHARE A TARGET ELEMENT / MATRIX ROW.

ON THAT CORRECT GRAPH, EVERY E12 TARGET VARIABLE IS MULTICLAW:

  L1-L3, P1-P3, D1-D6 : c(v)=4;
  L4-L5, P4-P5       : c(v)=2;
  D7                  : c(v)=8.

THUS EVERY TARGET VERTEX HAS c(v)>=2 AND
  t_multiclaw=n.

THE EARLIER POINT-GRAPH 4/8 COUNT WAS AN ORIENTATION ERROR AND IS NOT USED.
THIS CORRECTED NOTE REPLACES IT.

P_VS_NP = OPEN.
```

## 1. Orientation correction

The E12 reduction is naturally written as a 3-uniform hypergraph:

```text
target elements  = Exact-One constraints / matrix rows,
target triples   = selectable Exact-One variables / matrix columns.
```

R5 E45--E49 define the conflict graph on **variable-columns**.
Therefore the correct E12 conflict graph has:

```text
one conflict vertex per target triple L_i,P_i,D_i,
```

with two conflict vertices adjacent exactly when the corresponding target triples
share a target element.

The point graph on target elements is also 6-regular because the target is square,
cubic and linear, but it is the conflict graph of the dual incidence matrix and is
not the graph used by E45--E49. E50 henceforth uses only the correct column graph.

## 2. Recall one E12 gadget

For one source triple, the 17 selectable target triples are

```text
L1={x1,z1,z4}       P1={p1,Z1,Z4}
L2={x2,z2,z5}       P2={p2,Z2,Z5}
L3={x3,z3,z6}       P3={p3,Z3,Z6}
L4={z1,z2,z3}       P4={Z1,Z2,Z3}
L5={z4,z5,z6}       P5={Z4,Z5,Z6}

D1={z2,z6,t1}
D2={z3,z4,t2}
D3={z1,z5,t3}
D4={Z2,Z6,t2}
D5={Z3,Z4,t3}
D6={Z1,Z5,t1}
D7={t1,t2,t3}.
```

Every target triple contains three elements. Every target element lies in exactly
three target triples. Linearity says any two target triples share at most one
element.

Therefore each conflict vertex has six distinct neighbors arranged into three
adjacent pairs, one pair for each element of the triple.

A claw-leaf triple centered at a target triple is an independent transversal:
choose one neighbor from each of those three pairs, subject to no extra adjacency
between the three chosen neighbors.

There are at most `2^3=8` such transversals.

## 3. Boundary L/P triples L1--L3 and P1--P3 have c=4

Consider `L1={x1,z1,z4}`.

Its three conflict-neighbor pairs are:

```text
through x1 : the two other target triples from the other two source gadgets
             incident with the same global RXC3 element x1;
through z1 : {L4,D3};
through z4 : {L5,D2}.
```

The two external neighbors through `x1` belong to distinct gadgets. They have no
cross-adjacencies to the local `z`-neighbors above.

Between the two local pairs, direct gadget inspection gives exactly two forbidden
cross choices:

```text
L4 -- D2   (share z3),
D3 -- L5   (share z5).
```

The other two pairwise choices are nonadjacent.

Hence the external pair contributes a free factor `2`, while the two local pairs
have exactly two compatible transversals:

```text
boxed:
c(L1)=2*2=4.
```

The same argument holds for `L2,L3` by cyclic symmetry and for `P1,P2,P3` in the
primed copy:

```text
boxed:
c(L1)=c(L2)=c(L3)=c(P1)=c(P2)=c(P3)=4.
```

This count is independent of the global RXC3 wiring beyond the regular promise that
each source element occurs in three source triples.

## 4. Internal L4,L5,P4,P5 have c=2

Take

```text
L4={z1,z2,z3}.
```

Its three neighbor pairs are

```text
{L1,D3},
{L2,D1},
{L3,D2}.
```

Among the eight raw transversals, direct inspection of the fixed gadget shows that
only two are independent:

```text
{L1,L2,L3},
{D3,D1,D2}.
```

Every mixed choice contains a conflicting pair through one of the other `z`
incidences.

Thus

```text
boxed:
c(L4)=2.
```

The same fixed local pattern gives

```text
boxed:
c(L5)=c(P4)=c(P5)=2.
```

## 5. D1--D6 have c=4

Consider

```text
D1={z2,z6,t1}.
```

Its three neighbor pairs are

```text
through z2 : {L2,L4},
through z6 : {L3,L5},
through t1 : {D6,D7}.
```

The local cross-adjacencies of the fixed E12 gadget eliminate exactly half of the
eight raw transversals. Direct enumeration leaves four independent triples.

The six rows `D1,...,D6` are related by the unprimed/primed and cyclic gadget
symmetries, hence

```text
boxed:
c(D_i)=4 for i=1,...,6.
```

The companion checker enumerates these transversals explicitly on the frozen q=6
target.

## 6. D7 has c=8

For

```text
D7={t1,t2,t3},
```

the three conflict-neighbor pairs are

```text
{D1,D6},
{D2,D4},
{D3,D5}.
```

No target triple from one displayed pair shares an element with a target triple
from another displayed pair. Therefore there are no cross-adjacencies at all among
the three pairs.

Every one of the eight transversals is independent:

```text
boxed:
c(D7)=8.
```

## 7. Global count for every E12 target

Each source gadget contributes exactly

```text
6 columns of type L1-L3/P1-P3 with c=4,
4 columns of type L4-L5/P4-P5    with c=2,
6 columns of type D1-D6          with c=4,
1 column  of type D7             with c=8.
```

Therefore per gadget:

```text
c=2 : 4 columns,
c=4 : 12 columns,
c=8 : 1 column.
```

For an RXC3 source with `q` triples, the E12 target has

```text
n=17q
```

variable-columns and exact distribution

```text
boxed:
c=2 : 4q,
c=4 : 12q,
c=8 : q.
```

In particular every target variable satisfies

```text
boxed:
c(v)>=2.
```

Thus the E49 exceptional set

```text
B={v:c(v)>=2}
```

is the entire target:

```text
boxed:
|B|=n.
```

## 8. Frozen q=6 control

For the E17 q=6 fixture,

```text
n=102.
```

The corrected checker computes on the target-column conflict graph:

```text
24 vertices with c=2,
72 vertices with c=4,
 6 vertices with c=8,
 0 vertices with c<=1.
```

Equivalently:

```text
L1-L3,P1-P3,D1-D6 -> 72 total vertices with c=4,
L4-L5,P4-P5       -> 24 total vertices with c=2,
D7                 ->  6 total vertices with c=8.
```

Hence

```text
t_multiclaw=102=n.
```

## 9. Consequence for E49

R5 E49 is polynomial when every local conflict domain has at most two states and is
FPT when only `t` vertices have two or more claw triples.

The E12 target instead has local state-domain sizes

```text
1+c(v) in {3,5,9}
```

at every vertex and

```text
t=n.
```

So the E49 backdoor is linear on the frozen NP-complete bridge.

Therefore:

```text
boxed:
DENSE MULTICLAW AMBIGUITY IS GENUINELY PRESENT THROUGHOUT THE E12 HARDNESS
TARGET ON THE CORRECT VARIABLE-CONFLICT GRAPH.
```

The exact 2/4/8 distribution replaces the erroneous point-graph 4/8 distribution.

## 10. What survives after the firewall

The hard bridge already defeats all strategies based only on:

```text
existence of claws,
non-claw forcing,
unique-claw 2-SAT,
small numbers of multiclaw vertices,
bounded constant local-state domains.
```

Every local domain is still constant-size, but the global compatibility CSP remains
NP-hard.

Thus the next graph-state attack must exploit the structure of **compatibility among
many 3/5/9-state domains**, not their individual sizes.

R5 E12's exact local gadget theorem and R5 E17's kernel quotient already suggest the
expected firewall: exact elimination of bounded gadget interiors can project back
to the original RXC3 source language.

## 11. Updated frontier

After corrected E50, a universal graph-state theorem must go beyond local ambiguity
counts and find a global matching, parity, potential, quotient, or decomposition
structure that the E12 source itself cannot reproduce.

The active graph-state frontier remains:

```text
GLOBAL COMPATIBILITY STRUCTURE OF DENSE MULTICLAW DOMAINS.
```

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e50_e12_multiclaw_firewall.py
```
