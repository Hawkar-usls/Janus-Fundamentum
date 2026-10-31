# R5 E9 — Singular UNSAT nontrivial-3-cut-irreducible hostile core

Date: 2026-09-28

Status: `JANUS_EXACT_HOSTILE_CORE_CONTROL__NO_D1_PROMOTION`

Scientific ceiling:

```text
THIS IS A FINITE EXACT COUNTERCONTROL INSIDE THE CURRENT RESIDUAL.
IT DOES NOT PROVE NP-HARDNESS OF THE 3-CUT-IRREDUCIBLE SUBCLASS.
IT DOES NOT PROVIDE A UNIVERSAL POLYNOMIAL DECIDER.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

Parents:
- `research/R5_E9_SINGULAR_UNSAT_RANK14_COUNTERCONTROL_2026-09-27_v1.0.md`
- `research/R5_E9_THREE_EDGE_CUT_BOUNDARY_ALGEBRA_2026-09-28_v1.0.md`
- `research/R5_E9_BALANCED_SET_PARTITIONING_EXACTONE_TERMINAL_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_singular_unsat_3cut_irreducible.py`

## 1. Frozen carrier

Use the existing normalized `15_3` carrier

```text
p = [5,7,9,10,3,1,14,2,4,6,12,13,8,0,11]
q = [12,9,14,11,13,10,7,3,1,0,2,5,6,8,4]
A = I + P + Q.
```

The row triples are

```text
{0,5,12}
{1,7,9}
{2,9,14}
{3,10,11}
{3,4,13}
{1,5,10}
{6,7,14}
{2,3,7}
{1,4,8}
{0,6,9}
{2,10,12}
{5,11,13}
{6,8,12}
{0,8,13}
{4,11,14}
```

The parent theorem already proves exactly

```text
connected = true
linear = true
row/column degree = 3
rank_Q(A) = 14
nullity_Q(A) = 1
Exact-One = UNSAT
```

with primitive rational-kernel generator

```text
g=(1,4,1,1,-2,-2,1,-2,-2,-2,-2,1,1,1,1).
```

## 2. Exact Levi 3-cut census

Let `L(A)` be the 30-vertex cubic bipartite Levi graph of `A`. It has 45 edges.

The checker exhausts all

```text
C(45,3)=14190
```

three-edge subsets. For each triple it deletes those three edges and computes the connected components by exact graph traversal.

The result is

```text
number of disconnecting 3-edge subsets = 30
component-size profile for every one   = (1,29)
nontrivial 3-edge cuts                 = 0
```

Moreover the 30 disconnecting triples are exactly the incident-edge stars of the 30 Levi vertices.

Thus every 3-edge cut is trivial: it isolates one vertex and leaves the other 29 vertices connected.

### Theorem SIC-3CUT-1

The frozen `15_3` Levi graph has edge-connectivity three and has no nontrivial three-edge separation. Equivalently for the current JANUS decomposition gate, it is already a `3-cut-irreducible` core; in standard cubic-graph language it is cyclically 4-edge-connected with respect to 3-edge cuts.

The theorem is a finite exact graph certificate, not an asymptotic statement.

## 3. Interaction with the balanced terminal

The new balanced set-partitioning theorem says every balanced cubic Exact-One incidence matrix is SAT. This frozen carrier is UNSAT, so it is necessarily unbalanced and belongs to the strong-odd-cycle residual.

Therefore the same explicit instance simultaneously satisfies

```text
connected linear cubic
nontrivial-3-cut-free
unbalanced / strong-odd-cycle residual
rank_Q = 14 < 15
nullity_Q = 1
Exact-One UNSAT
```

## 4. Consequence

The following prospective shortcut is false even after exhaustive exact <=3-edge separator preprocessing:

```text
3-CUT-IRREDUCIBLE
AND
SINGULAR OVER Q
=>
SAT.
```

Hence neither rational singularity nor the existence of the `-3` spectral eigenspace becomes sufficient merely by removing all genuine three-edge separations.

This control must be replayed against any proposed terminal based on

- determinant/singularity alone;
- `lambda_min=-3` alone;
- nontrivial-3-cut exhaustion plus singularity;
- balanced-vs-unbalanced classification followed by a bare spectral test.

## 5. What this does not close

The instance has constant size. It does not prove that Exact-One remains NP-hard on the entire 3-cut-irreducible subclass. It also does not rule out a different polynomial terminal using the certified strong odd cycle, Boben semantic reduction, or a source-specific global syndrome representation.

The active universal obligation remains:

```text
UNBALANCED + NONTRIVIAL-3-CUT-IRREDUCIBLE CORE
-> exact polynomial contraction or terminal
```

with polynomial witness reconstruction.

## 6. Frozen status

```text
SINGULAR LINEAR-CUBIC UNSAT = PROVED
NONTRIVIAL 3-EDGE CUTS      = NONE
TRIVIAL 3-EDGE CUTS         = 30 vertex stars
CURRENT RESIDUAL MEMBERSHIP = YES
SINGULAR CORE => SAT        = FALSIFIED
UNIVERSAL POLYNOMIAL DECIDER = OPEN
E8_D1 = EMPTY
P_VS_NP = OPEN
```
