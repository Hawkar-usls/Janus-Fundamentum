> **E102 correction (2026-10-06).** The 31-partition LOCAL defect classification in E96 remains valid. The former GLOBAL claim that, without a rigid defect, failure of all four canonical candidates requires all three proper-conflict signatures is superseded by E102: a kernel correction can create a new defect at a base-good check. Use `R5_E102_FULL_SIGNATURE_HOLONOMY_FIREWALL_2026-10-06_v1.0.md` for global reasoning.

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

THE 31-PARTITION STATEMENT IS LOCAL TO BASE E95 DEFECTS. THE EARLIER GLOBAL
THREE-CONFLICT NECESSITY IS SUPERSEDED BY E102'S COMPLETE 122-PARTITION AUDIT.

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

## Local intersection observation (global extrapolation superseded by E102)

Among the 31 **base E95 defects**, the three proper repair signatures are the three 2-subsets of the nonzero corrections. Any two intersect and all three have empty common intersection.

This observation remains correct locally. It is **not** a complete global criterion, because E102 shows that applying a correction can create a new defect at a check that was exact for the base E95 candidate. E102 classifies all 122 ordinary support partitions and replaces this section's former global inference with a component-wise holonomy criterion.

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
