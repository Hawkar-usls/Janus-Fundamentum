# R5 E8 6I — Bijunctive Local Threshold 2→1 PP Barrier

Date: 2026-09-22

Authority: `PROVED_SCOPED_THEOREM__CURRENT_A3_SBM_FRONTIER_CONTROL__NO_D1_PROMOTION`

## 1. Current positive-control context

The sealed A3 semilattice-block-Mal'tsev lift has:

```text
decoder/prototype discovery
=
2-SAT

local admission condition
=
AT_LEAST_2(l1,l2,l3)

=
(l1 OR l2)
AND
(l1 OR l3)
AND
(l2 OR l3).
```

The universal 3-SAT target requires:

```text
OR3(l1,l2,l3)
=
AT_LEAST_1(l1,l2,l3).
```

The cheapest possible repair would be to retain a bijunctive / 2-SAT prototype language and add auxiliary prototype variables so that existential projection weakens the local threshold from two true literals to one.

This theorem rules out that entire local repair class.

## 2. Bijunctive preservation fact

Every 2-CNF relation is preserved by Boolean majority:

```text
MAJ(a,b,c)
=
1
iff
at least two of a,b,c are 1.
```

Equivalently, the bijunctive Boolean relations are exactly the relations closed under the majority polymorphism.

This is the standard Schaefer/Post algebraic characterization of the 2-SAT tractable class.

## 3. Primitive-positive closure

Take any finite conjunction of bijunctive relations over free variables `x` and auxiliary variables `z`:

```text
G(x,z)
=
R_1(...)
AND
...
AND
R_m(...).
```

Because every `R_i` is preserved by MAJ, the full solution relation:

```text
Sol(G)
```

is preserved by coordinate-wise MAJ.

Projecting away auxiliary variables preserves closure under MAJ.

Therefore every relation of the form:

```text
S(x)
=
exists z
G(x,z)
```

is again preserved by MAJ.

Hence:

```text
PP-CLOSURE(2SAT / BIJUNCTIVE)
subseteq
MAJ-PRESERVED RELATIONS.
```

For finite Boolean structures this is also the standard polymorphism / pp-definability correspondence, but only the easy preservation direction is needed here.

## 4. OR3 is not majority-preserved

Consider the three tuples:

```text
100
010
001.
```

All three belong to:

```text
OR3
=
{0,1}^3 \ {000}.
```

Their coordinate-wise majority is:

```text
MAJ(100,010,001)
=
000.
```

But:

```text
000
notin
OR3.
```

Therefore:

```text
OR3
IS NOT MAJ-PRESERVED.
```

## 5. Theorem

There is no finite bijunctive / 2-SAT gadget with any number of existential auxiliary Boolean prototype variables whose projected relation on three exposed prototype bits is exactly:

```text
OR3.
```

Equivalently:

```text
AT_LEAST_2
->
AT_LEAST_1
```

cannot be achieved by merely adding local 2-SAT certificate variables while keeping prototype discovery inside a fixed bijunctive pp-language.

## 6. Consequence for the A3 SBM route

The A3 positive control already realizes:

```text
ARBITRARY 3-CNF
-> coarse decoder 2-SAT
-> exact A3 local lifts
-> polynomial SBM solve
-> exact decode
```

on the strict at-least-two-per-clause subclass.

The present theorem says the universal-coverage defect cannot be repaired locally by:

```text
MORE 2SAT AUXILIARY DECODER BITS
+
CONJUNCTION
+
EXISTENTIAL PROJECTION.
```

Thus the next exact lift must change the prototype tractability reason.

Admissible directions include:

```text
A. a non-bijunctive but source-bound tractable prototype language;

B. a multi-sorted / lifted-domain prototype whose polynomial algorithm is
   SBM, Mal'tsev, few-subpowers, bounded-width, or another exact algebraic algorithm;

C. a nonlocal exact preprocessing theorem not expressible as a fixed local
   bijunctive gadget.
```

## 7. Relation to hidden-choice firewall

The theorem does not say that OR3 cannot be represented with auxiliary variables.

It says it cannot be represented by a **bijunctive** pp-gadget.

If the auxiliary prototype language is expanded until OR3 becomes pp-definable, its tractability must be independently proved.

Otherwise the original 3-SAT choice may simply have been moved into the prototype layer.

## 8. Exact current narrowing

```text
A3_SBM
=
FIRST COMPLETE POLY LIFT ARCHITECTURE

CURRENT GAP
=
2_OF_3 -> 1_OF_3

LOCAL BIJUNCTIVE PP REPAIR
=
THEOREM_LEVEL IMPOSSIBLE

NEXT
=
NON-BIJUNCTIVE TRACTABLE PROTOTYPE
OR NONLOCAL EXACT LIFT
```

## 9. Claim ceiling

```text
P_VS_NP
=
OPEN

D1
=
EMPTY

SUCCESSOR_ALGORITHM
=
LOCKED

A3 UNIVERSAL COVERAGE
=
OPEN

2SAT-ONLY LOCAL THRESHOLD BRIDGE
=
CLOSED
```
