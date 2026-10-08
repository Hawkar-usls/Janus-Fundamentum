# R5 E113 — TARGET6 Support-Lift and Signed-Parallel Normal Firewall

Date: 2026-10-08

Status:
`E112_EDGE_FAITHFUL_LIFT_IMPOSSIBLE__ANY_JOINT_LIFT_REQUIRES_SIGNED_PARALLEL_NORMAL_COPIES`

Scientific ceiling:

```text
E113 DOES NOT YET EXCLUDE EVERY TARGET6 LIFT OF THE E112 ABSTRACT COVER.

IT IDENTIFIES THE EXACT INFORMATION LOST BETWEEN THE SIX-WITNESS SUPPORT
LAYER AND THE E105-E112 NORMAL/FLAT QUOTIENT.

THE CANONICAL ONE-VARIABLE-PER-PRISM-EDGE LIFT IS IMPOSSIBLE.

ANY GENUINE JOINT LIFT MUST SPLIT EACH PRISM NORMAL INTO DISTINCT TANNER
VARIABLES WITH THE SAME RESIDUAL NORMAL BUT OPPOSITE TARGET6-SUPPORT PARITY.

P_VS_NP = OPEN.
```

## 1. Restore the six-witness support bit

Fix six exact TARGET6 witnesses and let

```text
S_v subseteq {0,1,2,3,4,5}
```

be the labels of witnesses selecting Tanner variable (v).

E95 defines the raw8 parity candidate by

```text
e_v = 1 iff |S_v| is even.
```

E105 says that at one ordinary check the unique forbidden local kernel pattern is

```text
f_c = 111 xor e_c.
```

Therefore on every incidence ((c,v)),

```text
f_{c,v}
 = 1 xor e_v
 = |S_v| mod 2.
```

Hence:

```text
boxed:
THE E105 FORBIDDEN MARK IS A VARIABLE-GLOBAL SUPPORT-PARITY MARK.
```

It is not an arbitrary independent character bit attached to each check.

The same Tanner variable carries the same mark at all three checks containing it.

## 2. E112 uses opposite endpoint marks

In the E112 cubic cycle-space construction every prism edge (e=uv) carries one abstract normal

```text
g_e.
```

The forbidden character is defined by an orientation:

```text
phi_v(g_e)=1 iff e enters v.
```

Thus on every edge,

```text
boxed:
phi_u(g_e) xor phi_v(g_e)=1.
```

So the same abstract normal occurs in two check lines with opposite marks.

## 3. Edge-faithful lift is impossible

Suppose one Tanner variable (x_e) realized both occurrences of (g_e).

Its six-witness support (S_{x_e}) has one fixed parity.

By Section 1 its forbidden mark would therefore be identical at both endpoint checks.

But E112 requires opposite endpoint marks.

Contradiction.

Hence:

```text
boxed:
NO ONE-TANNER-VARIABLE-PER-E112-EDGE SUPPORT LIFT EXISTS.
```

This is a universal support identity, not a finite search result.

## 4. Signed-parallel normal pairs

Any joint lift must instead use at least two distinct Tanner variables for one E112 normal direction:

```text
x_e^0,
x_e^1
```

with

```text
g(x_e^0)=g(x_e^1)=g_e
```

on the residual E106 direction space, but

```text
|S_{x_e^0}| != |S_{x_e^1}| mod 2.
```

Call this a **signed-parallel normal pair**.

Thus every one of the 18 prism normals must split.

The 12 distinguished prism checks contain 36 normal incidences, and no pair of opposite-mark endpoint incidences can be one Tanner variable.

Therefore the prism part of any joint lift already needs at least

```text
36 distinct active Tanner variables.
```

Since each Tanner variable is cubic and occurs only once among those 12 distinguished checks, at least

```text
2*36 = 72
```

additional variable-check incidences must leave the distinguished prism-check set.

So an E112 lift cannot remain a 12-check closed gadget.

## 5. Complement-pair semantics

For residual repair direction (z), variables in a signed-parallel pair have the same kernel value:

```text
z(x_e^0)=z(x_e^1).
```

Their E95 bits are opposite because their support parities are opposite.

Therefore their final raw8-parity candidate bits remain complementary:

```text
(e xor z)(x_e^0)
xor
(e xor z)(x_e^1)
=1
```

for every residual repair direction.

Thus a signed-parallel normal pair behaves as one Boolean selector and its complement.

This is exactly the literal/anti-literal mechanism hidden in the E112 orientation proof.

## 6. Support semantics alone does lift

E113 next asks whether the full six-state partition condition itself already forbids the prism pattern.

It does not.

The checker constructs a closed Tanner geometry with

```text
36 variables,
36 checks,
degree 3 on both sides,
connected,
C4-free.
```

The 36 variables are one per prism half-edge occurrence.

At the 12 distinguished prism checks, supports are assigned so their cardinality parities are exactly the E112 orientation marks.

Twenty-four additional checks complete every variable to degree three.

At every one of all 36 checks, the three variable supports are pairwise disjoint and have union

```text
{0,1,2,3,4,5}.
```

Therefore each of the six labels gives an exact cover.

So:

```text
boxed:
FULL SIX-STATE CHECK-PARTITION SEMANTICS ALONE DOES NOT KILL THE PRISM MARK PATTERN.
```

## 7. But the support-only lift loses the E112 normal system

Compute the complete GF(2) zero-boundary kernel of the 36x36 support-only construction.

Its kernel dimension is five.

For each of the 18 prism edges, compare the coordinate normal of its two endpoint half-edge variables.

Frozen result:

```text
equal residual-normal pairs = 0 / 18.
```

So the construction is deliberately only a support lift.

It does not realize the E112 cycle-space normal identifications.

This separates two notions that must no longer be conflated:

```text
SUPPORT LIFT:
  six exact covers / partition of six labels at every check.

NORMAL LIFT:
  the E105-E112 residual coordinate functionals and affine-flat system.

JOINT LIFT:
  both simultaneously.
```

E113 proves that the first is realizable and the canonical edge-faithful joint lift is not.

## 8. Actual TARGET6 five-port graft

The support-only prism gadget contains variables of support

```text
{4,5}.
```

The E92 five-port TARGET6 geometry also contains variables with the same support.

Perform one support-preserving Tanner 2-switch between such variables.

The checker verifies the combined five-port cluster:

```text
54 internal variables,
55 internal checks,
connected,
C4-free,
ordinary variable/check degrees 3,
correct four check-side boundary degrees,
correct variable-side boundary x,
all six actual raw TARGET6 masks
  {1,2,4,19,21,22}
remain exactly feasible.
```

Therefore even the existence of the real six TARGET6 boundary witnesses does not forbid the prism **support-mark** pattern.

Again, however:

```text
equal prism endpoint residual normals = 0 / 18.
```

So this is not an E112 joint lift.

## 9. Algebraic meaning of signed-parallel pairs

Let (U) be the residual direction space after E106 propagation.

Two Tanner variables have the same residual normal iff

```text
z_u=z_v
for every z in U.
```

Equivalently the weight-two coordinate vector

```text
e_u+e_v
```

lies in the annihilator

```text
U^perp.
```

Thus every required E112 split produces a weight-two dual/series relation.

The remaining lift question is therefore not generic branchwidth.

It is:

```text
CAN A SQUARE-CUBIC-C4-FREE TARGET6 PARENT REALIZE
18 OPPOSITE-MARK SIGNED-PARALLEL NORMAL PAIRS
AFTER E106 PROPAGATION?
```

That is a far more rigid object.

## 10. Correct E114 target

```text
E114 SIGNED-PARALLEL / WEIGHT-2 DUAL KILLER

Assume a joint E112-style lift exists.

For every repeated normal g with opposite TARGET6 support parity:
  choose variables u,v with
      g_u=g_v,
      |S_u| != |S_v| mod2.

Then
  e_u+e_v in U^perp.

Exploit:
  * U is obtained only by E106 affine unit propagation from the actual
    zero-boundary Tanner kernel;
  * every original Tanner variable has degree three;
  * the Tanner graph is C4-free;
  * support parity is fixed by the six actual TARGET6 witnesses.

Goal:
  A. prove every such signed-parallel pair is reducible/series-contractible
     in polynomial time;
  B. show 18 prism-style pairs force a low-order separation already handled
     by E108-E111;
  C. show they force raw8 / another boundary state;
  D. or construct the first exact TARGET6/no-raw8 joint support+normal lift.
```

Scientific status:

```text
E113 = SUPPORT-LIFT / NORMAL-LIFT SEPARATION THEOREM.
E112 EDGE-FAITHFUL JOINT LIFT = IMPOSSIBLE.
ANY E112 JOINT LIFT => SIGNED-PARALLEL NORMAL PAIRS.
TARGET6 SUPPORT-MARK PATTERN ALONE = REALIZABLE.
SIGNED-PARALLEL JOINT LIFT = OPEN.
UNIVERSAL POLYNOMIAL EXACTONE SOLVER = NOT YET CONSTRUCTED.
P_VS_NP = OPEN.
```
