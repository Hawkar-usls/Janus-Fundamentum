# R5 E84 — Direct U2,4 Linearity Killer

Date: 2026-10-06

Status:
`DIRECT_C4FREE_S5_U24_EXCLUDED_THROUGH_12x12__RESIDUAL_CUBIC_NORMAL_FORM_PROVED__CONDITIONED_MINOR_FRONTIER_OPEN`

Scientific ceiling:

```text
E84 DOES NOT PROVE THAT EVERY SQUARE-CUBIC-LINEAR RXC3 DELTA INTERFACE IS BINARY.

IT PROVES AN EXACT NORMAL FORM FOR A DIRECT FOUR-PORT S5/U2,4 INTERFACE AND
EXHAUSTS THAT NORMAL FORM FOR EVERY SIMPLE-CUBIC RESIDUAL TOPOLOGY THROUGH
12 CHECKS + 12 VARIABLES.

NO DIRECT S5/U2,4 WITNESS EXISTS IN THAT RANGE.

U2,4 MAY STILL APPEAR
  (A) DIRECTLY AT 15x15 OR LARGER, OR
  (B) ONLY AS A CONDITIONED/DELETED/CONTRACTED MINOR OF A LARGER BOUNDARY
      MATROID.

THE STATIC GLOBAL PARTITION ROUTE REMAINS FALSIFIED BY E81.
P_VS_NP = OPEN.
```

## 1. Starting point

E83 proved the universal canonical-matroid theorem:

```text
exact ExactOne_3/Equality_3 boundary + delta exchange
    =>
D * P is an ordinary matroid,
```

where `P` is the complete variable-side boundary set.

Therefore the only binary-matroid obstruction is `U_{2,4}`.  Before E84 we had
an explicit unrestricted Tanner witness whose four-port relation was

```text
S5 = {0,5,6,9,10,15},
```

and whose canonical twist was `U_{2,4}`.  That witness contained Tanner C4s and
therefore did not lie in the square-cubic-linear RXC3 class.

E84 asks the sharp direct question:

```text
CAN A C4-FREE CUBIC TANNER CLUSTER HAVE EXACTLY FOUR BOUNDARY STUBS AND EXACT
BOUNDARY RELATION S5?
```

The answer is now **no through 12x12**, by an exact structural reduction plus a
complete finite census.

## 2. Four-port S5 orientation is forced

E82's signed mod-3 invariant gives every boundary coordinate a sign:

```text
+1 : variable-side boundary incidence,
-1 : check-side boundary incidence.
```

For `S5`, the only signed `+/-1` affine invariants are the two alternating sign
vectors, differing by a global sign.  Therefore a four-port Tanner realization
must have exactly

```text
2 check-side boundary coordinates,
2 variable-side boundary coordinates.
```

Relabel so bits `0,1` are check-side and bits `2,3` are variable-side.

## 3. The four boundary stubs lie on four distinct Tanner vertices

`S5` contains the all-one state `1111`.

### Check side

If the two check-side boundary stubs belonged to one ExactOne check, the all-one
boundary state would select two incident edges of that check, impossible under
ExactOne_3.

Hence the two check boundary stubs lie on two distinct checks.  Since there are
exactly two check-side stubs total, those two checks have internal degree two;
every other included check has internal degree three.

### Variable side

`S5` contains states in which the two variable boundary bits differ.  Two
boundary stubs on one Equality_3 variable must always carry the same bit.
Therefore the two variable boundary stubs lie on distinct variables.

Those two variables have internal degree two; every other included variable has
internal degree three.

## 4. The cluster must be square and divisible by three

Let

```text
a = number of included checks,
b = number of included variables,
m = number of internal Tanner edges.
```

The two check-side boundary deficits give

```text
m = 3a - 2.
```

The two variable-side boundary deficits give

```text
m = 3b - 2.
```

Therefore

```text
boxed: a=b.
```

Now use the `1111` feasible state as a reference exact cover.

The two boundary checks are already satisfied externally and hence have no
selected internal neighbour.  The two boundary variables are selected, each
covering its two internal checks.  Let `r` be the number of additional selected
internal degree-three variables.

The number of internally covered checks is therefore

```text
4 + 3r.
```

But precisely `a-2` checks must be covered internally.  Hence

```text
4 + 3r = a - 2,
```

so

```text
boxed:
a=b=3(r+2)=3t,
```

for an integer `t>=2`.

Thus a direct C4-free S5 candidate can exist only at

```text
6x6, 9x9, 12x12, 15x15, ...
```

The reference state selects exactly `t` variables: the two boundary variables
plus `t-2` degree-three core variables.

## 5. Residual-exchange graph normal form

Remove the `t` selected reference-cover variables conceptually and retain the
remaining

```text
3t - t = 2t
```

unselected variables as vertices of a graph `G`.

Every included check has exactly two neighbours among these unselected
variables:

* each of the two boundary checks has internal degree two and neither neighbour
  is selected in the `1111` reference state;
* every other check has internal degree three and exactly one selected
  reference-cover neighbour, leaving two unselected neighbours.

Represent each Tanner check by an edge joining its two residual variable
neighbours.  Then

```text
|V(G)| = 2t,
|E(G)| = 3t.
```

Every residual variable has original Tanner degree three and is incident with
three checks, so every vertex of `G` has degree three.

Because the source Tanner graph is C4-free, two residual variables cannot share
two checks.  Therefore `G` has no parallel edges.

Hence:

```text
boxed:
G is a SIMPLE CUBIC graph on 2t vertices.
```

Crucially, `G` need **not** be connected.  The original Tanner cluster may
remain connected through the selected reference-cover variables even when the
residual graph has multiple components.  This point was explicitly repaired
before freezing E84.

## 6. Reference-cover variables become edge matchings

Every selected reference-cover variable is incident with a set of Tanner
checks, hence with the corresponding set of edges of `G`.

If two such edges shared a residual vertex, the selected reference variable and
that residual variable would share two Tanner checks, producing a Tanner C4.
Therefore the edge set associated with each reference-cover variable is a
matching in `G`.

Specifically:

```text
* the two boundary variables give two 2-edge matchings;
* the t-2 core reference variables give t-2 3-edge matchings;
* the two boundary checks give two distinguished single edges;
* these blocks partition all 3t edges of G.
```

So every direct four-port C4-free S5 candidate is completely encoded by

```text
1. a simple cubic graph G on 2t vertices;
2. two distinguished check edges;
3. two disjoint 2-edge matching blocks;
4. t-2 disjoint 3-edge matching blocks;
5. the requirement that these blocks partition E(G).
```

This is the E84 residual-cubic normal form.

## 7. Exact boundary semantics in the normal form

Starting from the all-one reference cover, choose a subset `S` of residual
vertices whose variables become selected.

ExactOne immediately requires `S` to be an independent set of `G`; otherwise an
edge/check would receive two selected residual neighbours.

For a reference-cover matching block `B`, let `delta(S)` be the edge cut of `S`
in `G`.

There are only two valid possibilities:

```text
B cap delta(S) = empty:
    retain the reference-cover variable;

B subseteq delta(S):
    deselect the reference-cover variable and let the residual variables cover
    all its checks.
```

A partial crossing would leave some check uncovered or doubly covered.

For either distinguished boundary-check edge, its boundary bit is the complement
of whether that edge crosses `S`.  For either boundary-variable 2-matching, its
boundary bit is the complement of whether the entire matching crosses `S`.

Therefore the four-port exact boundary family is obtained exactly from
independent sets of `G` satisfying these uniform matching-crossing conditions.
No SAT oracle or heuristic search remains.

## 8. Complete residual topology census through t=4

The number of connected unlabeled simple cubic graphs on `2n` vertices is the
classical sequence A002851.  In particular the connected counts on 4,6,8
vertices are

```text
1, 2, 5.
```

The House of Graphs also publishes complete connected cubic graph lists and
notes independent verification by multiple generators for these graph classes.

For the E84 normal form we must include disconnected residual graphs as well.
A simple cubic connected component has at least four vertices.  Therefore:

```text
4 vertices: no disconnected case;
6 vertices: no disconnected case;
8 vertices: exactly one disconnected isomorphism type, K4 disjoint-union K4.
```

Thus the complete simple-cubic residual topology counts used by E84 are

```text
2t = 4 : 1 topology,
2t = 6 : 2 topologies,
2t = 8 : 6 topologies = 5 connected + K4 disjoint-union K4.
```

The checker freezes explicit representatives for every topology and verifies
cubicity, simplicity, and pairwise-distinguishing graph fingerprints.

## 9. Exhaustive matching-partition census

For every residual topology, E84 enumerates every choice of:

```text
* two distinguished check edges;
* ordered pair of disjoint 2-edge matching blocks for the two boundary vars;
* unordered collection of the remaining 3-edge matching blocks.
```

The exact totals are

```text
t=2  -> |C|=|V|=6  :       6 partitions,
t=3  -> |C|=|V|=9  :     360 partitions,
t=4  -> |C|=|V|=12 : 105,724 partitions,
--------------------------------------------
TOTAL                    : 106,090 partitions.
```

The disconnected `K4 disjoint-union K4` topology contributes an additional

```text
13,752
```

`t=4` configurations beyond the connected census.  Every one has singleton
boundary family `{1111}`; none is S5.

For each of all 106,090 configurations, the checker computes the exact four-bit
boundary relation by enumerating all independent residual sets and enforcing the
uniform crossing rule.

Result:

```text
boxed:
DIRECT S5 / U2,4 WITNESSES = 0
```

through `12 checks + 12 variables`.

## 10. Frozen relation distributions

The exact relation counters are part of the replay certificate.

### t=2

```text
{1111} : 6
```

### t=3

```text
{1111}      : 144
{0000,1111} : 216
```

### t=4

Using integer masks for four boundary bits:

```text
(15,)             : 80,130
(0,15)            : 19,488
(6,15)            : 1,592
(10,15)           : 1,592
(5,15)            : 1,420
(9,15)            : 1,420
(0,6,9,15)        : 24
(0,5,10,15)       : 24
(5,9,15)          : 18
(6,10,15)         : 16
```

Every relation in this census that satisfies delta exchange passes the E79
binary reconstruction test.  Thus the finite direct census produces no hidden
nonbinary delta relation either.

## 11. What E84 proves

```text
THEOREM / NORMAL FORM:
A direct four-port C4-free S5 candidate must have |C|=|V|=3t and is equivalent
to the residual simple-cubic matching-partition model above.

EXACT FINITE COROLLARY:
No direct S5/U2,4 exact boundary relation exists for t=2,3,4, i.e. for
6x6, 9x9, or 12x12 C4-free cubic Tanner clusters.
```

This strictly strengthens the earlier statement that the known E83 nonbinary
witness merely happened to contain C4s.

## 12. What E84 does not prove

Two representation-side escape hatches remain.

### A. Larger direct witness

The first possible untouched size is

```text
|C|=|V|=15  (t=5),
```

whose residual graph has ten cubic vertices.  The connected cubic census already
jumps to 19 isomorphism types before disconnected cases are included.

### B. Conditioned/minor-only U2,4

Tutte's obstruction theorem concerns a **minor** of the canonical boundary
matroid, not necessarily an interface whose raw boundary ground set already has
four elements.

Thus a larger exact delta interface might be binary-failing because, after
fixing/deleting/contracting other boundary coordinates, four surviving
coordinates realize `U_{2,4}`, even though no raw four-port S5 interface occurs.

E84 does not exclude this.

This is now the more important killer-test than merely extending the direct
census to `t=5`.

## 13. Interaction with the global algorithm route

Even a full proof that every linear RXC3 delta interface is binary would not by
itself solve the whole problem.  E81 already falsified the universal static
vertex-partition premise.

The two independent open fronts are therefore:

```text
REPRESENTATION FRONT:
exclude conditioned U2,4 minors (or find one).

GLOBAL ALGORITHM FRONT:
construct a recursive/overlapping represented elimination scheme that passes
E81 q=8 without assuming a static disjoint delta partition.
```

Both are needed before a universal polynomial Exact-One solver can be claimed.

## 14. Next killer-test — E85

```text
CONDITIONED U24 MINOR KILLER

Take a hypothetical C4-free square-cubic-linear RXC3 exact delta interface.
Assume four boundary coordinates survive after deletion/contraction/conditioning
and form U_{2,4} in the canonical matroid.

Propagate every fixed boundary bit through Equality_3 and ExactOne_3 first.
Derive the residual normal form of the six surviving S5 states, then either:

1. prove that the residual geometry forces a repeated check-pair, hence a Tanner
   C4; or
2. construct the first genuine C4-free conditioned S5/U2,4 witness.
```

A proof of impossibility for conditioned minors would establish the desired
universal binary-representation theorem for every square-cubic-linear RXC3
exact delta interface.

## 15. Companion replay

```text
experiments/r5_e84_u24_linearity_killer.py
```

Frozen assertions:

```text
complete simple-cubic residual topologies on 4/6/8 vertices: 1/2/6;
matching partitions: 6 / 360 / 105724;
total matching partitions: 106090;
direct S5 witnesses: 0;
all encountered delta relations: binary-even.
```

Scientific status:

```text
E84 = PROVED DIRECT-S5 RESIDUAL-CUBIC NORMAL FORM
      + EXACT NO-DIRECT-U24 CENSUS THROUGH 12x12.

DIRECT_U24_6x6_9x9_12x12 = EXCLUDED.
DIRECT_U24_15x15_PLUS = OPEN.
CONDITIONED_U24_MINOR = OPEN.
STATIC_GLOBAL_DELTA_VERTEX_PARTITION = FALSIFIED (E81).
RECURSIVE_REPRESENTED_DECOMPOSITION = OPEN.
P_VS_NP = OPEN.
```
