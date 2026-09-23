# R5 E8 6I — Direct Delta-Matroid Occurrence-Split Barrier

Date: 2026-09-23

Authority: `PROVED_MODEL_BINDING_BARRIER__NO_D1_PROMOTION`

Parent gate:

`R5_E8_6I_REPRESENTATION_CHANGE_BEFORE_RELAXATION_GATE_V1`

## 1. Source tractability donor

Kazda--Kolmogorov--Rolinek,
*Even Delta-Matroids and the Complexity of Planar Boolean CSPs*
(arXiv:1602.03124 / TALG 2018), give a polynomial algorithm for Boolean
edge-CSP instances in which every variable occurs in exactly two constraints
and every constraint is an even delta-matroid relation (with an extension to
efficiently coverable delta-matroids).

Feder--Ford and Dalmau--Ford likewise connect two-occurrence Boolean CSPs
to delta-matroid intersection/parity.

Therefore a natural JANUS attempt is:

```text
split every SAT variable into occurrence variables
+
enforce global equality of its occurrences
+
treat occurrence variables as edges
+
solve by delta-matroid / matching machinery.
```

This artifact checks that direct binding.

## 2. Local sheet-choice relation

The frozen three-sheet flip patterns are

```text
S_sheet
=
{000,010,001}.
```

As a feasible-set system on three coordinates:

```text
F_sheet
=
{ empty, {2}, {3} }.
```

### Delta-matroid property

The symmetric-exchange axiom holds.

Any two distinct feasible sets differ by one or two elements, and for any
chosen element of the symmetric difference one may choose an exchange
element returning either the empty feasible set or the other singleton.

Thus:

```text
S_sheet
=
DELTA_MATROID.
```

### Evenness

It is not an even delta-matroid, since it contains feasible sets of
cardinality 0 and 1.

Twisting by any fixed set T does not repair parity: modulo 2,

```text
|F Delta T|
=
|F| + |T|  (mod 2),
```

so the parity difference between the empty feasible set and singleton
feasible sets is invariant under twisting.

Hence:

```text
S_sheet
=
NOT EVEN DELTA_MATROID
AND NOT TWIST-EVEN.
```

This already places the raw local sheet relation outside the basic
even-delta-matroid edge-CSP theorem.

It does not by itself exclude the larger efficiently-coverable classes.

## 3. Global variable-coherence relation

After occurrence splitting, a SAT variable with d occurrences requires

```text
EQ_d
=
{0^d,1^d}.
```

As a feasible-set system:

```text
F_EQ_d
=
{ empty, [d] }.
```

For every d >= 3 this is not a delta-matroid.

### Proof

Take

```text
X = empty
Y = [d].
```

Choose any

```text
e in X Delta Y = [d].
```

The symmetric-exchange axiom would require some

```text
f in [d]
```

such that

```text
X Delta {e,f}
```

is feasible.

If f=e, this is the singleton {e}.
If f!=e, this is a two-element set {e,f}.

For d>=3 neither is empty nor [d].

Therefore no allowed f exists and the exchange axiom fails.

Thus:

```text
EQ_d
IS NOT A DELTA_MATROID
FOR d>=3.
```

## 4. Consequence for the direct occurrence-split model

The most direct transformation

```text
SAT variable
->
one occurrence variable per clause
+
one ALL_EQUAL constraint per original variable
```

does produce the desired two-incidence shape for each occurrence variable:

```text
occurrence
belongs to
one clause constraint
+
one variable-coherence constraint.
```

However the variable-coherence vertex carries `EQ_d`, which is not a
delta-matroid as soon as the original variable has at least three occurrences.

Therefore:

```text
DIRECT OCCURRENCE-SPLIT
EDGE-CSP
DOES NOT FIT
THE DELTA-MATROID TRACTABILITY HYPOTHESES.
```

This is a source/model-binding blocker, not a hardness theorem for every
possible delta-matroid representation.

## 5. Why binary-equality replacement is not a free repair

Replacing `EQ_d` by a chain/tree/cycle of binary equality constraints does
not automatically give the same edge-CSP form.

An occurrence variable already participates in its clause constraint.
Attaching enough binary equalities to propagate one global value generally
raises variable occurrence degree above two, or introduces a further copying
gadget whose own exact two-occurrence / delta-matroid contract must be proved.

Therefore the repair is itself a new representation theorem, not an
application of the known edge-CSP algorithm.

## 6. Exact surviving delta-matroid question

Only a genuine representation change remains admissible:

```text
Does there exist a polynomial-size exact gadgetization
of the three-sheet + variable-coherence system
into a two-occurrence edge-CSP
whose constraints belong to a source-proved
tractable delta-matroid class,
with polynomial reconstruction and no hidden selector?
```

No such theorem is claimed here.

## 7. Ceiling

```text
RAW SHEET RELATION
=
DELTA_MATROID BUT NOT EVEN

DIRECT HIGH-ARITY VARIABLE EQUALITY
=
NOT DELTA_MATROID FOR DEGREE >= 3

DIRECT OCCURRENCE-SPLIT
MATCHING / EVEN-DELTA-MATROID ROUTE
=
BLOCKED BY MODEL BINDING

NONTRIVIAL DELTA-MATROID GADGETIZATION
=
OPEN

D1
=
EMPTY

P_VS_NP
=
OPEN
```
