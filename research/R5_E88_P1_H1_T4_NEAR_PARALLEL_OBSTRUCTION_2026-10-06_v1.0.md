# R5 E88 — p=1,h=1 t=4 Near-Parallel-Class Obstruction

Date: 2026-10-06

Status:
`P1_H1_CONDITIONED_U24_EXCLUDED_THROUGH_T4__THREE_NEAR_PARALLEL_CLASSES_FORCE_DEGREE_CONTRADICTION`

Scientific ceiling:

```text
E88 DOES NOT EXCLUDE ALL CONDITIONED U2,4 MINORS.

IT CLOSES THE p=1,h=1 LANE AT
    t=4 -> 13 checks / 12 variables
BY A STRUCTURAL NEAR-PARALLEL-CLASS ARGUMENT, WITH AN EXACT ENUMERATIVE REPLAY.

COMBINED WITH E86/E87:
    p=1,h=1 IS EXCLUDED FOR t=1,2,3,4.

THE FIRST OPEN SIZE IN THIS LANE IS
    t=5 -> 16 checks / 15 variables.

P_VS_NP = OPEN.
```

## 1. Six conditioned states as exact covers

For the E85 orientation (p=1,h=1),

[
a=3t+1,qquad b=3t.
]

There are three surviving check ports (A,B,C) and one surviving variable
port carried by the unique degree-two active variable (x).

The target four-port family is

[
{1,2,4,11,13,14}.
]

The three states with variable bit (v=0) leave exactly one of
(A,B,C) externally satisfied.

The three states with (v=1) select (x) and leave exactly one pair among

[
{A,B},quad {A,C},quad {B,C}
]

externally satisfied.

At (t=4), every state selects exactly four active variables.

## 2. Remove the common degree-two variable

Write

[
x={r,s}
]

for the two internal check-neighbours of the boundary variable.

Because (x) is selected in all three (v=1) states, it cannot meet any of
(A,B,C): each of those three checks is externally satisfied in two of the
three states.

Remove (x) and the two points (r,s) from the three (v=1) covers.

The remaining ground set is

[
W,qquad |W|=11,
]

containing (A,B,C) and eight ordinary checks.

The three (v=1) covers become three collections of three cubic variables:

[
Q_{AB},quad Q_{AC},quad Q_{BC},
]

with

[
Q_{AB}	ext{ partitions }W-{A,B},
]
[
Q_{AC}	ext{ partitions }W-{A,C},
]
[
Q_{BC}	ext{ partitions }W-{B,C}.
]

Thus they are three near-parallel classes in a linear 3-uniform system.

## 3. Pairwise shared-block capacity lemma

Consider (Q_{AB}) and (Q_{AC}).

They have nine covered points each and eight common ordinary covered points.
Suppose they share (kge1) triple variables.

Cancel those common triples from both classes.

Let

[
m=3-k
]

triples remain on each side.

The remaining classes have exactly

[
3m-1
]

common covered points.

Since the system is linear, two distinct triples can intersect in at most one
point. Therefore their common points form a simple bipartite intersection
graph with (m) vertices on each side and at most

[
m^2
]

edges.

For (k=1), (m=2):

[
3m-1=5>4=m^2.
]

For (k=2), (m=1):

[
3m-1=2>1=m^2.
]

Therefore no common block is possible.

The same argument applies to every pair of the three classes.

Hence:

[
oxed{
Q_{AB},Q_{AC},Q_{BC}
	ext{ consist of nine distinct triple variables.}
}
]

## 4. Degree saturation

Every ordinary point of

[
W-{A,B,C}
]

is covered once by each of the three near-parallel classes.

Because the nine triple variables are all distinct, each ordinary point already
has active variable-degree exactly three.

Each of (A,B,C) occurs in exactly one of the classes, so each currently has
degree one.

The variable (x={r,s}) contributes one incidence to each of (r,s).

The active Tanner instance has

[
b=12
]

variables total:

* the common degree-two variable (x);
* the nine distinct triples in the three (v=1) classes;
* exactly two remaining cubic variables.

Thus only two triples remain available to complete every active check degree.

## 5. Overlap zero-hole case is impossible

Suppose the unique zero hole overlaps one of the survivor checks, say (A).

Then the required internal check degrees are:

[
deg(A)=1,qquad
deg(B)=deg(C)=2,
]

and every ordinary check, including (r,s), has internal degree three.

After the nine near-class triples plus (x):

* (A) already has degree 1;
* (B,C) each need one more incidence;
* every ordinary point in (W-{A,B,C}) is already saturated;
* (r,s) each have degree 1 and therefore each need two more incidences.

There are only two remaining cubic variables.

Thus both remaining triples would have to contain both (r) and (s).

But (x) itself contains the pair ({r,s}). Any cubic variable containing
both would share two checks with (x), creating a Tanner (C_4).

Contradiction.

## 6. Distinct zero-hole case is impossible

Now suppose the zero-hole check (H) is distinct from (A,B,C).

If (H) lies among the eight ordinary points in (W), it is already saturated
to degree 3 by the three near-parallel classes, whereas a zero-hole check must
have internal degree 2.

So (H) must be one of (r,s). Without loss let

[
H=r.
]

Required deficits after the nine triples plus (x) are then:

* (A,B,C): one incidence each;
* (r): one incidence;
* (s): two incidences.

Again only two cubic variables remain.

Therefore both extra triples contain (s), and one of them must also contain
(r).

That triple contains the pair ({r,s}), again sharing two checks with the
degree-two variable (x).

Contradiction.

Therefore:

[
oxed{
p=1,h=1,t=4
	ext{ is impossible under Tanner C4-freeness.}
}
]

## 7. Exact replay

The companion checker independently freezes the complete finite core.

By relabeling the eight ordinary points, fix (Q_{AB}) canonically.

It then enumerates every compatible (Q_{AC},Q_{BC}) under linearity.

Exact count:

[
oxed{72}
]

canonical three-class systems.

Every one uses nine distinct triple variables, agreeing with the capacity
lemma.

The checker then enumerates every pair of additional cubic variables that is
linear with:

* all nine near-class triples;
* the degree-two variable (x={r,s});
* each other.

Across the 72 systems:

[
oxed{245,592}
]

linear extra-triple pairs are checked.

Degree-completing configurations:

```text
overlap zero-hole case  : 0
distinct zero-hole case : 0
```

The finite replay is therefore a regression certificate for the structural
proof, not its logical basis.

## 8. Combined p=1,h=1 frontier

The lane now reads:

```text
t=1 : impossible by pair-intersection counting       (E86)
t=2 : exact C4-free incidence census, zero hits      (E86)
t=3 : residual edge/half-edge census, zero hits      (E87)
t=4 : near-parallel-class degree obstruction         (E88)
t>=5: OPEN
```

The first open size is

[
t=5:
qquad
a=16,qquad b=15.
]

After removing the common degree-two variable from the three (v=1) covers,
the near-parallel classes each contain

[
n=t-1=4
]

triples on a ground of

[
3n+2=14
]

points.

The E88 pairwise-capacity argument now allows at most one shared triple between
a pair of classes, because cancellation of two shared blocks would leave
(m=2) and again require five intersections in a (2	imes2) graph.

Thus the next frontier is already sharply constrained:

[
oxed{
	ext{for }t=5,	ext{ every pair of the three }v=1	ext{ classes shares at most one block.}
}
]

## 9. Next killer-test — E89

```text
P1_H1_T5_SHARED-BLOCK KILLER

Classify the possible pairwise sharing pattern among
Q_AB, Q_AC, Q_BC when each has four triples:

  * no shared blocks;
  * one block shared by exactly one pair;
  * one shared block on two/three pairs;
  * a block shared by all three classes.

For each sharing type:

1. derive the degree deficit left for the five active variables not represented
   by the three v=1 cover occurrences and x;
2. impose the active check-degree pattern for overlap/distinct zero holes;
3. use linearity with x and between completion triples;
4. either prove the deficit cannot be completed, or construct the first
   C4-free six-cover candidate.

Only after a six-cover candidate survives should full four-port exact semantics
be evaluated.
```

A successful all-sharing-pattern exclusion at (t=5) would extend the lane
without a large Tanner-graph census and may expose the induction invariant
needed for all (t).

## 10. Companion replay

```text
experiments/r5_e88_p1_h1_t4_near_parallel_obstruction.py
```

Frozen assertions:

```text
canonical three near-parallel-class systems = 72
all systems use nine distinct triple variables
linear extra-triple pairs checked = 245,592
overlap degree completions = 0
distinct-hole degree completions = 0
```

Scientific status:

```text
E88 = STRUCTURAL P1_H1 T4 EXCLUSION
      + EXACT FINITE REPLAY.

P1_H1_T1_T2_T3_T4 = EXCLUDED.
P1_H1_T5_PLUS = OPEN.

LINEAR_RXC3_CONDITIONED_U24 = OPEN.
DIRECT_U24_THROUGH_12x12 = EXCLUDED BY E84.
STATIC_GLOBAL_DELTA_VERTEX_PARTITION = FALSIFIED BY E81.
RECURSIVE_REPRESENTED_DECOMPOSITION = OPEN.
P_VS_NP = OPEN.
```
