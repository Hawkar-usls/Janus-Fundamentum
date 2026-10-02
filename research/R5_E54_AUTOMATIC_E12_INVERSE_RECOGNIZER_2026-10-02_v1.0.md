# R5 E54 — Automatic E12 Inverse-Reduction Recognizer

Date: 2026-10-02

Status:
`EXACT_RAW_INCIDENCE_RECOGNITION__D7_ANCHOR_RECOVERY__AUTOMATIC_17Q_TO_2Q_BOUNDARY_QUOTIENT__FULL_RANK_QUOTIENT_TERMINAL`

Scientific ceiling:

```text
R5 E53 SHOWS THAT IF THE 17-COLUMN E12 GADGET PARTITION IS KNOWN, COMPLETE
LOCAL BOOLEAN ELIMINATION RECOVERS TWO INDEPENDENT COPIES OF THE ORIGINAL
RXC3 SOURCE SYSTEM.

E54 REMOVES THE NEED TO SUPPLY THAT GADGET PARTITION.

ON EVERY EXACT E12-REDUCTION TARGET, THE RAW INCIDENCE STRUCTURE ITSELF
CANONICALLY EXPOSES ONE D7 ANCHOR PER GADGET THROUGH THE CORRECT
VARIABLE-CONFLICT CLAW COUNT c(v)=8. FROM EACH ANCHOR THE WHOLE 17-COLUMN
GADGET, ITS 15 INTERNAL ROWS, ITS SIX BOUNDARY ROWS, AND ITS TWO BOUNDARY
TRIPLES ARE RECOVERED BY POLYNOMIAL INCIDENCE TRAVERSAL.

THE RESULTING 2q-BIT BOUNDARY QUOTIENT IS EXACTLY R⊕R UP TO ROW/COLUMN
PERMUTATIONS, WHERE R IS THE ORIGINAL q×q RXC3 INCIDENCE MATRIX.

THUS E12-SHAPED TARGETS CAN BE RECOGNIZED AND INVERTED AUTOMATICALLY.
THIS DOES NOT SOLVE ARBITRARY SINGULAR RXC3 QUOTIENTS.
P_VS_NP = OPEN.
```

## 1. Setting

Let `B` be an unlabeled square+cubic+linear Exact-One target that is promised to
have been produced by the exact R5 E12 reduction from some RXC3 source with `q`
source triples.

Thus

```text
B has 17q rows and 17q columns.
```

The input to the recognizer is only the raw incidence relation of `B`.

The algorithm is not given:

```text
the source matrix R,
the gadget partition,
the names L_i,P_i,D_i,
the internal/boundary row partition,
or the correspondence to source elements.
```

It reconstructs these structural objects from incidence alone.

## 2. Correct conflict orientation

As corrected in R5 E50, the conflict graph used by R5 E45--E49 has one vertex per
Exact-One variable-column of `B`.

Two columns are adjacent iff they share a row.

Because `B` is square+cubic+linear, every conflict vertex has degree six.
For each conflict vertex `v`, compute

```text
c(v)=#{ independent 3-subsets of N(v) }.
```

Since `deg(v)=6`, this needs at most `binom(6,3)=20` local tests per vertex.

R5 E50 proves the exact E12 pattern:

```text
c=2 : L4,L5,P4,P5,
c=4 : L1,L2,L3,P1,P2,P3,D1,...,D6,
c=8 : D7 only.
```

Therefore:

```text
boxed:
The c(v)=8 columns are exactly the D7 anchors, one per gadget.
```

So the raw target exposes the number of source gadgets immediately:

```text
q=#{v:c(v)=8}.
```

## 3. Recover the three t-rows from one anchor

Fix one anchor column `a` with `c(a)=8`.

A target column has degree three, so `a` is incident with exactly three target rows.
In the E12 gadget these are precisely

```text
t1,t2,t3.
```

Call the recovered row set

```text
T(a).
```

Thus

```text
|T(a)|=3.
```

No labels are needed; this is simply the incidence neighborhood of the anchor on the
row side of the Levi graph.

## 4. Recover D1,...,D6

Every recovered t-row has column degree three and contains:

```text
the anchor D7,
plus exactly two columns among D1,...,D6.
```

Remove the anchor from the three row neighborhoods and take their union.
The result is exactly six columns:

```text
D(a)={D1,...,D6}.
```

Hence

```text
|D(a)|=6.
```

This step uses only local degree-three incidence.

## 5. Recover the twelve z/Z internal rows

Each column in `D(a)` contains exactly one recovered t-row and two additional rows.
Those additional rows are the internal

```text
z1,...,z6,Z1,...,Z6.
```

Take the union of these non-t rows over the six D-columns. Linearity and the fixed
E12 gadget pattern give exactly twelve distinct rows:

```text
Z(a).
```

Thus

```text
|Z(a)|=12.
```

Together,

```text
I(a)=T(a) union Z(a)
```

is the full set of fifteen gadget-internal rows.

## 6. Recover the ten L/P columns

Every row in `Z(a)` has column degree three.

One of those incident columns is already one of the recovered D-columns. The other
two are among

```text
L1,...,L5,P1,...,P5.
```

Take the union of those non-D incident columns over all twelve z/Z rows. The fixed
local incidence gives exactly ten distinct columns:

```text
L(a).
```

Thus

```text
|L(a)|=10.
```

The complete recovered gadget-column set is

```text
G(a)={a} union D(a) union L(a),
```

with

```text
|G(a)|=1+6+10=17.
```

## 7. Recover the six boundary rows

Each recovered L/P column contains either:

```text
three internal z/Z rows,
```

or

```text
two internal z/Z rows plus one global boundary row.
```

Subtract the fifteen recovered internal rows `I(a)` from the row supports of all ten
L/P columns. The union of the remaining rows is exactly the six boundary ports:

```text
B(a)={x1,x2,x3,x'1,x'2,x'3}.
```

Hence

```text
|B(a)|=6.
```

These boundary rows may also occur in other recovered gadgets; that is exactly how
the original RXC3 source is globally wired.

## 8. Split the gadget into unprimed and primed sides without labels

It remains to partition the six boundary rows into the two source triples.

Build an auxiliary graph on the twelve recovered z/Z rows `Z(a)`:
connect two internal rows when they occur together in one recovered L/P column.

Inside an E12 gadget there are no L/P columns mixing primed and unprimed z-families.
Therefore this auxiliary graph has exactly two connected components, each of size
six.

Call them

```text
Z_0(a), Z_1(a).
```

For each component, collect the recovered L/P columns touching it and then collect
their boundary rows outside `I(a)`.
Each side exposes exactly three boundary rows:

```text
C_0(a), C_1(a),
|C_0(a)|=|C_1(a)|=3,
C_0(a) cap C_1(a)=empty,
C_0(a) union C_1(a)=B(a).
```

The recognizer need not decide which side is called unprimed; swapping the two sides
has no effect on the final quotient.

## 9. Recover all gadgets

Run Sections 3--8 independently from every c=8 anchor.

For an exact E12 target, the recovered 17-column gadget sets are pairwise disjoint
and cover every target column:

```text
boxed:
union_a G(a)=all 17q columns.
```

Likewise the recovered internal row sets are pairwise disjoint and contain exactly

```text
15q
```

rows.

The remaining

```text
17q-15q=2q
```

rows are exactly the global boundary rows corresponding to the q original source
elements and their primed copies.

These cardinality/disjointness conditions are part of the recognizer's validation;
if they fail, the input is not certified as an exact E12-shaped target by this
branch.

## 10. Construct the automatic Boolean boundary quotient

For every recovered gadget `a`, introduce one Boolean quotient column for each of
its two recovered boundary triples

```text
C_0(a), C_1(a).
```

The quotient row set is the recovered set of `2q` global boundary rows.

Put a one in quotient row `r` and quotient column `(a,s)` iff

```text
r in C_s(a).
```

This constructs a raw quotient matrix

```text
Q_B in {0,1}^{2q x 2q}
```

directly from the unlabeled target.

By R5 E53, choosing quotient bit `(a,s)=1` means the corresponding local gadget side
covers all three boundary rows of `C_s(a)`, while bit zero means it covers none.
All four two-side choices are locally realizable.

Therefore the target is SAT iff

```text
Q_B y=1,
y in {0,1}^{2q}.
```

## 11. Why Q_B is R direct-sum R

For an exact E12 reduction target, each recovered side triple is one original source
triple on either the unprimed or primed boundary copy.

Boundary rows from the two copies never mix in one recovered side.
Thus, after a row permutation and a column permutation,

```text
boxed:
Q_B = R direct-sum R,
```

where `R` is the q×q incidence matrix of the original RXC3 source.

The automatic recognizer does not need to know the permutations or even explicitly
identify the two global copies to obtain an exact decision-equivalent quotient.

## 12. Decision equivalence

R5 E53 proves local completeness of the four side-bit states. Combining that theorem
with the automatic structural recovery gives:

### Theorem AUTO-E12-INVERSE

```text
boxed:
For every target produced by the exact R5 E12 reduction, the raw target incidence
matrix can be recognized/inverted in polynomial time to a 2q×2q Boolean quotient
Q_B permutation-equivalent to R direct-sum R, and

  target SAT iff exists y in {0,1}^{2q}: Q_B y=1.
```

Since the two source copies are identical, the quotient may subsequently be reduced
to either q×q connected/source copy once that copy separation is exposed, but the
2q×2q quotient itself is already exact and requires no such labeling.

## 13. Complexity

All local incidence degrees are constant.

The only potentially nonconstant primitive used by the recognizer is computing
conflict adjacency among columns; this is polynomial by direct incidence indexing.
Once the graph is built:

```text
claw counts: at most 20 triples per column;
anchor traversals: constant radius in the Levi graph;
component split inside one gadget: 12 vertices;
quotient construction: linear in recovered boundary incidences.
```

Hence the complete inverse recognizer and quotient construction run in polynomial
time, and in a sparse implementation essentially linear time after incidence
indexing.

## 14. Frozen q=6 replay

The companion checker starts only from the raw 102-row / 102-column E12 target
fixture and performs the reconstruction above.

It obtains:

```text
c=8 anchors                  = 6,
reconstructed gadgets        = 6,
columns per gadget           = 17,
internal rows per gadget     = 15,
boundary rows total          = 12,
automatic quotient dimension = 12 x 12.
```

The quotient satisfies

```text
row sum = column sum = 3,
rank_Q(Q_B)=12,
|det(Q_B)|=81=(-9)^2.
```

Because every row sum is three,

```text
Q_B * ((1/3)1)=1.
```

Full rank makes this the unique rational solution. It is not Boolean, so the raw
102-variable target is certified UNSAT.

No supplied gadget partition is used in the reconstruction.

## 15. New polynomial terminal for recognized full-rank quotients

Whenever AUTO-E12-INVERSE succeeds and the recovered quotient `Q_B` is rationally
full rank, its unique solution is

```text
(1/3)1
```

because the quotient is cubic.

Therefore:

```text
boxed:
recognized E12-shaped target + full-rank automatic boundary quotient -> UNSAT
```

in polynomial time.

More generally, small quotient nullity can be passed directly to the existing R5
small-nullity exact solver.

## 16. Scientific limit

E54 is an inverse-reduction recognizer, not a universal solver.

For arbitrary E12-shaped targets with singular recovered source quotient, the
quotient remains precisely an RXC3 Exact-Cover instance:

```text
R a=1,
a in {0,1}^q.
```

That source problem is NP-complete in general. Automatic recognition removes the
17× gadget overhead but does not make the singular global quotient polynomial.

So:

```text
P_VS_NP = OPEN.
```

## 17. Router update

Add the specialized inverse branch:

```text
INV0  build variable-column conflict graph;
INV1  compute local claw counts c(v);
INV2  candidate E12 anchors = {v:c(v)=8};
INV3  traverse each anchor and verify the 17-column / 15-internal-row module shape;
INV4  split its 12 z/Z rows into two six-row sides;
INV5  recover two boundary triples per gadget;
INV6  verify gadget column partition and boundary/internal row counts globally;
INV7  build the 2q×2q Boolean boundary quotient Q_B;
INV8  full rank -> UNSAT;
INV9  small nullity / known quotient language -> route to existing terminal;
INV10 otherwise expose the singular source quotient as the new global frontier.
```

## 18. Updated frontier

R5 E17, E53 and E54 together close the internal E12 gadget layer at three levels:

```text
rational kernel quotient,
exact Boolean boundary quotient,
automatic structural recognition from raw incidence.
```

Therefore further universal progress must operate on the recovered **global source
quotient**, not on local gadget internals.

The high-value post-E54 target is now explicit:

```text
SINGULAR GLOBAL RXC3 SOURCE QUOTIENT

R in {0,1}^{q x q},
row sum = column sum = 3,
R a = 1,
a in {0,1}^q,
large effective nullity / no existing global terminal.
```

This is the layer that must be cracked for a universal polynomial result.

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e54_automatic_e12_inverse_recognizer.py
```
