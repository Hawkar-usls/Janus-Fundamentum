# R5 E93 — Parent-Delta Loop Reduction for the x-Neighbour-Hole Lane

Date: 2026-10-06

Status:
`DELTA_PARENT_FORCES_CONDITIONED_PORT_TO_BE_A_LOOP__RAW_PARENT_MUST_BE_EXACT_SIX_STATE_FAMILY`

Scientific ceiling:

```text
E93 DOES NOT YET EXCLUDE A C4-FREE NONBINARY DELTA PARENT.

IT PROVES THAT IN THE p=1,h=1 SUBCASE WHERE THE CONDITIONED CHECK PORT E
IS INCIDENT TO THE SPECIAL BOUNDARY VARIABLE x, ANY DELTA PARENT HAS ONLY
ONE POSSIBLE MATROIDAL FORM:

    E IS A LOOP.

EQUIVALENTLY, THE RAW FIVE-PORT EXACT RELATION MUST CONTAIN ONLY THE SIX
E=0 U2,4-TWIST STATES AND NO E=1 STATE.

E92 MISSES THIS BY EXACTLY ONE EXTRA STATE, RAW MASK 8.

P_VS_NP = OPEN.
```

## 1. Boundary convention

Use five raw boundary coordinates

```text
A, B, C, E, V
```

with bit positions 0,1,2,3,4.

Here:

```text
A,B,C = the three surviving check-side ports,
E     = the conditioned check-side port,
V     = the variable-side port of the special variable x.
```

This E93 lane assumes E is attached to one of the two internal checks incident
to x.

Conditioning

```text
E=0
```

must produce the p=1 four-port U2,4 twist. In raw five-bit coordinates the six
E=0 states are

```text
{1,2,4,19,21,22}.
```

After twisting V, these become all six 2-subsets of the four survivor
coordinates A,B,C,V.

## 2. Primitive semantic restriction

At the check carrying E, the special variable x is also incident.

Therefore

```text
E=1 and V=1
```

is impossible: the ExactOne check would receive two selected incidences.

So every feasible E=1 state must have

```text
V=0.
```

## 3. Signed mod-3 restriction

For p=1,h=1 E85 gives

```text
a=3t+1
```

active checks.

Let k be the number of selected survivor check ports among A,B,C in an E=1,
V=0 state.

The signed boundary quantity is

```text
phi = 0 - (1+k) = -(1+k).
```

The exact primitive identity gives

```text
phi = 3|Y|-a
    == -1 (mod 3).
```

Hence

```text
k == 0 (mod 3).
```

Since k is one of 0,1,2,3, only

```text
k=0 or k=3
```

are possible.

Thus every raw E=1 state is one of only two masks:

```text
8  = E,
15 = A+B+C+E.
```

No source-linearity assumption is needed for this reduction.

## 4. Bring back the parent delta axiom

Assume the raw five-port relation D is a delta-matroid.

E83 then says

```text
M = D * {V}
```

is an ordinary matroid.

The E=0 slice of M is exactly U2,4.

Because M has bases avoiding E, E is not a coloop. Therefore deletion by E
preserves rank:

```text
rank(M)=rank(M\E)=2.
```

Every basis of M must consequently have size two.

## 5. Raw state 15 is impossible

Twisting V in raw mask 15 gives

```text
15 xor 16 = 31.
```

Mask 31 is the full five-element ground set and has cardinality five.

It cannot be a basis of a rank-two matroid.

Therefore:

```text
15 notin D.
```

## 6. Raw state 8 is also impossible under delta exchange

Twisting V in raw mask 8 gives

```text
8 xor 16 = 24,
```

the two-element set {E,V}.

So cardinality alone does not exclude it.

But Sections 2-3 proved that there can be no other E-containing rank-two basis:
all alternatives would require a raw E=1,V=1 state and are semantically
impossible.

Hence if 8 were feasible, the canonical basis family would be

```text
U2,4 bases
plus the single extra basis {E,V}.
```

This violates ordinary matroid basis exchange.

For example, compare

```text
{E,V}
and
{A,B}.
```

Exchange V out of {E,V}. Matroid basis exchange requires either

```text
{E,A}
or
{E,B}
```

to be a basis. Neither is semantically possible.

Therefore:

```text
8 notin D.
```

## 7. Exact parent classification in this lane

There are no E=1 states at all.

So E is a loop of the canonical matroid M and the raw relation is exactly

```text
boxed:
D = {1,2,4,19,21,22}.
```

After twisting V:

```text
M = U2,4 plus a loop E.
```

This is a valid nonbinary matroid.

Therefore the entire x-neighbour-hole representation frontier is now one
sharp realization question:

```text
CAN A C4-FREE SQUARE-CUBIC-LINEAR TANNER CLUSTER HAVE
EXACT RAW FIVE-PORT RELATION

    {1,2,4,19,21,22} ?
```

If yes, the universal binary-interface conjecture is false.

If no, the x-neighbour-hole subcase of the conditioned-U24 minor route is
closed for every t.

## 8. E92 is an exact one-state near miss

E92 constructs a full 24x24 square-cubic-linear C4-free source whose raw
five-port family is

```text
{1,2,4,8,19,21,22}.
```

So it realizes the required six states and exactly one forbidden state:

```text
8.
```

The symmetric-exchange failure in E92 is precisely the matroid-exchange defect
identified in Section 6.

This is strong evidence that E93 has isolated the correct obstruction rather
than merely changing notation.

It is not a proof that state 8 is always forced.

## 9. Next killer-test — E94

```text
LOOP-STATE REALIZATION KILLER

Assume the six E=0 states exist in C4-free cubic geometry.

Prove one of:

A. raw state 8 is necessarily feasible.
   Then E93 says a delta parent is impossible.

B. construct a C4-free source with raw family exactly
       {1,2,4,19,21,22}.
   Then the binary-representation conjecture is refuted by a genuine
   nonbinary delta interface.

Use E92 as the first near-miss regression.

Do NOT continue a geometry-only search for arbitrary conditioned U2,4;
E92 already falsifies that theorem.
```

## 10. Companion replay

```text
experiments/r5_e93_parent_delta_xneighbor_loop_reduction.py
```

Frozen assertions:

```text
semantically possible E=1 states = {8,15};
raw15 is impossible in a rank-2 canonical parent;
raw8 as the sole E-containing basis violates basis exchange;
therefore every delta parent in this lane has E as a loop.
```

Scientific state:

```text
E93 = EXACT PARENT-DELTA CLASSIFICATION FOR THE x-NEIGHBOUR-HOLE LANE.

DELTA_PARENT_FORM = U2,4 + LOOP.
E92_NEAR_MISS = U2,4 + ONE_ILLEGAL_EXTRA_BASIS.
LOOP_STATE_REALIZATION = OPEN.

LINEAR_RXC3_NONBINARY_DELTA_PARENT = OPEN.
RECURSIVE_REPRESENTED_DECOMPOSITION = OPEN.
P_VS_NP = OPEN.
```
