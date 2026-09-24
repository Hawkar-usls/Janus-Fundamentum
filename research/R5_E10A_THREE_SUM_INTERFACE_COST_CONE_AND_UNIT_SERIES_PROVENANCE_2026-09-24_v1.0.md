# R5 E10A — 3-Sum Interface Cost Cone and Unit-Series Provenance Universalization

Date: 2026-09-24

Authority:
`JANUS_DERIVED_EXACT_INTERFACE_THEOREM__P2_SCALAR_PROVENANCE_NOT_A_COMPRESSION_CURRENCY__NO_DETERMINISTIC_SOLVER_CLAIM`

Parent:
`R5_E10A_TWO_ROW_LINEAGE_REBIND_GATE_V2`

Checker:
`experiments/r5_e10a_three_sum_interface_cost_cone.py`

## 1. Purpose

The lineage rebind identified a real scope widening:

```
actual E10 origin
M([I+P+Q | 1])
    ->
3-connected S8-containing torso/interface
    ->
PA-0005 generic two-row lift [B_G;S].
```

The first proposed surviving promise was separator-conditioned weight provenance:

- original/nonvirtual elements have unit origin cost;
- nonunit effective costs may arise only on virtual elements produced by 2/3-sum absorption;
- in a 3-sum, the three virtual costs satisfy source-induced consistency relations.

This note determines the exact scalar 3-sum cost cone in the positive-unit lineage and then tests whether scalar provenance alone restricts the generic two-row torso class.

## 2. Source-bound necessity: the three interface costs are metric

Let

```
Z={z_12,z_23,z_31}
```

be the common triangle of a binary 3-sum.

Golynski--Horton, *A Polynomial Time Algorithm to Find the Minimum Cycle Basis of a Regular Matroid* (SWAT 2002), define the weight transferred from an absorbed side by first assigning the connecting elements prohibitively large temporary weight and then, for each `z in Z`, computing a minimum circuit `D_z` containing `z` and no other connecting element. Write

```
Q_z = D_z - {z}
```

and transfer

```
w(z)=w(Q_z).
```

Their proof explicitly derives the triangle inequalities. For example,

```
w(z_31) <= w(z_12)+w(z_23),
```

because the symmetric difference of the corresponding conditioned cycles with the separator triangle supplies a candidate for the third condition.

Thus every positive-unit 3-sum child exports a positive integer triple

```
(a,b,c)
```

satisfying

```
a <= b+c,
b <= a+c,
c <= a+b.
```

Source:
Golynski--Horton 2002, DOI 10.1007/3-540-45471-3_21.

## 3. Converse theorem: every positive integer metric triple is realizable

### Theorem — UNIT_GRAPHIC_3SUM_INTERFACE_CONE

Let

```
(a,b,c) in Z_{>0}^3
```

satisfy the three triangle inequalities.

Construct three interface vertices

```
A,B,C.
```

Add internally vertex-disjoint unit-edge paths

```
P_AB of length a,
P_BC of length b,
P_CA of length c.
```

Add the three virtual separator edges

```
z_AB=AB,
z_BC=BC,
z_CA=CA,
```

which form the common triangle `Z`.

Consider the graphic matroid of this side.

For `z_AB`, a circuit containing `z_AB` but no other element of `Z` is exactly `z_AB` plus an internal A--B path. The two candidates are:

```
P_AB                       cost a
P_AC union P_CB            cost c+b.
```

Because `a<=b+c`, the conditioned transferred cost is exactly `a`.

Cyclically the other two costs are `b` and `c`.

Deleting all of `Z` leaves the connected internal three-path network, so no cocircuit of this graphic matroid is contained in `Z). Hence the separator satisfies the standard binary 3-sum side condition used by the source decomposition.

Therefore

```
POSITIVE INTEGER 3-SUM INTERFACE COST CONE
=
POSITIVE INTEGER METRIC CONE ON THREE POINTS.
```

This is an exact converse to the source-bound triangle inequalities.

It is a scalar-interface theorem only. It does not characterize every additional matroid state a different decomposition algorithm might retain.

## 4. Stronger P2 control: arbitrary integer weights can be unitized

Let

```
(G, lambda, w),
lambda:E->GF(2)^2,
w:E->Z_{>0}
```

be any positively integer-weighted two-row graph-lift path instance.

Replace every edge

```
e=uv
```

of weight `w(e)=k` by an internally vertex-disjoint path of exactly `k` unit edges.

Put the original group label `lambda(e)` on one edge of this chain and label every other chain edge `00`.

Then every simple path of the original graph has a unique expanded simple path and conversely every simple path in the expanded graph suppresses to a simple path in the original graph.

The maps preserve exactly:

```
total GF(2)^2 label,
weighted cost <-> unit edge count,
endpoints,
simplicity.
```

Hence for every label `g`,

```
d_g(G,lambda,w)
=
d_g(G_unit,lambda_unit,1).
```

At the lifted-matroid level each subdivision vertex supplies an incidence row supported on its two adjacent chain elements. Repeatedly suppressing these series extensions recovers the original weighted core element. Equivalently, the weighted core can appear as the torso after 2-sum/series-side absorption, with the nonunit value carried by a virtual interface element.

Therefore the condition

```
GLOBAL REAL ELEMENTS ARE UNIT WEIGHT
+
NONUNIT CORE VALUES COME FROM SEPARATOR ABSORPTION
```

does not by itself restrict positive-integer weighted two-row path optimization.

## 5. Consequence for the complete-scaffold strict-max control

The generic weighted self-embedding based on the complete four-labelled scaffold can be repaired with respect to P2:

1. retain the 3-connected, S8-containing complete two-row scaffold as the core torso;
2. choose polynomially bounded large integer weights on auxiliary completion edges;
3. replace each weight-`k` core edge by a unit series chain of length `k` in the global graph-lift;
4. after series/2-sum absorption the core recovers exactly the intended effective weight.

Thus, inside the generic **unit-weight two-row graph-lift class with decomposition interfaces**,

```
STRICT-MAX
+
THREE-CONNECTED TORSO
+
S8-CONTAINING
+
UNIT REAL ELEMENTS
+
SEPARATOR-GENERATED NONUNIT CORE COSTS
```

still does not by itself exclude the prescribed-label shortest-path self-embedding.

The blow-up is polynomial whenever the chosen artificial weights are polynomially bounded; the strict-max completion only needs a bound larger than the polynomially known maximum length of a simple target path.

## 6. P2 verdict

Freeze:

```
THREE_SUM_INTERFACE_TRIANGLE_INEQUALITIES
=
SOURCE_BOUND NECESSARY

EVERY POSITIVE INTEGER METRIC TRIPLE
=
UNIT_GRAPHIC REALIZABLE

2_SUM / SERIES EFFECTIVE SCALAR COST
=
ARBITRARY POSITIVE INTEGER REALIZABLE

SEPARATOR_CONDITIONED SCALAR WEIGHT PROVENANCE
=
NOT A COMPRESSION CURRENCY
IN THE GENERIC UNIT TWO-ROW CLASS
```

This invalidates the hope that the three triangle inequalities alone form the first strict image invariant.

## 7. What remains lineage-specific

The repaired self-embedding is **not** proved to come from the actual cubic origin

```
M([I+P+Q | 1]).
```

The original E10 target retains the global identity

```
3|x| = n + 2t
```

for `Hx=1`, and the exact decision/search target

```
shortest_f = n/3 + 1.
```

The cubic `I+P+Q` representation is not hereditary torso-by-torso, so it may not be imposed locally. The next admissible question is instead an image/provenance question:

```
Which 3-connected two-row-lift torsos,
together with their virtual separator elements,
can actually occur in a decomposition of
M([I+P+Q | 1])?
```

Scalar separator costs alone no longer distinguish this image.

## 8. Next gate

Freeze:

```
R5_E10A_CUBIC_ORIGIN_TORSO_IMAGE_GATE_V1
```

Required:

either

A. construct a polynomial lineage-preserving embedding of arbitrary prescribed `GF(2)^2` shortest path into an actual `M([I+P+Q|1])` decomposition whose relevant torso is the strict-max 3-connected S8-containing two-row core; or

B. derive an exact invariant of the cubic-origin decomposition image that the repaired unit-series self-embedding cannot satisfy.

Priority invariants to test:

- restrictions on the joint pattern of 2/3-sum virtual elements, not their scalar weights alone;
- cocircuit/cycle parity inherited from the all-ones distinguished column;
- coupling between torso interface choices and the global lower-bound-tight equality;
- any decomposition-tree conservation law induced by the square 3-regular origin.

Forbidden:

- reimposing literal local `I+P+Q` or local cubic degree on a torso;
- treating triangle inequalities as a strict lineage invariant;
- reopening generic weighted PA-0005 PIT before this image audit;
- performing new cubic-origin image mathematics before PA-0006 is completed;
- using series expansion itself as evidence that the expanded instance has cubic origin.

## 9. Scientific ceiling

```
3-SUM POSITIVE-INTEGER INTERFACE CONE
=
EXACTLY METRIC TRIPLES

UNIT SERIES EXPANSION
=
EXACT LABEL/COST PRESERVING

P2 SCALAR COST PROVENANCE
=
FALSIFIED AS STANDALONE LEVERAGE

GENERIC UNIT TWO-ROW SELF-EMBEDDING
WITH P0+P1+P2
=
SURVIVES

ACTUAL I+P+Q ORIGIN SELF-EMBEDDING
=
NOT PROVED

CUBIC-ORIGIN TORSO IMAGE
=
OPEN

DETERMINISTIC GF(2)^2 PRESCRIBED SHORTEST PATH
=
OPEN

D1
=
EMPTY

P_VS_NP
=
OPEN
```
