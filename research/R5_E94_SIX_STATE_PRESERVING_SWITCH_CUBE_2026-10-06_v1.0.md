# R5 E94 — Six-State-Preserving C4-Free Switch Cube

Date: 2026-10-06

Status:
`E92_TARGET6_LOCAL_COMPONENT_IS_Q6__EXTRA_STATE8_INVARIANT`

Scientific ceiling:

```text
E94 DOES NOT PROVE THAT THE EXACT SIX-STATE DELTA PARENT IS GLOBALLY
IMPOSSIBLE.

IT EXHAUSTS THE ENTIRE E92-CONNECTED COMPONENT UNDER ELEMENTARY
DEGREE-PRESERVING C4-FREE 2-SWITCHES THAT PRESERVE ALL SIX REQUIRED
PARENT STATES.

THAT COMPONENT HAS EXACTLY 64 GEOMETRIES AND EVERY ONE RETAINS THE
SAME EXTRA RAW STATE 8, HENCE EVERY ONE FAILS THE E93 DELTA-PARENT GATE.

A DISCONNECTED DEGREE-SEQUENCE COMPONENT COULD STILL EXIST.

P_VS_NP = OPEN.
```

## 1. E93 target

For the x-neighbour-hole orientation, E93 proved that a delta parent whose
E=0 conditioning is the p=1 U2,4 twist cannot contain any E=1 feasible state.

Therefore the only allowed raw five-port family is exactly

```text
TARGET6 = {1,2,4,19,21,22}.
```

E92 gives an explicit square-cubic-linear/C4-free full source whose relevant
19-check/18-variable cluster realizes

```text
RAW7 = TARGET6 union {8}.
```

The sole extra state 8 is exactly the state forbidden by parent delta exchange.

## 2. Elementary source-preserving switch

Take two cubic cluster variables with triples X,Y and choose

```text
a in X-Y,
b in Y-X.
```

Replace

```text
X -> X-a+b,
Y -> Y-b+a.
```

when both resulting sets remain triples and the whole variable family remains
linear, i.e. no two variables share more than one check.

This operation preserves:

```text
* every cubic variable degree;
* every check degree;
* the boundary degree pattern;
* square/cubic source bookkeeping;
* Tanner C4-freeness when the local pair test passes.
```

It is therefore the smallest natural local trade on the E92 residual
incidence geometry.

## 3. Target-preserving component

E94 starts at the exact E92 cluster and explores every valid one-switch
neighbour.

A neighbour is retained only if every state in

```text
TARGET6
```

remains feasible.

The exploration is repeated recursively until no new target-preserving
geometry remains.

No heuristic pruning or random sampling is used.

## 4. Exact result

The complete connected component has size

```text
64.
```

Its BFS distance layers from E92 are

```text
distance 0 :  1
distance 1 :  6
distance 2 : 15
distance 3 : 20
distance 4 : 15
distance 5 :  6
distance 6 :  1
```

which are exactly the binomial coefficients

```text
C(6,0),...,C(6,6).
```

Thus the component has the layer profile of the Boolean cube Q6.

The directed target-preserving switch count is

```text
64 * 6 = 384.
```

## 5. Raw-family invariant

For every one of the 64 geometries, the complete five-port exact boundary
family is recomputed from ExactOne/Equality semantics.

Every one gives exactly

```text
{1,2,4,8,19,21,22}.
```

In particular the forbidden E=1 state

```text
8
```

never disappears.

Therefore:

```text
boxed:
Within the complete E92 target-preserving local trade component,
TARGET6 => state8.
```

Combined with E93, **no geometry in this entire 64-state component can be a
delta parent**.

## 6. What this tells us

The E92 near miss is not isolated.  It sits inside a rigid 64-member local
trade family, and all local trades preserving the six desired states also
preserve the exact same seventh state.

This strongly suggests that state8 may be enforced by a structural invariant
of the six exact covers rather than by the particular E92 labeling.

But E94 deliberately does not promote that suggestion to theorem status.

## 7. Remaining universal target

The correct successor is:

```text
E95 GLOBAL TARGET6 -> STATE8 KILLER

Either prove that every C4-free 19x18 p=1,h=1 parent geometry realizing
TARGET6 is switch-equivalent (through TARGET6-preserving moves) to E92,
or find a disconnected component.

Equivalent structural route:
derive state8 directly from the six target exact covers, without using
connectivity of the switch graph.
```

A proof of

```text
TARGET6 => state8
```

for all C4-free cubic geometries in this orientation would combine with E93
to eliminate the x-neighbour-hole parent-delta lane universally.

## 8. Companion replay

```text
experiments/r5_e94_six_state_preserving_switch_cube.py
```

Frozen assertions:

```text
component size = 64
BFS layers = 1,6,15,20,15,6,1
directed preserving switches = 384
full raw family of every state = {1,2,4,8,19,21,22}
```

Scientific status:

```text
E94 = EXACT LOCAL-COMPONENT FIREWALL.
E92_COMPONENT_DELTA_PARENT = EXCLUDED.
GLOBAL_TARGET6_PARENT = OPEN.
P_VS_NP = OPEN.
```
