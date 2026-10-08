# R5 E114 — Signed-Parallel Residual-Interface Compression

Date: 2026-10-08

Status:
`ANY_FIXED_E112_STYLE_JOINT_LIFT_HAS_CONSTANT_RESIDUAL_INTERFACE__PRISM_BOUND_IS_7_BITS`

Scientific ceiling:

```text
E114 DOES NOT YET EXCLUDE EVERY GROWING SIGNED-PARALLEL TARGET6 CORE.

IT PROVES THAT SIGNED-PARALLEL COPIES CAN BE CONTRACTED EXACTLY AT THE
POST-E106 REPAIR-DIRECTION LAYER, AND THAT ANY FIXED E112-STYLE CUBIC NORMAL
GADGET HAS ONLY A FINITE-STATE INTERFACE TO THE REST OF THE TANNER PARENT.

FOR THE HEXAGONAL PRISM, 72 OUTGOING TANNER INCIDENCES CARRY AT MOST
7 INDEPENDENT RESIDUAL BITS, SO THE ENTIRE JOINT LIFT HAS AT MOST 128
EXTERNAL REPAIR PATTERNS.

P_VS_NP = OPEN.
```

## 1. Input from E113

E113 proved that one Tanner variable cannot realize both endpoint occurrences
of one E112 abstract prism normal.

For every abstract edge normal g_e, a joint lift requires two distinct Tanner
variables

```text
x_e^0,
x_e^1
```

with:

```text
same residual normal g_e,
opposite six-witness support parity.
```

The parity sign matters for the final ExactOne literal, but for every repair
direction z in the E106 direction space U the equal-normal condition means

```text
z(x_e^0)=z(x_e^1).
```

Thus the pair contributes only one residual selector bit.

## 2. General connected cubic signed-parallel block

Let H be a connected cubic graph whose q vertices are distinguished active
checks and whose m=3q/2 edges are abstract residual normals.

A joint Tanner lift uses two distinct occurrence variables per edge, one at
each endpoint check.

So before using any equations there are

```text
2m = 3q
```

occurrence coordinates.

Every occurrence variable is still cubic in the original Tanner graph, so
besides its distinguished check it has two further incidences outside the
block.

## 3. Pair equalities

For every edge e, equality of residual normals gives one repair-direction
equation

```text
z(x_e^0)+z(x_e^1)=0.
```

The m pair equations are independent because their coordinate supports are
disjoint.

After substituting them, one residual selector remains per abstract edge.

Hence the 2m occurrence coordinates collapse to m edge selectors.

This is the exact residual meaning of series/parallel contraction here.  It
does not identify the two original Tanner variables physically; it only removes
their redundant repair-direction degree of freedom.

## 4. Distinguished-check parity becomes graph incidence

Every repair direction lies in the zero-boundary Tanner kernel.

Therefore at every distinguished cubic check the three incident occurrence
coordinates have even parity.

After the pair substitutions, these q equations become exactly the binary
vertex-edge incidence equations of H.

For a connected graph the binary incidence matrix has rank

```text
q-1.
```

Therefore the restricted repair space on the entire signed-parallel block has
dimension at most

```text
m-(q-1)
 = 3q/2-q+1
 = q/2+1.
```

Equivalently, working before pair substitution:

```text
dim rho_H(U)
 <= 2m - m - (q-1)
 = q/2+1.
```

This bound is independent of how complicated the rest of the Tanner parent is.

## 5. Physical Tanner boundary can be huge while residual boundary is tiny

Each of the 2m occurrence variables has two additional Tanner incidences
outside the distinguished check set.

Thus the number of outgoing physical Tanner incidences is

```text
4m = 6q.
```

But all their repair values are copies of the same at-most q/2+1 internal
selector bits.

Hence:

```text
boxed:
A connected q-check signed-parallel cubic normal block has
at most 2^(q/2+1) distinct residual boundary patterns,
even though it exposes 6q Tanner incidences.
```

The important complexity parameter is therefore not the number of Tanner
stubs but the residual interface rank.

## 6. Hexagonal-prism consequence

For the E112 prism:

```text
q = 12 checks,
m = 18 abstract normals,
36 distinct Tanner occurrence variables,
72 outgoing Tanner incidences.
```

The connected incidence rank is

```text
12-1 = 11.
```

So

```text
dim interface <= 18-11 = 7.
```

Therefore:

```text
boxed:
ANY genuine joint Tanner lift of the fixed E112 prism has at most
2^7 = 128 residual external patterns.
```

This remains true if the 72 outgoing incidences attach to an arbitrarily large
C4-free Tanner parent.

The prism may be a real local NO-RAW8 mechanism, but it cannot by itself create
asymptotic solver hardness.

## 7. Relation to E108-E110

E108 already solves a residual problem by enumerating the active normal-span
quotient when its dimension is small.

E110 summarizes a low-dimensional interface by exact boundary-state dynamic
programming.

E114 shows that a fixed signed-parallel normal gadget automatically presents
such a bounded interface after the equal-normal contraction.

Thus an E112 prism joint lift, if it exists, should be treated as a finite
factor with at most 128 repair states rather than as a new high-width primitive.

No assumption is made that the whole outside normal component has rank seven.
Only the restriction/interface carried by the prism occurrence variables is
bounded.

## 8. General algorithmic consequence

For any connected signed-parallel cubic block with q checks:

```text
interface rank <= q/2+1.
```

Therefore:

```text
fixed q            -> constant-state exact interface,
q=O(log n)         -> polynomial-size exact interface,
large q            -> still potentially asymptotically hard.
```

So a genuine asymptotic obstruction cannot be a bounded E112 motif repeated
without interaction.

It must contain a growing signed-parallel core whose independent residual
interface also grows.

## 9. Companion replay

```text
experiments/r5_e114_signed_parallel_interface_compression.py
```

The checker verifies the exact rank formula on three independent connected
cubic graphs:

```text
K4:              q=4,  interface dimension=3,
3-cube:          q=8,  interface dimension=5,
hexagonal prism: q=12, interface dimension=7.
```

For the prism it freezes:

```text
18 pair equalities,
11 independent distinguished-check equations,
36 occurrence coordinates,
residual interface dimension 7,
128 possible repair patterns,
72 outgoing Tanner incidences.
```

## 10. Correct E115 target

The fixed prism is now algorithmically compressed.

The remaining asymptotic route is:

```text
E115 GROWING SIGNED-PARALLEL CORE SEPARATOR ATTACK

Input:
  a connected cubic signed-parallel normal incidence graph H of growing size,
  realized inside an actual TARGET6 Tanner parent.

Use:
  * every edge is represented by two distinct Tanner variables with the same
    residual normal and opposite support parity;
  * every occurrence variable has exactly two further Tanner incidences;
  * source Tanner geometry is C4-free;
  * H contributes only its binary cycle-space selector degrees of freedom.

Goal:
  A. prove every large realizable H has a polynomially discoverable
     O(sqrt(log n)) residual separator/decomposition and invoke E110-E111;
  B. show the outside Tanner completion forces additional equalities that
     reduce the interface rank below the generic q/2+1 bound;
  C. force raw8 / an additional boundary state;
  D. or construct the first unbounded exact TARGET6/no-raw8 joint-lift family.
```

Scientific status:

```text
E114 = SIGNED-PARALLEL RESIDUAL CONTRACTION
       + FIXED-GADGET INTERFACE COMPRESSION.

E112 PRISM JOINT LIFT, IF IT EXISTS:
  <=7 residual interface bits,
  <=128 exact external repair patterns.

GROWING SIGNED-PARALLEL CORE = OPEN.
UNIVERSAL POLYNOMIAL EXACTONE SOLVER = NOT YET CONSTRUCTED.
P_VS_NP = OPEN.
```
