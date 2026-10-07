# R5 E104 — Pairwise-Minimal Witness Phase-Clash Firewall

Date: 2026-10-07

Status:
`MINIMALITY_ONLY_PHASE_CLASH_KILLER_FALSIFIED__NO_RAW8_IS_THE_MISSING FORCE`

Scientific ceiling:

```text
E104 DOES NOT PROVE TARGET6 => RAW8.

IT PROVES THAT EVEN GLOBAL MINIMUM OPPOSITE-PAIR WITNESS CHOICES, TOGETHER
WITH E98 2+2 RECTANGLE NORMAL FORMS, DO NOT BY THEMSELVES ELIMINATE THE
SMALLEST E102 H_a^0/H_a^1 HOLONOMY CLASH.

THE EXPLICIT COUNTEREXAMPLE STILL HAS RAW8 WITNESSES.
THEREFORE THE NEXT VALID UNIVERSAL KILLER MUST USE EXACT-PARENT / NO-RAW8
SEMANTICS, NOT GEOMETRY OR WITNESS MINIMALITY ALONE.

P_VS_NP = OPEN.
```

## 1. Why E104 was necessary

E103 killed the geometry-only hope by constructing a connected C4-free cubic
six-cover phase clash.

A natural repair was:

```text
choose each opposite TARGET6 witness pair at minimum symmetric-difference
distance and use E98 to forbid internal switch noise.
```

E104 tests that stronger premise exactly.

The three opposite pairs are disjoint and cover all six TARGET6 states:

```text
(X_A,Q_BC),
(X_B,Q_AC),
(X_C,Q_AB).
```

Therefore each pair can be globally minimized independently.

## 2. Nonzero-support phase gadget

Use direction

```text
a=(0,1).
```

The two phases are the d-vectors

```text
001 and 110.
```

E104 uses three Pappus blocks with support partitions

```text
H_a^0:
  empty | {3} | {0,1,2,4,5}

neutral:
  {0,1,2} | {3} | {4,5}

H_a^1:
  empty | {4,5} | {0,1,2,3}.
```

The supports {3} and {4,5} both occur in the real E92 TARGET6 witness
spectrum and have nonzero E102 color.

Two support-preserving switches join the three Pappus blocks.

Then two additional support-preserving switches graft the gadget directly into
the E92 five-port cluster through:

```text
support {3}
support {4,5}.
```

Unlike E103's first empty-support graft, these switches merge the phase gadget
into the actual opposite-pair exchange geometry.

## 3. Combined exact geometry

The checker verifies:

```text
45 internal variables,
46 internal checks,
four check-side boundary ports A,B,C,E,
one variable-side port V,
connected,
C4-free,
all ordinary variables cubic,
all ordinary checks cubic,
all six TARGET6 masks feasible.
```

## 4. Full exact witness enumeration

A deterministic Algorithm-X recursion enumerates all exact internal witnesses
for the six TARGET6 states and raw8.

Counts are:

```text
raw1  = 4
raw2  = 4
raw4  = 4
raw19 = 2
raw21 = 4
raw22 = 2
raw8  = 4.
```

This is exhaustive for the combined cluster.

## 5. Global minimum opposite-pair distances

For every witness pair in the exact fibers, E104 computes the full internal
symmetric-difference distance.

For the three opposite pairs:

```text
(1,22):  minimum distance = 24
(2,21):  minimum distance = 24
(4,19):  minimum distance = 24.
```

The six support-labelled witnesses used to define the phase structure attain
all three global minima.

Thus the phase clash is present under genuine pairwise-global-minimum witness
selection, not merely under an arbitrary bad choice.

## 6. E98 terminal-component normal form already holds

For the chosen minimum pairs, the three exchange graphs have no terminal-free
component.

Exact component structure:

```text
G0:
  size 6  terminals {A,B}
  size 18 terminals {C,V}

G1:
  size 6  terminals {A,B}
  size 18 terminals {C,V}

G2:
  size 18 terminals {A,V}
  size 6  terminals {B,C}.
```

So all three opposite exchange graphs are already in the E98 2+2 rectangle
normal form.

No further terminal-free same-boundary switch exists for these chosen pairs.

## 7. Bad holonomy still survives

The nonzero E102 colors form a connected component containing the phase
gadget.

Within that component the gadget contributes

```text
9 checks with Good=H_(0,1)^0,
9 unrestricted checks,
9 checks with Good=H_(0,1)^1.
```

Therefore the component-wide intersection is empty.

So:

```text
boxed:
PAIRWISE GLOBAL MINIMUM OPPOSITE WITNESSES
+ C4-FREE
+ CUBIC
+ ACTUAL TARGET6 WITNESSES
+ E98 2+2 RECTANGLES
DO NOT FORCE HOLONOMY CONSISTENCY.
```

## 8. What the example also contains

The same cluster has exactly

```text
4 raw8 witnesses.
```

This is the key positive clue.

The phase clash can coexist with minimum witnesses and rectangle structure,
but in this construction it cannot coexist with absence of raw8.

Hence the relevant counterexample class is now narrower:

```text
exact TARGET6 parent
+ no raw8
+ pairwise-minimal witnesses
+ bad holonomy.
```

E104 shows that the first three structural ingredients without no-raw8 are not
enough.

## 9. Correct E105 target

The next step should directly exploit the missing seventh boundary state.

```text
E105 NO-RAW8 HOLONOMY KILLER

Assume the exact parent boundary relation is TARGET6 and raw8 is infeasible.

Choose the three opposite witness pairs at global minimum distance.

For a bad holonomy component, prove that its signed phase clash plus E98
rectangle transports necessarily constructs an exact raw8 witness.

Equivalent formulation:
  show that every pairwise-minimal TARGET6 witness tuple with empty component
  Good-intersection has an exact state8 solution outside the four E95/E102
  affine candidates.

If false, freeze the first exact TARGET6/no-raw8 minimal holonomy obstruction.
```

This is now the first proof target that uses the hypothesis every previous
firewall showed to be essential.

Scientific status:

```text
E104 = PAIRWISE-MINIMALITY FIREWALL.
MINIMALITY_ONLY_PHASE_CLASH_KILLER = FALSE.
NO_RAW8_PHASE_CLASH_KILLER = OPEN.
P_VS_NP = OPEN.
```
