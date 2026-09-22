# R5 E8 6I — Boolean Occurrence-Synchronization Conjugation Barrier

Date: 2026-09-22

Authority: `PROVED_SCOPED_THEOREM__NO_D1_PROMOTION__NO_SUCCESSOR_AUTHORIZATION`

## 1. Motivation

After direct B4/Bwnu coverage fails on NAE3, the cheapest representation-changing repair is:

1. split repeated occurrences of each Boolean variable into separate copies;
2. permit each copy to use its own Boolean orientation `id` or `not`;
3. reconnect copies by exact `EQ` or `NEQ` synchronization constraints;
4. ask whether the transformed local clause relations admit B4 algebra labels.

This is the natural occurrence-level extension of Boolean domain permutation / renaming.

The question is whether this representation change produces genuinely new B4 coverage.

It does not.

## 2. Frozen algebra family

```text
B4
=
{AND3, OR3, MAJ3, XOR3}.
```

For any ternary Boolean operation `f`, define its Boolean dual:

```text
f*(x,y,z)
=
not f(not x, not y, not z).
```

For B4:

```text
AND3* = OR3
OR3*  = AND3
MAJ3* = MAJ3
XOR3* = XOR3.
```

Thus B4 is closed under Boolean conjugation.

## 3. Synchronization lemma

Let `f,g` be ternary Boolean operations.

### Equality

```text
EQ
=
{(0,0),(1,1)}.
```

Mixed coordinate operation `(f,g)` preserves `EQ` iff for every input triple `a`:

```text
f(a)=g(a).
```

Hence:

```text
(f,g) preserves EQ
iff
f=g.
```

### Disequality

```text
NEQ
=
{(0,1),(1,0)}.
```

Mixed coordinate operation `(f,g)` preserves `NEQ` iff:

```text
g(not a)
=
not f(a)
```

for every Boolean input triple `a`.

Equivalently:

```text
g
=
f*.
```

Therefore:

```text
(f,g) preserves NEQ
iff
g=dual(f).
```

For B4 the exact allowed pairs are:

```text
EQ:
(AND,AND)
(OR,OR)
(MAJ,MAJ)
(XOR,XOR)

NEQ:
(AND,OR)
(OR,AND)
(MAJ,MAJ)
(XOR,XOR).
```

## 4. Boolean coordinate-conjugation lemma

Let `R subseteq {0,1}^k`.

For each coordinate `i`, choose a Boolean permutation

```text
pi_i in {id,not}.
```

Define the transformed relation:

```text
R'
=
{(pi_1(x_1),...,pi_k(x_k))
 :
 (x_1,...,x_k) in R}.
```

Let local operations on transformed coordinates be `g_i`.

Pull each operation back to the original coordinate:

```text
f_i
=
pi_i^{-1}
circ g_i
circ pi_i^3.
```

Since Boolean permutations are involutions:

```text
pi_i=id
=> f_i=g_i

pi_i=not
=> f_i=dual(g_i).
```

Then, directly from the definition of relation preservation:

```text
R' preserved by (g_1,...,g_k)
iff
R preserved by (f_1,...,f_k).
```

This identity is exact and does not depend on the clause language.

## 5. Occurrence-splitting theorem

Take any Boolean CSP instance `I`.

Replace every occurrence of every variable by its own copy.

For each copy choose an orientation in `{id,not}`.

For copies of the same original variable, add the exact synchronization relation:

```text
EQ
if orientations agree;

NEQ
if orientations differ.
```

Transform each local relation by the corresponding coordinate orientations.

Assume every occurrence copy receives a B4 label and every transformed constraint plus every synchronization relation must be preserved.

By the synchronization lemma, after pulling every occurrence label back through its orientation, all copies of the same original variable have one common normalized B4 operation.

By the coordinate-conjugation lemma, every transformed local relation is preserved iff the original local relation is preserved by those normalized original-variable operations.

Therefore:

```text
THE OCCURRENCE-SPLIT INSTANCE
HAS A B4 PROTOTYPE

iff

THE ORIGINAL INSTANCE
HAS A VARIABLE-WISE B4 PROTOTYPE.
```

Hence:

```text
BOOLEAN OCCURRENCE SPLITTING
+
ID/NOT DOMAIN REFORMULATION
+
EQ/NEQ SYNCHRONIZATION

DOES NOT EXPAND B4 COVERAGE.
```

This is an arbitrary-instance statement for this representation class.

## 6. Relation to known domain permutation reduction

Green and Cohen's domain permutation framework allows a separate domain permutation per variable and asks whether transformed constraints enter a tractable language.

On the Boolean domain the only permutations are:

```text
id
not.
```

The theorem above is the polymorphism-level analogue of the fact that Boolean bijective reformulation changes a tractable-language description by conjugation rather than adding semantic freedom.

The result here additionally handles per-occurrence copies connected by exact EQ/NEQ synchronization and proves that this apparent extra freedom collapses back to one normalized operation per original variable.

## 7. Exact replay control

Checker:

`research/tools/r5_e8_6i_boolean_occurrence_sync_barrier.py`

Receipt:

`research/R5_B1B1C5B2B2_E8_6I_BOOLEAN_OCCURRENCE_SYNC_BARRIER_2026-09-22_v1.0.json`

The checker verifies:

```text
all 16 B4 operation pairs on EQ/NEQ;

all 8 signed clause relations;

all 8 Boolean coordinate orientations;

all 64 B4 label triples;

4096 conjugation equivalences total.
```

For the frozen NAE3/two-clause witness it also checks:

```text
64 pairs of occurrence-orientation triples
x
64 normalized B4 label triples
=
4096 split configurations,

rescued prototypes
=
0.
```

The finite NAE replay is a control for the symbolic theorem; the theorem itself is not inferred from the finite replay.

## 8. Consequence for weak relaxation

Three cheap repairs are now closed for Boolean B4:

```text
DIRECT COVERAGE
=
FAIL

STANDARD ARC/PATH/STRONG-3 PRUNING
=
FAIL ON NAE3

BOOLEAN OCCURRENCE SPLITTING
+ ID/NOT REFORMULATION
+ EQ/NEQ SYNCHRONIZATION
=
NO COVERAGE GAIN
```

Therefore any successful B4 weak relaxation must use at least one mechanism outside this class, for example:

```text
RICHER LIFTED DOMAIN
NON-BIJECTIVE AUXILIARY RELATIONS
A GENUINELY NONLOCAL EXACT TRANSFORMATION
OR ANOTHER SOURCE-BOUND CERTIFICATE FAMILY.
```

This is a structural narrowing, not a proof that such a transformation cannot exist.

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

BOOLEAN BIJECTIVE OCCURRENCE-LIFT REPAIR
=
THEOREM_LEVEL FALSIFIED AS A B4 COVERAGE EXPANDER

GENERAL WEAK-RELAXATION COVERAGE
=
OPEN
```
