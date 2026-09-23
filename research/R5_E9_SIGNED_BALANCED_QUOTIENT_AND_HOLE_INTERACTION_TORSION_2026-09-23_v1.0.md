# R5 E9 — Signed-Balanced Quotient and Hole-Interaction Torsion

**Date:** 2026-09-23  
**Status:** source-bound signed-balanced positive island + exact JANUS-derived hard micro-core.  
**Scientific boundary:** D1=EMPTY; P_VS_NP=OPEN.

## 1. Exact D1 pair substitution

For every D1 pair (x_i,y_i) with

x_i XOR y_i = 1,

choose one representative r_i=x_i and substitute

y_i=1-r_i.

Every D2/D3 positive NAE3 constraint becomes a **signed NAE3** constraint on three representatives.

Encode one signed NAE row by a vector

a in {0,+1,-1}^m,

where +1 means the representative appears positively and -1 means its complemented occurrence appears.

Let n(a) be the number of -1 entries and p(a) the number of +1 entries.

For Boolean r, the signed NAE row is exactly:

1-n(a) <= a r <= p(a)-1.

Indeed:
- the lower inequality says at least one signed literal is true;
- the upper inequality says at least one signed literal is false.

Thus the pair-defect zero problem is a generalized bicoloring system for a 0,±1 matrix.

## 2. Signed-balanced polynomial island

Classical balanced-matrix theory extends from 0/1 to 0,±1 matrices.

If A is balanced, the generalized bicoloring polytope

P(A)
=
{r in [0,1]^m :
 A r >= 1-n(A),
 -A r >= 1-n(-A)}

is integral.

Moreover balancedness of 0,±1 matrices is polynomial-time recognizable.

Therefore:

### Theorem SBQ-1

After exact D1 pair substitution, if the signed D2/D3 incidence matrix is balanced, then the zero-syndrome fiber is polynomially solvable and an integral witness is constructible.

This strictly sharpens the unsigned balanced-hypergraph positive island because pair substitution exposes literal signs and can recognize signed structure directly.

## 3. Exact 6-variable signed hard micro-core

Start from the 12-variable linear three-partition NO instance:

D1:
(0,1),(2,3),(4,5),(6,7),(8,9),(10,11)

D2:
(2,6,11),(1,8,10),(4,7,9),(0,3,5)

D3:
(1,5,11),(2,9,10),(0,7,8),(3,4,6)

Choose representatives:

r0=x0,
r1=x2,
r2=x4,
r3=x6,
r4=x8,
r5=x10.

The eight signed NAE rows are:

[ 0,+1, 0,+1, 0,-1]
[-1, 0, 0, 0,+1,+1]
[ 0, 0,+1,-1,-1, 0]
[+1,-1,-1, 0, 0, 0]
[-1, 0,-1, 0, 0,-1]
[ 0,+1, 0, 0,-1,+1]
[+1, 0, 0,-1,+1, 0]
[ 0,-1,+1,+1, 0, 0].

This signed NAE3 system has no Boolean solution.

Yet its generalized bicoloring polytope contains the exact vertex

r*
=
1/13 (7,3,4,12,5,2).

All eight rows are tight at one of their two signed-NAE bounds.

Six independent active rows form a 6x6 matrix of determinant +13.

Its Smith normal form is

diag(1,1,1,1,1,13).

Thus:

### Theorem SBQ-2

High-denominator fractional structure survives **after** exact D1 pair substitution.

The denominator-13 phenomenon is therefore intrinsic to the signed ternary hard core, not an artifact of duplicated pair variables.

## 4. Minimal signed unbalanced hole

Rows 0 and 5, restricted to representative columns r1 and r5, give:

[+1,-1
 +1,+1].

Each row and column has exactly two nonzeros and the total sum is 2 mod 4.

Hence this is a minimal signed unbalanced hole.

Its determinant has magnitude 2.

## 5. Signed-hole boundary projection is still locally universal

Consider two signed NAE3 rows realizing this 2x2 hole.
Up to renaming/complementing local coordinates the constraints have form

NAE(x, NOT y, u)
and
NAE(x, y, v),

where u,v are the third/spoke variables.

For every fixed pair (u,v) in {0,1}^2, there exists an assignment to (x,y) satisfying both rows.

Therefore projecting the two cycle/interface variables yields the universal binary relation on (u,v).

More generally, the same traversal argument as for unsigned odd holes extends to any signed cycle in which every row has a third spoke:
after normalizing literal signs, use unequal local literal values around all but one row; the closing row can always be satisfied, choosing the starting value appropriately if equality is required.

Thus an individual signed unbalanced hole is again **locally boundary-harmless**.

## 6. Structural consequence

Signed balancedness gives a real polynomial island.

But failure of signed balancedness is not itself a local hard constraint:

- one signed hole has determinant 2;
- one signed hole projects to no boundary restriction;
- the 6-variable NO core has an active determinant 13.

Therefore the missing structure is:

INTERACTION OF MULTIPLE LOCALLY-UNIVERSAL SIGNED HOLES.

This interaction can create higher-order lattice/torsion behavior that cannot be modeled as independent parity defects.

## 7. New active gate

### R5_E9_SIGNED_HOLE_INTERACTION_TORSION_GATE_V1

Pipeline:

1. exact D1 pair substitution;
2. build signed NAE matrix A;
3. if A is signed-balanced, solve by generalized bicoloring;
4. otherwise identify signed unbalanced holes / decomposition blocks.

Target:

construct a polynomial exact quotient of their **interaction**, preserving:
- Boolean feasibility;
- witness reconstruction;
- polynomial total state;
- no branch over holes or pair orientations.

Primary invariants:
- signed-hole overlap graph;
- determinant / Smith-normal-form growth in active blocks;
- whether pivot/decomposition operations reduce hole interaction;
- whether signed-balanced blocks can be separated by small interfaces;
- whether torsion-generating blocks admit compact series/parallel composition.

Frozen micro-benchmark:
the exact 6-variable denominator-13 signed NO core above.

Any candidate quotient must explain why:
- each individual signed hole is locally harmless,
- yet their coupled system has no Boolean model,
- and fractional extreme structure reaches denominator 13.

D1 = EMPTY.
P_VS_NP = OPEN.
