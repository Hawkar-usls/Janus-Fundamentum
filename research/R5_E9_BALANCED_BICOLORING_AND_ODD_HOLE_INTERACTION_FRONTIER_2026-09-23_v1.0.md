# R5 E9 — Balanced Bicoloring Island, Denominator-13 LP Counterexample, and Odd-Hole Interaction Frontier

**Date:** 2026-09-23  
**Status:** source-bound positive island + exact JANUS-derived counterexamples/theorems.  
**Scientific boundary:** D1=EMPTY; P_VS_NP=OPEN.

## 1. Pair-defect zero fiber as a hypergraph bicoloring system

After the mandatory pivot conditioning / D1 defect normalization, the hard fiber can be written over the original Boolean variables x as:

- every D1 pair e={u,v}: x_u+x_v=1;
- every D2/D3 triple e={u,v,w}: 1 <= x_u+x_v+x_w <= 2;
- 0 <= x <= 1.

Equivalently every row/hyperedge must be non-monochromatic.

Let A be the 0/1 row-vertex incidence matrix of the mixed hypergraph with:
- D1 edges of size 2;
- D2,D3 edges of size 3.

Then the fractional bicoloring polytope is

P_bi(A)
=
{x in [0,1]^V :
 1 <= A_e x <= |e|-1 for every row e}.

The universal half-center x=(1/2,...,1/2) is always feasible.

## 2. Important correction: balanced does not mean totally unimodular

A balanced 0/1 matrix need not be totally unimodular.

Therefore the correct positive theorem is NOT:

BALANCED => TU.

The correct source-native theorem is stronger in the direction actually needed here:

If A is balanced, the bicoloring system obtained from (A,-A)

A x >= 1,
-A x >= 1-|e|,
0 <= x <=1

has an integral point whenever it is nonempty.

Equivalently every balanced hypergraph is bicolorable, and the standard balanced-matrix coloring machinery constructs such a bicoloring in polynomial time.

Balancedness itself is polynomial-time recognizable.

Hence:

### Theorem BBI-1

If the mixed D1/D2/D3 incidence matrix is balanced, then the zero pair-defect fiber is automatically YES and a witness is polynomially constructible.

This is a genuine polynomial positive island for the syndrome-image gate.

## 3. Unbalanced does NOT imply half-integral structure

A natural next hope is that the unbalanced side might still have only half-integral LP vertices, enabling a Nemhauser-Trotter style quotient.

This is false even on a tiny linear three-partition source instance.

Take variables 0,...,11 and the three partitions:

### D1 pairs

(0,1)
(2,3)
(4,5)
(6,7)
(8,9)
(10,11)

### D2 triples

(2,6,11)
(1,8,10)
(4,7,9)
(0,3,5)

### D3 triples

(1,5,11)
(2,9,10)
(0,7,8)
(3,4,6)

The instance is linear: any two distinct rows share at most one variable.

The bicoloring polytope has the exact feasible vertex

x*
=
1/13 *
(7,6,3,10,4,9,12,1,5,8,2,11).

All D1 equations are tight at 1.

All eight ternary rows are tight at either 1 or 2:

D2 row sums:
2,1,1,2.

D3 row sums:
2,1,1,2.

A set of twelve active equalities has determinant -13 and full rank 12.
The Smith normal form of that active basis is

diag(1,1,1,1,1,1,1,1,1,1,1,13).

Therefore x* is a genuine LP vertex with denominator 13.

### Theorem BBI-2

The mixed D1/D2/D3 bicoloring relaxation is not half-integral, quarter-integral, or bounded to denominator 2 even on a 12-variable linear partition instance.

In fact this exact instance has **no integral bicoloring at all** (verified exhaustively over all 2^12 assignments), while the universal half-center and the denominator-13 vertex are fractional feasible points.

Thus generic LP-feasibility, half-integral rounding, and bounded-denominator-2 quotienting do not solve the hard fiber.

## 4. Explicit unbalanced hole inside the denominator-13 instance

The incidence matrix contains the 3x3 odd-cycle submatrix on:

rows:
- D1 edge (0,1),
- D2 edge (1,8,10),
- D3 edge (0,7,8),

columns:
- 0,1,8.

The submatrix is

[1 1 0
 0 1 1
 1 0 1]

with determinant 2.

Thus the instance is unbalanced.

But this local odd hole is not by itself an unsatisfiable constraint.

## 5. Odd-hole boundary projection theorem

Consider a strong odd cycle of length l in a mixed NAE hypergraph.
Each cycle row is either:

- a pair edge NAE2(v_i,v_{i+1}), requiring v_i != v_{i+1}; or
- a ternary row NAE3(v_i,v_{i+1},s_i), with one outside spoke s_i.

Fix arbitrary values of every spoke.

### Theorem OH-1

If at least one row of the odd cycle is ternary, then existentially projecting all cycle vertices yields the universal relation on all spoke variables.

### Proof

Choose one ternary cycle row j.

Set its two consecutive cycle vertices equal to the value opposite its fixed spoke:

v_j=v_{j+1}=1-s_j.

This ternary NAE row is satisfied.

Traverse the remaining l-1 cycle rows around the cycle, assigning consecutive cycle vertices to alternate.

Every pair row is satisfied by inequality.

Every other ternary row is also satisfied because unequal first two coordinates always satisfy NAE regardless of its spoke.

Since l is odd, l-1 is even, so the alternating path returns with the same value at the second endpoint of row j, consistent with the initial equal assignment.

Thus every spoke assignment extends. QED.

## 6. In the three-partition source, every strong odd cycle is locally boundary-universal

D1 is a partition into disjoint pairs.

An all-D1 strong cycle would require every cycle vertex to lie in two distinct D1 pair rows, impossible.

Therefore every strong odd cycle in the D1/D2/D3 incidence hypergraph contains at least one ternary D2 or D3 row.

By OH-1:

> every individual strong odd cycle, considered with its own cycle vertices existentially projected, imposes no constraint at all on its outside spokes.

This is the crucial structural correction.

### Consequence

UNBALANCED
does NOT mean
ONE ODD HOLE CARRIES THE HARD CONSTRAINT.

Instead:

HARDNESS
=
INTERACTION / OVERLAP OF MULTIPLE LOCALLY-HARMLESS ODD HOLES
through variables and rows that cannot all be projected independently.

The denominator-13 vertex is a concrete witness that such interactions can create arithmetic structure far beyond a single determinant-2 odd cycle.

## 7. Why the denominator 13 matters

A single odd-cycle incidence submatrix has determinant magnitude 2.

Yet the 12-variable source instance has an active basis determinant 13.

Therefore overlapping/tightly coupled hole structure can generate higher-order lattice/torsion behavior that is not representable as independent Z_2 odd-cycle defects.

This kills another tempting simplification:

GLOBAL UNBALANCEDNESS
!=
INDEPENDENT COLLECTION OF PARITY-2 HOLES.

## 8. New active object

### R5_E9_ODD_HOLE_INTERACTION_COMPRESSION_GATE_V1

Input:
the pair-defect zero-fiber incidence system after all existing easy reductions.

First:
- if balanced, solve by balanced-hypergraph bicoloring;
- otherwise obtain / identify strong odd-hole structure.

Do NOT branch independently on holes.

Target:
construct a polynomial exact quotient of the **interaction system among locally boundary-universal odd holes**.

A candidate representation must preserve:
- zero-syndrome existence;
- polynomial witness reconstruction;
- polynomial total size;
- no enumeration of hole choices.

Primary invariants to study:
- overlap graph / hypergraph of strong odd holes;
- rank of the row space generated by hole submatrices;
- determinants / Smith normal forms of active interaction blocks;
- whether hole interaction admits exact series/parallel contractions;
- whether a bounded-interface block decomposition reduces balanced pieces plus a small nonbalanced torso.

## 9. Immediate falsifier program

Use the exact 12-variable denominator-13 NO instance as a frozen hard micro-benchmark.

Any proposed odd-hole quotient must:
1. detect that the instance is NOT in the balanced automatic-YES island;
2. not collapse its interacting holes into independent parity bits;
3. account for the determinant-13 active lattice behavior;
4. return NO without enumerating all 2^6 D1 pair orientations;
5. provide a replayable certificate.

D1 = EMPTY.  
P_VS_NP = OPEN.
