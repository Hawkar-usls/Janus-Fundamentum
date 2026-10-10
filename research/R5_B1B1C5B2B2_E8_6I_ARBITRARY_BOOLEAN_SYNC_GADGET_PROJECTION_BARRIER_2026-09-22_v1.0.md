# R5 E8 6I — Arbitrary Boolean Synchronization-Gadget Projection Barrier

Date: 2026-09-22

Authority: `PROVED_SCOPED_THEOREM__NO_D1_PROMOTION__NO_SUCCESSOR_AUTHORIZATION`

## 1. Statement

Consider any finite Boolean CSP gadget `G` with exposed Boolean variables:

```text
x, y
```

and any finite set of internal Boolean auxiliary variables:

```text
z_1,...,z_t.
```

Every gadget constraint may be an arbitrary Boolean relation of arbitrary finite arity.

Assign to every gadget variable `v` a ternary Boolean operation:

```text
f_v.
```

Assume each gadget constraint relation is preserved by the mixed tuple of operations assigned to the variables in its scope.

Then the full gadget solution relation:

```text
Sol(G)
subseteq
{0,1}^{2+t}
```

is a subalgebra of the product of the variable algebras.

Therefore its projection onto the exposed variables:

```text
S(x,y)
=
exists z_1...z_t
Sol(G)
```

is preserved by:

```text
(f_x,f_y).
```

This conclusion is independent of the internal gadget shape, relation arities, number of auxiliaries, or whether the internal operations are equal.

## 2. Proof

Take any three satisfying gadget assignments:

```text
a,b,c in Sol(G).
```

Construct a new assignment `d` coordinate-wise:

```text
d(v)
=
f_v(a(v),b(v),c(v)).
```

For every gadget constraint `R(v_1,...,v_k)`, the three restricted tuples from `a,b,c` belong to `R`.

By the assumed mixed preservation of that constraint:

```text
(
 f_{v_1}(a(v_1),b(v_1),c(v_1)),
 ...
 f_{v_k}(a(v_k),b(v_k),c(v_k))
)
in R.
```

Hence `d` satisfies every constraint.

Thus:

```text
d in Sol(G).
```

So `Sol(G)` is closed under the coordinate-wise product operation.

Now project `Sol(G)` onto `x,y`.

Given any three endpoint tuples in the projected relation, choose witnesses for their internal variables, combine the three full witnesses coordinate-wise as above, and project the resulting satisfying assignment.

Therefore:

```text
S
is preserved by
(f_x,f_y).
```

This is exactly the standard fact that projections of subalgebras are subalgebras, written here in the variable-specific/multi-sorted form needed by 6I.

## 3. Exact equality consequence

Suppose the gadget is an exact synchronization gadget:

```text
S
=
EQ
=
{(0,0),(1,1)}.
```

Then `(f_x,f_y)` preserves EQ.

For arbitrary ternary Boolean operations this is equivalent to:

```text
f_x
=
f_y.
```

Proof:

for every input triple `u=(u_1,u_2,u_3)`, use the three EQ tuples:

```text
(u_1,u_1),
(u_2,u_2),
(u_3,u_3).
```

Preservation requires:

```text
(f_x(u),f_y(u))
in EQ,
```

hence:

```text
f_x(u)=f_y(u)
```

for every `u`.

Therefore:

```text
ANY EXACT BOOLEAN EQ GADGET
FORCES IDENTICAL ENDPOINT OPERATIONS.
```

This is not specific to B4.

## 4. Exact disequality consequence

Suppose instead:

```text
S
=
NEQ
=
{(0,1),(1,0)}.
```

Preservation requires for every input triple `u`:

```text
(
 f_x(u),
 f_y(not u)
)
in NEQ.
```

Thus:

```text
f_y(not u)
=
not f_x(u).
```

Equivalently:

```text
f_y
=
dual(f_x),
```

where:

```text
dual(f)(x,y,z)
=
not f(not x,not y,not z).
```

Therefore:

```text
ANY EXACT BOOLEAN NEQ GADGET
FORCES DUAL ENDPOINT OPERATIONS.
```

Again this is not specific to B4.

## 5. B4 consequence

For:

```text
B4
=
{AND3,OR3,MAJ3,XOR3},
```

the dual map is:

```text
AND3 <-> OR3
MAJ3 <-> MAJ3
XOR3 <-> XOR3.
```

Therefore no existential Boolean gadget implementing exact EQ or NEQ can permit endpoint B4 labels beyond the same/dual synchronization already proved for direct EQ/NEQ.

Internal auxiliary relations may themselves admit mixed algebra types.

That does not matter:

```text
EXACT ENDPOINT SYNCHRONIZATION
PROJECTS THE FULL GADGET
BACK TO EQ/NEQ,

AND THE ENDPOINT TYPE BARRIER
REAPPEARS AUTOMATICALLY.
```

## 6. Strength over the previous occurrence theorem

Previous theorem:

`R5_B1B1C5B2B2_E8_6I_BOOLEAN_OCCURRENCE_SYNCHRONIZATION_CONJUGATION_THEOREM_2026-09-22_v1.0.md`

closed:

```text
direct EQ/NEQ constraints
+
Boolean id/not occurrence reformulation.
```

The present theorem closes the strictly larger class:

```text
ARBITRARY FINITE BOOLEAN AUXILIARY GADGET
whose existentially projected endpoint semantics
is exactly EQ or NEQ.
```

No restriction is made on:

- number of Boolean auxiliaries;
- arity of internal relations;
- internal graph/treewidth;
- choice of variable-specific ternary operations;
- whether internal relations are functional.

## 7. Consequence for the search

A successful B4 weak-relaxation mechanism cannot resolve a variable-type conflict merely by:

1. splitting one original Boolean variable into Boolean copies;
2. inserting any exact Boolean gadget between copies;
3. existentially hiding the gadget variables.

If reconstruction requires those exposed Boolean copies to represent exactly the same original bit, then the endpoint operation labels remain equal/dual.

Therefore the next admissible escape must change at least one foundational feature, for example:

```text
A. remove exposed Boolean copies and encode the bit in a richer lifted domain;

B. use a global/nonlocal exact representation whose consistency is not a projected EQ/NEQ gadget;

C. change the tractable certificate family rather than trying to route B4 labels through Boolean synchronization.
```

This theorem does not rule out any of A-C.

## 8. Relation to corpus mechanisms

The theorem explains why several old mechanisms fail to become universal merely by gadgetization:

- Boolean variable renaming/domain permutations;
- Tseitin-style Boolean copy variables;
- hidden local Boolean synchronization networks.

It is a direct multi-sorted/subalgebra projection argument and therefore belongs next to the induced-algebra and lifted-CSP source cluster.

## 9. Claim ceiling

```text
ARBITRARY BOOLEAN EQ/NEQ AUXILIARY GADGET
AS B4 TYPE ROUTER
=
THEOREM_LEVEL FALSIFIED

RICHER LIFTED-DOMAIN CODE
=
OPEN

NONLOCAL EXACT REPRESENTATION
=
OPEN

OTHER TRACTABLE CERTIFICATE FAMILY
=
OPEN

P_VS_NP
=
OPEN

D1
=
EMPTY

SUCCESSOR_ALGORITHM
=
LOCKED
```
