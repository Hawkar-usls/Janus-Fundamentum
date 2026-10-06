# R5 E90 — p=1,h=1 All-t Shared-Savings Firewall

Date: 2026-10-06

Status:
`SIGMA0_SIGMA1_ALL_T_EXCLUDED__SIGMA2_COMMON_BLOCK_EXCLUDED__FIRST_SURVIVOR_TWO_DISTINCT_PAIR_SHARES`

Scientific ceiling:

```text
E90 DOES NOT YET CLOSE THE ENTIRE p=1,h=1 ORIENTATION.

IT PROVES THREE ALL-t STRUCTURAL EXCLUSIONS:
  sigma=0;
  sigma=1;
  sigma=2 WHEN THE SAVING COMES FROM ONE BLOCK COMMON TO ALL THREE v=1 CLASSES.

THE FIRST SURVIVING STRUCTURAL LANE IS
  sigma=2 WITH TWO DISTINCT PAIR-SHARED BLOCKS.

OTHER E85 ORIENTATIONS p=0,2,3,4 ALSO REMAIN OPEN.
E81 STILL FALSIFIES THE STATIC GLOBAL PARTITION ROUTE.
P_VS_NP = OPEN.
```

## 1. Setup

E85 specialized the smallest conditioned-minor orientation to

[
p=1,qquad h=1,
]

with

[
a=3t+1,qquad b=3t.
]

Choose the three target states with variable survivor bit (v=1).  Let
(x={r,s}) be the unique degree-2 boundary variable.  Removing (x)
from those three exact covers leaves three near-parallel classes

[
Q_{AB},quad Q_{AC},quad Q_{BC},
]

each containing

[
n=t-1
]

cubic variables.  On the check ground

[
W=U-{r,s},
]

they partition respectively

[
W-{A,B},qquad
W-{A,C},qquad
W-{B,C}.
]

Source linearity means any two distinct cubic variables intersect in at most
one check.

E89 introduced

[
oxed{
sigma
=
3n-
|Q_{AB}cup Q_{AC}cup Q_{BC}|
}
]

and proved that the number of active cubic variables outside the three
near-class union is exactly

[
oxed{2+sigma}.
]

Call these the **completion triples**.

## 2. Pairwise shared-block capacity

Take any two near-classes of (n) triples and suppose they share (k) whole
blocks.

Cancel those (k) common blocks.  Put

[
m=n-k.
]

The remaining two classes must carry (3m-1) common ordinary points.  Build
their block-intersection graph:

* left vertices = residual blocks of the first class;
* right vertices = residual blocks of the second class;
* every common point gives one edge.

Linearity makes this graph simple.  Hence it has capacity at most (m^2).

Therefore

[
oxed{3m-1le m^2}.
]

For (m=1,2),

[
3m-1>m^2.
]

Thus

[
oxed{kle n-3}.
]

This recovers and generalizes the finite shared-block capacity checks that
appeared in E88-E89.

The language is closely related to partial parallel classes in partial Steiner
triple systems; however the E90 statement is a direct consequence of source
linearity and does not require an external design-theory existence theorem.

## 3. sigma=0 is impossible for every t

If (sigma=0), there are exactly two completion triples.

### Overlap zero-hole geometry

Both (r) and (s) have cubic deficit two.  Hence the completions must supply
four incidences among ({r,s}).

But no cubic variable may contain both (r) and (s), because it would share
the pair ({r,s}) with (x) and create a Tanner (C_4).

So each completion contributes at most one (r/s) incidence.  Two completions
have capacity only two, while four are required.

Contradiction.

### Distinct zero-hole geometry

If the zero hole is an ordinary (W)-point, that point already has degree
three from the three block-disjoint near-classes and is immediately overfull.

If the zero hole is (r) or (s), the (r/s) cubic deficits are (1+2=3).
Two completion triples can supply at most two such incidences.

Contradiction.

Therefore

[
oxed{sigma=0	ext{ is impossible for every }t.}
]

This is the all-(t) version of the no-share contradiction observed in E89.

## 4. sigma=1 has exactly one pair-shared block

A saving of one cannot come from a block common to all three classes: such a
block saves two union elements.

Hence (sigma=1) means, after relabeling, exactly one block

[
Tin Q_{AB}cap Q_{AC}
]

and no other sharing.

The three points of (T) have active near-class degree two rather than three,
so each requires one completion incidence.

There are exactly

[
2+sigma=3
]

completion triples.

## 5. Capacity eliminates every sigma=1 hole except r or s

### Overlap hole

The (r/s) deficits are (2+2=4).

Three completions, each containing at most one of (r,s), have capacity only
three.

Impossible.

### Distinct ordinary hole outside T

Such a point already has near-class degree three but target active degree two.

Overfull; impossible.

### Distinct hole on T

The hole removes one of the three shared-block deficits, but the (r/s)
deficit remains four.

Again three completions have (r/s)-capacity only three.

Impossible.

Therefore the only capacity-surviving case is a distinct zero hole at (r)
or (s).  By symmetry take the hole at (r).

## 6. Exact local structure in the sole surviving sigma=1 case

With the hole at (r):

* (r/s) deficits are (1+2=3);
* the three points of (T) have total deficit three;
* (A,B,C) each have deficit one, total three.

The three completion triples contain exactly nine incidences.

Linearity with (x={r,s}) allows at most one (r/s) point per completion.
Since three such incidences are required, **every completion contains exactly
one of (r,s)**.

Linearity with the shared cubic variable (T) allows at most one point of
(T) per completion.  Since all three points of (T) require completion,
**every completion contains exactly one point of (T)**.

Six slots are now occupied.  The final three required incidences are exactly
(A,B,C).

Hence every completion has the form

[
oxed{
{	ext{one of }r,s}
cup
{	ext{one point of }T}
cup
{	ext{one of }A,B,C}.
}
]

Moreover each of (A,B,C) occurs in exactly one completion.

## 7. Hole-neighbour forcing contradiction

Because (r) is the zero-hole check, its active total degree is two.

One incidence is the special variable (x).  Therefore **exactly one cubic
completion triple** is incident with (r); call it (R).

Now consider the three target states with survivor variable bit (v=0).
Their selected cubic variables form covers

[
X_A,quad X_B,quad X_C,
]

where (X_A) covers every active check except (A), and similarly for
(B,C).

The variable (x) is off in all three states.  Therefore every one of
(X_A,X_B,X_C) must cover (r) using a cubic variable.

But (R) is the **only** cubic variable incident with (r).

Thus

[
oxed{
Rin X_Acap X_Bcap X_C.
}
]

Section 6 proved that (R) contains exactly one of (A,B,C).  Suppose it
contains (A).

Then (R) cannot belong to (X_A), because (X_A) must omit the check
(A).

Contradiction.

Therefore

[
oxed{sigma=1	ext{ is impossible for every }t.}
]

No finite census is involved.

## 8. sigma=2: one all-three-common block is also impossible for every t

A block common to all three near-classes has union saving two, so this is one
possible (sigma=2) pattern.

Let that block be (T).

Each of its three points has near-class union degree one instead of target
degree three.  Thus (T)'s points require six completion incidences.

There are only

[
2+sigma=4
]

completion triples.

By linearity, a completion triple distinct from (T) can meet (T) in at
most one point.  Hence total completion capacity on (T) is at most four.

Even if a distinct zero hole lies on one point of (T), the requirement falls
only from six to five.

Thus

[
5>4.
]

So

[
oxed{
sigma=2	ext{ via one block common to all three classes is impossible
for every }t.
}
]

This upgrades E89's finite all-three-common obstruction to an explicit all-size
statement.

## 9. First surviving structural lane

After E90, a minimal (p=1,h=1) counterexample must satisfy

[
oxed{sigmage2}.
]

At (sigma=2), the all-three-common pattern is dead.  The only remaining
possibility is therefore:

[
oxed{
	ext{two distinct pair-shared blocks}.
}
]

After relabeling, one may take

[
T_1in Q_{AB}cap Q_{AC},
qquad
T_2in Q_{AB}cap Q_{BC}.
]

Because (T_1,T_2) co-occur in the parallel class (Q_{AB}),

[
oxed{T_1cap T_2=arnothing}.
]

There are exactly four completion triples.

This is the new E91 theorem target.

## 10. Why this is useful for the universal algorithm route

The representation front has moved from

```text
arbitrary conditioned U2,4 minor
```

to

```text
p=1,h=1:
  sigma=0 dead for all t
  sigma=1 dead for all t
  sigma=2 common-all-three dead for all t
  first survivor = two disjoint pair-shared blocks
```

So the size parameter (t) is no longer the primary frontier.  The correct
parameter is the structural overlap saving (sigma).

That is exactly what is needed for an induction: prove that every minimal
counterexample either has low (sigma) (now increasingly excluded) or
contains a reducible shared-block trade.

## 11. E91 killer-test

```text
SIGMA2 TWO-DISTINCT-SHARES KILLER

Assume
  T1 in Q_AB cap Q_AC,
  T2 in Q_AB cap Q_BC,
  T1 cap T2 = empty,
and no other near-class sharing.

There are four completion triples.

Classify the three zero-hole locations:
  overlap survivor hole;
  distinct hole at r/s;
  distinct hole on T1/T2.

Use exact deficit saturation plus the three v=0 covers X_A,X_B,X_C to
either:

1. derive a forced common completion / removable trade and reduce t; or
2. derive a repeated point-pair, hence a Tanner C4; or
3. construct the first genuine linear conditioned-U2,4 witness.
```

A universal (sigma=2) exclusion would leave (sigmage3) and make a
shared-savings induction substantially sharper.

## 12. Companion replay

```text
experiments/r5_e90_p1_h1_shared_savings_all_t_firewall.py
```

It freezes:

```text
pairwise shared capacity k <= n-3;
sigma=0 all-t exclusion;
sigma=1 all-t exclusion;
sigma=2 all-three-common all-t exclusion;
first surviving lane = two distinct pair-shared blocks.
```

Scientific status:

```text
E90 = ALL-t LOW-SHARED-SAVINGS FIREWALL.

P1_H1_SIGMA0 = EXCLUDED ALL t.
P1_H1_SIGMA1 = EXCLUDED ALL t.
P1_H1_SIGMA2_COMMON_ALL3 = EXCLUDED ALL t.
P1_H1_SIGMA2_TWO_DISTINCT_SHARES = OPEN.

LINEAR_RXC3_CONDITIONED_U24 = OPEN.
DIRECT_U24_THROUGH_12x12 = EXCLUDED BY E84.
STATIC_GLOBAL_DELTA_VERTEX_PARTITION = FALSIFIED BY E81.
RECURSIVE_REPRESENTED_DECOMPOSITION = OPEN.
P_VS_NP = OPEN.
```
