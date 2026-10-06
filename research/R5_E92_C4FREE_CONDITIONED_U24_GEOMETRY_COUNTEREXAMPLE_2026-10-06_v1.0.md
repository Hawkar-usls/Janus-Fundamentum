# R5 E92 — C4-Free Conditioned-U2,4 Geometry Counterexample

Date: 2026-10-06

Status:
`C4FREE_CONDITIONED_U24_EXISTS_AT_T6__GEOMETRY_ONLY_EXCLUSION_FALSIFIED__RAW_PARENT_NOT_DELTA`

Scientific ceiling:

```text
E92 DOES NOT PROVIDE A NONBINARY DELTA-MATROID INTERFACE.

IT DOES PROVIDE AN EXPLICIT FULL SQUARE-CUBIC-LINEAR / C4-FREE SOURCE
WITH A CONDITIONED FOUR-PORT EXACT RELATION EQUAL TO A TWIST OF U_{2,4}.

THE RAW FIVE-PORT PARENT RELATION FAILS SYMMETRIC EXCHANGE.

THEREFORE:
  SOURCE LINEARITY / C4-FREENESS ALONE CANNOT EXCLUDE CONDITIONED U2,4.
  ANY VALID UNIVERSAL BINARY THEOREM MUST USE THE PARENT DELTA AXIOM.

P_VS_NP = OPEN.
```

## 1. Why E92 was necessary

E85 reduced any hypothetical nonbinary exact Tanner delta interface to a
conditioned four-port U2,4 witness.  E86-E91 then attacked that conditioned
geometry directly.

The danger was logical asymmetry:

```text
nonbinary delta parent
    => conditioned U2,4 witness
```

does not imply

```text
conditioned U2,4 witness
    => nonbinary delta parent.
```

E92 finds the first explicit witness separating those two statements inside the
actual square-cubic-linear/C4-free source class.

This prevents the proof search from trying to establish the false theorem
"conditioned U2,4 is impossible in C4-free geometry."

## 2. Full source

E92 freezes a 24-check / 24-variable Tanner source.

Every variable has degree 3.
Every check has degree 3.
The Tanner graph is connected.
Any two variables share at most one check, so there is no Tanner C4.

Thus the source is square, cubic and linear in exactly the RXC3 sense used by
the E12 hard route.

The 17 ordinary cluster variables have check triples

```text
(0,2,18)
(0,6,13)
(1,9,14)
(1,10,16)
(2,3,4)
(3,5,12)
(3,9,15)
(4,7,11)
(4,8,14)
(5,6,7)
(5,11,17)
(6,10,15)
(7,12,18)
(8,9,10)
(8,13,16)
(11,12,13)
(14,15,16).
```

Variable x has full source neighbourhood

```text
{17,18,19}.
```

The induced cluster uses checks 0..18 and variables consisting of those 17
cubic variables plus x.  Its five boundary incidences are:

```text
check-side free ports at checks 0,1,2,17;
variable-side free port of x through outside check 19.
```

The remaining outside vertices complete the graph to a full cubic C4-free
24x24 source.

## 3. Exact raw five-port relation

Order the boundary bits as

```text
A, B, C, E, V
```

where E is the check-side port at check 17 and V is the variable-side port of
x.

Exhaustive enumeration of all 2^18 internal variable assignments gives exactly

```text
D_raw = {1,2,4,8,19,21,22}.
```

No heuristic or SAT oracle is involved in the replay.

## 4. Conditioning produces U2,4

Pin

```text
E=0
```

and project E away.

The surviving four-port family is

```text
{1,2,4,11,13,14}.
```

Twist the surviving variable-side coordinate V.  The result is

```text
{3,5,6,9,10,12},
```

which is precisely all six 2-subsets of a four-element ground set:

```text
boxed:
U_{2,4}.
```

So conditioned U2,4 is genuinely realizable by a C4-free square-cubic-linear
source.

## 5. Why this does not refute E83's binary-delta conjecture

The raw parent relation must itself be a delta-matroid before E83 can turn it
into a canonical matroid.

For D_raw, symmetric exchange fails.  The checker freezes the exact witness

```text
X = 19,
Y = 8,
exchange element = 3.
```

Hence

```text
boxed:
D_raw is NOT a delta-matroid.
```

So E92 is not a nonbinary delta interface.

It is instead a firewall showing that parent delta structure is essential.

## 6. Interaction with E90-E91

One choice of the three v=1 exact covers has near-class shared-savings

```text
sigma = 4.
```

Thus the example also explains why the low-sigma exclusions E90 and the
sigma=2 local normal form E91 do not close the entire conditioned-geometry
problem.

Those theorems remain valid; their intended universal extrapolation is what
must stop.

## 7. Correct next theorem target

The representation question is no longer:

```text
Can C4-free geometry realize conditioned U2,4?
```

E92 answers YES.

The correct question is:

```text
Can a C4-free square-cubic-linear exact boundary relation D
simultaneously satisfy:

  1. D is a delta-matroid;
  2. the canonical matroid D*P is nonbinary;
  3. some deletion/contraction exposes U2,4?
```

That parent-delta condition is the missing force.

## 8. Immediate E93 reduction in the p=1,h=1 x-neighbour-hole lane

When the conditioned-away check-side port E is incident to x itself, primitive
ExactOne semantics forbids

```text
E=1 and V=1
```

simultaneously.

The signed E82 counting identity then leaves only two possible E=1 raw boundary
patterns:

```text
8  = E only,
15 = A+B+C+E.
```

If the raw parent is delta, E83 says its canonical twist is an ordinary
matroid.  Because the E=0 deletion slice is U2,4, the parent canonical matroid
must have rank 2 and E is not a coloop.

The raw state 15 becomes a 5-element canonical set after twisting V, so it
cannot be a rank-2 basis.

The raw state 8 becomes the canonical basis {E,V}.  But U2,4 plus only that
single additional basis violates ordinary basis exchange.

Therefore a delta parent in this orientation can contain neither 15 nor 8.

So:

```text
boxed:
A DELTA PARENT WITH AN x-NEIGHBOUR CONDITIONED PORT MUST MAKE E A LOOP
IN THE CANONICAL MATROID.
```

Equivalently, the exact raw family would have to be only the six E=0 states.

E92 is a one-state near miss: it has exactly those six states plus state 8.

This is the next sharp frontier.

## 9. Companion replay

```text
experiments/r5_e92_c4free_conditioned_u24_geometry_counterexample.py
```

Frozen assertions:

```text
full source = 24x24 square/cubic/connected/C4-free;
raw five-port relation = {1,2,4,8,19,21,22};
condition E=0 -> {1,2,4,11,13,14};
canonical conditioned matroid = U2,4;
raw parent symmetric-exchange failure = (19,8,3);
one v=1 near-class realization has sigma=4.
```

Scientific state:

```text
E92 = CONDITIONED-GEOMETRY COUNTEREXAMPLE.

C4FREE_CONDITIONED_U24 = REALIZABLE.
C4FREE_NONBINARY_DELTA_PARENT = STILL OPEN.
GEOMETRY_ONLY_EXCLUSION = FALSIFIED.
PARENT_DELTA_CLOSURE = NEW FRONTIER.

STATIC_GLOBAL_DELTA_VERTEX_PARTITION = FALSIFIED BY E81.
RECURSIVE_REPRESENTED_DECOMPOSITION = OPEN.
P_VS_NP = OPEN.
```
