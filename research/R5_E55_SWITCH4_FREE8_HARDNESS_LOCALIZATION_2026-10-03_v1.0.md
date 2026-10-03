# R5 E55 — SWITCH4 / FREE8 Hardness Localization

Date: 2026-10-03

Status:
`EXACT_E12_HARDNESS_LOCALIZATION__RXC3_BRIDGE_USES_ONLY_SWITCH4_AND_FREE8_CLAW_TYPES`

Scientific ceiling:

```text
THIS NOTE DOES NOT GIVE A POLYNOMIAL ALGORITHM.

IT SHARPENS THE POST-E54 FRONTIER BY REPLAYING THE SELF-CONTAINED R5 E12
NP-HARDNESS REDUCTION THROUGH THE E53 CLAW ATLAS.

FOR EVERY E12 TARGET PRODUCED FROM AN RXC3 SOURCE OF SIZE q:

  ALL 12q z/z' INTERNAL VARIABLES HAVE THE SAME UNCORRELATED SIZE-4 CLAW
  ORBIT

      SWITCH4 = {000,001,010,101};

  ALL 3q t VARIABLES AND ALL 2q GLOBAL BOUNDARY x/x' VARIABLES HAVE

      FREE8 = {0,1}^3.

THUS THE 17q-VARIABLE NP-HARD TARGET LIVES ENTIRELY IN THE TWO-TYPE LOCAL
LANGUAGE

      { SWITCH4, FREE8 }.

COUNTS ARE EXACTLY

      SWITCH4 = 12q,
      FREE8   =  5q.

THEREFORE THE OTHER E53 CLAW ORBITS ARE NOT NEEDED TO CARRY THE FROZEN E12
HARDNESS.  ANY UNIVERSAL POLYNOMIAL CLOSURE OF THE E12 ROUTE MUST IN
PARTICULAR SOLVE THE SWITCH4/FREE8 MIXTURE OR ELIMINATE IT BY A GLOBAL
QUOTIENT/DECOMPOSITION.

P_VS_NP = OPEN.
```

## 1. Recall the E12 gadget

For one RXC3 source triple `C_j={x_1,x_2,x_3}`, R5 E12 introduces

```text
unprimed internal variables z_1,...,z_6,
primed internal variables   z'_1,...,z'_6,
three connector variables   t_1,t_2,t_3,
```

plus the global boundary variables `x_i,x'_i`.

The target rows are

```text
L_1={x_1,z_1,z_4}
L_2={x_2,z_2,z_5}
L_3={x_3,z_3,z_6}
L_4={z_1,z_2,z_3}
L_5={z_4,z_5,z_6}
```

and the primed copy `L'_1,...,L'_5`, together with

```text
D_1={z_2,z_6,t_1}
D_2={z_3,z_4,t_2}
D_3={z_1,z_5,t_3}
D_4={z'_2,z'_6,t_2}
D_5={z'_3,z'_4,t_3}
D_6={z'_1,z'_5,t_1}
D_7={t_1,t_2,t_3}.
```

R5 E12 proves this gives a square+cubic+linear target with `17q` variables and
`17q` rows, and that target Exact-One is equivalent to the source RXC3 instance.

## 2. Boundary variables are FREE8

Fix one global boundary variable `x`.

Because the RXC3 source is 3-regular, `x` occurs in exactly three E12 gadgets and in
exactly one `L_1/L_2/L_3` row inside each incident gadget.

Hence the three source-pairs around the conflict vertex `x` consist of two internal
`z` neighbors from each of three distinct gadgets.

There is no target row containing internal variables from two distinct gadgets.
Therefore there are no cross-pair conflict edges among these six neighbors.

Every one of the eight pair transversals is consequently independent, so

```text
boxed:
C_x={0,1}^3=FREE8.
```

The same argument applies to every primed boundary variable `x'`.

There are exactly

```text
q unprimed boundary variables,
q primed boundary variables,
```

so boundary FREE8 contributes `2q` vertices.

## 3. Connector variables t are FREE8

Consider for example `t_1`.  Its three source rows are

```text
D_1={z_2,z_6,t_1},
D_6={z'_1,z'_5,t_1},
D_7={t_1,t_2,t_3}.
```

Thus its three source-pairs are

```text
{z_2,z_6},
{z'_1,z'_5},
{t_2,t_3}.
```

Direct inspection of the gadget row list shows that no row contains one endpoint
from two distinct displayed pairs.  Hence no cross-pair conflict edge exists in
`N(t_1)` beyond the three source-pair edges themselves.

Therefore every pair transversal is a claw and

```text
C_(t_1)=FREE8.
```

The same cyclic argument holds for `t_2,t_3`.

Every gadget contributes exactly three `t` variables, hence connector FREE8
contributes `3q` vertices.

Combining with the boundary contribution gives

```text
boxed:
FREE8 count = 2q+3q = 5q.
```

## 4. Every z-variable is SWITCH4

Now fix an unprimed `z_i` in one gadget.  Its three incident source rows are among

```text
one boundary L-row,
one of L_4/L_5,
one of D_1/D_2/D_3.
```

The six neighbors therefore split into three source-pairs.

A direct finite role audit of the six symmetric positions `z_1,...,z_6` gives,
after arbitrary orientation of each source-pair and cube symmetry,

```text
boxed:
C_(z_i) = {000,001,010,101}.
```

This is exactly the uncorrelated size-4 E53 orbit denoted here by `SWITCH4`.

One convenient Boolean parameterization is

```text
a=z_2,
b=the free switch bit,

z_0=a AND b,
z_1=(1-a) AND b,
z_2=a,
```

so all four `(a,b)` states occur.  Equivalently the canonical claw relation is the
2-CNF family forbidding

```text
(z_0,z_1)=(1,1),
(z_0,z_2)=(1,0),
(z_1,z_2)=(1,1).
```

The primed gadget is isomorphic, so every `z'_i` has the same orbit.

There are six `z` and six `z'` variables per source gadget. Therefore

```text
boxed:
SWITCH4 count = 12q.
```

The companion checker explicitly constructs full E12 targets and verifies this
classification and count for several deterministic 3-regular RXC3 fixtures.

## 5. Exact count audit

The two classes account for all target variables:

```text
SWITCH4 : 12q,
FREE8   :  5q,
----------------
total   : 17q.
```

This matches the E12 target size exactly.

No size-2, size-3, correlated size-4, size-5 or size-6 E53 local orbit is needed by
the hardness reduction.

## 6. Consequence for E48--E54

R5 E48--E52 give strong forcing when a vertex has too few claws, non-full claw union,
or nonempty all-claw intersection.

R5 E54 folds deterministic pair-coordinate correlations, eliminating the size-3
orbit and one correlated size-4 orbit.

E55 shows why those exact reductions cannot by themselves close the universal E12
route: the self-contained NP-hardness bridge already avoids them.

Its internal hard logic is carried by `SWITCH4`, while `FREE8` supplies maximally
ambiguous boundary/connector neighborhoods.

Thus the post-E55 local hard target can be frozen much more sharply as

```text
SWITCH4 + FREE8 MIXTURE.
```

## 7. What a universal algorithm must now do

Any claimed deterministic polynomial algorithm for the frozen square+cubic+linear
Exact-One class must, at minimum, handle all E12 images.  By this note, that means it
must handle instances whose every conflict vertex belongs to only the two local
orbits

```text
SWITCH4,
FREE8.
```

So the next high-value attack should not spend effort on the other E53 local types.
It should target one of the following global questions:

```text
1. Can the SWITCH4 vertices be quotient-compressed into a polynomial global
   language while leaving FREE8 boundaries tractable?

2. Can the SWITCH4/FREE8 incidence pattern be recognized as a known RHS-stable
   kernel language after exact gauge elimination?

3. Can the E12 local gadget be algebraically eliminated to expose a simpler source
   operator on the RXC3 boundary variables, and can that boundary operator then be
   solved in polynomial time?
```

R5 E17 already shows that local gauge elimination exposes the original source kernel
rather than destroying the source difficulty, so option 3 must genuinely solve the
remaining RXC3 boundary problem rather than merely rename it.

```text
P_VS_NP = OPEN.
```

Companion checker:

```text
experiments/r5_e55_e12_switch4_free8_hardness_localization.py
```
