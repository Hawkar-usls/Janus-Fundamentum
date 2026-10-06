# R5 E101 — B3 Router to Mixed-Check Composition

Date: 2026-10-06

Status:
`SIXTEEN_OF_SEVENTEEN_B3_ROUTERS_ENTER_BINARY_DELTA_CLOSURE__EQ3_IS_THE_UNIQUE_SELF_SIMILAR_EXCEPTION`

Scientific ceiling:

```text
E101 DOES NOT YET GIVE A UNIVERSAL P-TIME EXACT-ONE SOLVER.

IT PROVES AN EXACT LOCAL COMPOSITION THEOREM FOR EVERY B_C=3 RIGID CORE:
AFTER ABSORBING ITS THREE ADJACENT MIXED ExactOne CHECKS, 16/17 POSSIBLE
ROUTER TYPES BECOME EXPLICITLY REPRESENTED BINARY MATROID MODULES.

THE UNIQUE EXCEPTION IS THE TRUE TERNARY EQUALITY ROUTER. ITS COMPOSED
SIX-PORT RELATION IS NON-DELTA, BUT IT IS EXACTLY SEMANTICALLY EQUIVALENT
TO A SINGLE ORDINARY Equality_3 VARIABLE CONNECTED TO THE SAME THREE
MIXED CHECKS.

THUS ARBITRARILY LARGE B3 RIGID INTERIORS DISAPPEAR FROM THE HARD KERNEL:
THEY BECOME EITHER COMPACT BINARY MODULES OR ONE PRIMITIVE EQUALITY NODE.

THE REMAINING CONSTRUCTIVE GAP IS IDENTIFYING THE EXACT ROUTER FAMILY
INSIDE AN ARBITRARILY LARGE CORE IN POLYNOMIAL TIME.

P_VS_NP = OPEN.
```

## 1. Input from E99-E100

E99 proved that every connected rigid core has boundary size divisible by three.

E100 completely classified the first nontrivial boundary

```text
B_C=3.
```

Its exact three-port relation R is one of exactly 17 nonempty families:

```text
3 affine residue-0 families:
  {000}
  {111}
  {000,111}

7 nonempty subsets of the weight-1 layer:
  {100,010,001}

7 nonempty subsets of the weight-2 layer:
  {110,101,011}.
```

Every relation except

```text
EQ3={000,111}
```

is equicardinal and therefore an ordinary matroid basis family on three
elements. Since every matroid on at most three elements is binary, all 16 are
binary matroids.

## 2. Mixed checks adjacent to a B3 core

A B3 rigid core has three boundary inert incidences.

Each enters a non-rigid mixed ExactOne check

```text
ExactOne(r_i,a_i,b_i),
qquad i=0,1,2,
```

where r_i is the inert/router bit and a_i,b_i are the other two incident
Boolean variables/incidences.

E99 proved that an ordinary check can contain

```text
0, 1, or 3 inert incidences,
never exactly 2.
```

A mixed check is by definition non-rigid, so it cannot contain 3 inert
incidences.

Therefore every mixed check contains at most one inert incidence.

Consequences:

```text
* the three boundary incidences of one B3 core land on three distinct
  mixed checks;

* no mixed check can simultaneously belong to the boundary of two
  different rigid cores;

* B3 core + its three mixed checks is a vertex-disjoint local gadget
  across different B3 cores.
```

So the E101 rewrite can be applied to all B3 gadgets in parallel.

## 3. Exact six-port composition

Eliminate r_i from

```text
R(r_0,r_1,r_2)
AND
ExactOne(r_0,a_0,b_0)
AND
ExactOne(r_1,a_1,b_1)
AND
ExactOne(r_2,a_2,b_2).
```

At each port:

```text
r_i=1  =>  (a_i,b_i)=(0,0)

r_i=0  =>  exactly one of (a_i,b_i) is 1.
```

Call the resulting exact six-port relation G(R).

## 4. Dual-plus-parallel theorem

Assume first that R is not EQ3.

Then all feasible router sets have one cardinality, so R is the basis family of
a three-element binary matroid M.

For a router basis S in R, the six-port state selects one representative from
pair

```text
P_i={a_i,b_i}
```

exactly when

```text
i notin S.
```

Thus the active pair indices form the complement

```text
[3]-S,
```

which is a basis of the dual matroid M*.

For every element i of M*, replace i by a parallel pair P_i.

The bases of that parallel extension are exactly:

```text
choose a basis B of M*;
for each i in B choose exactly one of a_i,b_i.
```

But this is exactly G(R).

Hence:

```text
boxed:
G(R) = parallel-pair lift of M*
```

for every non-EQ B3 router.

Binary representability is preserved by duality and parallel extension.

Therefore:

```text
boxed:
16 of the 17 E100 B3 router types become explicitly represented
binary matroid basis families after absorbing the three mixed checks.
```

In particular every such six-port relation is an even binary delta-matroid and
can enter the E78 linear-delta gluing machinery.

## 5. Explicit representation size

The simplified dual matroid M* has only three elements and rank at most three.

Choose any GF(2) matrix representation

```text
A=[v_0 v_1 v_2].
```

Then a representation of G(R) is obtained by duplicating each column:

```text
boxed:
A_G=[v_0 v_0 v_1 v_1 v_2 v_2].
```

So every non-EQ B3 gadget has a binary representation of size at most

```text
3 x 6.
```

The representation size is constant, independent of the number of vertices
hidden inside the original rigid core.

This is stronger than a bounded-interface statement: it is an explicit
representation construction once the exact router family R is known.

## 6. The unique EQ3 exception

Now take

```text
R={000,111}.
```

If r=111, all three mixed checks force

```text
(a_i,b_i)=(0,0)
```

for every i.

If r=000, each pair must contain exactly one selected bit.

Hence

```text
G(EQ3)
=
{000000}
union
{choose exactly one from each of P_0,P_1,P_2}.
```

There are exactly

```text
1+2^3=9
```

states, of Hamming weights 0 and 3.

E101 freezes an explicit symmetric-exchange failure, so:

```text
boxed:
G(EQ3) is NOT a delta-matroid.
```

This kills the tempting but false theorem

```text
"every B3 router plus one mixed-check layer enters linear-delta closure."
```

The failure is unique among all 17 E100 types.

## 7. Why EQ3 does not create a new gadget

Although G(EQ3) is non-delta, it is exactly the relation obtained from one
ordinary Boolean variable z satisfying Equality_3 across its three incidences:

```text
exists z:
  ExactOne(z,a_0,b_0)
  AND ExactOne(z,a_1,b_1)
  AND ExactOne(z,a_2,b_2).
```

Indeed:

```text
z=1 => all active pairs 00,
z=0 => each active pair has exactly one 1.
```

Thus:

```text
boxed:
an arbitrarily large EQ3 rigid core can be replaced exactly by ONE
ordinary Equality_3 variable.
```

The exceptional relation is therefore self-similar, not a new growing
boundary language.

## 8. Parallel elimination theorem

Because mixed checks are unique to their incident rigid core, all B3 cores can
be processed simultaneously.

For each core:

```text
if R != EQ3:
  absorb the core plus its three mixed checks into one represented
  binary-matroid six-port module;

if R == EQ3:
  replace the whole rigid core by one Equality_3 variable and keep the
  three mixed checks.
```

After this exact rewrite:

```text
* no internal rigid check remains from any B3 core;
* non-EQ rigid complexity survives only as constant-size represented
  binary modules;
* EQ rigid complexity survives only as ordinary primitive equality nodes.
```

So B3 rigid interiors cannot themselves generate unbounded representation
complexity.

## 9. Relation to E78

Every non-EQ E101 module is a represented binary matroid basis family, hence a
linear delta-matroid.

Therefore multiple such modules can be combined by E78's exact equality-gluing
identity and the Koana-Wahlstrom linear-delta closure theorem whenever the rest
of the decomposition also enters that represented class.

This is the first direct route from the E99/E100 rigid-core structure into the
existing E78 polynomial algebra.

What remains outside that closure is now explicit:

```text
primitive Equality_3 stars + whatever active/mixed residual network still
connects them.
```

That is a much smaller target than arbitrary rigid interiors.

## 10. The constructive identification gap

E101 must not hide one important issue.

E100 proves that the exact router family belongs to one of 17 possibilities
and gives three canonical atom-cover states.

But in repeated-atom cases there may be optional feasible boundary states not
determined by those three canonical covers alone.

Therefore the following is NOT yet proved:

```text
given an arbitrary large B3 rigid core,
identify its exact member of the 17-family list in polynomial time.
```

Once R is known, E101's representation construction is constant-time.

Finding R is still a constructive problem.

This distinction is essential for the eventual universal algorithm:

```text
existence of a compact representation
!=
polynomial-time extraction of the exact representation.
```

## 11. What E101 changes

Before E101:

```text
B3 rigid cores:
  constant-size semantics known,
  but composition with surrounding mixed checks open.
```

After E101:

```text
16/17 types:
  exact explicit binary-delta module after one mixed-check layer.

1/17 type:
  exact contraction to one primitive Equality_3 node.

all B3 cores:
  parallel local reduction is exact.
```

Thus the rigid obstruction has been reduced to two independent residual
questions:

```text
A. constructive router identification;

B. the rigid-free / equality-star residual network and its E97/E98
   rectangle holonomy.
```

## 12. E102 target

The next proof target should not revisit B3 topology.

It should attack the remaining global kernel:

```text
E102 RIGID-FREE RECTANGLE-HOLONOMY KILLER

After applying the E101 reductions:

1. represented non-EQ B3 modules are handed to the E78 algebra;
2. EQ3 cores are contracted to primitive Equality nodes;
3. no large rigid interior remains.

Use E96-E98 on the residual mixed network.

Goal:
  prove that a rigid-free TARGET6 parent necessarily admits two coherent
  independent 2+2 exchange rectangles, hence h1=h2=0 and raw8;

or:
  construct the first rigid-free rectangle-holonomy obstruction.
```

In parallel, the algorithmic branch must solve:

```text
E102-C CONSTRUCTIVE ROUTER IDENTIFICATION

Recover the exact one of 17 router families in polynomial time from the
internal B3 core, or show that the global solver can avoid identifying it.
```

Scientific status:

```text
E101 = EXACT B3 ROUTER-TO-MIXED-CHECK COMPOSITION THEOREM.

NON_EQ_B3_TYPES = 16/16 ENTER EXPLICIT BINARY-DELTA CLOSURE.
EQ3_B3_TYPE = UNIQUE NON-DELTA SELF-SIMILAR EXCEPTION.
B3_RIGID_INTERIOR_GROWTH = ELIMINATED SEMANTICALLY.
CONSTRUCTIVE_ROUTER_IDENTIFICATION = OPEN.
RIGID_FREE_RECTANGLE_HOLONOMY = OPEN.
UNIVERSAL_POLYNOMIAL_EXACT_ONE_SOLVER = NOT YET CONSTRUCTED.
P_VS_NP = OPEN.
```
