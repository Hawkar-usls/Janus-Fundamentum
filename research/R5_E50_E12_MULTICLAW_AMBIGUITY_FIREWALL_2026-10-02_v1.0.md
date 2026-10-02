# R5 E50 — E12 Multiclaw Ambiguity Firewall

Date: 2026-10-02

Status:
`EXACT_HARDNESS_BRIDGE_MULTICLAW_FIREWALL__EVERY_E12_TARGET_VERTEX_HAS_4_OR_8_CLAW_STATES__E49_BACKDOOR_LINEAR`

Scientific ceiling:

```text
R5 E49 SOLVES THE CONFLICT-STATE CSP BY 2-SAT WHEN EVERY VERTEX HAS AT MOST
ONE CLAW-LEAF TRIPLE, AND BY O(21^t poly(n)) WHEN ONLY t VERTICES HAVE TWO
OR MORE CLAW TRIPLES.

THE R5 E12 NP-COMPLETE HARDNESS BRIDGE LIVES MAXIMALLY FAR FROM THAT REGIME.
FOR EVERY TARGET PRODUCED BY THE E12 GADGET REDUCTION:

  each internal z or Z vertex has exactly 4 claw triples;
  each local t vertex has exactly 8 claw triples;
  each global boundary x or x' vertex has exactly 8 claw triples.

THEREFORE EVERY TARGET VERTEX IS MULTICLAW AND
  t_multiclaw = n.

SO E49 IS A GENUINE FPT ISLAND, NOT A UNIVERSAL SOLVER IN DISGUISE.
P_VS_NP = OPEN.
```

## 1. Recall the E12 target gadget

Each RXC3 source triple is replaced by the 17-row / 15-internal-element gadget of
R5 E12.

For one gadget the variable types are

```text
boundary: x1,x2,x3,p1,p2,p3
unprimed internal: z1,...,z6
primed internal:   Z1,...,Z6
local: t1,t2,t3.
```

The target source rows are

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

Global boundary variables are identified across the three source gadgets incident
to the same RXC3 element. Every target variable has source degree three and the
target remains linear.

## 2. Claw triples in a cubic-linear conflict neighborhood

For any target variable `v`, its six conflict neighbors are partitioned into the
three source-pairs contributed by the three source rows containing `v`.

A claw-leaf triple centered at `v` is exactly an independent transversal selecting
one neighbor from each of those three pairs.

Without extra cross-adjacencies there are

```text
2^3=8
```

possible transversals.

The E12 gadget either preserves all eight or introduces local cross-conflicts that
remove exactly half.

## 3. Boundary variables have eight claw triples

Take a global boundary variable `x` (the primed case is identical).

RXC3 regularity makes `x` occur in exactly three source gadgets. In each gadget its
target occurrence is in one row of the form

```text
{x, z_a, z_b}.
```

Hence its six conflict neighbors are arranged as three disjoint pairs, one pair
from each distinct gadget.

Internal variables belonging to different gadgets never share target source rows,
so there are no cross-adjacencies between different pairs.

Therefore every choice of one endpoint from each pair is independent:

```text
boxed:
c(x)=8.
```

The same proof gives

```text
c(x')=8.
```

This is independent of the specific RXC3 instance.

## 4. The t-variables have eight claw triples

Consider `t1`; the other two cases are cyclic relabelings.

Its three source rows are

```text
D1={z2,z6,t1},
D6={Z1,Z5,t1},
D7={t1,t2,t3}.
```

Thus its neighbor pairs are

```text
{z2,z6},
{Z1,Z5},
{t2,t3}.
```

No endpoint from one displayed pair is adjacent to an endpoint from another pair:
inspection of D2--D5 shows that `t2,t3` couple to different z/Z coordinates, while
primed and unprimed z families meet only through the t variables and never directly.

Therefore the induced neighborhood is exactly `3K2`, and all eight transversals are
independent:

```text
boxed:
c(t_i)=8
```

for `i=1,2,3`.

## 5. The z/Z variables have exactly four claw triples

It suffices by gadget symmetry to inspect one representative, say `z1`.

The three source rows containing `z1` are

```text
L1={x1,z1,z4},
L4={z1,z2,z3},
D3={z1,z5,t3}.
```

So the three source-pairs in `N(z1)` are

```text
{x1,z4},
{z2,z3},
{z5,t3}.
```

There are eight raw transversals. Additional gadget rows create cross-adjacencies:

```text
z4 -- z5     via L5,
z4 -- z3     via D2,
z2 -- z5     via L2,
z2 -- t3     via D1? no: D1 uses z2,z6,t1,
```

and the complete direct inspection of the fixed 17-row gadget leaves exactly four
independent transversals.

The same local pattern is carried to every `z_i` by the cyclic gadget symmetries;
the primed copy is isomorphic. Hence

```text
boxed:
c(z_i)=c(Z_i)=4
```

for every `i=1,...,6`.

Because this statement is purely local, the global RXC3 wiring does not change it.

The companion exact checker independently enumerates all neighborhood triples on the
frozen q=6 target and verifies the full count distribution.

## 6. Global count

For an RXC3 instance with `q` source triples, the E12 target contains

```text
12q z/Z internal vertices,
3q  t vertices,
2q  global boundary x/x' vertices,
```

for a total of

```text
n=17q.
```

The claw-count distribution is therefore

```text
c=4 : 12q vertices,
c=8 :  5q vertices.
```

Equivalently,

```text
boxed:
all n=17q vertices satisfy c(v)>=4.
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

## 7. Frozen q=6 control

For the q=6 E17 fixture,

```text
n=102.
```

The checker obtains exactly

```text
72 vertices with c=4,
30 vertices with c=8,
0 vertices with c<=1.
```

Broken down by type:

```text
z  : 36 vertices, all c=4,
Z  : 36 vertices, all c=4,
t  : 18 vertices, all c=8,
x  :  6 vertices, all c=8,
x' :  6 vertices, all c=8.
```

Therefore

```text
t_multiclaw=102=n.
```

## 8. Consequence for E49

R5 E49 gives

```text
O(21^t poly(n))
```

when only `t` vertices have multiple claw triples.

On the E12 reduction target,

```text
t=n,
```

so this branch is exponential and gives no universal polynomial bound.

Therefore:

```text
boxed:
MULTICLAW AMBIGUITY IS GENUINELY PRESENT AT LINEAR DENSITY IN THE FROZEN
NP-COMPLETE HARDNESS BRIDGE.
```

This is the correct firewall against over-interpreting E48/E49.

## 9. What survives after the firewall

The local-state picture is still useful, but the hard target carries 5-state or
9-state local domains everywhere:

```text
1 SEL state + 4 claw states for z/Z,
1 SEL state + 8 claw states for t/x/x'.
```

So the next question cannot be whether local domains are small in an absolute
constant sense; they already are, yet the global CSP remains NP-hard.

The useful next target is structural compression of **compatibility among these
constant-size domains**.

For the E12 gadget, R5 E17 already shows that much local linear freedom quotients to
the original RXC3 source. The graph-state analogue should therefore determine
whether eliminating internal 5/9-state variables also projects exactly to a compact
boundary relation that recreates the RXC3 choice.

If so, that will identify precisely how the NP-hard source survives every local-state
compression.

## 10. Updated frontier

After E50, a universal graph-state theorem must exploit something stronger than

```text
bounded local state count,
claw existence,
unique-claw forcing,
or a sparse population of ambiguous vertices.
```

The hard bridge already defeats all four.

The remaining graph-state frontier is:

```text
GLOBAL COMPATIBILITY STRUCTURE OF DENSE MULTICLAW DOMAINS.
```

A successful polynomial theorem must either expose another global matching/parity/
potential structure in that compatibility system or prove a decomposition that the
E12 source cannot evade.

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e50_e12_multiclaw_firewall.py
```
