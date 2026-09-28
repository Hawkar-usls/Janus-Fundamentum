# R5 E9 — RKPR Post-Quotient Reconciliation and EQ3 Source Return

Date: 2026-09-28

Status: `JANUS_DERIVED_ROUTE_RECONCILIATION__PRIME_TOWER_EXTINCT_AFTER_RKPR__EQ3_REGULARIZER_QUOTIENT_RETURNS_SOURCE__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_RATIONAL_KERNEL_PROJECTIVE_RATIO_PINNING_QUOTIENT_2026-09-28_v1.0.md`
- `research/R5_E9_PRIME_TOWER_PROJECTIVE_ESCAPE_RADIUS_RECURRENCE_2026-09-28_v1.0.md`
- `research/R5_E9_EQ3_MID_NULLITY_HARDNESS_SLAB_2026-09-28_v1.0.md`
- `research/R5_E9_LINEAR_CUBIC_EQ3_REGULARIZATION_UNIVERSALITY_2026-09-27_v1.0.md`

Checker:
- `experiments/r5_e9_rkpr_postquotient_reconciliation.py`

Scientific ceiling:

```text
THE LINEAR PROJECTIVE ESCAPE-RADIUS PRIME TOWER REMAINS A VALID THEOREM
ABOUT THE PRE-RKPR RATIONAL-KERNEL ARRANGEMENT, BUT IT IS NOT A VALID
HOSTILE FAMILY FOR THE POST-RKPR LIVE RESIDUAL: THE FIRST n=30 MEMBER IS
KILLED IMMEDIATELY BY AN ILLEGAL PROJECTIVE RATIO 4.

CONVERSELY RKPR DOES NOT MAGICALLY SOLVE THE EQ3 NP-HARDNESS IMAGE.
ON THE FROZEN 10-VARIABLE EQ3 REGULARIZER, THE GUARANTEED RKPR EQUALITY
QUOTIENT COLLAPSES EACH GADGET TO ONE SOURCE VARIABLE q_i PLUS A PRIVATE
EXACT-ONE SLACK PAIR.  ALL CROSS-GADGET PROJECTIVE RELATIONS AMONG q_i ARE
EXACTLY THE PROJECTIVE RELATIONS ALREADY PRESENT IN THE SOURCE KERNEL.

THUS EQ3-REGULARIZE THEN RKPR IS, UP TO PRIVATE SLACK VARIABLES, THE SAME
SEMANTIC CORE AS APPLYING RKPR TO THE ORIGINAL SOURCE.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Why this reconciliation is necessary

The projective escape-radius recurrence proved an explicit connected cubic
UNSAT family with a chamber whose geometric escape radius is linear in `n`.
After that theorem, RKPR introduced a strictly earlier polynomial preprocessor:
proportional rational-kernel rows may have SAT-compatible ratios only

```text
{1,-2,-1/2}.
```

Any other ratio is an exact UNSAT certificate.

Therefore every navigation barrier must now be classified as either

```text
PRE-RKPR only
```

or

```text
SURVIVES RKPR and is still a live hostile control.
```

## 2. Prime-tower extinction at the first lifted stage

Use the frozen `n=15` prime-tower seed kernel vectors

```text
g=(1,4,1,1,-2,-2,1,-2,-2,-2,-2,1,1,1,1),

z=(-7,-4,3,1,-2,2,-1,-4,6,8,2,-3,-5,1,5).
```

The first `n=30` lift has exact two-dimensional right kernel basis

```text
W_1=(sym(g), asym(z)).
```

Hence its coordinate functionals are the rows

```text
b_i=(sym(g)_i, asym(z)_i).
```

Look at 0-based coordinates `3` and `16` (1-based coordinates `4` and `17`):

```text
b_3  = (1,1),
b_16 = (4,4) = 4 b_3.
```

RKPR allows only ratios `1,-2,-1/2` on a SAT-compatible projective class.
Therefore

```text
ratio(b_16,b_3)=4
```

is an exact immediate UNSAT certificate.

### Theorem RPER-1

The `n=30` member, and hence every recursive descendant for which this member
is an ancestor in the frozen prime-tower route, is removed before the
post-RKPR navigation gate.

Consequently the theorem

```text
escape radius = (2/15)n+1
```

remains mathematically correct on that preprocessed-away family, but it must
not be cited as proving a linear-radius barrier for the **post-RKPR survivor**.

This is a route-scope correction, not a retraction of the escape-radius proof.

## 3. Frozen EQ3 gadget kernel coordinates

The EQ3 regularizer uses one 10-variable / 9-clause gadget per source variable,
with local clauses

```text
(2,5,6)
(1,4,7)
(5,7,9)
(0,3,7)
(4,6,9)
(2,4,8)
(3,8,9)
(0,5,8)
(1,3,6).
```

The parent exact rank computation gives the homogeneous local parametrization

```text
coordinates 0,1,2,9 = q_i,
coordinates 6,7,8   = r_i,
coordinates 3,4,5   = -q_i-r_i.
```

After all `m` gadgets are assembled and the retained source clauses are added,
the full rational kernel is parametrized by

```text
q in ker_Q(M),
r in Q^m arbitrary,
```

where `M` is the original source incidence matrix.  Write the three functional
types for gadget `i` as

```text
Q_i(q,r)= q_i,
R_i(q,r)= r_i,
S_i(q,r)= -q_i-r_i.
```

Their guaranteed multiplicities are

```text
Q_i : 4 coordinates,
R_i : 3 coordinates,
S_i : 3 coordinates.
```

## 4. Guaranteed RKPR classes inside every gadget

Within one gadget all four `Q_i` rows are exactly equal rational kernel rows,
all three `R_i` rows are equal, and all three `S_i` rows are equal.  Thus RKPR
merges at least the classes

```text
Q_i^4,
R_i^3,
S_i^3
```

by ratio `1`.

No Boolean information is lost: these are exact equality relations on every
kernel vector and hence on every Exact-One witness.

After these merges, each of the nine local gadget clauses becomes the same
single quotient clause

```text
Q_i + R_i + S_i = 1
```

over Boolean quotient variables.

So nine local constraints collapse to one duplicate-free Exact-One row.

## 5. Cross-gadget proportionality theorem

Assume the source zero-kernel-row terminal has failed, i.e. every source
coordinate functional `q_i` is nonzero on `ker_Q(M)`.

Because every `r_i` is an independent free coordinate in the full regularized
kernel:

- `R_i` is not proportional to `R_j` for `i!=j`;
- no `R_i` is proportional to any `Q_j`;
- no `R_i` is proportional to any `S_j`;
- `S_i` is not proportional to `S_j` for `i!=j`, since they carry different
  independent `r_i,r_j` coefficients;
- no `S_i` is proportional to any `Q_j`, because `S_i` has a nonzero `r_i`
  coefficient while every `Q_j` has none.

The only possible proportionality across distinct gadgets is therefore

```text
Q_i = lambda Q_j.
```

But this holds exactly when the original source rational-kernel coordinate
functionals satisfy

```text
q_i = lambda q_j
```

on `ker_Q(M)`, with the **same scalar ratio** `lambda`.

### Theorem RPER-2 — projective commutation

All nontrivial cross-gadget RKPR information of the EQ3-regularized instance is
precisely the RKPR information already present among source kernel coordinates.
No new hidden cross-gadget projective relation is created by the regularizer.

If a source `Q_i` is identically zero, the regularized instance exposes the
same zero-row UNSAT terminal on its terminal coordinates; this is again source
information, not a new gadget effect.

## 6. Quotient returns the source plus private slack

The retained source clauses touch one terminal `Q_i` from each of three source
gadgets. After the guaranteed equality merges they remain exactly

```text
Q_i + Q_j + Q_k = 1
```

for every original source row `{i,j,k}`.

The only remaining local clause of gadget `i` is

```text
Q_i + R_i + S_i = 1.
```

Both `R_i` and `S_i` are private to this one quotient row.

For either Boolean value of `Q_i`, this local row is extendable:

```text
Q_i=1 -> (R_i,S_i)=(0,0),
Q_i=0 -> (R_i,S_i) in {(1,0),(0,1)}.
```

Therefore existentially projecting all private slack pairs gives exactly the
original source system

```text
M Q = 1,
Q in {0,1}^m.
```

### Theorem RPER-3 — source-return identity

Modulo duplicate rows and private slack pairs,

```text
RKPR(EQ3_REGULARIZE(Phi))
```

has the same Boolean decision core as

```text
RKPR(Phi).
```

More explicitly, the regularizer's guaranteed quotient is

```text
SOURCE_EXACT_ONE(Q)
AND
for every i EXACT_ONE(Q_i,R_i,S_i),
```

with private `R_i,S_i`, after which any further RKPR merge/pin among the `Q_i`
coordinates is exactly a source RKPR merge/pin.

Witness reconstruction is linear time once the source `Q` witness is known.

## 7. Consequence for the hardness slab

The EQ3 middle-nullity theorem remains useful as a **pre-RKPR** exact
NP-complete image and as a nullity-router barrier.  But after RKPR its equality
gadget shell is stripped away and returns the underlying source core.

Hence neither of the following is admissible:

```text
PRIME-TOWER LINEAR ESCAPE RADIUS
=> post-RKPR navigation is linearly trapped.
```

The prime tower is already extinct.

Nor:

```text
RKPR COLLAPSES THE EQ3 GADGETS
=> RKPR SOLVES THE NP-COMPLETE EQ3 IMAGE.
```

The collapse returns the original source problem rather than solving it.

This is exactly the desired anti-loop behavior: representation overhead is
removed, while the semantic source core remains visible.

## 8. Sharpened live carrier

The live gate is now explicitly **post-RKPR**:

```text
R5_E9_POST_RKPR_SOURCE_KERNEL_BOUNDARY_DIRECTION_GATE_V1
```

Input must satisfy:

```text
no zero rational kernel row,
no illegal projective ratio,
all -2/-1/2 pin consequences propagated,
every surviving nontrivial projective class is an equality class,
duplicate quotient rows removed,
ordinary Exact-One propagation exhausted.
```

A valid navigation/barrier theorem must be proved on this carrier.  Pre-RKPR
hostile families may still be useful diagnostics, but they do not close this
new gate.

Mandatory positive control:
- PG15 after its four equality merges; it still contains the nonmonotone
  boundary-navigation phenomenon.

Mandatory negative controls:
- source instances surviving RKPR without an immediate contradiction;
- any future arbitrary-size radius/barrier family must itself pass RKPR.

## 9. Ceiling

```text
PRIME-TOWER n=30 PROJECTIVE RATIO
b_16 / b_3 = 4
=> RKPR UNSAT TERMINAL

PRIME-TOWER LINEAR ESCAPE FAMILY
= VALID PRE-RKPR THEOREM
= NOT A POST-RKPR HOSTILE FAMILY

EQ3 GADGET GUARANTEED RKPR CLASSES
= Q_i^4, R_i^3, S_i^3

9 LOCAL GADGET ROWS AFTER QUOTIENT
= ONE ROW EXACT_ONE(Q_i,R_i,S_i)

CROSS-GADGET PROJECTIVE INFORMATION
= EXACTLY SOURCE Q-KERNEL PROJECTIVE INFORMATION

EXISTENTIAL PROJECTION OF PRIVATE R_i,S_i
= ORIGINAL SOURCE EXACT-ONE INSTANCE

RKPR(EQ3_REGULARIZE(Phi))
= RKPR(Phi) + PRIVATE EXTENDABLE SLACK
  (up to the stated source-level merges/pins)

POST-RKPR BOUNDARY-DIRECTION ORACLE
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```