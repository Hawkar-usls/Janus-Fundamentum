# R5 E89 — p=1,h=1 t=5 Shared-Block Killer

Date: 2026-10-06

Status:
`P1_H1_CONDITIONED_U24_EXCLUDED_THROUGH_T5__SHARED_NEAR_CLASS_ORBIT_CENSUS_ZERO_SIX_COVERS`

Scientific ceiling:

```text
E89 DOES NOT EXCLUDE ALL CONDITIONED U2,4 MINORS.

IT CLOSES THE p=1,h=1 LANE AT
    t=5 -> 16 checks / 15 variables.

COMBINED WITH E86-E88:
    p=1,h=1 IS EXCLUDED FOR t=1,2,3,4,5.

THE FIRST OPEN SIZE IN THIS LANE IS
    t=6 -> 19 checks / 18 variables.

OTHER E85 ORIENTATIONS REMAIN OPEN.

P_VS_NP = OPEN.
```

## 1. Three v=1 covers at t=5

For (p=1,h=1,t=5),

[
a=16,qquad b=15.
]

Let (x={r,s}) be the unique degree-two active variable carrying the
surviving variable-side port.

As in E88, remove (x,r,s) from the three target states with (v=1).

On the remaining ground

[
W,qquad |W|=14,
]

we obtain three near-parallel classes

[
Q_{AB},Q_{AC},Q_{BC},
]

each containing four cubic variables:

[
Q_{AB}	ext{ partitions }W-{A,B},
]
[
Q_{AC}	ext{ partitions }W-{A,C},
]
[
Q_{BC}	ext{ partitions }W-{B,C}.
]

The active triple system is linear.

## 2. Any pair shares at most one triple

Take two classes and suppose they share (k) triple variables.

Cancel those common triples.

With

[
m=4-k
]

blocks remaining on each side, the classes must still carry exactly

[
3m-1
]

common points.

Distinct triples intersect in at most one point, so their common points form a
simple bipartite intersection graph with at most

[
m^2
]

edges.

If (kge2), then (mle2), and:

[
3m-1>m^2.
]

Therefore

[
oxed{kle1.}
]

So each pair of the three near-parallel classes either shares no block or
shares exactly one block.

## 3. Complete canonical near-class census

Fix (Q_{AB}) canonically by relabeling the eleven ordinary points while
fixing (A,B,C).

There are exactly

[
2052
]

linear possibilities for (Q_{AC}).

For each, E89 enumerates every compatible (Q_{BC}).

Complete total:

[
oxed{412,344}
]

canonical ordered triples

[
(Q_{AB},Q_{AC},Q_{BC}).
]

The exact sharing-pattern counts are:

```text
no pair shares                         291,600

Q_AB/Q_AC only                          36,288
Q_AB/Q_BC only                          36,288
Q_AC/Q_BC only                          36,288

Q_AB/Q_AC and Q_AB/Q_BC                 3,888
Q_AB/Q_AC and Q_AC/Q_BC                 3,888
Q_AB/Q_BC and Q_AC/Q_BC                 3,888

one block common to all three              216

three distinct pair-shared blocks              0
```

The last zero also has a direct structural explanation.

If three distinct pair-shared triples existed, each pair of them would
co-occur in one near-parallel class and hence they would be pairwise disjoint.

Consider one class, say (Q_{AB}). It contains two of the shared triples and
does not contain the third. The third shared triple has three points. Those
three points must all be covered by the two remaining triples of (Q_{AB}).

Linearity allows each remaining triple to meet the omitted shared triple in at
most one point, giving capacity only two.

Contradiction.

Therefore the complete sharing classification above is structural, not merely
an observed pattern.

## 4. No-share pattern dies immediately

Suppose the three near-parallel classes share no triple.

Then all

[
3(t-1)=12
]

near-class triples are distinct.

Every ordinary point of (W-{A,B,C}) is already incident with three active
variables and is saturated.

Each of (A,B,C) has degree one.

The active instance has

[
3t-1=14
]

cubic variables besides (x), so only two additional cubic variables remain.

Exactly the same deficit argument as E88 applies:

* in the overlap case both (r,s) need two additional incidences;
* in the distinct case either an ordinary zero-hole point is already overfull,
  or one of (r,s) is the hole and the other still needs two incidences.

With only two remaining triples, linearity with (x={r,s}) is violated.

Thus:

[
oxed{	ext{no-share is impossible.}}
]

This argument in fact works at every (t): if the three (v=1) near-classes
are pairwise block-disjoint, only two active triples remain outside their union.

## 5. All-three-common pattern dies by degree capacity

Suppose one triple (Tsubseteq W-{A,B,C}) is common to all three classes.

As an active variable it contributes degree one, not three, to each of its
three check points.

The occurrence savings are two, so there are exactly four completion triples
outside the near-class union.

### Overlap zero hole

All three points of (T) require two more incidences:

[
6
]

required incidences on (T).

Every completion triple can meet (T) in at most one point by linearity.

Four completion triples have capacity only four.

Impossible.

### Distinct zero hole

If the hole lies outside (T) on an already saturated ordinary point, the
degree target is already violated.

If the hole lies on (T), the three points of (T) require

[
1+2+2=5
]

additional incidences.

Again four completion triples have capacity only four.

If the hole is (r) or (s), all six incidences on (T) are still required.

Thus:

[
oxed{	ext{all-three-common is impossible.}}
]

## 6. One-pair-share pattern

By symmetry it is enough to take

[
Q_{AB}cap Q_{AC}={T},
]

with the other two pairwise intersections empty.

The shared block (T) lies entirely among ordinary points.

The union contains 11 distinct near-class triples, so there are exactly three
completion triples.

The only degree-feasible zero-hole placement is a distinct hole at (r) or
(s).

Why:

* overlap leaves both (r,s) needing two incidences across only three
  completion triples; two 2-subsets of a 3-set must intersect, forcing some
  completion triple to contain both (r,s);
* a distinct hole on a saturated ordinary point is impossible;
* a distinct hole on a point of (T) still leaves both (r,s) requiring two
  incidences across three triples and gives the same contradiction.

So only

[
H=rquad	ext{or}quad H=s
]

survives the degree count.

## 7. One-share orbit reduction

Fixing (Q_{AB}) canonically leaves an automorphism group generated by:

* the swap of the two ordinary points in the special (C)-block;
* permutations inside each of the three ordinary (Q_{AB})-blocks;
* permutations of those three blocks.

For the representative one-share pattern, the

[
36,288
]

canonical systems collapse to exactly

[
oxed{15	ext{ orbits}}
]

with sizes

```text
13 orbits of size 2592
 2 orbits of size 1296.
```

E89 tests one representative of each orbit and both possible x-neighbour hole
placements (H=r,s).

Every degree-completing set of three cubic variables is enumerated under
linearity with:

* the near-class triples;
* (x={r,s});
* each other completion triple.

Exact total over the 15 orbit representatives:

[
oxed{468	ext{ degree completions}.}
]

For a six-state (U_{2,4})-twist witness, the final active triple system must
also admit the three (v=0) exact covers:

[
X_A,quad X_B,quad X_C,
]

where (X_A) partitions all active checks except (A), and similarly for
(B,C).

Result:

[
oxed{
468	ext{ completions},qquad
0	ext{ admit all }X_A,X_B,X_C.
}
]

Therefore the one-share lane is impossible.

## 8. Two-pair-share pattern

By symmetry take

[
|Q_{AB}cap Q_{AC}|=1,
]
[
|Q_{AB}cap Q_{BC}|=1,
]
[
Q_{AC}cap Q_{BC}=arnothing.
]

The two shared blocks are distinct and disjoint because they co-occur inside
(Q_{AB}).

The union contains ten distinct near-class triples, leaving four completion
triples.

The

[
3888
]

canonical systems collapse under the same automorphism group to only

[
oxed{2	ext{ orbits}},
]

of sizes

[
2592,qquad1296.
]

For each representative E89 tests:

* all three overlap-hole choices (A,B,C);
* every distinct-hole position among the ordinary points and (r,s);
* every degree-completing set of four cubic variables satisfying linearity.

Exact total:

[
oxed{7392	ext{ degree completions}.}
]

Again require all three (v=0) covers (X_A,X_B,X_C).

Result:

[
oxed{
7392	ext{ completions},qquad
0	ext{ admit all three }v=0	ext{ covers}.
}
]

Therefore the two-share lane is impossible.

## 9. t=5 conclusion

All possible sharing patterns are exhausted:

```text
no shares             -> structural degree/C4 contradiction
one pair shares       -> 15 orbit representatives, zero six-cover completions
two pairs share       -> 2 orbit representatives, zero six-cover completions
one block common all  -> structural shared-block capacity contradiction
three distinct shares -> structurally impossible
```

Hence:

[
oxed{
p=1, h=1, t=5
	ext{ cannot realize conditioned }U_{2,4}
	ext{ under C4-freeness.}
}
]

Combined with E86-E88:

[
oxed{
p=1,h=1	ext{ is excluded for }t=1,2,3,4,5.
}
]

## 10. First open size

The first open size in this orientation is

[
t=6:
qquad
a=19,qquad
b=18.
]

After removing the common variable (x), the three (v=1) near-parallel
classes have

[
n=t-1=5
]

triples each on

[
3n+2=17
]

points.

The pairwise shared-block capacity inequality becomes:

[
3m-1le m^2,qquad m=n-k.
]

It only forbids (mle2), so a pair may now share as many as

[
kle n-3=2
]

blocks.

Thus the sharing state space expands, and a blind canonical enumeration is not
the preferred next move.

## 11. New general invariant exposed by E88-E89

The right induction parameter is not (t) itself but the **shared-block
savings**

[
sigma
=
3(t-1)
-
left|Q_{AB}cup Q_{AC}cup Q_{BC}ight|.
]

There are always exactly

[
2+sigma
]

active cubic variables outside the three (v=1) near-class union.

Every shared block creates degree deficits of three on its points but also
creates one additional completion variable.

The E88/E89 contradictions arise because linearity limits how efficiently
those completion variables can refill the shared-block deficits while also
servicing the two neighbours (r,s) of (x) and enabling the three
(v=0) parallel classes.

This is the likely all-(t) induction quantity.

## 12. Next killer-test — E90

```text
P1_H1 SHARED-SAVINGS INDUCTION

For arbitrary t, encode the three v=1 near-parallel classes by their shared
blocks and the simple pairwise intersection graphs after common blocks are
cancelled.

Prove an inequality of the form

    completion capacity required by
      shared-block deficits + x-neighbour deficits + three X-covers
    >
    capacity allowed by
      2+sigma completion triples under linearity,

unless a removable common subtrade exists.

If a removable common subtrade exists, reduce to smaller t and invoke the
already-closed base cases t<=5.

Primary target:
    prove every minimal counterexample has sigma=0;
then the no-share contradiction closes the entire p=1,h=1 lane.

Fallback:
    classify sigma=1,2 for arbitrary t and prove they reduce/contradict.
```

A full E90 induction would eliminate the most dangerous minor-only orientation
for all sizes.

## 13. Companion replay

```text
experiments/r5_e89_p1_h1_t5_shared_block_killer.py
```

Frozen assertions:

```text
canonical near-class systems = 412,344

sharing counts:
  no share = 291,600
  each one-share type = 36,288
  each two-share type = 3,888
  all-three-common = 216
  three distinct pair-shares = 0

one-share:
  15 automorphism orbits
  468 degree completions
  0 six-cover hits

two-share:
  2 automorphism orbits
  7,392 degree completions
  0 six-cover hits
```

Scientific status:

```text
E89 = EXACT P1_H1 T5 EXCLUSION
      + COMPLETE SHARED-BLOCK CLASSIFICATION.

P1_H1_T1_TO_T5 = EXCLUDED.
P1_H1_T6_PLUS = OPEN.

LINEAR_RXC3_CONDITIONED_U24 = OPEN.
DIRECT_U24_THROUGH_12x12 = EXCLUDED BY E84.
STATIC_GLOBAL_DELTA_VERTEX_PARTITION = FALSIFIED BY E81.
RECURSIVE_REPRESENTED_DECOMPOSITION = OPEN.
P_VS_NP = OPEN.
```
