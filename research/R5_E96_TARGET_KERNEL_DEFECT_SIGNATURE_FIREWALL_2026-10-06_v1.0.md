# R5 E96 — Target-Kernel Defect Signature Firewall

Date: 2026-10-06

Status:
`FOUR_CANONICAL_STATE8_PARITY_CANDIDATES__RIGID_DEFECTS_ARE_EXACTLY_OPPOSITE_PAIR_COARSENINGS`

Scientific ceiling:

```text
E96 DOES NOT YET EXCLUDE ALL SIX-STATE DELTA PARENTS.

IT PROVES A COMPLETE FINITE CLASSIFICATION OF HOW AN E95 TRIPLE-EVEN DEFECT
CAN REACT TO THE TWO INDEPENDENT TARGET-DERIVED GF(2) KERNEL CORRECTIONS.

ONLY FIVE OF 31 EVEN SUPPORT PARTITIONS ARE LOCALLY UNREPAIRABLE.
THEY ARE EXACTLY THE COARSENINGS OF THREE OPPOSITE TARGET-STATE PAIRS.

IF NO SUCH RIGID DEFECT EXISTS, GLOBAL FAILURE OF ALL FOUR CANONICAL
PARITY CANDIDATES REQUIRES ALL THREE PAIRWISE-CONFLICT REPAIR SIGNATURES
TO OCCUR SOMEWHERE IN THE GEOMETRY.

P_VS_NP = OPEN.
```

## Setup

Use target-state labels

```text
0 = X_A
1 = X_B
2 = X_C
3 = Q_AB
4 = Q_AC
5 = Q_BC.
```

The six boundary masks have two independent XOR dependencies

```text
D1 = {X_A,X_B,Q_AC,Q_BC}
D2 = {X_A,X_C,Q_AB,Q_BC}.
```

XORing the corresponding four internal witnesses gives two GF(2) kernel
vectors h1,h2.  Adding span<h1,h2> to the E95 even-occurrence assignment
produces four canonical parity assignments with the same raw boundary parity
state 8.

At an E95 base defect, the three incident variable support sets form a
partition of the six target labels into three even-cardinality blocks.

There are exactly 31 unlabeled such partitions.

## Exact finite classification

For each even partition and each nonzero correction

```text
h2, h1, h1+h2
```

E96 asks whether the corrected assignment selects exactly one of the three
incident variables.

Frozen count:

```text
5 partitions : repaired by none
8 partitions : repaired by all three
6 partitions : repaired by {h2,h1}
6 partitions : repaired by {h1,h1+h2}
6 partitions : repaired by {h2,h1+h2}
```

The five unrepaired partitions are exactly the coarsenings of the three
opposite pairs

```text
{X_A,Q_BC}
{X_B,Q_AC}
{X_C,Q_AB}.
```

Equivalently, regard those three pairs as indivisible atoms and partition the
three atoms among three incident variables; modulo permutation of variables
there are exactly Bell(3)=5 possibilities.

Thus a locally rigid defect has no arbitrary form.

## Global consequence

Suppose no rigid opposite-pair defect occurs.

Every remaining proper repair signature is one of the three 2-subsets of the
three nonzero corrections.

Any two distinct such signatures intersect in one correction.

All three different signature types have empty common intersection.

Therefore:

```text
boxed:
Without a rigid defect, all four canonical state8 parity candidates can fail
globally only if defect checks of all three pair-conflict signature types are
present.
```

This is the E96 universal residual frontier.

## Next killer

```text
E97 GEOMETRIC DEFECT-SIGNATURE KILLER

Either:
  * show a rigid opposite-pair coarsening forces a repeated variable pair,
    a removable common block, or another raw boundary state; and
  * show the three distinct pair-conflict signatures cannot coexist in one
    C4-free cubic source;

or construct the first genuine exact TARGET6 delta parent.
```

Scientific status:

```text
E96 = UNIVERSAL FINITE KERNEL-SIGNATURE FIREWALL.
GLOBAL_TARGET6_PARENT = OPEN.
P_VS_NP = OPEN.
```
