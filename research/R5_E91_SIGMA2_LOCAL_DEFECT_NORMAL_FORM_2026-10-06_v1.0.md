# R5 E91 — Sigma=2 Distinct-Shares Local Defect Normal Form

Date: 2026-10-06

Status:
`SIGMA2_DISTINCT_PAIR_SHARES_REDUCES_TO_FINITE_11_POINT_DEFECT_CORE`

Scientific ceiling:

```text
E91 DOES NOT YET EXCLUDE THE sigma=2 DISTINCT-PAIR-SHARE LANE.

IT PROVES THAT THE FOUR COMPLETION TRIPLES OF EVERY SUCH ALL-t WITNESS
LIVE ON A FIXED 11-POINT LOCAL DEFECT GROUND, INDEPENDENT OF t.

THE DISTINCT r/s ZERO-HOLE SUBCASE HAS AN ADDITIONAL FORCING THEOREM:
THE UNIQUE HOLE-NEIGHBOUR COMPLETION IS COMMON TO ALL THREE v=0 COVERS
AND MUST HAVE THE FORM {r, t_i, u_j}.

THE REMAINING DIFFICULTY IS A GLOBAL EXTENSION QUESTION FOR THE THREE
NEAR-PARALLEL CLASSES, NOT GROWTH OF THE LOCAL DEFECT.

P_VS_NP = OPEN.
```

## 1. Starting point from E90

For the p=1,h=1 conditioned-U2,4 lane, remove the special degree-2 variable

```text
x = {r,s}.
```

The three v=1 solutions give near-parallel classes

```text
Q_AB, Q_AC, Q_BC
```

of n=t-1 cubic variables.

E90 proved all-t impossibility for:

```text
sigma=0,
sigma=1,
sigma=2 via one block common to all three classes.
```

The first surviving structural lane is therefore

```text
sigma=2
```

realized by two distinct pair-shared blocks. After relabeling:

```text
T1 in Q_AB cap Q_AC,
T2 in Q_AB cap Q_BC,
Q_AC cap Q_BC = empty,
```

with no other near-class sharing.

Because T1 and T2 co-occur in Q_AB, source linearity gives

```text
T1 cap T2 = empty.
```

Exactly

```text
2 + sigma = 4
```

cubic active variables lie outside the near-class union. Call them the
completion triples.

## 2. Universal local degree profile

Every ordinary W-point outside T1 union T2 belongs to three distinct near-class
variables, one in each Q-class. Its active cubic degree is therefore already 3.

Hence:

```text
* no completion triple may touch such a saturated point;
* a distinct zero hole cannot be placed there, because the target active
  degree would drop from 3 to 2 while the near-class union already contributes 3.
```

Each point of T1 appears in only two distinct near-class variables because its
Q_AB and Q_AC occurrences are the same block T1. Thus every T1 point has cubic
deficit 1 unless it itself is the distinct zero-hole check.

Likewise every point of T2 has deficit 1 unless it is the zero-hole check.

The survivor checks A,B,C each have near-class degree 1 and normally require
one completion incidence. If the zero hole overlaps one of those survivor
checks, that one target degree drops to 1 and its completion deficit becomes 0.

The checks r,s are covered in every v=1 state by x. In the active incidence
geometry x is their only near-class variable. Their cubic deficits are therefore

```text
2 and 2,
```

except that if the distinct zero hole is at one of r,s, the corresponding
cubic deficit becomes 1.

In all legal hole positions the total completion deficit is exactly 12, hence
exactly four cubic triples are required.

Therefore:

```text
boxed:
EVERY sigma=2 DISTINCT-SHARES COMPLETION TRIPLE IS SUPPORTED ON

    T1 union T2 union {A,B,C,r,s},

A FIXED 11-POINT GROUND INDEPENDENT OF t.
```

This is the central E91 normal form.

## 3. Intrinsic linearity constraints

Every completion triple must obey:

```text
* at most one point from T1;
* at most one point from T2;
* at most one of {r,s};
* any two completion triples intersect in at most one point.
```

The first two follow because T1,T2 are themselves active cubic variables.
The third follows because x={r,s} is an active variable.
The fourth is the original C4-free / source-linearity condition.

Additional restrictions coming from nonlocal Q-blocks can only delete local
skeletons from the E91 list; they can never add new ones.

## 4. Three zero-hole location types

Up to the natural symmetries, every surviving zero hole is one of:

```text
A. overlap survivor hole:
   one of A,B,C;

B. distinct x-neighbour hole:
   r or s;

C. distinct shared-block hole:
   one point of T1 or T2.
```

A distinct zero hole on a saturated ordinary point is impossible by Section 2.

For one fixed representative of each type, E91 exhausts the local completion
quadruples subject only to the universal degree and intrinsic-linearity rules.

Exact counts:

```text
overlap hole at A :  252
distinct hole at r: 1152
hole at t1 in T1 :  324
```

These are relaxed supersets of the genuine global candidates.

The crucial point is not the numerical count by itself: the count is
independent of t. The local part of the supposed all-size counterexample is now
finite.

## 5. Strong forcing in the r/s-hole case

Take the distinct zero hole to be r.

Then r has active total degree 2:

```text
one incidence from x,
one cubic completion incidence.
```

So there is a unique completion triple R containing r.

In every v=0 state the special variable x is off. Every v=0 exact cover must
therefore cover r using R.

Hence:

```text
boxed:
R belongs to X_A, X_B and X_C simultaneously.
```

But X_A omits A, X_B omits B, and X_C omits C. Therefore a block common to all
three cannot contain any of A,B,C:

```text
R cap {A,B,C} = empty.
```

Linearity with x forbids s in R.

No saturated nonlocal point is available by Section 2.

R has two remaining positions. A completion may meet T1 and T2 in at most one
point each. Therefore necessarily

```text
boxed:
R = {r, t_i, u_j}
with t_i in T1 and u_j in T2.
```

This is an all-t structural theorem, not a finite census artifact.

## 6. Necessary v=0 endpoint filter

For each v=0 cover X_A,X_B,X_C:

```text
* x is off;
* r must be covered by one r-completion;
* s must be covered by one s-completion;
* those two selected completion triples must be disjoint;
* a selected completion in X_A cannot contain A, etc.
```

Applying only this necessary local condition to the 1152 relaxed r-hole
quadruples leaves exactly

```text
558
```

local skeletons.

Every one of those 558 has the forced common form from Section 5.

Again this is a necessary filter only. The remaining Q-block geometry and
complete X_A/X_B/X_C exact covers impose additional constraints.

## 7. Relation to design-theory trade machinery

The E84-E91 residual objects are partial Steiner triple systems: source
linearity says every point-pair occurs in at most one cubic variable, and the
Q-classes are partial parallel classes.

This makes the trade literature relevant. In particular, Cavenagh and Griggs
classify subcubic Steiner trades using simultaneous edge-colourings and show
that the fundamental cubic building blocks are 3-regular 1-factorisable graphs.

Reference:

```text
Nicholas J. Cavenagh, Terry S. Griggs,
"Subcubic trades in Steiner triple systems",
Discrete Mathematics 340 (2017), 1351-1358.
DOI: 10.1016/j.disc.2016.10.021
```

Their theorem is not inserted as a black-box proof of E91: our six exact covers
are not automatically a Steiner trade set in their technical pair-balanced
sense. But their simultaneous-edge-colouring normal form is now a natural
candidate language for the E92 global extension problem.

## 8. Why E91 matters for the universal algorithm route

Before E91, sigma=2 appeared to require a new census for every t.

After E91:

```text
local completion geometry = finite 11-point defect skeleton;
all t-dependence = extension of three near-parallel classes outside that core.
```

So the representation frontier has become a finite-defect extension theorem,
which is the right shape for induction or a graph-colouring argument.

## 9. Next killer-test — E92

```text
SIGMA2 GLOBAL EXTENSION KILLER

Input:
  one of the finite E91 local defect skeletons,
  plus three linear near-parallel classes extending T1,T2.

Goal:
  decide whether all three v=0 covers X_A,X_B,X_C can coexist.

Primary routes:
  1. convert the extension outside the defect core to a simultaneous
     edge-colouring / 1-factorisation object;
  2. prove every legal extension forces a common reducible trade;
  3. or derive a repeated pair, hence Tanner C4.

The r/s-hole subcase starts from the forced common block
  {r,t_i,u_j} in X_A cap X_B cap X_C.
```

A universal E92 exclusion would kill the entire sigma=2 distinct-share lane
for all t.

## 10. Companion replay

```text
experiments/r5_e91_sigma2_local_defect_normal_form.py
```

Frozen assertions:

```text
fixed-hole relaxed local skeletons:
  overlap = 252
  r-hole  = 1152
  shared-hole = 324

r-hole skeletons satisfying the necessary all-three endpoint condition:
  558

every surviving r-hole skeleton:
  unique r-completion = {r, one T1 point, one T2 point}.
```

Scientific state:

```text
E91 = ALL-t SIGMA2 LOCAL DEFECT NORMAL FORM PROVED.

SIGMA2_LOCAL_GROWTH_WITH_t = ELIMINATED.
SIGMA2_GLOBAL_EXTENSION = OPEN.

P1_H1_SIGMA0 = EXCLUDED ALL t.
P1_H1_SIGMA1 = EXCLUDED ALL t.
P1_H1_SIGMA2_COMMON_ALL3 = EXCLUDED ALL t.
P1_H1_SIGMA2_DISTINCT_SHARES = REDUCED TO FINITE DEFECT + GLOBAL EXTENSION.

LINEAR_RXC3_CONDITIONED_U24 = OPEN.
RECURSIVE_REPRESENTED_DECOMPOSITION = OPEN.
P_VS_NP = OPEN.
```
