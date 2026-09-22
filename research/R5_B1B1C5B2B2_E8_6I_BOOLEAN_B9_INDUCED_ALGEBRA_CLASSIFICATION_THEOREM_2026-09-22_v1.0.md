# R5 E8 6I — Boolean B9 induced-algebra family classification

Date: 2026-09-22

Authority: `EXACT_FIXED-FAMILY_CLASSIFICATION__NO_GENERAL_BOOLEAN-ALGEBRA_LOWER-BOUND__NO_D1_PROMOTION`

Parent gate:

`R5_E8_6I_INDUCED_ALGEBRA_COVERAGE_DISCOVERY_BRIDGE_GATE_V1`

## 1. Purpose

The first B4 control only tested the four canonical ternary Schaefer operations

```text
AND3
OR3
MAJ3
XOR3
```

and showed that source-native induced-algebra coverage already fails.

That control was intentionally narrow.

This result expands the exact finite universe to include the two trivial Schaefer tractability controls and **all** ternary Boolean Mal'tsev operations.

## 2. Frozen B9 library

```text
B9 =
{
  C0,
  C1,
  AND3,
  OR3,
  MAJ3,
  MALTSEV_0,
  MALTSEV_1,
  MALTSEV_2,
  MALTSEV_3
}
```

where:

- `C0` and `C1` are the constant ternary operations;
- `AND3(x,y,z)=x∧y∧z`;
- `OR3(x,y,z)=x∨y∨z`;
- `MAJ3` is Boolean majority;
- `MALTSEV_0..3` are exactly all four Boolean ternary operations satisfying

```text
m(x,y,y)=x
m(y,y,x)=x.
```

Each member is a source-native tractability control:

- constants correspond to 0-valid / 1-valid trivial satisfiability;
- semilattice operations are standard Horn / dual-Horn algebraic controls;
- majority is the bijunctive control;
- every Mal'tsev algebra admits the polynomial Bulatov–Dalmau style algebraic route.

The point of the classification is not to claim B9 exhausts every tractable algebraic presentation of Boolean CSP.

It asks a narrower exact question:

> Can arbitrary signed 3-SAT already be universally covered by Takhanov's variable-specific induced-algebra mechanism when the variable labels are allowed to range over this enlarged canonical tractable ternary family?

## 3. Exact checker

Checker:

`research/tools/r5_e8_6i_boolean_b9_family_classifier.py`

Frozen receipt:

`research/R5_B1B1C5B2B2_E8_6I_BOOLEAN_B9_INDUCED_ALGEBRA_FAMILY_CLASSIFICATION_2026-09-22_v1.0.json`

The checker performs only finite definitional enumeration.

For every signed 3-clause relation `rho`:

1. every candidate algebra-label triple from B9³ is checked directly;
2. preservation is tested on all `7³=343` triples of rows of `rho`;
3. the induced relation `rho^B9` is frozen exactly.

Each of the eight induced signed-clause relations contains exactly:

```text
239
```

B9-label triples.

The checker then enumerates **all** nonempty subfamilies

```text
∅ ≠ B ⊆ B9.
```

Count:

```text
2^9 - 1
=
511.
```

## 4. Coverage classification

For each B the source-native Takhanov coverage map is tested:

```text
Gamma_3SAT
->
Gamma_3SAT^B.
```

A homomorphism consists of a pair of algebra labels

```text
h(0), h(1) in B.
```

Exact result:

```text
COVERAGE
iff
{C0,C1} subseteq B.
```

Therefore:

```text
COVERING SUBFAMILIES
=
128

NONCOVERING SUBFAMILIES
=
383.
```

For every covering B, the only coverage homomorphism is

```text
0 -> C0
1 -> C1.
```

So the nonconstant algebraic labels never supply the universal entry map.

## 5. Retraction theorem for every covering family

For every covering B, the induced template admits a homomorphism

```text
r:
Gamma_3SAT^B
->
Gamma_3SAT
```

with

```text
r(C0)=0
r(C1)=1.
```

Together with the coverage embedding

```text
e:
Gamma_3SAT
->
Gamma_3SAT^B
```

we have

```text
r o e
=
id.
```

Thus:

```text
Gamma_3SAT
is a retract of
Gamma_3SAT^B.
```

For the full B9 family there are exactly:

```text
32
```

retractions.

All of them force

```text
AND3 -> 0
OR3  -> 1,
```

while the five labels

```text
MAJ3
MALTSEV_0
MALTSEV_1
MALTSEV_2
MALTSEV_3
```

may be mapped arbitrarily to 0 or 1.

Hence for every covering B and every instance R:

```text
R -> Gamma_3SAT
iff
R -> Gamma_3SAT^B.
```

The induced prototype problem retains the original satisfiability problem exactly.

## 6. Classification verdict

The whole frozen B9 subfamily universe falls into exactly two classes:

```text
CASE A
C0,C1 not both present
=>
UNIVERSAL COVERAGE FAILS

CASE B
C0,C1 both present
=>
Gamma_3SAT is a retract of Gamma_3SAT^B
=>
ZERO COMPLEXITY PROGRESS
```

Therefore:

```text
BOOLEAN_B9_INDUCED_ALGEBRA_ROUTE
=
EXACTLY_CLASSIFIED

D1 HIT
=
NO
```

## 7. What this teaches us

The result is stronger than the earlier B4 and B_const controls.

It says that simply enlarging the variable-specific algebra menu by:

- Horn semilattice behavior,
- dual-Horn semilattice behavior,
- majority behavior,
- every Boolean Mal'tsev behavior,
- and the two trivial constant behaviors

does not create the missing bridge.

The decisive obstruction is now visible:

```text
UNIVERSAL COVERAGE
requires the value-coding constants,

and once they are present,
the original 3-SAT template survives as a retract.
```

So the next 6I step should **not** add more labels of the same canonical Boolean-one-operation kind without a theorem explaining why the retract disappears.

## 8. Relation to old mechanisms

This result also places several old mechanisms correctly.

### Boolean domain permutation / renaming

Boolean variable flips can enlarge recognizable tractable subclasses such as renamable Horn/max-closed instances, but they do not change the universal B9 classification.

### Conservative coloured-graph methods

On the literal Boolean domain there is only one unordered value pair `{0,1}`.  The rich pair-colour interaction used by conservative CSP algorithms becomes genuinely richer only after a larger/lifted domain is introduced.

### Semilattice-block Mal'tsev

On a two-element domain the coarse-block/fine-Mal'tsev hybrid has too little room to realize the multi-block mechanism that makes the general algorithm interesting.

This points to the next source-bound object:

```text
POLYNOMIAL LIFT
TO A LARGER FINITE / INSTANCE-SORTED DOMAIN

+
TRACTABLE COARSE CERTIFICATE

+
MAL'TSEV / FEW-SUBPOWERS RESIDUAL
```

not another renaming of the same Boolean B9 menu.

## 9. Scope ceiling

This result does **not** prove:

- that every tractable Boolean algebra of arbitrary signature is covered by B9;
- that induced-algebra methods in general fail;
- that lifted-domain or multi-sorted algebras fail;
- any lower bound for SAT;
- P≠NP.

It only closes the exact frozen B9 family.

## Current state

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

6I
=
OPEN

BOOLEAN B9 FIXED-FAMILY BRANCH
=
CLOSED / ZERO D1 PROGRESS

NEXT
=
SOURCE-BOUND LIFTED-DOMAIN
COARSE+RESIDUAL SYNTHESIS
```
