# R5 E99 — Rigid-Defect Inert-Core Boundary Reduction

Date: 2026-10-06

Status:
`RIGID_DEFECTS_FORM_INERT_CORES__CORE_BOUNDARY_IS_MULTIPLE_OF_THREE__CLOSED_CORES_ARE_SOLVABLE`

Scientific ceiling:

```text
E99 DOES NOT YET ELIMINATE EVERY RIGID DEFECT.

IT PROVES THAT THE FIVE E96 RIGID DEFECT TYPES ARE EXACTLY THE CHECKS OF AN
"INERT" SUBSYSTEM INVISIBLE TO ALL THREE E97 OPPOSITE-PAIR EXCHANGE GRAPHS.

EVERY CONNECTED RIGID CORE HAS BOUNDARY SIZE DIVISIBLE BY THREE, AND A CLOSED
BOUNDARY-ZERO RIGID CORE HAS AN EXPLICIT EXACT COVER AND CANNOT BE A MINIMAL
OBSTRUCTION.

P_VS_NP = OPEN.
```

## 1. Inert supports

Recall the three opposite TARGET6 atoms

```text
O0={X_A,Q_BC}
O1={X_B,Q_AC}
O2={X_C,Q_AB}.
```

Call a six-state variable support inert when it is a union of whole opposite
atoms.

There are exactly

```text
2^3 = 8
```

such support types.

Equivalently, for every opposite pair the two labels are either both present or
both absent, so the support has split vector

```text
000.
```

Thus an inert variable is absent from all three E97 opposite-pair exchange
graphs.

## 2. Rigid defects are exactly all-inert checks

At an ordinary ExactOne check, the supports of the three incident variables
partition all six TARGET6 labels.

If all three supports are inert, they partition the three indivisible opposite
atoms among three bins. Up to permutation of incident variables, these are
exactly the Bell(3)=5 coarsenings already identified by E96.

Hence

```text
boxed:
ordinary check is E96-rigid
iff
all three incident variables have inert supports.
```

This gives a geometric meaning to the five formerly abstract rigid partitions.

## 3. Exactly two inert incidences are impossible

Suppose two incident supports are inert.

They are disjoint unions of opposite atoms. Their union is therefore also a
union of atoms. Since the three supports partition all six labels, the third
support is the complement of that union and is again a union of whole atoms.

Therefore

```text
boxed:
an ordinary check has 0, 1, or 3 inert variables — never exactly 2.
```

So every non-rigid check is either completely exchange-active at the support
level or carries a single inert incidence that joins a rigid region to the
active region.

## 4. Rigid-core boundary arithmetic

Construct the rigid core from

```text
* inert cubic variables;
* rigid ordinary checks;
* incidences between them.
```

For one connected core component C let

```text
V_C = number of inert variables,
R_C = number of rigid checks,
B_C = incidences from inert variables of C to non-rigid/mixed checks.
```

Every inert variable is a cubic source variable, so it contributes three
incidences.

Every rigid check consumes exactly three inert incidences.

Thus

```text
3|V_C| = 3|R_C| + B_C
```

and therefore

```text
boxed:
B_C = 3(|V_C|-|R_C|).
```

Immediate consequences:

```text
B_C == 0 (mod 3),
and if B_C>0 then B_C>=3.
```

So a rigid obstruction cannot leak into the exchange-active region through one
or two isolated incidences. The first possible interface has arity three.

## 5. Closed rigid cores are exactly coverable

Now take

```text
B_C=0.
```

Every check of the component is rigid and every inert variable keeps all three
incidences inside the component.

Choose any one opposite atom O_i globally.

Select exactly those inert variables whose support contains O_i.

At each rigid check the three incident supports partition the three opposite
atoms. Therefore exactly one incident support contains O_i.

Hence every rigid check is covered exactly once.

Thus the closed core has three canonical exact covers, one for each opposite
atom:

```text
boxed:
B_C=0 => rigid core is exactly coverable and cannot by itself obstruct state8.
```

In a minimal TARGET6/no-state8 obstruction, closed rigid components can
therefore be discarded from the hard core.

## 6. New rigid frontier

Any genuinely relevant rigid region must satisfy

```text
B_C in {3,6,9,...}.
```

The first unresolved rigid gadget is therefore a connected inert core with
exactly three mixed boundary incidences.

This is finite-interface structure, not arbitrary global geometry.

Combined with E98, a no-state8 parent must now use at least one of two
mechanisms:

```text
A. a rigid core with boundary >=3 and 0 mod3;

B. exchange-rectangle holonomy preventing two coherent independent
   2+2 opposite-pair decompositions.
```

## 7. E100 target

The next rigid killer is now exact:

```text
B3 RIGID-CORE CLASSIFICATION

Classify connected inert cores with B_C=3 under C4-free cubic geometry.

For each core:
  * compute the relation induced on its three mixed incidences;
  * show it is either reducible/affine/exactly coverable for state8,
    or forces a repeated Tanner pair;
  * otherwise freeze the first irreducible B3 rigid gadget.
```

A successful B3 reduction should then support induction by cutting any larger
B_C=3k core along a 3-boundary separator.

Scientific status:

```text
E99 = UNIVERSAL RIGID-INERT CORE REDUCTION.
CLOSED_RIGID_CORES = SOLVABLE.
RELEVANT_RIGID_BOUNDARY = 0 MOD 3, MINIMUM 3.
GLOBAL_TARGET6_PARENT = OPEN.
P_VS_NP = OPEN.
```
