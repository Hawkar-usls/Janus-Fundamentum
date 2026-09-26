# R5 E9 — Cubic Source-Boundary Pinning and Context Separation

Date: 2026-09-26

Authority:
`JANUS_DERIVED_EXACT_SOURCE_CONTEXT_BARRIER_AFTER_PA0021__NO_COMPLEXITY_LOWER_BOUND`

Authorizing audit:
`PA-0021-CUBIC-EXACT-ONE-BOUNDARY-PINNING`

Conceptual parent:
`PA-0020-ODD-HOLE-CONTEXTUAL-MULTISELECTOR-DOMINANCE`

Checker:
`experiments/r5_e9_cubic_source_boundary_pinning.py`

## 1. Exact theorem target

Let x,y,z be three exposed variables of a positive Exact-One-3 block.
Each exposed variable already has one occurrence in the source block.

A source-valid cubic pin gadget must therefore contribute exactly two
occurrences to each of x,y,z, use every new internal variable exactly three
times, and use only clauses of three distinct positive variables.

PA-0021 authorized the question whether every target

```
t in {0,1}^3
```

admits a constant-size gadget whose exact projected boundary relation is
the singleton `{t}`.

It does.

## 2. Four canonical gadgets

All constraints below mean positive Exact-One-3.

### Weight 0: pin 000

Use one internal variable p:

```
(x,y,p)
(x,z,p)
(y,z,p)
```

The last two equations minus the first force y=z, and the exact-one system
has the unique boundary value

```
(x,y,z)=(0,0,0),
```

with p=1.

Boundary degrees are 2,2,2 and p has degree 3.

### Weight 2: pin 011

Use internal p,q:

```
(x,y,p)
(x,z,q)
(y,p,q)
(z,p,q)
```

Exact enumeration / elementary substitution gives the singleton projection

```
(x,y,z)=(0,1,1).
```

Both p and q have degree three and every boundary variable has degree two.

Boundary permutation gives all three weight-2 patterns.

### Weight 1: pin 001

Use internal p,q,r:

```
(x,z,p)
(x,q,r)
(y,z,p)
(y,q,r)
(p,q,r)
```

The exact projected relation is

```
(x,y,z)=(0,0,1).
```

Every internal has degree three and every boundary variable degree two.

Boundary permutation gives all three weight-1 patterns.

### Weight 3: pin 111

Use internal p,q,r,s:

```
(x,p,q)
(x,p,r)
(y,p,s)
(y,q,r)
(z,q,s)
(z,r,s)
```

The exact projected relation is

```
(x,y,z)=(1,1,1).
```

Again all three boundary degrees are two and all four internal degrees are
three.

Thus the four Hamming-weight representatives, together with boundary
permutation, realize all eight singleton relations.

## 3. Arbitrary full-boundary pinning

The full odd-hole boundary has

```
(w_0,...,w_{k-1},
 a_0,...,a_{k-1},
 b_0,...,b_{k-1}),
```

hence exactly `3k` exposed variables.

Each exposed variable occurs exactly once inside the odd-hole source block.

Take any complete boundary assignment

```
beta in {0,1}^{3k}.
```

Partition the labeled boundary variables into any k triples.  For each triple,
attach the corresponding singleton gadget from Section 2.

Because the gadgets use disjoint new internal variables:

- every old boundary variable receives exactly two new occurrences;
- its total source degree becomes `1+2=3`;
- every new internal variable has degree exactly 3;
- every new clause has three distinct positive variables;
- the glued outside context is satisfiable exactly for boundary assignment beta.

Therefore:

```
boxed(
EVERY COMPLETE FULL-BOUNDARY ASSIGNMENT
CAN BE PINNED BY A SOURCE-VALID CUBIC POSITIVE EXACT-ONE CONTEXT.
)
```

The checker verifies all eight primitive gadgets exactly and replays the degree
composition for full boundaries of sizes 15, 21 and 27.

## 4. Source-language Boundary Myhill--Nerode consequence

PA-0020 used the general boundary Myhill--Nerode fact:

```
different projected boundary relations
can be separated by a pinning context.
```

NM-0025 strengthens the relevant part for the present source language.

Let R and R' be two distinct relations on a full odd-hole boundary.
Choose

```
beta in R symmetric_difference R'.
```

The cubic pin context for beta constructed above has exactly one exposed
boundary assignment, namely beta.

Hence one of the glued source instances is satisfiable and the other is not.

So:

```
R != R'
=>
R and R' are distinguishable
by a cubic positive Exact-One source-valid context.
```

Accordingly, a **context-independent** replacement of an odd-hole block that
claims validity for every cubic source context must preserve its exact projected
boundary relation.

The arbitrary-context firewall is therefore not an artifact of allowing a more
expressive external CNF language.

## 5. Important scope limit

The pinning completion preserves the original cubic positive Exact-One source
contract.

It is NOT claimed that after gluing it also preserves every later PA-0001
preprocessor promise such as:

```
P,Q noncommuting,
Z3 phase FAIL,
low-nullity lane removed,
known special classes removed.
```

Therefore NM-0025 blocks universal hole-only source reductions.  It does not
block an instance-specific contraction that uses the actual already-filtered
outside context.

That remains exactly the PA-0020 frontier.

## 6. Relation to known forcing gadgets

PA-0021 source-binds broad Boolean-CSP pp gadgets, generic 1-in-3 forcing
gadgets, and the cubic positive 1-in-3 source class.

NM-0025 claims only the exact degree-profile theorem above:

```
3 boundary ports each gadget-degree 2
+
all internals degree 3
+
positive Exact-One-3 only
+
singleton projection for every 3-bit target.
```

## 7. Verdict

Freeze:

```
NM-0025
CUBIC SOURCE BOUNDARY PINNING
=
PASS

ALL 8 THREE-BIT SINGLETONS
=
EXPLICIT CONSTANT GADGETS

ARBITRARY 3k FULL BOUNDARY ASSIGNMENT
=
PINNABLE BY DISJOINT COMPOSITION

CONTEXT-INDEPENDENT ODD-HOLE STATE MERGE
EVEN WITHIN THE CUBIC SOURCE LANGUAGE
=
BLOCKED UNLESS EXACT BOUNDARY RELATION IS PRESERVED

INSTANCE-SPECIFIC CONTEXTUAL DOMINANCE
=
OPEN / ACTIVE

D1
=
EMPTY

P_VS_NP
=
OPEN

P_EQ_NP
=
NOT PROVED
```
