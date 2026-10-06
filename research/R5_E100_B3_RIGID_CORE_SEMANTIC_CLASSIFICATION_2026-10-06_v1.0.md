# R5 E100 — Complete B_C=3 Rigid-Core Semantic Classification

Date: 2026-10-06

Status:
`THREE_PORT_RIGID_CORE_SEMANTICS_COLLAPSE_TO_17_FAMILIES__BINARY_MATROID_OR_AFFINE_EQUALITY`

Scientific ceiling:

```text
E100 DOES NOT TOPOLOGICALLY ENUMERATE EVERY INTERNAL C4-FREE B_C=3 CORE.

IT DOES SOMETHING STRONGER FOR THE INTERFACE: IT CLASSIFIES THE ENTIRE
THREE-PORT EXACT BOUNDARY SEMANTICS OF EVERY SUCH CORE, INDEPENDENT OF
INTERNAL SIZE OR TOPOLOGY.

EVERY NONEMPTY B_C=3 RELATION IS ONE OF ONLY 17 FAMILIES:
  7 RANK-1 BINARY-MATROID BASIS FAMILIES,
  7 RANK-2 BINARY-MATROID BASIS FAMILIES,
  3 AFFINE CONSTANT/EQUALITY FAMILIES.

P_VS_NP = OPEN.
```

## 1. Setup

Let C be one connected rigid/inert core from E99 with exactly

```text
B_C = 3
```

boundary incidences leaving its inert variables for mixed/non-rigid checks.

Write

```text
R = number of rigid ExactOne checks in C,
V = number of inert Equality variables in C.
```

E99 already gives

```text
B_C = 3(V-R)=3,
```

hence

```text
V=R+1.
```

But E100 does not need C4-freeness, connectedness, or this last equality for
the key semantic identity. It only uses cubic variables, exact-one checks, and
the fact that there are three exposed variable-side incidences.

## 2. Universal incidence-count identity

Take any feasible assignment of the core.

Let

```text
Y = selected core variables,
F = selected boundary stubs among the three exposed incidences.
```

Every selected cubic variable contributes exactly three selected incidences.

Every rigid internal check receives exactly one selected incidence.

The remaining selected incidences are exactly the selected boundary stubs.

Therefore

```text
boxed:
3|Y| = R + |F|.
```

Consequently

```text
boxed:
|F| == -R (mod 3).
```

Because the boundary has only three bits, this congruence is already a complete
Hamming-layer classification.

## 3. The three residue classes

### R == 0 mod 3

Then

```text
|F| in {0,3}.
```

So the complete exact boundary relation is a nonempty subset of

```text
{000,111}.
```

There are exactly three possibilities:

```text
{000}
{111}
{000,111}.
```

All three are affine over GF(2):

```text
constant 0,
constant 1,
ternary equality.
```

### R == 1 mod 3

Then every feasible boundary state has

```text
|F|=2.
```

So the relation is a nonempty subset of

```text
{110,101,011}.
```

There are exactly

```text
2^3-1 = 7
```

such relations.

Every one is the basis family of a rank-2 matroid on at most three effective
elements. Every matroid on this layer is binary.

### R == 2 mod 3

Then every feasible boundary state has

```text
|F|=1.
```

So the relation is a nonempty subset of

```text
{100,010,001}.
```

Again there are exactly seven relations.

Every one is a rank-1 matroid basis family and is binary.

Hence:

```text
boxed:
TOTAL POSSIBLE NONEMPTY B3 CORE BOUNDARY RELATIONS = 3+7+7 = 17.
```

No internal size parameter appears.

## 4. Why the relation is nonempty in the TARGET6 rigid lane

E99 defines an inert variable support as a union of the three opposite-pair
atoms

```text
O0={X_A,Q_BC}
O1={X_B,Q_AC}
O2={X_C,Q_AB}.
```

At every rigid check the three incident inert supports partition these three
atoms.

For any chosen atom O_i, select exactly the inert variables whose support
contains O_i.

At every rigid check exactly one incident variable is selected.

Thus each atom produces a canonical exact cover of the rigid core.

Therefore the B3 relation is guaranteed nonempty in the actual TARGET6
setting.

## 5. Sharper canonical atom-routing normal form

Let the three boundary stubs be ports 0,1,2.

For each atom O_i, look at the three-bit boundary pattern produced by its
canonical atom cover.

The universal counting identity applies to each atom cover.

### R == 2 mod 3 — one-hot router

Every atom pattern has weight one.

Therefore every atom occurs in exactly one of the three boundary-port support
sets.

Equivalently, the three port supports partition the three atoms.

So there is a function

```text
pi : {O0,O1,O2} -> {port0,port1,port2}
```

and choosing atom O_i activates exactly port pi(O_i).

This is a one-hot router.

There are

```text
3^3 = 27
```

labelled routing maps.

### R == 1 mod 3 — two-hot co-router

Every atom pattern has weight two.

Thus every atom is absent from exactly one boundary port.

Equivalently, the complements of the three port-support sets partition the
atoms.

Again there is a map

```text
pi : atoms -> unique missing port.
```

Choosing an atom activates the two ports other than pi(atom).

This is a two-hot co-router.

Again there are 27 labelled maps.

### R == 0 mod 3 — equality router

Every atom boundary pattern has weight zero or three.

Hence for every atom either all three ports contain it or none do.

Therefore the three boundary-port support sets are identical.

There are only

```text
2^3 = 8
```

labelled support possibilities.

This is an equality/constant router.

## 6. Exact-relation sandwich

The three canonical atom patterns are known feasible states.

Every other feasible state, if any, must lie in the same residue layer from
Section 3.

Therefore:

```text
canonical atom image
  subseteq
exact B3 boundary relation
  subseteq
allowed residue layer.
```

This often determines the exact relation immediately.

Examples:

```text
if the three one-hot atom patterns are distinct,
the exact relation is forced to be full ExactOne_3.

if the three two-hot atom patterns are distinct,
the exact relation is forced to be full U_{2,3} basis family.

if residue 0 atom covers realize both 000 and 111,
the exact relation is forced to be ternary equality.
```

If canonical atom patterns repeat, there can be one or two still-undetermined
extra states, but the whole interface remains within the same 17-family list.

## 7. What “reducible” means here

E100 proves a **semantic compression theorem**:

```text
an arbitrarily large B_C=3 rigid core
has only a constant-size three-port interface type.
```

The interface is always either

```text
* binary-matroidal, or
* affine constant/equality.
```

Thus a B3 core introduces no new unbounded three-ary relation family.

This is exactly the kind of collapse needed for a recursive decomposition
algorithm.

Important limitation:

```text
E100 does NOT yet provide a universal polynomial-time method that,
given only the raw internal core graph, decides which optional extra boundary
states beyond the three canonical atom states also exist.
```

So the global algorithm still needs either:

```text
1. a way to avoid querying those optional states;
2. a direct polynomial representation extracted from the witness-support data;
3. or a recursive elimination theorem that composes these 3-state routers.
```

## 8. Consequence for the rigid frontier

Before E100 a B_C=3 rigid core could still look like an arbitrarily large
unknown obstruction.

After E100:

```text
boxed:
B_C=3 topological size is irrelevant to boundary semantic complexity.
```

Every such core collapses to one of 17 constant-size interface families, with
three explicit canonical atom covers always available.

So the rigid frontier now shifts from classifying huge internal cores to
coupling these small routers through the surrounding mixed checks.

## 9. E101 target

The next step should not enumerate larger rigid cores.

It should solve the composition problem:

```text
E101 B3 ROUTER-TO-MIXED-CHECK COMPOSITION

Use the one-hot / two-hot / equality router normal forms and the E97/E98
exchange-graph structure of mixed checks.

Goal:
  prove that every network of B3 rigid routers can be eliminated or represented
  by a polynomial-size binary/affine state system;

or:
  construct the first router network that still blocks raw state8.
```

If successful, B3 rigid cores disappear as a global obstruction rather than
only as local gadgets.

Scientific status:

```text
E100 = COMPLETE B_C=3 THREE-PORT SEMANTIC CLASSIFICATION.
B3_INTERFACE_TYPES = 17 CONSTANT-SIZE FAMILIES.
B3_NEW_UNBOUNDED_LOCAL_HARDNESS = EXCLUDED.
GLOBAL_ROUTER_COMPOSITION = OPEN.
RECTANGLE_HOLONOMY = OPEN.
P_VS_NP = OPEN.
```
