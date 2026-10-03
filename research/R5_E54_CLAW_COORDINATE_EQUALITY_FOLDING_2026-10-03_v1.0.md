# R5 E54 — Claw-Coordinate Equality Folding

Date: 2026-10-03

Status:
`EXACT_BOOLEAN_EQUALITY_QUOTIENT__TYPE3_AND_ONE_TYPE4_CLAW_ORBITS_ARE_NOT_IRREDUCIBLE`

Scientific ceiling:

```text
THIS NOTE DOES NOT SOLVE THE FULL E12 HARD CORE.

IT PROVES THAT SEVERAL OF THE E53 LOCAL CLAW TYPES ARE NOT GENUINELY
IRREDUCIBLE.  WHEN TWO CLAW-CHOICE COORDINATES ARE PERFECTLY CORRELATED
OR ANTICORRELATED OVER THE ENTIRE LOCAL CLAW FAMILY, THE CORRESPONDING
NEIGHBOR VARIABLES ARE EQUAL IN EVERY GLOBAL EXACT-ONE WITNESS.

THESE EQUALITIES ARE SAFE BOOLEAN QUOTIENTS.  AFTER SUBSTITUTION, THE TWO
SOURCE ROWS THROUGH THE CENTER BECOME DUPLICATES AND ONE CAN BE DELETED.

IN THE E53 ATLAS THIS APPLIES TO:
  THE SIZE-2 ORBIT,
  THE UNIQUE SIZE-3 ORBIT,
  ONE OF THE THREE SIZE-4 ORBITS.

THUS THE UNIQUE TYPE-3 FRONTIER FROM E53 IS ELIMINABLE BY EXACT EQUALITY
FOLDING; IT IS NOT A FINAL HARD LOCAL LANGUAGE.

P_VS_NP = OPEN.
```

## 1. Local setup

Let `v` be a variable-vertex of the conflict graph of an all-positive
square+cubic+linear E12 carrier.

The three source rows containing `v` partition its six neighbors into three pairs

```text
P_i={p_i^0,p_i^1},  i=0,1,2.
```

If `v` is unselected in an Exact-One witness, each of its three source rows chooses
exactly one of the two neighbors.  Hence the selected-neighbor set is encoded by a
claw choice

```text
z=(z_0,z_1,z_2) in C_v subseteq {0,1}^3,
```

where `p_i^(z_i)` is selected.

If `v` itself is selected, all six neighbors are unselected.

## 2. Deterministic coordinate correlation

Suppose for two source-pair coordinates `i != j` there is a fixed bit `c` such that

```text
z_i xor z_j = c
```

for every claw choice `z in C_v`.

Then for every endpoint label `a in {0,1}` and every global Exact-One witness,

```text
boxed:
x_(p_i^a) = x_(p_j^(a xor c)).
```

Proof.

If `v=1`, all six neighbors are zero, so the equality is immediate.

If `v=0`, exactly one endpoint is selected from each pair.  The relation
`z_j=z_i xor c` says precisely that endpoint `a` in pair `i` is selected iff endpoint
`a xor c` in pair `j` is selected.  Therefore the Boolean values agree.

This is a global witness implication derived from local conflict geometry; it does
not assume anything about the states of the other vertices.

## 3. Exact quotient

The two equalities

```text
p_i^0 = p_j^c,
p_i^1 = p_j^(1 xor c)
```

may therefore be substituted globally in the Boolean Exact-One instance.

The two source rows through `v`

```text
R_i={v,p_i^0,p_i^1},
R_j={v,p_j^0,p_j^1}
```

then become identical after quotienting.

Hence one duplicate row can be deleted without changing the Boolean solution set.

The quotient operation may create repeated variables, changed coefficients, lower
occurrences, or additional forcing.  Those outputs must be routed through the
existing exact simplifiers (E40 low-degree peeling, E43 asymmetric ternary reduction,
E44 occurrence reduction, KPROJ/equality closure, etc.).  No claim is made that the
quotient remains square+cubic+linear.

## 4. E53 atlas consequence

The eight canonical E53 post-E52 claw families are represented by sizes

```text
2,3,4,4,4,5,6,8.
```

The companion checker tests pairwise XOR correlations between the three claw-choice
coordinates and finds exactly:

```text
size 2 : three deterministic coordinate correlations;
size 3 : one deterministic coordinate correlation;
size 4a: none;
size 4b: none;
size 4c: one deterministic coordinate correlation;
size 5 : none;
size 6 : none;
size 8 : none.
```

For the unique size-3 representative

```text
C_v={000,001,110},
```

we have

```text
z_0=z_1
```

for every claw.  Therefore, after orienting the first two source pairs consistently,

```text
boxed:
x_(p_0^0)=x_(p_1^0),
x_(p_0^1)=x_(p_1^1).
```

Thus TYPE-3 can always be folded; it is not an irreducible local core.

For the correlated size-4 representative

```text
C_v={000,001,110,111},
```

the same equality `z_0=z_1` holds, so the same quotient applies.

The size-2 orbit already has stronger global treatment in E51, but E54 shows that it
also carries local equality folding.

## 5. Router update

After E52/E53 local claw classification, apply:

```text
EQC0  for every unresolved vertex compute its canonical claw family;
EQC1  search pairwise claw-coordinate XOR constants;
EQC2  convert each constant to two exact Boolean equalities among neighbors;
EQC3  union-find the equalities globally;
EQC4  substitute quotient variables in all source rows;
EQC5  delete duplicate equations;
EQC6  rerun E40/E43/E44/KPROJ and all cheap forcing until closure.
```

This procedure is polynomial and preserves SAT exactly.

## 6. Updated local frontier

Before E54, E53 left eight local orbit types.

After equality folding, three are locally reducible:

```text
size 2,
size 3,
one size-4 orbit.
```

The genuinely uncorrelated local atlas is therefore reduced to five canonical types:

```text
two size-4 orbits,
size 5,
size 6,
size 8.
```

The size-8 type is the maximally ambiguous neighborhood in which no cross-pair
conflict edge exists beyond the three source-pair edges; it remains a particularly
important candidate for the true hard core.

The next useful attack is to determine which of the two uncorrelated size-4 relations
admit another exact polynomial quotient/propagation rule, and whether the maximally
ambiguous size-8 family already supports the full E12 hardness after all previous
closures.

```text
P_VS_NP = OPEN.
```

Companion checker:

```text
experiments/r5_e54_claw_coordinate_equality_folding.py
```
