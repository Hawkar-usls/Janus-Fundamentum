# R5 E90 — p=1,h=1,t=6 Conditioned U2,4 Witness and Delta Firewall

Date: 2026-10-06

Status:
`C4FREE_CONDITIONED_U24_REALIZABLE_AT_T6__IMMEDIATE_PARENT_NONDELTA__FINITE_SOURCE_EXPANSION_CONE_BINARY`

Scientific ceiling:

```text
E90 FALSIFIES THE CLAIM THAT C4-FREE RXC3 GEOMETRY ALONE EXCLUDES
CONDITIONED U_{2,4}.

IT DOES NOT PRODUCE A NONBINARY DELTA INTERFACE.
IT DOES NOT PROVE A UNIVERSAL BINARY-REPRESENTATION THEOREM.
IT DOES NOT REPAIR THE E81 GLOBAL-DECOMPOSITION OBSTRUCTION.
P_VS_NP = OPEN.
```

## 1. Starting point

E85 reduced every possible nonbinary exact delta interface to a conditioned
four-port U2,4 witness after pin-and-project. E86–E89 excluded the smallest
p=1,h=1 cases through t=5.

For this lane

```text
a = 3t+1 checks,
b = 3t variables,
```

and the target four-port relation on three check-side ports A,B,C and one
variable-side port x is

```text
{1,2,4,11,13,14}.
```

E89 suggested an all-t induction via shared-block savings sigma. E90 shows that
the strongest version of that induction is false.

## 2. All-t firewalls that survive

Let n=t-1 and let Q_AB,Q_AC,Q_BC be the three near-parallel classes from the
v=1 target states after removing the common degree-two variable x={r,s}. Define

```text
sigma = 3n - |Q_AB union Q_AC union Q_BC|.
```

Then exactly 2+sigma cubic completion variables lie outside the union.

Three structural exclusions hold for every t.

### sigma=0

Only two completion triples remain. The two checks r,s incident with x require
at least three distinct completion variables once the single zero hole is
accounted for. A completion triple cannot contain both r and s, because it
would share the pair {r,s} with x and create a Tanner C4.

Hence sigma=0 is impossible.

### sigma=1

There are exactly three completion triples and one pair-shared triple T.

The zero hole must be r or s; otherwise r and s each require two additional
incidences and at least four completion triples are needed.

Assume the hole is r. The total deficits are exactly:

```text
three points of T : 1 each,
r,s               : 1 and 2,
A,B,C              : 1 each.
```

There are nine deficit incidences and exactly nine completion slots. Linearity
therefore forces each completion triple to contain:

```text
one point of T,
one of {r,s},
one of {A,B,C}.
```

The unique completion through r must be chosen by all three v=0 exact covers,
because x is absent in them and no other variable can cover r. But that
completion contains one survivor J in {A,B,C}; the cover X_J externally
satisfies J and therefore cannot choose an internal variable containing J.
Contradiction.

Hence sigma=1 is impossible for every t.

### sigma=2 from one all-three-common block

There are four completion triples. A triple shared by all three near-parallel
classes leaves its three points needing six additional incidences, or at least
five if the unique zero hole lies on the common triple. By linearity each
completion triple can meet that common triple in at most one point.

Capacity four is below the required five. Hence this sigma=2 subtype is
impossible for every t.

## 3. The first genuine residual counterexample occurs at t=6

At t=6:

```text
a=19,
b=18.
```

E90 finds an exact C4-free active residual with checks 0..18, survivor checks

```text
A=0, B=1, C=2,
```

zero-hole check

```text
R=17,
```

and degree-two boundary variable

```text
x={17,18}.
```

The seventeen cubic active variables are

```text
(0,3,15)
(0,12,16)
(1,2,18)
(1,7,8)
(2,3,4)
(3,6,10)
(4,5,9)
(4,7,13)
(5,6,7)
(5,10,12)
(6,9,16)
(8,9,10)
(8,11,14)
(11,12,13)
(11,15,18)
(13,14,17)
(14,15,16)
```

together with x={17,18}.

Every pair of variables meets in at most one check, so the Tanner geometry is
C4-free.

With the R boundary incidence pinned to zero, the exact four-port family on
A,B,C,x is exactly

```text
boxed:
{1,2,4,11,13,14}
= U_{2,4} twisted by the x coordinate.
```

Therefore:

```text
boxed:
C4-free RXC3 residual geometry DOES NOT by itself exclude conditioned U2,4.
```

This kills the proposed universal zero-hole-geometric exclusion.

## 4. Immediate unpin is not a delta parent

Restore R as a fifth free check-side port. The exact five-port family on
A,B,C,R,x is

```text
D5 = {1,2,4,8,19,21,22}.
```

Conditioning R=0 and projecting recovers the U2,4-twist target.

But D5 is not a delta-matroid. After the E83 canonical twist by x, all feasible
sets have rank two, yet ordinary matroid basis exchange fails.

So the first C4-free conditioned witness does **not** supply the missing
nonbinary exact delta interface.

This moves the representation frontier from conditioned geometry to
**delta-parent liftability**.

## 5. Explicit square-cubic-linear source embedding

The residual gadget is not merely an abstract subcubic network. E90 embeds it
in an explicit full source with

```text
26 checks,
26 variables,
78 Tanner edges,
degree 3 at every Tanner vertex,
connected Tanner graph,
no Tanner C4.
```

Hence it belongs to the same square-cubic-linear/C4-free RXC3 geometry as the
hard-source lane.

Four active checks A,B,C,R are completed by outside variables and x is
completed by one outside check. The remaining seven outside checks and eight
outside variables are connected by the frozen completion in the companion
checker.

Thus the conditioned U2,4 phenomenon is compatible with a full cubic linear
source, not only with a residual gadget.

## 6. Complete expansion cone inside the frozen 26x26 source

Starting from the five-port residual D5, E90 absorbs boundary-adjacent outside
Tanner vertices one at a time. Each absorption composes the exact boundary
relation with one primitive Equality_3 or ExactOne_3 constraint, so no interior
SAT search or approximation is used.

Every connected induced superset of the witness cluster inside the frozen
26x26 completion is reached exactly once up to its outside-vertex subset.

Frozen totals:

```text
connected supersets                     = 14,345
canonical matroid boundary interfaces   =    160
nonbinary canonical matroid interfaces  =      0
```

The 160 matroidal interfaces are distributed by boundary arity as

```text
arity 3 :  9
arity 4 : 16
arity 5 : 23
arity 6 : 57
arity 7 : 36
arity 8 : 14
arity 9 :  5
```

Every one is independently reconstructed over GF(2) from a fundamental basis
and reproduces its complete basis family.

Therefore this full finite expansion cone contains no nonbinary delta parent.

## 7. What E90 proves and refutes

```text
REFUTED:
C4-free conditioned zero-hole geometry alone forbids U2,4.

PROVED:
sigma=0 and sigma=1 are impossible for all t;
the all-three-common sigma=2 subtype is impossible for all t;
a genuine C4-free conditioned U2,4 residual exists at p=1,h=1,t=6;
that residual embeds in a full connected square-cubic-linear 26x26 source;
its immediate five-port unpin is non-delta;
all 160 matroidal interfaces in the complete connected expansion cone of one
explicit 26x26 completion are binary.
```

The finite expansion-cone result is deliberately not promoted to a universal
theorem.

## 8. New exact representation frontier

A universal binary theorem now requires a **delta-parent liftability** argument:

```text
Can a conditioned U2,4 residual be embedded into ANY exact Tanner boundary
relation D that is itself a delta-matroid, such that the E83 canonical matroid
D*P is nonbinary?
```

Equivalently, one must classify the possible one-element and multi-element
matroid lifts above U2,4 and determine whether their Tanner-side twisted
boundary families are compatible with square-cubic-linear exact semantics.

This is more precise than continuing to exclude residual C4-free geometries,
because E90 proves those geometries can already realize the minor.

## 9. Next killer-test — E91

```text
U24 DELTA-PARENT LIFT CLASSIFICATION

Classify every one-element matroid extension/coextension N of U2,4:
  deletion predecessor N\e = U2,4,
  contraction predecessor N/e = U2,4.

Translate every basis-family type through the canonical Tanner twist and all
five survivor orientations p=0..4.

Then either:
  1. prove no corresponding five-free-port exact Tanner delta relation can
     occur after propagation in a square-cubic-linear source; or
  2. construct the first genuine nonbinary delta parent.

Use the E90 D5 family as a negative control: it conditions to U2,4 but fails
basis exchange before any global claim.
```

Even closing the representation front would not solve the full problem: E81
still falsifies static disjoint delta partitioning, so a recursive/overlapping
represented elimination theorem remains necessary.

Scientific status:

```text
E90 = CONDITIONED-U24 GEOMETRY COUNTEREXAMPLE
      + IMMEDIATE DELTA-PARENT FIREWALL
      + FINITE 26x26 EXPANSION-CONE BINARY CHECK.

LINEAR_RXC3_CONDITIONED_U24 = REALIZABLE.
LINEAR_RXC3_NONBINARY_DELTA_PARENT = OPEN.
STATIC_GLOBAL_DELTA_VERTEX_PARTITION = FALSIFIED.
RECURSIVE_REPRESENTED_DECOMPOSITION = OPEN.
P_VS_NP = OPEN.
```
