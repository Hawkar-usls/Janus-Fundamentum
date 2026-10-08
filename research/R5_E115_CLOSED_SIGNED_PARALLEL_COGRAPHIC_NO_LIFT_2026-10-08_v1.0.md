# R5 E115 — Closed Signed-Parallel Cographic Lift No-Go

Date: 2026-10-08

Status:
`OCCURRENCE_CLOSED_3CIRCUIT_RIGID_SIGNED_PARALLEL_JOINT_LIFT_IMPOSSIBLE`

Scientific ceiling:

```text
E115 DOES NOT YET EXCLUDE MIXED-NORMAL LEAKAGE OR COGRAPHIC CORES WITH
NONTRIVIAL 3-EDGE CUTS.

IT PROVES AN ALL-SIZE NO-LIFT THEOREM FOR THE OCCURRENCE-CLOSED,
NORMAL-FAITHFUL LANE WHEN THE ABSTRACT CUBIC NORMAL GRAPH HAS ONLY
VERTEX-STAR 3-CIRCUITS.

IN THAT LANE, EVERY EXACT COVER SELECTS THE TWO TANNER COPIES OF EACH
SIGNED-PARALLEL NORMAL IDENTICALLY.  E113 REQUIRES THEIR SIX-WITNESS
SUPPORT PARITIES TO BE OPPOSITE.  CONTRADICTION.

P_VS_NP = OPEN.
```

## 1. Setup

Let H be a connected simple cubic graph.

For every abstract normal edge e=uv, a joint E113 lift has two distinct Tanner
occurrence variables

```text
x_(u,e),
x_(v,e)
```

with the same residual normal g_e.

The distinguished check D_v contains the three occurrence variables local to v.

E113 requires the two copies on every edge to have opposite six-witness support
parity.

E115 studies the strongest closed realization attempt:

```text
* every remaining check touching these variables contains only variables from
  the same occurrence block;
* every such external check is normal-faithful, so its three residual normals
  form a 3-circuit of the abstract normal matroid;
* H has no nontrivial 3-edge cuts, hence its only 3-circuits are the three-edge
  vertex stars.
```

Thus every external occurrence-only check has a unique star type v.

## 2. External star multiplicities

Let t_v be the number of external checks of star type v.

Take one normal edge e=uv.

There are exactly two Tanner occurrence variables carrying g_e.
Each already occurs once in a distinguished check and, by cubicity, has two
remaining external incidences.

So the total number of external incidences carrying g_e is four.

Only star types u and v contain normal g_e. Therefore

```text
t_u+t_v=4
```

for every edge uv.

## 3. C4-free restriction on one star type

A type-v external check chooses, for each of the three incident normals, either

```text
local copy x_(v,e)
or
remote copy x_(u,e).
```

Represent that choice by a 3-bit word, with 1 meaning local.

Two restrictions follow from Tanner C4-freeness.

First, one external type-v check may contain at most one local copy. Otherwise
two local variables would share both D_v and that external check.

Hence the only allowed words are

```text
000, 100, 010, 001.
```

Second, two external checks of the same star type may share at most one actual
variable. Two choice words therefore need Hamming distance at least two.

Consequently:

```text
t_v <= 3.
```

Combining with t_u+t_v=4 gives only

```text
(1,3), (2,2), (3,1)
```

across an edge.

For connected nonbipartite H, t_v=2 globally.

For connected bipartite H, the two bipartition classes may carry 1/3, 2/2,
or 3/1.

## 4. The 3/1 lane

At a t=3 vertex, the only pairwise C4-free family is the three unit words

```text
100, 010, 001.
```

Write local occurrence values as a1,a2,a3 and remote copies as b1,b2,b3.

The distinguished ExactOne equation is

```text
a1+a2+a3=1.
```

The three external equations are

```text
a1+b2+b3=1,
b1+a2+b3=1,
b1+b2+a3=1.
```

Subtracting the distinguished equation gives

```text
(a2-b2)+(a3-b3)=0,
(a1-b1)+(a3-b3)=0,
(a1-b1)+(a2-b2)=0.
```

Over the integers these force

```text
a1=b1,
a2=b2,
a3=b3.
```

Thus every signed-parallel pair incident to the t=3 side is selected equally
in every exact cover.

In a 3/1 bipartite completion every edge touches the t=3 side, so this already
forces equality on every pair globally.

## 5. The 2/2 lane

At a t=2 vertex, the two C4-free star checks must be two distinct unit words.

Relabel the two local-choice edges a,b and the omitted edge m.

The omitted edges match across endpoints by variable-degree accounting, so they
form a perfect matching M of H.

The other two edges at every vertex form the complementary 2-factor.

Write local-minus-remote exact-cover differences

```text
d_a, d_b, d_m.
```

Subtracting the two external ExactOne equations from the distinguished equation
gives

```text
d_a=d_b=-d_m.
```

Call the common value tau_v.

Across every graph edge the endpoint-oriented difference reverses sign.
Because matching/nonmatching status is consistent at both endpoints,

```text
tau_u=-tau_v
```

for every edge uv.

If tau_v=+1, both local nonmatching variables at v must equal one, contradicting
the distinguished ExactOne check immediately.

If tau_v=-1, every neighbor has tau=+1 and is impossible.

Therefore

```text
tau_v=0
```

for every vertex.

Hence local and remote copies are equal on every edge.

## 6. Exact-cover support consequence

Sections 4 and 5 cover every possible star-multiplicity pattern.

Therefore for every exact cover C and every edge e=uv,

```text
C(x_(u,e)) = C(x_(v,e)).
```

Take six exact TARGET6 witnesses.

The two occurrence copies of e are selected by exactly the same subset of the
six witness labels.

Thus their complete support sets are equal:

```text
S_(u,e)=S_(v,e).
```

In particular their support cardinality parities are equal.

But E113 requires the two copies of every signed-parallel normal to have
opposite support parity.

Contradiction.

So:

```text
boxed:
NO occurrence-closed C4-free normal-faithful joint lift exists when the
abstract cubic normal graph has only vertex-star 3-circuits.
```

## 7. Frozen graph witness

The checker uses the 12-vertex Möbius ladder.

It is:

```text
cubic,
connected,
nonbipartite,
18 edges.
```

Exhaustive three-edge-cut enumeration gives exactly 12 cuts, each isolating one
vertex.

Therefore it is a concrete 12-check E112-style abstract obstruction whose
3-circuit structure is rigid enough for the E115 theorem.

The point is not the finite size.  The proof above is all-size.

## 8. What remains

A genuine growing signed-parallel joint lift must now escape E115 in one of two
ways:

```text
A. nontrivial 3-edge cuts:
   an external occurrence-only check may use a non-vertex-star 3-circuit;

B. mixed-normal leakage:
   at least one outside check mixes signed-core occurrence variables with
   variables/normals outside the closed core.
```

Both are structured escape mechanisms.

The first is already a low-order graph separation.
The second creates an explicit interface between the signed core and the rest
of the Tanner parent.

## 9. Correct E116 target

```text
E116 THREE-EDGE-CUT / LEAKAGE DECOMPOSITION

Input:
  a growing signed-parallel core that escapes E115.

Goal:
  * if a nontrivial 3-edge cut exists, cut the normal core there and summarize
    the side by an O(1)-state interface compatible with E110;
  * otherwise E115 forces mixed-normal leakage;
  * prove enough leakage also yields a bounded-width separator or lowers the
    residual interface rank;
  * or construct the first exact TARGET6/no-raw8 mixed-leakage family.
```

Scientific status:

```text
E115 = ALL-SIZE CLOSED-COMPLETION NO-LIFT THEOREM.

OCCURRENCE-CLOSED + NORMAL-FAITHFUL + ONLY VERTEX-STAR 3-CIRCUITS
=> SIGNED-PARALLEL SUPPORT LIFT IMPOSSIBLE.

ESCAPES:
  NONTRIVIAL 3-EDGE CUTS,
  OR MIXED-NORMAL LEAKAGE.

UNIVERSAL POLYNOMIAL EXACTONE SOLVER = NOT YET CONSTRUCTED.
P_VS_NP = OPEN.
```
