# R5 E95 — Even-Occurrence State-8 Defect Reduction

Date: 2026-10-06

Status:
`TARGET6_ALWAYS_GIVES_CANONICAL_PARITY_STATE8_CANDIDATE__FAILURE_LOCALIZES_TO_TRIPLE_EVEN_CHECKS`

Scientific ceiling:

```text
E95 DOES NOT YET PROVE THAT RAW STATE 8 MUST EXIST.

IT PROVES THAT ANY SIX-STATE E93 PARENT HAS A CANONICAL CANDIDATE ASSIGNMENT
WHICH ALREADY SATISFIES EVERY BOUNDARY CHECK EXACTLY AND EVERY ORDINARY CHECK
MODULO 2.

THE ONLY POSSIBLE FAILURE IS A LOCAL ORDINARY CHECK WITH THREE SELECTED
INCIDENT VARIABLES.

SUCH A CHECK HAS ONE OF ONLY THREE OCCURRENCE TYPES:
  (0,0,6), (0,2,4), (2,2,2).

P_VS_NP = OPEN.
```

## 1. Six required parent states

E93 reduced the x-neighbour-hole delta-parent target to the exact raw family

```text
TARGET6 = {1,2,4,19,21,22}
```

with boundary order

```text
A,B,C,E,V.
```

The states split into:

```text
V=0:
  X_A = 1
  X_B = 2
  X_C = 4

V=1:
  Q_AB = 19
  Q_AC = 21
  Q_BC = 22.
```

In every one of these six states E=0.

Choose **one arbitrary internal exact-cover witness** for each of the six
states.  The argument below does not require uniqueness.

## 2. Occurrence counts

For every active variable j define

```text
w_j = number of the six chosen witnesses containing j.
```

Now define a new candidate assignment

```text
e_j = 1  iff  w_j is even.
```

Equivalently over GF(2),

```text
e_j = 1 + (w_j mod 2).
```

This is the complement of the XOR of the six chosen witness assignments.

## 3. Checkwise parity identity

Let c be an active ExactOne check and let d_c be its internal active degree.

Across the six target witnesses, let kappa_c be the number of states in which
c must be internally covered.

Because each chosen witness is exact,

```text
sum_{j incident c} w_j = kappa_c.
```

Therefore

```text
sum_{j incident c} e_j
  == d_c + kappa_c   (mod 2).
```

This one identity gives the entire E95 reduction.

## 4. Survivor checks A,B,C are solved exactly

Each of A,B,C has one raw boundary port, hence internal degree

```text
d=2.
```

Each is internally covered in exactly three of the six target states:

```text
kappa=3.
```

Thus

```text
sum e_j == 2+3 == 1 (mod 2).
```

There are only two internal incidences, so the sum cannot be 3.

Hence:

```text
boxed:
e selects exactly one internal variable at each of A,B,C.
```

This is exactly what raw state 8 needs, because state 8 has A=B=C=0.

## 5. The conditioned check E is solved exactly

The raw parent has one free check-side port E.  Its two internal neighbours are:

```text
x = special variable carrying V,
y = the other internal variable at check E.
```

In the three V=1 target states, x=1 and ExactOne forces y=0.

In the three V=0 target states, x=0 and E=0 forces y=1.

Therefore

```text
w_x = 3,
w_y = 3.
```

Both are odd, so

```text
e_x=e_y=0.
```

Hence check E receives zero internal selected incidences under e.  Its required
boundary bit is therefore E=1.

Also e_x=0 gives

```text
V=0.
```

So the boundary values of e are already forced to be exactly raw state 8:

```text
A=B=C=0,
E=1,
V=0.
```

provided the ordinary checks satisfy ExactOne.

## 6. Ordinary checks have only one possible defect

Every other active check is fully internal cubic:

```text
d=3.
```

It is internally covered in all six target witnesses:

```text
kappa=6.
```

Thus

```text
sum e_j == 3+6 == 1 (mod 2).
```

Since there are three incident variables, the actual integer sum is only

```text
1 or 3.
```

Therefore:

```text
boxed:
Every ordinary check is either already ExactOne-correct,
or all three incident variables are selected by e.
```

Call the second case a **triple-even defect check**.

Hence:

```text
boxed:
If there are no triple-even defects, e is an exact witness for raw state 8.
```

By E93 that would contradict the existence of a delta parent.

Thus every hypothetical exact-six-state delta parent must force at least one
triple-even defect for **every** choice of one witness for each target state.

## 7. Defect support classification

At an ordinary check the three incident variables partition the six target
states: in every target witness exactly one of the three is selected.

At a defect check all three occurrence counts are even.

Three nonnegative even integers summing to six have, up to order, only the
following possibilities:

```text
(0,0,6)
(0,2,4)
(2,2,2).
```

So the universal parent-delta obstruction has been reduced from an arbitrary
C4-free cubic geometry to only three local cover-incidence types.

## 8. E92 replay

For the E92 near-miss geometry, choose deterministic witnesses for the six
TARGET6 states and compute all occurrence counts.

The even-occurrence assignment has **no triple-even defect**.

It is therefore automatically an exact assignment for boundary mask

```text
8.
```

This recovers E92's unique extra state by the universal E95 construction,
rather than by brute-force boundary enumeration.

That explains why the extra state survives the entire E94 local switch cube:
the six required covers keep producing a defect-free even-occurrence
candidate.

## 9. New frontier

The representation-side x-neighbour lane is now:

```text
E93:
  delta parent => raw family must be exactly TARGET6.

E94:
  the full 64-state E92 local trade component cannot remove raw8.

E95:
  every TARGET6 geometry has a canonical parity candidate for raw8;
  failure of raw8 can occur only through triple-even defect checks of type
  (0,0,6), (0,2,4), or (2,2,2).
```

The next killer-test is therefore local and exact:

```text
E96 TRIPLE-EVEN DEFECT KILLER

Either:
  1. prove that witness choices can always be made so that no defect remains;
or
  2. show each of the three defect types forces a Tanner C4 / reducible trade /
     additional forbidden boundary state;
or
  3. construct the first genuine C4-free exact-TARGET6 parent.
```

A universal defect elimination would imply

```text
TARGET6 => raw8
```

and, with E93, close this conditioned-minor orientation.

## 10. Companion replay

```text
experiments/r5_e95_even_occurrence_state8_defect_reduction.py
```

Scientific status:

```text
E95 = UNIVERSAL PARITY-TO-LOCAL-DEFECT REDUCTION.
GLOBAL_TARGET6_PARENT = OPEN.
P_VS_NP = OPEN.
```
