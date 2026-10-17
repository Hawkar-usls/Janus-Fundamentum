# R5 E9 — PG15 fixed-port NOR source composition, fanout, NOT, COPY and pins

Date: 2026-10-01

Status:
`JANUS_EXACT_PG15_FIXED_PORT_NOR_SOURCE_COMPOSITION__FANOUT2_NOT_COPY_PIN__HARDNESS_RETURN__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_PG15_MINIMAL_8MACRO_AFFINE_PIN_AND_NOR_RETURN_2026-10-01_v1.0.md`
- `research/R5_E9_PG15_AF3_AFFINE_IMPLICATION_THRESHOLD8_NOR_RETURN_2026-10-01_v1.0.md`

Checker:
- `experiments/r5_e9_pg15_nor_source_composition_fanout_copy.py`

## 1. Purpose

The previous PG15 result proved that maximal direct AF3 affine implication does not terminate in another affine island: after the unique rank-one affine pin, the four full-support states form exactly the Boolean NOR graph.

The open question was whether this NOR relation was merely a local residue of one frozen source, or whether it composes through legal cubic linear Exact-One source geometry.

This note answers that composition question positively for a fixed source-preserving port system.

It is a representation/hardness-return theorem, **not** a polynomial SAT solver.

## 2. Canonical PG15 Boolean gate

Use the frozen 15-row PG15 source

```text
(1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),
(3,4,7),(3,5,6),(4,9,13),(4,10,14),(5,8,13),
(5,10,15),(6,8,14),(6,9,15),(7,8,15),(7,11,12).
```

Its exact Boolean Exact-One model set has four elements.

With zero-based terminal coordinates

```text
o = 11,
a = 12,
b = 13,
```

the terminal projection is exactly

```text
(o,a,b) in
{(1,0,0),(0,0,1),(0,1,0),(0,1,1)},
```

hence

```text
o = NOR(a,b).
```

Each terminal triple determines exactly one full PG15 model.

## 3. Legal incidence 2-switch

Take two disjoint cubic linear PG15 copies.  Choose an occurrence of variable `x` in one row of the first copy and an occurrence of variable `y` in one row of the second copy.  Exchange those two variable occurrences between the rows.

This operation preserves:

```text
row size = 3,
column degree = 3.
```

Linearity is not automatic for an arbitrary set of switches and is therefore checked/proved for the fixed port system below.

## 4. Fixed four-port system

Use zero-based rows/variables.

Output ports:

```text
O0 = (row 2, variable 11),  row 2 = (0,11,12)
O1 = (row 4, variable 11),  row 4 = (1,11,13)
```

Input ports:

```text
I0 = (row 7,  variable 12), row 7  = (3,8,12)
I1 = (row 11, variable 13), row 11 = (5,7,13)
```

The checker exhausts all `2^15` assignments and proves the key redundancy identity

```text
Models(PG15 with rows {2,4,7,11} deleted)
=
Models(PG15)
```

with both sides containing exactly four models.

Therefore, even when all four port rows of one copy are modified by external wiring, its unchanged rows already force the copy to be one of the four canonical NOR states.

This removes the main compositional ambiguity that was still open in the previous PG15 note.

## 5. One switch is exactly one equality wire

Consider a wire from output port `Os` of copy `U` to input port `It` of copy `V`.

Before switching, the two selected rows have the form

```text
sum(C_out) + o_U = 1,
sum(C_in)  + i_V = 1.
```

After exchanging the occurrences `o_U` and `i_V`, they become

```text
sum(C_out) + i_V = 1,
sum(C_in)  + o_U = 1.
```

Because every local assignment is already one of the canonical PG15 models, the original row equations hold.  Subtracting gives

```text
i_V = o_U.
```

Conversely that equality restores both switched row equations.

Hence, on the exact local NOR state sets,

```text
one fixed-port incidence 2-switch
<=>
one Boolean equality wire.
```

The checker verifies all four fixed port combinations independently and also performs the larger all-incidence census.

## 6. Arbitrary acyclic fixed-port composition theorem

Let `D` be a finite directed acyclic wiring graph whose vertices are PG15 gate copies.  Each gate has:

```text
at most one wire entering I0,
at most one wire entering I1,
at most one wire leaving O0,
at most one wire leaving O1.
```

For every directed wire, perform the corresponding incidence 2-switch.

Then the resulting Exact-One source has the following exact properties.

### 6.1 Cubicity and 3-uniformity

Each switch only exchanges two occurrences, so every row still has size three and every variable still has degree three.

### 6.2 Exact Boolean semantics

The four-port deletion identity forces every gate copy into one of its four canonical NOR states before the switched rows are considered.

Each switched row pair is then equivalent to exactly one wire equality by Section 5.

Therefore the global Boolean models are exactly the assignments satisfying

```text
for every gate v:   o_v = NOR(a_v,b_v),
for every wire u->v: selected_input_v = o_u.
```

There are no extra terminal states and no missing terminal states.

### 6.3 Source linearity

For the fixed ports, the companion sets are

```text
C(O0) = {0,12},
C(O1) = {1,13},
C(I0) = {3,8},
C(I1) = {5,7}.
```

The two input companion sets are disjoint.

A switch creates only cross-copy pairs between the two gate copies incident with that wire.  If two wires join the same ordered pair of gate copies, they use different input ports; the consumer-side companion sets are disjoint, so no cross pair repeats.  Producer-side pairs contain different consumer input variables.  A producer-side cross pair cannot equal a consumer-side cross pair because output/input terminals are excluded from their own companion sets.

Pairs belonging to different unordered pairs of gate copies cannot coincide.

Finally, acyclicity forbids having wires simultaneously in both directions between the same pair of gate copies, which is the remaining way a cross-pair duplicate could be created.

Thus the composed source remains linear.

### 6.4 Connectivity

Each PG15 copy is internally connected.  Every switch creates incidence links between its two endpoint copies.  Hence if the underlying undirected wiring graph is connected, the resulting source incidence graph is connected.

### 6.5 Size

For `g` gate copies and `w` wires:

```text
variables = 15 g,
rows      = 15 g,
switches  = w.
```

No auxiliary row or variable is introduced by a wire.  Construction time is `O(g+w)` once the circuit wiring is given.

## 7. Exhaustive finite controls

The executable checker independently confirms the local ingredients and broader finite census:

```text
PG15 Boolean models                         = 4
fixed-port skeleton models                  = 4
all-incidence exact serial equality hits    = 36
natural fanout-2 candidates                 = 216
exact source-valid fanout-2 hits            = 216
semantic tied-input NOT candidates          = 54
source-linear tied-input NOT candidates     = 36
source-valid NOT-template pairs             = 36^2 = 1296
exact source-valid COPY compositions        = 1296
```

Thus bounded fanout is not merely inferred from one hand-picked switch.

## 8. Exact NOT and COPY

Connecting one producer output to both inputs of a consumer NOR gate yields

```text
n = NOR(x,x) = NOT x.
```

The exhaustive source-valid class contains 36 such linear connected realizations.

Composing two source-valid NOT templates gives

```text
x -> NOT x -> x.
```

Every one of the `36 x 36 = 1296` template pairs is checked exactly and realizes COPY while preserving cubicity, linearity and connectivity.

This is a bounded-cost identity-wire control inside the same source geometry.

## 9. Exact output pins

The canonical PG15 model set has one source coordinate that is identically zero:

```text
zero-based variable 3 = 0
```

in all four Boolean models.

### pin0

Switch an occurrence of a target gate output with an occurrence of this constant-zero coordinate in a fresh helper PG15 copy.  The checker uses

```text
target: row 14, variable 11
helper: row 5, variable 3
```

and proves exactly

```text
target output = 0.
```

The combined source remains cubic, linear and connected.

### pin1

First realize a tied-input NOT on the target output with the fixed safe ports, then pin the inverter output to zero using the same helper construction.

The checker proves exactly

```text
target output = 1.
```

Again the source remains cubic, linear and connected.

## 10. Scientific consequence

The PG15 Boolean residue is **not** an isolated local artifact and is **not** removed by source-preserving composition constraints.

The exact source language supports:

```text
NOR gate semantics,
serial equality wiring,
fanout <= 2,
NOT,
COPY,
output pin 0,
output pin 1,
acyclic fixed-port composition with O(1) source cost per gate/wire.
```

Therefore the earlier hope

```text
maximal direct AF3 affine implication
-> small residual
-> automatic polynomial contraction
```

is false on PG15: the residual can reconstitute ordinary Boolean logic under the original cubic linear source rules.

This is a hardness/representation return, not a proof that every arbitrary Boolean circuit has already been embedded with every desired high-fanout convention.  In particular, a complete source-level reduction from a named NP-complete circuit-SAT variant still requires its own bounded-fanout/input-generation normalization and explicit size accounting.

## 11. Next gate

Freeze

```text
R5_E9_PG15_NOR_GLOBAL_CIRCUIT_RETURN_OR_SOLVER_INVARIANT_GATE_V1
```

Next admissible tasks:

1. bind the fixed-port theorem to an explicit standard bounded-fanout NOR-Circuit-SAT normalization, including primary-input generation and output pinning;
2. prove polynomial size for that normalization without hidden signal-replication blowup;
3. if full circuit return closes, stop treating local PG15 affine compression as a solver route and search for a genuinely global invariant that contracts these composed networks;
4. if normalization fails, isolate the exact source invariant responsible and test whether it yields a polynomial decision algorithm;
5. keep witness reconstruction explicit in either direction.

## 12. Firewall

```text
PG15 local NOR relation                 = PROVED
fixed-port equality wire                = PROVED
arbitrary acyclic fanout<=2 composition = PROVED
source cubicity                         = PROVED
source linearity                        = PROVED for the fixed DAG port system
NOT / COPY                              = PROVED with exact checker
pin0 / pin1                             = PROVED with exact checker
universal polynomial SAT solver         = NOT PROVED
E8_D1                                   = EMPTY
P_VS_NP                                 = OPEN
```
