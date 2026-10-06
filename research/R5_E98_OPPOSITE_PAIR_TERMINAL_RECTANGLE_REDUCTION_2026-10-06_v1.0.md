# R5 E98 — Opposite-Pair Terminal-Component and Rectangle Reduction

Date: 2026-10-06

Status:
`MINIMAL_OPPOSITE_EXCHANGE_GRAPH_HAS_4_OR_2PLUS2_TERMINALS__DOUBLE_RECTANGLE_COLLAPSES_DEFECTS_TO_RIGID_ONLY`

Scientific ceiling:

```text
E98 DOES NOT YET PROVE TARGET6 => RAW STATE 8.

IT PROVES A UNIVERSAL TERMINAL-COMPONENT NORMAL FORM FOR MINIMAL OPPOSITE
TARGET6 EXCHANGE GRAPHS AND SHOWS THAT TWO COHERENT INDEPENDENT 2+2
DECOMPOSITIONS ZERO BOTH TARGET-DERIVED KERNEL CORRECTIONS.

IN THAT DOUBLE-RECTANGLE REGIME, THE ONLY POSSIBLE E95 DEFECTS ARE THE FIVE
RIGID OPPOSITE-PAIR COARSENINGS.

P_VS_NP = OPEN.
```

## 1. Minimal opposite witness pairs

Fix one of the three opposite TARGET6 pairs

```text
(X_A,Q_BC), (X_B,Q_AC), (X_C,Q_AB).
```

Choose exact internal witnesses for the pair minimizing the size of their
symmetric difference.

Build the E97 bipartite exchange graph. Its two variable sides are the
variables selected only by the first witness and only by the second witness.
Ordinary differing checks are graph edges. A,B,C,V are terminals.

Each variable vertex has degree three when terminal half-edges are counted.

## 2. No terminal-free component survives minimality

Suppose a connected component has no boundary terminal.

Flip the two witness sides on that component only. Every internal ExactOne
check remains exactly covered, and no boundary bit changes.

Thus the modified first witness realizes the same boundary state but agrees
with the second witness on the entire component. This strictly reduces the
symmetric difference.

Contradiction.

Therefore a minimum-difference opposite witness pair has no terminal-free
exchange component.

## 3. Every component is side-balanced

Let a connected component contain

```text
L = number of first-only variable vertices,
R = number of second-only variable vertices,
e = number of ordinary/internal exchange edges,
q_L = number of terminals attached to the first side,
q_R = number attached to the second side.
```

Degree counting gives

```text
3L = e + q_L,
3R = e + q_R.
```

Therefore

```text
3(L-R)=q_L-q_R.
```

For an opposite TARGET6 pair the four terminals split globally as two on each
side. Hence

```text
q_L,q_R in {0,1,2}.
```

The only difference divisible by three is zero:

```text
boxed:
q_L=q_R
```

in every connected component.

Combined with Section 2, each component has either

```text
q_L=q_R=1  -> two terminals,
q_L=q_R=2  -> all four terminals.
```

Thus the complete minimal exchange graph is exactly one of:

```text
A. one 4-terminal component;
B. two 2-terminal components.
```

No 1+3 or terminal-free decomposition is possible.

## 4. Edge congruence inside components

From

```text
e=3L-q_L
```

we get

```text
two-terminal component : e == 2 (mod 3),
four-terminal component: e == 1 (mod 3).
```

The total opposite-pair exchange graph always has internal exchange-edge count
1 modulo 3. Removing the distinguished E-edge recovers E97's ordinary-edge
multiple-of-three invariant.

## 5. TARGET6 is exactly closed under every legal 2-terminal flip

For each opposite pair, one witness has two of A,B,C,V terminals on each side.

A 2-terminal component must contain one terminal from each side. There are
exactly four such cross-side pairs.

Flip one component.

The result is a new exact witness whose boundary differs on exactly those two
terminals.

A direct finite check of the six TARGET6 masks shows:

```text
boxed:
all four legal cross-side terminal flips land on the four other TARGET6 states.
```

The forbidden perfect matching is exactly the same-side terminal pairing,
which Section 3 already excludes.

Hence a 2+2 decomposition does not generate an unwanted seventh boundary
state. It generates an exact TARGET6 rectangle.

## 6. Rectangle identity

Let opposite witnesses be X and Y and let the two exchange components be C1,C2.

The intermediate witnesses are

```text
Z1 = X xor C1,
Z2 = X xor C2,
Y  = X xor C1 xor C2.
```

Therefore

```text
boxed:
X xor Y xor Z1 xor Z2 = 0.
```

The four boundary states are one opposite pair plus one of the other opposite
pairs.

Thus one E96 target-derived kernel correction vanishes exactly.

This gives a geometric meaning to the algebraic event h_i=0.

## 7. Coherent double rectangle

Suppose the six TARGET6 witnesses can be chosen coherently so that two
independent rectangle identities hold.

Then both independent target-derived corrections vanish:

```text
h1=h2=0.
```

Equivalently the three opposite-pair symmetric-difference indicator vectors are
identical.

At any ordinary check, each incident variable therefore has one of only two
opposite-pair split vectors:

```text
000 or 111.
```

Now impose the E95 defect condition: all three incident support blocks have
even cardinality.

Exhausting all 31 E96 even partitions leaves exactly five compatible
partitions.

They are precisely the five rigid coarsenings of

```text
{X_A,Q_BC},
{X_B,Q_AC},
{X_C,Q_AB}.
```

Therefore:

```text
boxed:
COHERENT DOUBLE RECTANGLE + NO RIGID DEFECT
=> E95 PARITY CANDIDATE IS EXACT
=> RAW STATE 8 EXISTS.
```

By E93, that is incompatible with an exact TARGET6 delta parent.

## 8. New representation frontier

A genuine no-state8 TARGET6 parent must therefore satisfy at least one of:

```text
1. a rigid opposite-pair defect exists; or

2. the opposite exchange graphs obstruct any coherent choice of two
   independent 2+2 rectangles.
```

This is substantially narrower than E96's original local signature statement.

The next experiment should attack these two residual mechanisms separately.

### E99-A — rigid defect reduction

Use the five rigid support coarsenings

```text
(6,0,0),
three labelled (4,2,0) cases,
(2,2,2)
```

and propagate their incident variables through the other two checks of each
cubic variable under C4-freeness.

Target: prove a removable common exact-cover block, repeated pair, or raw8.

### E99-B — rectangle holonomy

Treat each 2-terminal exchange component as a basis-exchange edge between
TARGET6 states.

Target: prove that absence of a coherent double rectangle creates a nontrivial
holonomy cycle which itself forces a rigid defect or an extra boundary state.

Scientific status:

```text
E98 = UNIVERSAL MINIMAL EXCHANGE COMPONENT NORMAL FORM
      + TARGET6 RECTANGLE CLOSURE
      + DOUBLE-RECTANGLE RIGID-ONLY REDUCTION.

GLOBAL_TARGET6_PARENT = OPEN.
P_VS_NP = OPEN.
```
